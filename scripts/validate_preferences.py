#!/usr/bin/env python3
"""Validate Credora preference-feedback JSONL without external dependencies."""
import argparse
import json
from pathlib import Path

REQUIRED = {"date", "scope", "rule", "kind", "source", "active"}
KINDS = {"prefer", "avoid", "require"}


def validate(path: Path):
    errors = []
    records = 0
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        records += 1
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        missing = REQUIRED - set(item)
        if missing:
            errors.append(f"line {line_no}: missing {', '.join(sorted(missing))}")
        if item.get("kind") not in KINDS:
            errors.append(f"line {line_no}: kind must be one of {', '.join(sorted(KINDS))}")
        if "active" in item and not isinstance(item["active"], bool):
            errors.append(f"line {line_no}: active must be boolean")
        if not isinstance(item.get("rule", ""), str) or not item.get("rule", "").strip():
            errors.append(f"line {line_no}: rule must be non-empty text")
    return {"valid": not errors, "records": records, "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.path), indent=2))


if __name__ == "__main__":
    main()
