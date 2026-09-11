---
name: audit
description: >-
  Analyze past LinkedIn content using the user's own performance data, with
  transparent metrics, sample-size warnings, and testable recommendations.
---

# Credora audit

The user's own account history is the primary evidence. Generic LinkedIn advice
is only a prior and should never override clear account-level data.

## Inputs

Use whichever the user has:
- exported analytics
- screenshots
- manually supplied metrics
- memory/posts.jsonl
- memory/performance.jsonl

## Compute only what the data supports

Possible metrics:
- engagement rate = (reactions + comments + reposts) / impressions
- comment-to-reaction ratio
- reach multiple = impressions / follower count at time of post
- save/send rate when available
- lead/conversation rate when tracked

Always show the formula used and do not compare metrics with missing or
incompatible denominators.

## Pattern analysis

Compare stronger and weaker posts across:
- topic
- claim type
- hook shape
- format
- length
- use of real proof
- story vs explanation vs opinion
- CTA
- posting time only after more substantive factors

## Confidence discipline

Every conclusion must include:
- n = sample size
- observed difference
- likely confounders
- confidence: low / medium / high

With a small sample, recommend a test rather than declaring a rule.

## Output

1. data coverage and missing fields
2. top and bottom posts by appropriate normalized metric
3. strongest patterns with confidence
4. weak or unsupported assumptions
5. what to stop, continue, and test next
6. updates to feed into `content-plan`

Never invent causes from correlation alone.
