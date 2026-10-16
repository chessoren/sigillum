"""Command line: `python -m sigillum audit PATH`, `serve`, `community`, `verify`."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__, i18n
from .apertus import Apertus
from .report import audit, badge_svg, save, verify

DATA = Path(os.environ.get("SIGILLUM_DATA", Path(__file__).resolve().parents[2] / "data"))


def _llm(args) -> Apertus | None:
    if getattr(args, "no_llm", False):
        return None
    return Apertus(cache_dir=DATA / "cache")


def cmd_audit(args) -> int:
    langs = tuple(args.langs.split(",")) if args.langs else i18n.LANGS
    rep = audit(args.path, name=args.name, llm=_llm(args), langs=langs,
                progress=lambda m: print(f"  · {m}", file=sys.stderr))
    out = save(rep, args.out or DATA / "reports")
    q = " ".join(f"Q{x['q']}:{x['level'] if x['level'] != 'unknown' else '?'}" for x in rep["questions"])
    print(f"{rep['project']['name']}: {rep['grade']} — {rep['label']['en']}  [{q}]  gaps:{len(rep['gaps'])}  → {out}")
    if args.badge:
        Path(args.badge).write_text(badge_svg(rep), encoding="utf-8")
    return 0


def cmd_verify(args) -> int:
    rep = json.loads(Path(args.report).read_text(encoding="utf-8"))
    ok = verify(rep)
    print("seal intact" if ok else "SEAL BROKEN: graded content was modified")
    return 0 if ok else 1


def cmd_serve(args) -> int:
    from .server import serve
    serve(args.host, args.port, DATA)
    return 0


def cmd_community(args) -> int:
    from .community import run
    run(Path(args.dir), DATA / "community", llm=None)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sigillum", description=f"Sigillum {__version__} — sovereignty seal for AI tools")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="examine a project directory")
    a.add_argument("path")
    a.add_argument("--name")
    a.add_argument("--out")
    a.add_argument("--no-llm", action="store_true", help="skip Apertus (templates only)")
    a.add_argument("--langs", help="comma list among fr,de,it,rm,en")
    a.add_argument("--badge", help="write an SVG badge to this path")
    a.set_defaults(fn=cmd_audit)
    v = sub.add_parser("verify", help="check that a report's seal is intact")
    v.add_argument("report")
    v.set_defaults(fn=cmd_verify)
    s = sub.add_parser("serve", help="web interface")
    s.add_argument("--host", default=os.environ.get("SIGILLUM_HOST", "0.0.0.0"))
    s.add_argument("--port", type=int, default=int(os.environ.get("SIGILLUM_PORT", "8080")))
    s.set_defaults(fn=cmd_serve)
    c = sub.add_parser("community", help="aggregate, anonymous audit of a folder of public projects")
    c.add_argument("dir")
    c.set_defaults(fn=cmd_community)
    args = p.parse_args(argv)
    return args.fn(args)
