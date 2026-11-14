# Story 138: Manifest blind spot and three broken test-plan readers (Session 61, P0)

**Status:** Build-ready (Session 61, 2026-11-14).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P0 (only story this session, builds in the 01:55 dev wave).
**Assigned to:** **Kai** (backend/tooling, single owner, one PR). Riven peers the PR.
**Base commit:** `113e6af` (main, v0.50.0 SALTLINE).
**Design contract:** `flambeee-team/design-handoff.md`, Section H (Rook; the contract wins on regex, referents, exits, and thresholds).
**Session plan:** `flambeee-team/session-plan.md`, Session 61 (2026-11-14), P0 item.
**Tracked by:** Issue #241.

## Summary

Three test-plan readers broke when Story 134 moved `src/` to `archive/src-games/` on 2026-11-12. They still read the old paths and exit 1. The manifest generator broke the same day: its scan root `src` no longer exists, so it exits 1 and writes nothing, and both artifacts are frozen at base `09bb82d` describing a tree we no longer ship. On top of that, the generator has a blind spot: a component-form reference such as `path.join(ROOT, 'src', 'wordfire.html')` contains the quoted segment `'src'` and no `src/` literal, so the scanner filter at `dev/src-consumer-manifest.py:554` never sees it. The 193-row manifest holds zero rows for all three readers (measured `v070 rows: 0, v080 rows: 0, v090 rows: 0`). Retargeting the readers without fixing the scanner would make them vanish from the manifest and silently shrink its coverage while the artifacts still regenerate cleanly. This story fixes all three legs in one PR: retarget the readers, resolve the three `.openclaw` reads with stated substitutes, fix the generator per G1 through G8, and regenerate both artifacts in the same commit.

Tooling only. Zero website bytes. No `CACHE_VERSION` change. No `RUNNABLE_FLOOR` change.

## Files (one PR, Kai)

| File | Change | Owner |
|---|---|---|
| `docs/test-plans/v0.7.0-check.js` | Retarget `:14` to split `archive`, `src-games` segments | Kai |
| `docs/test-plans/v0.8.0-check.js` | Retarget `:10,11,12,72,73,74`; resolve `:13`; retire R1 at `:57` | Kai |
| `docs/test-plans/v0.9.0-check.js` | Retarget `:10,72`; resolve `:11,12`; retire R2 at `:44` | Kai |
| `dev/src-consumer-manifest.py` | G1 through G8 (H1 list) | Kai |
| `dev/src-consumer-manifest.json` | Regenerated in the same commit, no hand edits | Kai |
| `dev/src-consumer-manifest.md` | Regenerated in the same commit, no hand edits | Kai |

Nothing else. No website byte, no `CACHE_VERSION` bump, no `RUNNABLE_FLOOR` touch, no second story in the PR.

## Why this matters

The manifest currently has zero rows for all three readers. That is the blind spot proven, not argued: the scanner only matches the `src/` slash literal and the `kai-story` arm, so every component-form `path.join(ROOT, 'src', ...)` read is invisible. The generator cannot run at all since the 2026-11-12 archive move: it prints `error: scan root missing: src` and exits 1, writing nothing. The artifacts are frozen at base `09bb82d` from 2026-11-11, with `counts.family_under_src` 11 describing the pre-move tree. Fixing the readers without fixing the scanner ships the same lie in a new shape: green checks with shrinking manifest coverage. This story fixes the instrument and the readers together, with a throwaway-worktree proof that the new scanner arm catches a component-form probe and ignores a bare `src` mention.

## Functional requirements

### Part 1: retarget the three readers to `archive/src-games`

- FR-1. `docs/test-plans/v0.7.0-check.js:14`: `path.join(__dirname, '..', '..', 'src')` becomes `path.join(__dirname, '..', '..', 'archive', 'src-games')`. Shape unchanged, only the segments change.
- FR-2. `docs/test-plans/v0.8.0-check.js:10,11,12,72,73,74`: every `path.join(ROOT, 'src', ...)` becomes `path.join(ROOT, 'archive', 'src-games', ...)`. `ROOT` at `:9` keeps its repo-root shape.
- FR-3. `docs/test-plans/v0.9.0-check.js:10,72`: same retarget as FR-2. `ROOT` at `:9` keeps its repo-root shape.
- FR-4. Segment spelling rule (binding): component form stays component form, segments stay split. Never write a single `'archive/src-games'` literal segment. After the change, no `src/` literal and no quoted `src` segment remains in any of the three files.
- FR-4b (A5 rewrite, ruled 2026-11-14 01:35 CST). After the retarget, the v0.8.0 reader exits 1 with 21/22 and `FAIL A5 header format`. The assertion `/'Wordfire ' \+ guesses \+ '\/6'/` no longer matches because the shipped `archive/src-games/wordfire.html:930-931` generalized the header to a mode label. The invariant is alive, so rewrite rather than retire. Replace the single A5 assertion with exactly two, with the label vocabulary pinned and never a wildcard:
  - `check('A5 share header mode label', /const modeLabel = difficulty === 'hard' \? 'Wordfire Hard ' : 'Wordfire ';/.test(wordfire))`
  - `check('A5 share header format', /modeLabel \+ guesses \+ '\/6'/.test(wordfire))`
  R1 and R2 retire because their referents died. A5 does not, and deleting it to get a green line throws away the share-header audit.

### Part 2: resolve the three `.openclaw` reads with a stated substitute

The old referent is absent: the whole `/home/jake/.openclaw/workspace/share/Flambeee` tree does not exist. Each read moves to a live in-repo referent per the H3 table. Assertion survival was measured by Rook on HEAD `113e6af`.

- FR-5. `docs/test-plans/v0.8.0-check.js:13` reads `path.join(ROOT, 'website', 'index.html')` instead of the absent share-mirror index. Assertions A10 whats-new section, releases link, and BLOG.md link each survive (1 hit each, measured).
- FR-6. `docs/test-plans/v0.9.0-check.js:11` reads `path.join(ROOT, 'website', 'index.html')` instead of the absent share-mirror index. Assertions B4 four screenshot refs, B6 four alts, and B7 both CSS rules each survive (measured present).
- FR-7. `docs/test-plans/v0.9.0-check.js:12` becomes `const assetsDir = path.join(ROOT, 'website', 'assets');`. Assertion B5 survives: all four asset files exist on disk (measured: game-2048, game-minesweeper, game-simon, game-wordfire.png all present).
- FR-8. Retirement R1 (stated, not silent): delete `check('A10 site v0.8.0', /v0\.8\.0: Share your Wordfire streak/...)` at `v0.8.0-check.js:57`. The What's New section now names the newest release only (v0.50.0; the v0.8.0 heading measures 0 hits). Coverage lost: no check that the shipped page still announces v0.8.0. The announcement survives in git history and BLOG.md, so the loss is a stale-announcement audit, not a product claim.
- FR-9. Retirement R2 (stated, not silent): delete `check('B4 emoji icons removed', ...)` at `v0.9.0-check.js:44`. A current card still uses the `game-icon` glyph, so the v0.9.0-era all-four-emoji-gone invariant is genuine content drift. Coverage lost: the legacy-emoji audit. Icon policy belongs to Palette, not to this window.
- FR-10. Spot anchors under `archive/src-games/` were verified present on HEAD: `overlayShareBtn` and `flambeee-wordfire-distribution` in wordfire.html, `Migrate legacy flat shape` and `MIN_CELL = 18` in minesweeper.html, the A9 hub-shape anchors in index.html, `user-scalable=no` and `touch-action: manipulation` across the set. Any miss at build time is genuine drift only if proven against the archived bytes independent of the retarget; never paper over a miss by weakening a check.

### Part 3: fix the generator per G1 through G8, regenerate both artifacts

- FR-11 (G1). `:219`: `required_dirs = ("src", "docs/test-plans", "dev")` becomes `("archive/src-games", "docs/test-plans", "dev")`.
- FR-12 (G2). `:252`: `for root_rel in ("src", "docs/test-plans", "dev")` becomes `("archive/src-games", "docs/test-plans", "dev")`.
- FR-13 (G3). `:268-276`: add the single-quote arm directly after the double-quote arm: `if "path.join" in line and "'src'" in line: return True`. Both quote styles must count.
- FR-14 (G4). `:42-56` plus `:554`: add `COMPONENT_SRC_RE = re.compile(r"(?<![\w$])join\s*\([^()\n]*['\"]src['\"]\s*[,)]")` at module level, and the filter becomes `if "src/" not in line and "kai-story" not in line and not COMPONENT_SRC_RE.search(line): continue`. Uniform per-line predicate, no per-extension gating.
- FR-15 (G5). `:366`: `path.startswith("src/")` becomes `path.startswith("archive/src-games/")`, so the moved proofs stay runnable. Missing this edit is the floor-miss path.
- FR-16 (G6). `:401` and `:422`: `os.path.join(repo, "src")` becomes `os.path.join(repo, "archive", "src-games")`, and the `under` predicate `p.startswith("src/")` becomes `p.startswith("archive/src-games/")`. Without this, `family_total` silently drops 19 to 8.
- FR-17 (G7 prose). Docstring `:4-7` SCAN line gains the component-form mention; `:9-13` scan roots `src/` becomes `archive/src-games/`; markdown counts line `:438` (`%d under src/`) becomes `%d under archive/src-games/`; scan-roots prose `:449-450` same rename. `FAMILY_REASON`, `BEFORE_SNIPPET`, `AFTER_SNIPPET` are frozen history, do not touch. The JSON key `family_under_src` keeps its name (schema stability belongs to #238); its meaning is restated below.
- FR-18 (G8 regeneration). Both `dev/src-consumer-manifest.json` and `.md` regenerate in the same commit as the generator change. No hand edits to either artifact, ever. `base_commit` must equal the PR head. **Measured counts after the full simulated change (see FR-18b): runnable 17, historical 33, needs_decision 12, test_plan_files 35, family_total 19, family_under_src 11 (paths under `archive/src-games/`), consumer rows 204.** `RUNNABLE_FLOOR` stays 14 and is not touched.
- FR-18b (G9 and G10, ruled 2026-11-14 01:35 CST). The reader retarget alone leaves the generator red: `error: runnable floor missed: 11 paths, need 14`. The three JS plans `v0.4.0-logic-check.js`, `v0.6.0-logic-check.js` and `v0.6.0-smoke-test.js` were already retargeted to `archive/src-games` by the Story 134 move, so they carry no `src/` literal and produce no rows. The frozen artifact counted them only because it predates the move. The fix is the vocabulary, never the floor:
  - G9: add `MOVED_RE = re.compile(r"archive/src-games/")` beside `COMPONENT_SRC_RE`, and the row filter at `:554` gains a fourth arm. A line is a consumer row when it contains a literal `src/`, a `kai-story` token, a component-form quoted `src` segment, or a literal `archive/src-games/` path.
  - G10: no new classify branch. The existing `docs/test-plans/*.js` arm already returns runnable when `live_src_read` is true, and `file_has_live_src_read` matches a `readFileSync` line that mentions `src`, which `archive/src-games/` does.
  - Expected deltas against the frozen artifact: runnable 14 to 17 (+3 old JS readers restored, +3 retargeted readers now visible), historical 32 to 33, needs_decision 12 unchanged, test_plan_files 38 to 35 (the retargeted readers stop citing `src/`), family 19/11 unchanged, rows 193 to 204. Every delta is explainable row by row.
  - Stop conditions: runnable below 14 or above 20 after the change. Below 14 means the vocabulary repair failed. Above 20 means the new arm pulled more than the intended population, which is a scope call, not a 10 minute fix.
- FR-19. Exit codes keep their documented meaning: 0 written, 1 a scan root missing or unreadable or the runnable floor missed, 2 misuse. No new exit codes. No stdout on success; errors go to stderr.

## BDD acceptance criteria (ten observable commands, verbatim from design-handoff H8)

Threshold: 10 of 10 on the PR head. Each item states the plain-language scenario first (Given/When/Then), then the exact command, its expected exit code, and its expected first output line.

- AC-1 (BDD-1, v0.7.0 clean). Given the retargeted v0.7.0 reader on the PR head, when it runs, then it exits 0 and its first line names the viewport invariant.
  - Command: `node docs/test-plans/v0.7.0-check.js` exits 0, first line `A1. Viewport meta (games declare user-scalable=no)`.
- AC-2 (BDD-2, v0.8.0 clean). Given the retargeted v0.8.0 reader with R1 retired, when it runs, then it exits 0 and its first line passes the share-button check.
  - Command: `node docs/test-plans/v0.8.0-check.js` exits 0, first line `PASS A1 share button in overlay`.
- AC-3 (BDD-3, v0.9.0 clean). Given the retargeted v0.9.0 reader with R2 retired, when it runs, then it exits 0 and its first line passes the distribution-key check.
  - Command: `node docs/test-plans/v0.9.0-check.js` exits 0, first line `PASS B1 DIST_KEY exists`.
- AC-4 (BDD-4, generator writes). Given the fixed generator on the PR head, when it runs with a clean environment, then it exits 0, writes both artifacts, and the chained echo prints the marker (the generator itself is silent on success).
  - Command: `env -u PYTHONPATH python3 dev/src-consumer-manifest.py && echo GENERATOR-OK` exits 0, first line `GENERATOR-OK` (the generator itself is silent on success).
- AC-5 (BDD-5, base_commit correct). Given the regenerated JSON on the PR head, when its recorded base commit is compared to the current HEAD, then they match and the marker prints.
  - Command: `test "$(env -u PYTHONPATH python3 -c "import json; print(json.load(open('dev/src-consumer-manifest.json'))['base_commit'])")" = "$(git rev-parse HEAD)" && echo BASE-MATCH` exits 0, first line `BASE-MATCH`.
- AC-6 (BDD-6, component-form positive, scratch copy). Given a scratch copy of the checkout with a component-form `path.join(ROOT, 'src', ...)` probe file added, when the new generator scans that copy, then the probe appears in the copy's manifest and the marker prints. This is the proof the blind spot is closed; without it the reader rows stay absent and the fix is decoration. A linked git worktree cannot be the target: its `.git` is a file, the generator exits 2, and that is #237's known behavior, out of scope.
  - Command: `COPY=$(mktemp -d /home/jake/.hermes/profiles/flambeee/cache/scratch/probe-XXXXXX) && cp -a . "$COPY"/ && printf "const probe = path.join(ROOT, 'src', 'probe.html');\n" > "$COPY/docs/test-plans/zz-probe.js" && env -u PYTHONPATH python3 dev/src-consumer-manifest.py --repo "$COPY" >/dev/null 2>&1 && test "$(grep -c zz-probe "$COPY/dev/src-consumer-manifest.json")" -ge 1 && echo PROOF-CAUGHT` exits 0, first line `PROOF-CAUGHT`.
- AC-7 (BDD-7, component-form negative, scratch copy). Given a scratch copy with a bare-`src` file that has no join context, when the new generator scans that copy, then the file does not appear in the copy's manifest and the marker prints.
  - Command: `COPY=$(mktemp -d /home/jake/.hermes/profiles/flambeee/cache/scratch/clean-XXXXXX) && cp -a . "$COPY"/ && printf 'var src = getImageSource();\nimg.src = "x";\n' > "$COPY/docs/test-plans/zz-clean.js" && env -u PYTHONPATH python3 dev/src-consumer-manifest.py --repo "$COPY" >/dev/null 2>&1 && test "$(grep -c zz-clean "$COPY/dev/src-consumer-manifest.json")" = "0" && echo CLEAN-OK` exits 0, first line `CLEAN-OK`.
- AC-8 (BDD-8, false-positive control in-repo). Given the new module-level regex on the PR head, when it is tested against three known-negative lines, then none matches and the marker prints.
  - Command: `env -u PYTHONPATH python3 -c "import importlib.util; s = importlib.util.spec_from_file_location('m', 'dev/src-consumer-manifest.py'); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); neg = ['var src = getImageSource();', 'img.src = url;', \"path.join(ROOT, 'srcDir', 'x.html')\"]; print('NEG-OK' if not any(m.COMPONENT_SRC_RE.search(l) for l in neg) else 'NEG-LEAK')"` exits 0, first line `NEG-OK`.
- AC-9 (BDD-9, floor and family). Given the regenerated JSON on the PR head, when its counts are read, then runnable is 17, family_total is 19, and family_under_src is 11, and the marker prints. The floor itself is 14 and passes as a lower bound. A runnable below 14 or above 20 is a stop condition, not a number to explain away.
  - Command: `env -u PYTHONPATH python3 -c "import json; c = json.load(open('dev/src-consumer-manifest.json'))['counts']; print('COUNTS-OK' if (c['runnable'], c['family_total'], c['family_under_src']) == (17, 19, 11) else 'COUNTS-BAD')"` exits 0, first line `COUNTS-OK`.
- AC-10 (BDD-10, zero website bytes). Given the PR working tree, when the website tree is checked for modifications, then it is clean and the marker prints.
  - Command: `test -z "$(git status --porcelain -- website/)" && echo WEBSITE-CLEAN` exits 0, first line `WEBSITE-CLEAN`.

## Out of scope

- Stories 135 and 136 (#237 worktree support, #238 schema note). Deferred to a later LEGACY window. The standing ruling for #237 is option B, fail loud, write nothing, recorded 2026-11-13. If mentioned at all, mention only as deferred.
- M-3 Cinder counter (#215) and M-4 rule (#216). Not this window.
- Any byte under `website/`. The gating command is BDD-10.
- Any `CACHE_VERSION` change in `website/sw.js` (stays 26).
- Any `RUNNABLE_FLOOR` change (stays 14). If the floor misses after the retarget, the classification is wrong, never the floor. A PR that touches `RUNNABLE_FLOOR` is rejected at design review.
- `FAMILY_REASON`, `BEFORE_SNIPPET`, `AFTER_SNIPPET` prose (frozen history).
- The `family_under_src` JSON key name (schema stability belongs to #238); only its meaning is restated (paths under `archive/src-games/`).

## Definition of done

AC-1 through AC-10 recorded pass in the PR body, 10 of 10. Manifest diff explainable row by row, with only the four permitted row classes from H4: (a) consumer paths renamed `src/*.py` to `archive/src-games/*.py` with kind and reason unchanged; (b) `base_commit` advance; (c) counts and prose renames from G7; (d) reader rows absent throughout (zero before from the blind spot, zero after because no `src` refs remain; the BDD-6 worktree proof carries the detection evidence, not the artifact diff). A diff showing `family_total` 19 to 8 or `family_under_src` 11 to 0 is the silent shrink and fails the PR. Readers first (each exit 0, or fail only on a newly named pre-existing drift proven against the archived bytes; A5 is rewritten per FR-4b, not retired), then generator exit 0 with regenerated artifacts at the measured counts (runnable 17, family 19/11, rows 204), then the component-form scratch-copy proof (AC-6). Riven peers the PR. A PR that leaves any of the three readers red is not done.
