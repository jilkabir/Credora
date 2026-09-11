# Credora Personal Agent Quickstart

Credora is now usable as a personal social-writing layer for Claude-style workflows.

## 1. Build your platform context

```bash
python scripts/context_bundle.py --platform linkedin --task post > /tmp/credora-context.md
```

Supported platform values: `linkedin`, `facebook`, `instagram`, `youtube`.

## 2. Give the request to Claude

Ask Claude to use the Credora personal-agent/orchestrator skill and the generated context. Example:

> Write a LinkedIn post about AI coding assistants using my Credora profile. Keep it evidence-aware and return it for approval, not publishing.

The agent should load identity, positioning, expertise, audience, voice, writing rules, forbidden-style rules and the destination-platform rules before drafting.

## 3. Review a local draft

Save a draft to a UTF-8 text file, then run:

```bash
python scripts/review_draft.py /tmp/draft.txt
```

Optional evidence, voice and history inputs:

```bash
python scripts/review_draft.py /tmp/draft.txt \
  --ledger examples/claim_ledger.example.json \
  --voice-sample /path/to/your-sample.txt \
  --history /path/to/previous-post.txt
```

The top-level status is either `READY FOR APPROVAL` or `NEEDS REVISION`. It never means published.

## 4. Personal profile data

The public repository contains conservative profile templates and derived style rules. Do not put private or sensitive identity data into a public repository. For real personal facts, proof points and private writing samples, keep a private user pack and let Claude load it alongside Credora.

## 5. Approval rule

Credora does not auto-publish. The user remains the final approver.
