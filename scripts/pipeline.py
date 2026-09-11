#!/usr/bin/env python3
"""Run Credora's local editorial pipeline on a UTF-8 draft.

Stages:
1. deterministic cleanup
2. editorial quality scoring
3. intent-based hook suggestions

This pipeline does not fact-check claims or predict LinkedIn performance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.clean_text import clean, load_config as load_style_config
from scripts.quality_score import score
from scripts.select_hook import rank


def run_pipeline(text: str, intent: str = "analysis", hook_limit: int = 3) -> dict:
    style_config = load_style_config()
    cleaned, cleanup_report = clean(text, style_config)
    quality = score(cleaned, style_config)
    hooks = rank(intent, max(1, hook_limit))

    return {
        "cleaned_text": cleaned,
        "cleanup": cleanup_report,
        "quality": quality,
        "hook_suggestions": hooks,
        "intent": intent,
        "warnings": [
            "Hook suggestions are editorial options, not reach predictions.",
            "This local pipeline does not verify factual claims; use the fact-check workflow before publishing factual content.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="UTF-8 draft file")
    parser.add_argument("--intent", default="analysis", help="research, proof, story, teach, analysis, etc.")
    parser.add_argument("--hooks", type=int, default=3, help="number of hook options")
    parser.add_argument("--write-cleaned", help="optional output path for cleaned draft")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    report = run_pipeline(text, args.intent, args.hooks)

    if args.write_cleaned:
        Path(args.write_cleaned).write_text(report["cleaned_text"] + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
