# Story 124: Archive src/ duplicate game copies and wordpress mockup (Session 57 refresh, Ready to build)

## Session 57 refresh (2026-11-10)

**Status:** Ready to build.
**Author:** Quinn, Business Analyst.
**Scope:** Story 124 only. Correction per design-handoff E124-7: the Session 54 header line "Same PR also carries Story 125" is stale and withdrawn. Story 125 is not in this scope, and no PR carries both stories.
**Priority:** P1. Backlog item M-1 (issue #213).
**Assigned to:** Kai, sole code owner. Only code story today.
**Base:** `b918475` (main, Session 56 docs merge).
**Design contract:** `flambeee-team/design-handoff.md`, Session 57, Story 124 sections 0-7. The contract wins on structure and proof detail.

### Measured blast radius at b918475 (design-handoff classes A through I)

Story 127 (Session 55, merged `c078685`) retargeted the 19-script Cinder proof family and the three Afterglow dev proofs to live `website/` bytes after Story 124 was written. The Session 54 table below the history line is stale in both directions: four rows are already complete, and files that never made the table now need classification. Rook's snapshot at `b918475`, using Story 124 section 3's exact command: 364 hits total, 322 in `docs/`, 42 across 13 code files. Quinn re-runs and classifies; these numbers are a starting point, not the record.

| Class | Measured at `b918475` | Disposition |
|---|---|---|
| A. Live working-tree paths to moved files | `dev/capture-game-shots.py` lines 22-25: `src/wordfire.html`, `src/minesweeper.html`, `src/simon.html`, `src/2048.html` | retarget to `archive/src-games/`, as the Session 54 table says |
| B. Live path missing from the Session 54 table | `dev/gen-words.py` line 35 opens `src/wordfire-words.js` for write; root `generate-hard-words.py` line 13 has `SRCJS` pointing at a stale absolute path | `gen-words` must be retargeted or it raises `FileNotFoundError` after the move; `generate-hard-words` is already broken by an unrelated stale absolute path, so record it under requirement 2 and do not fix it in this PR |
| C. Family discovery rule, new since Session 54 | `scripts/run-cinder-family.py` `discover()` (lines 113-117) scans `repo/src/` and `docs/test-plans/` plus root `scout-qa-session*.py` | must also scan `archive/src-games/`, or the M-4 Cinder family silently shrinks 19 to 8 scripts while the runner still exits 0. A green gate that proves 11 fewer scripts is the worst failure in this story because nothing red ever appears |
| D. Moving-ref git object reads | 10 occurrences of `main:src/cinder.html` or `origin/main:src/cinder.html` across 8 `src/kai-story*.py` files, plus `docs/test-plans/session27-story054-qa.py` line 57 `REF` defaulting to `"main"` used at line 139 | retarget the 10 kai-family refs to `archive/src-games/cinder.html`; the immutable tag and commit pins (`77acd25` `CONTROL_PIN`, `v0.21.0` through `v0.24.0`) are left alone |
| E. Immutable git object reads | `v0.21.0`, `v0.22.0`, `v0.23.0`, `v0.24.0:src/cinder.html`, `77acd25:src/cinder.html` (`CONTROL_PIN`), `feature/<branch>:src/cinder.html` | no action: they resolve against immutable trees and survive the move |
| F. Rows already completed by Story 127 | `dev/afterglow-proof.py`, `dev/afterglow-daily-proof.py`, `dev/afterglow-060-residual.py`, `scout-qa-session19-032.py` all have 0 `src/` hits at `b918475` | retire those four Session 54 rows and record the retarget as already done |
| G. Row that must not be followed as written | `scout-qa-session24.py` line 422 reads `v0.21.0:src/cinder.html` via `git show` (immutable tag) | no change: retargeting it to the archive path would break a tag read. Classify as immutable |
| H. Historical prose and provenance comments | 322 `docs/` hits (22 in `docs/roadmap.md`, the rest stories and test plans), `website/games/cinder.html` lines 426, 442, 465, 517, `dev/capture-game-shots.py` line 5 docstring, `run-cinder-family.py` line 5 rule text, `docs/test-plans/v0.6.0-logic-check.js` comments | leave untouched, list every one in the PR's grep table with a one-line historical reason |
| I. Gaps in the Session 54 grep command itself | the pattern set omits `src/wordfire-words.js`, bare `src/` paths, and any `wordpress/` path other than `home-mockup`. Broader scan of bare `src/` in code files outside `docs/` and `src/`: 5 files, 12 hits | Quinn broadens the pattern before declaring zero unclassified live references; a zero count from a narrow pattern is not a proof |

Run-time discovery rule (from the runner's own docstring, line 5) reads "a file is in the family iff it ends in .py, it lives under src/ or docs/test-plans/ or matches scout-qa-session*.py at the repo root". That sentence is itself a live reference to `src/` and belongs in class C.

Layout before (measured at `b918475`): `src/` holds exactly 19 files: 7 HTML (`2048.html`, `afterglow.html`, `cinder.html`, `index.html`, `minesweeper.html`, `simon.html`, `wordfire.html`), `wordfire-words.js`, and 11 `kai-story*-proof.py` scripts. `wordpress/` sits at the repo root with `home-mockup.html` and `preview/`. Layout after: `src/` gone (or empty and deleted), `archive/src-games/` holds the same 19 files by `git mv` plus `README.md`, `archive/wordpress/` holds the mockup and preview images plus `README.md`, `archive/README.md` exists. Transitions are `git mv` only so history follows; no content edit to any moved file; no edit under `website/`; tooling path constants updated in place; then the grep proof runs at head.

Structural values this PR must not move (not tunable): `CACHE_VERSION` 23 on main at `b918475` (24 if PR #230 merges first), unchanged by this PR with zero diff on that line (`website/sw.js` line 21); `PRECACHE_URLS` 8 game entries, byte-identical; `GAME_ORDER` 6 entries, byte-identical (`website/index.html` line 1169).

### Acceptance criteria (A124-1 through A124-7, from the contract, which wins)

- **A124-1.** Given the repo at head, when `git diff <base> -- website/` is run, then it is empty; when `website/sw.js` is read, then `PRECACHE_URLS` is byte-identical to base and `CACHE_VERSION` has no diff line. Zero served bytes changed.
- **A124-2.** Given each of the 19 `src/` files plus the `wordpress/` mockup and preview images, when `git rev-parse <base>:<old-path>` and `git rev-parse <head>:<new-path>` are run, then the blob hashes are equal for every file: byte-identical, not "looks the same".
- **A124-3.** Given `website/index.html` at head, when every `href="games/*.html"` is resolved against a served `website/` tree, then all 8 unique Play links resolve to `website/games/*.html` (8 unique at base `b918475`, count unchanged) and `GAME_ORDER` is byte-identical.
- **A124-4.** Given the broadened grep from section 2 class I, when it is run at head and its output is pasted in the PR, then every hit carries a class (A through I) and a one-line reason, and the count of unclassified live references is 0.
- **A124-5.** Given `scripts/run-cinder-family.py` at head, when discovery output is printed, then it reports 19 family scripts, the same set as at base. A count of 8 fails even with exit 0.
- **A124-6.** Given `archive/src-games/`, when `git log --follow archive/src-games/cinder.html` is run, then history traces through the move (`git mv`, not copy-delete), and each archive directory carries its README.
- **A124-7.** Given the repo at head, when `ls src/` is run, then no duplicate game HTML remains there, and root `wordpress/` no longer holds the mockup or preview images.

### Verification plan (V1 through V7, from the contract, which wins)

Deterministic, hash-based, no randomness, no seeds, no simulated rounds.

| # | Run | Pass threshold |
|---|---|---|
| V1 | Inventory counts before and after: 19 files in `src/` -> 19 in `archive/src-games/` plus 3 READMEs; `wordpress/` 2 entries -> same content under `archive/wordpress/` | exact counts, 0 missing, 0 extra |
| V2 | Blob hash pairs for every moved file: `git rev-parse` old path at base against new path at head (19 + 2 = 21 pairs) | 21/21 equal, 0 unequal |
| V3 | `website/` byte diff against base, plus `sw.js` line-level read | 0 changed files, 0 changed lines in `CACHE_VERSION` or `PRECACHE_URLS` |
| V4 | Link check on a served tree at head and at base | 8/8 unique `games/` hrefs resolve at base, 8/8 at head, 0 broken |
| V5 | Grep proof at head, run 3 times to confirm the count is stable on a static tree | stable count each run, 0 unclassified live references, table pasted in the PR |
| V6 | Family runner discovery count at base and at head | 19 == 19, exit code semantics unchanged (0/1/2/3 per the runner docstring) |
| V7 | Spot execution: `python3 dev/afterglow-proof.py` (or its documented invocation) at head, output pasted in the PR | resolves its source and runs; file has 0 `src/` hits |

Plan B (unhappy path, from the contract): if a runnable harness cannot be made green because of an unrelated pre-existing break, do not fix it here. Record the break, its pre-existing status, and the exact command in the PR. If class C cannot be updated in the same PR, the PR does not merge: shipping the move without the discovery rule is a silently weaker M-4 gate, which is worse than deferring the story to the next LEGACY day.

Open questions carried from the contract: (1) classes B and C are not in the Session 54 table; if Quinn's re-measure agrees they enter Story 124 as two extra path-constant rows owned by Kai, else the PR names which class is out of scope and why; (2) class D disposition is retarget the 10 moving reads to `archive/src-games/cinder.html` (Rook's recommendation) with tag and commit pins left alone, or record them as accepted-stale with the cost stated; (3) the broadened class I pattern must appear in the PR body.

---

## Session 54 history (kept below this line, superseded by the refresh above)

# Story 124: Archive src/ duplicate game copies and wordpress mockup (Session 54, P1b, repo hygiene)

**Status:** **Deferred** (Session 54, 2026-11-07, jakebot advisory). Prepared and ready for the next LEGACY day; do not build in Session 54.
**Author:** parent overseer (Wave 2 absorbed; see session-plan.md process incident).
**Priority:** P1b. Backlog item M-1 (issue #213).
**Assigned to:** **Kai**, sole owner. Same PR also carries Story 125. No other dev touches these paths.
**Design contract:** none (no player-facing mechanic). Acceptance is structural.

## Summary

`src/` holds a second copy of six game files frozen since 2026-10-18, plus a stale hub page. The live deploy root has been `website/` since Session 31 and nothing serves `src/`. The risk M-1 names is real: a future editor fixes the wrong copy and ships nothing. Move the duplicates under `archive/` with one-line READMEs, retarget the tooling that still points at the old paths, and prove by grep that no live reference remains.

## Measured blast radius at Session 54 planning (02:00-02:10 CST)

Files in `src/`: `2048.html` (454 lines), `afterglow.html` (657), `cinder.html` (1754), `index.html` (271), `minesweeper.html` (786), `simon.html` (605), `wordfire.html` (1093), `wordfire-words.js`, and 11 `kai-story*-proof.py` scripts.

References to `src/<game>.html` outside `src/`, by class:

| File | Kind | Required action |
|---|---|---|
| `dev/capture-game-shots.py` (lines 23-25) | live tooling | retarget to new archive paths |
| `dev/afterglow-proof.py` | live harness | retarget `src/afterglow.html` |
| `dev/afterglow-daily-proof.py` | live harness | retarget `src/afterglow.html` |
| `dev/afterglow-060-residual.py` | harness, already stale absolute path (`/home/jake/.openclaw/...`) | retarget to the repo-relative archive path |
| `scout-qa-session19-032.py` (lines 13, 26) | historical proof, runnable | retarget to `archive/src-games/cinder.html` |
| `scout-qa-session24.py` | historical proof, runnable | retarget to the archive path |
| `docs/roadmap.md` (many entries) | historical record | leave; list in the PR as historical prose |
| `website/games/cinder.html` comments (lines 426, 442, 465, 517) | origin notes in code comments | leave; they are provenance notes, not paths |

Definition used by this story: **live reference** = anything executed, served, precached, loaded by the site, or read by a harness or tool at run time. Historical prose in `docs/roadmap.md` and provenance comments are records and are allowed, but every one of them must be listed in the PR's grep table.

## Requirements

### 1. Layout

```
archive/
  README.md                      # one paragraph: what this is, why it exists, the live tree is website/
  src-games/
    README.md                    # one line per file: "archived duplicate of website/games/<name>.html as of <date>"
    2048.html afterglow.html cinder.html index.html minesweeper.html simon.html wordfire.html wordfire-words.js
    (the 11 kai-story*-proof.py scripts move here too, unchanged)
  wordpress/
    README.md                    # "WordPress home mockup, never deployed; live site is website/index.html"
    home-mockup.html
    preview/*.png
```

- `src/` must not remain as a directory with loose duplicates. If the move leaves nothing, delete the empty directory.
- Use `git mv` so history follows the files.
- Do not edit the archived HTML files. They are frozen artifacts; editing them would break the byte-provenance that earlier proofs rely on.

### 2. Tooling retarget

Every file in the table above that is runnable gets its path constant updated to the archive location. No other change to those files. If a harness cannot run because of an unrelated pre-existing break, record that in the PR rather than fixing it.

### 3. Grep proof

The PR body carries a table from a real command run at head, for example:

```
grep -rn "src/cinder\.html\|src/afterglow\.html\|src/2048\.html\|src/minesweeper\.html\|src/simon\.html\|src/wordfire\.html\|src/index\.html\|wordpress/home-mockup" \
  --include="*.py" --include="*.js" --include="*.html" --include="*.json" --include="*.md" .
```

Every remaining hit is classified as live or historical with a one-line reason. Zero unclassified live hits is the pass bar.

### 4. Site unaffected

- `PRECACHE_URLS` in `website/sw.js` unchanged (it never listed `src/`). No cache bump in this PR.
- `website/index.html` unchanged. `GAME_ORDER` unchanged. All Play links still resolve to `website/games/*.html`.
- No file under `website/` is touched by this PR.

## Acceptance criteria (BDD)

1. Given the repo at head, when `ls src/` runs, then no duplicate game HTML remains there.
2. Given the repo at head, when `ls archive/src-games/` runs, then all six game HTML files, `index.html`, `wordfire-words.js`, and the 11 proof scripts are present.
3. Given `git log --follow archive/src-games/cinder.html`, when run, then history traces back through the move (git mv, not copy-delete).
4. Given each archive directory, when listed, then a README exists with the one-line description.
5. Given the grep command in section 3, when run at head, then every hit is classified and no live reference to a removed path remains.
6. Given `python3 dev/afterglow-proof.py` (or the harness's documented invocation), when run at head, then it resolves its source file and executes, with the output pasted in the PR.
7. Given `git diff 1ea559f -- website/`, when run, then the diff is empty.
8. Given `grep -c "games/" website/sw.js` semantics, when `PRECACHE_URLS` is read, then the 8 game entries are unchanged.
9. Given `wordpress/`, when listed, then the mockup and preview images are gone from it and present under `archive/wordpress/`.

## Out of scope

Deleting history, rewriting `docs/roadmap.md`, editing archived HTML content, touching any `website/` file, the play counter (Riven owns it), M-2 content (Story 125 owns the wording, same PR), Cinder's QA harness run.
