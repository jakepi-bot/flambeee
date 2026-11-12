# Story 135: Manifest generator refuses a linked git worktree (Session 59, P2, CONTRACT ONLY, not built tonight)

**Status:** Contract only (Session 59, 2026-11-12). Story file written, nothing built.
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (builds in a later LEGACY window, after the M-1 move merges).
**Assigned to:** **Kai** (later). Touches `dev/src-consumer-manifest.py`, which is frozen tonight as the measuring instrument for Story 134 and must not change until the move merges.
**Base commit:** `3a60d21` (main, v0.49.0).
**Design contract:** `flambeee-team/design-handoff.md`, Session 59, Section F (Rook; the contract wins on the fail-loud rule).
**Session plan:** `flambeee-team/session-plan.md`, Session 59 (2026-11-12), priorities item 3.
**Tracked by:** Issue #237.

## Summary

The manifest generator reads the checkout it stands in but labels its output with a commit that may belong to a different checkout. Run inside a linked git worktree, it can therefore write a manifest that mislabels its own base: a complete-looking record built from the wrong tree. The contract rules that a mislabeled manifest is worse than none, so the generator must refuse loudly instead of guessing. This story is specified tonight and built later.

## Files (when built, later window only)

| File | Change | Owner |
|---|---|---|
| `dev/src-consumer-manifest.py` | Worktree detection plus fail-loud exit path only. No scan, taxonomy, or schema change. | Kai |

Nothing else. No artifact, website, or test-plan file changes in the later PR beyond what the generator itself writes.

## Functional requirements

- FR-1. When the target directory sits inside a linked worktree, the generator exits 1, names the worktree root and its resolved git directory, and creates or modifies neither artifact file.
- FR-2. In the main checkout, behavior is byte-identical to today: exit 0, identical artifacts, base commit equal to the current HEAD.
- FR-3. A target that is not a repo at all keeps its existing exit 2 misuse path, distinct from the worktree exit 1.

## BDD acceptance criteria (plain language, one observable outcome each)

- AC-1. Given a linked worktree of the repo at any commit, when the generator runs against a directory inside it, then it exits 1, names the worktree root and the resolved git directory, and neither artifact file is created or changed. (D135-1)
- AC-2. Given the main checkout with no tree change, when the generator runs twice, then both runs exit 0, both artifact pairs are byte-identical, and the recorded base commit equals the current HEAD. (D135-2)
- AC-3. Given a target directory that is not a repo at all, when the generator runs against it, then it exits 2 exactly as today. (D135-3)

## Open question, for the next LEGACY window

Issue #237's own Expected line asks for generation to work from a linked worktree. Rook's contract rules the opposite: fail loud, exit 1, write nothing. Both options are on the table for the build window:

- Option A (as the issue asks): transparent worktree support, resolving the worktree to its state and labeling the output correctly.
- Option B (as the contract rules): fail loud, exit 1, write nothing.

Rook's reasoning: a manifest that mislabels its own base is worse than none, and PR #232 already failed twice on understated sets, so a partial or mislabeled manifest must never read as complete. This matches the generator's existing exit-1-and-write-nothing behavior for a missing or unreadable scan root. When this story is built, the issue's acceptance will need rewording to whichever option the window chooses.

## Out of scope

Resolving the worktree to its main checkout and scanning that instead; bare-repo support; any taxonomy or schema change (that is Story 136); any change to the generator before the M-1 move merges.

## Definition of done (later window)

AC-1 through AC-3 recorded pass or fail in the later PR body; main-checkout output byte-identical to pre-change behavior; no website bytes; open question above resolved and the issue acceptance reworded to match.
