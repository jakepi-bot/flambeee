# Story 172: TRACE proof harness v2 (Session 74, P0b)

**Status:** Ready for development (Session 74, 2026-11-27).
**Author:** Quinn, Business Analyst.
**Priority:** P0b (the proof half of the session; the floor is only real if the harness proves it on every cell).
**Assigned to:** **Kai**, sole code owner. File: `dev/trace-proof.py` only. Zero website bytes.
**Base commit:** `5d4a7a9` (main, v0.60.0).
**Scope:** Six legs: exhaustive 49-cell mirror proof (primary), v1/v2 boundary pair, determinism 200/200, reachability 200/200, RED anchor against `5d4a7a9`, live-page browser leg. Exit discipline unchanged: PASS 0, FAIL 1, RED 2, SKIP 3.
**Design contract:** `flambeee-team/design-handoff.md`, Section 0 (amendment and cutoff) and Section 2 (Story 172, subsections 2.1 through 2.8). Design-owned observable criteria live in contract subsection 2.7 and are mapped here one for one.
**Non-blocking rule:** If headless Chromium cannot drive all 49 cells, the browser leg covers today plus at least one center-START day, and the exhaustive 49-cell proof lives in the mirror leg. If the wave runs short, Story 171 ships alone with this story named as the follow-up and the release notes state the proof is sampled again, not exhaustive.
**Note:** This story supersedes Session 73 Story 169's sampled determinism as the primary proof. Story 169 checked 200 day seeds and shipped the RED; sampling is not accepted as the primary proof here. The 49-cell exhaustive sweep is the primary leg; determinism and reachability 200/200 stay only as secondary regressions.

## Summary

Last session's harness checked a sample of days and the contract line slipped through anyway: 23 of 200 days were below the floor. Sampling days cannot prove a floor that must hold on every cell. This story rebuilds the harness around an exhaustive sweep: for each of the 49 interior START cells the Python mirror derives the v2 EXIT and asserts distance at least 6, START never equals EXIT, and all 3 skeleton cells sit apart from both. Around that core it keeps the old 200/200 determinism and reachability legs warm, pins the v1/v2 boundary on both sides of Day 20785, proves the harness itself is honest by going RED against the old fallback, and reads the real triple out of the live page in a browser for today plus at least one center-START day. Sampling days is demoted to a secondary leg, never the verdict.

## Story

As the team, I run one harness that proves the distance floor on every START cell instead of a sample of days, so the amended criterion ships on evidence, not on hope.

## Functional requirements

FR-1 (contract 2.1, leg 1, primary). Exhaustive 49-cell mirror proof. For each of the 49 interior cells: mirror v2 EXIT, assert manhattan >= 6, assert EXIT != START, assert all 3 skeleton cells are disjoint from both. 49/49 required. One miss fails the leg. This leg replaces sampling as the primary proof.

FR-2 (contract 2.1, leg 2, boundary). D = 20784 derives v1 byte-identical to the `5d4a7a9` triple; D = 20785 derives v2. Both asserted exactly. Catches a cutoff off by one and any change to the START draw call count.

FR-3 (contract 2.1, legs 3 and 4, secondary). Determinism 200/200 kept from Session 73: 200 seeded strokes forged twice, byte-identical wall sets. Reachability 200/200 kept: D = 20785 + i for 200 days, v2 triple, seeded synthetic stroke plus RING and CROSS fixtures, BFS START to EXIT within 80 moves.

FR-4 (contract 2.1, leg 5, RED anchor). The distance assertion run against the `5d4a7a9` tree (old point-reflection fallback) must exit RED 2 naming the fallback. Proves the harness fails the old code, not itself.

FR-5 (contract 2.1, leg 6, browser). Headless Chromium loads the actual page (never the mirror): read the derived triple for today's D and for at least one center-START day, assert the page triple equals the mirror v2 triple and distance >= 6. Minimum coverage if a full 49-cell browser drive is infeasible: today plus one center day. Triple read via JS evaluation after load; no screenshots, no timing asserts.

FR-6 (contract 2.4, absence discipline). Missing anchor commit object: the RED leg prints SKIP loudly and the verdict is SKIP 3, never PASS by omission. Missing browser binary: the browser leg alone prints SKIPPED loudly and exits 3 while the mirror legs still gate. Zero website bytes touched by this story.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 2.7; AC-1 through AC-5 map them directly. AC-6 pins the remaining normative behavior above.

1. Given the v2 tree, when the harness runs, then it exits PASS 0 printing `49/49 cells >= 6`, `200/200 determinism`, and `200/200 reachability`.
2. Given the `5d4a7a9` tree, when the distance leg runs against it, then it exits RED 2 naming the point-reflection fallback.
3. Given D = 20784, when either implementation derives, then the triple equals the v0.60.0 triple exactly; given D = 20785, when either derives, then the triple follows v2.
4. Given headless Chromium with the v2 page loaded on a center-START day, when the page triple is read, then it equals the mirror triple with distance >= 6.
5. Given a missing browser binary, when the harness runs, then the browser leg prints SKIPPED loudly and the verdict is SKIP 3 while the mirror legs still report.
6. Given the harness source, when inspected, then the primary floor verdict comes from the 49-cell sweep, not from a day-seed sample, and no file under `website/` changed.

## Out of scope (NOT DOING)

No website bytes. No change to exit discipline (PASS 0, FAIL 1, RED 2, SKIP 3). No new legs beyond the six named. No screenshots or timing asserts in the browser leg. No weakening of any threshold: 49/49, 200/200, and the boundary pair are absolute, one miss fails the leg.

## Dependencies

Depends on: Story 171 (same session; the mirror must match Riven's argmax order and first-wins tie-break exactly, or the boundary and browser legs catch it). If this story slips the wave, Story 171 ships alone and the release notes state the proof is sampled again, not exhaustive.

## Notes

Normative source is contract Section 0 (amendment, cutoff, RNG disclosure) and Section 2 (subsections 2.1 legs, 2.2 formulas, 2.3 tuning constants all living in `dev/trace-proof.py`, 2.4 edge cases, 2.5 failure modes, 2.6 Plan B, 2.7 design acceptance criteria, 2.8 rationale). Fixed values: PROOF_CELLS 49, DETERMINISM_RUNS 200, REACHABILITY_RUNS 200, V1_DAY 20784, V2_DAY 20785, ANCHOR_COMMIT `5d4a7a9`, BROWSER_MIN_DAYS 2. Rationale from contract 2.8: the 49-cell sweep covers the entire START space so no day seed can violate the floor; sampling is what shipped the RED.
