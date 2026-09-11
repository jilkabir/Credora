import json
import tempfile
import unittest
from pathlib import Path

from scripts.clean_text import clean, load_config
from scripts.pipeline import run_pipeline
from scripts.quality_score import score
from scripts.select_hook import rank
from scripts.validate_memory import validate_jsonl


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

    def test_memory_validator_accepts_valid_record(self):
        record = {
            "date": "2026-09-11",
            "first_line": "A precise opening.",
            "theme": "testing",
            "claim": "A claim that still needs evidence checking.",
            "hook_type": "direct-value",
            "examples": [],
            "stories": [],
            "proof": [],
            "cta": "What would you test next?",
            "audience": "researchers",
            "source_ids": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            report = validate_jsonl(path)
        self.assertTrue(report["valid"])
        self.assertEqual(report["records"], 1)

    def test_memory_validator_rejects_missing_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.jsonl"
            path.write_text('{"date":"2026-09-11"}\n', encoding="utf-8")
            report = validate_jsonl(path)
        self.assertFalse(report["valid"])
        self.assertTrue(report["errors"])

    def test_pipeline_returns_cleaned_quality_and_hooks(self):
        result = run_pipeline("Research\u200b matters. I tested this with 12 users in 2026.", "research", 2)
        self.assertNotIn("\u200b", result["cleaned_text"])
        self.assertIn("overall", result["quality"])
        self.assertEqual(len(result["hook_suggestions"]), 2)
        self.assertIn("research", result["hook_suggestions"][0]["best_for"])


if __name__ == "__main__":
    unittest.main()
