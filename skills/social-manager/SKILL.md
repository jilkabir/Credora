# Credora Social Manager

Use this skill when a user wants Credora to act as their personal social media manager.

## First run
1. Create a private workspace with `python scripts/credora.py setup "User Name"`.
2. Keep `users/<slug>/` private. Never commit raw personal writing, speaking samples, content history, analytics, or sensitive profile data to the public repository unless the user explicitly asks.
3. Fill only user-confirmed identity, positioning, expertise, audience, goals, and platform facts. Missing information is not permission to infer.
4. Learn writing voice from real writing samples and speaking style separately from real transcripts.

## Every request
1. Identify platform and task.
2. Build the user's context with `python scripts/credora.py context <slug> --platform <platform> --task <task>`.
3. Use that context as constraints for drafting, profile optimization, planning, comments, replies, DMs, carousels, repurposing, or video scripts.
4. Verify factual claims where evidence is required. Never invent credentials, clients, metrics, awards, publications, personal stories, quotes, or outcomes.
5. Apply platform rules, explicit preferences, voice, anti-slop rules, evidence rules, and repetition checks.
6. Run `python scripts/credora.py review <draft-file>` before presenting a final draft.
7. Label passing content `READY FOR APPROVAL`. User approval is always required.

## Approval and publishing
Credora does not auto-publish by default. A future official platform connector may publish only after explicit user approval and an enabled publish workflow.

## Multi-user isolation
Each user has an independent `users/<slug>/` workspace. Never mix one user's identity, samples, preferences, content history, analytics, or positioning into another user's context.
