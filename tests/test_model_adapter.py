import os
import unittest
from unittest.mock import patch

from scripts import model_adapter


class ModelAdapterTests(unittest.TestCase):
    def test_openai_requires_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                model_adapter.generate({"task": {}}, "openai")

    def test_anthropic_requires_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "ANTHROPIC_API_KEY"):
                model_adapter.generate({"task": {}}, "anthropic")

    def test_openai_response_is_parsed(self):
        response = {"output": [{"content": [{"type": "output_text", "text": "Draft text"}]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True), patch(
            "scripts.model_adapter._post_json", return_value=response
        ) as post:
            result = model_adapter.generate({"task": {"topic": "Test"}}, "openai", "test-model")
        self.assertEqual(result["text"], "Draft text")
        self.assertEqual(result["model"], "test-model")
        self.assertNotIn("test-key", str(post.call_args.args[2]))

    def test_anthropic_response_is_parsed(self):
        response = {"content": [{"type": "text", "text": "Claude draft"}]}
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True), patch(
            "scripts.model_adapter._post_json", return_value=response
        ):
            result = model_adapter.generate({"task": {"topic": "Test"}}, "anthropic", "test-model")
        self.assertEqual(result["text"], "Claude draft")

    def test_unknown_provider_fails(self):
        with self.assertRaises(ValueError):
            model_adapter.generate({}, "unknown")


if __name__ == "__main__":
    unittest.main()
