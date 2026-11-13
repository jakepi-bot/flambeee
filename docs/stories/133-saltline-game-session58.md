# Story 133: SALTLINE game design contract (Session 58, P2, DESIGN ONLY, builds Friday 2026-11-13)

**Status:** Ready for development (Session 60, 2026-11-13).
**Author:** Quinn (Business Analyst), Wave 2, from Rook's contract.
**Priority:** P2 (contract tonight so Friday's NEW-GAME window builds without a design sprint inside the window).
**Assigned to:** **Riven** (single code owner; holds Story 137 site integration in the same PR).
**Base commit:** `f029493`.
**Design contract:** `flambeee-team/design-handoff.md`, Session 58, Section D (Rook; the contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 58 (2026-11-11), priorities item 4.
**Tracked by:** Session 58 plan, Story 133. Directive 6 governs: one genuinely original mechanic, not a reskin.
Session 60 build note: design-handoff.md Section A is the binding contract; build one file plus the Story 137 site surfaces in a single PR.

## Summary

Friday needs a new original game, and a 50 minute window leaves no room to invent one on the spot. This story is the full blueprint, written tonight so Friday is pure building. The game is called SALTLINE. Picture a line of salt holding back the sea: each moment the water pushes forward by a random amount, and your only move is to push back. The twist is that holding back makes the push stronger: wait three moments and the push moves 1 step, wait six and it moves 6. Tap constantly and nothing happens, which is what makes constant tappers lose every time. One screen, one button, one minute per game, fully determined by a numbered starting arrangement so every result can be rechecked. The blueprint below pins every number Friday needs: the push table, the water amounts, the timing, the win rule, and the exact pass marks the finished game must hit before it can ship.

## Why this is not a reskin (D7, load-bearing)

Strip all art to an integer `p` in 0..8, an integer `passes`, and a binary gust stream. The remaining rule (push strength grows with the square of consecutive holds against a seeded 1D advance) is not a named shipped title. Rejected as duplicates: tower defense (no placement, targeting, HP, pathing, currency); Snake/line games (no growth, no self-collision); stop/go traffic games (no reaction test); clickers (mashing measured 0.000 win rate over 400 seeds); Afterglow (no information/input phase split); Typewreck (no text, no aiming); Snapline #206 (a load-breaking ceiling shooter, a different rule). If the Friday playtest reads as "hold Space until it flashes," the fix is to sharpen the charge readout (show the next-push gain integer), not to add a second verb.

## Files (Friday)

| File | Change | Owner |
|---|---|---|
| `website/games/saltline.html` | New single file, no dependencies, no build step, deterministic seeded generation, keyboard only for the first build. | Unassigned until Friday |

No file tonight. No PR tonight.

## Functional requirements

### 1. States and inputs (D1)

- FR-1. States: `TITLE` (name, one-line rule, seed display, Start control, no running tick), `RUN` (ticks advance, PUSH accepted), `WIN` (survived all 60 ticks; shows ticks, pushes used, seed, restart), `LOSE` (front reached home; shows ticks survived, seed, restart, reason string `flood`).
- FR-2. Inputs, keyboard only this build: Enter or Space starts from `TITLE`; Space pushes during `RUN`; R or Enter restarts from `WIN`/`LOSE` with a fresh seed. No pointer, no touch, no pad this build.
- FR-3. Transitions: S1 Enter/Space TITLE to RUN (tick 0, `p = P0`, `passes = 0`, gust stream dealt from the displayed seed); S2 tick every `TICK_MS` (action phase, then gust phase, then flood check); S3 tick 60 complete with `p > 0` to WIN; S4 flood check `p <= 0` to LOSE; S5 R or Enter from WIN/LOSE to RUN with a fresh seed (R mid-RUN also restarts with a fresh seed).
- FR-4. First five minutes: title line plus one-line rule, first push inside 10 seconds, first storm surge inside 20 ticks by seed construction, first loss no earlier than tick 8 on default tuning.

### 2. Formulas with units (D2)

- FR-5. Tick order (normative): (1) action: if Space pressed since last tick, `p = min(PMAX, p + gain(passes))`, `passes = 0`; else `passes = min(passes + 1, PASSCAP)`; at most one push per tick, extras ignored. (2) gust: `p = p - gust[t]`. (3) flood check: `p <= 0` loses.
- FR-6. Push gain in cells: `gain = min(floor(passes^2 / 6), GAIN_CAP)`. Gain table at defaults: passes 0,1,2 give 0; 3 gives 1; 4 gives 2; 5 gives 4; 6 or more gives 6. Pushing with 2 or fewer passes moves nothing.
- FR-7. Gust stream in cells per tick, seeded: `gust[t]` is 2 with probability `STORM_P`, 1 with probability `GUST_P`, else 0, drawn sequentially from `mulberry32(seed)`. Expected advance per tick `GUST_P + STORM_P` cells (0.48 at defaults), about 28.8 over 60 ticks against an opening buffer of 6 plus pushes. Dealt seeds re-roll until ticks 0..19 contain at least one storm; seed space `0..2^31-1`, displayed on TITLE and end screens.
- FR-8. Score: ticks survived 0..60; 60 with `p > 0` is a win. Best record persists under key `flambeee-saltline-best` as one plain JSON integer (max ticks), sanitized like the Afterglow counter (non-integer, negative, or above 60 degrades to 0). No other persisted state.
- FR-9. Timing: `TICK_MS = 600 ms`; a full run lasts at most 36 s plus start/end screens. Pushes used counted for the end screen only; score never depends on them.
- FR-10. Reference PRNG (normative): `mulberry32(a)`: `a` unsigned 32-bit; each draw does `a = (a + 0x6D2B79F5) mod 2^32`, `t = a ^ (a >> 15)`, `t = t + (t ^ (t >> 7)) * (61 | t)`, `t = t ^ (t >> 14)`, return `(t mod 2^32) / 2^32`.

### 3. Tuning constants (D3, all live in the single file)

| Name | Default | Min | Max |
|---|---|---|---|
| `TICKS` | 60 ticks | 40 | 90 |
| `TICK_MS` | 600 ms | 400 | 1000 |
| `P0` | 6 cells | 4 | 8 |
| `PMAX` | 8 cells | 6 | 10 |
| `GAIN_DIV` | 6 | 4 | 9 |
| `GAIN_CAP` | 6 cells | 4 | 8 |
| `PASSCAP` | 8 ticks | 6 | 12 |
| `GUST_P` | 0.40 | 0.30 | 0.55 |
| `STORM_P` | 0.08 | 0.04 | 0.15 |

- FR-11. Derived, not tunable: expected advance per tick `GUST_P + STORM_P`; full-run expectation `TICKS * (GUST_P + STORM_P)`. Fixed: one verb (Space), one screen, one best integer.

### 4. Edge cases (D4)

- FR-12. Space held down (key repeat): at most one push per tick; degrades to mashing and loses.
- FR-13. Push with `passes <= 2`: gain 0, `passes` still resets (the mash-killer, by design).
- FR-14. Push overflow above `PMAX`: wasted, by design.
- FR-15. Storm on tick 0: `p` falls at most to 4; minimum survival over the 400-seed set is >= 8 ticks for every policy.
- FR-16. Tab hidden mid-run: pause on `visibilitychange`, resume on visible, no catch-up burst.
- FR-17. Corrupt or missing best record: degrades to no best display; game plays on.
- FR-18. Restart mid-RUN: discards the run, deals a fresh seed, never touches the best record.
- FR-19. Seed failing the storm-in-first-20 rule: re-roll at generation (bounded 100 tries, then accept); the displayed seed is always the accepted one.

### 5. Plan B (D4, numeric retreat only)

- FR-20. If Friday's harness shows the skilled policy under 0.60: lower `GUST_P` to 0.36 first, then `STORM_P` to 0.06. If mashing exceeds 0.05: raise `GAIN_DIV` to 8. One lever at a time, harness re-run after each. No second verb, no powerups, no difficulty menu.

## BDD acceptance criteria (playable or measurable Friday, never by reading source)

- AC-1. Given TITLE with a displayed seed, when Enter is pressed, then RUN starts at tick 0 with `p == 6`, `passes == 0`, and the same seed deals the same first-ten gust values as the seed-7 vector on demand. (D133-1)
- AC-2. Given RUN with 3 consecutive hold ticks, when Space is pressed on the 4th tick, then the front moves back by exactly 1 cell before the gust phase. (D133-2)
- AC-3. Given RUN with 6 consecutive hold ticks, when Space is pressed on the 7th tick, then the front moves back by exactly 6 cells (capped at 8) before the gust phase. (D133-3)
- AC-4. Given RUN, when Space is pressed twice in the same 600 ms tick, then exactly one push resolves. (D133-4)
- AC-5. Given RUN at any tick, when the tab is hidden, then ticks stop within one tick period and resume without a catch-up burst on visible. (D133-5)
- AC-6. Given a run reaching tick 60 with `p > 0`, when the tick completes, then WIN shows ticks 60, pushes used, and the seed, and the best record is at least 60. (D133-6)
- AC-7. Given a run where the front reaches 0, when the tick completes, then LOSE shows reason `flood`, ticks survived, and the seed, and restart deals a fresh seed. (D133-7)
- AC-8. **Seed-7 cross-check vector (gating):** given the Friday node harness, when it draws ten values from `mulberry32(7)`, then they equal 0.564225, 0.722005, 0.528207, 0.901646, 0.417482, 0.088381, 0.669771, 0.932160, 0.406154, 0.985101, hence gust `0,0,0,0,1,1,0,0,1,0` at `GUST_P` 0.40 / `STORM_P` 0.08. The harness must reproduce this vector exactly before any balance leg runs; else its numbers mean nothing.
- AC-9. **Balance model (gating, seeds 0..399, 3 policies, 1200 runs total):** policies P_skill (push if `p <= 1`, else push if `p <= 2` and `passes >= 5`), P_rhythm (push every 6th tick), P_mash (push if `passes >= 1`). Calibration: P_skill 0.733 win rate / 51.2 mean ticks; P_rhythm 0.642 / 48.3; P_mash 0.000 / 11.3. Pass thresholds at defaults: P_skill win rate >= 0.60; P_rhythm in [0.45, 0.80]; P_mash <= 0.05; separation P_skill minus P_mash >= 0.55; mean ticks P_skill minus P_mash >= 30; minimum survival over all 1200 runs >= 8 ticks. A miss triggers Plan B levers in FR-20 order, one at a time. The Friday build must prove these before it can ship.
- AC-10. Given a first-time player with the charge number visible, when 15 ticks pass, then the falsifying read is recorded: held until the front was at 3 or closer at least once (pass), or mashed from the start (spine failed, see withdrawal).

## Withdrawal conditions (D8, what kills this design)

Withdraw, do not patch, if any holds: (1) the harness reproduces the seed-7 vector but P_skill lands under 0.45 after both Plan B levers; (2) P_mash exceeds 0.20 at any tuning in the D3 ranges; (3) the human falsifying read in AC-10 fails on 3 of 5 first-time players; (4) the build cannot fit one screen, one verb, and start/end-only menus inside the window. Any withdrawal returns Snapline #206 to the table as the rework base, not a new design sprint.

## Out of scope (tonight and Friday)

Tonight: all code. Friday: pointer, touch, pad input; a second verb; powerups; difficulty menu; economy; art beyond one readable screen; any second file; any dependency or build step.

## Definition of done (tonight)

This file plus design-handoff Section D committed through the docs PR; balance model restated above as AC-8/AC-9 with seeds, run counts, thresholds, and the seed-7 vector; no code written; nothing assigned until Friday.
