---
name: credora-voice
description: Build and maintain a grounded writing-voice profile from the user's own writing samples.
---

# Credora Voice

Use this skill when the user wants Credora to learn, refresh, or apply their writing voice.

## Goal

Create a reusable voice profile from evidence in the user's own writing. Do not invent personality traits, vocabulary preferences, or stylistic habits that are not supported by examples.

## Inputs

Prefer, in order:
1. 5-20 past posts written by the user.
2. Long-form writing written by the user.
3. Direct preferences supplied by the user.

If fewer than 3 meaningful samples are available, create a provisional profile and label confidence as low.

## What to extract

Capture:
- sentence length and rhythm
- paragraph length
- first-person vs third-person tendency
- formality
- vocabulary level
- common transitions
- use of questions
- use of numbers and examples
- preferred openings and endings
- words or patterns the user avoids
- emoji, punctuation, hashtag, and CTA preferences

## Guardrails

- Do not imitate errors accidentally unless the user explicitly wants them preserved.
- Do not infer demographic or sensitive personal traits from writing style.
- Do not claim the profile is complete when evidence is limited.
- Distinguish explicit user preferences from patterns inferred from samples.

## Output

Write or update `profile/voice.md` with:

```md
# Voice Profile

## Confidence
high | medium | low

## Explicit preferences
...

## Observed patterns
...

## Avoid
...

## Examples that best represent the voice
...

## Last updated
YYYY-MM-DD
```

When drafting content, use the voice profile as guidance, not as a rigid template.