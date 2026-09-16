#!/usr/bin/env python3
"""Generate one Credora-reviewed draft from a calendar item."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.content_generation import generate_draft

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and review a Credora draft")
    parser.add_argument("user")
    parser.add_argument("calendar_id")
    parser.add_argument("--provider", choices=["openai", "anthropic"], required=True)
    parser.add_argument("--model")
    args = parser.parse_args()
    try:
        result = generate_draft(args.user, ROOT, args.calendar_id, args.provider, args.model)
    except (FileNotFoundError, ValueError, OSError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, ensure_ascii=False))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
