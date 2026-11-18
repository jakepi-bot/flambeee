# Story 144: EMPTY HANDS proof harness and balance gate (Session 65, P1, tooling only)

**Status:** Build-ready (Session 65, 2026-11-18).
**Author:** Quinn (Business Analyst), Wave 1.
**Priority:** P1 (tooling; release blocker in practice: the gate must be green before the release wave cuts anything).
**Assigned to:** **Kai** (SOLE code owner; one PR covering the harness plus its seed manifest, zero `website/` bytes). Riven peers the PR. Scout verifies both PRs.
**Base commit:** `1a7e7f6` (main, Session 64 merge of #261).
**Design contract:** `flambeee-team/design-handoff.md`, Section M, binding M.9 (final seed set, mirror rule, seven thresholds, RED anchor); M.2 (dealer and DP to mirror); M.3 (CONFIG to mirror); M.6 (surface to drive).
**Session plan:** `flambeee-team/session-plan.md`, Session 65 (2026-11-18), P1 item plus the seven-check gate.
**Dependencies:** Story 142 (the harness aims at the shipped file; Kai builds after Riven's game file lands so the target exists). Order for the 01:55 wave: Riven game file first, Kai harness second, then Scout, then Rook design review.

## Context (why this story exists)

The session ships only if an honest 200-seed gate returns a non-degenerate band before 02:45. The probe (session-plan table, seeds 2000+s) says the band exists at greedy 0.60 on the hardest rung with a 40-point solver gap, but the probe is not the gate. This story builds the gate: a committed harness plus a committed seed manifest that replays the shipped constants, runs 200 seeds per level config, plays the page in real Chromium on desktop and mobile, and exits non-zero on every failure. A RED anchor proves the harness can fail: it exits 2 when the game file is absent.

## Scope

Two new paths, tooling only: `dev/empty-hands-proof.py` plus its committed seed manifest. Zero bytes under `website/`. No version cut, no release artifacts.

## Files (one PR, Kai)

| File | Change | Owner |
|---|---|---|
| `dev/empty-hands-proof.py` | New harness: sim band per level, purse monotonicity, no-waiting-action assert, drift check against shipped CONFIG, browser leg on both viewports, RED anchor | Kai |
| Seed manifest (committed next to the harness, name recorded in the PR body) | Final gate seed set: SEED_BASE 3000, level L (1-based) uses seeds `3000 + L*1000 + s` for s = 0..199; 200 runs per level config | Kai |

No other file. Zero paths under `website/`. The manifest is committed, not generated at run time, so the gate replays the identical seeds every run.

## Functional requirements

- FR-1. The harness runs under `env -u PYTHONPATH .venv/bin/python` (repo venv). All sim numbers are produced with that interpreter. The interpreter is named in every pasted evidence block.
- FR-2. Mirror rule: the harness reads the shipped CONFIG object from `website/games/empty-hands.html` and replays its constants (N_PER_LEVEL, SLACK_PER_LEVEL, VMIN, VMAX, SHRINK_STEP, SHRINK_FLOOR, LEVEL_CAP). Any drift between the harness copy and the shipped file is a build failure: the harness fails with the drifted constant named. A drift failure is never tuned around; the file and the harness are brought back into agreement and the gate re-runs.
- FR-3. Sim band per level config on the committed manifest: for each of the six level shapes (n 8/9/10/11/12/12 with slack 3/2/1/0/0/0), 200 seeds, four policies: solver (exact interval DP per M.2), fixed-greedy (cheaper end, tie left), random legal-end, never-give. Reports per level: solver win rate, greedy win rate, random win rate, solver-minus-greedy gap, mean optimal spend.
- FR-4. Gate check 1, solvable: solver spend at or below the dealt purse for every seed, 200/200 per level. Any miss means the dealer or purse formula drifted; nothing ships.
- FR-5. Gate check 2, greedy band: fixed-greedy win rate on the hardest level (L6, n=12 slack 0) between 0.15 and 0.60 inclusive. Probe reference: 0.60.
- FR-6. Gate check 3, skill gap: solver minus greedy at least 25 points on the hardest level. Probe reference: 40 points (1.00 minus 0.60).
- FR-7. Gate check 4, random cap: random legal-end play at or below 0.10 on the hardest level. Probe reference: 0.02. Level 1 random may read high (probe 0.49); that is the onboarding rung and is not gated.
- FR-8. Gate check 5, purse monotonicity: purse strictly decreases on every gift across all 200 runs per level, asserted through the shipped turn logic, no free moves, no refunds, no passive regen.
- FR-9. Gate check 6, no waiting action: the never-give policy wins 0/200 on every level, and the harness statically asserts the shipped file exposes no pass, hold, skip, or undo handler or control. Either a win without giving or a waiting-action handler fails the gate.
- FR-10. Gate check 7, browser leg: real Chromium at 1280x800 and at 375x667 with real clicks and taps (no synthetic state injection): TITLE to RUN, one full board clear, one deliberate bust, one level advance, best persistence across reload, overflow 0 on both viewports, zero page-attributable console errors, no network request after first load. Browser leg failures exit non-zero with the failing check named.
- FR-11. RED anchor: with the game file absent (verified in a worktree at base `1a7e7f6`, which predates the file), the harness exits 2. The anchor is demonstrated, not assumed: the exit code is pasted in the PR body.
- FR-12. Output discipline: one pasted block per gate check with the interpreter named, the seed set named, and the four sim numbers per level (solver, greedy, random, gap) in the same shape as the session-plan probe table. `git diff --stat` pasted to prove zero `website/` bytes.

## BDD acceptance criteria

Threshold: 10 of 10 on the PR head. Each Then names the observable command and the expected exit code under `env -u PYTHONPATH .venv/bin/python`.

- AC-1 (harness runs). Given the PR head, when run as `env -u PYTHONPATH .venv/bin/python dev/empty-hands-proof.py`, then it starts, loads the committed manifest, reads the shipped CONFIG, and reports per-level numbers or fails with the cause named.
- AC-2 (manifest committed). Given the PR head, when the manifest is read, then it holds SEED_BASE 3000 with seeds `3000 + L*1000 + s`, s = 0..199, 200 runs per level config, committed in git (not generated at run time).
- AC-3 (gate 1 solvable). Given the manifest seeds, when the solver leg runs, then optimal spend is at or below the dealt purse for 200/200 seeds on every level shape, exit 0 on this check.
- AC-4 (gate 2 greedy band). Given the manifest seeds, when the fixed-greedy leg runs on the hardest level (L6, n=12 slack 0), then the win rate reads between 0.15 and 0.60 inclusive (probe reference 0.60).
- AC-5 (gate 3 skill gap). Given the manifest seeds, when solver and greedy legs are compared on the hardest level, then solver minus greedy reads at least 25 points (probe reference 40 points).
- AC-6 (gate 4 random cap). Given the manifest seeds, when the random legal-end leg runs on the hardest level, then the win rate reads at or below 0.10 (probe reference 0.02).
- AC-7 (gate 5 monotone purse). Given all 200 runs per level, when every gift is asserted, then the purse strictly decreases on every gift with zero exceptions, exit 0 on this check.
- AC-8 (gate 6 no waiting action). Given the manifest seeds, when the never-give policy plays every level, then it wins 0/200 everywhere, and the static scan finds no pass, hold, skip, or undo handler in the shipped file.
- AC-9 (gate 7 browser legs). Given real Chromium, when the page is driven with real clicks and taps at 1280x800 and at 375x667, then TITLE to RUN, a full clear, a deliberate bust, a level advance, and best persistence across reload all pass, with overflow 0, zero page-attributable console errors, and no post-load network on both viewports.
- AC-10 (RED anchor). Given a worktree at base `1a7e7f6` where `website/games/empty-hands.html` is absent, when the harness runs there, then it exits 2, pasted in the PR body next to the green PR-head run.

## Acceptance command list (the 01:55 dev wave runs and pastes all of these)

```
env -u PYTHONPATH .venv/bin/python dev/empty-hands-proof.py
```

Full gate on the PR head: seven checks green, exit 0, with the per-level sim table (solver, greedy, random, gap, mean optimal) pasted in the PR body in the session-plan probe table shape.

```
git diff --stat
```

Pasted in the PR body to prove the diff holds only the harness plus the manifest: zero paths under `website/`.

RED anchor (in a throwaway worktree at base `1a7e7f6`, game file absent):

```
env -u PYTHONPATH .venv/bin/python dev/empty-hands-proof.py
```

Expected: exit 2. Pasted next to the green run. A harness that stays green with the file absent is a relaxed assertion and the PR is rejected.

Browser leg evidence: viewport readings at desktop 1280x800 and mobile 375x667 with overflow 0, driven with real clicks/taps, pasted per FR-10 (or the harness prints them; either way they appear verbatim in the PR body). Zero page-attributable console errors.

## Design criteria map (Rook M.8 and M.9, by reference, not duplicated)

M.9 is this story's contract: final seed set, mirror rule, seven thresholds, RED anchor. The AC above is its developer-testable form. M.8 scenarios that need a live page (first load, keyboard-only, touch, best persistence) are exercised by the browser leg (gate 7); the harness does not re-state them.

## Completion checklist

- [ ] `dev/empty-hands-proof.py` created; seed manifest committed beside it
- [ ] Manifest replays SEED_BASE 3000 schedule, 200 runs per level, identical every run
- [ ] Drift check reads shipped CONFIG and fails by name on any drift
- [ ] AC-1 through AC-10 recorded pass in the build PR body with live pasted output, 10 of 10
- [ ] Sim table pasted per level in probe-table shape with the interpreter named
- [ ] RED anchor exit 2 demonstrated from base worktree and pasted
- [ ] `git diff --stat` pasted: zero `website/` paths
- [ ] Riven peer review; Rook design review against Section M

## Cut line (binding, from session-plan)

This story is P1 tooling but the gate is the release blocker: all seven checks green before the release wave cuts anything. Hard out 1: gate not green by 02:45 ships nothing (no card, no precache line, no half-done bump). Hard out 4: if the gate says it is not a game, the mechanic is retired with a decision record like `001-snapline-spine-retired`; never tune after 02:45 to force a ship.

## Out of scope

- No game logic or site edits (Stories 142 and 143, Riven). This PR holds zero `website/` bytes.
- No version cut, no release artifacts, no BLOG, no Bluesky staging, no What's New.
- No Cinder, cadence, FPS, controller, manifest (#237/#238), or runner UX (#254/#255) work.
- No new seed schedule: the manifest replays M.9 verbatim. Any schedule change needs Rook and a new gate run.
- No visual redesign. Palette owns visual direction.
- No fourth story. Anything extra goes to follow-ups with a priority.

## Open questions

None. M.9 binds the seed set, thresholds, mirror rule, and RED anchor. The manifest name is Kai's call; it is recorded in the PR body.

## References

- `flambeee-team/session-plan.md`, Session 65 (2026-11-18): P1 harness, seven-check gate, interpreter, hard outs, gate evidence list for the PR body.
- `flambeee-team/design-handoff.md`, Section M (Rook): M.2 dealer and DP, M.3 CONFIG, M.6 surface, M.9 seed set plus thresholds plus RED anchor, M.11 HOARD deviation (gate 6 rationale).
- Format precedent: Story 141 (`docs/stories/141-cinder-proof-family-session64.md`) for the tooling-story shape with falsifying tests.
