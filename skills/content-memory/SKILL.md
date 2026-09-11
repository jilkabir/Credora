---
name: content-memory
description: >-
  Track what the user has already published so Credora can avoid repeating the
  same topic, story, claim, metaphor, hook, proof point, or CTA.
---

# Credora content-memory

Content memory is editorial memory, not surveillance.

## Store per published post

When the user approves logging a post, append a structured record containing:
- date
- title or first line
- theme
- central claim
- hook type
- examples/stories used
- proof points
- CTA
- target audience
- source links or evidence identifiers when relevant

Recommended file: `memory/posts.jsonl`.

## Before drafting

Compare the proposed post against recent records. Flag:
- same core claim
- same story
- same analogy
- same number/proof point
- same hook shape
- same CTA
- same conclusion with superficial wording changes

## Output

Return:
- NEW: materially fresh
- RELATED: same theme, new angle
- REPETITIVE: too close to recent content

Never block a deliberate series; explain the overlap and let the user decide.
