"""Apertus: reads, reconciles and explains. It never sets the grade.

Talks to any OpenAI-compatible endpoint (llama.cpp, vLLM, Ollama, CSCS…)
configured with LLM_BASE_URL / LLM_API_KEY / LLM_NAME. Standard library only.

Every answer is checked before use:
  * a claim must be a verbatim quote from the project's documentation;
  * a gap or an explanation line must cite evidence IDs that exist.
Anything that fails a check is dropped and counted in the report.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import registry

TOPICS = ["model_location", "data_flow", "offline", "third_parties", "verifiability"]
TOPIC_Q = {t: i + 1 for i, t in enumerate(TOPICS)}
LANG_NAME = {"fr": "French", "de": "German (Swiss standard German, use 'ss' not 'ß')", "it": "Italian",
             "rm": "Romansh (Rumantsch Grischun)", "en": "English"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[`*_>#\[\]()]", " ", s)
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


class Apertus:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None,
                 cache_dir: str | os.PathLike | None = None, timeout: float = 600):
        self.base_url = (base_url or os.environ.get("LLM_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.environ.get("LLM_API_KEY") or "none"
        self.model = model or os.environ.get("LLM_NAME") or "swiss-ai/Apertus-v1.5-8B"
        self.timeout = timeout
        self.cache = Path(cache_dir) if cache_dir else None
        self.calls = 0
        self.seconds = 0.0
        self.rejected = 0
        self.rejections: list[dict] = []  # kept as feedback for the Apertus team
        self._available: bool | None = None
        self._checked = 0.0

    # ------------------------------------------------------------------ infra
    @property
    def endpoint_host(self) -> str:
        return urllib.parse.urlparse(self.base_url).hostname or ""

    def jurisdiction(self) -> dict:
        h = registry.classify(self.endpoint_host) if self.endpoint_host else None
        return {"host": self.endpoint_host, "jurisdiction": h.jurisdiction if h else "",
                "operator": h.operator if h else ""}

    def available(self) -> bool:
        """Reachability, re-checked at most every 30 s (the endpoint may start after Sigillum)."""
        now = time.time()
        if self._available is not None and now - self._checked < 30:
            return self._available
        self._checked = now
        if not self.base_url:
            self._available = False
            return False
        try:
            req = urllib.request.Request(self.base_url + "/models", headers=self._headers())
            with urllib.request.urlopen(req, timeout=4) as r:
                self._available = r.status == 200
        except (urllib.error.URLError, OSError, ValueError):
            self._available = False
        return self._available

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

    def _chat(self, messages: list[dict], schema: dict | None, max_tokens: int) -> str:
        payload = {"model": self.model, "messages": messages, "temperature": 0, "seed": 7,
                   "max_tokens": max_tokens}
        if schema:
            payload["response_format"] = {"type": "json_schema",
                                          "json_schema": {"name": "answer", "schema": schema, "strict": True}}
        key = hashlib.sha256(json.dumps([self.model, payload], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if self.cache:
            f = self.cache / f"{key}.json"
            if f.exists():
                return json.loads(f.read_text(encoding="utf-8"))["content"]
        t0 = time.time()
        body = json.dumps(payload).encode()
        try:
            req = urllib.request.Request(self.base_url + "/chat/completions", data=body, headers=self._headers())
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            if schema and e.code in (400, 422):   # endpoint without structured output: ask for plain JSON
                payload.pop("response_format")
                req = urllib.request.Request(self.base_url + "/chat/completions",
                                             data=json.dumps(payload).encode(), headers=self._headers())
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    data = json.loads(r.read())
            else:
                raise
        content = data["choices"][0]["message"]["content"] or ""
        self.calls += 1
        self.seconds += time.time() - t0
        if self.cache:
            self.cache.mkdir(parents=True, exist_ok=True)
            (self.cache / f"{key}.json").write_text(json.dumps({"model": self.model, "content": content,
                                                                 "at": time.strftime("%Y-%m-%dT%H:%M:%S")},
                                                                ensure_ascii=False), encoding="utf-8")
        return content

    @staticmethod
    def _json(text: str) -> dict:
        text = text.strip()
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0) if m else text)

    # ------------------------------------------------------------------ tasks
    def extract_claims(self, docs_text: str) -> tuple[list[dict], int]:
        """Read the docs; return verbatim sovereignty claims (validated)."""
        if not docs_text.strip():
            return [], 0
        schema = {"type": "object", "properties": {"claims": {"type": "array", "maxItems": 6, "items": {
            "type": "object", "properties": {"quote": {"type": "string"}, "topic": {"type": "string", "enum": TOPICS}},
            "required": ["quote", "topic"]}}}, "required": ["claims"]}
        msg = [
            {"role": "system", "content": (
                "You audit software documentation. List the sentences in which the project claims something "
                "about where its AI model runs, where data goes, offline use, third-party services or tracking, "
                "or how it can be verified. Copy each sentence exactly as written, without changing a word. "
                "If there is no such sentence, return an empty list. Answer in JSON.")},
            {"role": "user", "content": docs_text[:3500]},
        ]
        try:
            data = self._json(self._chat(msg, schema, 400))
        except (ValueError, KeyError, urllib.error.URLError, OSError):
            return [], 0
        doc = _norm(docs_text)
        out, rejected = [], 0
        for c in data.get("claims", []):
            q = (c.get("quote") or "").strip()
            if not (len(q) >= 12 and _norm(q)[:200] in doc and c.get("topic") in TOPICS):
                self.rejections.append({"task": "read", "reason": "quote not found verbatim in the documentation", "answer": q[:200]})
            if len(q) >= 12 and _norm(q)[:200] in doc and c.get("topic") in TOPICS:
                if all(_norm(q) != _norm(o["quote"]) for o in out):
                    out.append({"id": f"C{len(out) + 1}", "quote": q, "topic": c["topic"], "q": TOPIC_Q[c["topic"]]})
            else:
                rejected += 1
        self.rejected += rejected
        return out, rejected

    def reconcile(self, claims: list[dict], evidence: list[dict]) -> tuple[list[dict], int]:
        """Compare what the project says with what the traces show — one verdict per claim."""
        # only traces that *can* contradict a sovereignty claim are shown — and may be cited
        traces = [e for e in evidence if e["kind"] == "trace" and contradicting(e)]
        if not claims or not traces:
            return [], 0
        ids = {e["id"] for e in traces}
        lines = []
        for e in traces[:28]:
            where = f'{e.get("file", "")}:{e.get("line", "")}'.strip(":")
            host = f' sends data to {e["host"]} ({e.get("operator", "")}, jurisdiction {e.get("jurisdiction", "")})' if e.get("host") else ""
            lines.append(f'{e["id"]}: {e.get("detail") or e["signal"]}{host} [{where}]')
        schema = {"type": "object", "properties": {"verdicts": {"type": "array", "items": {
            "type": "object", "properties": {"claim": {"type": "string"}, "contradicted": {"type": "boolean"},
                                             "evidence": {"type": "array", "items": {"type": "string"}},
                                             "shows": {"type": "string"}},
            "required": ["claim", "contradicted", "evidence", "shows"]}}}, "required": ["verdicts"]}
        msg = [
            {"role": "system", "content": (
                "You check a software project's claims against traces found in its code. For each claim, decide "
                "whether at least one trace contradicts it. A claim that data stays local or that nothing leaves is "
                "contradicted by any trace that sends data to an external host abroad or to a telemetry service. "
                "A claim that the tool works offline is contradicted by scripts or models fetched from the internet. "
                "Give the ids of the contradicting traces and, in 'shows', one short neutral English sentence saying "
                "what the traces show. Answer in JSON.")},
            {"role": "user", "content": "CLAIMS\n" + "\n".join(f'{c["id"]}: "{c["quote"]}"' for c in claims)
                                        + "\n\nTRACES\n" + "\n".join(lines)},
        ]
        try:
            data = self._json(self._chat(msg, schema, 400))
        except (ValueError, KeyError, urllib.error.URLError, OSError):
            return [], 0
        by_id = {c["id"]: c for c in claims}
        out, rejected = [], 0
        for v in data.get("verdicts", []):
            if not v.get("contradicted"):
                continue
            m = re.match(r"\s*(C\d+)\b", str(v.get("claim", "")))
            by_quote = {_norm(c["quote"]): c["id"] for c in claims}
            v["claim"] = m.group(1) if m else by_quote.get(_norm(str(v.get("claim", ""))), v.get("claim"))
            evs = [x for x in v.get("evidence", []) if x in ids]
            bogus = [x for x in v.get("evidence", []) if x not in ids]
            if v.get("claim") in by_id and evs and (v.get("shows") or "").strip():
                out.append({"claim": v["claim"], "evidence": evs, "says": by_id[v["claim"]]["quote"],
                            "shows": v["shows"].strip(), "source": "apertus", "dropped_ids": bogus})
            else:
                rejected += 1
                self.rejections.append({"task": "reconcile", "reason": "claim or evidence id does not exist", "answer": str(v)[:200]})
        self.rejected += rejected
        return out, rejected

    def explain(self, lang: str, verdict: list[dict], known_ids: set[str]) -> tuple[list[dict] | None, int]:
        """Rewrite the deterministic verdict for a non-technical reader, in `lang`.

        Each item carries a base sentence already written in `lang` and the
        concrete detail (in English). Apertus merges them into one plain
        sentence; a line in the wrong language is rejected."""
        schema = {"type": "object", "properties": {"lines": {"type": "array", "minItems": 5, "maxItems": 5, "items": {
            "type": "object", "properties": {"q": {"type": "integer"}, "text": {"type": "string"},
                                             "evidence": {"type": "array", "items": {"type": "string"}}},
            "required": ["q", "text", "evidence"]}}}, "required": ["lines"]}
        name = LANG_NAME[lang].split(" (")[0]
        items = "\n".join(f'{v["q"]}. base: "{v["base"]}" | who: {v["detail_en"] or "-"} | evidence: {", ".join(v["evidence"]) or "none"}'
                          for v in verdict)
        msg = [
            {"role": "system", "content": (
                f"You write for an elderly person or a pupil, in {LANG_NAME[lang]}. For each item write one short "
                f"sentence in {name}: start from the base sentence (already in {name}) and, when 'who' is not '-', "
                f"add the name of the service and its country, translated into {name}. At most 25 words, no "
                "technical jargon, no new facts. Copy the evidence ids. Answer in JSON.")},
            {"role": "user", "content": f"Language: {name}\n" + items},
        ]
        try:
            data = self._json(self._chat(msg, schema, 450))
        except (ValueError, KeyError, urllib.error.URLError, OSError):
            return None, 0
        out, rejected = [], 0
        by_q = {v["q"]: v for v in verdict}
        for ln in data.get("lines", []):
            q = ln.get("q")
            text = (ln.get("text") or "").strip()
            evs = [x for x in ln.get("evidence", []) if x in known_ids]
            if q in by_q and text and len(text.split()) <= 45 and language_ok(text, lang) and all(o["q"] != q for o in out):
                out.append({"q": q, "text": text, "evidence": evs or by_q[q]["evidence"]})
            else:
                rejected += 1
                why = "wrong language" if text and not language_ok(text, lang) else "too long, duplicate or unknown question"
                self.rejections.append({"task": f"explain:{lang}", "reason": why, "answer": text[:200]})
        self.rejected += rejected
        if len(out) != 5:
            # keep Apertus' valid lines, fill the others from templates (marked per line)
            have = {o["q"] for o in out}
            for v in verdict:
                if v["q"] not in have:
                    out.append({"q": v["q"], "text": v["base"], "evidence": v["evidence"], "template": True})
            if len([o for o in out if not o.get("template")]) < 3:
                return None, rejected
        return sorted(out, key=lambda x: x["q"]), rejected


NEGATIVE_SIGNALS = {"SDK_DEFAULT", "TUNNEL", "TELEMETRY_DEFAULT_ON", "TRACKER_DEP", "VENDOR_DEP",
                    "RUNTIME_DOWNLOAD", "MODEL_HUB", "OPAQUE", "MODEL_CLOSED"}


def contradicting(e: dict) -> bool:
    """A trace that can contradict a sovereignty claim: a foreign flow, telemetry, a download, an opaque file."""
    if e.get("signal") == "HOST":
        return registry.is_foreign(e.get("jurisdiction", "UNKNOWN"))
    return e.get("signal") in NEGATIVE_SIGNALS


# Distinctive function words: enough to tell the five languages apart.
_MARKERS = {
    "fr": {"le", "les", "des", "est", "vos", "votre", "pas", "une", "sur", "du", "ne", "sont", "aucun", "aucune"},
    "de": {"der", "die", "das", "und", "ist", "nicht", "ihre", "ein", "eine", "ohne", "im", "den", "sich", "es"},
    "it": {"di", "non", "un", "una", "sono", "gli", "del", "della", "dei", "lo", "si", "nessun", "anche"},
    "rm": {"betg", "quai", "ina", "las", "ils", "vossas", "voss", "da", "nua", "er", "sin", "tar", "tut", "dal", "vegn",
           "sa", "lascha", "gronda", "nagin", "nagina", "mintgin", "danovamain", "bandunan", "datas"},
    "en": {"the", "is", "and", "your", "not", "without", "of", "are", "it", "to", "no"},
}


def language_ok(text: str, lang: str) -> bool:
    words = re.findall(r"[a-zàâäéèêëîïôöùûüç']+", text.lower())
    score = {l: sum(w in m for w in words) for l, m in _MARKERS.items()}
    best = max(score.values())
    return best == 0 or score[lang] == best
