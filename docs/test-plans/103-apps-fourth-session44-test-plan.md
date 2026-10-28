# Test Plan: Story 103 Fourth Flambeee Apps App, Track A (Session 44)

**Story:** `docs/stories/103-apps-fourth-session44.md` (P1, v0.37.0 vehicle).
**Owner:** Riven. **QA:** Scout. **PR:** #175, branch `feat/session44-103-fourth-app`.
**Pick:** Dice. File `website/apps/dice.html` (219 lines). Key `flambeee-apps-dice` ({sides, last}).

## Scope
In scope: `website/apps/dice.html`, at most one card in `website/index.html`,
the `CACHE_VERSION` 12 to 13 bump line, one `sw.js` precache line appended
after the tally line. Out of scope: Day Pad, timer, Tally, games, schedule,
noon, checker scripts, FPS probe. Any diff there fails the plan.

## Checks (each maps to an AC)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Riven, four surfaces in one PR | `gh pr view` + diff stat | 3 files, 228+/2- |
| 2 | AC-2 | Equal-size: one file, no backend, no build, localStorage-only under `flambeee-apps-` | Read file, grep for fetch/XHR/socket | No network calls, key recorded |
| 3 | AC-3 | CACHE 12 to 13, exactly one new precache line after tally line | `git diff` on `website/sw.js` | 1 version line, 1 added entry, others unchanged |
| 4 | AC-4 | Scope guard | `git diff --name-only` vs base | Only the 3 files |
| 5 | AC-5 | Desktop 1280x800 real typed input + click | Serve + Chromium, type sides, click Roll | Result in range, label `d{n} rolled {r}`, 0 page errors |
| 6 | AC-6 | Mobile 375x667 same | Same at 375x667 | Same, overflow 0px |
| 7 | AC-7 | CACHE reads 13 merged, precache line present | grep merged tree | `var CACHE_VERSION = 13`, `'./apps/dice.html'` in PRECACHE_URLS |
| 8 | AC-8 | Gate rule recorded | Dev record + qa-results | Green keeps cut on table |
| 9 | AC-9 | Copy tone | grep for em dash | 0 em dashes, no heavy emoji |
| 10 | Neg | Invalid sides clamp: 1, 101, non-numeric | Drive bad values, click Roll | Clamp to 2 / 100, roll still in range |
| 11 | Neg | Reload persistence | Reload after roll | Result + sides persist from localStorage |

## Result (Scout independent re-run, 2026-10-28)
Driver: `s44qa-dice-qa.js` (Playwright + `/usr/bin/chromium`), served PR head
`7159b19` on `http://127.0.0.1:8911`. 19/19 QA-PASS, 0 fail. Detail in
`flambeee-team/qa-results.md`.
