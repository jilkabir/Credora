---
name: credora-personal-agent
description: Use Credora as a ready-to-use personalized social writing agent with profile, platform, evidence, style, and approval checks.
---

# Credora Personal Agent

Use this skill when the user asks for a social post, comment, reply, carousel, DM, profile rewrite, or video script in their own style.

## Fast path
1. Identify the platform and content type.
2. Load the Credora context bundle for that platform.
3. Draft in the user's stored voice and positioning.
4. Do not invent missing identity facts, achievements, metrics, stories, clients, publications, or results.
5. Run the local review path.
6. Return the content plus one status only: `READY FOR APPROVAL` or `NEEDS REVISION`.
7. Never publish automatically.

## Platform routing
- LinkedIn: professional, useful, evidence-aware, no engagement bait.
- Facebook: warmer and contextual, still factual.
- Instagram: concise and visually contextual, no emoji clutter.
- YouTube: use talking-style rules; do not pretend article voice equals speaking voice.

## Personal feedback
If the user explicitly says a rule should persist, record it in the private preference store using the validated preference shape. A one-off edit is not automatically a permanent rule.

## Example requests
- "Write a LinkedIn post in my style about this paper."
- "Rewrite my About section using my positioning."
- "Turn this into an Instagram caption that still sounds like me."
- "Write a YouTube script in my speaking style."

The final draft always requires user approval.
