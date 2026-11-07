# Story 123: Afterglow local play counter (Session 54, P1, user-visible)

**Status:** Ready for development (Session 54, 2026-11-07).
**Author:** parent overseer (Wave 2 absorbed; see session-plan.md process incident).
**Priority:** P1. Backlog item M-3 (issue #215), second game after Typewreck.
**Assigned to:** **Riven**, sole code owner (Story 048 protocol). Holds `website/games/afterglow.html` and the single `CACHE_VERSION` line in `website/sw.js`. No shared ownership.
**Design contract:** `flambeee-team/design-handoff.md`, Section 1.
**Pattern source:** `docs/play-counter-pattern.md` (shipped as Story 122, v0.45.0) and Story 121 as built (PR #220).

## Summary

Afterglow has three stats (levels cleared, runs finished, best level) but no record of how many times a visitor has played, so the team still cannot tell a played game from an unplayed one. Add the proven local play counter: each run start increments a persisted per-browser total exactly once, rendered on the setup surface as `Plays on this browser: N`, always including 0 on a first visit. One game file plus the cache bump. No network, no identity, no aggregation.

## Baseline measured at Session 54 planning (2026-11-07 02:00-02:10 CST)

| Check | Value |
|---|---|
| Base commit | `1ea559f` (main, v0.45.0 released) |
| `sw.js` `CACHE_VERSION` | 21 (line 21; re-read at build time, do not assume) |
| Afterglow size | 657 lines, `website/games/afterglow.html` |
| Existing keys | `DAILY_STORAGE_KEY` and `STORAGE_KEY`, per-mode stats via `statsKey()` |
| Run-start hook | `startRun()` at line 519; reached from `btnStart` click and `btnRestart` (`restartRun(); startRun();`) |
| Counter key on base | `flambeee-afterglow-plays` absent (RED anchor) |
| Counter text on base | no `Plays on this browser:` in the DOM (RED anchor) |
| Autostart | none; no `URLSearchParams` or `?start` path in the file |

## Requirements

### 1. Single owner (Story 048)

Riven owns `website/games/afterglow.html` (counter block, display element, one hook call, boot render) and `website/sw.js` line 21 (`CACHE_VERSION` 21 to 22). Kai owns no website file this session. No overlap.

### 2. Counting rule

One play equals one entry into `startRun()` that commits a run and calls `startLevel(0)`. Page loads, mode switches, level advances, phase changes, wins, losses, returns to idle, reloads, and tab restores never increment. The Restart run button counts, because it calls `restartRun(); startRun();` and deals a fresh run.

Single increment call inside `startRun()`. Never in a click handler. Never in `startLevel()` (it also runs on level advance).

### 3. Placement

- Counter block beside `statsKey()` with `COUNT_KEY = 'flambeee-afterglow-plays'` and `COUNT_CAP = 9007199254740991`.
- Load/sanitize/render/increment trio copied from the pattern doc, helper names unchanged (`playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`) so the next game copy is mechanical.
- Display element outside `#stats-block` (that block is hidden by `renderStats()` when no stats exist), adjacent to it, always rendered including 0.
- Boot: load then render once, before any interaction.
- Mode-agnostic: one key, one total across Daily and Free play. Do not touch the existing per-mode stats keys.

### 4. Copy

Exact: `Plays on this browser: N`. The words "on this browser" are mandatory. Never "Total plays", "Players", or cross-device wording. No plays line on reveal or end surfaces.

### 5. Cache

`CACHE_VERSION` 21 to 22 in `website/sw.js` in the same PR. Load-bearing: `./games/afterglow.html` is in `PRECACHE_URLS`.

### 6. No network

No fetch, XMLHttpRequest, sendBeacon, WebSocket, image beacon, or new external URL. Prove with a `git diff` grep in the PR body.

## Acceptance criteria (BDD)

1. Given a fresh browser with empty storage, when the page loads, then the setup surface shows `Plays on this browser: 0`.
2. Given the empty state, when the player clicks Start, then the line reads `Plays on this browser: 1`.
3. Given one run returned to idle, when the player clicks Start again, then the line reads `Plays on this browser: 2`.
4. Given a running game, when the player clicks Restart run, then the line increments by exactly 1.
5. Given a run in progress, when the player switches Daily to Free or Free to Daily, then the line does not change.
6. Given two counted plays, when the player reloads without starting, then the line still reads 2.
7. Given two counted plays, when the player closes the tab and returns, then the line still reads 2.
8. Given storage blocked (read and write throw), when the player starts a run, then the line still increments in memory, no error note appears, and no page-attributable console error is raised.
9. Given stored value `"abc"`, `-5`, `3.5`, or `null`, when the page loads, then the line shows 0; the next Start shows 1; no garbage renders.
10. Given stored value `999999999`, when the page loads, then the line shows 999999999 and the next Start shows 1000000000.
11. Given desktop 1280x800 and mobile 375x667, when the setup surface renders, then the line is fully visible with zero horizontal overflow.
12. Given the change is merged and deployed, when a returning visitor loads the site, then the service worker activates cache version 22.
13. Given `git diff` against `1ea559f`, when grepped for network APIs and external URLs, then the diff contains none.
14. Given base `1ea559f`, when the same harness runs, then scenarios 1 through 7 fail RED (no key, no text). A run GREEN on base is testing the wrong build.

## House proof bar (paste real output in the PR)

- Real clicks and real key input, no synthetic state injection.
- Desktop 1280x800 and mobile 375x667, `document.documentElement.scrollWidth <= innerWidth`, overflow 0.
- Zero page-attributable console errors on the happy path and on the blocked-storage path.
- RED-then-GREEN: capture the base-commit failure first, then the head-commit pass.
- Playwright harness runs must invoke the browser, not a mock DOM. Blocked-storage tests must assert the block took hold before trusting an absent key or an absent error.

## Out of scope

Cinder and the other 6 games (Cinder needs the M-4 harness family in a full window), win or share counters, site registry or detail views, M-2, M-1, visuals, any network or aggregation. Do not bump any version other than `CACHE_VERSION`. Do not touch `website/index.html`.
