# Credora Plug-and-Play Setup

Credora can run as a private personal social media manager for multiple users without mixing their data.

## 1. Create a private user workspace

```bash
python scripts/credora.py setup "Jane Doe"
```

This creates `users/jane-doe/`. The entire `users/` directory is ignored by Git so raw personal data stays local by default.

## 2. Add only confirmed profile information

Edit the user's identity, positioning, expertise, audience, goals, writing rules and platform files. Add real writing samples under `writing-samples/` and speaking transcripts under `speaking-samples/`.

Do not invent missing credentials, employers, metrics, clients, awards, publications, stories or outcomes.

## 3. Build the platform-specific manager context

```bash
python scripts/credora.py context jane-doe --platform linkedin --task post
```

For YouTube or spoken scripts:

```bash
python scripts/credora.py context jane-doe --platform youtube --task video-script
```

Credora keeps writing voice and speaking style separate.

## 4. Ask Claude to do the work

Give Claude the generated context and a request such as:

> Write a LinkedIn post about my new research project. Use my Credora profile, verify factual claims, avoid AI-slop, and return the result for approval.

The same workspace can be used for profile optimization, posts, comments, replies, DMs, carousels, content plans, repurposing and scripts.

## 5. Review before approval

Save a draft and run:

```bash
python scripts/credora.py review draft.txt
```

A passing draft is labelled `READY FOR APPROVAL`. User approval is always required. Credora does not auto-publish by default.

## 6. Check workspace readiness

```bash
python scripts/credora.py status jane-doe
```

`ready: true` means the required workspace files exist. `uninitialized_files` shows which areas still need real user information or samples.

## Architecture

```text
User account / profile
        ↓
Private Credora workspace
        ↓
Identity + positioning + audience + goals
        ↓
Writing voice / speaking style
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
