"""Web interface and JSON API — Python standard library only, no CDN, no telemetry."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import __version__, i18n
from .apertus import Apertus
from .report import audit, badge_svg, save

WEB = Path(__file__).resolve().parent / "web"
JOBS: dict[str, dict] = {}


class App:
    def __init__(self, data: Path):
        self.data = Path(data)
        self.reports_dir = self.data / "reports"
        self.samples = self.data / "samples"
        self.audit_root = Path(os.environ.get("SIGILLUM_AUDIT_ROOT", "/audit"))
        self.llm = Apertus(cache_dir=self.data / "cache")

    def reports(self) -> list[dict]:
        out = []
        for f in sorted(self.reports_dir.glob("*.json")):
            try:
                r = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            out.append({"id": r["id"], "name": r["project"]["name"], "grade": r["grade"], "label": r["label"],
                        "examined_at": r["examined_at"], "expires_at": r["expires_at"],
                        "levels": [q["level"] for q in r["questions"]], "gaps": len(r["gaps"]),
                        "commit": r["project"].get("commit"), "apertus": r.get("apertus", {}).get("used", False)})
        return sorted(out, key=lambda x: x["examined_at"], reverse=True)

    def report(self, rid: str) -> dict | None:
        if not re.fullmatch(r"[a-z0-9\-]+", rid):
            return None
        f = self.reports_dir / f"{rid}.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None

    def resolve_target(self, target: str) -> tuple[Path, str, Path | None]:
        """Only three kinds of targets: a bundled sample, a folder under SIGILLUM_AUDIT_ROOT, or a public https Git URL."""
        target = target.strip()
        if target.startswith("https://"):
            tmp = Path(tempfile.mkdtemp(prefix="sigillum-"))
            name = re.sub(r"\.git$", "", target.rstrip("/").rsplit("/", 1)[-1])
            r = subprocess.run(["git", "clone", "--depth", "1", "--quiet", target, str(tmp / name)],
                               capture_output=True, text=True, timeout=120,
                               env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"})
            if r.returncode != 0:
                shutil.rmtree(tmp, ignore_errors=True)
                raise ValueError("clone failed: " + (r.stderr.strip()[:200] or "unknown error"))
            return tmp / name, name, tmp
        name = target.removeprefix("samples/")
        for base in (self.samples, self.audit_root):
            p = (base / name).resolve()
            if base.exists() and p.is_dir() and str(p).startswith(str(base.resolve())):
                return p, p.name, None
        raise ValueError("unknown target: use a sample name, a folder under SIGILLUM_AUDIT_ROOT, or an https Git URL")

    def start_job(self, target: str, use_llm: bool, langs) -> str:
        jid = uuid.uuid4().hex[:10]
        JOBS[jid] = {"id": jid, "status": "running", "step": "queued", "target": target}

        def work():
            tmp = None
            try:
                path, name, tmp = self.resolve_target(target)
                rep = audit(str(path), name=name, llm=self.llm if use_llm else None, langs=langs,
                            progress=lambda m: JOBS[jid].update(step=m))
                save(rep, self.reports_dir)
                JOBS[jid].update(status="done", report=rep["id"], grade=rep["grade"])
            except Exception as e:  # report the failure to the UI, never crash the server
                JOBS[jid].update(status="error", error=str(e)[:300])
            finally:
                if tmp:
                    shutil.rmtree(tmp, ignore_errors=True)

        threading.Thread(target=work, daemon=True).start()
        return jid


def make_handler(app: App):
    class H(BaseHTTPRequestHandler):
        server_version = f"Sigillum/{__version__}"

        def log_message(self, fmt, *args):  # no access logs: nothing about visitors is kept
            pass

        def _send(self, code: int, body: bytes, ctype: str, cache: bool = False):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
                             "script-src 'self'; connect-src 'self'; font-src 'self'; frame-ancestors 'none'")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "public, max-age=3600" if cache else "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, code=200):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/health":
                return self._json({"ok": True, "version": __version__, "apertus": app.llm.available(),
                                   "model": app.llm.model, "endpoint": app.llm.jurisdiction()})
            if path == "/api/reports":
                return self._json(app.reports())
            m = re.fullmatch(r"/api/reports/([a-z0-9\-]+)", path)
            if m:
                r = app.report(m.group(1))
                return self._json(r) if r else self._json({"error": "not found"}, 404)
            m = re.fullmatch(r"/api/badge/([a-z0-9\-]+)\.svg", path)
            if m:
                r = app.report(m.group(1))
                if not r:
                    return self._json({"error": "not found"}, 404)
                return self._send(200, badge_svg(r).encode(), "image/svg+xml")
            if path == "/api/i18n":
                return self._json({"reason": i18n.REASON, "fix": i18n.FIX, "grade": i18n.GRADE_LABEL,
                                   "question": i18n.QUESTION, "gap": i18n.GAP_TAG, "unknown": i18n.UNKNOWN})
            if path == "/api/community":
                f = app.data / "community" / "aggregate.json"
                return self._json(json.loads(f.read_text(encoding="utf-8")) if f.exists() else {})
            if path == "/api/samples":
                return self._json(sorted(p.name for p in app.samples.iterdir() if p.is_dir()) if app.samples.exists() else [])
            m = re.fullmatch(r"/api/jobs/([a-f0-9]+)", path)
            if m:
                return self._json(JOBS.get(m.group(1), {"status": "unknown"}))
            # static files
            rel = path.lstrip("/") or "index.html"
            if rel.endswith("/"):
                rel += "index.html"
            f = (WEB / rel).resolve()
            if not str(f).startswith(str(WEB)) or not f.is_file():
                f = WEB / (rel + ".html")
                if not f.is_file():
                    return self._send(404, b"not found", "text/plain")
            ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype in ("application/javascript",):
                ctype += "; charset=utf-8"
            return self._send(200, f.read_bytes(), ctype, cache=f.suffix in (".woff2", ".svg", ".png", ".webp"))

        def do_POST(self):
            if urlparse(self.path).path != "/api/audit":
                return self._json({"error": "not found"}, 404)
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(min(n, 10_000)) or b"{}")
            except json.JSONDecodeError:
                return self._json({"error": "invalid json"}, 400)
            target = str(body.get("target", ""))[:300]
            if not target:
                return self._json({"error": "missing target"}, 400)
            langs = tuple(l for l in body.get("langs", i18n.LANGS) if l in i18n.LANGS) or i18n.LANGS
            jid = app.start_job(target, bool(body.get("apertus", True)), langs)
            return self._json({"job": jid}, 202)

    return H


def serve(host: str, port: int, data: Path) -> None:
    app = App(data)
    print(f"Sigillum {__version__} on http://{host}:{port}  ·  Apertus: "
          f"{'reachable at ' + app.llm.base_url if app.llm.available() else 'not reachable (templates will be used)'}")
    ThreadingHTTPServer((host, port), make_handler(app)).serve_forever()
