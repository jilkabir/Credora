---
name: credora-fact-check
description: Verify factual claims before they are presented as fact and preserve what the evidence actually supports.
---

# Credora Fact Check

Use this skill whenever a draft includes factual claims, statistics, study findings, rankings, dates, platform-behavior claims, or claims about named people, companies, products, or events.

## Core rule

Evidence before confidence.

A claim may be:
- verified
- partially supported
- disputed or mixed
- outdated
- unsupported
- unverifiable with available evidence

Never silently upgrade correlation to causation, a preliminary result to settled fact, or a single source to broad consensus.

## Claim ledger

For every material factual claim, create an internal ledger with:

```text
claim:
status:
source:
source_date:
evidence_strength:
what_the_source_actually_supports:
caveat:
```

## Source preference

Prefer the most direct and authoritative source available:
1. original paper, official dataset, official documentation, regulator, or company primary source
2. systematic review, meta-analysis, or reputable institutional synthesis
3. high-quality secondary reporting
4. community discussion only for sentiment or lived-experience questions

## Research claims

When using academic evidence, check at minimum:
- study type
- population/sample
- measured outcome
- whether result is correlational or causal
- uncertainty or limitations
- whether the claim generalizes beyond the studied population

## Output behavior

If verified, write the claim at the level the source supports.
If evidence is mixed, say it is mixed.
If the source is weak, narrow the wording.
If the claim cannot be verified, do not present it as fact. Ask for a source, remove it, or explicitly label it as an opinion/assumption.

## Prohibited behavior

- invented citations
- fabricated statistics
- fake quotes
- fake study titles
- citing a source that does not support the written claim
- using a citation merely because it discusses the same topic

The final draft should remain readable. Do not overload a post with citations unless the user asks for an academic style; preserve a source record separately when appropriate.