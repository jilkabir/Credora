#!/usr/bin/env python3
"""Evidence-aware claim and hook guard for Credora.

This module does not verify sources itself. It evaluates wording against a
structured claim ledger and flags unsupported certainty, causal upgrades, and
unverifiable claims before publication.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CAUSAL_TERMS = re.compile(r"\b(causes?|caused|leads? to|results? in|drives?|prevents?|improves?|reduces?|increases?)\b", re.I)
CERTAINTY_TERMS = re.compile(r"\b(proves?|proven|definitely|always|never|guarantees?|undeniably|conclusively)\b", re.I)

VALID_STATUSES = {"supported", "partially_supported", "mixed", "unsupported", "unverifiable"}
VALID_CONFIDENCE = {"low", "medium", "high"}


def _normalize_claims(ledger: dict | None) -> tuple[list[dict], list[dict]]:
    """Return valid claim records plus validation flags instead of crashing."""
    flags: list[dict] = []
    if ledger is None:
        return [], flags
    if not isinstance(ledger, dict):
        return [], [{"claim_id": None, "severity": "block", "code": "invalid_ledger", "message": "Claim ledger must be a JSON object."}]
    raw_claims = ledger.get("claims", [])
    if not isinstance(raw_claims, list):
        return [], [{"claim_id": None, "severity": "block", "code": "invalid_claims", "message": "Claim ledger 'claims' must be an array."}]

    claims: list[dict] = []
    for index, claim in enumerate(raw_claims):
        if not isinstance(claim, dict):
            flags.append({"claim_id": None, "severity": "block", "code": "invalid_claim_record", "message": f"Claim at index {index} must be an object."})
            continue
        missing = [key for key in ("id", "claim", "status", "source_ids", "causal_language", "confidence") if key not in claim]
        if missing:
            flags.append({"claim_id": claim.get("id"), "severity": "block", "code": "incomplete_claim_record", "message": "Missing required claim fields: " + ", ".join(missing)})
            continue
        if claim.get("status") not in VALID_STATUSES:
            flags.append({"claim_id": claim.get("id"), "severity": "block", "code": "invalid_claim_status", "message": f"Unsupported claim status: {claim.get('status')}"})
            continue
        if claim.get("confidence") not in VALID_CONFIDENCE:
            flags.append({"claim_id": claim.get("id"), "severity": "block", "code": "invalid_claim_confidence", "message": f"Unsupported confidence value: {claim.get('confidence')}"})
            continue
        if not isinstance(claim.get("source_ids"), list) or not isinstance(claim.get("causal_language"), bool):
            flags.append({"claim_id": claim.get("id"), "severity": "block", "code": "invalid_claim_types", "message": "source_ids must be an array and causal_language must be boolean."})
            continue
        if not str(claim.get("claim", "")).strip():
            flags.append({"claim_id": claim.get("id"), "severity": "block", "code": "empty_claim", "message": "Claim text cannot be empty."})
            continue
        claims.append(claim)
    return claims, flags


def assess_text(text: str, ledger: dict | None) -> dict:
    claims, flags = _normalize_claims(ledger)
    lowered = text.lower()

    for claim in claims:
        claim_text = str(claim.get("claim", "")).strip()
        status = claim.get("status", "unverifiable")
        causal_allowed = bool(claim.get("causal_language", False))
        confidence = claim.get("confidence", "low")

        keywords = [w.lower() for w in re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", claim_text)]
        overlap = sum(1 for word in set(keywords) if word in lowered)
        if keywords and overlap < max(1, min(3, len(set(keywords)) // 3)):
            continue

        if status in {"unsupported", "unverifiable"}:
            flags.append({"claim_id": claim.get("id"), "severity": "block", "code": "unsupported_claim", "message": f"Claim status is {status}; do not present it as established fact."})
        elif status in {"mixed", "partially_supported"} and CERTAINTY_TERMS.search(text):
            flags.append({"claim_id": claim.get("id"), "severity": "revise", "code": "certainty_overreach", "message": "Mixed or partial evidence is paired with certainty language."})

        if not causal_allowed and CAUSAL_TERMS.search(text):
            flags.append({"claim_id": claim.get("id"), "severity": "revise", "code": "causal_upgrade", "message": "Ledger does not support causal language for this claim."})

        if confidence == "low" and CERTAINTY_TERMS.search(text):
            flags.append({"claim_id": claim.get("id"), "severity": "revise", "code": "confidence_mismatch", "message": "Low-confidence evidence is paired with high-certainty wording."})

    if not claims and not flags and (CAUSAL_TERMS.search(text) or CERTAINTY_TERMS.search(text)):
        flags.append({"claim_id": None, "severity": "review", "code": "no_ledger_evidence", "message": "Strong factual language appears without any claim-ledger evidence."})

    severity_order = {"block": 3, "revise": 2, "review": 1}
    max_severity = max((severity_order.get(f["severity"], 0) for f in flags), default=0)
    verdict = "ready" if max_severity == 0 else "blocked" if max_severity == 3 else "needs_revision"
    return {"verdict": verdict, "flags": flags, "claims_checked": len(claims)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("text_file")
    p.add_argument("ledger_file")
    args = p.parse_args()
    try:
        text = Path(args.text_file).read_text(encoding="utf-8")
        ledger = json.loads(Path(args.ledger_file).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"verdict": "blocked", "flags": [{"claim_id": None, "severity": "block", "code": "input_error", "message": str(exc)}], "claims_checked": 0}, indent=2, ensure_ascii=False))
        return 2
    report = assess_text(text, ledger)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["verdict"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
