#!/usr/bin/env python3
"""Prepare grounded, model-agnostic generation requests for calendar items."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.training_pack import build_training_pack
from scripts.workspace import user_root

SUPPORTED_PLATFORMS = {"linkedin", "facebook", "instagram", "youtube"}


def _load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"{label} does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {label}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Invalid {label}: expected object")
    return value


def prepare_generation_request(slug: str, root: Path, calendar_id: str) -> dict:
    workspace = user_root(root, slug)
    if not workspace.is_dir():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")

    calendar = _load_json(workspace / "social-manager" / "calendar.json", "calendar.json")
    items = calendar.get("items")
    if not isinstance(items, list):
        raise ValueError("Invalid calendar.json: items must be a list")
    item = next((x for x in items if isinstance(x, dict) and x.get("id") == calendar_id), None)
    if item is None:
        raise ValueError(f"Calendar item does not exist: {calendar_id}")

    platform = str(item.get("platform", "")).strip().lower()
    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform in calendar item: {platform or 'missing'}")

    pack = build_training_pack(slug, root)
    warnings = list(pack.get("warnings", []))
    if pack.get("brand", {}).get("status") != "ready":
        warnings.append("Brand Brain is not ready; generated copy must avoid inferred positioning claims.")

    platform_path = workspace / "platforms" / f"{platform}.md"
    platform_rules = platform_path.read_text(encoding="utf-8").strip() if platform_path.is_file() else ""
    if not platform_rules:
        warnings.append(f"No private {platform} platform guidance found; use conservative platform conventions.")

    task = {
        "calendar_id": calendar_id,
        "platform": platform,
        "date": item.get("date"),
        "pillar": item.get("pillar"),
        "format": item.get("format"),
        "topic": item.get("topic"),
        "objective": item.get("objective"),
        "brand_signal": item.get("brand_signal"),
    }
    instructions = [
        "Create one draft for the requested platform and format.",
        "Ground identity, positioning, expertise and personal claims only in the supplied personalization context.",
        "Do not invent metrics, clients, credentials, quotes, stories, research findings, experiences or outcomes.",
        "Treat writing examples as style evidence; never copy distinctive passages verbatim.",
        "Follow active preferences and style rules unless they conflict with factuality or safety.",
        "If evidence is insufficient for a personal or factual claim, omit or hedge it instead of guessing.",
        "Return draft text only; Credora will review it before user approval.",
    ]
    request = {
        "schema_version": 1,
        "provider": "unbound",
        "model": None,
        "user": slug,
        "task": task,
        "platform_rules": platform_rules,
        "personalization": pack,
        "instructions": instructions,
        "approval_required": True,
        "auto_publish": False,
        "warnings": warnings,
    }

    target_dir = workspace / "social-manager" / "generation-requests"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{calendar_id}.json"
    target.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "status": "ready_for_model",
        "user": slug,
        "calendar_id": calendar_id,
        "platform": platform,
        "request_file": str(target),
        "provider": "unbound",
        "approval_required": True,
        "auto_publish": False,
        "warnings": warnings,
    }
