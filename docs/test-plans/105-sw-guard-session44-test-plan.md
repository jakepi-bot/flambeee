# Test Plan: Story 105 Service-Worker Guard in Currency Checker (Session 44)

**Story:** `docs/stories/105-sw-guard-session44.md` (P1b, release-gate mechanism).
**Owner:** Kai. **QA:** Scout. **PR:** #176, branch `feat/session44-105-sw-guard`.

## Scope
In scope: `scripts/verify-website-currency.sh` (Checks 6-8, lines 190-253)
plus any test fixture under `scripts/`. Out of scope: `website/`, `src/`,
`games/`, FPS probe, schedule, noon, `pending-post.txt`. Any diff outside
`scripts/` fails the plan.

## The three assertions (each prints measured values)

1. Heading == tag: mirror What's New heading names newest tag from
   `git ls-remote --tags origin` at run time. Both values print on failure.
2. CACHE changed since tag: `CACHE_VERSION` in `website/sw.js` differs from
   `git show <tag>:website/sw.js`. Both values print on failure.
3. Every app-card target precached: card hrefs read from mirror HTML at run
   time, each must appear in `PRECACHE_URLS`. Missing target named on failure.

## Checks

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Heading assertion installed, values print | Read Check 6 block | Fail line prints heading + tag |
| 2 | AC-2 | CACHE assertion installed, values print | Read Check 7 block | Fail line prints now + at-tag |
| 3 | AC-3 | Precache assertion installed, runtime targets | Read Check 8 block, confirm no hardcoded list | hrefs parsed from mirror, missing target named |
| 4 | AC-4 | RED run, exit non-zero, failing line pasted | Serve stale fixture, run guarded checker | Exit 1, at least one RED shape (CACHE 12==12; v0.36.0 heading + precache) |
| 5 | AC-5 | Green run on merged tree, exit 0 | Serve 103+105 merged tree, run checker | Exit 0, all three new lines PASS |
| 6 | AC-6 | Diff limited to `scripts/` | `git diff --stat` vs base | 1 file, 64+/0- |
| 7 | AC-7 | Copy tone | grep for em dash | 0 em dashes |
| 8 | Neg | Checker against stale fixture (v0.36.0 tree) | Guarded script on v0.36.0 serve | Exit 1, heading + precache FAIL lines name the drift |
| 9 | Neg | Checker on pre-103 tree (CACHE 12 == tag 12) | Guarded script on pre-103 serve | Exit 1, CACHE FAIL line with both values |

## Result (Scout independent re-run, 2026-10-28)
GREEN (merged 103+105): exit 0, all three Story 105 checks PASS
(heading v0.36.1, CACHE 13 vs 12, 4/4 precached).
RED-A (pre-103, CACHE 12==12): exit 1, CACHE FAIL line as specified.
RED-B (v0.36.0 fixture): exit 1, heading + precache FAIL lines as specified.
Full output in `flambeee-team/qa-results.md`.
