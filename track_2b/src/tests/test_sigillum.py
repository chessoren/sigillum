"""Sigillum test suite — standard library only, runs with networking disabled."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sigillum import registry  # noqa: E402
from sigillum.apertus import Apertus, language_ok  # noqa: E402
from sigillum.collect import scan  # noqa: E402
from sigillum.community import run as community_run  # noqa: E402
from sigillum.report import audit, verify  # noqa: E402
from sigillum.score import grade  # noqa: E402

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples"


def project(files: dict) -> Path:
    d = Path(tempfile.mkdtemp(prefix="sig-test-"))
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


APACHE = "Apache License\nVersion 2.0, January 2004\n"


class Registry(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(registry.classify("api.openai.com").jurisdiction, "US")
        self.assertEqual(registry.classify("eu.i.posthog.com").jurisdiction, "EU")
        self.assertEqual(registry.classify("swissai.cscs.ch").jurisdiction, "CH")
        self.assertEqual(registry.classify("apertus:8081").jurisdiction, "LOCAL")
        self.assertEqual(registry.classify("192.168.1.20").jurisdiction, "LOCAL")
        self.assertEqual(registry.classify("gemeinde-xy.ch").category, "swiss-tld")
        self.assertEqual(registry.classify("totally-unknown.io").jurisdiction, "UNKNOWN")


class Rules(unittest.TestCase):
    def test_samples_expected_grades(self):
        expected = {"gemeinde-assistent": "A", "chat-commune": "C", "civicgpt": "E",
                    "assistant-ecole-v1": "D", "assistant-ecole-v2": "B"}
        for name, g in expected.items():
            with self.subTest(name=name):
                self.assertEqual(grade(scan(SAMPLES / name))["grade"], g)

    def test_proof_rule_claim_without_trace_is_capped_at_c(self):
        d = project({"README.md": "Our assistant runs entirely locally. No data leaves your computer.",
                     "main.py": "print('hello')\n", "LICENSE": APACHE, "requirements.txt": ""})
        g = grade(scan(d))
        q1 = g["questions"][0]
        self.assertEqual(q1["level"], "C")
        self.assertEqual(q1["proof"], "declared")
        shutil.rmtree(d)

    def test_weakest_link(self):
        d = project({"app.py": "import requests\nrequests.post('https://api.openai.com/v1/chat/completions')\n",
                     "Dockerfile": "FROM python:3.12\n", "requirements.txt": "requests==2.32.3\n",
                     "LICENSE": APACHE, "tests/test_x.py": "def test(): pass\n"})
        g = grade(scan(d))
        self.assertEqual(g["grade"], "E")
        self.assertIn(2, g["weakest"])
        shutil.rmtree(d)

    def test_unknown_caps_at_c_and_is_shown(self):
        g = grade(scan(SAMPLES / "chat-commune"))
        self.assertEqual(g["questions"][3]["level"], "unknown")
        self.assertIn(4, g["unknown"])
        self.assertEqual(g["grade"], "C")

    def test_gap_detected(self):
        g = grade(scan(SAMPLES / "assistant-ecole-v1"))
        self.assertTrue(any(x["tag"] == "NO_DATA_EXIT" for x in g["gaps"]))

    def test_telemetry_off_switch_is_recognised(self):
        sc = scan(SAMPLES / "assistant-ecole-v2")
        self.assertTrue(any(e.signal == "TELEMETRY_OFF" for e in sc.evidence))

    def test_hyperlink_is_not_a_data_flow(self):
        d = project({"app.py": "TEXT = '<a href=\"https://example-docs.net/help\">help</a>'\n"})
        self.assertFalse(any(e.signal == "HOST" for e in scan(d).evidence))
        shutil.rmtree(d)

    def test_build_time_download_does_not_count_at_runtime(self):
        d = project({"Makefile": "model:\n\tcurl -L -o m.gguf https://huggingface.co/x/y/resolve/main/m.gguf\n",
                     "main.py": "print(1)\n"})
        sc = scan(d)
        self.assertTrue(any(e.signal == "BUILD_FETCH" for e in sc.evidence))
        self.assertFalse(any(e.signal in ("HOST", "MODEL_HUB") for e in sc.evidence))
        shutil.rmtree(d)


class Seal(unittest.TestCase):
    def test_seal_is_tamper_evident(self):
        r = audit(str(SAMPLES / "civicgpt"), llm=None, langs=("fr",))
        self.assertTrue(verify(r))
        r["grade"] = "A"
        self.assertFalse(verify(r))

    def test_report_is_dated_and_expires(self):
        r = audit(str(SAMPLES / "gemeinde-assistent"), llm=None, langs=("rm",))
        self.assertLess(r["examined_at"], r["expires_at"])
        self.assertEqual(r["explanations"]["rm"]["source"], "template")


class ApertusChecks(unittest.TestCase):
    def test_language_check(self):
        self.assertTrue(language_ok("Vossas dumondas na bandunan betg il computer.", "rm"))
        self.assertFalse(language_ok("Vos questions ne quittent pas la machine.", "rm"))
        self.assertTrue(language_ok("Ihre Daten bleiben in der Schweiz.", "de"))

    def test_invented_quote_is_rejected(self):
        a = Apertus(base_url="http://127.0.0.1:9", model="test")
        a._chat = lambda *args, **kw: json.dumps({"claims": [
            {"quote": "Everything runs offline on our servers", "topic": "offline"},
            {"quote": "Data is stored only in Switzerland.", "topic": "data_flow"}]})
        claims, rejected = a.extract_claims("# Tool\nData is stored only in Switzerland.\n")
        self.assertEqual([c["quote"] for c in claims], ["Data is stored only in Switzerland."])
        self.assertEqual(rejected, 1)

    def test_gap_citing_missing_evidence_is_rejected(self):
        a = Apertus(base_url="http://127.0.0.1:9", model="test")
        a._chat = lambda *args, **kw: json.dumps({"verdicts": [
            {"claim": "C1", "contradicted": True, "evidence": ["E99"], "shows": "invented"}]})
        gaps, rejected = a.reconcile([{"id": "C1", "quote": "No tracking."}],
                                     [{"id": "E01", "q": 4, "kind": "trace", "signal": "HOST"}])
        self.assertEqual(gaps, [])
        self.assertEqual(rejected, 1)

    def test_gap_citing_positive_evidence_is_impossible(self):
        a = Apertus(base_url="http://127.0.0.1:9", model="test")
        a._chat = lambda *args, **kw: json.dumps({"verdicts": [
            {"claim": "C1", "contradicted": True, "evidence": ["E01"], "shows": "local server contradicts offline"}]})
        gaps, _ = a.reconcile([{"id": "C1", "quote": "Runs fully offline."}],
                              [{"id": "E01", "q": 1, "kind": "trace", "signal": "LOCAL_SERVING"}])
        self.assertEqual(gaps, [])

    def test_unreachable_endpoint_falls_back_to_templates(self):
        r = audit(str(SAMPLES / "civicgpt"), llm=Apertus(base_url="http://127.0.0.1:9"), langs=("de",))
        self.assertFalse(r["apertus"]["used"])
        self.assertEqual(r["explanations"]["de"]["source"], "template")


class Ethics(unittest.TestCase):
    def test_community_aggregate_contains_no_names(self):
        src = Path(tempfile.mkdtemp())
        for n in ("secret-team-alpha", "secret-team-beta"):
            shutil.copytree(SAMPLES / "civicgpt", src / n)
        out = Path(tempfile.mkdtemp())
        sys.stdout, old = open(os.devnull, "w"), sys.stdout  # noqa: SIM115
        try:
            community_run(src, out)
        finally:
            sys.stdout.close()
            sys.stdout = old
        text = (out / "aggregate.json").read_text()
        self.assertNotIn("secret-team", text)
        self.assertEqual(json.loads(text)["count"], 2)
        shutil.rmtree(src), shutil.rmtree(out)


class Server(unittest.TestCase):
    def test_path_outside_allowed_roots_is_refused(self):
        from sigillum.server import App
        app = App(SAMPLES.parent)
        with self.assertRaises(ValueError):
            app.resolve_target("../../../etc")
        self.assertEqual(app.resolve_target("civicgpt")[1], "civicgpt")


if __name__ == "__main__":
    unittest.main()
