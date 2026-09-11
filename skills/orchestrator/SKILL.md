---
name: credora-orchestrator
description: Route social-content requests through Credora's personal brand, voice, evidence, memory, and approval layers.
---

# Credora Orchestrator

Use this skill as the default coordinator for profile optimization and social-content work.

## Always load first
Before drafting, read the relevant personal context:
- `profile/voice.md`
- `profile/writing-rules.md`
- `profile/forbidden-style.md`
- `profile/audience.md`
- `profile/expertise.md`

For spoken/video output also read:
- `profile/talking-style.md`

When identity, positioning, platform, content-history, or performance profiles exist, load the relevant files before drafting.

## Route by request
- LinkedIn post -> `skills/post/SKILL.md`
- research/evidence post -> `skills/research-post/SKILL.md` plus fact-check
- comment -> `skills/comment/SKILL.md`
- reply -> `skills/reply/SKILL.md`
- profile optimization -> `skills/profile/SKILL.md`
- content plan -> `skills/content-plan/SKILL.md`
- carousel -> `skills/carousel/SKILL.md`
- DM -> `skills/dm/SKILL.md`
- repurpose -> `skills/repurpose/SKILL.md`
- content audit -> `skills/audit/SKILL.md` or quality-audit as appropriate
- performance learning -> `skills/performance-review/SKILL.md`

## Personalization order
1. Respect explicit user instructions for the current request.
2. Apply the user's stored identity/positioning boundaries when available.
3. Apply the personal writing or talking voice.
4. Apply platform-specific constraints when available.
5. Apply anti-slop hard rules.
6. Check factual/evidence risk.
7. Check repetition against content memory when relevant.
8. Run voice fit and quality checks.
9. Return a draft for user approval.

## Approval rule
Do not treat generated social content as approved merely because local checks pass. Local checks may produce `READY FOR APPROVAL`; only explicit user approval can move a draft to an approved/final state.

## Revision behavior
If the user says a phrase, structure, or tone does not sound like them, treat that as personalization feedback. Update the relevant profile/preference file when the user asks for a persistent rule; otherwise apply the correction to the current draft only.

## Safety and truthfulness
- Do not fabricate personal experience or proof points.
- Do not convert association into causation.
- Do not claim a style score proves authorship or human authorship.
- Do not promise reach, virality, engagement, or ranking.
- Do not auto-publish unless a future publishing connector is explicitly configured and the user has approved that action.
