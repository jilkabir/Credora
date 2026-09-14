#!/usr/bin/env python3
"""Build a private, model-agnostic personalization pack from verified user data.

This does not train an LLM's weights. It prepares grounded examples, preferences,
brand context, and style rules that an external model can use at generation time.
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.style_profile import load_for_user
from scripts.workspace import user_root

TEXT_SUFFIXES = {".txt", ".md"}


def _read_samples(folder: Path, limit: int, max_chars: int) -> list[dict]:
    if not folder.is_dir():
        return []
    items: list[dict] = []
    used = 0
    for path in sorted(folder.iterdir()):
        if len(items) >= limit or used >= max_chars:
            break
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        remaining = max_chars - used
        excerpt = text[:remaining]
        if not excerpt:
            break
        items.append({"source": path.name, "text": excerpt, "truncated": len(excerpt) < len(text)})
        used += len(excerpt)
    return items


def _active_preferences(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out: list[dict] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid preferences.jsonl at line {line_number}: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Invalid preferences.jsonl at line {line_number}: expected object")
        if value.get("active", True) and isinstance(value.get("rule"), str) and value["rule"].strip():
            out.append({
                "scope": value.get("scope", "writing"),
                "kind": value.get("kind", "preference"),
                "rule": value["rule"].strip(),
                "source": value.get("source", "user_workspace"),
            })
    return out


def build_training_pack(slug: str, root: Path, *, max_writing_samples: int = 8, max_chars: int = 12000) -> dict:
    if max_writing_samples < 1 or max_writing_samples > 30:
        raise ValueError("max_writing_samples must be between 1 and 30")
    if max_chars < 500 or max_chars > 50000:
        raise ValueError("max_chars must be between 500 and 50000")
    workspace = user_root(root, slug)
    if not workspace.is_dir():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")

    brain_path = workspace / "brand-brain.json"
    brain: dict = {}
    if brain_path.is_file():
        try:
            value = json.loads(brain_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid brand-brain.json: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError("Invalid brand-brain.json: expected object")
        brain = value

    style, style_source = load_for_user(root, slug)
    writing = _read_samples(workspace / "writing-samples", max_writing_samples, max_chars)
    speaking = _read_samples(workspace / "speaking-samples", min(5, max_writing_samples), max_chars // 2)
    preferences = _active_preferences(workspace / "preferences.jsonl")

    warnings: list[str] = []
    if len(writing) < 3:
        warnings.append("Fewer than 3 real writing samples; writing imitation confidence should stay low.")
    if not brain:
        warnings.append("Brand Brain is missing; run Credora learn before relying on positioning guidance.")
    if not speaking:
        warnings.append("No speaking samples; video scripts should not assume writing voice equals speaking voice.")

    return {
        "schema_version": 1,
        "user": slug,
        "purpose": "runtime personalization context, not model-weight training",
        "privacy": "private user workspace; do not commit raw examples to the public repository",
        "brand": {
            "status": brain.get("status", "missing"),
            "confidence": brain.get("confidence", "low"),
            "positioning_signals": brain.get("positioning_signals", []),
            "source_sections": brain.get("source_sections", {}),
            "writing_strategy": brain.get("writing_strategy", {}),
        },
        "style": style,
        "style_source": style_source,
        "active_preferences": preferences,
        "writing_examples": writing,
        "speaking_examples": speaking,
        "safety_rules": [
            "Never invent facts, metrics, stories, credentials, clients, quotes, or outcomes.",
            "Missing context is not permission to infer.",
            "Use writing examples as soft style evidence, not text to copy verbatim.",
            "Keep final user approval mandatory before scheduling or publishing.",
        ],
        "warnings": warnings,
    }


def save_training_pack(slug: str, root: Path, **kwargs) -> dict:
    workspace = user_root(root, slug)
    pack = build_training_pack(slug, root, **kwargs)
    target = workspace / "training-pack.json"
    target.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "status": "ok",
        "user": slug,
        "training_pack": str(target),
        "writing_examples": len(pack["writing_examples"]),
        "speaking_examples": len(pack["speaking_examples"]),
        "preferences": len(pack["active_preferences"]),
        "brand_status": pack["brand"]["status"],
        "warnings": pack["warnings"],
    }
