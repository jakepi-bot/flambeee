# 010 - TRACE derivation v2: distance floor 6 with farthest-corner fallback, Session 74 (2026-11-27)

Date: 2026-11-27. Session: 74. Status: accepted. Stories: 171, 172. Design contract: flambeee-team/design-handoff.md, Section 0. Supersedes: Session 73 Section 2.5 criterion 2 (`manhattan(START, EXIT) >= 8`).

## Context

v0.60.0 shipped TRACE with one RED contract item: 23 of 200 UTC-day seeds derive START and EXIT below the contracted distance of 8 cells, worst case 2. The fallback (point reflection `{8 - r, 8 - c}`) lands near START for central cells, and a hardcoded `{r:1, c:7}` literal masks the single zero-distance case. Parent-verified geometry: 49 interior cells (rows/cols 1..7); point reflection gives distances min 0, max 12, with 25 cells below 8 and 13 below 6.

## Decision

Amend the criterion to `manhattan(START, EXIT) >= 6 [cells]` for every UTC-day seed, and replace the fallback with farthest-corner argmax over the fixed corner order (1,1), (1,7), (7,1), (7,7), first wins ties. This gives min 6, max 12, zero cells below 6, and exactly five cells below 8: (3,4), (4,3), (4,4), (4,5), (5,4). Add a reachability precheck: if maxCellDistance(START) over interior cells is below 8, skip the doomed 50-draw loop and take the farthest corner directly; otherwise keep the loop (now at floor 6) with the farthest corner on exhaustion. Delete the `{r:1, c:7}` literal. Freeze derivation v1 for D <= 20784 (today) and apply v2 from D >= 20785, so no mid-day triple changes. All 49 START cells stay in the pool. Bump CACHE_VERSION 36 to 37 as a one-line rider; precache list unchanged at 25.

## Reason

Max distance from (4,4) to any interior cell is 6, so `>= 8` is unsatisfiable from the five central cells. The criterion was wrong, not the code (jakebot ruling 2026-11-27). The rejected alternative, rejection-sampling START, deletes 5 of 49 cells from the START pool and biases the daily distribution permanently to fix a number. The new floor is enforced by construction on every cell and proven exhaustively (Story 172, 49/49), and the worst case improves from 2 to 6. RNG stream disclosure: v2 center-cell days skip 50 draws, so the skeleton draws shift relative to the v1 counterfactual; deterministic, v2 days only. Named limitation: pre-cutoff days are frozen on v1 and are not reproducible under v2.

## Deviation D1 (2026-11-27, jakebot ruling, same weight as the named limitation)

The v1 path's 50-draw exhaustion fallback is now `farthestCorner`, not point reflection plus the `{r:1, c:7}` mask, because the contract required both old constructs deleted from the derivation. Effect: 278 of 1501 sampled pre-cutoff days (D=20000..20784) differ in EXIT or guard-shifted skeleton from v0.60.0, e.g. D=20008 candidate EXIT (7,7) vs base (5,5). D=20784 is unaffected (7 draws, never exhausts) and pre-cutoff days are not re-derivable in the product: `deriveTriple` has exactly one call site, `todayD`. This sits alongside the named limitation, not beneath it: pre-cutoff days are frozen on v1 and are not reproducible under v2, and v1 days are not all byte-identical to v0.60.0 on the exhaustion path.

## What would change the decision

Harness evidence that farthest-corner argmax fails the floor of 6 on any of the 49 cells, or playtest evidence that the shorter center-day separations break the daily habit, reopens the floor value. Any retune above 6 requires a new geometry proof first. Decided by Rook, next TRACE session at the earliest.
