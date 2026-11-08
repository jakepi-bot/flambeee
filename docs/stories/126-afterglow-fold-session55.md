# Story 126: Afterglow plays line above the fold at mobile 375x667

**Status:** Ready for development (Session 55, 2026-11-08).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible; carries the release).
**Assigned to:** **Riven**, sole code owner (Story 048 protocol).
**Base commit:** `1d3a7bc`.
**Design contract:** `flambeee-team/design-handoff.md`, Section 1.
**Pattern source:** `docs/play-counter-pattern.md` (checklist carried verbatim below).
**Source issue:** #224.

## What it is

Afterglow's plays line ("Plays on this browser: N", the headline feature of v0.46.0) renders below the fold on a small phone, so a mobile visitor never sees it without scrolling. This story moves the line above the fold at 375x667 by compacting whitespace and/or reordering the setup stack, with the counter copy, counting behavior, storage key, and tap targets byte-identical. One game file plus the cache bump.

## Files

| File | Change |
|---|---|
| `website/games/afterglow.html` | `#plays` placement and the small-viewport stack only. Counter logic and the `startRun()` hook stay byte-identical (per contract Sections 1.4/1.6; see Open questions for the line-range note). Canvas stays 360x360, button padding stays `10px 18px`. |
| `website/sw.js` | Line 21 only: `CACHE_VERSION` 22 to 23, one line. |

No other file. In particular: no `website/index.html`, no `GAME_ORDER`, no other game file, no `dev/`, no `src/`.

## Baseline measured at Session 55 planning (base `1d3a7bc`, Playwright Chromium, viewport 375x667, `is_mobile`, touch)

| Check | Value |
|---|---|
| `#plays` rect top / bottom | 704 / 719 |
| Document height | 789 |
| Window inner height | 667 |
| Horizontal overflow | 0 |
| Overshoot past the fold | 37px at the top edge, 52px at the bottom edge |
| Reclaim target | about 52px (the issue's "~120px" is page offset, not overshoot) |
| `#stats-block` on first load | `display:none` (hidden), so moving the line above it reclaims nothing |
| `sw.js` `CACHE_VERSION` | 22 (line 21) |
| Counter key | `flambeee-afterglow-plays` (shipped, Story 123) |
| Counter copy on base | `Plays on this browser: N` (shipped, Story 123) |

## Out of scope

New games, FPS, Apps, website index or `GAME_ORDER` changes, Cinder edits (#215), `src/` archival (#213), the Cinder proof family (Story 127, Kai's files), PRs #206/#208/#211/#212/#217, `pending-post.txt`, release notes, BLOG.md, website What's New, any visual redesign (Palette owns appearance), any counting-rule or copy change (Story 123 invariants hold).

## Functional acceptance criteria (BDD, plain language)

1. **Scenario: First-time visitor sees the line without scrolling.** Given a first-time visitor on a small phone, when the Afterglow page finishes loading, then the plays line is fully visible without scrolling and reads "Plays on this browser: 0".
2. **Scenario: Returning visitor sees their total without scrolling.** Given a returning visitor with a stored play total, when the page loads, then the plays line is fully visible without scrolling and shows their stored total.
3. **Scenario: Starting a run still counts exactly once.** Given the page loaded, when the visitor presses Start once, then the plays total goes up by exactly 1 and the line wording is unchanged.
4. **Scenario: Restarting still counts.** Given a run in progress, when the visitor restarts into a fresh run, then the total goes up by exactly 1.
5. **Scenario: Reloading never counts.** Given a stored total, when the visitor reloads the page without starting, then the total is unchanged.
6. **Scenario: Switching modes never counts.** Given a run or setup state, when the visitor switches between Daily and Free play, then the total is unchanged.
7. **Scenario: Wins, losses, and returning to setup never count.** Given a run that ends or returns to setup, when the end or setup screen shows, then the total is unchanged from the run start.
8. **Scenario: Blocked storage stays silent.** Given a browser where storage is blocked, when the visitor loads and starts a run, then the line still counts for the session, no error note appears, and no page-caused console error is raised.
9. **Scenario: Bad stored values reset cleanly.** Given a stored value that is corrupt, negative, or otherwise invalid, when the page loads, then the line shows 0 and the next Start shows 1, with no garbage rendered.
10. **Scenario: Large stored values are kept.** Given a large but valid stored total, when the page loads and a run starts, then the total continues from that value plus 1.
11. **Scenario: Desktop layout is unchanged.** Given a desktop-size browser, when the page loads, then the board is the same size, the plays wording and its position relative to neighboring elements are unchanged, and there is no horizontal scrolling or overlap.
12. **Scenario: Returning visitor with stats still reads correctly.** Given a returning visitor whose stats panel is shown, when the page loads, then the stats panel is visible and the plays line sits below it with exact wording.
13. **Scenario: Cache version rides along.** Given the merged change, when the service worker file is inspected, then the cache version has moved from 22 to 23 in the same change.
14. **Scenario: No network added.** Given the merged diff, when it is checked for network calls and new external addresses, then none are present.
15. **Scenario: Scope guard.** Given the scope guard, when the diff is inspected, then at most the one game file plus the one cache-bump line changed.

## Design acceptance criteria (from Rook's contract, do not restate new numbers)

Observable design checks live in `flambeee-team/design-handoff.md`, Section 1.10 (Scenarios A through G) with the measurement plan in Section 1.11. This story does not re-state their numeric thresholds; the dev and QA runs satisfy them as written:

- Scenario A (primary fold placement, first load, zero scroll) and Scenario B (zero state).
- Scenario C (counting intact on Start) and Scenario D (stats present, DOM order).
- Scenario E (storage blocked, session count, same placement).
- Scenario F (desktop regression) and Scenario G (Plan B DOM placement, pre-approved per Section 1.9).
- Measurement plan: the four-viewport matrix, fresh-profile plus seeded returning-visitor runs, the settle rule, and the pass thresholds in Section 1.11 govern.

## Per-game checklist (from `docs/play-counter-pattern.md` Section 5, filled in for Afterglow)

Copy of the pattern table. Every row must hold before merge; this story must not break the shipped counter.

| # | Item | Typewreck value (worked example) | Afterglow value (this story) |
|---|---|---|---|
| 1 | Key suffix (middle slug) | `flambeee-typewreck-plays` | `flambeee-afterglow-plays`, unchanged by this story |
| 2 | Display element id and placement | `#plays` line on the setup screen, adjacent to `#best` | `#plays` element, outside `#stats-block` on the setup surface; placement moves up per the contract, id and copy unchanged |
| 3 | Run-start hook name | `startAiming()`, single `bumpPlays()` call inside it, reached only after the Start click-handler validation gate | `startRun()`, single `bumpPlays()` call inside it, reached only after the commit to a run; hook stays byte-identical |
| 4 | CACHE_VERSION +1 bump in `website/sw.js` | 20 to 21, same PR as the game change | 22 to 23, same PR as the game change |
| 5 | No-network grep | `git diff` grepped for fetch, XMLHttpRequest, sendBeacon, WebSocket, new external URLs: clean | Must read clean on this diff. No network call, no aggregation, no identity |

What must not change in this story: the counting rule, the copy, the always-render-zero empty state, and the silent-storage-failure discipline.

## Open questions

1. Contract line ranges vs plan line ranges: the contract cites counter logic lines 367-406 and the `startRun()` hook at 564-565; the session plan's ownership table cites 368-404 and 564-565. Both agree the block and hook stay byte-identical; Riven reads the actual lines at build time and the dev record states the range as found. Named, not resolved here.
2. Narrower viewports (360x640 best effort, 320x568 record only), 200% zoom, landscape 667x375, and reduced motion are record-only per contract Sections 1.3/1.7. A miss there is reported, not failed, provided the 375x667 criterion and zero horizontal overflow hold; any overflow found there becomes a new issue, not a Story 126 failure.
3. If the minimum compaction would touch canvas pixels, button padding, or tap targets, Riven stops and uses pre-approved Plan B (contract Section 1.9): move `#plays` higher in the DOM. No design re-review needed; if Plan B also fails, the story ships nothing and the defect rides the next LEGACY day with measurements attached.
