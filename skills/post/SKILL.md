---
name: credora-post
description: Turn a grounded idea into a professional post using the user's voice, audience context, evidence, and content history.
---

# Credora Post

Use this skill when the user asks for a professional social post, especially for LinkedIn.

## Required context

Read when available:
- `profile/voice.md`
- `profile/expertise.md`
- `profile/audience.md`
- recent entries in content memory
- evidence or claim ledger for factual material

## Workflow

1. Identify the single main idea.
2. Separate user-provided facts, sourced facts, opinions, and assumptions.
3. If material factual claims are present, run the fact-check workflow before drafting.
4. Check recent content history for repeated topic, story, hook, analogy, or conclusion.
5. Generate 2-3 genuinely different opening directions.
6. Choose the strongest direction for the intended audience.
7. Draft in the user's documented voice.
8. Run quality audit.
9. Return the final draft plus concise notes on any unresolved claim or placeholder.

## Writing rules

- One main idea per post.
- Specific examples beat generic claims.
- Never invent metrics, clients, outcomes, credentials, quotations, or personal experiences.
- Do not force a formula when the idea does not fit one.
- Do not use generic engagement bait.
- Avoid exaggerated certainty.
- Keep a natural reading rhythm rather than optimizing for an arbitrary character count.
- Hashtags, emojis, links, and CTAs should follow user preference and context, not hard-coded growth folklore.

## Opening directions

Openings can use approaches such as:
- concrete observation
- result or change
- tension or contradiction
- short scene
- precise question
- useful claim
- personal lesson

Do not label these as "proven" unless evidence exists.

## Final response format

```text
OPENING OPTIONS
1. ...
2. ...
3. ...

RECOMMENDED
Why: ...

FINAL POST
...

EVIDENCE NOTES
- only when needed

MEMORY TAGS
- topic:
- angle:
- audience:
- format:
```

Do not publish automatically. The skill prepares content; publishing requires a separate explicit action and supported integration.