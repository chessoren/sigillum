# Sigillum — a sovereignty seal for AI tools

> Everyone says "sovereign AI". Nobody measures it. Sigillum gives any AI project a grade from **A** to **E**, with the evidence behind every answer — and applied it to itself first.

*Sigillum* is Latin for "seal", as *Apertus* is Latin for "open".

Hack Apertus 2026 · Online · **Track 2B — Own Project** · project root: [`track_2b/`](track_2b/)

```bash
cd track_2b
make run          # Sigillum on http://localhost:8080 (+ a local Apertus if LLM_BASE_URL is not set)
make test         # 18 tests, standard library only
make offline-test # whole suite + every sample audit, with networking disabled (docker --network none)
```

- What it does, how to run it, and the challenge requirements: [`track_2b/README.md`](track_2b/README.md)
- Architecture, evaluation, limits: [`track_2b/technical_report.md`](track_2b/technical_report.md) · PDF: [`track_2b/Sigillum_Report.pdf`](track_2b/Sigillum_Report.pdf)
- Method, ethics and published limits: [`track_2b/docs/method.md`](track_2b/docs/method.md)

Code: Apache-2.0 · Report and method: CC-BY-4.0. Sigillum is a transparency instrument, not a legal certification, and it is not affiliated with the Swiss Confederation.
