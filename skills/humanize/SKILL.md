---
name: humanize
description: >-
  Improve naturalness, readability, specificity, and voice consistency without
  claiming to bypass AI detectors. Uses local Python tools for deterministic
  cleanup and editorial scoring.
---

# Credora humanize

Credora does not promise that text is "undetectable" or that any AI detector
will classify it a certain way. The goal is better writing: cleaner text,
stronger specificity, more natural rhythm, fewer generic phrases, and closer
alignment with the user's actual voice.

## Local tools

```bash
python3 scripts/clean_text.py draft.txt --report
python3 scripts/quality_score.py draft.txt
python3 scripts/quality_score.py before.txt after.txt
```

Both tools are dependency-free and run locally.

## What clean_text.py changes

- removes zero-width and other invisible formatting characters
- normalizes typographic punctuation where useful
- collapses accidental whitespace
- replaces configurable stock phrases only when a safe replacement exists
- preserves URLs and does not rewrite factual content

## What it never does automatically

It does not rewrite claims, numbers, quotations, citations, or technical terms.
It does not change sentence meaning to chase a score.

## quality_score.py checks

- rhythm: sentence-length variation without rewarding chaos
- specificity: concrete markers such as names, numbers, dates, examples
- generic-language density: configurable stock phrases per 100 words
- structural repetition: repeated sentence starts, repetitive bullets, canned
  rhetorical patterns
- readability: overly long sentences and paragraph density
- voice fit: optional comparison against `profile/voice.md`

The score is an editorial signal, not a detector result.

## Workflow

1. Run deterministic cleanup.
2. Review the change report.
3. Run quality scoring.
4. Rewrite only the flagged areas that genuinely improve clarity or voice.
5. If a rewrite changes a factual claim, run `fact-check` again.

## Output

Return the cleaned draft, a compact scorecard, and the top three editorial
fixes. Never label the result "human-written", "undetectable", or "detector-safe".
