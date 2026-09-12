#!/usr/bin/env python3
"""Build a Credora instruction bundle for a platform, task, and optional user workspace.

Default profile files keep backward compatibility. For plug-and-play multi-user use,
pass --user <slug> to load users/<slug>/ instead. No external dependencies and no
publishing side effects.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.workspace import user_root

BASE_FILES = [
    "identity.md",
    "positioning.md",
    "expertise.md",
    "audience.md",
    "voice.md",
    "writing-rules.md",
    "forbidden-style.md",
    "profile-goals.md",
]

PLATFORMS = {"linkedin", "facebook", "instagram", "youtube"}


def _root_for(user: str | None) -> Path:
    return user_root(ROOT, user) if user else ROOT / "profile"


def _load_preferences(path: Path, platform: str, task: str) -> list[dict]:
    if not path.exists():
        return []
    accepted = {"all", "global", "writing", platform, task}
    if platform == "youtube" or task in {"video", "video-script", "script"}:
        accepted.add("speaking")
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("active") is True and row.get("scope") in accepted:
            records.append(row)
    return records


def build(platform: str, task: str, user: str | None = None) -> str:
    if platform not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}")
    base = _root_for(user)
    files = list(BASE_FILES)
    files.append(f"platforms/{platform}.md")
    if platform == "youtube" or task in {"video", "video-script", "script"}:
        files.append("talking-style.md")

    title = "# Credora Personal Context\n\n"
    title += f"User: {user or 'default'}\nPlatform: {platform}\nTask: {task}\n"
    sections = [title]
    missing = []
    for rel in files:
        path = base / rel
        if not path.exists():
            missing.append(rel)
            continue
        sections.append(f"\n---\n\n## Source: `{path.relative_to(ROOT)}`\n\n{path.read_text(encoding='utf-8').strip()}\n")

    preferences = _load_preferences(base / "preferences.jsonl", platform, task)
    if preferences:
        sections.append("\n---\n\n## Active explicit user preferences\n")
        for item in preferences:
            sections.append(f"- [{item.get('kind','prefer')}] {item.get('rule','').strip()}\n")

    if missing:
        sections.append("\n---\n\n## Missing context\n")
        for rel in missing:
            sections.append(f"- {rel}\n")
        sections.append("Missing files are not permission to infer facts. Ask only when the missing information materially affects the task.\n")

    sections.append(
        "\n---\n\n## Execution rule\n"
        "Use the loaded context as constraints, not as permission to invent missing facts. "
        "Draft the requested content, then run Credora review checks. "
        "Return READY FOR APPROVAL only when checks pass; user approval is still required. "
        "Never auto-publish from this bundle.\n"
    )
    return "".join(sections)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--platform", choices=sorted(PLATFORMS), default="linkedin")
    p.add_argument("--task", default="post")
    p.add_argument("--user", help="Private workspace slug under users/<slug>")
    p.add_argument("--output")
    args = p.parse_args()
    try:
        text = build(args.platform, args.task, args.user)
    except ValueError as exc:
        p.error(str(exc))
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
