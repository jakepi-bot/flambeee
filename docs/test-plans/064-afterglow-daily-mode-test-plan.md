# Test Plan — Story 064: Afterglow daily UTC-seeded mode (Session 30, P1)

**Source:** `docs/stories/064-afterglow-daily-mode.md` (Quinn, Wave 2).
**Targets:** PR #122 (Kai proof harness `dev/afterglow-daily-proof.py`),
PR #123 (Riven game change `src/afterglow.html`, branch `riven/064-afterglow-daily`).
**QA tools (Session 30, kept out of the repo):**
`dev/afterglow-daily-proof.py` (PR #122), `dev/afterglow-proof.py` (Story 059
regression), scratch `browser-check.mjs` (real Chromium via playwright-core),
scratch `midnight-check.mjs` (mocked-clock AC-2), scratch `neg-check.mjs`
(pure-function negative inputs).

## 1. BDD scenario coverage

| # | Scenario (story) | Test | Method | Pass bar |
|---|---|---|---|---|
| 1 | Same UTC day, same sequence | T1 run-1/run-2 daily proof | Kai harness: run 1 pre-064 must exit 1 (absence), run 2 on PR #123 tip must exit 0 via PRODUCT `dailySeedForDay`, day indices + level signatures quoted | exit 1 then exit 0, DAY_A=20737 DAY_B=20738, level-0 sigs 955b63a7 vs 5cc0d664 |
| 2 | UTC midnight advances; free play unaffected | T2 mocked-clock midnight | Freeze `Date.now` to day A twice and day B once; daily seeds equal/equal/advance; free-play seed keeps `afterglow-<ts>` path | 4/4 checks pass |
| 3 | Different days differ | T1 run 2 + T3 negative sweep | Harness different-day check; `dailySeedForDay` over boundary inputs | exit 0; 11/11 negative cases return exact expected strings, never throw |
| 4 | Fresh browser empty state | T4 browser, both viewports | Fresh context load: `#stats-block.hidden`, no zeros, no crash | PASS desktop + mobile |
| 5 | Hostile storage | T4 browser hostile profile | `Storage.prototype` throws; start run, play a dark-phase move | No crash, zero console/page errors |
| 6 | Free play untouched | T5 regression + T6 purity diff | Story 059 harness exit 0 on candidate; pure-block diff vs `origin/main` is additive-only | `RESULT: all invariants hold`; diff = `dailySeedForDay` only |
| 7 | Phase gating in daily mode | T4 browser, both viewports | Lit input ignored (pos+budget kept); dark input applied; dark expiry reveals `Time up` with pos+budget kept; no console errors | All PASS desktop 1280x800 + mobile 375x667 |

## 2. Edge and boundary cases

- E1 `dailySeedForDay(0)` -> `'afterglow-daily:0'` (epoch day).
- E2 Negative index `-1` wraps via `>>> 0` (documented, no throw).
- E3 Fractional `3.7` truncates; numeric strings coerce; non-numeric/`null`/`undefined` -> day 0; `2**32` wraps to 0; `MAX_SAFE_INTEGER` wraps deterministically.
- E4 `dayIndex` recomputed at every `startRun`, not cached at page load (post-midnight reload advances even in a long-lived tab after re-clicking Start).
- E5 Mode switch mid-run stops the running run first (`setMode` calls `restartRun()` before flipping `state.mode`). NOTE (non-blocking, QA does not fix): the stop-then-flip order restarts in the OLD mode before flipping the label; reported on PR #123, not a release blocker since the seed contract and stats routing hold.
- E6 Stats isolation: daily writes go to `flambeee-afterglow-daily-stats`; after daily play the free key `flambeee-afterglow-stats` is absent from storage.
- E7 `AFTERGLOW-PURE` block stays pure: no DOM/storage/timer references (harness purity guard, comments stripped before scanning).
- E8 Private-mode safety: throwing store plays clean (Scenario 5, hostile profile).
- E9 No site surface for daily mode (in-game entry is the story default): PR #123 touches no `website/` or `scripts/` path.

## 3. Results (Session 30 QA re-run, real output)

- T1 run 1 (pre-064 `origin/main`): exit 1, `ABSENT`/`ABSENT`, purity PASS.
- T1 run 2 (PR #123 tip `c55b7de`): exit 0, `seed source: PRODUCT dailySeedForDay`.
- T5 Story 059 regression on `c55b7de`: exit 0, `RESULT: all invariants hold`.
- T4 browser (real Chromium `/usr/bin/chromium`, playwright-core 1.64.0): **39 passed, 0 failed** (17 desktop + 17 mobile + 5 hostile). One first-pass FAIL was a `/favicon.ico` 404 from the scratch static server, proven environmental by a clean re-run with a stub favicon; the game file references no favicon.
- T2 midnight: 4/4. T3 negatives: 11/11. T6 purity diff: 17 diff lines, all the additive `dailySeedForDay` block.
- Full pasted outputs: `flambeee-team/qa-results.md` (Session 30).

## 4. Verdict

Story 064 AC-1..AC-6 verified against PR #122 + PR #123. No blocking defects.
E5 is a non-blocking observation for the release wave.
