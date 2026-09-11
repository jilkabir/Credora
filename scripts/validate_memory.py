#!/usr/bin/env python3
"""Validate Credora JSONL content-memory records.

Dependency-free and intentionally conservative. It checks structure only; it
does not verify whether claims or evidence are true.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "date": str,
    "first_line": str,
    "theme": str,
    "claim": str,
    "hook_type": str,
    "examples": list,
    "stories": list,
    "proof": list,
    "cta": str,
    "audience": str,
    "source_ids": list,
}


def validate_record(record: object, line_number: int) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"line {line_number}: record must be a JSON object"]

    for key, expected_type in REQUIRED.items():
        if key not in record:
            errors.append(f"line {line_number}: missing required field '{key}'")
            continue
        if not isinstance(record[key], expected_type):
            errors.append(
                f"line {line_number}: field '{key}' must be {expected_type.__name__}"
            )

    for key in ("examples", "stories", "proof", "source_ids"):
        value = record.get(key)
        if isinstance(value, list) and not all(isinstance(item, str) for item in value):
            errors.append(f"line {line_number}: '{key}' entries must all be strings")

    if isinstance(record.get("first_line"), str) and not record["first_line"].strip():
        errors.append(f"line {line_number}: 'first_line' cannot be empty")
    if isinstance(record.get("theme"), str) and not record["theme"].strip():
        errors.append(f"line {line_number}: 'theme' cannot be empty")

    return errors


def validate_jsonl(path: Path) -> dict:
    errors: list[str] = []
    count = 0

    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        count += 1
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON ({exc.msg})")
            continue
        errors.extend(validate_record(record, line_number))

    return {
        "file": str(path),
        "records": count,
        "valid": not errors,
        "errors": errors,
        "note": "Structure validation only; factual claims and evidence still require verification.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="JSONL content-memory file")
    args = parser.parse_args()

    report = validate_jsonl(Path(args.file))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
