# LIGHTFARE Session 70 QA Test Plan (Stories 155, 156, 157, 158)

**Author:** Scout, QA Analyst. **Date:** 2026-11-23 (Session 70).
**Product under test:** PR #283 (Stories 155 + 156 + 158, head `9a46c4c`) and PR #284 (Story 157, head `ae0832f`), both OPEN against main `609de7f`.
**Build under test:** detached integration worktree `.../cache/scratch/s70-qa/wt` on base `609de7f`, with `git merge --no-ff origin/feat/session70-lightfare-155-158 -m 'qa: merge 283'` (merge commit `89f1354`) then `git merge --no-ff origin/feat/session70-157-lightfare-proof -m 'qa: merge 284'` (merge commit `11ca51d`). No conflicts; nothing resolved by hand.
**RED anchor baseline:** worktree `.../cache/scratch/s70-qa/base` at `609de7f` (game file absent), harness copied in untracked.
**Mutation fixture:** `.../cache/scratch/s70-qa/drift` (shipped game file with exactly one interior `.` -> `#` wall drift), built and BFS-verified independently by `drift_setup.py` + `bfs_independent.py`.
**Serve:** `python3 -m http.server 8945 --bind 127.0.0.1` from `<qa-wt>/website`. Cleanup is port-scoped only (`pkill -f "http[.]server 8945"`).
**Interpreter:** `env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python` (Playwright lives in the team venv).
**Harness serve:** the harness starts and tears down its own server with port-scoped cleanup; the 8945 server is only for the QA scripts.

Test environment: Chromium via Playwright. Viewports: desktop 1280x800, mobile 375x667 (touch enabled). Fresh browser context per scenario (clean storage, clean service worker). `window.__lightfare` is used read-only (getters only; `reset()` never called); storage seeding is done as *test input* through `localStorage`, never through the probe.

Severity scale: **Blocker** (ships broken / release gate fails), **Major** (AC violated, user-visible), **Minor** (cosmetic or doc drift, no player harm), **Low** (environmental / hardening).

QA scripts (scratch dir, read-only against the product):
- `static_check.py` - Story 156 site + scope + tuning + Story 158 doc checks over HTTP and the two worktrees.
- `browser_qa.py` - Story 155/156 Playwright scenarios, both viewports (156 checks).
- `supp_board_qa.py` - Story 155 AC-2/AC-3 board visibility in RUN (halo truth, full reveal, hide), both viewports, levels 1 and 2 (18 checks).
- `stale_worker.py` - Story 156 AC-3 returning-visitor worker path (seeded v32 -> v33 activation, no stale mix).
- `hints_check.py` - LEVELCLEAR / LOSE / WIN panel copy plus Enter hints and the HUD text.
- `bfs_independent.py` - independent BFS over the shipped `LEVELS` strings (also run against the drift fixture).
- `drift_setup.py` - builds the one-wall mutation fixture.

---

## Part A - Story 155 (game, `website/games/lightfare.html`)

### A.1 Boot and counting (AC-1, AC-8, AC-17)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-01 | Fresh boot | Fresh context, open `/games/lightfare.html`, no input | State TITLE; one-liner `Every look costs. Reach the exit with light to spare.` visible before first input; `Plays on this browser: 0`; `Best: 0`; no play counted |
| T-155-02 | Start counts exactly 1 | Click `#startBtn` | State RUN, level 1, light 15, moves 0, plays 1 |
| T-155-03 | Reload keeps count, returns to TITLE | After Start, reload page | State TITLE; plays still 1; run abandoned (level 1, bank 0) |
| T-155-04 | Enter start + auto-repeat guard | Fresh context, press Enter 3x on TITLE | One count total; single-transition guard holds; state RUN |
| N-155-b | Enter in RUN (negative) | Press Enter again in RUN | No count, no transition |
| N-155-a | Space/arrows on TITLE (negative) | Press them on TITLE | No count, no movement, state stays TITLE |
| T-155-05 | Single call site | Grep shipped file for `bumpPlays` / `enterRun` | Exactly one `bumpPlays();` call inside the one `enterRun()`; `advance()`, `retry()`, `backToTitle()`, `look()`, `move()` never call it; `enterRun` reached only from the Start click and the TITLE Enter branch |
| T-155-06 | No network in game file | Grep for `fetch(`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `http(s)://` | No matches |

### A.2 Look economy (AC-3, AC-4, AC-9, AC-12, AC-11)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-08 | First look | Start, press Space once | Light 15 -> 14; reveal hides after about 1.0 s (accept window 850-1600 ms) |
| T-155-43-reveal | Full-board reveal (AC-3) | During the reveal, read all 49 `#board .cell` texts | All 49 non-empty, every cell matches layout truth including `E`, then hides back to the 9-cell halo |
| T-155-43-hide | Reveal hides | Wait for reveal end | Back to exactly the 9 halo cells; measured ~1000 ms |
| T-155-09 | Four-look spend ladder | Look 4x, waiting for each hide | Light reads 14, 12, 8, 0; looks counter 4 |
| T-155-10 | Fifth look refused verbatim | After 4 looks, press Space twice | Line is exactly `Not enough light.` both times; light 0, looks 4, state RUN |
| T-155-11 | Refusal charges nothing (negative) | Snapshot light/moves/looks/reveal before the refused press | All unchanged after |
| T-155-12/13/14 | Reveal freezes input | During reveal hammer Space, arrows, WASD | No second charge; pos/moves unchanged; reveal ends on schedule and input works after |
| T-155-15 | 4-look level completable | Spend all 4 looks on L1, walk to exit | `Level 1 clear. Light kept: 0.` (no soft-lock) |
| T-155-16 | Zero-look solve banks 15 (AC-11) | Fresh run, no looks, walk L1 exit | `Level 1 clear. Light kept: 15.`; bank 15 |

### A.3 Movement and wall bumps (AC-5)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-17/18 | Wall bump silent and free | 5 wall bumps from (1,1) | pos unchanged, moves 0, `#msg` empty, light/looks unchanged |
| T-155-19/20 | Legal moves | Arrows and WASD | One cell per press, moves increments once per press |

### A.4 LOSE and retry (AC-6)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-21 | LOSE at exactly 80 | Bounce between two floor cells 80 times | After the 80th successful move: LOSE, moves 80, line exactly `Out of moves.` |
| T-155-22 | Wall bumps do not count toward 80 | Interleave wall bumps before the run | LOSE still at exactly 80 *successful* moves |
| T-155-23/24 | Retry keeps bank, no count | Clear L1 zero-look (bank 15), advance to L2, exhaust 80 moves, retry | Retry -> RUN level 2, light 15, moves 0, bank 15, plays unchanged (repeatable) |

### A.5 LEVELCLEAR and advance (AC-10)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-25b | LEVELCLEAR copy + hint | Clear L1 | `Level 1 clear. Light kept: X.` plus `Next level (Enter)` |
| T-155-26 | Advance fresh, no count | Press Enter | Level 2, moves 0, light 15, bank unchanged, plays unchanged |

### A.6 WIN and best (AC-7)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-28 | Full run WIN | Complete all 5 levels zero-look | `Run complete. Total light: 75.`; best 75 |
| T-155-29a/b | Best = max, JSON number | Second run with one look (total 74) | stored `flambeee-lightfare-best` stays `75`; line reads 74 |
| T-155-30 | WIN does not increment | Before/after WIN | plays unchanged |
| T-155-31 / N-155-f | WIN -> TITLE -> new run | Back to title, Start again | plays +1 exactly (new run from TITLE) |

### A.7 Storage discipline (AC-14, AC-15, AC-16)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-32/33 | Corrupt seeds -> 0 (both keys) | Seed `abc`, `{bad json`, `1.5`, `null`, `-1`, `NaN`, `Infinity`, `9007199254740992`, absent | Plays and best lines read 0 for every shape |
| T-155-34 | Numeric string kept | Seed `"3"` | Line reads 3 |
| T-155-34b/36 | Cap | Seed `9007199254740991`, then Start | Renders cap; new run stays at cap, no wrap |
| T-155-37 | Blocked storage silent | Init script makes `localStorage` throw; boot, Start, look | Plays tracks in memory (1), best in memory, no notice, play continues, zero page-attributable console errors |
| T-155-38 | Storage probe match | Normal run | `JSON.parse(localStorage[...])` equals `__lightfare.plays()` / `.best()` |

### A.8 Touch pad (AC-13) - mobile 375x667
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-39 | Pad moves one cell | Tap `#btnRight` | Exactly one cell per tap |
| T-155-40 | Pad wall refusal | Tap into a wall | pos and moves unchanged, silent |
| T-155-41/41b | LOOK button | Tap `#btnLook` | Reveal runs, light 15 -> 14; frozen during reveal; plays still counts correctly |

### A.9 Readable state (AC-2 / FR-7)
| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-155-43 | Halo-only truth (TITLE preview) | Fresh boot, read all 49 cells | Exactly the 3x3 around `@` non-empty and true; other 40 empty |
| T-155-43-run | Halo-only truth in RUN, L1 and L2 | Start (and advance to L2), no look, read all cells | Same as above while actually in RUN, both viewports |
| T-155-44 | HUD text always readable | During RUN | Level, Light, Moves, Looks, Bank, Best, Plays present as text |

### A.10 Structure / scope (AC-17, AC-18, AC-19, AC-20)
| ID | Scenario | Expected |
|---|---|---|
| T-155-45 | Diff scope vs `609de7f` | Exactly the four owned files |
| T-155-46 | sw.js bump | `CACHE_VERSION` 32 -> 33 on exactly one line, plus exactly one precache line (23 -> 24) |
| T-155-47 | No extra storage keys | Only `flambeee-lightfare-plays` and `flambeee-lightfare-best` |
| T-155-48 | Tuning constants | GRID 7, LEVEL_COUNT 5, LIGHT_BUDGET 15, LOOK_PRICES [1,2,4,8], REVEAL_MS 1000, MOVE_LIMIT 80, HALO_RADIUS 1, COUNT_CAP 9007199254740991 |
| T-155-49 | Layouts byte-exact + BFS | Byte-identical to FR-11; lengths exactly 8, 10, 12, 14, 16 (checked by `static_check.py`, by `bfs_independent.py`, and by the shipped harness); pars 1/1/2/2/3 all <= 4 |
| T-155-50 | No out-of-scope features | No enemy/timer/seed/streak/modal terms |

### Story 155 negatives
- N-155-a: Space/arrows on TITLE - no count, no movement.
- N-155-b: Enter in RUN - no count, no transition.
- N-155-d: 5th look mashed - every press refused with the same verbatim line, light stays 0.
- N-155-e: input during reveal - ignored, no charge, no restart.
- N-155-f: reload mid-run - title, bank cleared, plays unchanged.

---

## Part B - Story 156 (site card + cache activation)

| ID | Scenario | Expected |
|---|---|---|
| T-156-01 | `GET /games/lightfare.html` | HTTP 200 |
| T-156-02 / 02b | Count copy (source and rendered DOM) | `Eleven games, one arcade` present, `Ten games, one arcade` absent |
| T-156-03 | 11 cards | Exactly 11 `.game-card` in the games section |
| T-156-04 | Card placement | LIGHTFARE directly after Empty Hands (indices 10 and 9) |
| T-156-05 | Card link | `games/lightfare.html`, GET 200 |
| T-156-06 | `GAME_ORDER` byte-identical | Extracted block from `609de7f` vs branch byte-identical (sha256 compare too) |
| T-156-07 | Worker installs v33 | `caches.keys()` == `['flambeee-shell-v33']` after activation |
| T-156-08 | Precaches the game | v33 cache holds 24 entries including `./games/lightfare.html` |
| T-156-09 | No precache warnings | Zero install warnings/errors |
| T-156-10 | No stale-mix (returning visitor) | Seed a v32 cache pre-load, load the new shell: v32 deleted, only v33 remains, card and copy present, zero errors |
| T-156-11 | Diff hunks | Only the count-copy line and one new card block |
| T-156-12 | No modal / no rotation | `GAME_ORDER` untouched; no gotw/modal changes |
| T-156-07 (story) | Conflict rule | Shipped game file governs - stated in pattern-doc section 10 (checked in Part D) |

---

## Part C - Story 157 (proof harness, `dev/lightfare-proof.py`)

| ID | Scenario | Steps | Expected |
|---|---|---|---|
| T-157-01 | RED anchor | Run harness in `base` (game file absent) | Exit **2**, `RED: game file absent` |
| T-157-02 | Full run on the integrated tree | No flags | Real output recorded, `RESULT: PASS`, exit 0 |
| T-157-03 | Static legs | Read output | BFS 8/10/12/14/16, costs 1/2/4/8, spends 1/3/7/15, budget 15, 5th-look refusal all PASS |
| T-157-04 | Trial legs | Read output | 250 trials (50/level), 50/50 within 80 moves, medians <= par 1/1/2/2/3, max looks <= 4 |
| T-157-05 | Mutation control (harness's own) | Read output | Its internal one-wall drift turns the length check red |
| T-157-05b | Independent mutation control | QA's own drift fixture + `--sim-only` | `static-bfs-lengths FAIL`, overall exit 1 (FAIL dominates SKIP proven at the same time) |
| T-157-06 | Browser legs both viewports | Read output | fresh 0/0, Start 1, reload keeps, advance +0, retry +0 same level light 15 bank kept, 4-look spend with refused 5th and completable level, probe match, corrupt -> 0, blocked silent, pad path mobile, zero page errors |
| T-157-07 | Exit discipline | `--sim-only`, `--viewport=desktop`, `--viewport=bogus`, `--port=abc` | exit 3 / 3 / 1 / 1 with `SKIPPED:` lines for narrowing |
| T-157-08 | Scope | `git diff 609de7f --stat` for the branch | Only `dev/lightfare-proof.py`, +1512/-0 |

---

## Part D - Story 158 (pattern-doc section 10)

| ID | Scenario | Expected |
|---|---|---|
| T-158-01 | Section 10 present after section 9 | `## 10. LIGHTFARE instance` appended; everything before it byte-identical to base |
| T-158-02 | Counting unit verbatim | Word-for-word Story 155 counting rule, both sentences |
| T-158-03 | Both keys named | `flambeee-lightfare-plays` and `flambeee-lightfare-best` |
| T-158-04 | Formulas | `plays_new = min(plays_old + 1, 9007199254740991)`; `best = max(bestStored, runTotal)` at WIN only |
| T-158-05 | Section-10 tuning table | Rows: pattern section 10, both keys, cap, run-start hook, cache bump |
| T-158-06 | Boot-deal nuance + non-counts | `Boot-deal nuance: none.`, LOSE-retry non-count, LEVELCLEAR-advance non-count |
| T-158-07 | Checklist rows filled | All five section-5 rows (key suffix, display element, run-start hook, cache bump in same PR, no-network grep) have LIGHTFARE values |
| T-158-08 | Conflict rules | `game file wins` and `next free section number wins` |
| T-158-09 | No code change in this doc | The doc diff is one appended section only (`@@ -293,0 +294,89 @@`), zero deletions |

---

## Part E - Cross-cutting

| ID | Scenario | Expected |
|---|---|---|
| T-X-01 | Zero page-attributable console errors, desktop | Across every desktop scenario |
| T-X-02 | Zero page-attributable console errors, mobile | Same at 375x667 |
| T-X-03 | Scope audit vs `wave3-ownership.md` | File list and every `-U0` hunk header match the ownership map exactly, both PRs |
| T-X-04 | QA never fixes | No product-code edits, no commits to product files, no pushes to main, no merges |

## Execution order (as executed)
1. Detached integration worktree; merge both PR branches `--no-ff`; record conflicts if any (none).
2. Scope audit (`git diff --stat`, `-U0` hunk headers, `GAME_ORDER` sha256, storage keys, tuning).
3. Serve on 8945; static/site checks (`static_check.py`), independent BFS (`bfs_independent.py`), verbatim-copy greps.
4. Browser scenarios desktop then mobile (`browser_qa.py`), board-visibility supplement (`supp_board_qa.py`), worker path (`stale_worker.py`), panel hints (`hints_check.py`).
5. Harness: RED anchor on `base`, full run on the integrated tree, narrowing and invalid flags, independent drift fixture.
6. Story 158 document read-through.
7. PR comment reviews; `qa-results.md` with verdict.

## Execution results (2026-11-23)

| Group | Result |
|---|---|
| `static_check.py` (site, scope, tuning, Story 158) | 26/26 PASS, exit 0 |
| `browser_qa.py` (Story 155 + 156, both viewports) | 156/156 PASS, exit 0 |
| `supp_board_qa.py` (AC-2 halo in RUN, AC-3 reveal, both viewports, L1+L2) | 18/18 PASS, exit 0 |
| `stale_worker.py` (AC-3 worker path) | 3/3 PASS, exit 0 |
| `hints_check.py` (panel copy + HUD) | 4/4 PASS, exit 0 |
| `bfs_independent.py` on shipped file | `[8, 10, 12, 14, 16]`, exit 0 |
| `bfs_independent.py` on drift fixture | `[8, None, 12, 14, 16]`, exit 1 (fixture genuinely drifted) |
| Harness full run (integrated tree) | `RESULT: PASS`, exit 0; 250/250 trials; medians 0/1/1/1/1 <= par; max looks 1 |
| Harness RED anchor (`base`) | `RED: game file absent`, exit 2 |
| Harness `--sim-only` / `--viewport=desktop` | exit 3 / 3 with `SKIPPED:` lines |
| Harness `--viewport=bogus` / `--port=abc` | exit 1 / 1 (FAIL dominates SKIP; invalid value named) |
| Harness on QA's drifted fixture (`--sim-only`) | `static-bfs-lengths FAIL`, `RESULT: FAIL`, exit 1 |
| Defects raised | 0 blocking, 0 major; 2 cosmetic/low notes recorded in `qa-results.md` |

No product file was modified by QA. Nothing was merged, tagged, or pushed to main.
