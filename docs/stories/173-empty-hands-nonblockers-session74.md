# Story 173: EMPTY HANDS non-blockers (Session 74, P2, conditional, cut first)

**Status:** Ready for development (Session 74, 2026-11-27), conditional.
**Author:** Quinn, Business Analyst.
**Priority:** P2, conditional, cut first and entire. Ships only if Stories 171 and 172 both land and Scout covers it. Separate PR from 171/172; never touches `trace.html`. If the wave runs short, this story dies first and whole.
**Assigned to:** **Riven** (game file: items 4 and 6 in `website/games/empty-hands.html`) plus **Kai** (harness: items 9 and 10 in `dev/empty-hands-proof.py`).
**Base commit:** `5d4a7a9` (main, v0.60.0).
**Scope:** #265 items 4 and 6 (game guards) and items 9 and 10 (harness discipline). Item 2 is a telemetry re-check with no build action. Items 3 and 5 ride only if trivial (one line, zero risk).
**Design contract:** `flambeee-team/design-handoff.md`, Section 3 (Story 173, subsections 3.1 through 3.8). Design-owned observable criteria live in contract subsection 3.7 and are mapped here one for one.

## Summary

Four small non-blockers from issue #265 ride along only if the real session lands. In the game: holding Ctrl (or Cmd on macOS) must never trigger select-all, and `accepts()` must refuse a bad level quietly instead of throwing. In the harness: skipped seeds must print one loud SKIPPED line each and exit with the distinct skip code, and a page-level DP cross-check over a fixed seed sample must agree with the mirror N/N. None of this is load-bearing for TRACE; it ships only on top of a green 171 plus 172 with QA coverage, in its own PR, and it is the first thing cut.

## Story

As a player, modifier keys never fire game actions by accident and bad levels fail quietly, so the game only ever responds to inputs I meant.

## Functional requirements

FR-1 (contract 3.1, item 4, Riven). The select-all key path gains a modifier guard: when `ctrlKey` or `metaKey` is true, the handler returns before select-all fires (Ctrl+A / Cmd+A never trigger it). Plain unmodified input is behavior-identical.

FR-2 (contract 3.1, item 6, Riven). `accepts()` gains an invalid-level guard: an out-of-range or malformed level returns invalid with no state change and no exception, using the existing invalid copy.

FR-3 (contract 3.1, item 9, Kai). The harness prints one loud `SKIPPED` line per skipped seed case and exits with the distinct skip code 3 when skips occur with zero failures. Zero skips means exit 0 with no SKIPPED lines; FAIL dominates SKIP.

FR-4 (contract 3.1, item 10, Kai). The harness adds a page-level DP cross-check over a fixed seed sample, asserting the live page result equals the mirror result per seed, N/N over the sample. The check loads the live page, not the mirror twice. A seed that must skip counts as a skip with its line, never as a pass.

FR-5 (conditional terms). Separate PR from 171/172. Ships only if 171 and 172 land and Scout covers it. Item 2 (telemetry re-check) has no build action. Items 3 and 5 ride only if trivial. Cut order: item 10 first, then 9, then 6, then 4; any surviving subset ships.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 3.7; AC-1 through AC-4 map them directly. AC-5 pins the conditional terms.

1. Given the game focused, when the player presses Ctrl+A (or Cmd+A), then no select-all fires and game state is unchanged; given a plain unmodified key, when pressed, then behavior is identical to before.
2. Given `accepts()` called with level index -1 (or NaN, or out of range), when it runs, then it returns invalid with no state change and no exception.
3. Given a harness run with skipped seeds and zero failures, when it finishes, then stdout contains one SKIPPED line per skipped seed and the exit code is 3.
4. Given the DP seed sample, when the page cross-check runs, then page results equal mirror results N/N.
5. Given Stories 171 and 172 unlanded or Scout uncovered, when the wave ends, then this story does not ship; given a short wave, when cuts happen, then this story is cut first and entire, and no byte of it lands in the 171/172 PR.

## Out of scope (NOT DOING)

No TRACE bytes (`trace.html` untouched by this story). No change to EMPTY HANDS difficulty, economy, ladder, or purse math. No new game states. Item 2 is a telemetry re-check with no build action and authorizes no code. Items 3 and 5 ship only if trivial. Telemetry never blocks.

## Dependencies

Depends on: Stories 171 and 172 landing plus Scout coverage; #265 stays open unless this ships. Blocked by nothing else; cuts before everything else.

## Notes

Normative source is contract Section 3 (subsections 3.1 states and transitions, 3.2 formulas, 3.3 tuning constants in `website/games/empty-hands.html` and `dev/empty-hands-proof.py`, 3.4 edge cases, 3.5 failure modes, 3.6 Plan B cut order, 3.7 design acceptance criteria, 3.8 rationale). No difficulty or economy change: the guards only remove accidental inputs and the DP check is read-only. Fixed values: INPUT_MOD_GUARD on, ACCEPTS_GUARD on, SKIP_EXIT_CODE 3, DP_SAMPLE_N per this story file (10..200).
