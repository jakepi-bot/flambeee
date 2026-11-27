# Story 171: TRACE derivation v2 and contract amendment (Session 74, P0)

**Status:** Ready for development (Session 74, 2026-11-27).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (the session; the one RED contract item shipped in v0.60.0).
**Assigned to:** **Riven**, sole code owner. Files: `website/games/trace.html` only, plus a one-line `CACHE_VERSION` 36 to 37 rider in `website/sw.js` (precache list unchanged at 25 entries). No other website bytes.
**Base commit:** `5d4a7a9` (main, v0.60.0).
**Scope:** Replace the EXIT fallback with farthest-corner argmax, add the reachability precheck, delete the `{r:1,c:7}` literal, cut derivation v1/v2 at D=20785, amend criterion 2.5.2 from >= 8 to >= 6.
**Design contract:** `flambeee-team/design-handoff.md`, Section 0 (binding amendment, supersedes Session 73 Section 2.5 criterion 2) and Section 1 (Story 171, subsections 1.1 through 1.8). Design-owned observable criteria live in contract subsection 1.7 and are mapped here one for one.
**Non-blocking rule:** If the precheck threatens the diff, drop the precheck and keep the 50-draw loop at floor 6 plus the farthest-corner fallback. The floor stays 6.
**Note:** This story supersedes Session 73 Story 167's acceptance criterion AC-2 (`manhattan(START, EXIT) >= 8`). That criterion was unsatisfiable from the five central cells and is replaced by the amended floor of >= 6 below.

## Summary

TRACE shipped with one contract line that cannot be true. The daily frame promises START and EXIT at least 8 cells apart, but on a 9 by 9 field with interior rows and columns 1..7 the farthest interior cell from the center (4,4) is only 6 away, so five central cells can never satisfy it. This story amends the line to what the geometry allows (at least 6) and replaces the old point-reflection fallback with a farthest-corner pick that guarantees 6 on every one of the 49 interior cells. Today's triple (Day 20784) is frozen byte-identical so nobody's game changes mid-day; the new derivation starts tomorrow (Day 20785).

## Story

As a player, I get a daily frame whose start and exit are always a real distance apart, so the shared day never ships with the endpoints nearly touching.

## Functional requirements

FR-1 (contract 1.1, v2 derivation). Derivation v1 is frozen for `D <= 20784` (byte-identical to `5d4a7a9`); derivation v2 applies from `D >= 20785`. No mid-day triple change. v2: START is drawn exactly as v1 (same two `rng()` calls from `mulberry32(D)`). Compute `maxCellDistance(START)` over all 49 interior cells, range 6..12. If it is below 8, take `farthestCorner(START)` directly and skip the 50-draw loop. Otherwise run the v1 50-draw loop at the new floor 6; on exhaustion, take `farthestCorner(START)`. `farthestCorner` is the argmax of manhattan distance over the fixed corner order (1,1), (1,7), (7,1), (7,7), first wins ties. Skeleton draws follow exactly as v1. Delete the point-reflection fallback and the `{r:1, c:7}` literal; a grep for `8 - start` and `{ r: 1, c: 7 }` in the derivation reads clean.

FR-2 (contract 1.1, untouched states). No new states. TITLE to DRAW to FORGE to RUN to WIN/LOSE transitions, DRAW/FORGE/RUN/WIN/LOSE behavior, ink budget, stitch rule, move limit, play counter, and site card are unchanged. A run crossing UTC midnight keeps its boot triple; the next Start re-derives under the cutoff rule.

FR-3 (contract 1.3, tuning). `MANHATTAN_MIN` 8 to 6 in the CONFIG in `website/games/trace.html`, locked at 6 by geometry. `MAX_EXIT_DRAWS` stays 50. `V2_CUTOFF_DAY` 20785, locked. `CORNER_ORDER` fixed as above. `CACHE_VERSION` 36 to 37 in `website/sw.js`, one line; precache list unchanged at 25 entries.

FR-4 (contract 1.4, edge cases). START on a center cell takes the precheck path (loop skipped, EXIT is the farthest corner). `maxCellDistance` exactly 8 takes the loop path (threshold is strict `< 8`). START == EXIT is impossible by construction (floor 6 > 0); no literal needed. Corrupt best JSON and past-day best behave exactly as Story 167. Old browsers: arithmetic, Math.floor, plain objects only.

FR-5 (distribution and disclosure). All 49 START cells stay in the pool; rejection sampling of START is forbidden. RNG stream disclosure: on the five center cells v2 skips 50 draws, so the skeleton draws shift relative to the v1 counterfactual. This is deterministic and disclosed, and applies to v2 days only. Named limitation (must appear in the release notes and decision 010 as well as here): pre-cutoff days are frozen on v1 and are not reproducible under v2.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 1.7; AC-1 through AC-6 map them directly. AC-7 through AC-9 pin the remaining normative behaviors above.

1. Given D = 20784, when the page derives the triple, then START, EXIT, and skeleton are byte-identical to v0.60.0 (`5d4a7a9`).
2. Given D >= 20785, when the page derives the triple, then manhattan(START, EXIT) >= 6.
3. Given a v2 day with START (4,4), when EXIT derives, then EXIT is (1,1) (first of four tied corners) at distance 6.
4. Given `website/games/trace.html`, when inspected, then the point-reflection fallback and the `{r:1, c:7}` literal are absent.
5. Given `website/sw.js`, when inspected, then CACHE_VERSION is 37 and the precache list holds 25 entries including `./games/trace.html`.
6. Given any of the 49 interior START cells, when v2 derives EXIT, then distance >= 6 and EXIT != START (proven by the Story 172 mirror leg).
7. Given a run in progress across UTC midnight, when the player finishes it, then it keeps its boot triple, and the next Start re-derives under the cutoff rule.
8. Given any v2 day, when the page renders, then DRAW, FORGE, RUN, WIN/LOSE behavior, ink, stitch, move limit, play counter, and site card are unchanged from v0.60.0.
9. Given the diff under review, when inspected, then no website byte outside `trace.html` plus the one-line `sw.js` rider changed, and no new storage key, dependency, or network call exists.

## Out of scope (NOT DOING)

No change to DRAW, FORGE, RUN, WIN, LOSE, ink, stitch, move limit, play counter, or site card. No new storage key, no new dependency, no network call. No resampling or removal of START cells. No EMPTY HANDS bytes (that is Story 173, separate PR). No harness bytes (that is Story 172).

## Dependencies

Depends on: design-handoff Section 0 amendment on main (the one outcome not allowed is shipping this without the amendment written down). Story 172 proves it; Story 173 is independent and cut first.

## Notes

Normative source is contract Section 0 (amendment with geometry, cutoff, RNG disclosure, named limitation) and Section 1 (subsections 1.1 states and transitions, 1.2 formulas, 1.3 tuning, 1.4 edge cases, 1.5 failure modes, 1.6 Plan B, 1.7 design acceptance criteria, 1.8 rationale). Day-number reference: today 2026-11-27 is Day 20784 (v1, frozen); first v2 day is Day 20785. Balance note from contract 1.8: MOVE_LIMIT 80 is untouched against an interior diameter of at most 12, so LOSE still only ever happens to a wanderer, and the distance floor was never load-bearing for LOSE.
