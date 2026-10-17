# Test Plan: Story 072 Apps First App (Day Pad)

Source: `docs/stories/072-apps-first-app.md`. Code under test: PR #137 branch `feat/session33-072-apps-073-currency`, file `website/apps/index.html` (176 lines, 5284 bytes), tested from worktree `/home/jake/.hermes/flambeee/wt-pr137`.

## Setup
- Base `54925ce`. PR137 head `4394348`.
- `git diff 54925ce..pr137 --stat` => 3 files, 197 insertions, 2 deletions.
- `git diff 54925ce..pr137 --name-only` => `website/apps/index.html, website/index.html, website/sw.js`.
- Toolchain: Playwright-core with system `chromium 155.0.8059.79`, script `/home/jake/.hermes/profiles/flambeee/cache/scratch/qa072/qa072.js` (in scratch, NOT in repo).

## Cases (real browser, headless Chromium, file:// URL)
1. T1 UTC date renders: `#utcDate` textContent equals `new Date().toISOString().slice(0,10) + ' UTC'`. Got `2026-10-17 UTC` vs expected `2026-10-17 UTC`, match true. PASS.
2. T2 countdown ticks: read `#countdown`, wait 2100ms, read again. Got `16:36:34` -> `16:36:32`, ticks true, format `HH:MM:SS` true. PASS.
3. T3 localStorage note persists across reload: type note, click Save, status `Saved.`, key `flambeee-apps-daypad-note` holds value, reload, input value restored. Got persistOK true. PASS.
4. T4 corrupt-value degrades: store empty string, reload, input empty, no exception, pageErrors []. Got corruptEmptyOK true. PASS.
5. T5 maxlength enforced via real typing: `page.type` 400 chars, got `typedLen 280`, attr `maxlength="280"`. PASS.
6. T6 stats prefix: `grep flambeee-apps-` => `PREFIX = 'flambeee-apps-'`, `NOTE_KEY = PREFIX + 'daypad-note'`. Fixed before first write. PASS.
7. T7 size cap: single file, 5284 bytes, 176 lines, no `src=` or external href, no backend/build/deps. PASS.
8. T8 division boundary: PR137 file set contains no `website/games/`, `src/`, no games rename; Apps tree `website/apps/` separate. `website/index.html` adds `<section id="apps">` after #games, reuses styles, What's New heading untouched (`v0.30.0`). PASS.
9. T9 CACHE_VERSION: `website/sw.js` 7->8 with precache entry `./apps/index.html` (line 38). Moved because precached file added. PASS.
10. T10 copy: no em dashes in new files. PASS.

## Full real output (qa072.js)
```
{"utcDate":"2026-10-17 UTC","utcDateExpected":"2026-10-17 UTC","utcDateMatch":true,"countdown1":"16:36:34","countdown2":"16:36:32","countdownTicks":true,"countdownFormat":true,"lsAvailable":true,"statusAfterSave":"Saved.","storedKey":"QA probe note 2026-10-17","noteAfterReload":"QA probe note 2026-10-17","persistOK":true,"corruptEmptyValue":"","corruptEmptyOK":true,"typedLen":280,"maxlengthAttr":"280","maxlengthOK":true,"pageErrors":[]}
```

## Verdict
PASS. All AC-1..AC-7 hold on the PR137 tree.
