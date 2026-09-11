# Credora Roadmap

## V1
V1 is complete and released as `v1.0.0`. Historical V1 completion remains unchanged.

### Product skills
- [x] Voice
- [x] Fact check
- [x] Post
- [x] Research post
- [x] Comment
- [x] Reply
- [x] Profile
- [x] Repurpose
- [x] Content plan
- [x] Content memory
- [x] Performance review
- [x] Quality audit
- [x] DM
- [x] Inbox triage
- [x] Audit

### Local engines
- [x] Deterministic text cleanup
- [x] Transparent editorial scoring
- [x] Intent-based hook selection
- [x] Content-memory validator
- [x] End-to-end draft pipeline runner
- [x] Clean-checkout self-check command

### V1 verification
GitHub Actions run `34590277784` passed across Python 3.10, 3.11, and 3.12.

GitHub release `Credora v1.0.0` was published on 2026-09-11 and points to commit `fd270b558435abaec6e6e68dc89f8ced7374db8f`.

## V1.1 Personalization

### Personal voice and style
- [x] Initialize Adrita writing voice
- [x] Add positive writing rules
- [x] Add hard anti-slop rules
- [x] Keep speaking style separate from writing style
- [x] Record public source metadata without raw article corpus
- [x] Add transparent writing-fingerprint learner
- [ ] Run learner on the full verified article corpus and persist only derived fingerprint data
- [ ] Learn speaking style from user-provided transcripts

### Personal brand brain
- [ ] Identity profile
- [ ] Positioning profile
- [ ] Profile goals
- [ ] LinkedIn rules/profile
- [ ] Facebook rules/profile
- [ ] Instagram rules/profile
- [ ] YouTube rules/profile

### Orchestration and approval
- [x] Master Credora orchestrator skill
- [x] Personal style guard
- [x] Approval gate
- [x] Explicit user approval remains required
- [ ] Persistent validated preference-feedback memory
- [ ] End-to-end profile optimization route through the orchestrator

### Reliability
- [x] Tests for voice learner
- [x] Tests for style guard and approval gate
- [x] Personalization CLI smoke checks in CI
- [x] Clean-checkout self-check covers personalization

Latest personalization verification: GitHub Actions run `34594454353` passed Python 3.10, 3.11, and 3.12, including unit/integration tests, self-check, and CLI examples.

## Current completion rule
**V1 is complete. V1.1 remains in progress until the unchecked personalization items are implemented and verified.**
