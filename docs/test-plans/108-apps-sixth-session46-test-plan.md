# Test Plan: Story 108 Sixth Flambeee Apps App, Track A (Session 46)

**Story:** `docs/stories/108-apps-sixth-session46.md` (P1, v0.39.0 vehicle, gated on green).
**Owner:** Riven. **QA:** Scout. **PR:** #184, branch `riven/story-108-convert-v2`.
**Pick:** Convert (unit converter). File `website/apps/convert.html` (247 lines). Key `flambeee-apps-convert` ({pair, amount}).

## Scope
In scope: `website/apps/convert.html`, at most one card in `website/index.html`,
the `CACHE_VERSION` 14 to 15 bump line, one `sw.js` precache line appended
after the coin line. Out of scope: Day Pad, timer, Tally, Dice, Coin Flip,
games, schedule, noon, checker scripts, FPS probe, pending-post.txt.
Any diff there fails the plan.

## Checks (each maps to an AC)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Riven, four surfaces in one PR | `gh pr view` + diff stat | 3 files, 256+/2- |
| 2 | AC-2 | Equal-size: one file, no backend, no build, localStorage-only under `flambeee-apps-` | Read file, grep for fetch/XHR/socket/remote refs | No network calls, key `PREFIX + 'convert'` recorded |
| 3 | AC-3 | Value gate: one-line real use case in dev record | Read dev record | Cook scaling a recipe converts cups to ml in one tap |
| 4 | AC-4 | CACHE 14 to 15, exactly one new precache line after coin line | `git diff` on `website/sw.js` | 1 version line, 1 added entry, others unchanged |
| 5 | AC-5 | Scope guard | `git diff --name-only` vs base | Only the 3 files |
| 6 | AC-6 | Desktop 1280x800 real typed input + clicks | Serve + Chromium, type 2 cups-ml, click Convert | `473.176 ml`, label `2 cups is 473.176 ml`, 0 page errors |
| 7 | AC-7 | Mobile 375x667 same | Same at 375x667 | Same, no overflow, 0 page errors |
| 8 | AC-8 | CACHE reads 15 merged, precache line present | grep merged tree | `var CACHE_VERSION = 15`, `'./apps/convert.html'` in PRECACHE_URLS |
| 9 | AC-9 | Gate rule recorded | Dev record + qa-results | Green keeps cut on table, slip means no tag |
| 10 | AC-10 | Copy tone | grep for em dash | 0 em dashes, no heavy emoji |
| 11 | Neg | Invalid input converts nothing with note | Drive `bogus`, click Convert | Result `-`, status `Type a plain number, like 2 or 0.5.` |
| 12 | Neg | Reload persistence | Reload after valid conversion | Stored {pair, amount} byte-identical across reload |
| 13 | Edge | Temperature leg + card target | Type 100 c-f, click Convert; GET card href | `212 F`; card href `apps/convert.html` resolves 200 |

## Result (Scout independent re-run, 2026-10-30)
Driver: `s46qa/qa108.js` (own script, own serve on port 8905, playwright-core
with cached Chromium 1248, real keyboard.type with delay plus real clicks).
Pass/fail counts and full output in `flambeee-team/qa-results.md`.
