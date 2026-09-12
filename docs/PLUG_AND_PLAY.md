# Credora Plug-and-Play Setup

Credora can run as a private personal social media manager for multiple users without mixing their data.

## Fastest setup

Create your workspace:

```bash
python scripts/credora.py setup "Jane Doe"
```

Credora tells you the next command. Run the guided onboarding:

```bash
python scripts/credora.py onboard jane-doe
```

You only answer five plain-language questions:

1. Who are you professionally?
2. What do you want people to know you for?
3. What can you credibly teach or explain?
4. Who do you want to reach?
5. What should your social presence help you achieve?

Short answers are enough. Type `skip` if you want to complete something later.

## Teach Credora your real writing style

Put 3 or more real posts/articles in:

`users/jane-doe/writing-samples/`

Then run:

```bash
python scripts/credora.py learn jane-doe
```

Credora builds `brand-brain.json` and a writing-voice profile from observable features in those real samples. It uses positioning, audience, goals, expertise, vocabulary signals, sentence rhythm, paragraph density, person usage, punctuation and transition habits as soft writing constraints.

It does not infer missing credentials, sensitive traits, employers, metrics, clients, awards, publications, stories or outcomes.

More samples improve voice confidence. Rough guide: 3 samples / 1,000 words gives medium voice confidence; 8 samples / 4,000 words gives high voice confidence.

## Create the personal manager context

For LinkedIn:

```bash
python scripts/credora.py context jane-doe --platform linkedin --task post
```

For Facebook or Instagram, change the platform. For YouTube or spoken scripts:

```bash
python scripts/credora.py context jane-doe --platform youtube --task video-script
```

The context now includes the Personal Brand Brain. The LLM is instructed to start from the user's brand nerve rather than a generic viral-post template, choose one audience-relevant angle, preserve verified positioning and use the user's observable writing rhythm when confidence allows.

Writing voice and speaking style remain separate. Add speaking transcripts under `speaking-samples/` for future talking-style learning.

## Ask Claude or another LLM to write

Example:

> Write a LinkedIn post about my new research project. Use my Credora personal context. Keep the angle aligned with my positioning and audience, use my real writing rhythm, verify factual claims, avoid generic AI-style writing, and return the draft for approval.

The same workspace can support profile optimization, posts, comments, replies, DMs, carousels, content plans, repurposing and scripts.

## Review before approval

Save a draft and run:

```bash
python scripts/credora.py review draft.txt --user jane-doe
```

Credora checks the user's real voice samples, previous content history and claim ledger when available. A passing draft is labelled `READY FOR APPROVAL`. User approval is always required. Credora does not auto-publish by default.

## Check readiness

```bash
python scripts/credora.py status jane-doe
```

The report shows missing or uninitialized profile areas, whether the Brand Brain has been built, and how many writing samples are available.

## Simple mental model

```text
User answers 5 questions
        ↓
Private profile workspace
        ↓
Real writing samples
        ↓
Credora Personal Brand Brain
        ↓
Positioning + audience + proof + goals + voice
        ↓
Platform-specific context
        ↓
Claude or another LLM
        ↓
Evidence + anti-generic + repetition + voice + quality checks
        ↓
READY FOR APPROVAL
        ↓
User approval
```

Each user gets an isolated private workspace under `users/<slug>/`, which is ignored by Git by default.
