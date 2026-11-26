# Story 167: TRACE daily skeleton (Session 73, P0b)

**Status:** Ready for development (Session 73, 2026-11-26).
**Author:** Quinn, Business Analyst.
**Priority:** P0b (the daily habit; ships in the same PR as Story 166 in v0.60.0).
**Assigned to:** **Riven**, sole code owner, same PR as Story 166. File: `website/games/trace.html` only (CONFIG plus derivation plus day label plus best persistence).
**Base commit:** `d5e8b63` (main, v0.59.0).
**Scope:** A UTC-day seed fixes the start cell, the exit cell, and a short pre-drawn skeleton fragment, identical for every player that day with no network. Day label plus local best per day (the only gameplay persistence).
**Design contract:** `flambeee-team/design-handoff.md`, Section 2 (Story 167, subsections 2.1 through 2.5). Design-owned observable criteria live in contract subsection 2.5 and are mapped here one for one.
**Non-blocking rule:** if the seeded derivation cannot ship, it degrades to a fixed hand-authored triple (FIXED_TRIPLE: START {r:1,c:1}, EXIT {r:7,c:7}, SKELETON {(4,3),(4,4),(4,5)}) before it is cut entirely. The game never ships without a reachable exit; the 166 stitch guarantee covers the fixed triple too.

## Summary

Every player on a given day draws onto the same frame. At midnight UTC the game derives three things from the date alone: where you start, where the exit is, and a short three-cell wall fragment already sitting on the field. Everybody in every timezone gets the same three things, and no server or download is involved: the seed is just the day number, computed on the device. At the end of each run the game keeps your best coverage percentage for today and shows it beside the plays line. Tomorrow it resets. This is a shared daily habit, not a shared online level and not a leaderboard.

## Story

As a player, I start each UTC day with the same start, exit, and skeleton fragment as every other player so my run is comparable to my own best today.

## Functional requirements

FR-1 (contract 2.1, derivation). No new states. The skeleton is data loaded at boot and shown on TITLE: START, EXIT, and a 3-cell skeleton bar, all derived from the UTC date index D with mulberry32 (unsigned 32-bit wrap, same code shape as EMPTY HANDS). D equals floor(Date.now() / 86400000); Date.now is UTC-based, no timezone guess. START equals { r: 1 + floor(rng() * 7), c: 1 + floor(rng() * 7) }. EXIT is drawn the same way until manhattan(START, EXIT) reaches at least MANHATTAN_MIN 8, max 50 draws; fallback EXIT equals { r: 8 - START.r, c: 8 - START.c }, and if that equals START, EXIT equals { r: 1, c: 7 }. SKELETON is a 3-cell horizontal bar: row skR equals 1 + floor(rng() * 7), col skC equals 1 + floor(rng() * 5), cells (skR, skC), (skR, skC+1), (skR, skC+2); while any bar cell equals START or EXIT, skR equals (skR % 7) + 1 (terminates: at most 2 of 7 rows blocked).

FR-2 (contract 2.1, rendering and label). Skeleton cells render as fixed walls visually distinct from ink, are part of WALLS, and are excluded from inkCells and brushed. The day label on TITLE reads "Day {D}" (for 2026-11-26, Day 20783).

FR-3 (contract 2.1, local best). Single key BEST_KEY (flambeee-trace-best) holding JSON {day: D, pct: 0..100}. Load: parse, require integer day equal to today and integer pct 0..100, else 0. Save: on WIN or LOSE, if pct beats stored (or stored day is stale), write {day: today, pct}. Blocked storage stays silent with a memory fallback. This is the only gameplay persistence; plays use COUNT_KEY per Story 170.

FR-4 (contract 2.3, tuning). Covered by the 166 table (MANHATTAN_MIN) plus BEST_KEY flambeee-trace-best (JSON {day, pct}) and FIXED_TRIPLE for the degradation path. No second key, no per-day key family.

FR-5 (contract 2.4, edge cases). Same D across timezones yields the identical triple everywhere: D derives from UTC milliseconds, never local midnight. A run crossing UTC midnight keeps its boot triple; the next Start re-derives and shows the new day label. Corrupt best JSON is treated as 0 for today, overwritten on the next end, never rendered as garbage. A best from a past day is treated as 0, with the day label making the reset legible ("Best today: 0%"). If the rng draws 50 exits all too close, the fallback triple applies (probability ~0, deterministic).

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 2.5; AC-1 through AC-5 map them directly. AC-6 through AC-10 pin the remaining normative behaviors above.

1. Given two boots with the same UTC date, when the fields render, then START, EXIT, and SKELETON are identical cell for cell. (design 2.5.1)
2. Given any day seed, when the skeleton derives, then manhattan(START, EXIT) is at least 8 and no skeleton cell equals START or EXIT. (design 2.5.2)
3. Given TITLE, when it renders, then the label reads "Day {D}" with D equal to floor(Date.now()/86400000). (design 2.5.3)
4. Given a WIN at 60% with best today 40%, when the end screen renders, then the HUD reads "Best today: 60%" and storage holds {day: D, pct: 60}. (design 2.5.4)
5. Given a stored best from a different day, when the game boots, then the HUD reads "Best today: 0%". (design 2.5.5)
6. Given a stored best holding corrupt JSON, when the game boots, then the HUD reads "Best today: 0%" and the next end overwrites it with a clean value.
7. Given a run in progress across UTC midnight, when the player finishes it, then it keeps its boot triple, and the next Start re-derives and shows the new day label.
8. Given any boot, when the field renders, then skeleton cells render as fixed walls distinct from ink and are excluded from the ink meter and the brushed percentage.
9. Given a LOSE that beats the stored best, when the end screen renders, then the best updates exactly as on a WIN; given an end below the stored best, when it renders, then the stored best is unchanged.
10. Given the degradation path in force, when the game boots, then START is {r:1,c:1}, EXIT is {r:7,c:7}, SKELETON is {(4,3),(4,4),(4,5)}, the Day label still reads D, and the exit is reachable via the 166 stitch guarantee.

## Out of scope (NOT DOING)

No network, no fetch, no server, no shared online level: the skeleton is a deterministic local seed derived from the UTC date index on the device. No timezone guess: D derives from UTC milliseconds, never local midnight. No per-day key family: one BEST_KEY holding {day, pct}, no second key. No leaderboard, no accounts, no cross-player comparison beyond the shared frame. No change to the forge rule itself (that is Story 166), no site rider (that is Story 168), no play-counter line (that is Story 170).

## Dependencies

Depends on: Story 166 (same PR; this story's START, EXIT, SKELETON, carve, stitch, and HUD slot all land in the 166 file). Degrades to FIXED_TRIPLE per the cut order before it is cut.

## Notes

Normative source is contract Section 2 (subsections 2.1 derivation and states, 2.2 formulas, 2.3 tuning, 2.4 edge cases and Plan B, 2.5 design acceptance criteria). Day-number reference: 2026-11-26 is Day 20783. Determinism rationale lives in contract Section 6.
