import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.init_user import init_user
from scripts.style_profile import load_for_user, validate_style_config
from scripts.training_pack import build_training_pack, save_training_pack


class StyleTrainingTests(unittest.TestCase):
    def test_new_workspace_gets_private_style_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("scripts.init_user.USERS_ROOT", root / "users"):
                result = init_user("Demo Person")
            ws = root / "users" / result["slug"]
            style = json.loads((ws / "style.json").read_text(encoding="utf-8"))
            self.assertEqual(style["profile"], "demo-person-default")
            self.assertEqual(style["voice_fit_threshold"], 65)
            self.assertIn("style.json", result["files_created"])

    def test_user_style_overrides_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = root / "users" / "demo"
            ws.mkdir(parents=True)
            style = {
                "profile": "demo-custom",
                "voice_fit_threshold": 77,
                "hard_banned_phrases": [],
                "generic_ctas": [],
                "limits": {
                    "max_emojis_per_300_words": 1,
                    "max_em_dash_per_300_words": 0,
                    "max_single_sentence_paragraph_ratio": 0.4,
                },
                "notes": ["Custom user rules."],
            }
            (ws / "style.json").write_text(json.dumps(style), encoding="utf-8")
            loaded, source = load_for_user(root, "demo")
            self.assertEqual(source, "user")
            self.assertEqual(loaded["voice_fit_threshold"], 77)

    def test_invalid_style_threshold_is_rejected(self):
        bad = {
            "voice_fit_threshold": 120,
            "hard_banned_phrases": [],
            "generic_ctas": [],
            "notes": [],
            "limits": {
                "max_emojis_per_300_words": 1,
                "max_em_dash_per_300_words": 1,
                "max_single_sentence_paragraph_ratio": 0.5,
            },
        }
        with self.assertRaises(ValueError):
            validate_style_config(bad)

    def test_training_pack_uses_real_samples_preferences_and_brain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = root / "users" / "demo"
            (ws / "writing-samples").mkdir(parents=True)
            (ws / "speaking-samples").mkdir()
            for i in range(3):
                (ws / "writing-samples" / f"sample-{i}.txt").write_text(
                    f"Real writing sample {i}. I explain the reason, show an example, and mention limitations.",
                    encoding="utf-8",
                )
            (ws / "speaking-samples" / "talk.txt").write_text(
                "When I explain this aloud, I keep it simple and conversational.", encoding="utf-8"
            )
            (ws / "preferences.jsonl").write_text(
                json.dumps({"rule":"Avoid decorative em dashes.","active":True,"scope":"writing","kind":"avoid"}) + "\n",
                encoding="utf-8",
            )
            (ws / "brand-brain.json").write_text(
                json.dumps({"status":"ready","confidence":"high","positioning_signals":["documentation"],"source_sections":{"audience":"developers"},"writing_strategy":{"north_star":"Be useful."}}),
                encoding="utf-8",
            )
            (ws / "style.json").write_text(
                json.dumps({
                    "profile":"demo",
                    "voice_fit_threshold":65,
                    "hard_banned_phrases":[],
                    "generic_ctas":[],
                    "limits":{"max_emojis_per_300_words":2,"max_em_dash_per_300_words":1,"max_single_sentence_paragraph_ratio":0.55},
                    "notes":[],
                }), encoding="utf-8"
            )
            pack = build_training_pack("demo", root)
            self.assertEqual(len(pack["writing_examples"]), 3)
            self.assertEqual(len(pack["speaking_examples"]), 1)
            self.assertEqual(pack["brand"]["status"], "ready")
            self.assertEqual(pack["active_preferences"][0]["rule"], "Avoid decorative em dashes.")
            self.assertEqual(pack["purpose"], "runtime personalization context, not model-weight training")
            result = save_training_pack("demo", root)
            self.assertTrue((ws / "training-pack.json").is_file())
            self.assertEqual(result["writing_examples"], 3)

    def test_training_pack_rejects_malformed_preferences(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = root / "users" / "demo"
            ws.mkdir(parents=True)
            (ws / "preferences.jsonl").write_text("{bad-json\n", encoding="utf-8")
            (ws / "style.json").write_text(
                json.dumps({
                    "profile":"demo",
                    "voice_fit_threshold":65,
                    "hard_banned_phrases":[],
                    "generic_ctas":[],
                    "limits":{"max_emojis_per_300_words":2,"max_em_dash_per_300_words":1,"max_single_sentence_paragraph_ratio":0.55},
                    "notes":[],
                }), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                build_training_pack("demo", root)


if __name__ == "__main__":
    unittest.main()
