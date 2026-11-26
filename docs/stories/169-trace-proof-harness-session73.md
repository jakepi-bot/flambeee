# Story 169: TRACE proof harness (Session 73, P1)

**Status:** Ready for development (Session 73, 2026-11-26).
**Author:** Quinn, Business Analyst.
**Priority:** P1 (the instrument half of the session; per the session plan this story is not cut: it is the only proof the forge is deterministic and the level reachable).
**Assigned to:** **Kai**, sole code owner. File: `dev/trace-proof.py` only. Zero website bytes.
**Base commit:** `d5e8b63` (main, v0.59.0).
**Scope:** Determinism leg (200 seeded synthetic strokes forged twice), forge invariant leg (monotone, room fixtures, minimum refusal), reachability leg (200 day-seeds, BFS within 80 moves), RED anchor against the pre-166 tree, browser legs at 1280x800 and 375x667 with real pointer drawing. Exit discipline unchanged: PASS 0, FAIL 1, RED 2, SKIP 3.
**Design contract:** `flambeee-team/design-handoff.md`, Section 4 (Story 169, subsections 4.1 through 4.3). Design-owned observable criteria live in contract subsection 4.3 and are mapped here one for one. Balance and determinism rationale hooks live in contract subsections 4.2 and 6.
**Non-blocking rule:** Story 169 is never cut. If driving the full DRAW to FORGE to RUN to WIN pass proves flaky at 375x667, Kai fixes the wait/retry inside the browser leg (longer wait, same transitions) and records it; the assertions, run counts, thresholds, and RED anchor do not shrink.

## Summary

Nobody can look at a forged level and tell whether the forge is deterministic or the exit is always reachable, so this story builds the instrument that proves both. The harness reimplements the contract forge rule in Python and checks five things: forging the same stroke twice always gives byte-identical walls (200 seeded strokes, including 20 adversarial strokes hugging cell edges); growing a stroke never removes a wall, a ring of ink always makes a room while a straight line never does, and too-short strokes are always refused without changing state; 200 daily seeds always produce a level whose exit is reachable within 80 moves; the harness itself is honest, because it exits RED against the tree before the game file exists; and real pointer drawing in headless Chromium at desktop and phone sizes never scrolls the page and completes one full run to WIN on the fixed triple. One miss anywhere is FAIL, never a warning.

## Story

As the team, I run one harness that proves the forge is deterministic and every forged level is reachable so the game ships on evidence, not on looks.

## Functional requirements

FR-1 (contract 4.1, determinism leg). 200 seeded synthetic strokes (seed equals leg index 0..199, mulberry32, same normative code as the contract). Each stroke forged twice from identical point lists; wall sets must be byte-identical (sorted JSON compare) all 200 of 200. Includes 20 adversarial near-boundary strokes (points within 0.5 px of cell edges) exercising the tie-break.

FR-2 (contract 4.1, forge invariant leg). (a) Monotone: extending any stroke (appending 50 px) never removes a wall cell, 50 of 50. (b) Room: the RING fixture (3 by 3 hollow square of ink at rows and cols 2..4) forges at least 1 pocket floor cell; the STRAIGHT fixture (5 horizontal ink cells at row 4, cols 2..6) forges 0 pockets. (c) Minimum: 20 synthetic strokes under 108 px or under 3 cells are refused with no state change (state stays DRAW) 20 of 20.

FR-3 (contract 4.1, reachability leg). 200 day-seeds (D equals 20783 + i): derive skeleton per the 167 rule, forge a seeded synthetic stroke plus the RING and CROSS fixtures, BFS START to EXIT on floor. Reachable within MOVE_LIMIT 80 moves, 200 of 200, with the stitch firing count reported (legs where the L corridor was needed), not gated.

FR-4 (contract 4.1, RED anchor). The harness run against the pre-166 tree (trace.html absent) exits RED 2 with the missing-file line. Proves the harness tests the game, not itself.

FR-5 (contract 4.1, browser legs). Headless Chromium at 1280 by 800 and 375 by 667: real pointer drawing (synthetic pointer events through the page), scroll check (window.scrollY stays 0 during a diagonal drag), and one full DRAW to FORGE to RUN to WIN pass on the fixed triple. Touch discipline asserted: `touch-action: none` on the drawing surface plus single-pointerId tracking present in the file.

FR-6 (contract 4.2, thresholds). Pass thresholds: determinism 200/200, reachability 200/200, minimum-refusal 20/20, room fixtures exact (RING at least 1, STRAIGHT exactly 0), RED anchor RED 2, browser legs PASS at both viewports. Any single miss is FAIL 1, never a warning. Run count and seeds are fixed above so a rerun reproduces the same suite.

## Acceptance criteria (BDD, observable in harness runs)

Design-owned observable criteria are in contract subsection 4.3; AC-1 through AC-3 map them directly. AC-4 through AC-7 pin the remaining normative behaviors above.

1. Given the pre-166 tree, when the harness runs, then it exits RED 2 naming the missing game file. (design 4.3.1)
2. Given the 166 tree, when the harness runs, then it exits PASS 0 with 200/200 determinism and 200/200 reachability lines printed. (design 4.3.2)
3. Given the 375 by 667 run, when a diagonal pointer drag draws, then window.scrollY stays 0 and the stroke forges. (design 4.3.3)
4. Given any stroke extension of 50 px, when the invariant leg runs, then no wall cell is removed 50 of 50, the RING fixture forges at least 1 pocket, the STRAIGHT fixture forges 0 pockets, and 20 under-minimum strokes are refused with no state change 20 of 20.
5. Given the reachability leg, when it runs, then all 200 day-seeds forge fields with EXIT reachable within 80 moves and the stitch firing count is reported.
6. Given the 1280 by 800 run, when real pointer drawing completes a full DRAW to FORGE to RUN to WIN pass on the fixed triple, then the run prints PASS and the file asserts `touch-action: none` plus single-pointerId tracking.
7. Given the merged PR, when the reviewer runs `git diff --stat` against main, then only `dev/trace-proof.py` changed (zero website bytes).

## Out of scope (NOT DOING)

No website bytes: no `website/` path may appear in this story's diff. No game logic change, no tuning-constant change, no new CLI flag, no exit-discipline change (PASS 0, FAIL 1, RED 2, SKIP 3 stay). No narrowing of run counts, seeds, or thresholds under Plan B.

## Dependencies

Depends on: Story 166 (the forge this harness proves; the RED anchor runs against the pre-166 tree). Lands independently of the 166 PR but proves it.

## Notes

Normative source is contract Section 4 (subsections 4.1 legs, 4.2 rationale hooks, 4.3 acceptance criteria); run counts, seeds, and thresholds reproduce contract Section 6 determinism case.
