---
name: credora-quality-audit
description: Audit a professional-content draft for clarity, credibility, specificity, originality, voice consistency, and unsupported claims.
---

# Credora Quality Audit

Use this skill before a draft is treated as final.

## Purpose

This is an editorial quality check, not an AI-detector bypass tool.

## Scorecard

Score each category from 0-5 and explain any score below 4:

- clarity
- specificity
- credibility
- evidence discipline
- voice consistency
- audience fit
- originality of angle
- structural flow
- usefulness
- close/CTA fit

## Hard-fail checks

A draft cannot pass if it contains any of these:
- fabricated metric, quote, client, credential, outcome, or citation
- material factual claim presented confidently without adequate support
- source that does not actually support the claim
- contradiction with the user's supplied facts
- obvious reuse of a recent story or angle without a deliberate reason

## Editorial checks

Flag:
- vague abstractions where a concrete example is available
- generic openings that could fit almost any post
- repetitive sentence patterns
- unnecessary hype
- fake certainty
- cliches and stock phrasing
- an ending that introduces a second idea
- CTA that does not follow naturally from the post
- over-formatting

Do not automatically remove punctuation or vocabulary merely because it is sometimes associated with AI writing. Preserve natural language and the user's documented style.

## Verdict

Return one of:
- READY
- READY WITH MINOR EDITS
- REVISE
- BLOCKED BY EVIDENCE

For `BLOCKED BY EVIDENCE`, identify the exact claim that must be sourced, narrowed, or removed.