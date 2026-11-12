# Story 134: Archive the src/ duplicates and wordpress mockup, retarget every live reference (Session 59, P0)

**Status:** Ready for development (Session 59, 2026-11-12).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P0 (the only build story tonight; the whole feature slot).
**Assigned to:** **Kai**, sole owner. No other dev touches these paths.
**Base commit:** `3a60d21` (main, v0.49.0).
**Design contract:** `flambeee-team/design-handoff.md`, Session 59, Section E (Rook; the contract wins on states, paths, and gates).
**Session plan:** `flambeee-team/session-plan.md`, Session 59 (2026-11-12), priorities item 1.
**Tracked by:** Backlog item M-1, issue #213. **This story closes issue #213. It supersedes PR #232, which the dev wave closes unmerged** (its base predates the manifest and v0.49.0; rebase is not the job).

## Summary

The project keeps two copies of several game pages: the live copies under `website/`, which players actually receive, and older duplicates under `src/`, frozen for weeks, plus a wordpress mockup that was never deployed. The real risk is human: a future editor fixes the wrong copy and ships nothing. This story moves the whole `src/` tree and the whole `wordpress/` tree under `archive/` by rename, points every live reference at the new location, and proves the move worked with one number: the Cinder script family counts 19 members before the move and 19 after. Nothing players see changes. No version is cut.

## Files

Moves first (renames only, no content edits):

| Source | Destination | Contents |
|---|---|---|
| `src/` (whole directory) | `archive/src-games/` | 8 duplicate pages and data files plus 11 proof scripts, 19 files total |
| `wordpress/` (whole directory) | `archive/wordpress/` | `home-mockup.html`, `preview/` |
| (new) | `archive/src-games/README.md` | One line: what the directory holds and that it is frozen |
| (new) | `archive/wordpress/README.md` | One line: what the directory holds and that it is frozen |

Consumer edits second (19 files; exact lines in Rook E2/E4 at `3a60d21`):

| File | Lines at base | Change |
|---|---|---|
| `scripts/run-cinder-family.py` | 5, 115 | Docstring scan roots and `discover()` pointer move to `archive/src-games/` |
| `src/kai-story*.py` (11 proof scripts) | usage lines (033:28, 035:16, 037:20, 040:43-44, 042:84-85, 044:78-79, 045:41-42, 047:64-65, 051:53-54, 053:39, 066:12) | Usage text points at `archive/src-games/` |
| `src/kai-story066-notice-proof.py` | 47 | Baseline default becomes the pinned pre-move commit hex plus `:src/cinder.html` |
| `docs/test-plans/v0.4.0-logic-check.js` | 2, 8 | Comment and read path move to `archive/src-games/` |
| `docs/test-plans/v0.6.0-logic-check.js` | 3, 14, 54, 87, 95 | Comments and read path move to `archive/src-games/` |
| `docs/test-plans/v0.6.0-smoke-test.js` | 2, 84-85 | Comment and read paths move to `archive/src-games/` |
| `dev/capture-game-shots.py` | 5, 22-25 | Docstring and 4 read paths move to `archive/src-games/` |
| `dev/gen-words.py` | 5, 35 | Docstring and write path move to `archive/src-games/` |
| `generate-hard-words.py` | 4, 13 | Docstring and path move to a repo-relative `archive/src-games/` path (also fixes a stale absolute path) |
| `README.md` | 125 | Tree map line names `archive/src-games/` |

Zero bytes under `website/`. `CACHE_VERSION` stays 25. No other file.

## Functional acceptance criteria (what Kai must satisfy)

- FR-1. Land order: all consumer edits land while `src/` is still in place (S1), the family proves 19/19 there, and only then do the two renames run (S2).
- FR-2. The two moves are renames only. The only content diffs in the PR are the retarget lines above plus the two new one-line READMEs.
- FR-3. Family discovery reads 19 members at every state: 11 under `src/` plus 8 elsewhere before the move, 11 under `archive/src-games/` plus the same 8 after. A green run that counts 8 is a failure.
- FR-4. `git diff HEAD -- website/` is empty, the `website/sw.js` precache block hash equals the pre-move value, `CACHE_VERSION` reads 25, and the website currency checker exits 0.
- FR-5. Both reference sweeps return their defined-empty results (Rook E7 V4): no live `src/` pointer survives outside the stated frozen records and object-store refs.
- FR-6. Proof script 066 runs with no overrides, exits 0, and its baseline names the pinned pre-move commit hex, never a floating branch ref.
- FR-7. After the move, `ls src` fails (no resurrected directory); `archive/src-games` holds 19 files; `archive/wordpress` holds the mockup and `preview/`; both READMEs are exactly one line.
- FR-8. Revert path: on any red gate, reset to the recorded pre-move hash, confirm discovery reads 19 and the tree matches the pre-move state, record why, and stop. Never patch forward.

## Design criteria reference (Rook Section E, IDs only, not restated)

D134-1 (S1 discovery 19, 11 under `src/`), D134-2 (S1 full run equals main baseline), D134-3 (renames only), D134-4 (S2 discovery 19, 11 under `archive/src-games/`), D134-5 (S2 full run equals S1), D134-6 (website immutability plus currency checker), D134-7 (both sweeps defined-empty), D134-8 (066 exit 0 on pinned hex), D134-9 (dev-utility paths plus `ls src` fails), D134-10 (revert path).

## BDD acceptance criteria (plain language, one observable outcome each)

- AC-1. Given the branch with all retarget edits landed but `src/` not yet moved, when the family discovery count is printed, then it reads 19 with 11 under `src/` and 8 elsewhere. (D134-1; `scripts/run-cinder-family.py:115`)
- AC-2. Given that same pre-move branch, when the full unfiltered family runs, then discovery reads 19 and the pass set matches the pre-move main baseline exactly, with no new failures and no silent skips. (D134-2)
- AC-3. Given the pre-move branch is green, when both renames run, then the status shows renames only and the only content changes are the retarget lines plus the two new READMEs. (D134-3)
- AC-4. Given the move has run, when the discovery count is printed, then it reads 19 with 11 under `archive/src-games/`, 0 under `src/`, and the same 8 elsewhere. (D134-4; `scripts/run-cinder-family.py:115`)
- AC-5. Given the moved tree, when the full unfiltered family runs, then discovery reads 19 and the pass set matches the pre-move branch run exactly. (D134-5)
- AC-6. Given the verified head, when the website check runs, then no byte differs under `website/`, the precache block hash matches the pre-move value, the cache version reads 25, and the currency checker exits 0. (D134-6; `website/sw.js:21`)
- AC-7. Given the verified head, when the two reference sweeps run, then both return their defined-empty results and anything printed is a missed live reference that fails the story. (D134-7)
- AC-8. Given the verified head, when proof script 066 runs with no overrides, then it exits 0 and its baseline names the pinned pre-move commit hex, not a floating ref. (D134-8; `src/kai-story066-notice-proof.py:47`)
- AC-9. Given the verified head, when the three dev-utility paths are read and the old directory is listed, then all three point under `archive/src-games/`, none under bare `src/`, none under `website/`, and listing `src` fails. (D134-9; `dev/capture-game-shots.py:22-25`, `dev/gen-words.py:35`, `generate-hard-words.py:13`)
- AC-10. Given any red gate, when the branch resets to the recorded pre-move hash, then discovery reads 19 and the tree matches the pre-move state, with the reason recorded in the session note. (D134-10)

## Required proof

- V1 discovery counts at four states (main, pre-move branch, post-move, head): 19 / 19 / 19 / 19, with the 11-member block changing directories and the 8-member block identical.
- V2 full unfiltered family at pre-move branch and at head: discovery 19 every run, pass sets exactly equal. Filtered reruns never count.
- V3 website immutability: empty website diff, precache hash equal, cache version 25, currency checker exit 0.
- V4 both reference sweeps defined-empty per the exact commands in Rook E7.
- V5 proof 066 standalone at the new path: exit 0, baseline names the pinned hex.
- V6 tree shape: `ls src` fails, 19 files under `archive/src-games`, mockup plus `preview/` under `archive/wordpress`, both READMEs one line.
- The PR body records: pre-move commit hash, post-move commit hash, both discovery prints, the currency checker result, and the sha256 of the moved tree.

## Out of scope

Any byte under `website/`; any `CACHE_VERSION` change; Stories 135 and 136 (they touch the manifest generator, which is frozen as the measuring instrument until this move merges); regenerating the manifest artifacts (frozen pre-move evidence); any version cut or tag; any claim that the move makes games faster, smaller, or cleaner to play.

## Definition of done

V1 reads 19/19/19/19; V2 pass sets exactly equal; V3 green; V4 both sweeps defined-empty; V5 exit 0 on the pinned hex; V6 tree shape holds; website diff empty; PR body carries both hashes, both discovery prints, checker result, and tree hash; PR #232 closed unmerged; issue #213 closed after verification with the family count in the closing comment.
