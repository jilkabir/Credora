# Credora V1 Release Checklist

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
- [x] ROADMAP has no unresolved V1 blockers
- [x] STATUS says V1 complete
- [x] Tag/release `v1.0.0` published

Release evidence: `Credora v1.0.0` was published on 2026-09-11, targeting commit `fd270b558435abaec6e6e68dc89f8ced7374db8f`.

## Release decision
**Credora V1 is complete. No core V1 tasks remain.**
