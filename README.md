# Credora

**Evidence-aware professional content intelligence for LinkedIn.**

Credora started from the useful workflow ideas in Jake Schincariol's MIT-licensed `linkedin-agent-skill`, then expands them into a more evidence-aware system with research posts, factual claim checks, content memory, confidence-aware analytics, and transparent local editorial tools.

## What Credora does

- learns and preserves the user's writing voice
- turns ideas and research into credible professional content
- verifies factual claims before they are presented as fact
- tracks content history to reduce repeated topics, hooks, stories, and angles
- adapts writing to the intended audience
- audits drafts for clarity, specificity, credibility, originality, and tone
- analyzes real post-performance data without pretending small samples are conclusive
- drafts comments, replies, DMs, carousels, profile rewrites, and content plans

## Core skills

- `post`
- `research-post`
- `fact-check`
- `voice`
- `humanize`
- `comment`
- `reply`
- `dm`
- `inbox`
- `profile`
- `carousel`
- `repurpose`
- `content-plan`
- `content-memory`
- `performance-review`
- `audit`
- `quality-audit`

## Local engines

Credora now includes dependency-free Python tools:

```bash
python3 scripts/clean_text.py draft.txt --report
python3 scripts/quality_score.py draft.txt
python3 scripts/quality_score.py before.txt after.txt
python3 scripts/select_hook.py research --limit 3
python3 -m unittest tests/test_engines.py
```

`clean_text.py` performs deterministic cleanup without rewriting factual meaning.

`quality_score.py` scores editorial signals such as specificity, rhythm, generic-language density, structural repetition, and readability. It is **not an AI detector** and does not claim that text is undetectable.

`select_hook.py` chooses editorial hook patterns by content intent. The hook library is deliberately treated as a writing aid, not as a reach-prediction model.

## Why Credora is different

**Evidence before confidence.** Research and factual claims should preserve what the source actually supports.

**No fabricated proof.** Never invent metrics, customers, outcomes, credentials, quotes, or citations.

**Voice over formula.** Templates are helpers, not a substitute for the user's real voice.

**Memory over repetition.** Past content should inform future content and help prevent repeated angles.

**Account data over generic growth rules.** Recommendations should prefer the user's own performance history when enough data exists.

**Human editorial quality, not detector gaming.** Credora optimizes for natural, specific, credible writing rather than claiming to bypass AI detectors.

**Confidence-aware analytics.** Small samples produce test suggestions, not universal rules.

## Repository layout

```text
.claude-plugin/       Claude plugin metadata
config/               hooks and editable editorial flags
profile/              voice, expertise and audience profiles
scripts/              runnable local Python engines
skills/               Credora skill workflows
tests/                engine tests
LICENSE                MIT license and retained upstream notice
NOTICE.md              upstream attribution
```

## Upstream attribution

Portions of the project are adapted from `linkedin-agent-skill` by Jake Schincariol, used under the MIT License. See `LICENSE` and `NOTICE.md`.

## Status

V1 foundation in active development. Content generation remains human-approved; Credora does not automatically publish to LinkedIn.
