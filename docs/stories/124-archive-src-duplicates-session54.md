# Story 124: Archive the src/ duplicate game copies and the wordpress mockup (Session 57 refresh, P1, repo hygiene)

**Superseded by Story 134 (Session 59, 2026-11-12).**

**Status:** **Deferred three times, refreshed and ready.** Deferred Session 54 (2026-11-07, jakebot advisory, prepared and held; record `5ae6a4f`), deferred Session 55 (Story 127 took the window, `c078685`), deferred Session 56 (the release carrier took the window). Refreshed against base `b918475` for Session 57, 2026-11-10. **Ready for the 01:55 dev wave.** If it is not green by 02:40, leave the PR open and let the release ship without it; **it is mergeable after the release tag if it runs late.**
**Author:** Quinn (Business Analyst), Session 57 refresh. Session 54 draft by the parent overseer.
**Priority:** **P1.** Backlog item M-1, issue #213.
**Assigned to:** **Kai**, sole owner, one PR. No other dev touches these paths.
**Base commit for measurement:** `b918475`. The story file itself now sits on `c384cd2` (PR #231), which changed only `docs/stories/`, so every code measurement below is still valid; the prose counts will drift and V5 re-runs the sweep at head.
**Design contract:** `flambeee-team/design-handoff.md`, Story 124 sections 0-7 (Rook; structural declaration, no player mechanic).
**Session plan:** `flambeee-team/session-plan.md`, Session 57 (2026-11-10), priorities item 2, file ownership table, handoff to the 01:55 dev wave.
**Dependencies:** None. Zero `website/` bytes means no conflict with the frozen carriers PR #230 (`204bb7d`) or PR #229 (`be55a43`).
**Open dev PR:** #232 (`feat/session57-124-archive-src`) is building this story. This refresh completes the measurement that the merged first draft explicitly deferred to Quinn and names three gaps that PR #232 has not yet covered.
**Scope correction:** the Session 54 header claimed Story 125 rode this same PR. It does not. Story 124 is the whole PR.

## Summary

`src/` holds a second copy of seven game pages and a stale hub, frozen since 2026-10-18, plus 11 proof scripts. The live deploy root has been `website/` since Session 31 and nothing serves `src/`. M-1 (#213) names the real risk: a future editor fixes the wrong copy and ships nothing. This story moves the duplicates under `archive/` with one-line READMEs, retargets every runnable reference that points at the old paths, fixes the Cinder family discovery rule so the M-4 gate does not silently shrink, and proves by a broadened grep that zero unclassified live references remain.

There is no player-facing mechanic. No state, no formula, no tuning constant, no balance to simulate, no onboarding beat. Any change to what a player sees at any URL is a failure of this story, not a feature of it.

## Files

| File | Change |
|---|---|
| `archive/src-games/**` | New. All 19 `src/` files moved here by `git mv`, plus a one-line README. |
| `archive/wordpress/**` | New. `home-mockup.html` plus 6 `preview/*.png` moved here by `git mv`, plus a one-line README. |
| `archive/README.md` | New, one paragraph: what this is, why it exists, the live tree is `website/`. |
| `src/**`, `wordpress/**` | Removed by move, not copy-delete. Delete the directory if the move empties it. |
| `scripts/run-cinder-family.py` | `discover()` scans `archive/src-games/` as well as `src/`, `docs/test-plans/`, and root `scout-qa-session*.py`. Line 5 rule text updated to match. Nothing else. |
| `dev/capture-game-shots.py` | Path constants only, lines 22-25 (line 5 docstring is class H, listed not edited). |
| `dev/gen-words.py` | Path constants only, line 35 (line 5 docstring is class H). |
| `README.md` | Line 125 only, the tree diagram line. |
| `docs/test-plans/v0.4.0-logic-check.js`, `v0.6.0-logic-check.js`, `v0.6.0-smoke-test.js`, `v0.7.0-check.js`, `v0.8.0-check.js`, `v0.9.0-check.js` | Read lines only, named in the class table. |
| `docs/test-plans/session27-story054-qa.py` | `REF` default at line 57 and the `git show REF:src/cinder.html` read at line 139, path strings only. |
| `src/kai-story040/042/044/045/047/051/053/066-*.py` (8 files) | The 10 `main:src/cinder.html` and `origin/main:src/cinder.html` string constants retargeted to the archive path. No test logic. |

Nothing under `website/`. No new file outside `archive/`. No code beyond path constants.

## Measured blast radius at base `b918475` (re-run by Quinn for this refresh, not copied)

Two commands were run against the clean tree at `b918475`. The first is Story 124 section 3's original command. The second is broadened, because a zero count from a narrow pattern is not a proof.

**Command 1, the Session 54 pattern:**

```
grep -rn "src/cinder\.html\|src/afterglow\.html\|src/2048\.html\|src/minesweeper\.html\|src/simon\.html\|src/wordfire\.html\|src/index\.html\|wordpress/home-mockup" \
  --include="*.py" --include="*.js" --include="*.html" --include="*.json" --include="*.md" .
```

Result: **364 hits. 322 in `docs/`. 42 across 13 code files.** Independently confirmed, matching Rook's snapshot exactly. It is also provably incomplete: it never matches `src/wordfire-words.js`, never matches a path built as `path.join(..., "src", "2048.html")`, and never matches a bare `src/`.

**Command 2, the broadened sweep (the one this story accepts):**

```
grep -rn "src/" . --exclude-dir=.git --exclude-dir=__pycache__
grep -rnE "['\"]src['\"]" . --exclude-dir=.git --exclude-dir=__pycache__
grep -rn "wordpress" . --exclude-dir=.git --exclude-dir=__pycache__
```

Result: **532 unique hits.** 458 in `docs/`, 51 inside `src/` (the files referring to themselves), 23 elsewhere. Classification below.

Layout before, measured: `src/` holds exactly **19** files (7 HTML `2048`, `afterglow`, `cinder`, `index`, `minesweeper`, `simon`, `wordfire`; `wordfire-words.js`; 11 `kai-story*-proof.py`). `wordpress/` holds **7** files (`home-mockup.html` plus 6 preview pngs). `archive/` does not exist yet. Last commit to touch `src/` is `c078685` (Story 127, 2026-11-08), which is why the Session 54 table is stale.

### Classification table (every hit carries a class and a one-line reason; zero unclassified live hits)

| Class | What it is | Measured at `b918475` | Disposition |
|---|---|---|---|
| **A. Live path constants in dev tooling** | `dev/capture-game-shots.py` lines 22, 23, 24, 25 open `src/wordfire.html`, `src/minesweeper.html`, `src/simon.html`, `src/2048.html` | 4 executable hits (line 5 is a docstring, class H) | Retarget to `archive/src-games/`. Behavior preserving: it screenshots the same frozen bytes it screenshots today. |
| **B1. Live write target** | `dev/gen-words.py` line 35 opens `src/wordfire-words.js` for **write** | 1 executable hit (line 5 docstring, class H) | Retarget. Otherwise the next run recreates `src/` and the duplicates come back (E124-4). |
| **B2. Live readers in runnable docs scripts, new since Session 54** | `docs/test-plans/v0.4.0-logic-check.js:8` reads `path.join(__dirname, "..", "..", "src", "2048.html")`; `v0.6.0-logic-check.js:95` reads `src/wordfire-words.js`; `v0.6.0-smoke-test.js:84,85` read `src/wordfire-words.js` and `src/wordfire.html`; `v0.7.0-check.js:14` sets `ROOT = path.join(__dirname, "..", "..", "src")` and reads `2048`, `minesweeper`, `simon`, `wordfire`, `index` through it; `v0.8.0-check.js:10,11,12,72,73,74` read `src/wordfire.html`, `src/minesweeper.html`, `src/index.html`; `v0.9.0-check.js:10,72` read `src/wordfire.html` | 15 executable hits across 6 files | **Retarget the read lines.** These are `#!/usr/bin/env node` scripts with a printed `Run:` instruction. They work today and throw `ENOENT` the moment the move merges, which makes them a break this story causes, not a pre-existing one. |
| **B3. Live structural claim** | `README.md` line 125 shows `src/ (code, managed by Kai & Riven)` in the repo tree diagram | 1 hit | Update the one line. It is the repo's own map of the live tree and it becomes false on merge. |
| **B4. Family member with a moving primary read** | `docs/test-plans/session27-story054-qa.py`: `REF = os.environ.get("REF", "main")` at line 57, read at line 139 `git show %s:src/cinder.html` | 7 hits (line 139 is the load-bearing read; 141, 146, 167, 168 interpolate the same ref; 24 and 56 are comments) | Retarget the default to the archive path. This file is **one of the 19 family members**, so leaving it breaks the M-4 run rather than a stray script. |
| **B-stale. Already broken by an unrelated cause** | `generate-hard-words.py` line 13 `SRCJS` points at a stale absolute `/home/jake/.openclaw/workspace/flambeee/src/wordfire-words.js` | 2 hits (lines 4, 13) | Record as accepted-stale in the PR with the exact command. Do not fix here (requirement 2). |
| **C. Family discovery rule** | `scripts/run-cinder-family.py` `discover()` lines 113-117 scan `repo/src/` and `docs/test-plans/` plus root `scout-qa-session*.py`; line 115 is `os.path.join(repo, "src")`; line 5 states the same rule in prose | 2 hits plus the function body | **Must also scan `archive/src-games/`.** See the measured before/after below. |
| **D. Moving git object reads** | 10 occurrences of `main:src/cinder.html` or `origin/main:src/cinder.html` across 8 `src/kai-story*.py` files (`040:74`, `042:80,115`, `044:163`, `045:97`, `047:145`, `051:141`, `053:106`, `066:14,47`), plus class B4 above | 10 in `src/` plus 7 in the test plan | Retarget to the archive path. Two of these are not merely degraded, see open question 2. |
| **E. Immutable git object reads** | `v0.21.0` through `v0.24.0:src/cinder.html` (15 in `src/`, 8 in `docs/test-plans/`), `77acd25:src/cinder.html` (`CONTROL_PIN`, `run-cinder-family.py:40`), five `feature/<branch>:src/cinder.html` pins | 24 hits | No action. They resolve against immutable trees and survive the move. |
| **F. Rows already completed by Story 127** | `dev/afterglow-proof.py`, `dev/afterglow-daily-proof.py`, `dev/afterglow-060-residual.py`, `scout-qa-session19-032.py` | 0 `src/` hits each, confirmed by re-run | Retire those four Session 54 rows and record the retarget as already done at `c078685`. |
| **G. Row that must not be followed as written** | `scout-qa-session24.py:422` reads `v0.21.0:src/cinder.html` via `git show` | 1 hit | No change. Retargeting it to the archive path would break a tag read. Classified immutable. |
| **H. Historical prose, provenance, and documentation strings** | 419 `docs/*.md` hits (roadmap, stories, test plans); `website/games/cinder.html` lines 426, 442, 465, 517, 789; `work-session-prompt.md:167`; `dev/fps-probe/VERDICT.md:11`; comment-only lines `v0.4.0:2`, `v0.5.0:3,14,47`, `v0.6.0-logic-check:3,14,54,87`, `v0.6.0-smoke:2`, `session27-story055-qa.py:96`; usage lines `python3 src/kai-story*.py` (17 hits inside the scripts that move); `capture-game-shots.py:5`, `gen-words.py:5`, `session26-story051-qa.py:7` | 490 hits | Leave untouched. Every one is listed in the PR's grep table with a one-line historical reason. None is executed: the family runner invokes scripts by path, never by their docstring. |
| **I. Gaps in the Session 54 grep command itself** | The pattern omits `src/wordfire-words.js`, the `path.join(..., "src", ...)` component form, any `wordpress/` path other than `home-mockup`, and bare `src/`. That omission hid all 15 of class B2 and the README claim | n/a | This is why command 2 exists. A zero count from command 1 is not a proof; command 2's output is pasted in the PR body. |
| **J. False positives, excluded with a reason** | `website/manifest.webmanifest` lines 11 and 17 are icon `"src"` keys, not repo paths; `src/kai-story037-badge-proof.py:241` is `{"src": SRC}`, a format key; `brand/render-logos.py` uses `src` as a loop variable | 3 hits | Excluded. Listed in the PR so the exclusion is visible rather than silent. |

Live hits: 4 (A) + 1 (B1) + 15 (B2) + 1 (B3) + 7 (B4) + 2 (C) + 10 (D) = **40**. Accepted-stale: 2. Historical, immutable, and false positives: 490. Sum: **532. Unclassified live hits: 0.**

### The `discover()` fix, with a measured before and after

`discover()` was executed against the real tree at `b918475`: **19 family scripts**.

Simulated on a scratch tree with `src/` removed and no fix: **8 scripts** (`docs/test-plans/session22-story040`, `session26-story050`, `session26-story051`, `session27-story053`, `session27-story054`, `session27-story055`, plus `scout-qa-session19-032.py` and `scout-qa-session24.py`), exit code semantics unchanged, so the runner still exits 0. With `archive/src-games/` added to the scan list: **19 scripts**.

**19 before, 8 without the fix, 19 with it.** A green gate that proves 11 fewer scripts is the worst failure available in this story because nothing red ever appears. It gets its own acceptance line (A124-5).

The 19 at base: 6 under `docs/test-plans/`, 2 root `scout-qa-session*.py`, and 11 `src/kai-story033/035/037/040/042/044/045/047/051/053/066-*.py`.

## Requirements

### 1. Layout

```
archive/
  README.md                 # one paragraph: what this is, why it exists, live tree is website/
  src-games/
    README.md               # one line per file: "archived duplicate of website/games/<name>.html as of <date>"
    2048.html afterglow.html cinder.html index.html minesweeper.html simon.html wordfire.html
    wordfire-words.js
    (the 11 kai-story*-proof.py scripts move here too)
  wordpress/
    README.md               # "WordPress home mockup, never deployed; live site is website/index.html"
    home-mockup.html
    preview/*.png           # 6 png files, unchanged
```

- `src/` must not survive as a directory of loose duplicates. If the move leaves nothing, delete the directory.
- **`git mv`, not copy and delete.** History must follow the files.
- Do not edit the archived HTML, JS, or png files. They are frozen artifacts; editing them breaks the byte provenance earlier proofs depend on.

### 2. Retarget every runnable reference

Every class A, B1, B2, B3, B4, C, and D row gets its path constant updated to the archive location. No other change to those files. Docstrings, usage lines, provenance comments, and historical prose (class H) are not edited; they are listed.

If a harness cannot run because of an unrelated pre-existing break, record the break, its pre-existing status, and the exact command in the PR. Do not fix it here. The one known case is `generate-hard-words.py`.

If a dev holds this PR to a narrower path scope than the table above, the remaining rows do not silently disappear: each is written into the PR's class table as accepted-stale with the reason, a named follow-up story, and an owner. **Leaving a live hit unlisted is the failure mode this story exists to kill.**

### 3. Fix the family discovery rule

`scripts/run-cinder-family.py` `discover()` must scan `archive/src-games/` in addition to `src/`, `docs/test-plans/`, and root `scout-qa-session*.py`. Update the line 5 rule text to match. Discovery count must print **19 at base and 19 at head**. Exit code semantics (0/1/2/3) unchanged.

If class C cannot be updated in the same PR, the PR does not merge. Shipping the move without the discovery rule is a silently weaker M-4 gate, which is worse than deferring the story to the next LEGACY day.

### 4. Grep proof

The PR body carries both commands' output: the Session 54 pattern for comparison with the old table, and the broadened three-pattern sweep, which is the one this story accepts. Every hit is classified A through J with a one-line reason. **Zero unclassified live hits is the pass bar.**

### 5. Site unaffected

- `git diff <base> -- website/` is empty. Zero served bytes changed.
- `PRECACHE_URLS` in `website/sw.js` byte-identical. It never listed `src/`.
- `CACHE_VERSION` unchanged by this PR, zero diff on that line. It reads 23 on main at `b918475` and 24 if PR #230 merges first; either way this PR does not touch it. **No cache bump in this PR.**
- `GAME_ORDER` byte-identical. All 8 unique Play links still resolve to `website/games/*.html`.

### 6. Structural constants that must not move

| Name | Value at base | Required after | Location |
|---|---|---|---|
| `CACHE_VERSION` | 23 on main at `b918475`, 24 if #230 merges first | unchanged, zero diff on that line | `website/sw.js` line 21 |
| `PRECACHE_URLS` | 8 game entries, never listed `src/` | byte-identical | `website/sw.js` |
| `GAME_ORDER` | 6 entries | byte-identical | `website/index.html` line 1169 |

## Acceptance criteria (BDD)

1. **Given** the repo at head, **when** `ls src/` runs, **then** no duplicate game HTML remains there and the directory is gone if the move emptied it.
2. **Given** the repo at head, **when** `ls archive/src-games/` runs, **then** all 7 HTML files, `wordfire-words.js`, and the 11 proof scripts are present, and `archive/README.md`, `archive/src-games/README.md`, and `archive/wordpress/README.md` each exist with their one-line description.
3. **Given** `git log --follow archive/src-games/cinder.html`, **when** run, **then** history traces back through the move, proving `git mv` and not copy-delete.
4. **Given** each moved file, **when** `git rev-parse <base>:<old-path>` and `git rev-parse <head>:<new-path>` are run, **then** every file this story does not retarget has equal blob hashes, and every file it does retarget shows a diff confined to the named path strings with no test logic changed. Byte-identical is not "looks the same".
5. **Given** the repo at head, **when** `git diff <base> -- website/` runs, **then** the diff is empty; **when** `website/sw.js` is read, **then** `PRECACHE_URLS` is byte-identical to base and `CACHE_VERSION` has no diff line.
6. **Given** `website/index.html` at head, **when** every `href="games/*.html"` is resolved against a served `website/` tree, **then** all 8 unique Play links resolve and `GAME_ORDER` is byte-identical to base.
7. **Given** the broadened three-pattern sweep, **when** it is run at head three times and its output is pasted in the PR, **then** the count is stable on a static tree, every hit carries a class A through J with a one-line reason, and the count of unclassified live references is **0**.
8. **Given** `scripts/run-cinder-family.py` at head, **when** discovery output is printed, **then** it reports **19** family scripts, the same set as at base. **A count of 8 fails even when the runner exits 0.**
9. **Given** `dev/capture-game-shots.py`, `dev/gen-words.py`, the six `docs/test-plans/*.js` checks, `docs/test-plans/session27-story054-qa.py`, `README.md`, and the 8 `src/kai-story*.py` files at head, **when** each is run or read, **then** it resolves its source under `archive/src-games/` and no longer references a path that no longer exists.
10. **Given** `generate-hard-words.py` at head, **when** its status is recorded in the PR, **then** it is listed as accepted-stale with its pre-existing stale absolute path, the exact command, and the statement that this PR did not cause or fix it.
11. **Given** `wordpress/`, **when** listed, **then** the mockup and the 6 preview images are gone from it and present under `archive/wordpress/`.
12. **Given** the merged diff of this story, **when** it is inspected, **then** the file list is exactly the `archive/` tree, the `src/` and `wordpress/` removals, and the path-constant retargets named above, with no file under `website/` changed.
13. **Given** the PR body, **when** read, **then** it states the measured narrow count (364), the broadened count (532), the discovery counts (19 / 8 / 19), and the class table, in plain punctuation with no em dashes.

## Verification plan

Deterministic, hash-based. No randomness, no seeds, no simulated rounds.

| # | Run | Pass threshold |
|---|---|---|
| V1 | Inventory counts before and after: 19 files in `src/` to 19 in `archive/src-games/` plus 3 READMEs; `wordpress/` 7 files to the same content under `archive/wordpress/` | exact counts, 0 missing, 0 extra |
| V2 | Blob hash pairs for every moved file, `git rev-parse` old path at base against new path at head | frozen artifacts equal; retargeted tooling differs only on the named path lines |
| V3 | `website/` byte diff against base, plus a line-level read of `sw.js` | 0 changed files, 0 changed lines in `CACHE_VERSION` or `PRECACHE_URLS` |
| V4 | Link check on a served tree at head and at base | 8/8 unique `games/` hrefs resolve at both, 0 broken |
| V5 | Grep proof at head, run 3 times to confirm the count is stable on a static tree | stable count each run, 0 unclassified live references, table pasted in the PR |
| V6 | Family runner discovery count at base and at head | 19 == 19, exit code semantics unchanged (0/1/2/3) |
| V7 | Spot execution: `python3 dev/afterglow-proof.py` at head, output pasted in the PR | resolves its source and runs; file has 0 `src/` hits |

Plan B, unhappy path: if a runnable harness cannot be made green because of an unrelated pre-existing break, do not fix it here. Record the break, its pre-existing status, and the exact command in the PR.

## Out of scope

Deleting history, rewriting `docs/roadmap.md`, editing archived HTML or png content, touching any `website/` file, the play counter (M-3, #215), M-2 content and Story 125, the seven Cinder-family content-drift failures, fixing `generate-hard-words.py`, `scripts/verify-website-currency.sh`, `pending-post.txt`, BLOG.md, release artifacts, and PRs #206, #208, #211, #212, #217. Release carriers PR #230 at `204bb7d` and PR #229 at `be55a43` are frozen and are verified, never edited.

## Risks and degrade path

Risk 1: the move merges without the `discover()` fix and the M-4 gate silently proves 8 scripts instead of 19 while exiting 0. Path: A124-8 is a hard gate; if class C cannot land in the same PR, do not merge.

Risk 2: an editor touches an archived copy and byte provenance dies invisibly. Path: hash pairs in A124-4, caught only by hash, never by eye.

Risk 3: a runnable reference outside the sweep's scope breaks after merge. Path: three patterns over the whole tree, including `docs/`. The first draft of this story's sweep stopped at `docs/` and therefore missed six runnable node scripts; that is the exact defect class I exists to name.

Risk 4: collision with the carrier. Path: zero `website/` bytes means no conflict with #230. If it is not green by 02:40, the release ships without it. It has no release dependency by design.

## Open questions

1. **Class D and the hash invariant.** The contract's A124-2 and V2 as written require all 19 moved `src/` files to keep equal blob hashes, but retargeting class D edits 8 of them. The two requirements cannot both hold. Resolution already in flight: PR #232 reports "18/26 byte-equal, 8/26 differ only by the 10 retargeted ref lines", which is the honest split Quinn asked for. This story now states the split as the requirement (A124-4) rather than a flat equality. Owner: Kai, settled.

2. **Two class D reads are fatal, not degraded.** The contract calls the kai family's moving refs "degraded rather than fatal" because they sit behind `LIVE_DEFAULT`. That is true for `resolve_source()`, but two scripts read the moving ref **unconditionally in `main()`**: `src/kai-story042-streak-proof.py:926` (`git_show(MAIN_REF)`) and `src/kai-story066-notice-proof.py:410` (`git_show(BASELINE_REF)`, default `origin/main:src/cinder.html`). Both print `BLOCK: could not read ...` and **exit 2** once the move merges. Story 127's commit message records "historical git-show base comparisons kept and labeled", which was correct then and is a live break now. Quinn's requirement was to retarget both; PR #232 does. Recorded here so the reasoning survives.

3. **Three gaps in PR #232's path scope.** #232 scopes its broadened scan to code files outside `docs/` and states "No docs/ file is executed by any live path." That is not correct: six `docs/test-plans/*.js` files are node scripts with printed run instructions and they read out of `src/`. Alongside them, `session27-story054-qa.py` (a family member) was recorded accepted-stale with the note that it is outside the PR's path scope, and `README.md:125` was classed historical when it is a live layout claim. Quinn's requirement: either retarget all three groups in #232, or list each in #232's class table as accepted-stale with a named follow-up story and an owner. Unclassified is the only unacceptable outcome. Owner: Kai, with Quinn on the classification.

4. **`capture-game-shots.py` target choice.** Archive paths are behavior preserving: it screenshots the same frozen bytes it screenshots today. Pointing it at `website/games/` would change what it captures. Quinn's requirement: archive paths. Live behavior would be a separate story.

## References

- `flambeee-team/session-plan.md`, Session 57 (2026-11-10): priorities item 2, file ownership table, handoff to the 01:55 dev wave, merge-after-tag rule.
- `flambeee-team/design-handoff.md`, Session 57 (Rook): Story 124 structural declaration, classes A through I, A124-1 through A124-7, V1 through V7, open questions 1 through 3.
- `docs/stories/127-proof-family-retarget-session55.md`: the retarget that made the Session 54 table stale, and the "historical git-show base comparisons kept and labeled" decision this story revisits.
- Issue #213 (M-1). Deferral record: Session 54 commit `5ae6a4f`, roadmap note at `b787067`, held through Sessions 55 and 56.
