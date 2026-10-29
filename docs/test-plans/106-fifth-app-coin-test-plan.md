# Test Plan: Story 106 Fifth Flambeee Apps App, Track A (Session 45)

**Story:** `docs/stories/106-apps-fifth-session45.md` (P1, v0.38.0 vehicle).
**Owner:** Riven. **QA:** Scout. **PR:** #179, branch `feat/session45-fifth-app`.
**Pick:** Coin Flip. File `website/apps/coin.html` (219 lines). Key `flambeee-apps-coin` ({call, last}).

## Scope
In scope: `website/apps/coin.html`, at most one card in `website/index.html`,
the `CACHE_VERSION` 13 to 14 bump line, one `sw.js` precache line appended
after the dice line. Out of scope: Day Pad, timer, Tally, Dice, games, schedule,
noon, checker scripts, FPS probe. Any diff there fails the plan.

## Checks (each maps to an AC)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Riven, four surfaces in one PR | `gh pr view` + diff stat | 3 files, 228+/2- |
| 2 | AC-2 | Equal-size: one file, no backend, no build, localStorage-only under `flambeee-apps-` | Read file, grep for fetch/XHR/socket | No network calls, key recorded |
| 3 | AC-3 | CACHE 13 to 14, exactly one new precache line after dice line | `git diff` on `website/sw.js` | 1 version line, 1 added entry, others unchanged |
| 4 | AC-4 | Scope guard | `git diff --name-only` vs base | Only the 3 files |
| 5 | AC-5 | Desktop 1280x800 real typed input + click | Serve + Chromium, type call, click Flip | Label `called X, flipped Y`, 0 page errors |
| 6 | AC-6 | Mobile 375x667 same | Same at 375x667 | Same, no overflow |
| 7 | AC-7 | CACHE reads 14 merged, precache line present | grep merged tree | `var CACHE_VERSION = 14`, `'./apps/coin.html'` in PRECACHE_URLS |
| 8 | AC-8 | Gate rule recorded | Dev record + qa-results | Green keeps cut on table |
| 9 | AC-9 | Copy tone | grep for em dash | 0 em dashes, no heavy emoji |
| 10 | Neg | Invalid input corrected: `bogus`, empty, `HEADS` | Drive bad values, click Flip | Corrected to heads with status note, flip still resolves |
| 11 | Neg | Reload persistence | Reload after flip | Last result persists from localStorage |
| 12 | Edge | Boundary: rapid double-flip, whitespace-padded input | Two fast clicks, `  tails  ` | Both resolve, padded input trimmed |

## Result (Scout independent re-run, 2026-10-29)
Driver: real Chromium via Python Playwright, served PR head on
`http://127.0.0.1`. Pass/fail counts and full output in
`flambeee-team/qa-results.md`.
