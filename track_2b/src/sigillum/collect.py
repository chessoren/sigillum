"""Evidence collection: read a project's files and record verifiable traces.

Every piece of evidence points to a file and a line that anyone can open.
Nothing here runs the project or contacts the network; the analysis is
static, deterministic and reproducible (same commit in, same evidence out).
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import registry

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    ".next", ".nuxt", ".svelte-kit", "site-packages", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode", "target", ".gradle", ".cache", "coverage",
}
CODE_EXT = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".html", ".htm",
    ".go", ".rs", ".java", ".kt", ".rb", ".php", ".sh", ".bash", ".ipynb", ".css", ".scss",
}
CONFIG_EXT = {".toml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".env", ".json"}
CONFIG_NAMES = {"dockerfile", "makefile", "procfile", "docker-compose.yml", "docker-compose.yaml",
                "compose.yml", "compose.yaml", ".env.example", "requirements.txt", "package.json",
                "pyproject.toml", "pipfile", "setup.py", "setup.cfg", "app.json", "space.yaml"}
DOC_EXT = {".md", ".rst", ".txt", ".adoc"}
OPAQUE_EXT = {".so", ".dll", ".exe", ".dylib", ".jar", ".wasm", ".bin", ".pyc", ".class"}
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock",
             "pipfile.lock", "requirements.lock", "cargo.lock", "go.sum", "bun.lockb"}
MAX_BYTES = 1_000_000

URL_RE = re.compile(r"(?:https?|wss?)://([A-Za-z0-9][A-Za-z0-9.\-]*[A-Za-z0-9](?::\d{2,5})?|\[::1\](?::\d+)?)")
COMMENT_RE = re.compile(r"^\s*(#|//|\*|/\*|<!--|--|;)")


@dataclass
class Evidence:
    q: int                 # question 1..5
    signal: str            # machine code, e.g. HOST, SDK_DEFAULT, LOCAL_SERVING
    kind: str              # trace | artifact | declaration | absence
    file: str = ""
    line: int = 0
    snippet: str = ""
    host: str = ""
    operator: str = ""
    jurisdiction: str = ""
    category: str = ""
    detail: str = ""
    id: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v not in ("", 0) or k in ("q", "line")}


@dataclass
class Scan:
    root: str
    files_scanned: int = 0
    code_files: int = 0
    doc_files: list[str] = field(default_factory=list)
    excluded: list[dict] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    deps: dict[str, list[str]] = field(default_factory=dict)  # manifest -> package names
    docs_text: str = ""
    commit: str = ""
    project_name: str = ""

    def add(self, ev: Evidence) -> None:
        key = (ev.q, ev.signal, ev.file, ev.line, ev.host, ev.detail)
        for e in self.evidence:
            if (e.q, e.signal, e.file, e.line, e.host, e.detail) == key:
                return
        self.evidence.append(ev)


# --------------------------------------------------------------------------
# Knowledge tables (public, documented in docs/method.md)
# --------------------------------------------------------------------------

PY_SDKS = {
    # package/import -> (vendor host when no base_url override, label)
    "openai": ("api.openai.com", "OpenAI SDK"),
    "anthropic": ("api.anthropic.com", "Anthropic SDK"),
    "google.generativeai": ("generativelanguage.googleapis.com", "Google Gemini SDK"),
    "google.genai": ("generativelanguage.googleapis.com", "Google GenAI SDK"),
    "mistralai": ("api.mistral.ai", "Mistral SDK"),
    "cohere": ("api.cohere.com", "Cohere SDK"),
    "groq": ("api.groq.com", "Groq SDK"),
    "together": ("api.together.xyz", "Together SDK"),
    "replicate": ("api.replicate.com", "Replicate SDK"),
}
JS_SDKS = {
    "openai": ("api.openai.com", "OpenAI SDK"),
    "@anthropic-ai/sdk": ("api.anthropic.com", "Anthropic SDK"),
    "@google/generative-ai": ("generativelanguage.googleapis.com", "Google Gemini SDK"),
    "@google/genai": ("generativelanguage.googleapis.com", "Google GenAI SDK"),
    "@mistralai/mistralai": ("api.mistral.ai", "Mistral SDK"),
    "groq-sdk": ("api.groq.com", "Groq SDK"),
    "@huggingface/inference": ("router.huggingface.co", "Hugging Face Inference SDK"),
}
TRACKER_PKGS = {
    # dependency name -> (host, label)
    "posthog": ("posthog.com", "PostHog"), "posthog-js": ("posthog.com", "PostHog"),
    "posthog-node": ("posthog.com", "PostHog"), "mixpanel": ("mixpanel.com", "Mixpanel"),
    "mixpanel-browser": ("mixpanel.com", "Mixpanel"),
    "@amplitude/analytics-browser": ("amplitude.com", "Amplitude"),
    "amplitude-analytics": ("amplitude.com", "Amplitude"),
    "@segment/analytics-next": ("segment.io", "Segment"), "analytics-python": ("segment.io", "Segment"),
    "segment-analytics-python": ("segment.io", "Segment"),
    "sentry-sdk": ("sentry.io", "Sentry"), "@sentry/browser": ("sentry.io", "Sentry"),
    "@sentry/react": ("sentry.io", "Sentry"), "@sentry/node": ("sentry.io", "Sentry"),
    "@sentry/nextjs": ("sentry.io", "Sentry"),
    "@vercel/analytics": ("vercel-insights.com", "Vercel Analytics"),
    "@vercel/speed-insights": ("vercel-insights.com", "Vercel Speed Insights"),
    "react-ga": ("google-analytics.com", "Google Analytics"),
    "react-ga4": ("google-analytics.com", "Google Analytics"),
    "@datadog/browser-rum": ("datadoghq.com", "Datadog RUM"), "ddtrace": ("datadoghq.com", "Datadog"),
    "langsmith": ("smith.langchain.com", "LangSmith"), "wandb": ("api.wandb.ai", "Weights & Biases"),
}
# Frameworks that phone home unless told not to: (dep names, import regex, off-switch regex, host)
TELEMETRY_DEFAULTS = [
    ("Streamlit", {"streamlit"}, r"^\s*import streamlit|^\s*from streamlit",
     r"gatherUsageStats\s*=\s*false|STREAMLIT_BROWSER_GATHER_USAGE_STATS\s*[=:]\s*['\"]?(false|0)",
     "data.streamlit.io"),
    ("Gradio", {"gradio"}, r"^\s*import gradio|^\s*from gradio",
     r"GRADIO_ANALYTICS_ENABLED\s*[=:]\s*['\"]?(false|0)|analytics_enabled\s*=\s*False",
     "api.gradio.app"),
    ("Chroma", {"chromadb"}, r"^\s*import chromadb|^\s*from chromadb",
     r"anonymized_telemetry\s*=\s*False|ANONYMIZED_TELEMETRY\s*[=:]\s*['\"]?(false|0)",
     "posthog.com"),
    ("vLLM", {"vllm"}, r"^\s*from vllm|^\s*import vllm|vllm/vllm-openai|vllm serve",
     r"VLLM_NO_USAGE_STATS\s*[=:]\s*['\"]?1|DO_NOT_TRACK\s*[=:]\s*['\"]?1",
     "usage.vllm.ai"),
]
LOCAL_SERVING = [
    (r"ghcr\.io/ggml-org/llama\.cpp|ggerganov/llama\.cpp|llama-server\b|from llama_cpp import|llama_cpp\.Llama", "llama.cpp"),
    (r"vllm/vllm-openai|vllm serve\b|from vllm import LLM", "vLLM"),
    (r"ollama/ollama|localhost:11434|127\.0\.0\.1:11434|ollama:11434|import ollama", "Ollama"),
    (r"text-generation-inference", "Hugging Face TGI"),
    (r"localai/localai", "LocalAI"),
    (r"AutoModelForCausalLM\.from_pretrained|AutoModelForImageTextToText\.from_pretrained|pipeline\(\s*['\"]text-generation", "Transformers (in-process)"),
    (r"\bmlx_lm\b", "MLX"),
    (r"@huggingface/transformers|@xenova/transformers|@mlc-ai/web-llm|navigator\.gpu", "In-browser (WebGPU/WASM, on the user's device)"),
]
ENDPOINT_ENV = re.compile(
    r"(LLM_BASE_URL|OPENAI_BASE_URL|OPENAI_API_BASE|APERTUS_BASE_URL|INFERENCE_URL|MODEL_ENDPOINT)")
OPEN_MODELS = re.compile(r"(apertus|swiss-ai/|llama[-_ ]?\d|mistral-7b|mixtral|qwen\d?|gemma|olmo|phi-[34]|falcon)", re.I)
CLOSED_MODELS = re.compile(r"[\"'](gpt-3\.5[\w.-]*|gpt-4[\w.-]*|gpt-5[\w.-]*|o[134]-[\w-]+|claude-[\w.-]+|gemini-[\w.-]+)[\"']", re.I)
RUNTIME_DOWNLOAD = re.compile(r"\.from_pretrained\(|hf_hub_download\(|snapshot_download\(|ollama pull|pipeline\(\s*['\"]")
OFFLINE_SWITCH = re.compile(r"HF_HUB_OFFLINE\s*[=:]\s*['\"]?1|TRANSFORMERS_OFFLINE\s*[=:]\s*['\"]?1|local_files_only\s*=\s*True")
OFFLINE_TEST = re.compile(r"network_mode:\s*['\"]?none|--network[= ]none|--network=none|internal:\s*true")
GRADIO_SHARE = re.compile(r"\.launch\([^)]*share\s*=\s*True")
LICENSES = [("Apache-2.0", r"Apache License"), ("MIT", r"MIT License|Permission is hereby granted, free of charge"),
            ("GPL", r"GNU GENERAL PUBLIC LICENSE"), ("AGPL", r"GNU AFFERO"), ("BSD", r"Redistribution and use in source and binary forms"),
            ("MPL-2.0", r"Mozilla Public License"), ("CC-BY-4.0", r"Attribution 4\.0"), ("EUPL", r"European Union Public Licen")]

# Claims people write in READMEs (en/fr/de/it). Tags map to the five questions.
CLAIM_PATTERNS = [
    ("LOCAL_MODEL", 1, r"runs? (entirely |fully |100% )?locally|local(ly)? hosted model|on[- ]prem(ise)?s?|self[- ]hosted|en local|tourne (en )?local|lokal (betrieben|ausgeführt|läuft)|in locale|eigene[nr]? (Server|Infrastruktur)"),
    ("SWISS_HOSTING", 2, r"hosted in switzerland|swiss (hosting|cloud|servers?|data residency)|h[ée]berg[ée]e? en suisse|in der schweiz gehostet|ospitat[oa] in svizzera|data stays? in switzerland|restent en suisse"),
    ("NO_DATA_EXIT", 2, r"no data (ever )?leaves|data never leaves|nothing leaves|aucune donn[ée]e ne (quitte|sort)|keine daten (verlassen|werden übertragen)|nessun dato (lascia|esce)|your data stays|privacy[- ]first|100% priv"),
    ("OFFLINE", 3, r"works? offline|offline[- ](first|capable|ready)|air[- ]?gapped|without (an )?internet|hors[- ]ligne|sans (connexion|internet)|ohne internet|offline[- ]fähig|senza (connessione|internet)"),
    ("NO_THIRD_PARTY", 4, r"no (tracking|telemetry|analytics|third[- ]part(y|ies))|zero tracking|aucun (suivi|traçage|tiers)|kein (tracking|telemetrie)|nessun tracciamento"),
    ("SOVEREIGN", 1, r"sovereign|souverain|souverän|sovran"),
    ("OPEN_SOURCE", 5, r"open[- ]source|code source ouvert|quelloffen|codice aperto"),
]


def _rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root)).replace(os.sep, "/")


def _load_ignore(root: Path) -> list[tuple[str, str]]:
    """`.sigillumignore`: `pattern  # reason`. Exclusions are published in the report."""
    f = root / ".sigillumignore"
    out = []
    if f.exists():
        for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw.strip() or raw.strip().startswith("#"):
                continue
            pat, _, reason = raw.partition("#")
            out.append((pat.strip(), reason.strip() or "no reason given"))
    return out


def _git_commit(root: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--short=12", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _is_build_file(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1].lower()
    return name == "makefile" or name.startswith("dockerfile") or name.endswith(".sh") or rel.startswith(".github/")


def _file_kind(path: Path) -> str:
    name = path.name.lower()
    ext = path.suffix.lower()
    if name in CONFIG_NAMES or name.startswith("dockerfile") or name.startswith(".env"):
        return "config"
    if ext in CODE_EXT:
        return "code"
    if ext in CONFIG_EXT:
        return "config"
    if ext in DOC_EXT or name.startswith("readme") or name in {"license", "licence", "notice"}:
        return "doc"
    if ext in OPAQUE_EXT:
        return "opaque"
    return "other"


def _snip(line: str) -> str:
    s = line.strip()
    return s if len(s) <= 160 else s[:157] + "..."


def _iter_notebook_lines(text: str) -> list[str]:
    try:
        nb = json.loads(text)
    except json.JSONDecodeError:
        return text.splitlines()
    lines: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = cell.get("source", [])
            lines.extend((src if isinstance(src, list) else src.splitlines()))
    return [l.rstrip("\n") for l in lines]


def scan(root_path: str | os.PathLike) -> Scan:
    root = Path(root_path).resolve()
    sc = Scan(root=str(root), commit=_git_commit(root), project_name=root.name)
    ignores = _load_ignore(root)
    used_ignores: dict[str, str] = {}

    texts: dict[str, list[str]] = {}
    kinds: dict[str, str] = {}
    artifacts = {"license": None, "container": [], "lock": [], "tests": [], "docs": [], "opaque": [], "manifest": []}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in filenames:
            p = Path(dirpath) / fn
            rel = _rel(root, p)
            hit = next(((pat, why) for pat, why in ignores
                        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.rstrip("/") + "/*")
                        or rel.startswith(pat.rstrip("*").rstrip("/") + "/")), None)
            if hit:
                used_ignores[hit[0]] = hit[1]
                # excluded from flow analysis, but the existence of tests still counts for verifiability
                if re.match(r"(test_.*\.py|.*_test\.py|.*\.test\.[jt]sx?|.*\.spec\.[jt]sx?)$", fn.lower()):
                    artifacts["tests"].append(rel)
                continue
            kind = _file_kind(p)
            low = fn.lower()
            if low in LOCKFILES:
                artifacts["lock"].append(rel)
            if low.startswith("dockerfile") or low in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
                artifacts["container"].append(rel)
            if low in {"requirements.txt", "package.json", "pyproject.toml", "pipfile", "setup.py", "cargo.toml", "go.mod"}:
                artifacts["manifest"].append(rel)
            if re.match(r"(test_.*\.py|.*_test\.py|.*\.test\.[jt]sx?|.*\.spec\.[jt]sx?)$", low) or "/tests/" in "/" + rel:
                artifacts["tests"].append(rel)
            if low in {"technical_report.md", "architecture.md", "method.md"} or rel.startswith("docs/"):
                artifacts["docs"].append(rel)
            if kind == "opaque":
                artifacts["opaque"].append(rel)
                continue
            if low.startswith("license") or low.startswith("licence") or low == "copying":
                try:
                    t = p.read_text(encoding="utf-8", errors="replace")[:4000]
                except OSError:
                    t = ""
                lic = next((name for name, rx in LICENSES if re.search(rx, t)), "unrecognised")
                if artifacts["license"] is None or lic != "unrecognised":
                    artifacts["license"] = (rel, lic)
                continue
            if kind == "other":
                continue
            try:
                if p.stat().st_size > MAX_BYTES:
                    continue
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            sc.files_scanned += 1
            lines = _iter_notebook_lines(text) if p.suffix == ".ipynb" else text.splitlines()
            if p.suffix in {".js", ".css"} and (".min." in fn or any(len(l) > 3000 for l in lines[:5])):
                artifacts["opaque"].append(rel)
                continue
            texts[rel] = lines
            kinds[rel] = kind
            if kind in ("code", "config"):
                sc.code_files += 1
            if kind == "doc":
                sc.doc_files.append(rel)

    sc.excluded = [{"pattern": k, "reason": v} for k, v in used_ignores.items()]

    # ---------------- dependency manifests --------------------------------
    for rel, lines in texts.items():
        name = rel.rsplit("/", 1)[-1].lower()
        if name == "requirements.txt" or name.endswith("requirements.txt"):
            pk = [re.split(r"[<>=!~\[; ]", l.strip(), maxsplit=1)[0].lower() for l in lines
                  if l.strip() and not l.strip().startswith(("#", "-"))]
            sc.deps[rel] = [x for x in pk if x]
        elif name == "package.json":
            try:
                pj = json.loads("\n".join(lines))
                sc.deps[rel] = sorted({*pj.get("dependencies", {}), *pj.get("devDependencies", {})})
            except json.JSONDecodeError:
                pass
        elif name == "pyproject.toml":
            blob = "\n".join(lines)
            m = re.search(r"dependencies\s*=\s*\[(.*?)\]", blob, re.S)
            if m:
                sc.deps[rel] = [re.split(r"[<>=!~\[; ]", x.strip().strip("'\""), maxsplit=1)[0].lower()
                                for x in m.group(1).split(",") if x.strip().strip("'\"")]
    all_deps = {d for v in sc.deps.values() for d in v}

    runtime = {r: l for r, l in texts.items() if kinds[r] in ("code", "config")}
    blob_all = "\n".join("\n".join(l) for l in runtime.values())

    # ---------------- Q2/Q1/Q4: network destinations in runtime files -------
    for rel, lines in runtime.items():
        build = _is_build_file(rel)
        for i, line in enumerate(lines, 1):
            if COMMENT_RE.match(line):
                continue
            for m in URL_RE.finditer(line):
                host = m.group(1)
                info = registry.classify(host)
                if info.category in ("docs",):
                    continue
                before = line[max(0, m.start() - 8):m.start()]
                if re.search(r"(href=[\"']?|\]\(|\$schema\"?\s*:\s*\")$", before) and info.category not in ("cdn", "fonts", "analytics"):
                    continue  # a hyperlink the reader may follow, not a request the software makes
                if build and info.category != "local":
                    sc.add(Evidence(q=5, signal="BUILD_FETCH", kind="trace", file=rel, line=i, snippet=_snip(line),
                                    host=host.lower(), operator=info.operator, jurisdiction=info.jurisdiction,
                                    category=info.category, detail="fetched at build time, not needed at runtime"))
                    continue
                q = 2
                sig = "HOST"
                if info.category == "local":
                    sig = "LOCAL_ENDPOINT"
                    q = 1
                elif info.category == "model-hub":
                    sig = "MODEL_HUB"
                    q = 3
                sc.add(Evidence(q=q, signal=sig, kind="trace", file=rel, line=i, snippet=_snip(line),
                                host=host.lower(), operator=info.operator, jurisdiction=info.jurisdiction,
                                category=info.category))

    # ---------------- SDKs with default foreign endpoints ------------------
    for rel, lines in runtime.items():
        joined = "\n".join(lines)
        overrides = bool(re.search(r"base_url\s*=|baseURL\s*:|api_base\s*=|OPENAI_BASE_URL|LLM_BASE_URL", joined))
        for i, line in enumerate(lines, 1):
            if COMMENT_RE.match(line):
                continue
            for mod, (host, label) in PY_SDKS.items():
                if re.match(rf"\s*(import {re.escape(mod)}\b|from {re.escape(mod)}(\.| import))", line):
                    info = registry.classify(host)
                    if overrides and mod == "openai":
                        sc.add(Evidence(q=1, signal="SDK_OVERRIDDEN", kind="trace", file=rel, line=i,
                                        snippet=_snip(line), detail=f"{label} pointed at a configurable endpoint"))
                    else:
                        sc.add(Evidence(q=2, signal="SDK_DEFAULT", kind="trace", file=rel, line=i,
                                        snippet=_snip(line), host=host, operator=info.operator,
                                        jurisdiction=info.jurisdiction, category=info.category,
                                        detail=f"{label} — default endpoint {host}"))
            for mod, (host, label) in JS_SDKS.items():
                if re.search(rf"from\s+['\"]{re.escape(mod)}['\"]|require\(\s*['\"]{re.escape(mod)}['\"]\s*\)", line):
                    info = registry.classify(host)
                    if overrides and mod == "openai":
                        sc.add(Evidence(q=1, signal="SDK_OVERRIDDEN", kind="trace", file=rel, line=i,
                                        snippet=_snip(line), detail=f"{label} pointed at a configurable endpoint"))
                    else:
                        sc.add(Evidence(q=2, signal="SDK_DEFAULT", kind="trace", file=rel, line=i,
                                        snippet=_snip(line), host=host, operator=info.operator,
                                        jurisdiction=info.jurisdiction, category=info.category,
                                        detail=f"{label} — default endpoint {host}"))
            if re.search(r"gr\.load\(\s*['\"]models/", line):
                info = registry.classify("router.huggingface.co")
                sc.add(Evidence(q=2, signal="SDK_DEFAULT", kind="trace", file=rel, line=i, snippet=_snip(line),
                                host="router.huggingface.co", operator=info.operator, jurisdiction="US",
                                category="llm-open", detail="gradio.load('models/…') — Hugging Face Inference Providers"))
            if re.search(r"InferenceClient\(", line) and not re.search(r"base_url|https?://(localhost|127\.)", line):
                info = registry.classify("router.huggingface.co")
                sc.add(Evidence(q=2, signal="SDK_DEFAULT", kind="trace", file=rel, line=i, snippet=_snip(line),
                                host="router.huggingface.co", operator=info.operator, jurisdiction="US",
                                category="llm-open", detail="huggingface_hub.InferenceClient — default HF Inference router"))
            if ENDPOINT_ENV.search(line):
                sc.add(Evidence(q=1, signal="CONFIGURABLE_ENDPOINT", kind="trace", file=rel, line=i,
                                snippet=_snip(line), detail=ENDPOINT_ENV.search(line).group(1)))
            for rx, label in LOCAL_SERVING:
                if re.search(rx, line):
                    sc.add(Evidence(q=1, signal="LOCAL_SERVING", kind="trace", file=rel, line=i,
                                    snippet=_snip(line), detail=label))
            mo = OPEN_MODELS.search(line)
            if mo and not line.strip().startswith(("http", "#")):
                sc.add(Evidence(q=1, signal="MODEL_OPEN", kind="trace", file=rel, line=i, snippet=_snip(line),
                                detail=mo.group(1)))
            mc = CLOSED_MODELS.search(line)
            if mc:
                sc.add(Evidence(q=1, signal="MODEL_CLOSED", kind="trace", file=rel, line=i, snippet=_snip(line),
                                detail=mc.group(1)))
            if GRADIO_SHARE.search(line):
                info = registry.classify("gradio.live")
                sc.add(Evidence(q=2, signal="TUNNEL", kind="trace", file=rel, line=i, snippet=_snip(line),
                                host="gradio.live", operator=info.operator, jurisdiction="US", category="tunnel",
                                detail="Gradio share=True relays every session through gradio.live"))
            if RUNTIME_DOWNLOAD.search(line) and not OFFLINE_SWITCH.search(blob_all) and not _is_build_file(rel):
                sc.add(Evidence(q=3, signal="RUNTIME_DOWNLOAD", kind="trace", file=rel, line=i, snippet=_snip(line),
                                detail="model weights fetched at start-up"))
            if OFFLINE_TEST.search(line):
                sc.add(Evidence(q=3, signal="OFFLINE_TEST", kind="artifact", file=rel, line=i, snippet=_snip(line),
                                detail="runs with networking disabled"))
            if OFFLINE_SWITCH.search(line):
                sc.add(Evidence(q=3, signal="OFFLINE_SWITCH", kind="trace", file=rel, line=i, snippet=_snip(line),
                                detail="model hub access disabled at runtime"))

    # ---------------- Q4: third parties in the loop -------------------------
    for rel, pk in sc.deps.items():
        for name in pk:
            if name in TRACKER_PKGS:
                host, label = TRACKER_PKGS[name]
                info = registry.classify(host)
                sc.add(Evidence(q=4, signal="TRACKER_DEP", kind="trace", file=rel, line=0, snippet=name,
                                host=host, operator=info.operator, jurisdiction=info.jurisdiction,
                                category=info.category, detail=f"{label} dependency"))
            if name == "openai" and any(e.signal == "SDK_OVERRIDDEN" for e in sc.evidence):
                continue  # used as a generic OpenAI-compatible client, pointed at a configurable endpoint
            if name in PY_SDKS or name in JS_SDKS or name in {"google-generativeai", "google-genai"}:
                host, label = (PY_SDKS.get(name) or JS_SDKS.get(name) or ("generativelanguage.googleapis.com", "Google SDK"))
                info = registry.classify(host)
                sc.add(Evidence(q=4, signal="VENDOR_DEP", kind="trace", file=rel, line=0, snippet=name,
                                host=host, operator=info.operator, jurisdiction=info.jurisdiction,
                                category=info.category, detail=f"{label} dependency"))
    for label, depnames, import_rx, off_rx, host in TELEMETRY_DEFAULTS:
        used_at = None
        for rel, lines in runtime.items():
            for i, line in enumerate(lines, 1):
                if re.search(import_rx, line):
                    used_at = used_at or (rel, i, _snip(line))
                    break
        if not used_at and depnames & all_deps:
            mf = next(r for r, v in sc.deps.items() if depnames & set(v))
            used_at = (mf, 0, ", ".join(sorted(depnames & all_deps)))
        if not used_at:
            continue
        off = re.search(off_rx, blob_all, re.I | re.M)
        info = registry.classify(host)
        if off:
            sc.add(Evidence(q=4, signal="TELEMETRY_OFF", kind="trace", file=used_at[0], line=used_at[1],
                            snippet=_snip(off.group(0)), detail=f"{label} telemetry explicitly disabled"))
        else:
            sc.add(Evidence(q=4, signal="TELEMETRY_DEFAULT_ON", kind="trace", file=used_at[0], line=used_at[1],
                            snippet=used_at[2], host=host, operator=info.operator, jurisdiction=info.jurisdiction,
                            category="telemetry",
                            detail=f"{label} sends usage statistics by default and no off-switch was found"))
    for rel in artifacts["opaque"][:20]:
        sc.add(Evidence(q=4, signal="OPAQUE", kind="trace", file=rel, detail="binary or minified file that cannot be audited"))
    if not artifacts["manifest"] and sc.code_files:
        sc.add(Evidence(q=4, signal="NO_MANIFEST", kind="absence",
                        detail="no dependency manifest: components cannot be enumerated"))

    # ---------------- Q5: verifiability artifacts ---------------------------
    if not artifacts["license"]:
        for rel in sc.doc_files:
            if rel.lower() == "readme.md":
                head = "\n".join(texts[rel][:30])
                fm = re.match(r"\s*---\s*\n(.*?)\n---", head, re.S)
                lm = re.search(r"^license:\s*([\w.\-]+)", fm.group(1), re.M) if fm else None
                if lm and lm.group(1).lower() not in ("other", "unknown", "none"):
                    artifacts["license"] = (rel, lm.group(1) + " (declared in README metadata)")
    if artifacts["license"]:
        rel, lic = artifacts["license"]
        sc.add(Evidence(q=5, signal="LICENSE", kind="artifact", file=rel, detail=lic))
    for rel in artifacts["container"][:3]:
        sc.add(Evidence(q=5, signal="CONTAINER", kind="artifact", file=rel, detail="reproducible container build"))
    for rel in artifacts["lock"][:3]:
        sc.add(Evidence(q=5, signal="LOCKFILE", kind="artifact", file=rel, detail="dependencies pinned"))
    pinned_req = [r for r, lines in texts.items() if r.endswith("requirements.txt")
                  and lines and all("==" in l for l in lines if l.strip() and not l.strip().startswith(("#", "-")))]
    for rel in pinned_req[:2]:
        sc.add(Evidence(q=5, signal="LOCKFILE", kind="artifact", file=rel, detail="all requirements pinned with =="))
    if not sc.deps and artifacts["manifest"] == [] and sc.code_files and re.search(r"^\s*import\s", blob_all, re.M):
        # stdlib-only projects have nothing to pin; record it as a fact, not a lockfile
        pass
    if artifacts["tests"]:
        sc.add(Evidence(q=5, signal="TESTS", kind="artifact", file=artifacts["tests"][0],
                        detail=f"{len(artifacts['tests'])} test file(s)"))
    if artifacts["docs"]:
        sc.add(Evidence(q=5, signal="DOCS", kind="artifact", file=artifacts["docs"][0],
                        detail=f"{len(artifacts['docs'])} documentation file(s)"))
    sc.add(Evidence(q=5, signal="SOURCE", kind="artifact", detail=f"{sc.code_files} code/config file(s) readable"))

    # ---------------- Declarations (what the project says about itself) ----
    doc_lines: list[str] = []
    for rel in sc.doc_files:
        lines = texts[rel]
        doc_lines.append(f"### {rel}")
        doc_lines.extend(lines[:400])
        for i, line in enumerate(lines, 1):
            for tag, q, rx in CLAIM_PATTERNS:
                if re.search(rx, line, re.I):
                    sc.add(Evidence(q=q, signal="CLAIM", kind="declaration", file=rel, line=i,
                                    snippet=_snip(line), detail=tag))
    sc.docs_text = "\n".join(doc_lines)[:12000]

    _cap(sc)
    _assign_ids(sc)
    return sc


CAPS = {"MODEL_OPEN": 3, "CONFIGURABLE_ENDPOINT": 4, "LOCAL_SERVING": 6, "CLAIM": 8, "MODEL_CLOSED": 4}


def _cap(sc: Scan) -> None:
    """Keep reports readable: repeated signals are capped (the first occurrences are kept)."""
    seen: dict[tuple, int] = {}
    kept = []
    for e in sc.evidence:
        k = (e.q, e.signal)
        seen[k] = seen.get(k, 0) + 1
        if seen[k] <= CAPS.get(e.signal, 1000):
            kept.append(e)
    sc.evidence = kept


def _assign_ids(sc: Scan) -> None:
    order = {"trace": 0, "artifact": 1, "absence": 2, "declaration": 3}
    sc.evidence.sort(key=lambda e: (e.q, order.get(e.kind, 9), e.signal, e.file, e.line, e.host))
    for n, e in enumerate(sc.evidence, 1):
        e.id = f"E{n:02d}"
