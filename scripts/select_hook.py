#!/usr/bin/env python3
"""Select Credora hook patterns by editorial intent.

This tool does not predict reach. It filters hook templates by the type of
content being written and returns transparent options for the writer to judge.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "config" / "hooks.json"


def load_hooks() -> list[dict]:
    data = json.loads(HOOKS.read_text(encoding="utf-8"))
    return data.get("hooks", [])


def rank(intent: str, limit: int) -> list[dict]:
    intent = intent.strip().lower()
    hooks = load_hooks()
    direct = [h for h in hooks if intent in [x.lower() for x in h.get("best_for", [])]]
    fallback = [h for h in hooks if h not in direct]
    return (direct + fallback)[:limit]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("intent", help="e.g. research, proof, story, teach, analysis")
    p.add_argument("--limit", type=int, default=3)
    args = p.parse_args()

    selected = rank(args.intent, max(1, args.limit))
    print(json.dumps({
        "intent": args.intent,
        "options": selected,
        "note": "These are editorial options, not performance predictions."
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
