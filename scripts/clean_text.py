#!/usr/bin/env python3
"""Deterministic text cleanup for Credora.

Dependency-free. Designed to improve copy quality without altering factual
meaning or claiming to evade AI detectors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "style_flags.json"

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
SPACE_RE = re.compile(r"[ \t]+")
MULTI_NL_RE = re.compile(r"\n{3,}")

PUNCT_MAP = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": " - ", "\u2026": "...", "\u2022": "-",
    "\u00a0": " ", "\u202f": " ",
})


def load_config() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {"safe_replacements": {}, "blocked_auto_terms": []}


def strip_format_chars(text: str) -> tuple[str, int]:
    out = []
    removed = 0
    for ch in text:
        if unicodedata.category(ch) == "Cf":
            removed += 1
            continue
        out.append(ch)
    return "".join(out), removed


def replace_outside_urls(text: str, replacements: dict[str, str]) -> tuple[str, list[tuple[str, str, int]]]:
    parts = []
    cursor = 0
    changes: list[tuple[str, str, int]] = []
    for m in URL_RE.finditer(text):
        chunk = text[cursor:m.start()]
        chunk, c = apply_replacements(chunk, replacements)
        changes.extend(c)
        parts.append(chunk)
        parts.append(m.group(0))
        cursor = m.end()
    tail, c = apply_replacements(text[cursor:], replacements)
    changes.extend(c)
    parts.append(tail)
    return "".join(parts), changes


def preserve_case(src: str, dst: str) -> str:
    if src.isupper():
        return dst.upper()
    if src[:1].isupper():
        return dst[:1].upper() + dst[1:]
    return dst


def apply_replacements(text: str, replacements: dict[str, str]) -> tuple[str, list[tuple[str, str, int]]]:
    changes = []
    for src, dst in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        pat = re.compile(r"(?<!\w)" + re.escape(src) + r"(?!\w)", re.I)
        count = 0
        def repl(m: re.Match) -> str:
            nonlocal count
            count += 1
            return preserve_case(m.group(0), dst)
        text = pat.sub(repl, text)
        if count:
            changes.append((src, dst, count))
    return text, changes


def clean(text: str, config: dict) -> tuple[str, dict]:
    report = {"format_chars_removed": 0, "phrase_replacements": [], "whitespace_normalized": False}

    text, removed = strip_format_chars(text)
    report["format_chars_removed"] = removed

    before_punct = text
    text = text.translate(PUNCT_MAP)
    text = re.sub(r"\s+-\s+", " - ", text)
    report["typography_normalized"] = text != before_punct

    text, changes = replace_outside_urls(text, config.get("safe_replacements", {}))
    report["phrase_replacements"] = [
        {"from": a, "to": b, "count": n} for a, b, n in changes
    ]

    before_ws = text
    lines = [SPACE_RE.sub(" ", line).rstrip() for line in text.splitlines()]
    text = "\n".join(lines).strip()
    text = MULTI_NL_RE.sub("\n\n", text)
    report["whitespace_normalized"] = text != before_ws

    return text, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="UTF-8 text file")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    cleaned, report = clean(text, load_config())

    if args.in_place:
        path.write_text(cleaned + ("\n" if cleaned else ""), encoding="utf-8")
    else:
        sys.stdout.write(cleaned)
        if cleaned and not cleaned.endswith("\n"):
            sys.stdout.write("\n")

    if args.report:
        sys.stderr.write("\nCREDORA CLEANUP REPORT\n")
        sys.stderr.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
