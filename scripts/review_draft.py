#!/usr/bin/env python3
"""Run Credora's local readiness checks for a draft.

This is the one-command review path for testing personalized content. It never
publishes and always leaves final approval to the user.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.approval_gate import approval_report


def review(
    text: str,
    ledger: dict | None = None,
    voice_samples: list[str] | None = None,
    history: list[str] | None = None,
    config: dict | None = None,
) -> dict:
    approval = approval_report(
        text,
        ledger=ledger,
        voice_samples=voice_samples,
        history=history,
        config=config,
    )
    return {
        "status": approval["status"],
        "approval_required": True,
        "blockers": approval["blockers"],
        "decision": approval["decision"],
        "approval_gate": approval,
        "note": "Credora review only. No content is published automatically.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("draft")
    p.add_argument("--ledger")
    p.add_argument("--voice-sample", action="append", default=[])
    p.add_argument("--history", action="append", default=[])
    args = p.parse_args()

    text = Path(args.draft).read_text(encoding="utf-8")
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8")) if args.ledger else None
    voice_samples = [Path(x).read_text(encoding="utf-8") for x in args.voice_sample]
    history = [Path(x).read_text(encoding="utf-8") for x in args.history]
    print(json.dumps(review(text, ledger, voice_samples, history), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
