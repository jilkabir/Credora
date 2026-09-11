#!/usr/bin/env python3
"""Credora clean-checkout verification.

Runs only with the Python standard library. It verifies that the core engines
and personalization layer can import, load configuration, process a draft,
validate memory, learn a voice fingerprint, and apply the approval gate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.approval_gate import approval_report, load_style
from scripts.clean_text import clean, load_config as load_style_config
from scripts.learn_voice import learn
from scripts.quality_score import score
from scripts.select_hook import rank
from scripts.validate_memory import validate_jsonl


def main() -> int:
    required = [
        ROOT / "config" / "style_flags.json",
        ROOT / "config" / "hooks.json",
        ROOT / "config" / "personal_style.json",
        ROOT / "profile" / "voice.md",
        ROOT / "profile" / "writing-rules.md",
        ROOT / "profile" / "forbidden-style.md",
        ROOT / "memory" / "posts.example.jsonl",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Missing required files: " + ", ".join(missing))

    config = load_style_config()
    personal_style = load_style()
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

    voice_result = learn([
        "Do you know why this matters? You can start with a simple example. However, there is a trade-off.",
        "For instance, you can test the idea first. Then explain what changes and why it matters.",
        "A practical explanation helps readers. You should also mention the limitation before the recommendation.",
    ])
    if voice_result.get("status") != "ok":
        raise SystemExit("Voice learner self-check failed")

    approval = approval_report("I tested this process with 12 records in 2026. The result changed my plan.", config=personal_style)
    if not approval.get("approval_required"):
        raise SystemExit("Approval gate self-check failed")

    summary = {
        "status": "PASS",
        "cleanup_report": report,
        "quality_score": result["overall"],
        "research_hook_options": len(hooks),
        "memory_records_checked": memory_result.get("records", 0),
        "voice_samples_checked": voice_result.get("sample_count", 0),
        "approval_status": approval.get("status"),
        "personal_style_profile": personal_style.get("profile"),
        "external_dependencies": 0,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
