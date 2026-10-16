"""Deterministic grading. The language model never touches this file's output.

Rules (published in docs/method.md):
  * Each of the five questions gets a level A..E, or "unknown".
  * Proof rule: a claim without a trace never earns more than C.
  * Unknown is shown as unknown, and caps the final grade at C.
  * Weakest link: the final grade is the worst level among the five.
"""

from __future__ import annotations

from .collect import Evidence, Scan
from . import registry

LEVELS = "ABCDE"
QUESTIONS = {1: "model", 2: "data", 3: "offline", 4: "third_parties", 5: "verifiable"}

CONTENT_FOREIGN = {"llm-closed", "llm-open", "tunnel", "storage", "hosting", "auth"}
METADATA = {"analytics", "fonts", "cdn", "telemetry"}


def _worst(*levels: str) -> str:
    return max(levels, key=LEVELS.index)


class _Q:
    def __init__(self, n: int):
        self.n = n
        self.level: str | None = None   # None = unknown
        self.proof = "none"            # reproducible | trace | declared | none
        self.reasons: list[dict] = []
        self.fixes: list[dict] = []

    def push(self, level: str, code: str, ev: list[Evidence] | None = None, **params) -> None:
        ids = [e.id for e in (ev or [])]
        self.reasons.append({"code": code, "level": level, "evidence": ids, "params": params})
        self.level = level if self.level is None else _worst(self.level, level)

    def fix(self, code: str, ev: list[Evidence] | None = None, **params) -> None:
        f = {"code": code, "q": self.n, "evidence": [e.id for e in (ev or [])], "params": params}
        if f not in self.fixes:
            self.fixes.append(f)

    def out(self) -> dict:
        return {"q": self.n, "key": QUESTIONS[self.n], "level": self.level or "unknown",
                "proof": self.proof, "reasons": self.reasons, "fixes": self.fixes}


def _hosts(evs: list[Evidence]) -> str:
    seen = []
    for e in evs:
        label = f"{e.host} ({e.operator}, {e.jurisdiction})" if e.host else e.detail
        if label not in seen:
            seen.append(label)
    return ", ".join(seen[:4]) + ("…" if len(seen) > 4 else "")


def grade(sc: Scan) -> dict:
    ev = sc.evidence
    by = lambda q=None, sig=None, kind=None: [e for e in ev if (q is None or e.q == q)
                                               and (sig is None or e.signal in ([sig] if isinstance(sig, str) else sig))
                                               and (kind is None or e.kind == kind)]
    claims = by(kind="declaration")
    flows = [e for e in ev if e.signal in ("HOST", "SDK_DEFAULT", "TUNNEL") and e.jurisdiction not in ("LOCAL",)]
    llm_foreign = [e for e in flows if e.category in ("llm-closed", "llm-open") and registry.is_foreign(e.jurisdiction)]
    llm_swiss = [e for e in flows if e.jurisdiction == "CH" and e.category in ("swiss-infra", "swiss-tld")]
    local_serv = by(1, "LOCAL_SERVING")
    local_ep = by(1, "LOCAL_ENDPOINT")
    configurable = by(1, ["CONFIGURABLE_ENDPOINT", "SDK_OVERRIDDEN"])
    closed_names = by(1, "MODEL_CLOSED")
    open_names = by(1, "MODEL_OPEN")
    telemetry_on = by(4, "TELEMETRY_DEFAULT_ON")
    trackers = by(4, "TRACKER_DEP")
    vendors = by(4, "VENDOR_DEP")

    q = {n: _Q(n) for n in range(1, 6)}

    # ---------------- Q1 — where does the model live? -----------------------
    q1 = q[1]
    closed_foreign = [e for e in llm_foreign if e.category == "llm-closed"]
    open_foreign = [e for e in llm_foreign if e.category == "llm-open"]
    if closed_foreign:
        q1.push("E", "Q1_CLOSED_FOREIGN", closed_foreign, hosts=_hosts(closed_foreign))
        q1.fix("FIX_SERVE_LOCAL", closed_foreign)
    if open_foreign:
        q1.push("D", "Q1_OPEN_FOREIGN", open_foreign, hosts=_hosts(open_foreign))
        q1.fix("FIX_SERVE_LOCAL", open_foreign)
    if closed_names and not closed_foreign:
        q1.push("D", "Q1_CLOSED_NAME", closed_names, models=", ".join(sorted({e.detail for e in closed_names})))
        q1.fix("FIX_OPEN_MODEL", closed_names)
    if llm_swiss and not llm_foreign:
        q1.push("B", "Q1_SWISS", llm_swiss, hosts=_hosts(llm_swiss))
    if (local_serv or local_ep) and not llm_foreign:
        serving = ", ".join(sorted({e.detail for e in local_serv})) or "local endpoint"
        q1.push("A", "Q1_LOCAL", (local_serv or local_ep)[:4] + open_names[:2], serving=serving)
    if q1.level is None and configurable:
        q1.push("C", "Q1_CONFIGURABLE", configurable[:3])
        q1.fix("FIX_LOCAL_RECIPE", configurable[:1])
    q1_claims = [c for c in claims if c.detail in ("LOCAL_MODEL", "SOVEREIGN")]
    if q1.level is None and q1_claims:
        q1.push("C", "Q1_CLAIM_ONLY", q1_claims[:3])
        q1.fix("FIX_PROVE_CLAIM", q1_claims[:1])
    q1.proof = "trace" if any(r["code"] not in ("Q1_CLAIM_ONLY",) for r in q1.reasons) else ("declared" if q1.reasons else "none")

    # ---------------- Q2 — where does the data go? ---------------------------
    q2 = q[2]
    meta_flows = [e for e in flows if e.category in METADATA] + [e for e in telemetry_on + trackers if e.host]
    content_foreign = [e for e in flows if registry.is_foreign(e.jurisdiction) and e.category in CONTENT_FOREIGN
                       and e.jurisdiction != "EU"]
    content_eu = [e for e in flows if e.jurisdiction == "EU" and e.category in CONTENT_FOREIGN]
    unknown_hosts = [e for e in flows if e.jurisdiction == "UNKNOWN"]
    meta_foreign = [e for e in meta_flows if registry.is_foreign(e.jurisdiction) and e.jurisdiction != "EU"]
    meta_eu = [e for e in meta_flows if e.jurisdiction == "EU"]
    ch_flows = [e for e in flows if e.jurisdiction == "CH"]
    if content_foreign:
        q2.push("E", "Q2_CONTENT_FOREIGN", content_foreign, hosts=_hosts(content_foreign))
        q2.fix("FIX_KEEP_CONTENT", content_foreign)
    if content_eu:
        q2.push("D", "Q2_CONTENT_EU", content_eu, hosts=_hosts(content_eu))
    if meta_foreign:
        q2.push("D", "Q2_META_FOREIGN", meta_foreign, hosts=_hosts(meta_foreign))
        for e in meta_foreign:
            if e.category == "fonts":
                q2.fix("FIX_SELFHOST_FONTS", [e])
            elif e.category == "cdn":
                q2.fix("FIX_VENDOR_SCRIPTS", [e])
            elif e.category == "analytics" or e.signal == "TRACKER_DEP":
                q2.fix("FIX_REMOVE_ANALYTICS", [e])
    if meta_eu:
        q2.push("C", "Q2_META_EU", meta_eu, hosts=_hosts(meta_eu))
    if unknown_hosts:
        q2.push("C", "Q2_UNKNOWN_HOST", unknown_hosts, hosts=_hosts(unknown_hosts))
        q2.fix("FIX_DOCUMENT_HOSTS", unknown_hosts)
    if ch_flows and q2.level is None:
        q2.push("B", "Q2_SWISS_ONLY", ch_flows, hosts=_hosts(ch_flows))
    if q2.level is None and sc.code_files:
        q2.push("A", "Q2_NOTHING_LEAVES", local_ep[:3], files=sc.code_files)
    q2_claims = [c for c in claims if c.detail in ("NO_DATA_EXIT", "SWISS_HOSTING")]
    if q2.level is None and q2_claims:
        q2.push("C", "Q2_CLAIM_ONLY", q2_claims[:3])
    q2.proof = "trace" if q2.reasons and q2.reasons[0]["code"] != "Q2_CLAIM_ONLY" else ("declared" if q2.reasons else "none")

    # ---------------- Q3 — what happens without internet? --------------------
    q3 = q[3]
    cdn = [e for e in flows if e.category == "cdn"]
    fonts = [e for e in flows if e.category == "fonts"]
    downloads = by(3, ["RUNTIME_DOWNLOAD", "MODEL_HUB"])
    offline_test = by(3, "OFFLINE_TEST")
    if llm_foreign:
        q3.push("E", "Q3_STOPS", llm_foreign[:4], hosts=_hosts(llm_foreign))
    if cdn:
        q3.push("D", "Q3_CDN", cdn, hosts=_hosts(cdn))
        q3.fix("FIX_VENDOR_SCRIPTS", cdn)
    if downloads and not by(3, "OFFLINE_SWITCH"):
        q3.push("C", "Q3_DOWNLOAD", downloads[:3])
        q3.fix("FIX_BAKE_WEIGHTS", downloads[:1])
    if fonts:
        q3.push("C", "Q3_FONTS", fonts, hosts=_hosts(fonts))
    if not (local_serv or local_ep) and configurable and not llm_foreign:
        q3.push("C", "Q3_REMOTE_MODEL", configurable[:2])
    if q3.level is None and (local_serv or local_ep):
        if offline_test:
            q3.push("A", "Q3_OFFLINE_PROVEN", offline_test[:3] + local_serv[:1])
        else:
            q3.push("B", "Q3_OFFLINE_INFERRED", local_serv[:2] or local_ep[:2])
            q3.fix("FIX_OFFLINE_TEST")
    q3_claims = [c for c in claims if c.detail == "OFFLINE"]
    if q3.level is None and q3_claims:
        q3.push("C", "Q3_CLAIM_ONLY", q3_claims[:3])
        q3.fix("FIX_OFFLINE_TEST")
    q3.proof = ("reproducible" if offline_test and q3.level == "A" else
                "trace" if q3.reasons and q3.reasons[0]["code"] != "Q3_CLAIM_ONLY" else
                "declared" if q3.reasons else "none")

    # ---------------- Q4 — who else is in the loop? ---------------------------
    q4 = q[4]
    analytics_hosts = [e for e in flows if e.category == "analytics" and registry.is_foreign(e.jurisdiction)]
    opaque = by(4, ["OPAQUE", "NO_MANIFEST"])
    tel_off = by(4, "TELEMETRY_OFF")
    if trackers or analytics_hosts:
        q4.push("E", "Q4_TRACKERS", (trackers + analytics_hosts)[:5], hosts=_hosts(trackers + analytics_hosts))
        q4.fix("FIX_REMOVE_ANALYTICS", (trackers + analytics_hosts)[:2])
    if telemetry_on:
        q4.push("D", "Q4_TELEMETRY_ON", telemetry_on, frameworks=", ".join(e.detail.split(" ")[0] for e in telemetry_on))
        for e in telemetry_on:
            q4.fix("FIX_TELEMETRY_" + e.detail.split(" ")[0].upper().replace("VLLM", "VLLM"), [e])
    if vendors:
        q4.push("D", "Q4_VENDOR", vendors[:4], hosts=_hosts(vendors))
    if q4.level is None and opaque:
        q4.reasons.append({"code": "Q4_OPAQUE", "level": "unknown", "evidence": [e.id for e in opaque[:4]], "params": {}})
        q4.fix("FIX_MANIFEST", opaque[:1])
        q4.proof = "none"
    elif q4.level is None and sc.code_files:
        q4.push("A", "Q4_NONE", tel_off[:3], deps=sum(len(v) for v in sc.deps.values()))
    q4_claims = [c for c in claims if c.detail == "NO_THIRD_PARTY"]
    if q4.level is None and not opaque and q4_claims:
        q4.push("C", "Q4_CLAIM_ONLY", q4_claims[:2])
    if q4.proof == "none" and q4.level:
        q4.proof = "declared" if q4.reasons and q4.reasons[0]["code"] == "Q4_CLAIM_ONLY" else "trace"

    # ---------------- Q5 — can it be verified? ---------------------------------
    q5 = q[5]
    lic = by(5, "LICENSE")
    cont = by(5, "CONTAINER")
    lock = by(5, "LOCKFILE")
    tests = by(5, "TESTS")
    no_deps = not any(sc.deps.values())
    if not sc.code_files:
        q5.push("E", "Q5_NO_SOURCE", [])
        q5.fix("FIX_PUBLISH_CODE")
    elif not lic or lic[0].detail == "unrecognised":
        q5.push("D", "Q5_NO_LICENSE", lic)
        q5.fix("FIX_LICENSE")
    elif cont and (lock or no_deps) and tests:
        q5.push("A", "Q5_REPRODUCIBLE", lic + cont[:1] + lock[:1] + tests[:1], license=lic[0].detail)
    elif cont or lock:
        q5.push("B", "Q5_PARTIAL", lic + cont[:1] + lock[:1], license=lic[0].detail)
        if not tests:
            q5.fix("FIX_TESTS")
        if not lock and not no_deps:
            q5.fix("FIX_PIN")
        if not cont:
            q5.fix("FIX_CONTAINER")
    else:
        q5.push("C", "Q5_LICENSE_ONLY", lic, license=lic[0].detail)
        q5.fix("FIX_CONTAINER")
    q5.proof = "reproducible" if q5.level == "A" else ("trace" if q5.level in "BC" else "none")

    # ---------------- Final grade -------------------------------------------
    per = [q[n].out() for n in range(1, 6)]
    effective = [p["level"] if p["level"] != "unknown" else "C" for p in per]
    final = _worst(*effective)
    weakest = [p["q"] for p, eff in zip(per, effective) if eff == final]
    unknowns = [p["q"] for p in per if p["level"] == "unknown"]
    fixes, seen = [], set()
    for p in per:
        for f in p["fixes"]:
            if f["code"] not in seen:
                seen.add(f["code"])
                fixes.append(f)
    return {"grade": final, "weakest": weakest, "unknown": unknowns, "questions": per,
            "fixes": fixes, "gaps": find_gaps(sc)}


# ---------------------------------------------------------------------------
# Gaps: "the project says X, the traces show Y" — rule-based baseline.
# Apertus may add more (see apertus.reconcile); each must cite real evidence.
# ---------------------------------------------------------------------------

def find_gaps(sc: Scan) -> list[dict]:
    ev = sc.evidence
    flows = [e for e in ev if e.signal in ("HOST", "SDK_DEFAULT", "TUNNEL") and registry.is_foreign(e.jurisdiction)]
    contra = {
        "LOCAL_MODEL": [e for e in flows if e.category in ("llm-closed", "llm-open")],
        "SOVEREIGN": [e for e in flows if e.category in ("llm-closed", "llm-open", "tunnel", "analytics", "storage")]
                     + [e for e in ev if e.signal in ("TELEMETRY_DEFAULT_ON", "TRACKER_DEP")],
        "NO_DATA_EXIT": flows + [e for e in ev if e.signal in ("TELEMETRY_DEFAULT_ON", "TRACKER_DEP")],
        "SWISS_HOSTING": flows,
        "OFFLINE": [e for e in flows if e.category in ("llm-closed", "llm-open", "cdn")]
                   + [e for e in ev if e.signal in ("RUNTIME_DOWNLOAD", "MODEL_HUB")],
        "NO_THIRD_PARTY": [e for e in ev if e.signal in ("TELEMETRY_DEFAULT_ON", "TRACKER_DEP", "VENDOR_DEP")]
                          + [e for e in flows if e.category == "analytics"],
    }
    gaps = []
    seen = set()
    for c in [e for e in ev if e.kind == "declaration"]:
        hits = contra.get(c.detail, [])
        if not hits:
            continue
        key = (c.detail, tuple(sorted(h.id for h in hits)))
        if key in seen:
            continue
        seen.add(key)
        gaps.append({"claim": c.id, "tag": c.detail, "evidence": [h.id for h in hits[:4]], "source": "rule"})
    return gaps
