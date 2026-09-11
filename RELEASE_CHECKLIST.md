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
- [ ] Unit tests pass on Python 3.10
- [ ] Unit tests pass on Python 3.11
- [ ] Unit tests pass on Python 3.12
- [ ] Clean-install self-check passes
- [ ] Example commands verified from a fresh checkout
- [ ] No known failing V1 blocker remains

## Product integrity
- [x] MIT license included
- [x] Upstream attribution retained
- [x] Known limitations documented
- [x] No AI-detector-bypass claim
- [x] No fabricated platform-performance guarantees
- [x] No auto-posting in V1

## Release
- [ ] README installation instructions rechecked
- [ ] ROADMAP has no unresolved V1 blockers
- [ ] STATUS says release candidate or complete
- [ ] Create tag/release `v1.0.0`

## Release decision
If any Verification or Release item remains unchecked, Credora V1 is still **BUILD IN PROGRESS**.
