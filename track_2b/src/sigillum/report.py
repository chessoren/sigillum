"""Assemble a dated, expiring, tamper-evident seal report."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from . import __version__, i18n
from .apertus import Apertus
from .collect import scan
from .registry import REGISTRY_VERSION
from .score import grade

METHOD_VERSION = "1.0"
VALID_DAYS = 90


COUNTRY = {"US": "United States", "EU": "European Union", "CH": "Switzerland", "GLOBAL": "worldwide network",
           "UNKNOWN": "unknown location", "CN": "China", "CA": "Canada", "LOCAL": "this machine"}


def _who(reasons: list[dict], evidence_by_id: dict) -> str:
    """Only names and countries — the plain explanation needs nothing more."""
    names = []
    for r in reasons:
        for x in r["evidence"]:
            e = evidence_by_id.get(x, {})
            if e.get("host") and e.get("operator"):
                n = f'{e["operator"]} ({COUNTRY.get(e.get("jurisdiction"), e.get("jurisdiction"))})'
                if n not in names:
                    names.append(n)
    return ", ".join(names[:3])


def _verdict_facts(questions: list[dict], lang: str = "fr", evidence_by_id: dict | None = None) -> list[dict]:
    """The deterministic verdict, one fact per question (source for Apertus)."""
    evidence_by_id = evidence_by_id or {}
    facts = []
    for qd in questions:
        lvl = qd["level"]
        rs = [r for r in qd["reasons"] if r["level"] == lvl or lvl == "unknown"]
        ev = []
        for r in rs:
            ev.extend(x for x in r["evidence"] if x not in ev)
        facts.append({"q": qd["q"], "level": lvl, "base": i18n.PLAIN[qd["q"]][lvl][lang],
                      "plain_en": i18n.PLAIN[qd["q"]][lvl]["en"],
                      "detail_en": _who(rs, evidence_by_id),
                      "evidence": ev[:4]})
    return facts


def template_lines(questions: list[dict], lang: str) -> list[dict]:
    return [{"q": f["q"], "text": f["base"], "evidence": f["evidence"]} for f in _verdict_facts(questions, lang)]


def audit(path: str, name: str | None = None, llm: Apertus | None = None, langs=i18n.LANGS,
          progress=lambda msg: None, examined_at: dt.datetime | None = None) -> dict:
    progress("scan")
    sc = scan(path)
    progress("grade")
    g = grade(sc)
    evidence = [e.to_dict() for e in sc.evidence]
    known = {e["id"] for e in evidence}
    now = (examined_at or dt.datetime.now(dt.timezone.utc)).replace(microsecond=0)

    report = {
        "sigillum": {"version": __version__, "method": METHOD_VERSION, "registry": REGISTRY_VERSION},
        "project": {"name": name or sc.project_name, "commit": sc.commit or None, "files_scanned": sc.files_scanned,
                    "code_files": sc.code_files, "excluded": sc.excluded,
                    "dependencies": sum(len(v) for v in sc.deps.values())},
        "examined_at": now.isoformat(),
        "expires_at": (now + dt.timedelta(days=VALID_DAYS)).isoformat(),
        "grade": g["grade"],
        "label": i18n.GRADE_LABEL[g["grade"]],
        "weakest": g["weakest"],
        "unknown": g["unknown"],
        "questions": g["questions"],
        "evidence": evidence,
        "gaps": g["gaps"],
        "fixes": g["fixes"],
        "claims": {"apertus": [], "rejected": 0},
        "explanations": {},
        "apertus": {"used": False},
    }

    use_llm = llm is not None and llm.available()
    if use_llm:
        progress("apertus:claims")
        claims, _ = llm.extract_claims(sc.docs_text)
        report["claims"]["apertus"] = claims
        progress("apertus:reconcile")
        gaps, _ = llm.reconcile(claims, evidence)
        report["gaps"].extend(gaps)
    for lang in langs:
        lines = None
        if use_llm:
            progress(f"apertus:explain:{lang}")
            lines, _ = llm.explain(lang, _verdict_facts(g["questions"], lang, {e["id"]: e for e in evidence}), known)
        tpl = template_lines(g["questions"], lang)
        source = "template"
        if lines:
            same = all(a["text"].strip() == b["text"].strip() for a, b in zip(lines, tpl))
            source = "apertus-confirmed" if same else "apertus"
        report["explanations"][lang] = {"source": source, "lines": lines or tpl}
    if use_llm:
        report["claims"]["rejected"] = llm.rejected
        report["apertus"] = {"used": True, "model": llm.model, "endpoint": llm.jurisdiction(),
                             "calls": llm.calls, "seconds": round(llm.seconds, 1),
                             "answers_rejected_by_checks": llm.rejected,
                             "rejections": llm.rejections[:20]}
    elif llm is not None:
        report["apertus"] = {"used": False, "model": llm.model, "reason": "endpoint unreachable — templates used",
                             "endpoint": llm.jurisdiction()}

    core = {k: report[k] for k in ("project", "examined_at", "grade", "questions", "evidence", "gaps")}
    digest = hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    report["seal"] = {"sha256": digest, "id": digest[:12]}
    slug = re.sub(r"[^a-z0-9]+", "-", report["project"]["name"].lower()).strip("-")[:40] or "project"
    report["id"] = f"{slug}-{now.strftime('%Y%m%d-%H%M%S')}"
    progress("done")
    return report


def verify(report: dict) -> bool:
    """Recompute the seal hash: any edit to the graded content breaks it."""
    core = {k: report[k] for k in ("project", "examined_at", "grade", "questions", "evidence", "gaps")}
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == report["seal"]["sha256"]


def save(report: dict, out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{report['id']}.json"
    p.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return p


GRADE_FILL = {"A": "#DA291C", "B": "#E2574C", "C": "#EC8B83", "D": "#F4C3BF", "E": "#E9E6E6"}


def badge_svg(report: dict, lang: str = "en") -> str:
    """A small embeddable seal for README files (no external resources)."""
    g = report["grade"]
    label = report["label"][lang] if lang in report["label"] else report["label"]["en"]
    date = report["examined_at"][:10]
    fill = GRADE_FILL[g]
    ink = "#FFFFFF" if g in "AB" else "#1A0B0C"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="236" height="40" viewBox="0 0 236 40" role="img" aria-label="Sigillum {g}: {label}">
<rect width="236" height="40" rx="20" fill="#FFFFFF" stroke="#1A0B0C" stroke-opacity=".12"/>
<rect x="4" y="4" width="32" height="32" rx="16" fill="{fill}"/>
<text x="20" y="26" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="18" font-weight="700" fill="{ink}">{g}</text>
<text x="46" y="18" font-family="Helvetica,Arial,sans-serif" font-size="11" font-weight="600" fill="#1A0B0C">Sigillum · {label}</text>
<text x="46" y="31" font-family="Helvetica,Arial,sans-serif" font-size="10" fill="#1A0B0C" fill-opacity=".6">{date} · seal {report['seal']['id']}</text>
</svg>"""
