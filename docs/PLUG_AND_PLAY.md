# Credora Plug-and-Play Setup

Credora can run as a private personal social media manager for multiple users without mixing their data.

## Fastest setup for non-technical users

Run one command:

```bash
python scripts/credora.py start "Jane Doe"
```

Credora creates the private workspace and immediately asks the short onboarding questions. No manual profile-file editing is required for the basic setup.

If you already have answers in a JSON file, use:

```bash
python scripts/credora.py start "Jane Doe" --answers answers.json
```

## Improve the writing intelligence

Put at least 3 real writing samples (`.txt` or `.md`) into:

```text
users/jane-doe/writing-samples/
```

Then run:

```bash
python scripts/credora.py learn jane-doe
```

Credora builds the personal Brand Brain and learns observable writing rhythm from the samples. It does not invent personality, credentials, stories, metrics, clients or outcomes.

## Check whether everything is ready

```bash
python scripts/credora.py doctor jane-doe
```

`doctor` checks missing profile data, writing-sample readiness, saved Brand Brain, malformed preferences, malformed claim ledgers and other setup problems. It returns one `next_action` so the user knows exactly what to do next.

`ready: true` means the workspace has enough profile information, at least 3 writing samples and a saved Brand Brain. `healthy: true` only means no broken/corrupted setup was detected, so always look at `ready` too.

## Build content context

```bash
python scripts/credora.py context jane-doe --platform linkedin --task post
```

For YouTube or spoken scripts:

```bash
python scripts/credora.py context jane-doe --platform youtube --task video-script
```

Credora keeps writing voice and speaking style separate.

## Ask Claude or another LLM to do the work

Give the generated context to the LLM and request the content you need, for example:

> Write a LinkedIn post about my new research project. Use my Credora profile, stay inside my verified positioning, verify factual claims, avoid AI-slop, and return the result for approval.

The same workspace can support profile optimization, posts, comments, replies, DMs, carousels, content plans, repurposing and scripts.

## Review before approval

Save a draft and run:

```bash
python scripts/credora.py review draft.txt --user jane-doe
```

A passing draft is labelled `READY FOR APPROVAL`. User approval is always required. Credora does not auto-publish by default.

## Existing-user commands

If you prefer the step-by-step flow instead of `start`:

```bash
python scripts/credora.py setup "Jane Doe"
python scripts/credora.py onboard jane-doe
python scripts/credora.py learn jane-doe
python scripts/credora.py doctor jane-doe
```

## Architecture

```text
User
  ↓
Private Credora workspace
  ↓
Guided onboarding
  ↓
Identity + positioning + expertise + audience + goals
  ↓
Real writing samples → writing voice
  ↓
Personal Brand Brain
  ↓
Platform-specific rules
  ↓
Claude or another LLM
  ↓
Evidence + style + repetition + quality checks
  ↓
READY FOR APPROVAL
  ↓
User approval
  ↓
Optional official publishing connector later
```

Each user gets an isolated workspace. Never load one user's private data into another user's context.
