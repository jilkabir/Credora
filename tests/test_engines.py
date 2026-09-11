import json
import tempfile
import unittest
from pathlib import Path

from scripts.approval_gate import approval_report, style_guard
from scripts.claim_guard import assess_text
from scripts.clean_text import clean, load_config
from scripts.decision_report import decide, repetition_check
from scripts.learn_voice import learn
from scripts.pipeline import run_pipeline
from scripts.quality_score import score
from scripts.select_hook import rank
from scripts.validate_memory import validate_jsonl
from scripts.validate_preferences import validate as validate_preferences
from scripts.voice_fit import compare as compare_voice


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
        record = {"date":"2026-09-11","first_line":"A precise opening.","theme":"testing","claim":"A claim that still needs evidence checking.","hook_type":"direct-value","examples":[],"stories":[],"proof":[],"cta":"What would you test next?","audience":"researchers","source_ids":[]}
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

    def test_claim_guard_blocks_unsupported_claim(self):
        ledger = {"claims":[{"id":"c1","claim":"Tool use improves code comprehension.","status":"unsupported","source_ids":[],"causal_language":False,"confidence":"low"}]}
        report = assess_text("Tool use definitely improves code comprehension.", ledger)
        self.assertEqual(report["verdict"], "blocked")

    def test_claim_guard_flags_causal_upgrade(self):
        ledger = {"claims":[{"id":"c2","claim":"Higher tool use is associated with lower comprehension.","status":"supported","source_ids":["s1"],"causal_language":False,"confidence":"medium"}]}
        report = assess_text("Higher tool use causes lower comprehension.", ledger)
        self.assertEqual(report["verdict"], "needs_revision")

    def test_voice_fit_requires_real_samples(self):
        report = compare_voice("A draft.", [])
        self.assertEqual(report["status"], "needs_samples")

    def test_voice_fit_returns_transparent_score(self):
        samples = ["I tested this myself. Short sentences help me explain the result. I avoid hype."]
        report = compare_voice("I tested this myself. Short sentences help explain the result.", samples)
        self.assertEqual(report["status"], "ok")
        self.assertIn("components", report)

    def test_repetition_check_detects_near_duplicate(self):
        report = repetition_check("I tested this workflow with twelve records and changed the process.", ["I tested this workflow with twelve records and changed the process."])
        self.assertEqual(report["status"], "high")

    def test_decision_report_prioritizes_evidence_blocker(self):
        ledger = {"claims":[{"id":"c3","claim":"This method guarantees higher engagement.","status":"unverifiable","source_ids":[],"causal_language":False,"confidence":"low"}]}
        report = decide("This method guarantees higher engagement.", ledger=ledger)
        self.assertEqual(report["verdict"], "NEEDS EVIDENCE")

    def test_voice_learner_reports_observable_features(self):
        samples = ["Do you know why this matters? You can start with a simple example. However, there is a trade-off.", "For instance, you can test the idea first. Then explain what changes and why it matters.", "A practical explanation helps readers. You should also mention the limitation before the recommendation."]
        report = learn(samples)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["sample_count"], 3)

    def test_personal_style_guard_blocks_ai_slop_phrase(self):
        report = style_guard("This game-changer will unlock your potential.")
        self.assertEqual(report["verdict"], "blocked")

    def test_approval_gate_requires_user_approval(self):
        report = approval_report("I tested this process with 12 records in 2026. The result changed my plan.")
        self.assertTrue(report["approval_required"])

    def test_preference_validator_accepts_explicit_feedback(self):
        record = {"date":"2026-09-11","scope":"writing","rule":"Avoid decorative em dashes.","kind":"avoid","source":"explicit_user_feedback","active":True}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preferences.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            report = validate_preferences(path)
        self.assertTrue(report["valid"])
        self.assertEqual(report["records"], 1)


if __name__ == "__main__":
    unittest.main()
