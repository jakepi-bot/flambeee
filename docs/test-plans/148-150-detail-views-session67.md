# Test Plan — Stories 148/149/150, Detail-View Plays Rows (Session 67)

- **PR under test:** #270, branch `feat/session67-268-detail-views`, HEAD `3c7aeed`, base `b6950f6`
- **Stories:** 148 (Cinder + Afterglow plays rows), 149 (Typewreck detail view), 150 (cache bump + docs)
- **Harness:** detached worktree of the PR HEAD serving `website/` on `http://127.0.0.1:8981`
  (port-scoped cleanup only); real Playwright Chromium at 1280x800 and 375x667, fresh
  context per scenario. Interpreter: `env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python`
- **Proof scripts (scratch, not committed):**
  `/home/jake/.hermes/profiles/flambeee/cache/scratch/qa_s67_proof.py` (253 checks),
  `.../qa_s67_supplement.py` (40 checks). Full logs: `qa_s67_full.log`, `qa_s67_sup.log`.
- **Result on PR HEAD:** 293/293 checks PASS (desktop 123 + 20 supplement; mobile 130 + 20 supplement),
  zero page-attributable console errors in every context. Exit 0 both scripts.

## 1. Modal inventory — all 7 cards (covers other-four-modal regressions)

| ID | Card Play href → modal | Title | Desc | Rules | Play href |
|----|------------------------|-------|------|-------|-----------|
| M-ALL-1..7 | click `.play-btn[href="games/<key>.html"]` for wordfire, minesweeper, simon, 2048, cinder, afterglow, typewreck | modal `#modalTitle` equals Wordfire / Minesweeper / Simon / 2048 / Cinder / Afterglow / Typewreck | `#modalDesc` non-empty | ≥1 `#modalRules li` | `#modalPlayBtn` href ends with `games/<key>.html` |

Also per modal: page URL still `index.html` (no navigation), zero page errors. At 375x667:
`document.documentElement.scrollWidth <= window.innerWidth` for each of the 7 open modals (O-FLOW-1..7).

## 2. Story 148 — Cinder + Afterglow plays rows

| ID | Story AC | Setup | Expect |
|----|----------|-------|--------|
| 148-1 | AC1 fresh Cinder | no flambeee keys | `#modalStats` text exactly `Play your first round to see your stats here`; no number, no `NaN`, no `undefined`, no exception |
| 148-2 | AC2 fresh Afterglow | same | same guarantees |
| 148-3 | AC3 plays-alone Cinder | `flambeee-cinder-plays`=`3`, no save | DATA rows `Level 0, Gold 0, Wins 0, Deaths 0, Plays 3` (Plays last); no empty message |
| 148-4 | AC4 plays-alone Afterglow | plays=`1`, no stats | DATA rows incl. `Plays 1` last; no empty message |
| 148-5 | AC5 save-no-plays Cinder | save `{level:4,gold:10,wins:2,deaths:1}`, no plays key | `Level 4, Gold 10, Wins 2, Deaths 1, Plays 0` in order |
| 148-6 | AC6 numeric string | plays=`"42"` | Plays row `42` (also Afterglow `"7"` → `7`, Typewreck `"7"` → `7`) |
| 148-7 | AC7 corrupt matrix | each of `abc`, `-5`, `3.5`, `null`, `"99999999999999999999"`, `{}`, `[]`, `true`, `` (raw as stored) per plays key, no save | empty message, no error, stored value byte-identical afterwards |
| 148-8 | AC8 large-valid | `999999999` | Plays `999999999`, no abbreviation/commas |
| 148-9 | AC9 storage-throws | `localStorage.getItem` overridden to throw (assert throw first) | modal opens, empty state, no page-attributable error |
| 148-10 | AC10 re-read | open, change plays 3→6 between opens, reopen | second open shows new value; plus open-twice-unchanged stability per modal |
| 148-11 | AC11 focus | Escape / close button / overlay click | closes, focus returns to invoking element |
| 148-12 | AC12 read-only+no-network | `git diff b6950f6..HEAD -- website/games/` empty; added lines grep for `setItem`/fetch/`XMLHttpRequest`/`sendBeacon`/`WebSocket` | games diff 0 bytes; only hit is a docs prose line (`never calls localStorage.setItem`) |
| 148-13 | AC13 real-browser QA | this plan at both viewports | exact copy, zero modal-attributable console errors |

## 3. Story 149 — Typewreck detail view

| ID | Story AC | Setup | Expect |
|----|----------|-------|--------|
| 149-1 | AC1 mapping | click / keyboard-Enter on Typewreck Play link | modal title `Typewreck`, Play href `games/typewreck.html`, no navigation |
| 149-2 | AC2 both rows | plays=`5`, best=`{"score":120,"seed":"abc123"}` | `Plays 5` then `Best score 120` in order; seeded `{"score":1234,"seed":"abc"}` → `Plays 5`, `Best score 1234` |
| 149-3 | AC3 fresh | no typewreck keys | exact empty copy, no NaN/undefined/exception |
| 149-4 | AC4 plays-only | plays=`5`, no best | `Plays 5` only |
| 149-5 | AC5 best-only | best valid, no plays | `Best score 120` only |
| 149-6 | AC6 zero-best | best `{"score":0,"seed":"abc"}`, no plays | empty message |
| 149-7 | AC7 corrupt best | `"junk"`, `{"score":"high"}`, `{"score":50}` (no seed), no plays | empty message, no error |
| 149-8 | AC8 corrupt-plays+valid-best | plays `not-json{{{` / `-3` / `2.5` / over-cap + valid best | `Best score 120` still surfaces |
| 149-9 | AC9 numeric string | plays=`"7"` | `Plays 7` |
| 149-10 | AC10 GAME_ORDER/GOTW | any date; source check | `GAME_ORDER` byte-exact `['cinder','wordfire','minesweeper','simon','2048','afterglow']` (6 entries); GOTW never Typewreck |
| 149-11 | AC11 Plan A screenshot | asset present | modal img `src assets/game-typewreck.png`, `naturalWidth` 1280 > 0, alt describes board |
| 149-12 | AC12 Plan B | n/a (Plan A shipped) | waived — asset exists; modal intact |
| 149-13 | AC13 keyboard | Enter opens, Tab trapped, Escape closes | focus returns to invoking link |
| 149-14 | AC14 read-only | corrupt best/plays before vs after | stored values byte-identical |
| 149-15 | AC15 real-browser QA | this plan at both viewports | exact labels/copy, zero modal-attributable errors |

## 4. Story 150 — cache + pattern doc

| ID | Story AC | Check | Expect |
|----|----------|-------|--------|
| 150-1 | AC1 value | read `website/sw.js` on HEAD | `CACHE_VERSION = 30` |
| 150-2 | AC2 one line | `git diff b6950f6..HEAD -- website/sw.js` | exactly one changed line (`29`→`30`) |
| 150-3..7 | AC3-7 doc | new §8 in `docs/play-counter-pattern.md` | names 3 plays keys + best `{score,seed}`; read-only rule; sanitize+cap `9007199254740991`; empty-state exact copy + plays-alone-flips; modal-not-rotation + Story 125; game-file-wins conflict rule — all six present |
| 150-8/9 | AC8-9 semantics/read-back | code review | bump is additive-only; release reads back 30, no other `sw.js` bytes |

## 5. Negative matrix (canonical raw stored values)

`abc`, `-5`, `3.5`, `null`, `"99999999999999999999"`, `{}`, `[]`, `true`, `` —
applied per key (`flambeee-cinder-plays`, `flambeee-afterglow-plays`, `flambeee-typewreck-plays`),
each in a fresh context: modal renders the empty state, no crash, no page-attributable console
error, and `localStorage.getItem(key)` afterwards returns the identical raw string.

## 6. Non-goals (explicitly not tested)

Merged-site cache activation (post-merge release-wave check); middle-click/new-tab default
(browser behavior, accepted by design); Plan B imageless modal (Plan A shipped).
