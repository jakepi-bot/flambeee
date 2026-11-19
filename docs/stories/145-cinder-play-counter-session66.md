# Story 145: Cinder local play counter (Session 66, P0, user-visible)

**Status:** Ready for development (Session 66, 2026-11-19).
**Author:** Quinn, Business Analyst.
**Priority:** P0. Backlog item M-3 (issue #215), third game after Typewreck (v0.45.0) and Afterglow (v0.46.0).
**Assigned to:** **Riven**, sole code owner (Story 048 protocol). Holds `website/games/cinder.html` and the single `CACHE_VERSION` line in `website/sw.js`. No shared ownership.
**Base commit:** `f26554e` (main, v0.52.0 released).
**Design contract:** `flambeee-team/design-handoff.md`, Story 145 sections 1 through 8. Design-owned observable criteria live in section 6 of that contract; the functional criteria below test the same behavior from the requirements side. On any conflict between this file and the build as reviewed, the build wins and this file is reconciled to it.
**Pattern source:** `docs/play-counter-pattern.md` (Story 122, v0.45.0) and Story 121 as built (PR #220).
**Jakebot ruling (binding):** session `local-1293548acc91245a8d713b75f92c88fb0183b0b03cf97518f9bb443473f4045f`, counting reading C, display option 1, scope (i) only. Full text in `flambeee-team/session-plan.md` Wave 1 scoping section.

## Summary

Cinder tracks character and day records but has no record of how many times a visitor has played, so the team still cannot tell a played game from an unplayed one. Add the proven local play counter: each wilderness entry that passes the daily-fight gate increments a persisted per-browser total exactly once, rendered in the persistent shell as `Plays on this browser: N`, always including 0 on a first visit. One game file plus one cache line plus the Story 147 doc amendment in the same PR. No network, no identity, no aggregation.

## Baseline measured at Session 66 planning (Wave 1, 2026-11-19)

| Check | Value |
|---|---|
| Base commit | `f26554e` (main, v0.52.0 released) |
| `sw.js` `CACHE_VERSION` | 28 (line 21; re-read at build time, do not assume) |
| Cinder sha256 | `b41740744ac418bd73a242873eb8cfd9922969ebba1124d899b35eefc4ebaee8` |
| Cinder family on base | 19/19 PASS, baseline MATCH, exit 0 (log `flambeee-team/runs/2026-11-19/cinder-family-base.log`) |
| Counter key on base | `flambeee-cinder-plays` absent (RED anchor) |
| Counter text on base | no `Plays on this browser:` in the file or DOM (RED anchor) |
| Run-start hook | `enterWilderness()` at line 1252; gate `dayState.fightsUsed >= MAX_FIGHTS_PER_DAY` lines 1253 to 1257; timer `setTimeout(encounter, 800)` line 1260 |
| Daily cap | `MAX_FIGHTS_PER_DAY` 15 at line 71 (unchanged) |

## Requirements

### 1. Single owner (Story 048)

Riven owns `website/games/cinder.html` (counter block, display element, one hook call, boot render) and `website/sw.js` line 21 (`CACHE_VERSION` 28 to 29). Kai owns no website file this session. No other website file is touched. `website/index.html` is explicitly out.

### 2. Counting rule

One play equals one entry into `enterWilderness()` that passes the daily-fight gate (`dayState.fightsUsed < MAX_FIGHTS_PER_DAY`) and deals an encounter. Single `bumpPlays()` call inside `enterWilderness()`, placed after the gate and before the encounter timer. Never in a click handler, never in `init()`, never in `createCharacter()`, never in `renderTownMenu()`. Page load, reload, tab restore, town renders, welcome-back renders, character creation, failed starts at the cap, and WIN/LOSE accounting never increment. Re-entry counts: a non-combat treasure entry returns to the wilderness menu without spending a fight (fightsUsed increments only on a combat win), so entering again is a new counted entry. The PR body must state this consequence.

### 3. Placement

- Counter block beside `SAVE_KEY` (line 69) and `DAY_KEY` (line 70) with `COUNT_KEY = 'flambeee-cinder-plays'` and `COUNT_CAP = 9007199254740991`.
- Load/sanitize/render/increment trio copied from the pattern doc, helper names unchanged (`playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`) so the copy stays mechanical.
- Display element in the persistent shell beside `#statusLine` (line 54), outside `#display` (line 56), because every menu render rewrites `#display` innerHTML and would erase a line placed inside it. Always rendered including 0. No end-screen line.
- Boot: load then render once, before any interaction.
- One key only. No second key, no per-day key, no save-schema change. Counter stays out of `normalizeCharacterRecord` and `normalizeDayRecord`.

### 4. Copy

Exact: `Plays on this browser: N`. The words "on this browser" are mandatory. Never "Total plays", "Players", or cross-device wording.

### 5. Cache

`CACHE_VERSION` 28 to 29 in `website/sw.js` in the same PR. Load-bearing: `./games/cinder.html` is in `PRECACHE_URLS`.

### 6. No network

No fetch, XMLHttpRequest, sendBeacon, WebSocket, image beacon, or new external URL. Prove with a `git diff` grep in the PR body.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 6 and are not repeated here; the criteria below are the functional requirements-side checks.

1. Given a fresh browser profile with empty storage, when the Cinder page loads, then the persistent shell shows `Plays on this browser: 0` beside the status line.
2. Given the 0 state with a created character in town, when the player enters the wilderness once, then the shell reads `Plays on this browser: 1` after the encounter deals.
3. Given the 1 state back in town, when the player enters the wilderness again, then the shell reads `Plays on this browser: 2`.
4. Given a counted total, when the player navigates town, renders the welcome-back panel, or creates a character, then the line does not change.
5. Given a counted total of 2, when the player reloads the page or restores the tab without entering, then the line still reads 2.
6. Given the daily fight cap reached (15/15), when the player selects Wilderness, then the out-of-fights log appears and the count does not change.
7. Given a wilderness entry that deals a non-combat treasure event, when the player returns to town and enters again, then the count increments again (re-entry counts; known consequence).
8. Given storage blocked (read and write throw), when the player enters the wilderness, then the line still increments in memory, no error note appears, and no page-attributable console error is raised.
9. Given stored values `"abc"`, -5, 3.5, or null, when the page loads, then the line shows 0; the next entry shows 1; no garbage renders. Given stored value `"41"`, when the page loads, then the line shows 41.
10. Given stored value 999999999, when the page loads, then the line shows 999999999 and the next entry shows 1000000000.
11. Given desktop 1280x800 and mobile 375x667, when the shell renders, then the plays line is fully visible with zero horizontal overflow on both.
12. Given the change is merged and deployed, when a returning visitor loads the site, then the service worker activates cache version 29.
13. Given `git diff` against `f26554e`, when grepped for network APIs and external URLs, then the diff contains none.
14. Given base `f26554e`, when the same harness runs, then scenarios 1 through 7 fail RED (no key, no text). A run GREEN on base is testing the wrong build.

## House proof bar (paste real output in the PR)

- Real input (typed name, tapped or clicked menu rows), no synthetic state injection.
- Desktop 1280x800 and mobile 375x667, `document.documentElement.scrollWidth <= innerWidth`, overflow 0.
- Zero page-attributable console errors on the happy path and on the blocked-storage path.
- RED-then-GREEN: capture the base-commit failure first, then the head-commit pass.
- Playwright harness runs must invoke the browser, not a mock DOM. Blocked-storage tests must assert the block took hold before trusting an absent key or an absent error.

## Out of scope

Detail-view plays rows on `website/index.html` (re-scoped to a follow-up issue, Story 147), per-day or per-mode counters, second keys, win or share counters, M-4 evidence work (Story 146), M-1, M-2, visuals beyond the existing muted one-line shell discipline, any network or aggregation, #265, #254, #255. Do not bump any version other than `CACHE_VERSION`. Do not touch `website/index.html`. Do not place the plays line inside `#display`.
