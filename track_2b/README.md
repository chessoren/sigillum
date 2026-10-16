# Sigillum — sovereignty seal for AI tools (Track 2B)

**Sigillum** asks five questions of any AI project, looks for verifiable evidence behind each answer, and sums it up in one letter from **A** (fully sovereign) to **E** (dependent on foreign services), with five pictograms — like the energy label or the Nutri-Score.

| # | Question | What the evidence shows |
|---|----------|-------------------------|
| 1 | Where does the model live? | hardware the organisation controls, Swiss infrastructure, or a foreign provider |
| 2 | Where does the data go? | nothing leaves, stays in Switzerland, or leaves the country |
| 3 | What happens without internet? | everything works (tested), degraded, or everything stops |
| 4 | Who else is in the loop? | third-party services, telemetry on by default, components that cannot be audited |
| 5 | Can it be verified? | licence, reproducible build, tests — or nothing |

Three rules, implemented in `src/sigillum/score.py`:
- **Proof rule** — a claim without a trace never earns more than C. When information is missing, the seal says *unknown* instead of guessing (unknown caps the grade at C).
- **Weakest link** — the final grade is the worst of the five answers.
- **Dated seal** — date, commit, method and registry versions, SHA-256 fingerprint; expires after 90 days.

**Apertus reads, compares and explains; the evidence decides.** Apertus v1.5 (served locally with llama.cpp, or any OpenAI-compatible endpoint) extracts what a project claims about itself (quotes must exist word for word), sets each claim against the traces and names the gaps ("the project says X, the traces show Y"), and explains the verdict in plain German, French, Italian and Romansh. Every answer is checked against the evidence before it is used; the grade itself never depends on the model.

## Run it

```bash
make run              # judges: uses LLM_BASE_URL / LLM_API_KEY / LLM_NAME if set,
                      # otherwise downloads Apertus v1.5 8B GGUF (~5 GB, build time) and serves it with llama.cpp
make run-lite         # no model at all: deterministic grades, template explanations
make test             # unit tests (standard library only)
make offline-test     # tests + all sample audits inside a container with --network none
```

Open http://localhost:8080 — examine a bundled sample (`gemeinde-assistent`, `chat-commune`, `civicgpt`, `assistant-ecole-v1`/`-v2`), any folder mounted under `/audit` (`AUDIT_DIR=/path/to/projects make run`), or a public Git URL.

Command line, without the web interface:

```bash
cd src
python3 -m sigillum audit ../data/samples/civicgpt         # writes data/reports/<id>.json
python3 -m sigillum audit .. --name sigillum               # Sigillum examines itself
python3 -m sigillum verify ../data/reports/<id>.json       # checks the seal fingerprint
```

### Input / output
- **Input:** a project directory (or a public https Git URL in the web UI).
- **Output:** a JSON report (`data/reports/<id>.json`): grade, five answers with levels and proof type, evidence (file, line, snippet, host, operator, jurisdiction), gaps, fixes, plain-language explanations in fr/de/it/rm/en, Apertus usage and rejected answers, seal fingerprint, expiry. Plus an embeddable SVG badge (`/api/badge/<id>.svg`).

### Target architecture — (b) air-gapped, also (a) on-premise
Sigillum uses the Python standard library only, bundles its fonts and icons, makes no runtime request except to the configured Apertus endpoint, and keeps no logs about visitors. With the local llama.cpp service it runs with no external network connection; `make offline-test` proves it. Build-time downloads (Python base image, llama.cpp image, Apertus weights) are listed in the report.

### Sigillum's own seal
Sigillum examined itself with the strictest rule — see `data/reports/sigillum-*.json` and the page *Le sceau de Sigillum*. Its limits are published in `docs/method.md`.

---

# Track 2 B: Own Project

Bring your own idea and build a working Apertus prototype that tackles a problem you care about — any domain, any use case. The project must be new, started within the hackathon period.

Submissions must use the Apertus model family.
For Track 2 this means that submitted solutions must be built with Apertus. Other open-weights models can be used to support development, e.g. as automatic judges during evaluation. Their role must be clearly described in the submission report.

💬 In case you have questions, join the conversation on [Discord](https://discord.gg/hack-apertus) or send an email to “hello@hackapertus.ch”

---

## 🔧 Resources & Tools

Check our resources & tools page for detailed information:
https://hackapertus.notion.site/resources-tools

| Models           | URL                                      |
|------------------|------------------------------------------|
| Apertus v1.5 8B  | [huggingface.co/swiss-ai/Apertus-v1.5-8B](https://huggingface.co/swiss-ai/Apertus-v1.5-8B)  |
| Apertus v1.5 70B | [huggingface.co/swiss-ai/Apertus-v1.5-70B](https://huggingface.co/swiss-ai/Apertus-v1.5-70B) |


## Target architecture (mandatory)

Whatever you build in Track 2B must be deployable in one of these three architectures:

- **a) On-premise** — on the organisation's own infrastructure, under its own administration.
- **b) Air-gapped** — with no external network connection at runtime.
- **c) Sovereign Swiss cloud** — on a cloud platform operated in Switzerland, under Swiss jurisdiction, with Swiss data residency.

---

## Data

The `data/` directory must not exceed 100 MB.

---

## 📦 Submission Requirements & Deliverables

❗️ Submissions are not handled on Devpost but via this URL only:
http://hackapertus.ch/online-hack/submissions

The submission must: 
1. follow the template repo and include all prerequisite files and definitions
2. follow the specified input/output formats
3. run in a Docker container, launched with `make run` from the root of the project
4. run end-to-end when judges try to run it

### Git repo (URL)
- Create your repo from this template (**Use this template**) and work in the `track_2b/` challenge directory. Delete the other track challenge directories.
- Keep `track_2b/` as it is: don't rename it or move its files.
- Set the repo to PUBLIC (Settings --> Collaborators --> Manage Visibility)
- Submit the URL of YOUR Git repo.

### Technical Report (pdf)
- Update [technical_report.md](technical_report.md) in this repository with all the details for your submission.
- Upload a pdf of your technical report to this directory, named as `TeamName_Report.pdf`.
- Format: pdf, max. 6 pages w/o references
- Submit the pdf of the technical report.

### Demo video (URL)
- Max. 2 min demo video of your prototype

### Dataset (URL) - optional, depending on your project
Submitted datasets must comply with our guidelines for responsibly sourced datasets.

- Create a user account on Hugging Face
- Clone our dataset template on Hugging Face: https://huggingface.co/datasets/HackApertus/online_hack_template
- Complete the dataset card with all required information
- Upload your dataset. It should consist of the following components:
    - evaluation dataset (i.e. individual test cases)
    - model response dataset (i.e. the model response to each test case)
    - metadata file (i.e. additional information about each test case; where relevant, this file must contain instance-level licensing information) 
- Make sure your dataset access control is set to PUBLIC
- Provide the URL of _your_ data set


---

## ⚖️ Judging Criteria

1. Purposeful use of AI
2. Technical rigour
3. Value, cost & scalability
4. Sovereign deployability
5. Implementation feasibility

Judges use a Scale 0–5 per dimension.

---

## Support

**Licensing requirements**
Please check our Terms & Conditions (6. What you build is open source):
https://hackapertus.ch/terms-and-conditions

## FAQ
💡 https://hackapertus.ch/faq

## Contact
💬 In case you have questions, join the conversation on Discord or send an email to “hello@hackapertus.ch”
