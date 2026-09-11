#!/usr/bin/env python3
"""Credora plug-and-play command line entrypoint.

One command surface for private user setup, context generation, workspace status,
and draft review. It never auto-publishes.
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


def workspace_status(slug: str) -> dict:
    root = ROOT / "users" / slug
    if not root.exists():
        return {"status": "missing", "user": slug, "ready": False}
    required = [
        "identity.md", "positioning.md", "expertise.md", "audience.md", "voice.md",
        "writing-rules.md", "forbidden-style.md", "profile-goals.md",
        "platforms/linkedin.md", "platforms/facebook.md", "platforms/instagram.md", "platforms/youtube.md",
    ]
    missing = [x for x in required if not (root / x).exists()]
    uninitialized = []
    for rel in required:
        path = root / rel
        if path.exists() and "Status: not initialized" in path.read_text(encoding="utf-8"):
            uninitialized.append(rel)
    return {
        "status": "ok" if not missing else "incomplete",
        "user": slug,
        "ready": not missing,
        "missing_files": missing,
        "uninitialized_files": uninitialized,
        "approval_required": True,
        "auto_publish": False,
    }


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
        print(json.dumps(review(text), indent=2, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
