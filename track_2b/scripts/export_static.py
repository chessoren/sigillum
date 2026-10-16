"""Export the web interface and the real reports as a static site (for Netlify).

    python3 scripts/export_static.py dist/

The static demo serves the same pages and the same reports; examining a new
project needs the Python server (`make run`).
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sigillum import __version__, i18n  # noqa: E402
from sigillum.report import badge_svg  # noqa: E402
from sigillum.server import App  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "dist").resolve()
if out.exists():
    shutil.rmtree(out)
shutil.copytree(ROOT / "src/sigillum/web", out)
app = App(ROOT / "data")
api = out / "api"
(api / "reports").mkdir(parents=True)
(api / "badge").mkdir()
w = lambda p, obj: p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
reports = app.reports()
w(api / "reports.json", reports)
for r in reports:
    full = app.report(r["id"])
    w(api / "reports" / f"{r['id']}.json", full)
    (api / "badge" / f"{r['id']}.svg").write_text(badge_svg(full), encoding="utf-8")
w(api / "i18n.json", {"reason": i18n.REASON, "fix": i18n.FIX, "grade": i18n.GRADE_LABEL,
                      "question": i18n.QUESTION, "gap": i18n.GAP_TAG, "unknown": i18n.UNKNOWN})
w(api / "community.json", json.loads((ROOT / "data/community/aggregate.json").read_text()))
w(api / "samples.json", sorted(p.name for p in (ROOT / "data/samples").iterdir() if p.is_dir()))
w(api / "health.json", {"ok": True, "version": __version__, "static": True, "apertus": False})
(out / "_redirects").write_text(
    "/api/health        /api/health.json        200\n"
    "/api/reports       /api/reports.json       200\n"
    "/api/reports/:id   /api/reports/:id.json   200\n"
    "/api/i18n          /api/i18n.json          200\n"
    "/api/community     /api/community.json     200\n"
    "/api/samples       /api/samples.json       200\n")
(out / "_headers").write_text(
    "/*\n"
    "  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; connect-src 'self'; font-src 'self'; frame-ancestors 'none'\n"
    "  Referrer-Policy: no-referrer\n"
    "  X-Content-Type-Options: nosniff\n")
print(f"{len(reports)} reports → {out}")
