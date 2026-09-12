#!/usr/bin/env python3
"""Produce a pre-publish Credora decision report.

Combines editorial quality, evidence guard results, repetition risk and optional
voice fit into a simple publication verdict. It does not publish content.
"""
from __future__ import annotations

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.claim_guard import assess_text
from scripts.quality_score import load_config, score
from scripts.voice_fit import compare as compare_voice

DEFAULT_VOICE_THRESHOLD = 65.0


def load_voice_threshold() -> float:
    """Load the configured voice-fit threshold with a safe fallback."""
    path = ROOT / "config" / "personal_style.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return float(data.get("voice_fit_threshold", DEFAULT_VOICE_THRESHOLD))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_VOICE_THRESHOLD


def repetition_check(text: str, history: list[str]) -> dict:
    if not history:
        return {"score": 0.0, "closest": None, "status": "no_history"}
    best_score = -1.0
    best_index = None
    for idx, previous in enumerate(history):
        ratio = SequenceMatcher(None, text.lower(), previous.lower()).ratio()
        if ratio > best_score:
            best_score = ratio
            best_index = idx
    pct = round(max(0.0, best_score) * 100, 1)
    status = "high" if pct >= 65 else "medium" if pct >= 40 else "low"
    return {"score": pct, "closest": best_index, "status": status}


def decide(
    text: str,
    ledger: dict | None = None,
    voice_samples: list[str] | None = None,
    history: list[str] | None = None,
    voice_threshold: float | None = None,
) -> dict:
    quality = score(text, load_config())
    evidence = assess_text(text, ledger or {"claims": []})
    repetition = repetition_check(text, history or [])
    voice = compare_voice(text, voice_samples or [])
    threshold = load_voice_threshold() if voice_threshold is None else float(voice_threshold)

    reasons: list[str] = []
    verdict = "READY"

    if evidence["verdict"] == "blocked":
        verdict = "NEEDS EVIDENCE"
        reasons.append("At least one claim is unsupported or unverifiable.")
    elif evidence["verdict"] == "needs_revision":
        verdict = "NEEDS REVISION"
        reasons.append("Evidence wording overreaches the ledger or confidence level.")

    if repetition.get("status") == "high" and verdict == "READY":
        verdict = "TOO REPETITIVE"
        reasons.append("Draft is highly similar to prior content.")

    if voice.get("status") == "ok" and voice.get("score", 100) < threshold and verdict == "READY":
        verdict = "VOICE MISMATCH"
        reasons.append(f"Draft voice-fit score is below the configured threshold of {threshold:g}.")

    if quality.get("overall", 100) < 55 and verdict == "READY":
        verdict = "NEEDS REVISION"
        reasons.append("Editorial quality score is below the current readiness threshold.")

    if not reasons:
        reasons.append("No blocking issue was detected by the local checks provided.")

    return {
        "verdict": verdict,
        "reasons": reasons,
        "quality": quality,
        "evidence": evidence,
        "repetition": repetition,
        "voice_fit": voice,
        "thresholds": {"voice_fit": threshold, "quality": 55, "repetition_high": 65},
        "note": "Decision support only. Credora does not verify source truth automatically or publish to social platforms.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("draft")
    p.add_argument("--ledger")
    p.add_argument("--voice-sample", action="append", default=[])
    p.add_argument("--history", action="append", default=[])
    p.add_argument("--voice-threshold", type=float)
    args = p.parse_args()

    text = Path(args.draft).read_text(encoding="utf-8")
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8")) if args.ledger else None
    voice_samples = [Path(x).read_text(encoding="utf-8") for x in args.voice_sample]
    history = [Path(x).read_text(encoding="utf-8") for x in args.history]
    print(
        json.dumps(
            decide(text, ledger, voice_samples, history, args.voice_threshold),
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
