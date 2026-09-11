#!/usr/bin/env python3
"""Credora clean-checkout verification.

Runs only with the Python standard library. It verifies that the core engines
can import, load their configuration, process a draft, validate memory, and
produce representative output without external dependencies.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.clean_text import clean, load_config as load_style_config
from scripts.quality_score import score
from scripts.select_hook import rank
from scripts.validate_memory import validate_jsonl


def main() -> int:
    required = [
        ROOT / "config" / "style_flags.json",
        ROOT / "config" / "hooks.json",
        ROOT / "memory" / "posts.example.jsonl",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Missing required files: " + ", ".join(missing))

    config = load_style_config()
    sample = (
        "In today's fast-paced world, research proves everything.\n\n"
        "I tested this workflow with 12 example records in 2026."
    )
    cleaned, report = clean(sample, config)
    result = score(cleaned, config)
    hooks = rank("research", 3)

    if not cleaned or result.get("overall") is None or not hooks:
        raise SystemExit("Core engine self-check failed")

    memory_result = validate_jsonl(ROOT / "memory" / "posts.example.jsonl")
    if not memory_result.get("valid"):
        raise SystemExit("Example memory file failed validation")

    summary = {
        "status": "PASS",
        "cleanup_report": report,
        "quality_score": result["overall"],
        "research_hook_options": len(hooks),
        "memory_records_checked": memory_result.get("records", 0),
        "external_dependencies": 0,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
