#!/usr/bin/env python3
"""Apply personal hard-style rules and convert checks into approval status."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.decision_report import decide

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF]")


def load_style(path: Path | None = None) -> dict:
    target = path or ROOT / "config" / "personal_style.json"
    return json.loads(target.read_text(encoding="utf-8"))


def style_guard(text: str, config: dict | None = None) -> dict:
    config = config or load_style()
    lower = text.lower()
    words = max(1, len(re.findall(r"\b[\w'-]+\b", text)))
    units = max(1.0, words / 300.0)
    flags: list[dict] = []

    for phrase in config.get("hard_banned_phrases", []):
        if phrase.lower() in lower:
            flags.append({"code": "banned_phrase", "value": phrase})

    for phrase in config.get("generic_ctas", []):
        if phrase.lower() in lower:
            flags.append({"code": "generic_cta", "value": phrase})

    limits = config.get("limits", {})
    emoji_count = len(EMOJI_RE.findall(text))
    emoji_limit = int(limits.get("max_emojis_per_300_words", 2) * units)
    if emoji_count > max(1, emoji_limit):
        flags.append({"code": "emoji_overuse", "count": emoji_count})

    dash_count = text.count("—")
    dash_limit = int(limits.get("max_em_dash_per_300_words", 1) * units)
    if dash_count > max(1, dash_limit):
        flags.append({"code": "em_dash_overuse", "count": dash_count})

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if len(paragraphs) >= 4:
        one_sentence = 0
        for paragraph in paragraphs:
            sentences = [s for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()]
            if len(sentences) == 1:
                one_sentence += 1
        ratio = one_sentence / len(paragraphs)
        if ratio > limits.get("max_single_sentence_paragraph_ratio", 0.55):
            flags.append({"code": "fragmented_structure", "ratio": round(ratio, 3)})

    return {
        "verdict": "blocked" if flags else "pass",
        "flags": flags,
        "profile": config.get("profile", "default"),
    }


def approval_report(
    text: str,
    ledger: dict | None = None,
    voice_samples: list[str] | None = None,
    history: list[str] | None = None,
    config: dict | None = None,
) -> dict:
    effective_config = config or load_style()
    voice_threshold = float(effective_config.get("voice_fit_threshold", 65))
    decision = decide(
        text,
        ledger=ledger,
        voice_samples=voice_samples,
        history=history,
        voice_threshold=voice_threshold,
    )
    style = style_guard(text, config=effective_config)

    blockers: list[str] = []
    if decision["verdict"] != "READY":
        blockers.append(decision["verdict"])
    if style["verdict"] == "blocked":
        blockers.append("PERSONAL STYLE VIOLATION")

    status = "READY FOR APPROVAL" if not blockers else "NEEDS REVISION"
    return {
        "status": status,
        "blockers": blockers,
        "decision": decision,
        "personal_style": style,
        "approval_required": True,
        "note": "Passing Credora checks never substitutes for explicit user approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft")
    parser.add_argument("--ledger")
    parser.add_argument("--voice-sample", action="append", default=[])
    parser.add_argument("--history", action="append", default=[])
    args = parser.parse_args()

    text = Path(args.draft).read_text(encoding="utf-8")
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8")) if args.ledger else None
    voice_samples = [Path(x).read_text(encoding="utf-8") for x in args.voice_sample]
    history = [Path(x).read_text(encoding="utf-8") for x in args.history]
    print(json.dumps(approval_report(text, ledger, voice_samples, history), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
