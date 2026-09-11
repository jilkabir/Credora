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


def assess_text(text: str, ledger: dict) -> dict:
    flags: list[dict] = []
    lowered = text.lower()
    claims = ledger.get("claims", []) if isinstance(ledger, dict) else []

    for claim in claims:
        claim_text = str(claim.get("claim", "")).strip()
        if not claim_text:
            continue
        status = claim.get("status", "unverifiable")
        causal_allowed = bool(claim.get("causal_language", False))
        confidence = claim.get("confidence", "low")

        # Conservative lexical overlap: enough to decide whether a ledger claim is
        # plausibly represented in the draft, without pretending semantic proof.
        keywords = [w.lower() for w in re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", claim_text)]
        overlap = sum(1 for word in set(keywords) if word in lowered)
        if keywords and overlap < max(1, min(3, len(set(keywords)) // 3)):
            continue

        if status in {"unsupported", "unverifiable"}:
            flags.append({
                "claim_id": claim.get("id"),
                "severity": "block",
                "code": "unsupported_claim",
                "message": f"Claim status is {status}; do not present it as established fact.",
            })
        elif status in {"mixed", "partially_supported"} and CERTAINTY_TERMS.search(text):
            flags.append({
                "claim_id": claim.get("id"),
                "severity": "revise",
                "code": "certainty_overreach",
                "message": "Mixed or partial evidence is paired with certainty language.",
            })

        if not causal_allowed and CAUSAL_TERMS.search(text):
            flags.append({
                "claim_id": claim.get("id"),
                "severity": "revise",
                "code": "causal_upgrade",
                "message": "Ledger does not support causal language for this claim.",
            })

        if confidence == "low" and CERTAINTY_TERMS.search(text):
            flags.append({
                "claim_id": claim.get("id"),
                "severity": "revise",
                "code": "confidence_mismatch",
                "message": "Low-confidence evidence is paired with high-certainty wording.",
            })

    if not claims and (CAUSAL_TERMS.search(text) or CERTAINTY_TERMS.search(text)):
        flags.append({
            "claim_id": None,
            "severity": "review",
            "code": "no_ledger_evidence",
            "message": "Strong factual language appears without any claim-ledger evidence.",
        })

    severity_order = {"block": 3, "revise": 2, "review": 1}
    max_severity = max((severity_order.get(f["severity"], 0) for f in flags), default=0)
    verdict = "ready" if max_severity == 0 else "blocked" if max_severity == 3 else "needs_revision"
    return {"verdict": verdict, "flags": flags, "claims_checked": len(claims)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("text_file")
    p.add_argument("ledger_file")
    args = p.parse_args()
    text = Path(args.text_file).read_text(encoding="utf-8")
    ledger = json.loads(Path(args.ledger_file).read_text(encoding="utf-8"))
    report = assess_text(text, ledger)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["verdict"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
