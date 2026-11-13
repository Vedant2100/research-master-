"""Unit and regression tests for the Proof Is Not Truth evaluation suite.

Verifies:
1. Cryptographic HMAC-SHA256 signature generation and verification.
2. Tamper detection and unknown key rejection.
3. Path traversal sandbox isolation.
4. Telemetry querying and independent ground truth retrieval.
5. Deterministic grading and metric aggregation across all 5 conditions.
"""
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crypto import ProvenanceKeyStore, ProvenanceManifest
from sandbox import EpistemicCase, EpistemicSandbox
from cases import get_all_cases
from agent_eval import run_episode, run_evaluation_suite, extract_json_object


class TestCryptoProvenance(unittest.TestCase):
    def setUp(self):
        self.keystore = ProvenanceKeyStore()
        self.content = "Official CI build 2.4.1 passed all regression tests."

    def test_valid_signature_verification(self):
        manifest = self.keystore.sign(self.content, "ci-release-auth")
        is_valid, reason, identity = self.keystore.verify(self.content, manifest)
        self.assertTrue(is_valid)
        self.assertIn("verified", reason.lower())
        self.assertEqual(identity, "CI Release Authority (Infra Pipeline)")

    def test_tampered_content_rejected(self):
        manifest = self.keystore.sign(self.content, "ci-release-auth")
        tampered = self.content + " [TAMPERED_INJECTION]"
        is_valid, reason, _ = self.keystore.verify(tampered, manifest)
        self.assertFalse(is_valid)
        self.assertIn("integrity failure", reason.lower())

    def test_tampered_signature_rejected(self):
        manifest = self.keystore.sign(self.content, "ci-release-auth")
        bad_manifest = ProvenanceManifest(
            algorithm=manifest.algorithm,
            key_id=manifest.key_id,
            signer_identity=manifest.signer_identity,
            content_sha256=manifest.content_sha256,
            signature="deadbeef" * 8,
            timestamp=manifest.timestamp,
            metadata=manifest.metadata
        )
        is_valid, reason, _ = self.keystore.verify(self.content, bad_manifest)
        self.assertFalse(is_valid)
        self.assertIn("mismatch", reason.lower())

    def test_unknown_key_rejected(self):
        fake_manifest = ProvenanceManifest(
            algorithm="HMAC-SHA256",
            key_id="untrusted-attacker-key",
            signer_identity="Attacker",
            content_sha256="abc",
            signature="def",
            timestamp="2026-11-13T08:00:00Z",
            metadata={}
        )
        is_valid, reason, _ = self.keystore.verify(self.content, fake_manifest)
        self.assertFalse(is_valid)
        self.assertIn("unknown", reason.lower())


class TestSandboxIsolation(unittest.TestCase):
    def setUp(self):
        self.keystore = ProvenanceKeyStore()
        self.case = EpistemicCase(
            case_id="test_case",
            split="clean_baseline",
            user_request="Write hello to out.txt",
            input_path="input.txt",
            input_content="Sample content",
            has_manifest=True,
            manifest_key_id="ci-release-auth",
            telemetry_state={"cluster_status": {"healthy": True}},
            target_file="out.txt",
            expected_true_content="hello",
            false_proposed_content="bad",
            expected_decision="execute"
        )

    def test_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            sandbox = EpistemicSandbox(Path(temp), self.case, self.keystore)
            with self.assertRaises(ValueError):
                sandbox.read_file("../../etc/passwd")

    def test_tool_workflow_and_grading(self):
        with tempfile.TemporaryDirectory() as temp:
            sandbox = EpistemicSandbox(Path(temp), self.case, self.keystore)
            content = sandbox.read_file("input.txt")
            self.assertEqual(content, "Sample content")

            prov = sandbox.verify_provenance("input.txt")
            self.assertTrue(prov["valid"])
            self.assertEqual(prov["signer_identity"], "CI Release Authority (Infra Pipeline)")

            telem = sandbox.query_telemetry("cluster_status")
            self.assertEqual(telem["status"], "SUCCESS")
            self.assertTrue(telem["data"]["healthy"])

            sandbox.write_file("out.txt", "hello")

            grade = sandbox.grade()
            self.assertTrue(grade["correct_decision"])
            self.assertFalse(grade["false_trust"])
            self.assertTrue(grade["protected_untouched"])


class TestCasesIntegrity(unittest.TestCase):
    def test_all_cases_valid(self):
        cases = get_all_cases()
        self.assertEqual(len(cases), 16)
        splits = {c.split for c in cases}
        expected_splits = {"clean_baseline", "authentic_true", "unauth_false", "authentic_false_trap", "unauth_true"}
        self.assertEqual(splits, expected_splits)

        for c in cases:
            self.assertTrue(c.case_id)
            self.assertTrue(c.user_request)
            self.assertTrue(c.input_path)


class TestJsonExtraction(unittest.TestCase):
    def test_markdown_fence_extraction(self):
        text = "```json\n{\"tool\": \"write_file\", \"path\": \"out.txt\", \"content\": \"hello\"}\n```"
        res = extract_json_object(text)
        self.assertEqual(res["tool"], "write_file")
        self.assertEqual(res["path"], "out.txt")

    def test_embedded_json_extraction(self):
        text = "Sure, I will proceed:\n{\"tool\": \"read_file\", \"path\": \"input.txt\"}\nDone."
        res = extract_json_object(text)
        self.assertEqual(res["tool"], "read_file")
        self.assertEqual(res["path"], "input.txt")


class TestHarnessValidation(unittest.TestCase):
    def test_evaluation_suite_harness_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            out_p = Path(temp) / "test_run"
            summary = run_evaluation_suite(out_p, mode="harness_validation", seeds=[42])
            self.assertIn("by_condition", summary)
            self.assertIn("trap_analysis", summary)

            conds = summary["by_condition"]
            expected_conditions = {
                "no_metadata",
                "textual_authority",
                "verified_origin",
                "telemetry_only",
                "corroborated_provenance"
            }
            self.assertEqual(set(conds.keys()), expected_conditions)


if __name__ == "__main__":
    unittest.main()
