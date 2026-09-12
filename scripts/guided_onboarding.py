#!/usr/bin/env python3
"""Friendly guided onboarding for non-technical Credora users."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.profile_intelligence import save_for_user
from scripts.workspace import user_root

ROOT = Path(__file__).resolve().parents[1]

QUESTIONS = [
    ("identity", "In one or two lines, who are you professionally?", "identity.md", "# Identity\n\n"),
    ("positioning", "What do you want people to know you for?", "positioning.md", "# Positioning\n\n"),
    ("expertise", "What 3-5 topics can you credibly teach, explain, or comment on?", "expertise.md", "# Expertise\n\n"),
    ("audience", "Who do you most want to help or reach?", "audience.md", "# Audience\n\n"),
    ("goals", "What should your social presence help you achieve?", "profile-goals.md", "# Profile Goals\n\n"),
]


def _clean_answer(value: str) -> str:
    return value.strip()


def apply_answers(workspace: Path, answers: dict[str, str], overwrite: bool = False) -> list[str]:
    updated = []
    for key, _, rel, heading in QUESTIONS:
        answer = _clean_answer(answers.get(key, ""))
        if not answer:
            continue
        path = workspace / rel
        if path.exists() and not overwrite:
            existing = path.read_text(encoding="utf-8")
            if "Status: not initialized" not in existing and "- TBD" not in existing:
                continue
        path.write_text(heading + answer + "\n", encoding="utf-8")
        updated.append(rel)
    return updated


def interactive_answers() -> dict[str, str]:
    print("\nCredora setup\n-------------")
    print("Short, natural answers are enough. You can type 'skip' for anything you want to fill later.\n")
    answers: dict[str, str] = {}
    for key, prompt, _, _ in QUESTIONS:
        value = input(f"{prompt}\n> ").strip()
        if value.lower() != "skip":
            answers[key] = value
        print()
    return answers


def main() -> int:
    parser = argparse.ArgumentParser(description="Guided Credora personal brand onboarding")
    parser.add_argument("user", help="Workspace slug created by credora setup")
    parser.add_argument("--answers", help="Optional JSON file for non-interactive onboarding")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        workspace = user_root(ROOT, args.user)
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2
    if not workspace.is_dir():
        print(json.dumps({"status": "error", "error": f"User workspace does not exist: {args.user}"}, indent=2))
        return 2

    if args.answers:
        try:
            answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            print(json.dumps({"status": "error", "error": f"Could not read onboarding answers: {exc}"}, indent=2))
            return 2
        if not isinstance(answers, dict):
            print(json.dumps({"status": "error", "error": "Onboarding answers must be a JSON object."}, indent=2))
            return 2
    else:
        answers = interactive_answers()

    updated = apply_answers(workspace, answers, overwrite=args.overwrite)
    brain = save_for_user(args.user)
    result = {"status": "ok", "user": args.user, "updated_files": updated, "brand_brain": brain}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
