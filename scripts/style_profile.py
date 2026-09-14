#!/usr/bin/env python3
"""Load and validate per-user writing-style configuration."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.workspace import user_root

REQUIRED_LIMIT_KEYS = {
    "max_emojis_per_300_words",
    "max_em_dash_per_300_words",
    "max_single_sentence_paragraph_ratio",
}


def validate_style_config(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Style config must be a JSON object.")
    threshold = value.get("voice_fit_threshold", 65)
    if not isinstance(threshold, (int, float)) or not 0 <= float(threshold) <= 100:
        raise ValueError("voice_fit_threshold must be between 0 and 100.")
    for key in ("hard_banned_phrases", "generic_ctas", "notes"):
        current = value.get(key, [])
        if not isinstance(current, list) or not all(isinstance(item, str) for item in current):
            raise ValueError(f"{key} must be an array of strings.")
    limits = value.get("limits", {})
    if not isinstance(limits, dict):
        raise ValueError("limits must be a JSON object.")
    missing = REQUIRED_LIMIT_KEYS - set(limits)
    if missing:
        raise ValueError("Style limits missing: " + ", ".join(sorted(missing)))
    for key in REQUIRED_LIMIT_KEYS:
        if not isinstance(limits[key], (int, float)) or limits[key] < 0:
            raise ValueError(f"Invalid style limit: {key}")
    return value


def load_json_style(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid style JSON in {path}: {exc.msg}") from exc
    return validate_style_config(value)


def load_for_user(root: Path, slug: str, fallback: Path | None = None) -> tuple[dict, str]:
    workspace = user_root(root, slug)
    if not workspace.is_dir():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")
    user_style = workspace / "style.json"
    if user_style.is_file():
        return load_json_style(user_style), "user"
    fallback_path = fallback or root / "config" / "personal_style.json"
    if not fallback_path.is_file():
        raise FileNotFoundError(f"Default style config does not exist: {fallback_path}")
    return load_json_style(fallback_path), "default"
