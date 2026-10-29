# Test Plan: Story 107 Check 7 Predecessor-Tag Fix (Session 45)

**Story:** `docs/stories/107-check7-predecessor-session45.md` (P1b, required first leg).
**Owner:** Kai. **QA:** Scout. **PR:** #180, branch `feat/session45-check7-predecessor`.

## Scope
In scope: `scripts/verify-website-currency.sh` (tag-resolution block plus Check 7)
plus any fixture/harness under `scripts/`, plus the two stale-doc updates
(`docs/test-plans/041`, `docs/test-plans/046`). Out of scope: `website/`,
`src/`, `games/`, FPS probe, schedule, noon, `pending-post.txt`. Any diff
outside `scripts/` plus the two named docs fails the plan.

## The three assertions (each prints measured values)

1. Predecessor resolved at run time: newest plus second-newest origin tag from
   `git ls-remote --tags origin`, same `vX.Y.Z` filter, same `sort -V` ordering.
   Both values print.
2. Check 7 CACHE changed since predecessor: `CACHE_VERSION` in `website/sw.js`
   differs from `git show <predecessor>:website/sw.js`. Both values plus the
   predecessor tag print on failure. Check 6 still targets the newest tag.
3. Checks 6 and 8 re-run green in the same pass (shared tag-resolution block).

## Checks

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Predecessor + newest resolved at run time, both printed | Read tag block, run checker | `origin latest tag:` + `origin predecessor tag:` lines, nothing hardcoded |
| 2 | AC-2 | Check 7 vs predecessor, Check 6 vs newest | Read Check 7/6 blocks | `git show ${...pred...}:website/sw.js`, fail line names predecessor tag |
| 3 | AC-3 | GREEN tag-cut run, exit 0, Check 7 passing line | Scratch clone, bump CACHE, tag, run checker | Exit 0, `PASS: Story 107 CACHE check` against predecessor |
| 4 | AC-4 | RED no-bump run, non-zero exit, Check 7 failing line | Scratch tag with CACHE unchanged, run checker | Exit 1, `FAIL: Story 107 CACHE check` with both values |
| 5 | AC-5 | Checks 6 and 8 green in the same pass | Same runs | `PASS: Story 105 heading check` + `PASS: Story 105 precache check` lines |
| 6 | AC-6 | 041 + 046 byte-identity retired in same PR | `git diff` on the two docs | No `byte-identical to v0.19.0` claim left, current rule stated |
| 7 | AC-7 | Diff limited to `scripts/` + the two docs | `git diff --stat` vs base | 3 files, no `website/`, `src/`, `games/` |
| 8 | AC-8 | Copy tone | grep for em dash | 0 em dashes |
| 9 | Neg | Old self-compare shape would FAIL post-tag | Old Check 7 logic on clean tree (13 vs 13) | Exit 1 by construction, fix required |
| 10 | Edge | Boundary: single-tag origin (no predecessor exists) | Read fallback path in tag block | Checker handles gracefully, named behavior, no crash |

## Result (Scout independent re-run, 2026-10-29)
Checker run by Scout on the PR tree plus scratch-clone falsifying runs.
Pass/fail counts and full output in `flambeee-team/qa-results.md`.
