import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.context_bundle import build as build_context
from scripts.guided_onboarding import apply_answers
from scripts.profile_intelligence import build_brand_brain, save_for_user


class ProfileIntelligenceTests(unittest.TestCase):
    def _workspace(self, root: Path) -> Path:
        ws = root / "users" / "demo"
        (ws / "platforms").mkdir(parents=True)
        (ws / "writing-samples").mkdir()
        for rel in ["writing-rules.md", "forbidden-style.md"]:
            (ws / rel).write_text("# Rules\nClear and practical.\n", encoding="utf-8")
        (ws / "voice.md").write_text("# Writing Voice\n\nStatus: not initialized\n", encoding="utf-8")
        (ws / "platforms" / "linkedin.md").write_text("# LinkedIn\nProfessional and useful.\n", encoding="utf-8")
        return ws

    def test_guided_answers_create_profile_nerve(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self._workspace(Path(tmp))
            updated = apply_answers(ws, {
                "identity": "Documentation engineer and researcher.",
                "positioning": "I explain technical systems clearly.",
                "expertise": "Technical documentation, AI workflows, research.",
                "audience": "Developers, product teams, and researchers.",
                "goals": "Build trust and attract relevant collaborations.",
            })
            self.assertEqual(len(updated), 5)
            brain = build_brand_brain(ws)
            self.assertEqual(brain["profile_completeness"], 100)
            self.assertIn("documentation", brain["positioning_signals"])
            self.assertEqual(brain["status"], "ready")

    def test_learning_persists_voice_profile_and_context_uses_brand_brain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = self._workspace(root)
            apply_answers(ws, {
                "identity": "Documentation engineer.",
                "positioning": "Clear technical communication.",
                "expertise": "Documentation and AI workflows.",
                "audience": "Developers and technical teams.",
                "goals": "Build professional trust.",
            })
            samples = [
                "I usually start with the problem. Then I explain why it matters. A practical example makes the idea easier to use.",
                "Documentation is useful when people can act on it. I prefer clear steps and I mention limitations when they matter.",
                "For example, I test a workflow before recommending it. Then I explain what changed and what someone should check next.",
            ]
            for i, text in enumerate(samples):
                (ws / "writing-samples" / f"sample-{i}.txt").write_text(text, encoding="utf-8")
            result = save_for_user("demo", root)
            self.assertTrue(result["voice_profile_updated"])
            self.assertIn("Status: learned from real user writing samples", (ws / "voice.md").read_text(encoding="utf-8"))
            brain = json.loads((ws / "brand-brain.json").read_text(encoding="utf-8"))
            self.assertEqual(brain["voice_fingerprint"]["status"], "ok")
            with patch("scripts.context_bundle.ROOT", root):
                bundle = build_context("linkedin", "post", "demo")
            self.assertIn("Personal Brand Brain", bundle)
            self.assertIn("Anti-generic rules", bundle)
            self.assertIn("Start from the user's personal brand nerve", bundle)


if __name__ == "__main__":
    unittest.main()
