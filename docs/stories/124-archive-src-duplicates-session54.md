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
