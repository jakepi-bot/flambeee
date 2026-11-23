# Story 158: LIGHTFARE pattern-doc section 10 (Session 70, P1, docs rider)

**Status:** Ready for development (Session 70, 2026-11-23).
**Author:** Quinn, Business Analyst.
**Priority:** P1 (docs; same PR as Story 155, no cache impact of its own).
**Assigned to:** **Kai or Riven**, same PR as Story 155.
**Base commit:** `23674a2` (main, v0.56.0 released).
**Scope:** `docs/play-counter-pattern.md` only: one appended LIGHTFARE instance as section 10, following the Empty Hands section-9 shape. No code, no cache bump from this story alone (rides the 155/156 bump).
**Design contract:** `flambeee-team/design-handoff.md`, Story 158 sections 1 through 6. Design-owned observable criteria live in contract section 5 and are mapped here one for one.

## Summary

The shipped-counter pattern doc needs its LIGHTFARE instance so the next session inherits the counting rule instead of rediscovering it. This story appends section 10 to `docs/play-counter-pattern.md` in the section-9 shape: the counting unit verbatim from Story 155, the boot-deal nuance (none: level 1 loads on Start, nothing pre-dealt), the display rule (plays line plus best line placement in the game shell), key/cap/helper names, the LOSE-retry non-count, and the LEVELCLEAR-advance non-count.

## Functional requirements

FR-1 (contract section 1). Append the LIGHTFARE instance to `docs/play-counter-pattern.md` as section 10, following the Empty Hands section-9 shape: counting unit verbatim from Story 155 (one play equals one Start from TITLE that begins level 1 of a new run), boot-deal nuance (none: level 1 loads on Start, nothing pre-dealt), display rule (plays line plus best line placement in the game shell), key/cap/helper names, LOSE-retry non-count, LEVELCLEAR-advance non-count.

FR-2 (contract section 2). Record the formulas: `plays_new [plays] = min(plays_old + 1, 9007199254740991)` per Start-from-TITLE entry; `best [points] = max(bestStored, runTotal)` at WIN only.

FR-3 (contract section 3). Record the tuning constants: pattern section 10 (LIGHTFARE instance); COUNT_KEY `flambeee-lightfare-plays`; BEST_KEY `flambeee-lightfare-best` (JSON number).

FR-4 (contract section 4, conflict rules). Doc/game drift at merge: the shipped game file wins per the standing conflict rule; fix the doc, never edit the game to match prose. Section numbering clash: the next free section number wins; content normative, number administrative.

FR-5 (contract section 6). Fill every per-game checklist row from the pattern doc (key suffix, display element, run-start hook, cache bump in same PR, no-network grep) before merge.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in contract section 5; AC-1 and AC-2 map them directly. AC-3 pins the checklist.

1. Given the merged PR, when the pattern doc is read, then section 10 states the LIGHTFARE counting unit verbatim and names both storage keys. (design 5.1; FR-1, FR-3)
2. Given any conflict between section 10 and the shipped game file, when reviewed, then the game file governs. (design 5.2; FR-4)
3. Given the merged tree, when the per-game checklist is checked, then every row (key suffix, display element, run-start hook, cache bump in the same PR, no-network grep) is filled. (FR-5)

## Edge cases

- Doc/game drift at merge: shipped game file wins; fix the doc. Never edit the game to match prose. (contract section 4; FR-4)
- Section numbering clash: next free section number wins; content normative, number administrative. (contract section 4; FR-4)

## Out of scope

The game file (Story 155), the site card (Story 156), the proof harness (Story 157), any code, any cache bump from this story alone, any other doc change.

## Traceability

Every contract clause is covered: section 1 states/inputs/transitions map to FR-1 (AC-1); section 2 formulas map to FR-2 (AC-1); section 3 tuning table maps to FR-3 (AC-1); section 4 edge cases map to FR-4 and the Edge cases list (AC-2); section 5 design criteria map to AC-1 and AC-2; section 6 measurement rationale maps to FR-5 (AC-3: every per-game checklist row filled before merge).

## Evidence the dev must paste (in the PR)

- Section 10 present with counting unit verbatim, boot-deal nuance, display rule, key/cap/helper names, retry and advance non-counts.
- Per-game checklist rows all filled.
- No other doc section touched.

## Definition of done

- AC-1 through AC-3 all hold on the branch.
- Changes limited to the one appended section in `docs/play-counter-pattern.md`.
