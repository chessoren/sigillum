# Sigillum method 1.0

Open, versioned, contestable. Everything below is implemented in `src/sigillum/score.py`; the language model never sets the grade.

## The five questions

| # | Question | A (best) | E (worst) |
|---|---|---|---|
| 1 | Where does the model live? | open-weight model served on hardware the organisation controls | closed model at a foreign company |
| 2 | Where does the data go? | no external destination in the code | user content (questions, documents) sent abroad |
| 3 | What happens without internet? | everything runs locally and a test proves it (`--network none`) | the core feature calls a foreign service: everything stops |
| 4 | Who else is in the loop? | no analytics, telemetry or third-party AI service | trackers observe the users |
| 5 | Can it be verified? | open licence + container build + pinned dependencies + tests | no code published |

Intermediate levels (B, C, D) and the exact triggers are listed in `score.py` and shown, with evidence, in every report.

## Three rules

1. **Proof rule.** A claim without a trace is not proof: a question answered only by the documentation cannot exceed C. When information is missing the answer is *unknown*, displayed as such, and the final grade is capped at C.
2. **Weakest link.** The final grade is the worst of the five answers.
3. **Dated seal.** Date, commit, method and registry versions, SHA-256 fingerprint of the graded content (`python -m sigillum verify`); expiry after 90 days.

## Evidence

Static, deterministic analysis of code and configuration (never of user data):
- network destinations in runtime files, classified by a public registry (`registry.py`: operator, jurisdiction CH/EU/US/…, category);
- SDKs whose default endpoint is foreign (OpenAI, Anthropic, Gemini, Hugging Face Inference, `gradio.load("models/…")`…), and whether the endpoint is overridden (`LLM_BASE_URL`, `base_url=`);
- local serving (llama.cpp, vLLM, Ollama, TGI, Transformers in-process, in-browser WebGPU);
- frameworks with telemetry on by default and their off-switches (Streamlit `gatherUsageStats`, Gradio `GRADIO_ANALYTICS_ENABLED`, Chroma `anonymized_telemetry`, vLLM `VLLM_NO_USAGE_STATS`);
- trackers in dependency manifests; opaque files (binaries, minified bundles);
- licence, container, lockfile, tests, offline test;
- claims in the documentation (multilingual patterns + Apertus extraction).

Hyperlinks (`href=`, Markdown links) and build-time downloads (Makefile, Dockerfile, shell scripts) are not counted as runtime data flows; build-time fetches are listed.

## The role of Apertus

1. **Read** — extract the sentences in which the project describes its own sovereignty. A quote that does not exist word for word in the documentation is rejected.
2. **Reconcile** — for each claim, decide whether traces contradict it, citing evidence IDs. A gap citing no valid evidence is rejected.
3. **Explain** — rewrite the verdict in plain German, French, Italian, Romansh (and English) for non-technical readers. A line in the wrong language is rejected and replaced by the template.

Rejected answers are counted in each report. The endpoint's jurisdiction is shown in each report.

## Ethics

1. Only public projects. 2. Aggregated and anonymous results (the community code cannot output names). 3. Right of reply before naming anyone. 4. A free service, not a trial. 5. Sigillum first, on itself.

Sigillum is a transparency instrument — not a legal label, not an official certification, not affiliated with the Swiss Confederation.

## Published limits

- Static analysis only; runtime-only behaviour (dynamic URLs, plugins) can be missed.
- The registry is hand-curated and incomplete; unknown hosts are reported as unknown, never as safe.
- Hyperlink exclusion is heuristic.
- Apertus 8B (Q4, CPU) makes occasional German errors and tends to keep the Romansh template wording; Romansh should be proof-read by a native speaker.
- Build-time downloads are listed but do not lower the runtime grade.
- `.sigillumignore` exclusions are self-declared and published in every report.
- Examining a Git URL needs network access to that host; in air-gapped mode, mount local folders under `/audit`.
