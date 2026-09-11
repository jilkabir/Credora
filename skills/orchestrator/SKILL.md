---
name: credora-orchestrator
description: Route social-content requests through Credora's personal brand, voice, evidence, memory, platform, and approval layers.
---

# Credora Orchestrator

Use this skill as the default coordinator for profile optimization and social-content work.

## Always load first
Before drafting, read:
- `profile/identity.md`
- `profile/positioning.md`
- `profile/voice.md`
- `profile/writing-rules.md`
- `profile/forbidden-style.md`
- `profile/audience.md`
- `profile/expertise.md`

Then load the requested platform file from `profile/platforms/` when one exists. For spoken/video output also read `profile/talking-style.md`. Load active explicit feedback from the user's preference memory when available; `memory/preferences.example.jsonl` documents the public format and is not itself a private user-memory store.

## Route by request
- LinkedIn post -> `skills/post/SKILL.md` + `profile/platforms/linkedin.md`
- research/evidence post -> `skills/research-post/SKILL.md` + fact-check + relevant platform rules
- comment -> `skills/comment/SKILL.md` + relevant platform rules
- reply -> `skills/reply/SKILL.md` + relevant platform rules
- profile optimization -> `skills/profile/SKILL.md` + identity + positioning + platform rules
- content plan -> `skills/content-plan/SKILL.md`
- carousel -> `skills/carousel/SKILL.md` + relevant platform rules
- DM -> `skills/dm/SKILL.md` + relevant platform rules
- repurpose -> `skills/repurpose/SKILL.md` + destination platform rules
- content audit -> `skills/audit/SKILL.md` or quality-audit as appropriate
- performance learning -> `skills/performance-review/SKILL.md`
- YouTube/video script -> talking style + `profile/platforms/youtube.md`

## Personalization order
1. Respect explicit user instructions for the current request.
2. Enforce identity truth boundaries.
3. Enforce approved positioning and avoid unsupported positioning.
4. Apply the personal writing or talking voice.
5. Apply destination-platform rules.
6. Apply active explicit preference feedback.
7. Apply anti-slop hard rules.
8. Check factual/evidence risk.
9. Check repetition against content memory when relevant.
10. Run voice fit and quality checks.
11. Return a draft for user approval.

## Missing information
Do not fill missing identity, positioning, proof, experience, or platform facts from inference. Ask only when the missing fact materially affects the requested output; otherwise write without it.

## Approval rule
Do not treat generated social content as approved merely because local checks pass. Local checks may produce `READY FOR APPROVAL`; only explicit user approval can move a draft to an approved/final state.

## Feedback learning
When the user explicitly makes a persistent preference (for example, never use a phrase again), record it in the private/user preference store using the validated JSONL shape: date, scope, rule, kind, source, active. Do not silently infer permanent preferences from one edit. Public example files are documentation, not the user's private memory.

## Safety and truthfulness
- Do not fabricate personal experience or proof points.
- Do not convert association into causation.
- Do not claim a style score proves authorship or human authorship.
- Do not promise reach, virality, engagement, or ranking.
- Do not auto-publish unless a future publishing connector is explicitly configured and the user has approved that action.
