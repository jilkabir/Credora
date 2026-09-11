# Credora V1 Release Checklist

Do not create `v1.0.0` until every required item is checked and test evidence exists.

## Code and behavior
- [x] Core writing and research skills present
- [x] Local cleanup engine present
- [x] Editorial scoring engine present
- [x] Hook selection engine present
- [x] Content-memory validator present
- [x] End-to-end pipeline present
- [x] Self-check command present
- [x] CI workflow present

## Verification
- [x] Unit tests pass on Python 3.10
- [x] Unit tests pass on Python 3.11
- [x] Unit tests pass on Python 3.12
- [x] Clean-install self-check passes
- [x] Example commands verified from a fresh checkout
- [x] No known failing V1 blocker remains

Verification evidence: GitHub Actions run `34590277784` passed the test suite, self-check, and CLI smoke commands on Python 3.10, 3.11, and 3.12.

## Product integrity
- [x] MIT license included
- [x] Upstream attribution retained
- [x] Known limitations documented
- [x] No AI-detector-bypass claim
- [x] No fabricated platform-performance guarantees
- [x] No auto-posting in V1

## Release
- [x] README installation instructions rechecked
- [x] ROADMAP has no unresolved V1 code/test blockers
- [x] STATUS says release candidate
- [ ] Create tag/release `v1.0.0`

## Release decision
All V1 code, test, documentation, and release-candidate checks are complete. The only remaining action is creating the GitHub tag/release `v1.0.0`.
