"""Aggregate, anonymous audit of a folder of public projects.

Ethics, enforced in code: only the aggregate is written to disk. No project
name, URL or per-project grade leaves this function.
"""

from __future__ import annotations

import collections
import datetime as dt
import json
from pathlib import Path

from . import __version__, registry
from .collect import scan
from .score import grade


def run(src: Path, out_dir: Path, llm=None) -> dict:
    projects = sorted(p for p in Path(src).iterdir() if p.is_dir() and not p.name.startswith("."))
    grades = collections.Counter()
    per_q = {q: collections.Counter() for q in range(1, 6)}
    foreign_ops = collections.Counter()
    n_foreign_llm = n_tel = n_offline = n_claim_gap = 0
    for p in projects:
        sc = scan(p)
        if sc.code_files == 0:
            continue
        g = grade(sc)
        grades[g["grade"]] += 1
        for qd in g["questions"]:
            per_q[qd["q"]][qd["level"]] += 1
        flows = [e for e in sc.evidence if e.signal in ("HOST", "SDK_DEFAULT", "TUNNEL", "TELEMETRY_DEFAULT_ON", "TRACKER_DEP")
                 and e.host and registry.is_foreign(e.jurisdiction)]
        for op in {e.operator for e in flows}:
            foreign_ops[op] += 1
        n_foreign_llm += any(e.category in ("llm-closed", "llm-open") for e in flows)
        n_tel += any(e.signal == "TELEMETRY_DEFAULT_ON" for e in sc.evidence)
        n_offline += g["questions"][2]["level"] in ("A", "B")
        n_claim_gap += bool(g["gaps"])
    n = sum(grades.values())
    pct = lambda k: round(100 * k / n) if n else 0
    agg = {
        "sigillum": __version__, "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "scope": "public Hugging Face Spaces mentioning Apertus (static analysis of the code, no request to running apps)",
        "count": n, "grades": {g: grades.get(g, 0) for g in "ABCDE"},
        "per_question": {q: dict(c) for q, c in per_q.items()},
        "pct": {"foreign_llm": pct(n_foreign_llm), "telemetry_on": pct(n_tel), "offline": pct(n_offline),
                "claim_contradicted": pct(n_claim_gap)},
        "top_foreign": [{"operator": op, "count": c} for op, c in foreign_ops.most_common(5)],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "aggregate.json").write_text(json.dumps(agg, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(agg, indent=1, ensure_ascii=False))
    return agg
