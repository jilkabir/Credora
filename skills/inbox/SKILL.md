---
name: inbox
description: >-
  Triage LinkedIn inbox messages by intent and suggest concise, context-aware
  responses without pretending to know facts outside the message thread.
---

# Credora inbox

## Triage categories

- LEAD: a genuine problem, buying signal, or request related to the user's work
- RECRUITER: role, hiring, contract, or interview outreach
- PEER: professional conversation, collaboration, or networking
- ASK: request for advice, introduction, feedback, or help
- SUPPORT: thanks, reaction, or relationship maintenance
- SPAM: mass pitch, irrelevant sequence, suspicious link, or manipulative outreach
- UNCLEAR: insufficient context to classify confidently

## Process

For each message:
1. classify the intent
2. cite the clue from the message that drove the classification
3. assign urgency: now / today / later / ignore
4. draft a response only when a response is useful
5. surface any missing context rather than inventing it

## Rules

- Do not infer budgets, authority, hiring power, or buying intent without evidence.
- Do not manufacture familiarity or previous conversations.
- Do not open links or scrape profiles unless the user explicitly supplies or
  authorizes the relevant context through available tools.
- If a message asks a factual question, verify the answer when needed.
- Keep responses proportional to the incoming message.
- Nothing is sent automatically.

## Output

Return a compact table-like block per message:

CATEGORY · URGENCY · WHY
Suggested action
Copy-ready reply, or SKIP

For batches, sort by urgency first, then category.
