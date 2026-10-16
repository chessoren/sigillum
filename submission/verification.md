# Sigillum — final check against the brief

Each line was checked on the real product (screens, reports, tests) on 16 Oct 2026, 06:20 UTC.

| Brief requirement | Status | Where to see it |
|---|---|---|
| A letter A–E + five pictograms, readable by a mayor, a CIO or a pupil | ✅ | every seal card; home page carousel; deck slides 3, 9 |
| Proof rule: no grade without proof; a claim without a trace ≤ C | ✅ | `score.py` (`*_CLAIM_ONLY`), test `test_proof_rule_claim_without_trace_is_capped_at_c` |
| "Unknown" instead of guessing | ✅ | town-hall-chat: Q4 unknown → C; test `test_unknown_caps_at_c_and_is_shown` |
| Weakest link caps the grade | ✅ | `score.py` final grade; "Maillon faible" badges in reports; test `test_weakest_link` |
| Apertus reads the docs (claims) | ✅ | `claims.apertus` in reports; verbatim-quote check, test `test_invented_quote_is_rejected` |
| Apertus reconciles claims vs traces and flags gaps | ✅ | school-assistant v1: "Everything runs locally: no data leaves the school." vs Streamlit (US) + CDN, badge "Apertus" |
| Apertus explains in DE / FR / IT / RM | ✅ | "En mots simples" tabs; civicgpt lines written by Apertus naming OpenAI / Mixpanel (US); lines identical to templates are labelled "confirmed" |
| The grade never depends on the model | ✅ | grade computed before Apertus, part of the SHA-256 fingerprint |
| Dated seal, version examined, expiry | ✅ | seal meta (examined, commit, expires, seal #), `python -m sigillum verify` |
| Not a legal label / not official | ✅ | banner, menu note, method page, footer |
| Scene 1 — CIO compares A / C-with-unknown / E | ✅ | samples municipal-assistant, town-hall-chat, civicgpt; deck slide 9; video 0:21 (the "unknown" on question 4) |
| Scene 2 — team goes D → B, history kept | ✅ | school-assistant v1 → v2, history timeline, fixes list; video 0:48 |
| Scene 3 — five plain lines in one's language, each linked to proof | ✅ | report "En mots simples" with evidence chips |
| Scene bonus — Sigillum's own seal with its limits | ✅ | Sigillum D (no licence) → A; limits on the method page and deck slide 12 |
| Community audit: public only, aggregated, anonymous, no names | ✅ | 26 public Apertus Spaces; `community.py` writes proportions only; test `test_community_aggregate_contains_no_names` |
| Plan B if teams are not available | ✅ | Hack Apertus submissions not public before 24 Oct → public Apertus ecosystem instead, stated openly |
| Apertus contribution: failures logged as feedback | ✅ | `apertus.rejections` in each report |
| Open method, criteria and code | ✅ | `docs/method.md`, Apache-2.0 / CC-BY-4.0 |
| Cost per examination announced | ✅ | ~70 ms deterministic; ~5 min with Apertus on 4 CPU cores |
| Tool itself runs offline and grades A (or says why) | ✅ | `make offline-test` (`network_mode: none`): 18 tests + 5 audits pass; `docs/offline-test.log` |
| Demo ≤ 2 min, real screens, English UI, English voice (Oren), English subtitles | ✅ | `docs/video/sigillum-demo.mp4`, Fish Audio s2.1-pro-free, English voice "Stick · Oren"; `sigillum-demo.en.srt` |
| America.gov design system in Swiss colours | ✅ | display serif −0.05 em, tight sans, 48 px hero shell, pill search, manifesto with inline icons, feature rows, floating cards, giant footer wordmark; flag red #FF0000 (cross), #DA291C (actions) |
| Hack Apertus template: `track_2b/`, `make run` in Docker, LLM_* env vars, report PDF ≤ 6 pages | ✅ | `make run`; `Sigillum_Report.pdf` (5 pages) |

## Issues found by the loop and fixed

1. Hero seal card off-centre, Alps missing, pictogram captions too long → fixed.
2. Duplicate fixes across questions → de-duplicated.
3. Mobile: hero grid wider than the viewport, report overflow → `minmax(0, 1fr)` grids.
4. Community audit false positives (hyperlinks as flows, licences in Space metadata missed, `gr.load` not detected) → fixed and tested before publishing the aggregate.
5. Sigillum detecting its own detection tables → published exclusions; exclusions can no longer hide tests.
6. Sigillum's first self-examination: D, no licence in the project folder → licence added → A.
7. Apertus answering in English when asked for French/German, copying French into Romansh → language check rejects them.
8. Apertus "contradicting" an A project with positive evidence → only contradicting traces are shown and citable; test added.
9. Apertus writing the quote instead of the claim ID → matched by verbatim quote.
10. Home page showed no gap (latest report had none) → picks the report with a gap.
11. "Written by Apertus" shown for lines identical to templates → now labelled "Confirmed by Apertus".
12. Deck: misleading Apertus statistics computed on cached runs → replaced by measured per-project figures.

## What remains for Oren (cannot be done from this session)

- Push the repository to a **public** GitHub repo created from the HackApertus template, and paste its URL.
- Upload the video (YouTube/Vimeo, unlisted is fine) and paste its URL.
- Submit on **hackapertus.ch/online-hack/submissions** (Track 2B), then mirror on Devpost.
