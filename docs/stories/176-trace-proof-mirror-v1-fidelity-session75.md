# Story 176: trace-proof mirror v1 fidelity (Session 75, P2, closes #303)

**Status:** Ready for development (Session 75, 2026-11-28).
**Author:** Quinn, Business Analyst.
**Priority:** P2 (cut first and entire; nothing of it rides along elsewhere).
**Assigned to:** **Kai**, sole code owner.
**Files touched:** `dev/trace-proof.py` only. Page bytes untouched.
**Depends on:** `flambeee-team/design-handoff.md` Section 3 (Session 75); shipped page `website/games/trace.html` lines 236-250 as the oracle; Session 74 floor-8 freeze for D <= 20784.

## Context

The audit mirror `derive_v1` kept the old point-reflection fallback while the shipped page moved to farthestCorner, so the mirror lies on exhausting pre-cutoff days (issue #303).
One fallback line plus one real exhausting day as a mirror-versus-page equality check restores the audit without touching the page.
This story is cut first if the wave runs short, and it closes #303.

## Functional requirements

FR-1 (mirror change). Mirror `derive_v1` exhaustion fallback becomes `farthestCorner(start)` with fixed corner order (1,1), (1,7), (7,1), (7,7), first wins ties, matching page `deriveTripleV1`. The v1 path keeps its 50-draw loop at the frozen floor 8 with NO precheck (the precheck belongs to v2 only). Draw accounting is unchanged: draws counts the initial draw plus loop redraws up to 50.
FR-2 (fidelity leg). New V1-FIDELITY leg for pre-cutoff exhausting day D=20008: assert mirror `derive_v1(20008)` equals page `deriveTripleV1(20008)` read by JS evaluation in the browser leg, and both equal the pinned triple START (3,3), EXIT (7,7), skeleton [(5,4),(5,5),(5,6)], draws 50, distance 8. D=20008 is verified exhausting under old semantics (50 draws, loop-exit distance 5, fallback fires).
FR-3 (no-move proof). The D=20784 boundary assertion is unchanged and stays green (draws 7, no exhaustion, triple identical to EXP_V1_20784), proving the fallback change touches only exhausting days. Full harness still exits 0 and `--red-anchor` still exits 2.
FR-4 (tuning). `V1_FIDELITY_DAY` 20008, `V1_MANHATTAN_MIN` 8 frozen, `MAX_EXIT_DRAWS` 50, `EXP_V1_20008` (3,3),(7,7),[(5,4),(5,5),(5,6)], `V1_DAY`/`V2_DAY` 20784/20785 locked, `ANCHOR_COMMIT` 5d4a7a9. All live in `dev/trace-proof.py`.
FR-5 (path and edges). The record must state the real-day path was used (3163 pre-cutoff days exhaust; the synthetic pure-function path is NOT used). D=20785 is untouched by this story. Page evaluation unavailable means V1-FIDELITY FAILs loudly, never passes by omission. Anchor-commit-missing keeps the existing SKIP 3 discipline.
FR-6 (forbidden moves). Adding a precheck to mirror v1 to match v2 style is forbidden; changing corner order or tie-break is forbidden; touching any website byte is forbidden (the release rejects it); recording the synthetic path when the real day was used is forbidden.

## Acceptance criteria (BDD, contract 3.7 verbatim)

1. Given the harness tree, when the full harness runs, then it exits 0 with all existing legs plus V1-FIDELITY green.
2. Given `--red-anchor`, when the harness runs, then it exits 2 exactly as before.
3. Given D=20008, when mirror `derive_v1` runs, then it returns START (3,3), EXIT (7,7), skeleton [(5,4),(5,5),(5,6)], draws 50.
4. Given D=20008, when the page `deriveTripleV1` is evaluated, then it equals the mirror triple exactly.
5. Given D=20784, when either implementation derives, then the triple equals EXP_V1_20784 exactly (no behavior change on non-exhausting days).
6. Given the story record, when read, then it names the real-day path with D=20008.

## Out of scope

OUT OF SCOPE: page bytes untouched (the release rejects any); no v2 change; no new v1 precheck; no corner-order change; the synthetic pure-function path is not used on this story.

## Proof required in the dev record

PROOF: paste the full-harness exit-0 line with V1-FIDELITY green, the `--red-anchor` exit-2 line, and one line stating the real-day path with D=20008.

## Notes

Normative source is contract Section 3 (3.1 states and transitions, 3.2 formulas, 3.3 tuning, 3.4 edge cases, 3.5 failure modes, 3.6 Plan B, 3.7 BDD, 3.8 rationale).
Plan B: if page evaluation cannot run (no browser), the mirror still asserts the pinned triple in pure Python and the equality is recorded as unverified under SKIP discipline; if D=20008 ever stops exhausting, pick the lowest exhausting pre-cutoff day and record the substitution.
Tie-break note: all corner orders agree on (7,7) at distance 8 for START (3,3), so the leg also asserts the pinned skeleton, which shifts on any stream change.
Cut order: this story is cut first and entire; nothing of it rides along inside another story.
