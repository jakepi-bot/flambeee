# Story 127: Game proof family retarget plus one runner

**Status:** Ready for development (Session 55, 2026-11-08).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1b (tooling repair; makes the M-4 gate enforceable, unblocks #215 Cinder half and #213).
**Assigned to:** **Kai**, sole code owner (Story 048 protocol).
**Base commit:** `1d3a7bc`.
**Design contract:** `flambeee-team/design-handoff.md`, Section 2.
**Source:** M-4 (#216); session plan Section "The defect that sets this session's second story".

## What it is

The 19-script Cinder proof family proves a frozen duplicate instead of the live game file, so the M-4 rule (no Cinder edit merges without a recorded full-family proof run) cannot be satisfied honestly today. This story repoints every family script at the live file, removes dead absolute paths and dead worktree references, ships one runner that discovers and executes the family with honest exit codes, and applies the same repointing to the three Afterglow dev proofs that currently prove stale bytes on the exact file Story 126 ships. Own PR, tooling only, no product code, no cache bump, does not ride the release commit.

## Files

Group A, the 19-script Cinder family (path constants and target file only):

| # | File |
|---|---|
| 1 | `src/kai-story033-pure-read-proof.py` |
| 2 | `src/kai-story035-pure-read-proof.py` |
| 3 | `src/kai-story037-badge-proof.py` |
| 4 | `src/kai-story040-pure-read-proof.py` |
| 5 | `src/kai-story042-streak-proof.py` |
| 6 | `src/kai-story044-questlog-streak-proof.py` |
| 7 | `src/kai-story045-reload-guard-proof.py` |
| 8 | `src/kai-story047-questlog-readpath-proof.py` |
| 9 | `src/kai-story051-away-window-proof.py` |
| 10 | `src/kai-story053-record-normalize-proof.py` |
| 11 | `src/kai-story066-notice-proof.py` |
| 12 | `docs/test-plans/session22-story040-qa.py` |
| 13 | `docs/test-plans/session26-story050-qa.py` |
| 14 | `docs/test-plans/session26-story051-qa.py` |
| 15 | `docs/test-plans/session27-story053-qa.py` |
| 16 | `docs/test-plans/session27-story054-qa.py` |
| 17 | `docs/test-plans/session27-story055-qa.py` |
| 18 | `scout-qa-session19-032.py` |
| 19 | `scout-qa-session24.py` |

Group B, the three Afterglow dev proofs (path constants and default target only):

| # | File |
|---|---|
| 20 | `dev/afterglow-proof.py` |
| 21 | `dev/afterglow-daily-proof.py` |
| 22 | `dev/afterglow-060-residual.py` |

New runner plus the already-dirty cleanup edit:

| # | File |
|---|---|
| 23 | `scripts/run-cinder-family.py` (new file, stdlib only, executable) |
| 24 | `docs/test-plans/035-cinder-recent-quests-streak.md` (the pre-existing uncommitted cleanup edit is committed in this PR, text only, nothing else) |

Target file for Group A defaults to `website/games/cinder.html`; Group B defaults to `website/games/afterglow.html`. No file under `website/` is modified by this story.

## Baseline measured at Session 55 planning (base `1d3a7bc`)

| Check | Value |
|---|---|
| Family size | 19 scripts (11 under `src/`, 6 under `docs/test-plans/`, 2 `scout-qa-session*.py` at root) |
| Literal `src/cinder.html` references across the 19 | 86 |
| Reads of `website/games/` across the 19 | 0 |
| Dead absolute path refs | present (plan sweep vs file-scoped re-measurement differ on counts; see Open questions; acceptance is zero remaining either way) |
| `src/afterglow.html` vs live | 657 lines vs 705 lines in `website/games/afterglow.html`; the dev Afterglow proofs prove stale bytes |
| `src/cinder.html` vs live | byte-identical today only because `src/` was frozen; the first live Cinder edit makes every proof stale |

## Out of scope

Any edit to `website/games/cinder.html`, `website/games/afterglow.html`, `website/sw.js`, or any game file (revert on sight); Cinder play counter (#215 second half); `src/` archival (#213); new games, FPS, Apps, website index or `GAME_ORDER` changes; PRs #206/#208/#211/#212/#217; `pending-post.txt`, release notes, BLOG.md, website What's New; `dev/capture-game-shots.py` and the `render-*.py` art generators (not proofs); installing a browser inside a harness run; editing game code to make a proof pass.

## Functional acceptance criteria (BDD, plain language)

1. **Scenario: Full family runs green on the real tree.** Given the repointed family at the repo root with a browser available, when the runner is invoked with no filters, then every discovered script runs, each reports a pass, the final line reads "family: N/N scripts passed" with the discovered count, and the runner exits 0.
2. **Scenario: Repeat runs agree.** Given a green run just completed, when the runner is invoked a second time with nothing changed, then it exits 0 again with the identical script list and count.
3. **Scenario: A broken copy is caught.** Given a temporary copy of a live game file with one small break introduced, when the runner is pointed at that copy, then at least one script reports failure, the log names it, and the runner exits nonzero.
4. **Scenario: No proof reads the frozen duplicate.** Given the repointed family, when the scripts are searched for reads of the frozen duplicate paths used as the file under test, then none remain (labeled historical-base comparisons via `git show` excepted and listed in the PR).
5. **Scenario: No dead paths remain.** Given the repointed family, when the scripts are searched for the dead workspace root, the dead virtual-environment path, and the dead temporary worktree path, then none remain.
6. **Scenario: One failure does not hide the rest.** Given one script forced to fail, when the runner completes, then it exits with the any-fail code, the failure line names the script with its reason, and every remaining script still ran.
7. **Scenario: Runner errors are honest.** Given zero discoverable scripts, a missing target file, or bad arguments, when the runner is invoked, then it exits with the runner-error code and prints the reason rather than claiming a pass.
8. **Scenario: Filtered reruns are labeled.** Given a debugging rerun with include/exclude filters, when it completes, then its use is recorded in the PR body and it is never presented as the full family run; the M-4 record cites an unfiltered run.
9. **Scenario: Afterglow proofs point at the live file.** Given the three Afterglow dev proofs with no arguments and no environment overrides, when each is invoked once, then each tests the live game file and its exit code is recorded in the PR body; a nonzero exit is recorded as a known failure with reason, owner, and follow-up, never fixed by editing the game file.
10. **Scenario: Tooling only.** Given this story's diff, when the file list is inspected, then no file under `website/` is modified and the service worker cache version is unchanged.
11. **Scenario: More than three non-path failures stops the line.** Given over three scripts failing for reasons unrelated to paths, when Kai has recorded each with its output, then Kai stops, posts the log, and the parent re-scopes rather than editing paths until green.

## Design acceptance criteria (from Rook's contract, do not restate new numbers)

Observable design checks live in `flambeee-team/design-handoff.md`, Section 2.10 (Scenarios A through H) with the acceptance run matrix in Section 2.11. This story does not re-state their numeric thresholds; the dev and QA runs satisfy them as written:

- Scenario A (real tree green, unfiltered, final N/N line) and Scenario B (mutation red on a temp copy, log names the failing script).
- Scenario C (zero stale artifact reads, historical-base lines excepted and listed) and Scenario D (zero dead paths).
- Scenario E (idempotent consecutive runs) and Scenario F (honest any-fail exit, no short-circuit).
- Scenario G (no product touch, cache version unchanged) and Scenario H (Group B defaults resolve under the live file, exits recorded).
- Acceptance run matrix: the minimum five recorded runs (two consecutive green, one mutation, one forced failure, the two zero-count greps) with command, exit code, discovered count, and target hash in the PR body, which is the M-4 record for this change.

## Per-script checklist

No pattern-doc table applies to this story. The substitute is the runner's own discovery output: every run prints the discovered count and the sorted member list, the per-script PASS/FAIL lines, and the aggregate verdict line, all pasted into the PR body with the target hash. A missing or renamed script shows as a changed discovery count with a written explanation, never silence.

## Open questions

1. Dead-path file counts: the plan sweep cites one set of counts and the contract's file-scoped re-measurement cites a smaller set. The gap is sweep scope (companion docs and helpers vs exactly the 19 `.py` files), not substance. Kai's runner discovery scan tiebreaks; acceptance is zero remaining either way.
2. Mutation choice: whether the negative-control demo breaks a token in a temp Afterglow copy or in a temp Cinder quest-log copy depends on which family scripts cover Afterglow pure functions. Kai picks per contract Section 2.5 and records the mutation, the command, and the nonzero exit; both variants satisfy the contract.
3. Port allocation assumes a free base per the contract's tuning table; if the box holds that range, Kai moves the base within the table bounds and records the value. No design impact.
4. A script that legitimately reads a historical base revision via `git show` stays in the family, labeled with the documented variable name, excluded from the zero-count, and listed in the PR body; if `git show` fails, that script fails with reason, never skips silently.
5. Non-path failures follow Plan B (contract Section 2.9): record script name, reason, and first lines of output, mark KNOWN_FAIL with owner and follow-up story, keep the runner exit nonzero. A red gate with a named owner is honest; a green gate with a hidden skip repeats the defect this story exists to kill.
