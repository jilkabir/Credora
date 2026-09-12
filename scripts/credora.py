#!/usr/bin/env python3
"""Credora plug-and-play command line entrypoint.

One command surface for private user setup, context generation, workspace status,
and personalized draft review. It never auto-publishes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.context_bundle import build
from scripts.init_user import init_user
from scripts.review_draft import review

REQUIRED_PROFILE_FILES = [
    "identity.md", "positioning.md", "expertise.md", "audience.md", "voice.md",
    "writing-rules.md", "forbidden-style.md", "profile-goals.md",
    "platforms/linkedin.md", "platforms/facebook.md", "platforms/instagram.md", "platforms/youtube.md",
]


def workspace_status(slug: str) -> dict:
    root = ROOT / "users" / slug
    if not root.exists():
        return {"status": "missing", "user": slug, "ready": False}
    missing = [x for x in REQUIRED_PROFILE_FILES if not (root / x).exists()]
    uninitialized = []
    for rel in REQUIRED_PROFILE_FILES:
        path = root / rel
        if path.exists() and "Status: not initialized" in path.read_text(encoding="utf-8"):
            uninitialized.append(rel)
    ready = not missing and not uninitialized
    return {
        "status": "ready" if ready else "incomplete",
        "user": slug,
        "ready": ready,
        "missing_files": missing,
        "uninitialized_files": uninitialized,
        "approval_required": True,
        "auto_publish": False,
    }


def _read_text_files(folder: Path) -> list[str]:
    if not folder.exists():
        return []
    samples: list[str] = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                samples.append(text)
    return samples


def _load_user_review_inputs(slug: str) -> tuple[dict | None, list[str], list[str]]:
    root = ROOT / "users" / slug
    if not root.exists():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")

    ledger = None
    ledger_path = root / "claim-ledger.json"
    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

    voice_samples = _read_text_files(root / "writing-samples")
    history = _read_text_files(root / "content-history")
    return ledger, voice_samples, history


def main() -> int:
    p = argparse.ArgumentParser(prog="credora", description="Credora personal social media manager")
    sub = p.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup", help="Create a private user workspace")
    setup.add_argument("name")
    setup.add_argument("--slug")

    status = sub.add_parser("status", help="Inspect a user workspace")
    status.add_argument("user")

    context = sub.add_parser("context", help="Build an LLM-ready personal context bundle")
    context.add_argument("user")
    context.add_argument("--platform", choices=["linkedin", "facebook", "instagram", "youtube"], default="linkedin")
    context.add_argument("--task", default="post")
    context.add_argument("--output")

    check = sub.add_parser("review", help="Run readiness checks on a draft")
    check.add_argument("draft")
    check.add_argument("--user", help="Load this user's private voice samples, history, and claim ledger")
    check.add_argument("--ledger", help="Optional explicit claim ledger JSON path; overrides user ledger")
    check.add_argument("--voice-sample", action="append", default=[], help="Optional extra writing sample path")
    check.add_argument("--history", action="append", default=[], help="Optional extra prior-content path")

    args = p.parse_args()

    if args.command == "setup":
        try:
            result = init_user(args.name, args.slug)
        except FileExistsError as exc:
            print(json.dumps({"status": "exists", "error": str(exc)}, indent=2))
            return 2
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "status":
        print(json.dumps(workspace_status(args.user), indent=2, ensure_ascii=False))
        return 0

    if args.command == "context":
        text = build(args.platform, args.task, args.user)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text)
        return 0

    if args.command == "review":
        text = Path(args.draft).read_text(encoding="utf-8")
        ledger = None
        voice_samples: list[str] = []
        history: list[str] = []

        if args.user:
            try:
                ledger, voice_samples, history = _load_user_review_inputs(args.user)
            except FileNotFoundError as exc:
                print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
                return 2

        if args.ledger:
            ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
        voice_samples.extend(Path(x).read_text(encoding="utf-8") for x in args.voice_sample)
        history.extend(Path(x).read_text(encoding="utf-8") for x in args.history)

        result = review(text, ledger=ledger, voice_samples=voice_samples, history=history)
        result["user"] = args.user
        result["inputs"] = {
            "voice_samples": len(voice_samples),
            "history_items": len(history),
            "claim_ledger": ledger is not None,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
