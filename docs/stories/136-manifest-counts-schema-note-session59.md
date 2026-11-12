# Story 136: Manifest counts-versus-consumers schema note (Session 59, P2, CONTRACT ONLY, not built tonight)

**Status:** Contract only (Session 59, 2026-11-12). Story file written, nothing built.
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (builds in a later LEGACY window, after the M-1 move merges).
**Assigned to:** **Kai** (later). Touches `dev/src-consumer-manifest.py`, which is frozen tonight as the measuring instrument for Story 134 and must not change until the move merges.
**Base commit:** `3a60d21` (main, v0.49.0).
**Design contract:** `flambeee-team/design-handoff.md`, Session 59, Section G (Rook; the contract wins on the invariant sentence and the self-assertion).
**Session plan:** `flambeee-team/session-plan.md`, Session 59 (2026-11-12), priorities item 3.
**Tracked by:** Issue #238.

## Summary

The manifest holds two different tallies that look comparable but are not. One tally counts distinct file paths by their highest-action kind; the other lists one row per matching line, so a single file with several hits contributes several rows. A reader who sums the rows and compares them to the path counts concludes the generator miscounts, when the schema is correct and only its documentation is missing. This story writes the missing sentence in the three places a reader stands, and makes the generator check its own arithmetic before writing. Specified tonight, built later.

## Files (when built, later window only)

| File | Change | Owner |
|---|---|---|
| `dev/src-consumer-manifest.py` | Help text plus emitted JSON `description` field plus markdown header sentence, and one self-assertion over its own rows. No kind relabeling, no recount, no taxonomy change. | Kai |

Nothing else. Generated artifacts update through the generator only, never by hand.

## The arithmetic at the generation base

At the manifest generation base: 26 runnable rows plus 140 historical rows plus 27 needs-a-decision rows equals 193 consumer rows, against counts of 14 runnable plus 32 historical plus 12 needs-a-decision equals 58 distinct paths. The row total exceeds the path total because many paths contribute multiple hit lines. Equality is not expected.

## Functional requirements

- FR-1. The generator help, the JSON top-level `description` field (new, one sentence), and the markdown artifact header each state the same invariant: counts are distinct paths by highest-action kind, consumers is one row per hit line, so the consumer length meets or exceeds the counts sum and equality is not expected.
- FR-2. The markdown header states the same invariant plus the worked example from its own rows (at the generation base, 26 plus 140 plus 27 equals 193).
- FR-3. The generator asserts over its own labeled rows that the consumer length equals the runnable plus historical plus needs-a-decision row tallies, and on mismatch exits nonzero naming the mismatch without writing either artifact.

## BDD acceptance criteria (plain language, one observable outcome each)

- AC-1. Given the generated JSON, when a reader opens it, then a one-sentence description states the distinct-paths versus per-hit-line invariant clearly enough that no reader mistakes the counts for a row sum. (D136-1)
- AC-2. Given the markdown artifact, when a reader opens it, then its header states the same invariant plus the worked example computed from its own rows. (D136-2)
- AC-3. Given a scratch copy of the generator with one consumer row duplicated (never in the repo), when it runs, then it exits nonzero and writes neither artifact. (D136-3)

## Out of scope

Relabeling any kind, recounting history, changing the taxonomy (counts stay distinct-paths-by-highest-kind; the note explains the schema, it does not redesign it); any change to the generator before the M-1 move merges.

## Definition of done (later window)

AC-1 through AC-3 recorded pass or fail in the later PR body; the worked example matches the artifacts' own rows; no website bytes.
