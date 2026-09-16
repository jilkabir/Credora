import json
import tempfile
import unittest
from pathlib import Path

from scripts.content_generation import prepare_generation_request


class ContentGenerationTests(unittest.TestCase):
    def _workspace(self, root: Path) -> Path:
        ws = root / "users" / "demo-user"
        (ws / "social-manager").mkdir(parents=True)
        (ws / "platforms").mkdir()
        (ws / "writing-samples").mkdir()
        (ws / "speaking-samples").mkdir()
        (ws / "platforms" / "linkedin.md").write_text("Use clear professional language.", encoding="utf-8")
        (ws / "writing-samples" / "one.txt").write_text("A real writing sample.", encoding="utf-8")
        (ws / "style.json").write_text(json.dumps({
            "profile":"demo",
            "version":2,
            "voice_fit_threshold":65,
            "hard_banned_phrases":[],
            "generic_ctas":[],
            "limits":{
                "max_emojis_per_300_words":2,
                "max_em_dash_per_300_words":1,
                "max_single_sentence_paragraph_ratio":0.55
            },
            "notes":[]
        }), encoding="utf-8")
        (ws / "brand-brain.json").write_text(json.dumps({
            "status":"ready", "confidence":"high", "positioning_signals":["documentation"],
            "source_sections":{"audience":"developers"}, "writing_strategy":{}
        }), encoding="utf-8")
        (ws / "social-manager" / "calendar.json").write_text(json.dumps({"items":[{
            "id":"2026-10-linkedin-01", "platform":"linkedin", "date":"2026-10-01",
            "pillar":"educational", "format":"text", "topic":"Explain documentation",
            "objective":"teach", "brand_signal":"documentation"
        }]}), encoding="utf-8")
        return ws

    def test_request_is_grounded_and_never_publishes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root)
            result = prepare_generation_request("demo-user", root, "2026-10-linkedin-01")
            self.assertEqual(result["status"], "ready_for_model")
            self.assertTrue(result["approval_required"])
            self.assertFalse(result["auto_publish"])
            request = json.loads(Path(result["request_file"]).read_text(encoding="utf-8"))
            self.assertEqual(request["provider"], "unbound")
            self.assertEqual(request["task"]["brand_signal"], "documentation")
            self.assertIn("professional language", request["platform_rules"])
            self.assertEqual(request["personalization"]["writing_examples"][0]["source"], "one.txt")

    def test_unknown_calendar_item_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root)
            with self.assertRaises(ValueError):
                prepare_generation_request("demo-user", root, "missing")

    def test_corrupt_calendar_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = self._workspace(root)
            (ws / "social-manager" / "calendar.json").write_text("{bad", encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare_generation_request("demo-user", root, "2026-10-linkedin-01")


if __name__ == "__main__":
    unittest.main()
