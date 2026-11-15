"""Negative failure tests for the submission verifier.

Demonstrates that the adversarial verifier fails closed when:
1. A protected artifact hash is tampered or incorrect.
2. A manifest entry is missing from the required path set.
3. A duplicate manifest entry is supplied.
4. A quantitative metric in documentation is corrupted or mismatched.
5. An unsupported causal or directive claim is introduced into submission text.
6. An invalid baseline Git commit SHA is provided.
"""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path

# Workspace setup
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import verify_submission


class TestVerifierNegativeFailClosed(unittest.TestCase):
    """Test suite proving the adversarial verifier fails closed under corruption."""

    def test_tampered_hash_fails_closed(self):
        """Verifier must fail closed if a manifest SHA-256 does not match Git baseline or disk."""
        tampered_manifest = copy.deepcopy(verify_submission.PROTECTED_MANIFEST_ENTRIES)
        # Tamper the first entry's hash
        rel_path, _ = tampered_manifest[0]
        tampered_manifest[0] = (rel_path, "0000000000000000000000000000000000000000000000000000000000000000")
        
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_real_artifact_immutability(
                manifest_entries=tampered_manifest
            )
        self.assertIn("hash matches manifest", str(ctx.exception))

    def test_missing_manifest_entry_fails_closed(self):
        """Verifier must fail closed if any required protected path is omitted from the manifest."""
        truncated_manifest = verify_submission.PROTECTED_MANIFEST_ENTRIES[:-1]
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_real_artifact_immutability(
                manifest_entries=truncated_manifest
            )
        self.assertIn("Manifest matches expected path set exactly", str(ctx.exception))

    def test_duplicate_manifest_entry_fails_closed(self):
        """Verifier must fail closed if duplicate entries exist in the manifest list."""
        duplicate_manifest = copy.deepcopy(verify_submission.PROTECTED_MANIFEST_ENTRIES)
        duplicate_manifest.append(duplicate_manifest[0])  # Duplicate the first path
        
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_real_artifact_immutability(
                manifest_entries=duplicate_manifest
            )
        self.assertIn("No duplicate manifest entry", str(ctx.exception))

    def test_invalid_baseline_commit_fails_closed(self):
        """Verifier must fail closed if the pinned baseline commit does not exist."""
        invalid_commit = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_real_artifact_immutability(
                baseline_commit=invalid_commit
            )
        self.assertIn("Pinned baseline commit exists in Git history", str(ctx.exception))

    def test_corrupted_metric_in_documentation_fails_closed(self):
        """Verifier must fail closed if report or package table contains corrupted numbers."""
        clean_report = (verify_submission.REPORTS / "APART_RESEARCH_REPORT.md").read_text(encoding="utf-8")
        corrupted_report = clean_report.replace("37.5%", "99.9%")
        
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_documentation_and_claim_calibration(
                report_text=corrupted_report
            )
        self.assertIn("Report contains verified table row", str(ctx.exception))

    def test_prohibited_overclaim_in_documentation_fails_closed(self):
        """Verifier must fail closed if unsupported causal or directive language is introduced."""
        clean_report = (verify_submission.REPORTS / "APART_RESEARCH_REPORT.md").read_text(encoding="utf-8")
        clean_pkg = (verify_submission.REPORTS / "APART_SUBMISSION_PACKAGE.md").read_text(encoding="utf-8")
        
        # Test 1: Injected directive claim
        injected_pkg_1 = clean_pkg + "\nEpistemic directives are required to activate corroboration.\n"
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_documentation_and_claim_calibration(
                pkg_text=injected_pkg_1
            )
        self.assertIn("Prohibited overclaim absent from package", str(ctx.exception))
        
        # Test 2: Injected causal claim
        injected_pkg_2 = clean_pkg + "\nProvenance checks caused severe over-abstention, causing agents to refuse tasks.\n"
        with self.assertRaises(AssertionError) as ctx:
            verify_submission.verify_documentation_and_claim_calibration(
                pkg_text=injected_pkg_2
            )
        self.assertIn("Prohibited overclaim absent from package", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
