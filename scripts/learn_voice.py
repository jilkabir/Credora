#!/usr/bin/env python3
"""Learn a transparent writing-style fingerprint from user-provided samples.

This module measures observable stylistic features only. It does not identify
author identity, infer sensitive traits, or determine whether text is AI-written.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
PARAGRAPH_RE = re.compile(r"\n\s*\n+")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF]")
TRANSITIONS = (
    "for instance", "for example", "however", "moreover", "besides", "so",
    "in addition", "on the other hand", "therefore", "finally", "well",
)
FIRST_PERSON = {"i", "i'm", "i've", "me", "my", "mine", "we", "we're", "we've", "our", "ours"}
SECOND_PERSON = {"you", "you're", "you've", "your", "yours"}


def _safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def features(text: str) -> dict:
    words = WORD_RE.findall(text)
    lower_words = [w.lower() for w in words]
    wc = max(1, len(words))
    sentences = [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]
    paragraphs = [p.strip() for p in PARAGRAPH_RE.split(text) if p.strip()]
    sentence_lengths = [len(WORD_RE.findall(s)) for s in sentences]
    paragraph_lengths = [len(WORD_RE.findall(p)) for p in paragraphs]
    lower_text = text.lower()

    transitions = {
        phrase: lower_text.count(phrase)
        for phrase in TRANSITIONS
        if lower_text.count(phrase)
    }
    punctuation = {
        "question_rate": text.count("?") / wc,
        "exclamation_rate": text.count("!") / wc,
        "colon_rate": text.count(":") / wc,
        "semicolon_rate": text.count(";") / wc,
        "dash_rate": (text.count("-") + text.count("—")) / wc,
    }

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "avg_sentence_length": round(_safe_mean(sentence_lengths), 2),
        "median_sentence_length": round(statistics.median(sentence_lengths), 2) if sentence_lengths else 0.0,
        "short_sentence_ratio": round(sum(1 for n in sentence_lengths if n <= 8) / max(1, len(sentence_lengths)), 4),
        "avg_paragraph_words": round(_safe_mean(paragraph_lengths), 2),
        "first_person_rate": round(sum(1 for w in lower_words if w in FIRST_PERSON) / wc, 4),
        "second_person_rate": round(sum(1 for w in lower_words if w in SECOND_PERSON) / wc, 4),
        "emoji_rate": round(len(EMOJI_RE.findall(text)) / wc, 4),
        "punctuation": {k: round(v, 4) for k, v in punctuation.items()},
        "transitions": transitions,
    }


def learn(samples: list[str]) -> dict:
    usable = [s.strip() for s in samples if s and s.strip()]
    if not usable:
        return {"status": "needs_samples", "confidence": "none", "sample_count": 0}

    per_sample = [features(text) for text in usable]
    total_words = sum(item["word_count"] for item in per_sample)
    transition_counts: Counter[str] = Counter()
    for item in per_sample:
        transition_counts.update(item["transitions"])

    aggregate = {
        "avg_sentence_length": round(_safe_mean([x["avg_sentence_length"] for x in per_sample]), 2),
        "short_sentence_ratio": round(_safe_mean([x["short_sentence_ratio"] for x in per_sample]), 4),
        "avg_paragraph_words": round(_safe_mean([x["avg_paragraph_words"] for x in per_sample]), 2),
        "first_person_rate": round(_safe_mean([x["first_person_rate"] for x in per_sample]), 4),
        "second_person_rate": round(_safe_mean([x["second_person_rate"] for x in per_sample]), 4),
        "emoji_rate": round(_safe_mean([x["emoji_rate"] for x in per_sample]), 4),
        "punctuation": {
            key: round(_safe_mean([x["punctuation"][key] for x in per_sample]), 4)
            for key in per_sample[0]["punctuation"]
        },
        "common_transitions": transition_counts.most_common(10),
    }
    confidence = "high" if len(usable) >= 8 and total_words >= 4000 else "medium" if len(usable) >= 3 and total_words >= 1000 else "low"
    return {
        "status": "ok",
        "confidence": confidence,
        "sample_count": len(usable),
        "sample_word_count": total_words,
        "aggregate": aggregate,
        "per_sample": per_sample,
        "note": "Observable style fingerprint only; not authorship detection and not an AI detector.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("samples", nargs="+", help="UTF-8 .txt or .md writing samples")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    texts = [Path(path).read_text(encoding="utf-8") for path in args.samples]
    report = learn(texts)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
