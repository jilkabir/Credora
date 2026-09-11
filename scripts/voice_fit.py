#!/usr/bin/env python3
"""Compare a draft with user-provided writing samples.

This is a transparent style-fit heuristic, not authorship detection. It only
learns from explicit sample text supplied by the user.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
PUNCT = ["!", "?", ":", ";", "-", "(", ")"]


def _features(text: str) -> dict:
    words = WORD_RE.findall(text)
    sentences = [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]
    wc = max(1, len(words))
    lengths = [len(WORD_RE.findall(s)) for s in sentences] or [0]
    avg_sentence = sum(lengths) / len(lengths)
    short_ratio = sum(1 for n in lengths if n <= 8) / len(lengths)
    first_person = sum(1 for w in words if w.lower() in {"i", "i'm", "i've", "me", "my"}) / wc
    punctuation = {p: text.count(p) / wc for p in PUNCT}
    return {
        "avg_sentence_length": avg_sentence,
        "short_sentence_ratio": short_ratio,
        "first_person_rate": first_person,
        "punctuation": punctuation,
        "word_count": len(words),
        "sentence_count": len(sentences),
    }


def _similarity(a: float, b: float, scale: float) -> float:
    return max(0.0, 1.0 - abs(a - b) / max(scale, 1e-9))


def compare(draft: str, samples: list[str]) -> dict:
    usable = [s for s in samples if s.strip()]
    if not usable:
        return {
            "status": "needs_samples",
            "score": None,
            "confidence": "none",
            "reason": "No user-provided writing samples were supplied.",
        }

    reference = "\n\n".join(usable)
    d = _features(draft)
    r = _features(reference)

    components = {
        "sentence_length": _similarity(d["avg_sentence_length"], r["avg_sentence_length"], max(8.0, r["avg_sentence_length"])),
        "short_sentence_ratio": _similarity(d["short_sentence_ratio"], r["short_sentence_ratio"], 0.5),
        "first_person_rate": _similarity(d["first_person_rate"], r["first_person_rate"], 0.08),
    }
    punct_scores = [_similarity(d["punctuation"][p], r["punctuation"][p], 0.05) for p in PUNCT]
    components["punctuation"] = sum(punct_scores) / len(punct_scores)

    score = round(sum(components.values()) / len(components) * 100, 1)
    sample_words = r["word_count"]
    confidence = "high" if sample_words >= 1000 else "medium" if sample_words >= 300 else "low"
    return {
        "status": "ok",
        "score": score,
        "confidence": confidence,
        "sample_word_count": sample_words,
        "components": {k: round(v * 100, 1) for k, v in components.items()},
        "draft_features": d,
        "reference_features": r,
        "note": "Style-fit heuristic only; it does not determine authorship or whether text is AI-written.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("draft")
    p.add_argument("samples", nargs="+")
    args = p.parse_args()
    draft = Path(args.draft).read_text(encoding="utf-8")
    samples = [Path(path).read_text(encoding="utf-8") for path in args.samples]
    print(json.dumps(compare(draft, samples), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
