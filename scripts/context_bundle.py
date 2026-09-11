#!/usr/bin/env python3
"""Build the Credora instruction bundle for a specific platform and task.

This makes the personalization layer easy to hand to Claude or another LLM.
No external dependencies and no publishing side effects.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BASE_FILES = [
    "profile/identity.md",
    "profile/positioning.md",
    "profile/expertise.md",
    "profile/audience.md",
    "profile/voice.md",
    "profile/writing-rules.md",
    "profile/forbidden-style.md",
]

PLATFORM_FILES = {
    "linkedin": "profile/platforms/linkedin.md",
    "facebook": "profile/platforms/facebook.md",
    "instagram": "profile/platforms/instagram.md",
    "youtube": "profile/platforms/youtube.md",
}


def build(platform: str, task: str) -> str:
    files = list(BASE_FILES)
    platform_file = PLATFORM_FILES.get(platform)
    if platform_file:
        files.append(platform_file)
    if platform == "youtube" or task in {"video", "video-script", "script"}:
        files.append("profile/talking-style.md")

    sections = [f"# Credora Personal Context\n\nPlatform: {platform}\nTask: {task}\n"]
    for rel in files:
        path = ROOT / rel
        if not path.exists():
            continue
        sections.append(f"\n---\n\n## Source: `{rel}`\n\n{path.read_text(encoding='utf-8').strip()}\n")

    sections.append(
        "\n---\n\n## Execution rule\n"
        "Use the loaded context as constraints, not as permission to invent missing facts. "
        "Draft the requested content, then run Credora review checks. "
        "Return READY FOR APPROVAL only when checks pass; user approval is still required.\n"
    )
    return "".join(sections)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--platform", choices=sorted(PLATFORM_FILES), default="linkedin")
    p.add_argument("--task", default="post")
    p.add_argument("--output")
    args = p.parse_args()
    text = build(args.platform, args.task)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
