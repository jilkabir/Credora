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
from scripts.workspace import user_root

REQUIRED_PROFILE_FILES = [
    "identity.md", "positioning.md", "expertise.md", "audience.md", "voice.md",
    "writing-rules.md", "forbidden-style.md", "profile-goals.md",
    "platforms/linkedin.md", "platforms/facebook.md", "platforms/instagram.md", "platforms/youtube.md",
]


def workspace_status(slug: str) -> dict:
    try:
        root = user_root(ROOT, slug)
    except ValueError as exc:
        return {"status": "error", "user": slug, "ready": False, "error": str(exc)}
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


def _load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {label} JSON in {path}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Invalid {label}: expected a JSON object in {path}")
    return value


def _load_user_review_inputs(slug: str) -> tuple[dict | None, list[str], list[str]]:
    root = user_root(ROOT, slug)
    if not root.exists():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")

    ledger = None
    ledger_path = root / "claim-ledger.json"
    if ledger_path.exists():
        ledger = _load_json(ledger_path, "claim ledger")

    voice_samples = _read_text_files(root / "writing-samples")
    history = _read_text_files(root / "content-history")
    return ledger, voice_samples, history


def _error(message: str, code: int = 2) -> int:
    print(json.dumps({"status": "error", "error": message}, indent=2, ensure_ascii=False))
    return code


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
        except (FileExistsError, ValueError) as exc:
            return _error(str(exc))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "status":
        result = workspace_status(args.user)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 2 if result["status"] == "error" else 0

    if args.command == "context":
        try:
            text = build(args.platform, args.task, args.user)
        except ValueError as exc:
            return _error(str(exc))
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text)
        return 0

    if args.command == "review":
        draft_path = Path(args.draft)
        if not draft_path.is_file():
            return _error(f"Draft file does not exist: {args.draft}")
        text = draft_path.read_text(encoding="utf-8")
        ledger = None
        voice_samples: list[str] = []
        history: list[str] = []

        if args.user:
            try:
                ledger, voice_samples, history = _load_user_review_inputs(args.user)
            except (FileNotFoundError, ValueError) as exc:
                return _error(str(exc))

        try:
            if args.ledger:
                ledger_path = Path(args.ledger)
                if not ledger_path.is_file():
                    return _error(f"Claim ledger file does not exist: {args.ledger}")
                ledger = _load_json(ledger_path, "claim ledger")
            for filename in args.voice_sample:
                path = Path(filename)
                if not path.is_file():
                    return _error(f"Voice sample file does not exist: {filename}")
                voice_samples.append(path.read_text(encoding="utf-8"))
            for filename in args.history:
                path = Path(filename)
                if not path.is_file():
                    return _error(f"History file does not exist: {filename}")
                history.append(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            return _error(str(exc))

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
