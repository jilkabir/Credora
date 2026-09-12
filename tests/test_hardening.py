import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.claim_guard import assess_text
from scripts.context_bundle import build


class CredoraHardeningTests(unittest.TestCase):
    def test_claim_guard_blocks_non_object_claim_record(self):
        report = assess_text("This definitely works.", {"claims": ["bad-record"]})
        self.assertEqual(report["verdict"], "blocked")
        self.assertEqual(report["flags"][0]["code"], "invalid_claim_record")

    def test_claim_guard_blocks_claims_when_not_array(self):
        report = assess_text("This definitely works.", {"claims": {"id": "x"}})
        self.assertEqual(report["verdict"], "blocked")
        self.assertEqual(report["flags"][0]["code"], "invalid_claims")

    def test_context_bundle_rejects_missing_user_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("scripts.context_bundle.ROOT", Path(tmp)):
                with self.assertRaises(ValueError):
                    build("linkedin", "post", "missing-user")

    def test_context_bundle_rejects_corrupt_preferences(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "users" / "demo"
            (root / "platforms").mkdir(parents=True)
            (root / "identity.md").write_text("# Identity\nDemo", encoding="utf-8")
            (root / "platforms" / "linkedin.md").write_text("# LinkedIn\nRules", encoding="utf-8")
            (root / "preferences.jsonl").write_text("{bad-json\n", encoding="utf-8")
            with patch("scripts.context_bundle.ROOT", Path(tmp)):
                with self.assertRaises(ValueError):
                    build("linkedin", "post", "demo")


if __name__ == "__main__":
    unittest.main()
