# Story 125: GOTW rotation ruling (M-2) (Session 54, P1c, docs only)

**Status:** Ready for development (Session 54, 2026-11-07).
**Author:** parent overseer (Wave 2 absorbed; see session-plan.md process incident).
**Priority:** P1c. Backlog item M-2 (issue #214).
**Assigned to:** **Kai** (docs owner). Rides in the same PR as Story 124.
**Design contract:** `flambeee-team/design-handoff.md`, Section 2.

## Summary

Echo Rounds and Typewreck are shipped and precached but have no Game of the Week slot. Issue #214 allows either admitting them to `GAME_ORDER` or recording why each stays out with a revisit date. This story records the ruling: neither enters today, with reasons, gates, and one dated revisit. Docs only. Zero code, zero cache impact.

## Decision to record (from the design contract, do not re-derive)

| Game | Decision | Reason | Revisit |
|---|---|---|---|
| Echo Rounds | stays out | Keyboard-only prototype, no touch input, no detail view; #214 says promotion is a separate NEW-GAME-day proposal | Gated on touch controls + detail view + one month of issue signal; no calendar date |
| Typewreck | stays out | Shipped 2026-11-05, one day old, zero issue signal; a GOTW slot is a 7-day homepage placement | **2026-12-07**, requires 3+ external signals or 20+ local plays across the new counters |

## Requirements

### 1. File

`docs/design-decisions/002-gotw-rotation-session54.md`, following the shape of the existing `001-snapline-spine-retired.md`.

### 2. Contents (all required)

1. Date, session, issue number (#214), status (accepted).
2. The measured mechanic: `GAME_ORDER` at `website/index.html:1169`, six entries, ISO-week index `(week - 1) % 6`, one featured week per game per six.
3. The decision table above, with reason and revisit gate per game.
4. The rotation-width rationale: eight slots would make every game's time-to-feature 33 percent longer while the homepage still shows one card; admission should be evidence-driven, and that evidence is what the play counters produce.
5. What would change the decision: the named gates, and who decides (next LEGACY-day planner with the issue signal in hand).
6. Explicit statement that this record changes no code and that `GAME_ORDER` is byte-identical to base `1ea559f`.

### 3. No site change

`website/index.html` must not be touched. `GAME_ORDER` stays six entries. No cache bump in this PR.

### 4. Issue linkage

PR body names #214 and states that merging the note satisfies its acceptance clause "or a design note records why each stays out with a revisit date". The release wave closes the issue, not the dev.

## Acceptance criteria (BDD)

1. Given the file, when read, then Echo Rounds and Typewreck each have a decision, a reason, and a revisit condition.
2. Given the file, when read, then the Typewreck revisit date is 2026-12-07 and the Echo Rounds gate names touch input and a detail view.
3. Given `git diff 1ea559f -- website/index.html`, when run, then it is empty.
4. Given the record, when read, then it contains the rotation-width rationale and states that no code changes.
5. Given no em dashes and no emoji, when the file is grepped for the em dash character, then zero hits.

## Out of scope

Changing the rotation, adding detail views for either game, Echo Rounds promotion work, Typewreck promotion, any `website/` edit, any cache change.
