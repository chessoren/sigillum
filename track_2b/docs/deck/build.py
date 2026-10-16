"""Build the pitch deck (3:2 slides) from the real reports, then render PNG + PDF.

    python3 docs/deck/build.py            # writes docs/deck/deck.html
    node docs/deck/render.js              # writes docs/deck/slides/*.png
"""

import glob
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get("DECK_DATA", ROOT / "data"))
OUT = Path(__file__).resolve().parent
LANG = os.environ.get("DECK_LANG", "en")

reports = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(str(DATA / "reports" / "*.json")))]
by = {}
for r in reports:
    by.setdefault(r["project"]["name"], []).append(r)
for v in by.values():
    v.sort(key=lambda r: r["examined_at"])
latest = {k: v[-1] for k, v in by.items()}
comm = json.loads((DATA / "community" / "aggregate.json").read_text())
e = html.escape

ICON = {
    1: '<rect x="6" y="6" width="12" height="12" rx="2.5"/><path d="M9.5 2.5v3.5M14.5 2.5v3.5M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/>',
    2: '<path d="M12 15V3"/><path d="m7 7.5 5-4.5 5 4.5"/><path d="M4.5 13v6a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-6"/>',
    3: '<path d="m3 3 18 18"/><path d="M8.6 16.4a5 5 0 0 1 6.3-.4"/><path d="M5 12.7a10 10 0 0 1 4.1-2.4"/><path d="M14.5 10.4A10 10 0 0 1 19 12.7"/><path d="M1.7 9.1a15 15 0 0 1 4-2.6"/><path d="M10.6 5.1A15 15 0 0 1 22.3 9.1"/><circle cx="12" cy="19.6" r="1" fill="currentColor" stroke="none"/>',
    4: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    5: '<circle cx="10.5" cy="10.5" r="7"/><path d="m20.5 20.5-4.9-4.9"/><path d="m7.5 10.6 2.1 2.1 3.9-4"/>',
}
SHORT = {1: "Model", 2: "Data", 3: "Offline", 4: "Third parties", 5: "Verifiable"}
LABEL = {"A": "Fully sovereign", "B": "Largely sovereign", "C": "Partial or unproven", "D": "Foreign dependencies", "E": "Dependent on foreign services"}
CROSS = '<svg class="cross" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#FF0000"/><rect x="13" y="6" width="6" height="20" fill="#fff"/><rect x="6" y="13" width="20" height="6" fill="#fff"/></svg>'


def icon(q, size=24):
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[q]}</svg>'


def lv(l):
    return "g-unknown" if l == "unknown" else f"g-{l}"


def seal(r, big=False, scale=1.0):
    levels = [q["level"] for q in r["questions"]]
    sc = "".join(f'<span class="g-{g} {"on" if g == r["grade"] else ""}">{g}</span>' for g in "ABCDE")
    pics = "".join(f'<div class="picto"><div class="disc {lv(l)}">{icon(i + 1)}<span class="lvl">{"?" if l == "unknown" else l}</span></div><span class="cap">{SHORT[i + 1]}</span></div>' for i, l in enumerate(levels))
    meta = (f'<div class="seal-meta"><span>Examined <b>{r["examined_at"][:10]}</b></span>'
            + (f'<span>commit <b>{e(r["project"]["commit"])}</b></span>' if r["project"].get("commit") else "")
            + f'<span>expires <b>{r["expires_at"][:10]}</b></span><span>seal <b>#{r["seal"]["id"]}</b></span></div>') if big else ""
    return (f'<div class="seal-card {"big" if big else ""}" style="transform:scale({scale});transform-origin:center">'
            f'<div class="seal-top"><span class="seal-brand">{CROSS} Sigillum</span><span class="badge">{r["examined_at"][:10]}</span></div>'
            f'<h3 class="seal-name">{e(r["project"]["name"])}</h3><div class="scale">{sc}</div>'
            f'<p class="seal-verdict">{r["grade"]} — {LABEL[r["grade"]]}</p><div class="pictos">{pics}</div>{meta}</div>')


def gap(r):
    g = next((x for x in r["gaps"] if x["source"] == "apertus"), r["gaps"][0] if r["gaps"] else None)
    if not g:
        return ""
    ev = {x["id"]: x for x in r["evidence"]}
    claim = g.get("says") or ev.get(g["claim"], {}).get("snippet", "")
    traces = [ev[i] for i in g["evidence"] if i in ev]
    shows = e(g["shows"]) if g.get("shows") else "<br>".join(f'{e(t["host"])} → {e(t["operator"])}' for t in traces if t.get("host"))
    srcs = "".join(f'<span class="src">' + (f'<span class="jur {t.get("jurisdiction", "")}">{t.get("jurisdiction", "")}</span> {e(t["host"])} · ' if t.get("host") else f'{e(t.get("detail", ""))} · ') + f'{e(t.get("file", ""))}:{t.get("line", "")}</span>' for t in traces)
    return (f'<div class="gap" style="font-size:1.25em"><div class="says"><span class="k">The project says</span><blockquote>“{e(claim)}”</blockquote><span class="src">README.md</span></div>'
            f'<div class="shows"><span class="k">The traces show</span><span class="trace">{shows}</span>{srcs}</div>'
            f'<div class="gap-foot"><span class="badge {"apertus" if g["source"] == "apertus" else ""}">{"Found by Apertus" if g["source"] == "apertus" else "Rule"}</span>'
            + "".join(f'<span class="ev">{i}</span>' for i in g["evidence"]) + '<span>— every ID points to a file and a line</span></div></div>')


ae = by.get("school-assistant", [])
v1, v2 = (ae[0], ae[-1]) if len(ae) > 1 else (latest.get("school-assistant"),) * 2
sig = by.get("sigillum", [])
self_first, self_last = (sig[0], sig[-1]) if sig else (None, None)
apertus_reports = [r for r in latest.values() if r.get("apertus", {}).get("used")]
calls = sum(r["apertus"]["calls"] for r in apertus_reports)
rejected = sum(r["apertus"]["answers_rejected_by_checks"] for r in apertus_reports)
secs = [r["apertus"]["seconds"] for r in apertus_reports]
avg_min = round(sum(secs) / len(secs) / 60, 1) if secs else 0
civ = latest.get("civicgpt")
langs_line = {l: civ["explanations"][l]["lines"][1]["text"] for l in ("de", "fr", "it", "rm")} if civ else {}

slides = []


def S(body, cls=""):
    slides.append(f'<section class="slide {cls}">{body}<footer class="sf"><span>{CROSS} Sigillum</span><span>Hack Apertus 2026 · Track 2B</span><span>{len(slides) + 1:02d}</span></footer></section>')


# 1 — cover
S(f'''<div class="cover"><div class="cover-l"><div class="brand">{CROSS}<span class="wordmark">Sigillum</span></div>
<h1 class="type-heading-xl">Sovereign?<br>Prove it.</h1>
<p class="type-lead">A sovereignty seal for AI tools — from A to E, with proof behind every answer. Built with Apertus, applied to ourselves first.</p>
<p class="muted small">Sigillum is Latin for “seal”, as Apertus is Latin for “open”.</p></div>
<div class="cover-r">{seal(latest["municipal-assistant"], big=True)}</div></div>''', "shellbg")

# 2 — problem
S('''<div class="center"><span class="type-eyebrow">The problem</span><h2 class="type-heading-l">Everyone says “sovereign”.<br>Nobody measures it.</h2></div>
<div class="three">
<div class="card"><h3>Unverifiable promises</h3><p>A public buyer cannot tell a sovereign tool from one that only says so.</p></div>
<div class="card"><h3>Hidden dependencies</h3><p>An app on an open model can still send data to a foreign API, an analytics service or a CDN — or stop when the connection drops.</p></div>
<div class="card"><h3>No common yardstick</h3><p>Two teams that say “sovereign” do not mean the same thing. Organisers cannot tell which projects to showcase.</p></div></div>''')

# 3 — the idea
S(f'''<div class="split"><div><span class="type-eyebrow">The idea</span><h2 class="type-heading-l">One letter.<br>Five pictograms.<br>A proof for each.</h2>
<p class="type-lead">Before the energy label, we bought fridges on the seller's word. Sigillum does for AI sovereignty what the label did for energy: a simple sign, backed by a public method.</p></div>
<div class="center-v">{seal(v1, big=True) if v1 else ""}</div></div>''')

# 4 — five questions
qa = {1: ("Where does the model live?", "On hardware the organisation controls", "Closed model at a foreign company"),
      2: ("Where does the data go?", "Nothing leaves", "Questions and documents leave the country"),
      3: ("What happens without internet?", "Everything works — and it is tested", "Everything stops"),
      4: ("Who else is in the loop?", "Nobody: no tracking, no telemetry", "Trackers observe the users"),
      5: ("Can it be verified?", "Licence, reproducible build, tests", "Nothing to check")}
S('<div class="center"><span class="type-eyebrow">The five questions</span><h2 class="type-heading-l">Five questions. One proof for each.</h2></div><div class="qgrid">'
  + "".join(f'<div class="q-card"><div class="disc">{icon(q, 26)}</div><h3>{t}</h3><ul><li><i class="g-A">A</i><span>{a}</span></li><li><i class="g-E">E</i><span>{b}</span></li><li><i class="g-unknown">?</i><span>unknown — never guessed</span></li></ul></div>' for q, (t, a, b) in qa.items())
  + '</div><p class="center muted" style="margin-top:28px">Sigillum reads code and configuration — never user data.</p>')

# 5 — three rules
S('''<div class="center"><span class="type-eyebrow">The method</span><h2 class="type-heading-l">Three rules make the grade credible.</h2></div><div class="three">
<div class="card big"><div class="num">1</div><h3>The proof rule</h3><p>A claim without a trace never earns more than C. Missing information is shown as <b>unknown</b> — and caps the grade at C.</p></div>
<div class="card big"><div class="num">2</div><h3>The weakest link</h3><p>The final grade is the worst of the five answers. Perfect on four but data goes abroad? Not an A.</p></div>
<div class="card big"><div class="num">3</div><h3>A dated, tamper-evident seal</h3><p>Date, commit, method version and a SHA-256 fingerprint. It expires after 90 days: a project that changes must be examined again.</p></div></div>''')

# 6 — Apertus
S(f'''<div class="split"><div><span class="badge apertus">Apertus v1.5 8B · local</span><h2 class="type-heading-l" style="margin-top:18px">Apertus reads, reconciles and explains. The evidence decides.</h2>
<p class="type-lead">The grade never depends on the model. Apertus does what fixed rules cannot — and every answer is checked before use.</p></div>
<div class="stack">
<div class="card row"><div class="num">1</div><div><h3>Reads</h3><p>Extracts what the documentation claims about sovereignty. A quote must exist word for word.</p></div></div>
<div class="card row"><div class="num">2</div><div><h3>Reconciles</h3><p>Sets each claim against the code traces and names the gap. It must cite evidence IDs that exist.</p></div></div>
<div class="card row"><div class="num">3</div><div><h3>Explains</h3><p>Writes — or confirms — the verdict in plain German, French, Italian and Romansh. A line in the wrong language is rejected.</p></div></div>
<p class="muted">Per project: up to 7 Apertus calls (read 1 · reconcile 1 · explain 5) · about 5 minutes on 4 CPU cores, no GPU · every rejected answer is logged as feedback for the Apertus team</p></div></div>''')

# 7 — the gap
S(f'''<div class="center"><span class="type-eyebrow">The moment that matters</span><h2 class="type-heading-l">When what is said and what is done diverge, Sigillum shows it.</h2></div>
<div style="max-width:1300px;margin:48px auto 0">{gap(v1) if v1 else ""}</div>
<p class="center muted" style="margin-top:28px">Calmly, with evidence, without accusing anyone. Example project built by the Sigillum team.</p>''')

# 8 — four languages
S('<div class="center"><span class="type-eyebrow">Four national languages</span><h2 class="type-heading-l">Explained in the four national languages.</h2><p class="type-lead">So that sovereignty is understood by the people it is meant to protect. Here: “Where does the data go?” for the closed-model example.</p></div><div class="four">'
  + "".join(f'<div class="card"><span class="type-eyebrow">{n}</span><p class="quote">{e(langs_line.get(l, ""))}</p><span class="badge {"apertus" if civ and civ["explanations"][l]["source"].startswith("apertus") else ""}">{("Written by Apertus" if civ["explanations"][l]["source"] == "apertus" else "Checked by Apertus") if civ and civ["explanations"][l]["source"].startswith("apertus") else "reviewed template"}</span></div>' for l, n in (("de", "Deutsch"), ("fr", "Français"), ("it", "Italiano"), ("rm", "Rumantsch")))
  + '</div>')

# 9 — scene 1
trio = [latest.get(n) for n in ("municipal-assistant", "town-hall-chat", "civicgpt")]
S('<div class="center"><span class="type-eyebrow">Scene 1 · a municipal CIO</span><h2 class="type-heading-l">Three vendors say “sovereign”. Two minutes to decide.</h2></div><div class="three seals">'
  + "".join(seal(r) for r in trio if r)
  + '</div><p class="center type-lead" style="margin-top:36px">An A; a C with “unknown” on question 4 — the question to ask that vendor; an E, because the data leaves the country.</p>')

# 10 — scene 2
if v1 and v2:
    S(f'''<div class="split"><div><span class="type-eyebrow">Scene 2 · a team that wants to improve</span><h2 class="type-heading-l">Not a sanction: a roadmap.</h2>
<p class="type-lead">Each report lists concrete fixes. The team fixed three of them and moved from {v1["grade"]} to {v2["grade"]}. The history keeps the before and after.</p>
<ol class="fixes">{"".join(f"<li><span>{e(x)}</span></li>" for x in ["Remove the CDN script — bundle it", "Switch off Streamlit usage statistics", "Serve Apertus on the school's server (llama.cpp)"])}</ol></div>
<div class="duo">{seal(v1, scale=.92)}<div class="arrow">→</div>{seal(v2, scale=.92)}</div></div>''')

# 11 — community
mx = max(comm["grades"].values()) or 1
S(f'''<div class="split"><div><span class="type-eyebrow">The headline · aggregated and anonymous</span><h2 class="type-heading-l">We measured the public Apertus ecosystem.</h2>
<p class="type-lead">Hack Apertus submissions are public only after 24 October. So we applied the seal to every public Hugging Face Space that uses Apertus — without naming anyone.</p>
<p class="muted">Static analysis of public code only · no request to running apps · no data about users · the aggregation code cannot output names.</p></div>
<div class="stack"><div class="card"><div style="display:flex;align-items:baseline;gap:14px"><span class="stat">{comm["count"]}</span><span>public Apertus projects examined</span></div>
<div class="bars">{"".join(f'<div class="bar"><i class="g-{g}">{g}</i><div class="track"><div class="fill" style="width:{100 * comm["grades"][g] / mx}%;background:var(--grade-{g.lower()})"></div></div><span>{comm["grades"][g]}</span></div>' for g in "ABCDE")}</div></div>
<div class="three tight"><div class="card"><span class="stat s">{comm["pct"]["foreign_llm"]}%</span><p>call the model through a foreign service</p></div><div class="card"><span class="stat s">{comm["pct"]["telemetry_on"]}%</span><p>ship telemetry on by default</p></div><div class="card"><span class="stat s">{comm["pct"]["offline"]}%</span><p>proven or likely to work offline</p></div></div>
<p class="muted">Most frequent foreign dependency: {e(comm["top_foreign"][0]["operator"])} ({comm["top_foreign"][0]["count"]}/{comm["count"]}) — a one-line fix.</p></div></div>''')

# 12 — ourselves first
if self_last:
    S(f'''<div class="split"><div><span class="type-eyebrow">Scene bonus · the jury opens our seal</span><h2 class="type-heading-l">We started with ourselves.</h2>
<p class="type-lead">Sigillum's first examination of itself gave <b>{self_first["grade"]}</b>: no licence file in the project folder. Fixed, re-examined: <b>{self_last["grade"]}</b>. Then we published our limits.</p>
<ul class="limits"><li>Static analysis only — runtime-only behaviour can be missed</li><li>Hand-curated registry: unknown hosts are reported as unknown, never as safe</li><li>Apertus 8B makes occasional German errors; Romansh needs a native proof-reader</li><li>Exclusions are self-declared — and published in every report</li></ul></div>
<div class="duo">{seal(self_first, scale=.92)}<div class="arrow">→</div>{seal(self_last, scale=.92)}</div></div>''')

# 13 — sovereign deployability
S('''<div class="center"><span class="type-eyebrow">Sovereign deployability · air-gapped</span><h2 class="type-heading-l">The tool runs offline — and proves it.</h2></div>
<div class="arch"><div class="box">Browser<br><small>no CDN, fonts bundled, strict CSP</small></div><div class="ar">→</div>
<div class="box red">Sigillum<br><small>Python standard library only · 0 runtime dependencies</small></div><div class="ar">→</div>
<div class="box ink">Apertus v1.5 8B<br><small>llama.cpp, on the same machine</small></div></div>
<div class="three tight" style="margin-top:40px"><div class="card"><span class="stat s">0</span><p>outbound requests at runtime (except the configured Apertus endpoint)</p></div>
<div class="card"><span class="stat s">18 + 5</span><p>tests and sample audits passing inside <code>docker --network none</code></p></div>
<div class="card"><span class="stat s">70 ms</span><p>deterministic examination per project · Apertus ≈ 5 min on 4 CPU cores · CHF 0 marginal cost</p></div></div>''')

# 14 — criteria
S('''<div class="center"><span class="type-eyebrow">Track 2B criteria</span><h2 class="type-heading-l">Built for the jury's five criteria.</h2></div>
<table class="crit"><tr><td>Purposeful use of AI</td><td>Apertus reads, reconciles and explains — where fixed rules fail; the evidence sets the grade</td></tr>
<tr><td>Technical rigour</td><td>Proof rule, weakest link, “unknown” shown, answers checked and rejections counted, 18 tests, false positives fixed and documented</td></tr>
<tr><td>Value, cost &amp; scalability</td><td>70 ms per project deterministic, minutes with Apertus on a CPU; any repository; one shared language for buyers, teams and organisers</td></tr>
<tr><td>Sovereign deployability</td><td>It is the subject: air-gapped by design, offline test in Docker, Sigillum examined by Sigillum</td></tr>
<tr><td>Implementation feasibility</td><td>Working end to end today: <code>make run</code>, CLI, web UI, JSON reports, badges</td></tr></table>''')

# 15 — close
S('''<div class="close"><h2 class="type-heading-xl">Sovereignty is not declared.<br>It is proven.</h2>
<p class="type-lead">So that sovereign AI does not remain a slogan, Sigillum makes it a common, open and verifiable rule of the game — ready for the on-site hacks and the May 2027 finals.</p>
<p class="type-lead" style="font-family:var(--font-display);color:var(--color-ink-900)">Apertus is open so that trust can be verified. Sigillum makes it readable.</p>
<p class="muted">Open source · Apache-2.0 · CC-BY-4.0 · Transparency instrument, not an official certification</p></div>''', "shellbg")

CSS = (ROOT / "src/sigillum/web/styles.css").read_text().replace('url("fonts/', 'url("../../src/sigillum/web/fonts/')
DECK_CSS = """
body{margin:0;background:#ddd}
.slide{width:1800px;height:1200px;background:#fff;position:relative;overflow:hidden;box-sizing:border-box;padding:96px 120px 120px;display:flex;flex-direction:column;justify-content:center;gap:12px;page-break-after:always;font-size:22px}
.slide.shellbg{background:radial-gradient(120% 90% at 50% 0%,#fbf8f8 0%,#f3efef 60%,#efeaea 100%)}
.sf{position:absolute;left:120px;right:120px;bottom:44px;display:flex;justify-content:space-between;align-items:center;font-size:15px;color:var(--color-text-tertiary)}
.sf span:first-child{display:flex;align-items:center;gap:8px;font-family:var(--font-display);font-size:20px;color:var(--color-ink-900)}
.sf .cross{width:20px;height:20px}
.type-heading-l{font-size:84px}.type-heading-xl{font-size:132px}.type-lead{font-size:30px;max-width:30ch}
.center{text-align:center;display:grid;justify-items:center;gap:18px}.center .type-lead{max-width:44ch}
.center-v{display:grid;place-items:center}
.cover{display:grid;grid-template-columns:1.15fr 1fr;gap:80px;align-items:center}
.cover-l{display:grid;gap:30px}.brand{display:flex;align-items:center;gap:14px}.brand .cross{width:44px;height:44px}.brand .wordmark{font-size:44px}
.small{font-size:20px}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:56px}
.three.tight{margin-top:0;gap:18px}
.three.seals{align-items:center;justify-items:center}
.four{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-top:56px}
.card{padding:34px;border-radius:32px;gap:16px}.card h3{font-size:30px;letter-spacing:-.04em;font-weight:500}.card p{margin:0;font-size:22px;color:var(--color-text-secondary);line-height:1.4;letter-spacing:-.02em}
.card.big{padding:44px}.card.row{display:grid;grid-template-columns:56px 1fr;gap:20px;align-items:start;padding:26px 30px}
.num{width:52px;height:52px;border-radius:999px;background:var(--color-red-600);color:#fff;display:grid;place-items:center;font-weight:700;font-size:22px}
.split{display:grid;grid-template-columns:1fr 1fr;gap:90px;align-items:center}
.split > div:first-child{display:grid;gap:26px}
.stack{display:grid;gap:18px}
.quote{font-family:var(--font-display);font-size:30px !important;line-height:1.2 !important;color:var(--color-ink-900) !important;letter-spacing:-.03em !important}
.qgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:20px;margin-top:56px}
.qgrid .q-card{padding:28px;gap:18px}.qgrid .q-card h3{font-size:24px}.qgrid .q-card ul{font-size:18px;gap:12px}.qgrid .q-card li{grid-template-columns:28px 1fr}.qgrid .q-card li i{width:28px;height:28px;font-size:14px}.qgrid .disc{width:56px;height:56px}
.qgrid .q-card:nth-child(even){margin-top:56px}
.duo{display:flex;align-items:center;gap:18px;justify-content:center}.duo .seal-card{width:400px}.arrow{font-size:56px;color:var(--color-text-tertiary)}
.stat{font-size:110px}.stat.s{font-size:76px}
.bars{gap:12px}.bar{grid-template-columns:30px 1fr 40px;font-size:20px}.bar i{width:30px;height:30px;font-size:15px}.bar .track{height:14px}
.fixes li{font-size:22px;padding:18px 20px}
.limits{margin:0;padding:0 0 0 24px;display:grid;gap:10px;font-size:22px;color:var(--color-text-secondary)}
.arch{display:flex;align-items:stretch;justify-content:center;gap:24px;margin-top:64px}
.box{border-radius:32px;padding:40px 44px;background:#f6f3f3;font-size:36px;font-weight:500;letter-spacing:-.04em;text-align:center;min-width:380px;display:grid;gap:10px;align-content:center}
.box small{font-size:20px;font-weight:400;color:var(--color-text-secondary);letter-spacing:-.01em}
.box.red{background:var(--color-red-600);color:#fff}.box.red small{color:#ffffffcc}.box.ink{background:var(--color-ink-900);color:#fff}.box.ink small{color:#ffffffaa}
.ar{display:grid;place-items:center;font-size:48px;color:var(--color-text-tertiary)}
.crit{width:100%;border-collapse:collapse;margin-top:48px;font-size:25px}.crit td{padding:22px 18px;border-top:1px solid var(--color-border-tertiary);vertical-align:top;letter-spacing:-.02em}
.crit td:first-child{font-weight:600;width:420px}.crit td:last-child{color:var(--color-text-secondary)}
.close{display:grid;gap:36px;justify-items:center;text-align:center}.close .type-lead{max-width:40ch}
.gap blockquote{font-size:40px}.gap .trace{font-size:26px}.gap .src{font-size:18px}.gap > div{padding:30px 34px}.gap .k{font-size:15px}
.seal-card.big{max-width:620px}
.slide .type-eyebrow{font-size:17px;letter-spacing:.08em}
.slide .badge{justify-self:start;font-size:17px;height:34px;padding:0 14px}
.slide .seal-card .badge{font-size:12px;height:24px}
"""
page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sigillum deck</title><style>{CSS}{DECK_CSS}</style></head><body>{"".join(slides)}</body></html>'
(OUT / "deck.html").write_text(page, encoding="utf-8")
print(f"{len(slides)} slides → {OUT / 'deck.html'}")
