import json
import tempfile
import unittest
from pathlib import Path

from scripts.guided_onboarding import apply_answers
from scripts.profile_intelligence import save_for_user
from scripts.usability import doctor


class UsabilityTests(unittest.TestCase):
    def _workspace(self, root: Path) -> Path:
        ws = root / "users" / "demo"
        (ws / "platforms").mkdir(parents=True)
        (ws / "writing-samples").mkdir()
        for rel in ["writing-rules.md", "forbidden-style.md"]:
            (ws / rel).write_text("# Rules\nClear and practical.\n", encoding="utf-8")
        (ws / "voice.md").write_text("# Writing Voice\n\nStatus: not initialized\n", encoding="utf-8")
        for platform in ["linkedin", "facebook", "instagram", "youtube"]:
            (ws / "platforms" / f"{platform}.md").write_text(f"# {platform}\nUseful and accurate.\n", encoding="utf-8")
        (ws / "preferences.jsonl").write_text("", encoding="utf-8")
        return ws

    def _onboard(self, ws: Path) -> None:
        apply_answers(ws, {
            "identity": "Documentation engineer and researcher.",
            "positioning": "I explain technical systems clearly.",
            "expertise": "Technical documentation, AI workflows, research.",
            "audience": "Developers, product teams, and researchers.",
            "goals": "Build trust and attract relevant collaborations.",
        })

    def test_doctor_points_incomplete_user_to_onboarding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root)
            report = doctor("demo", root)
            self.assertTrue(report["healthy"])
            self.assertFalse(report["ready"])
            self.assertEqual(report["status"], "needs_attention")
            self.assertIn("onboard demo", report["next_action"])

    def test_doctor_reports_ready_after_profile_samples_and_learning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = self._workspace(root)
            self._onboard(ws)
            samples = [
                "I start with the problem and explain why it matters. Then I give a practical example that someone can use.",
                "Clear documentation helps people act. I prefer simple steps, useful context, and limitations when they matter.",
                "For example, I test a workflow before recommending it. Then I explain what changed and what to check next.",
            ]
            for index, text in enumerate(samples):
                (ws / "writing-samples" / f"sample-{index}.txt").write_text(text, encoding="utf-8")
            save_for_user("demo", root)
            report = doctor("demo", root)
            self.assertTrue(report["healthy"])
            self.assertTrue(report["ready"])
            self.assertEqual(report["status"], "ready")
            self.assertIn("Ready to use", report["next_action"])

    def test_doctor_catches_corrupted_preferences(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = self._workspace(root)
            self._onboard(ws)
            (ws / "preferences.jsonl").write_text("{bad-json\n", encoding="utf-8")
            report = doctor("demo", root)
            self.assertFalse(report["healthy"])
            self.assertFalse(report["ready"])
            self.assertEqual(report["status"], "needs_fix")
            self.assertTrue(any("preferences.jsonl" in item for item in report["problems"]))

    def test_doctor_rejects_non_object_claim_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = self._workspace(root)
            self._onboard(ws)
            (ws / "claim-ledger.json").write_text(json.dumps([]), encoding="utf-8")
            report = doctor("demo", root)
            self.assertFalse(report["healthy"])
            self.assertTrue(any("claim-ledger.json" in item for item in report["problems"]))


if __name__ == "__main__":
    unittest.main()
