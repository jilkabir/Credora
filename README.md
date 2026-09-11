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

## Requirements

- Python 3.10, 3.11, or 3.12
- no third-party Python dependencies for the local engines

## Quick start

```bash
git clone https://github.com/jilkabir/Credora.git
cd Credora
python3 scripts/self_check.py
```

A passing self-check prints `"status": "PASS"`.

## Local engines

```bash
python3 scripts/clean_text.py draft.txt --report
python3 scripts/quality_score.py draft.txt
python3 scripts/quality_score.py before.txt after.txt
python3 scripts/select_hook.py research --limit 3
python3 scripts/pipeline.py draft.txt --intent research --hooks 3
python3 scripts/validate_memory.py memory/posts.example.jsonl
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

`clean_text.py` performs deterministic cleanup without rewriting factual meaning.

`quality_score.py` scores editorial signals such as specificity, rhythm, generic-language density, structural repetition, and readability. It is **not an AI detector** and does not claim that text is undetectable.

`select_hook.py` chooses editorial hook patterns by content intent. The hook library is deliberately treated as a writing aid, not as a reach-prediction model.

`pipeline.py` runs cleanup, editorial scoring, and intent-based hook selection in one local command. It does not fact-check claims; factual content still needs the `fact-check` workflow.

`validate_memory.py` checks the structure of Credora JSONL content-memory records. It does not verify whether stored claims are true.

## Verification

GitHub Actions runs the unit/integration tests, clean-checkout self-check, and CLI smoke checks on Python 3.10, 3.11, and 3.12.

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
.github/workflows/    CI verification
config/               hooks and editable editorial flags
memory/               example content-memory records
profile/              voice, expertise and audience profiles
scripts/              runnable local Python engines
skills/               Credora skill workflows
tests/                engine and integration tests
LICENSE                MIT license and retained upstream notice
NOTICE.md              upstream attribution
```

## Limitations

See `KNOWN_LIMITATIONS.md` before treating Credora output as verified evidence or platform guidance.

## Release status

See `ROADMAP.md`, `STATUS.md`, and `RELEASE_CHECKLIST.md` for the authoritative V1 completion state.

## Upstream attribution

Portions of the project are adapted from `linkedin-agent-skill` by Jake Schincariol, used under the MIT License. See `LICENSE` and `NOTICE.md`.
