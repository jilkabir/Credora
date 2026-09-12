import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.approval_gate import approval_report, style_guard
from scripts.claim_guard import assess_text
from scripts.clean_text import clean, load_config
from scripts.context_bundle import build as build_context
from scripts.credora import _load_user_review_inputs, workspace_status
from scripts.decision_report import decide, repetition_check
from scripts.init_user import init_user
from scripts.learn_voice import learn
from scripts.pipeline import run_pipeline
from scripts.quality_score import score
from scripts.review_draft import review as review_draft
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

    def test_decision_report_uses_supplied_voice_threshold(self):
        samples = ["I tested this myself. Short sentences help me explain the result. I avoid hype."]
        report = decide(
            "I tested this myself. Short sentences help explain the result.",
            voice_samples=samples,
            voice_threshold=101,
        )
        self.assertEqual(report["verdict"], "VOICE MISMATCH")
        self.assertEqual(report["thresholds"]["voice_fit"], 101.0)

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

    def test_context_bundle_loads_linkedin_personalization(self):
        bundle = build_context("linkedin", "post")
        self.assertIn("profile/voice.md", bundle)
        self.assertIn("profile/platforms/linkedin.md", bundle)
        self.assertIn("READY FOR APPROVAL", bundle)

    def test_review_draft_keeps_user_approval_required(self):
        report = review_draft("I tested this workflow with 12 records in 2026. It changed how I explain the result.")
        self.assertIn(report["status"], {"READY FOR APPROVAL", "NEEDS REVISION"})
        self.assertTrue(report["approval_required"])

    def test_review_draft_propagates_evidence_inputs_to_approval_gate(self):
        ledger = {"claims":[{"id":"c4","claim":"This guarantees higher engagement.","status":"unsupported","source_ids":[],"causal_language":False,"confidence":"low"}]}
        report = review_draft("This guarantees higher engagement.", ledger=ledger)
        self.assertEqual(report["decision"]["verdict"], "NEEDS EVIDENCE")
        self.assertEqual(report["approval_gate"]["decision"]["verdict"], "NEEDS EVIDENCE")
        self.assertEqual(report["status"], "NEEDS REVISION")

    def test_init_user_creates_private_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            with patch("scripts.init_user.USERS_ROOT", temp_root / "users"):
                result = init_user("Test Person")
                root = temp_root / "users" / "test-person"
                self.assertEqual(result["status"], "created")
                self.assertTrue((root / "identity.md").exists())
                self.assertTrue((root / "platforms" / "linkedin.md").exists())
                manifest = json.loads((root / "credora.json").read_text(encoding="utf-8"))
                self.assertTrue(manifest["approval_required"])
                self.assertFalse(manifest["auto_publish"])

    def test_context_bundle_can_load_user_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "users" / "demo"
            (base / "platforms").mkdir(parents=True)
            (base / "identity.md").write_text("# Identity\nDemo Person", encoding="utf-8")
            (base / "platforms" / "linkedin.md").write_text("# LinkedIn\nDemo rules", encoding="utf-8")
            with patch("scripts.context_bundle.ROOT", Path(tmp)):
                bundle = build_context("linkedin", "post", "demo")
            self.assertIn("Demo Person", bundle)
            self.assertIn("Demo rules", bundle)
            self.assertIn("Missing context", bundle)

    def test_context_bundle_rejects_path_traversal_user(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("scripts.context_bundle.ROOT", Path(tmp)):
                with self.assertRaises(ValueError):
                    build_context("linkedin", "post", "../outside")

    def test_workspace_status_is_not_ready_when_profile_is_uninitialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "users" / "demo"
            (root / "platforms").mkdir(parents=True)
            required = ["identity.md", "positioning.md", "expertise.md", "audience.md", "voice.md", "writing-rules.md", "forbidden-style.md", "profile-goals.md"]
            for rel in required:
                (root / rel).write_text("Status: not initialized\n", encoding="utf-8")
            for platform in ["linkedin", "facebook", "instagram", "youtube"]:
                (root / "platforms" / f"{platform}.md").write_text("rules\n", encoding="utf-8")
            with patch("scripts.credora.ROOT", Path(tmp)):
                report = workspace_status("demo")
            self.assertFalse(report["ready"])
            self.assertEqual(report["status"], "incomplete")
            self.assertIn("identity.md", report["uninitialized_files"])
            self.assertTrue(report["approval_required"])
            self.assertFalse(report["auto_publish"])

    def test_workspace_status_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("scripts.credora.ROOT", Path(tmp)):
                report = workspace_status("../outside")
            self.assertEqual(report["status"], "error")
            self.assertFalse(report["ready"])

    def test_user_review_inputs_load_private_voice_history_and_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "users" / "demo"
            (root / "writing-samples").mkdir(parents=True)
            (root / "content-history").mkdir(parents=True)
            (root / "writing-samples" / "one.txt").write_text("My real writing sample.", encoding="utf-8")
            (root / "content-history" / "old.md").write_text("My earlier post.", encoding="utf-8")
            (root / "claim-ledger.json").write_text(json.dumps({"claims": []}), encoding="utf-8")
            with patch("scripts.credora.ROOT", Path(tmp)):
                ledger, samples, history = _load_user_review_inputs("demo")
            self.assertEqual(ledger, {"claims": []})
            self.assertEqual(samples, ["My real writing sample."])
            self.assertEqual(history, ["My earlier post."])

    def test_user_review_inputs_reject_malformed_claim_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "users" / "demo"
            root.mkdir(parents=True)
            (root / "claim-ledger.json").write_text("{not-json", encoding="utf-8")
            with patch("scripts.credora.ROOT", Path(tmp)):
                with self.assertRaises(ValueError):
                    _load_user_review_inputs("demo")


if __name__ == "__main__":
    unittest.main()
