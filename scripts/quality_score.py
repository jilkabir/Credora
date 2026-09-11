#!/usr/bin/env python3
"""Editorial quality scoring for Credora.

This is not an AI detector. It provides transparent, local heuristics for
specificity, rhythm, generic-language density, repetition, and readability.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "style_flags.json"

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")
DATE_RE = re.compile(r"\b(?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\b", re.I)
CAP_NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?\b")
BULLET_RE = re.compile(r"^\s*[-*•]\s+", re.M)


def clamp(v: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, v))


def load_config() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {"generic_phrases": [], "structural_tells": []}


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def specificity_score(text: str, wc: int) -> tuple[float, dict]:
    if wc == 0:
        return 0.0, {}
    numbers = len(NUMBER_RE.findall(text))
    dates = len(DATE_RE.findall(text))
    names = len(CAP_NAME_RE.findall(text))
    marker_rate = (numbers + dates + names) / wc * 100
    score = clamp(30 + marker_rate * 12)
    return score, {"numbers": numbers, "dates": dates, "named_markers": names, "markers_per_100_words": round(marker_rate, 2)}


def rhythm_score(sents: list[str]) -> tuple[float, dict]:
    lengths = [len(words(s)) for s in sents if words(s)]
    if len(lengths) < 2:
        return 55.0, {"sentence_lengths": lengths, "variation": None}
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    sd = math.sqrt(variance)
    cv = sd / mean if mean else 0
    # Moderate variation is rewarded; extreme jaggedness is not.
    score = 100 - abs(cv - 0.45) * 110
    return clamp(score, 35, 100), {"sentence_lengths": lengths, "mean": round(mean, 2), "variation": round(cv, 3)}


def generic_score(text: str, wc: int, phrases: list[str]) -> tuple[float, dict]:
    low = text.lower()
    hits = []
    total = 0
    for phrase in phrases:
        n = low.count(phrase.lower())
        if n:
            hits.append({"phrase": phrase, "count": n})
            total += n
    rate = (total / wc * 100) if wc else 0
    return clamp(100 - rate * 22), {"hits": hits, "hits_per_100_words": round(rate, 2)}


def repetition_score(text: str, sents: list[str], structural_tells: list[str]) -> tuple[float, dict]:
    starts = []
    for s in sents:
        ws = [w.lower() for w in words(s)]
        if ws:
            starts.append(" ".join(ws[:2]))
    repeated_starts = len(starts) - len(set(starts))
    low = text.lower()
    tells = [p for p in structural_tells if p.lower() in low]
    bullets = BULLET_RE.findall(text)
    penalty = repeated_starts * 8 + len(tells) * 10
    if len(bullets) >= 5:
        penalty += 5
    return clamp(100 - penalty), {"repeated_sentence_starts": repeated_starts, "structural_flags": tells, "bullet_lines": len(bullets)}


def readability_score(sents: list[str]) -> tuple[float, dict]:
    lengths = [len(words(s)) for s in sents if words(s)]
    if not lengths:
        return 0.0, {}
    long_sentences = sum(1 for n in lengths if n > 32)
    very_long = sum(1 for n in lengths if n > 45)
    score = 100 - long_sentences * 7 - very_long * 12
    return clamp(score), {"sentences_over_32_words": long_sentences, "sentences_over_45_words": very_long}


def score(text: str, config: dict) -> dict:
    ws = words(text)
    sents = sentences(text)
    wc = len(ws)
    spec, spec_meta = specificity_score(text, wc)
    rhythm, rhythm_meta = rhythm_score(sents)
    generic, generic_meta = generic_score(text, wc, config.get("generic_phrases", []))
    repeat, repeat_meta = repetition_score(text, sents, config.get("structural_tells", []))
    readable, readable_meta = readability_score(sents)

    dimensions = {
        "specificity": round(spec, 1),
        "rhythm": round(rhythm, 1),
        "generic_language": round(generic, 1),
        "structural_variety": round(repeat, 1),
        "readability": round(readable, 1),
    }
    overall = round(sum(dimensions.values()) / len(dimensions), 1)
    return {
        "overall": overall,
        "dimensions": dimensions,
        "meta": {
            "word_count": wc,
            "sentence_count": len(sents),
            "specificity": spec_meta,
            "rhythm": rhythm_meta,
            "generic_language": generic_meta,
            "structural_variety": repeat_meta,
            "readability": readable_meta,
        },
        "note": "Editorial heuristic only; not an AI-detector score."
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+", help="One file, or before.txt after.txt")
    args = p.parse_args()
    config = load_config()
    reports = []
    for f in args.files:
        text = Path(f).read_text(encoding="utf-8")
        reports.append({"file": f, **score(text, config)})
    if len(reports) == 2:
        reports.append({"delta": round(reports[1]["overall"] - reports[0]["overall"], 1)})
    print(json.dumps(reports, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
