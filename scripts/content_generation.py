#!/usr/bin/env python3
"""Prepare grounded requests and generate reviewed drafts for calendar items."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.model_adapter import generate as call_model
from scripts.review_draft import review
from scripts.style_profile import load_for_user
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


def _read_text_files(folder: Path) -> list[str]:
    if not folder.exists():
        return []
    values = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                values.append(text)
    return values


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


def generate_draft(slug: str, root: Path, calendar_id: str, provider: str, model: str | None = None) -> dict:
    prepared = prepare_generation_request(slug, root, calendar_id)
    workspace = user_root(root, slug)
    request = _load_json(Path(prepared["request_file"]), "generation request")
    generated = call_model(request, provider=provider, model=model)
    text = generated["text"].strip()
    if not text:
        raise RuntimeError("Model returned an empty draft")

    drafts_dir = workspace / "social-manager" / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    draft_file = drafts_dir / f"{calendar_id}.txt"
    draft_file.write_text(text + "\n", encoding="utf-8")

    ledger_path = workspace / "claim-ledger.json"
    ledger = _load_json(ledger_path, "claim ledger") if ledger_path.is_file() else None
    voice_samples = _read_text_files(workspace / "writing-samples")
    history = _read_text_files(workspace / "content-history")
    style, style_source = load_for_user(root, slug)
    review_result = review(text, ledger=ledger, voice_samples=voice_samples, history=history, config=style)

    review_dir = workspace / "social-manager" / "generation-reviews"
    review_dir.mkdir(parents=True, exist_ok=True)
    review_file = review_dir / f"{calendar_id}.json"
    review_payload = {
        "calendar_id": calendar_id,
        "provider": generated["provider"],
        "model": generated["model"],
        "draft_file": str(draft_file),
        "style_source": style_source,
        "review": review_result,
        "approval_required": True,
        "auto_publish": False,
    }
    review_file.write_text(json.dumps(review_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "status": "draft_generated",
        "user": slug,
        "calendar_id": calendar_id,
        "provider": generated["provider"],
        "model": generated["model"],
        "draft_file": str(draft_file),
        "review_file": str(review_file),
        "review_decision": review_result.get("decision"),
        "approval_required": True,
        "auto_publish": False,
        "next": f"Review the draft, then queue it with calendar item {calendar_id}. Nothing is published automatically.",
    }
