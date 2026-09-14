import tempfile
import unittest
from pathlib import Path

from scripts.social_manager import create_calendar, manager_status, queue_draft, set_approval


class SocialManagerTests(unittest.TestCase):
    def _root(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "users" / "demo").mkdir(parents=True)
        return root

    def test_calendar_requires_approval_and_never_autopublishes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            report = create_calendar("demo", root, month="2026-10", posts=4)
            self.assertEqual(report["posts"], 4)
            self.assertTrue(all(x["approval_required"] for x in report["items"]))
            self.assertTrue(all(not x["auto_publish"] for x in report["items"]))

    def test_draft_moves_to_approval_queue_then_can_be_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            calendar = create_calendar("demo", root, month="2026-10", posts=1)
            draft = root / "draft.txt"
            draft.write_text("A useful draft that the user must approve.", encoding="utf-8")
            queued = queue_draft("demo", root, calendar_id=calendar["items"][0]["id"], draft_file=draft)
            self.assertEqual(queued["status"], "waiting_approval")
            status = manager_status("demo", root)
            self.assertEqual(status["waiting_approval"], 1)
            self.assertFalse(status["publishing_connected"])
            approved = set_approval("demo", root, queued["id"], True)
            self.assertEqual(approved["status"], "approved")
            self.assertIsNotNone(approved["approved_at"])

    def test_bad_month_and_empty_draft_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            with self.assertRaises(ValueError):
                create_calendar("demo", root, month="October")
            calendar = create_calendar("demo", root, month="2026-10", posts=1)
            draft = root / "draft.txt"
            draft.write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                queue_draft("demo", root, calendar_id=calendar["items"][0]["id"], draft_file=draft)


if __name__ == "__main__":
    unittest.main()
