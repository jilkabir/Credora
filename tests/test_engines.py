import json
import tempfile
import unittest
from pathlib import Path

from scripts.clean_text import clean, load_config
from scripts.quality_score import score
from scripts.select_hook import rank


class CredoraEngineTests(unittest.TestCase):
    def test_clean_removes_format_chars(self):
        text = "Hello\u200b world"
        cleaned, report = clean(text, load_config())
        self.assertEqual(cleaned, "Hello world")
        self.assertEqual(report["format_chars_removed"], 1)

    def test_quality_score_has_expected_dimensions(self):
        result = score("I tested this with 12 users in 2026. The result changed my plan.", load_config())
        self.assertIn("overall", result)
        self.assertIn("specificity", result["dimensions"])
        self.assertIn("readability", result["dimensions"])

    def test_research_hooks_rank_first(self):
        result = rank("research", 3)
        self.assertTrue(result)
        self.assertIn("research", result[0]["best_for"])


if __name__ == "__main__":
    unittest.main()
