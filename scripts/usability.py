#!/usr/bin/env python3
"""Friendly Credora workspace health checks and next-step guidance."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.profile_intelligence import build_brand_brain
from scripts.style_profile import load_json_style
from scripts.workspace import user_root

PROFILE_FILES = [
    "identity.md", "positioning.md", "expertise.md", "audience.md",
    "profile-goals.md", "voice.md", "writing-rules.md", "forbidden-style.md",
]
PLATFORM_FILES = [
    "platforms/linkedin.md", "platforms/facebook.md",
    "platforms/instagram.md", "platforms/youtube.md",
]


def _count_text_files(folder: Path) -> int:
    if not folder.is_dir():
        return 0
    return sum(
        1 for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in {".txt", ".md"} and p.read_text(encoding="utf-8").strip()
    )


def _valid_json(path: Path) -> tuple[bool, str | None]:
    if not path.exists():
        return True, None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            return False, "expected a JSON object"
        return True, None
    except (json.JSONDecodeError, UnicodeError, OSError) as exc:
        return False, str(exc)


def _valid_jsonl(path: Path) -> tuple[bool, str | None]:
    if not path.exists():
        return True, None
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    return False, f"line {line_number} is not a JSON object"
        return True, None
    except (json.JSONDecodeError, UnicodeError, OSError) as exc:
        return False, str(exc)


def doctor(slug: str, root: Path) -> dict:
    workspace = user_root(root, slug)
    if not workspace.is_dir():
        return {
            "status": "error", "healthy": False, "ready": False, "user": slug,
            "problems": ["Workspace does not exist."], "warnings": [],
            "next_action": 'Create it first: python scripts/credora.py start "Your Name"',
        }

    problems: list[str] = []
    warnings: list[str] = []
    missing = [rel for rel in PROFILE_FILES + PLATFORM_FILES if not (workspace / rel).is_file()]
    if missing:
        problems.append("Missing workspace files: " + ", ".join(missing))

    uninitialized = []
    for rel in PROFILE_FILES:
        path = workspace / rel
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if "Status: not initialized" in text or "- TBD" in text:
                uninitialized.append(rel)
    if uninitialized:
        warnings.append("Profile setup is incomplete: " + ", ".join(uninitialized))

    samples = _count_text_files(workspace / "writing-samples")
    if samples == 0:
        warnings.append("No writing samples yet. Add 3 or more real samples for better voice matching.")
    elif samples < 3:
        warnings.append(f"Only {samples} writing sample(s). 3 or more is recommended.")

    pref_ok, pref_error = _valid_jsonl(workspace / "preferences.jsonl")
    if not pref_ok:
        problems.append(f"preferences.jsonl is invalid: {pref_error}")

    ledger_ok, ledger_error = _valid_json(workspace / "claim-ledger.json")
    if not ledger_ok:
        problems.append(f"claim-ledger.json is invalid: {ledger_error}")

    style_path = workspace / "style.json"
    if style_path.exists():
        try:
            load_json_style(style_path)
        except (ValueError, OSError, UnicodeError) as exc:
            problems.append(f"style.json is invalid: {exc}")
    else:
        warnings.append("No private style.json yet. Credora will use the conservative public default until one is created.")

    try:
        brain = build_brand_brain(workspace)
        completeness = brain.get("profile_completeness", 0)
        confidence = brain.get("confidence", "low")
    except (OSError, UnicodeError, ValueError) as exc:
        problems.append(f"Brand intelligence could not be built: {exc}")
        completeness = 0
        confidence = "low"

    brain_path = workspace / "brand-brain.json"
    if not brain_path.is_file():
        warnings.append("Brand brain has not been saved yet.")

    healthy = not problems
    ready = healthy and not uninitialized and samples >= 3 and brain_path.is_file() and completeness >= 80
    if problems:
        next_action = "Fix the reported errors, then run doctor again."
    elif uninitialized:
        next_action = f"Finish setup: python scripts/credora.py onboard {slug}"
    elif samples < 3:
        next_action = f"Add 3+ real writing samples to users/{slug}/writing-samples/ then run: python scripts/credora.py learn {slug}"
    elif not brain_path.is_file():
        next_action = f"Build the brand brain: python scripts/credora.py learn {slug}"
    else:
        next_action = f"Ready to use. Build context with: python scripts/credora.py context {slug} --platform linkedin --task post"

    return {
        "status": "ready" if ready else "needs_fix" if problems else "needs_attention",
        "healthy": healthy,
        "ready": ready,
        "user": slug,
        "profile_completeness": completeness,
        "brand_confidence": confidence,
        "writing_samples": samples,
        "brand_brain_built": brain_path.is_file(),
        "personal_style": "user" if style_path.is_file() else "default",
        "problems": problems,
        "warnings": warnings,
        "next_action": next_action,
    }
