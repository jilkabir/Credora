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
    if not user:
        return ROOT / "profile"
    root = user_root(ROOT, user)
    if not root.is_dir():
        raise ValueError(f"User workspace does not exist: {user}")
    return root


def _load_preferences(path: Path, platform: str, task: str) -> list[dict]:
    if not path.exists():
        return []
    accepted = {"all", "global", "writing", platform, task}
    if platform == "youtube" or task in {"video", "video-script", "script"}:
        accepted.add("speaking")
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid preferences JSON on line {line_number} in {path}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"Invalid preference on line {line_number} in {path}: expected an object")
        if row.get("active") is True and row.get("scope") in accepted:
            rule = row.get("rule")
            if not isinstance(rule, str) or not rule.strip():
                raise ValueError(f"Invalid active preference on line {line_number} in {path}: rule must be non-empty text")
            records.append(row)
    return records


def _load_brand_brain(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid brand brain JSON in {path}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Invalid brand brain in {path}: expected an object")
    return value


def _brand_brain_context(brain: dict) -> str:
    strategy = brain.get("writing_strategy", {}) if isinstance(brain.get("writing_strategy"), dict) else {}
    voice = brain.get("voice_fingerprint", {}) if isinstance(brain.get("voice_fingerprint"), dict) else {}
    aggregate = voice.get("aggregate", {}) if isinstance(voice.get("aggregate"), dict) else {}
    lines = [
        "\n---\n\n## Personal Brand Brain\n",
        f"Confidence: {brain.get('confidence', 'unknown')}\n",
        f"Profile completeness: {brain.get('profile_completeness', 0)}%\n",
    ]
    signals = brain.get("positioning_signals", [])
    if isinstance(signals, list) and signals:
        lines.append("Positioning signals: " + ", ".join(str(x) for x in signals[:16]) + "\n")
    north_star = strategy.get("north_star")
    if north_star:
        lines.append(f"North star: {north_star}\n")
    sequence = strategy.get("draft_sequence", [])
    if isinstance(sequence, list) and sequence:
        lines.append("\nDraft intelligence sequence:\n")
        lines.extend(f"- {item}\n" for item in sequence)
    anti = strategy.get("anti_generic_rules", [])
    if isinstance(anti, list) and anti:
        lines.append("\nAnti-generic rules:\n")
        lines.extend(f"- {item}\n" for item in anti)
    if aggregate:
        lines.append("\nObservable writing rhythm:\n")
        for key in ("avg_sentence_length", "short_sentence_ratio", "avg_paragraph_words", "first_person_rate", "second_person_rate", "emoji_rate"):
            if key in aggregate:
                lines.append(f"- {key}: {aggregate[key]}\n")
        transitions = aggregate.get("common_transitions")
        if transitions:
            lines.append(f"- common_transitions: {transitions}\n")
    warnings = brain.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("\nConfidence warnings:\n")
        lines.extend(f"- {item}\n" for item in warnings)
    return "".join(lines)


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

    if user:
        brain = _load_brand_brain(base / "brand-brain.json")
        if brain:
            sections.append(_brand_brain_context(brain))
        else:
            sections.append("\n---\n\n## Personal Brand Brain\nNot built yet. Run `python scripts/credora.py learn <user>` after onboarding and adding writing samples.\n")

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
        "Start from the user's personal brand nerve, not from a generic viral template. "
        "Use the loaded context as constraints, not as permission to invent missing facts. "
        "Choose one audience-relevant angle, preserve the user's verified positioning, and use their observable writing rhythm when confidence allows. "
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
