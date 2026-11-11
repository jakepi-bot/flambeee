# Story 131: Generated src consumer manifest for the M-1 archive (Session 58, P1, must get done)

**Status:** Ready for development (Session 58, 2026-11-11).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (the one item that must get done tonight; the archive cannot be attempted a fourth time without it).
**Assigned to:** **Kai**, sole owner. No other dev touches these files.
**Base commit:** `f029493`.
**Design contract:** `flambeee-team/design-handoff.md`, Session 58, Section B (Rook; the contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 58 (2026-11-11), priorities item 2.
**Tracked by:** Session 58 plan, Story 131. Unblocks issue #213 (M-1 archive) and protects issue #216 (M-4 family QA rule).

## Summary

Two attempts to tidy one old folder failed because the team underestimated how many scripts still point at it: the real count is 14 runnable scripts, 2.3 times the six the last attempt planned for, and one of them defines the script family the quality rule measures. This story does not move the folder. It builds a small program that scans the live project and writes down every pointer to that folder, with file names and line numbers, sorted into what runs today, what is only history, and what needs a decision. The next archive attempt then works from a complete list instead of a guess. No game or site file changes at all.

## Files

| File | Change | Owner |
|---|---|---|
| `dev/src-consumer-manifest.py` | New generator, stdlib only, `--repo DIR` optional (default is the enclosing repo). | Kai |
| `dev/src-consumer-manifest.json` | Generated artifact, machine-readable record. Never hand-edited; a hand edit is a defect. | Kai |
| `dev/src-consumer-manifest.md` | Generated artifact, human-readable table with the same rows as the JSON. Never hand-edited. | Kai |

Zero bytes under `website/`. No cache bump. One PR.

## Functional requirements

### 1. Generator stages (B1)

- FR-1. SCAN: walk the fixed roots (repo root `scout-qa-session*.py`, `src/`, `docs/test-plans/`, `dev/`, repo-root `*.py`, `README.md`, `docs/roadmap.md`, `scripts/run-cinder-family.py`), collect files by extension, record repo-relative paths with line numbers for every `src/` or `kai-story` hit.
- FR-2. CLASSIFY: exactly one label per row from the B3 taxonomy; ambiguous rows are `needs-a-decision`, never silently dropped.
- FR-3. EMIT: rows sorted by path then line, fixed schema, no timestamps; two consecutive runs on an untouched tree produce byte-identical files.
- FR-4. The generator is a pure function of the tree plus `git show` for `git-show` classification. No network, no clock reads, no absolute paths in output.
- FR-5. Coverage floor: all 14 runnable consumers outside `src/`, all 38 files under `docs/test-plans/` that mention `src/`, `README.md:125`, and the `docs/roadmap.md` historical lines. Fewer than 14 runnable rows fails (a root went missing); a 15th consumer is scanned and reported, never hardcoded away.

### 2. Counts and determinism (B2)

- FR-6. Family arithmetic recorded verbatim: 19 members today, 11 of the 19 under `src/`, `19 - 11 = 8`, so removing `src/` without rewriting `discover()` shrinks discovery 19 to 8 with no error and no exit-code change.
- FR-7. Determinism: `sha256(run1) == sha256(run2)` for both artifacts on an untouched tree. No timestamps, no absolute paths, no author names, no run counters. Sort order is byte order on the repo-relative path, then ascending line number.
- FR-8. Exit codes: 0 means the manifest was written; 1 means a scan root is missing or unreadable (names the root, writes nothing); 2 means misuse (unknown flag, `--repo` not a repo).

### 3. JSON schema and taxonomy (B3)

- FR-9. Top level: `base_commit` (full hex of HEAD at generation), `generated_by` (fixed `dev/src-consumer-manifest.py`), `counts` (`runnable`, `historical`, `needs_decision`, `test_plan_files`, `family_total`, `family_under_src`; expected 14, remainder, remainder, 38, 19, 11), `consumers` (array, one row per hit, sorted by path then line).
- FR-10. Consumer row: `path` (repo-relative, forward slashes), `line` (1-based), `text` (matched line, trimmed, max 300 chars), `kind` (exactly one of `runnable`, `historical`, `needs-a-decision`), `reason` (one line: what breaks or does not break on archive, and the disposition). Zero rows lack `reason`.
- FR-11. `runnable now`: paths executed against the live tree today; disposition names the archive-step edit.
- FR-12. `historical-only git-show reference`: `src/` strings resolving against immutable objects (`v0.21.0` through `v0.24.0` tags, `77acd25` control pin, `feature/<branch>` pins, `main:src/...` inside archived `kai-story` scripts once moved); each row says why no edit is needed.
- FR-13. `needs-a-decision`: live references the archive step must retarget or explicitly accept as stale (the six `docs/test-plans/` node scripts from the #232 gate failure, `session27-story054-qa.py` with `REF=main`, `README.md:125`, live `dev/capture-game-shots.py` and `dev/gen-words.py` paths). Each row names the owning decision, never prose around it.

### 4. Family-definition change (B4)

- FR-14. The manifest names the `scripts/run-cinder-family.py` `discover()` rewrite (lines 113-130 at `f029493`) as a `needs-a-decision` row, with the before snippet (`src_dir` from `src`, `scan_dirs` filtering on existing dirs) and the after snippet (`src_dir` from `archive/src-games`, runner docstring line 5 updated from `src/` to `archive/src-games/`), the 19-to-8 arithmetic, and the exit-0 trap stated. Acceptance on the archive step (not tonight): discovery prints 19 at base and 19 at head, same set.

### 5. Edge cases (B6)

- FR-15. `base_commit` must equal `git rev-parse HEAD` at generation; a mismatch fails acceptance.
- FR-16. Absolute-path leakage (`/home/...`, `/tmp/...`) forbidden in both artifacts.
- FR-17. Timestamp leakage forbidden; `stat` plus `sha256sum` equality on a regenerated pair is the whole proof.
- FR-18. Ambiguous rows labeled by execution path, never double-counted.
- FR-19. `generate-hard-words.py` stale absolute `SRCJS` recorded as a pre-existing break in its row, not fixed here.
- FR-20. The manifest is evidence for the archive PR, never an allowlist: every `needs-a-decision` row must resolve to an edit or an explicit accepted-stale note in the archive PR body.

## BDD acceptance criteria (observable by running named measurements, never by reading source)

- AC-1. Given the repo at `f029493`, when the generator runs twice with no tree change, then both pairs are byte-identical (`sha256sum` equal per artifact) and `base_commit` reads the HEAD hex. (D131-M1)
- AC-2. Given the generated JSON, when `counts` is read, then `runnable` is 14, `test_plan_files` is 38, `family_total` is 19, `family_under_src` is 11, and every one of the 14 runnable paths appears in `consumers` with line numbers. (D131-M2)
- AC-3. Given the generated JSON, when all rows are read, then every row carries exactly one `kind` from the B3 strings, zero rows lack `reason`, and unlabeled hits are 0. (D131-M3)
- AC-4. Given the markdown artifact, when it is read beside the JSON, then it contains the same row count, the `run-cinder-family.py` family-definition rewrite with the 19-to-8 arithmetic, and the `README.md:125` plus `docs/roadmap.md` rows. (D131-M4)
- AC-5. Given both artifacts, when grepped for the home directory, `/tmp/`, and `2026-` timestamps, then hits are 0. (D131-M5)
- AC-6. Given the repo at the manifest head, when `git diff -- website/` runs, then it is empty and `website/sw.js` has no diff line. (D131-M6)
- AC-7. Given a reader who did not write the generator, when the under-10-minute checklist runs, then 4/4 hold: every `needs-a-decision` row names an owner and a disposition; the six node scripts from the #232 gate failure are each present; the 19-to-8 arithmetic appears with the exit-0 trap stated; no row says "etc." or "and others".

## Required proof

- V1 reproducibility: two consecutive generator runs on an untouched tree, exit 0 both times, 4/4 hashes matching. Commands: `python3 dev/src-consumer-manifest.py && sha256sum dev/src-consumer-manifest.json dev/src-consumer-manifest.md`, run twice, compare.
- V2 coverage count: 14 runnable rows, 38 test-plan files represented, `README.md:125` row present, roadmap rows present, family row with the B4 snippet present.
- V3 reader checklist 4/4, recorded as pass or fail in the PR body.

## Out of scope

The archive itself (moving `src/` anywhere); any edit to `scripts/run-cinder-family.py` tonight; any `website/` byte including the cache bump; fixing `generate-hard-words.py`; M-3 Cinder counter (#215); release artifacts; any use of the manifest as permission to skip rows.

## Definition of done

V1 passes 4/4 hashes with exit 0 both runs; V2 counts hold (14, 38, 19, 11); V3 checklist 4/4 recorded in the PR body; `git diff -- website/` empty; new files only, Kai sole owner; nothing hand-edited in either artifact.
