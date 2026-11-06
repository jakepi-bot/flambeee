# Story 121: Typewreck local play counter (Session 53, P1, user-visible)

**Status:** Ready for development (Session 53, 2026-11-06).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (privacy-preserving local outcome signal; backlog item M-3, issue #215, scoped to one game per jakebot advisory).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the game file plus the CACHE bump together). Ember is product owner. No shared ownership.
**Tracked by:** Session 53 plan, Story 121. Follows Story 119 (Typewreck game, shipped v0.44.0) which built the file this story instruments. Design contract: `flambeee-team/design-handoff.md` (Rook, Session 53, sections 1-10).
**Depends on:** The shipped Typewreck at `website/games/typewreck.html` (states SETUP, AIM, FLYING, RESOLVE, WIN, LOSE; game object G; `startAiming()` at line 425; `BEST_KEY` at line 131). No code dependency on any other story this session. Story 122 rides alongside as docs only, zero code.

## Summary

Give Typewreck a local play counter. Today a visitor has no record of their own play history beyond a single best score, and the team cannot tell a played game from an unplayed one (the 2026-11-05 cadence audit found every played, shared, and retained cell reads "unknown by construction"). After this story, each run start increments a persisted per-browser total exactly once, rendered in plain words on the setup screen as `Plays on this browser: N`, always including 0 on a first visit. One game file plus the CACHE bump. No network, no identity, no aggregation. The value is the pattern Story 122 copies, not the volume.

## jakebot decision (advisory only, recorded)

Session 53 Wave 1 priorities per jakebot (session local-0e08fb1d409009efbdac0ea5aa30943fcbe38fedc6b860bfe93c1db62c3d44dc, proceeded on its read): point A, scoped to one game. Quoted: "Do A, scoped to one game. Counter pattern on Typewreck only, plus the shared snippet, in the 55-minute window. Not the full batch." Strongest reason given: the catalog has 9 shipped items and zero outcome data, and a 10th unmeasured title adds another row of unknowns one day after adopting the cadence policy meant to stop exactly that. Risk named: on-device counts cannot be read in aggregate, so this can quietly become a vanity number; if the next audit still has no outcome column, the instrumentation failed regardless of what the code does. Scope guard: one game, one file, no network, no identity.

**Citation:** `flambeee-team/session-plan.md`, Session 53 (2026-11-06), sections "Decision (jakebot advisory...)" and "Priorities (in order)".

## Baseline measured at Session 53 planning (2026-11-06 01:10-01:20 CST, paths re-verified Wave 2)

| Check | Value |
|---|---|
| Newest tag / release | v0.44.0 Typewreck (2026-11-05 08:56 UTC) |
| `sw.js` `CACHE_VERSION`, repo mirror | 20 (run must read the line, not assume it) |
| Game files | 8 game files, `website/games/typewreck.html` present |
| Counter key on base | `flambeee-typewreck-plays` absent under every scenario (RED anchor) |
| Counter text on base | no `Plays on this browser:` text in the DOM (RED anchor) |
| Counter hook sites | `BEST_KEY` at typewreck.html:131; `startAiming()` at typewreck.html:425; `#best` element on the setup screen |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the game file (`website/games/typewreck.html`) and the `CACHE_VERSION` bump line together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. Counting rule (Rook contract section 2, restated without weakening)

One play equals one entry into `startAiming()` that deals a wall and enters AIM. Page loads, setup views, preview renders, failed starts, wins, losses, returns to setup, reloads, and tab restores never increment.

Consequences, stated so a dev cannot implement them two ways:

- Restarting the same wall DOES count as a second play. A restart resets shots, score, and the dealt wall and grants a fresh ammo budget, so it is a new run with its own outcome. Not counting it would erase the rematch signal, which is the retention evidence this story exists to capture.
- Opening the page and leaving without starting does NOT count. A load is not a play.
- A reload mid-run does NOT count. The run is gone; boot only re-reads the stored total.
- A failed Start (empty paste, no random source, game stays in SETUP with the note) does NOT count. The hook sits after the validation gate, inside `startAiming()`, never in the click handler.
- A double click on Start cannot double count: the first call hides the setup screen, so the second click has no button to land on. Each `startAiming()` call maps to one visible run reset.
- R pressed during FLYING counts as a new play: it cancels the flight and re-deals through `restartWall()` to `startAiming()`.

Formula with units: plays_new [plays, integer] = plays_old [plays, integer] + 1 [play per run start]. No other term exists. There is no plays-per-page-load term and no plays-per-shot term.

Verified call-site funnel (read, not assumed): `startAiming()` is reached from exactly these paths: setup Start button paste path, setup Start button armed-random path, `restartWall()` (Restart button, Replay button, R key), plus `queryBoot` autostart. The single increment hook lives inside `startAiming()`, so every counted path counts exactly once and no other path can count.

### 3. Placement (one game file, three touch points)

- Counter block beside `BEST_KEY` at typewreck.html:131: `COUNT_KEY`, cap, load/increment/render trio mirroring the existing best trio (read with try/catch plus sanitize, write with try/catch, render on boot and after each increment).
- Single increment call inside `startAiming()` at typewreck.html:425, after the validation gate. Never in a click handler, never on a page-load path.
- Display element on the setup screen beside `#best`, plus its boot render call. The best line (`Best: N (seed X)`) is untouched and keeps its own key and logic.

### 4. Storage

Key `flambeee-typewreck-plays`. Value is a non-negative safe integer P [plays, unitless count]. On each counted run start: P := min(P + 1, 9007199254740991). On boot: P := sanitize(read(COUNT_KEY)), then render. No rates, no averages, no per-day math. No other persisted field, no new key.

Open question: the contract does not pin the serialization shape beyond "plain JSON number or string" handling in its corrupt-value rule, so this story does not over-specify it. Any structurally valid non-negative safe integer is accepted; only non-finite, non-integer, or negative values reset to 0. The dev record states the chosen shape.

### 5. Copy (exact words)

Required element: one text line on the setup screen, adjacent to the existing `#best` line, present and readable (no visual direction; Palette owns appearance).

Exact copy: `Plays on this browser: N` where N is the rendered total.

Scope honesty: the words "on this browser" are mandatory. This is a per-browser local count, not a global total. Never render "Total plays", "Players", or any wording that implies cross-device or cross-player data.

Empty-state rule: a first-time visitor sees `Plays on this browser: 0`, rendered on boot alongside the best line. Showing 0 teaches the player the counter exists and lets QA distinguish "instrument live, no plays yet" from "instrument broken or missing". The best line keeps its own existing behavior; only the plays line always renders.

End screen: no plays line required. The setup line plus persistence is the whole surface.

### 6. Unhappy paths (each with defined behavior)

- localStorage unavailable or throwing (private mode, disabled storage, blocked access): catch, stay silent, keep an in-memory P starting from 0, keep incrementing and rendering it for the session. Never surface an error note. Never throw a page-attributable console error. Mirror the existing best-key try/catch discipline.
- Quota exceeded on write: same as unavailable. In-memory P still increments and renders; the write is dropped silently. Next boot re-reads the last persisted value.
- Corrupt stored value (bad JSON, wrong shape, float, string, null): treat as 0, then apply the current increment normally and overwrite with the clean value. One corrupt entry never blocks counting and never renders garbage.
- Negative stored value (manual tamper): treat as 0, same path as corrupt.
- Absurd but structurally valid integer (manual tamper): accept and increment from it. Do not editorialize tampered values; the cap in section 4 bounds growth.
- Two tabs open at once: last write wins. Each tab holds its own in-memory P from its boot read and increments independently. Concurrent increments may lose at most one count. Defined as acceptable: this is an approximate per-browser signal, not an audit-grade total. Never add locking.
- Storage cleared between sessions: counter restarts at 0 and counts up again. Defined, no recovery, no error.
- Service worker serving a cached old shell: expected until the CACHE_VERSION 21 bump activates. Old shell shows no plays line; that is the versioned-out state, not a bug.
- `?start=1` autostart: counts as a play, because it is a real run start through `startAiming()`. Harness authors must account for it when asserting exact totals.

### 7. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (20 to 21) in `website/sw.js`. Nothing else in `sw.js`.
- Why the bump is load-bearing: `./games/typewreck.html` is in PRECACHE_URLS, so a game-file change without the bump serves the old shell to returning visitors and the counter never appears for them.
- The dev record states the version readout before and after. Never bump CACHE without the game change in the same diff.

### 8. Scope guard

In scope: `website/games/typewreck.html` (counter block, single increment hook, display element plus boot render) plus the one `CACHE_VERSION` bump line in `website/sw.js`. Untouched: every other game file, every app file, GAME_ORDER, the hub card surface, the What's New block, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, jobs, jakebot, cron config, PRs #206/#208/#211/#212/#217.

Plan B (per Rook contract section 7): if the visible line plus sanitization cannot be made trustworthy in the window, ship persist-only counting (COUNT_KEY, single increment inside `startAiming()`, try/catch discipline), readout through the existing `window.__tw` hook, and the CACHE bump in the same PR. What does NOT shrink: the counting rule and the single-hook placement.

### 9. Proof bar (release gate)

All seven, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. RED on the current tree, then GREEN: on base the key `flambeee-typewreck-plays` is absent under every scenario and no `Plays on this browser:` text exists in the DOM (exit 1 at minimum); on the merged tree the scenario script exits 0 with all cases passing. A run that is GREEN on base is testing the wrong thing.
3. Desktop 1280x800 with real typed input and real clicks: each case shows its count, layout holds with overflow 0.
4. Mobile 375x667 with real typed input and real clicks: same cases, layout holds with overflow 0.
5. Zero page-attributable console errors on both viewports (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
6. `CACHE_VERSION` reads 21 on the merged tree.
7. Grep proves no network call was added: no fetch, XMLHttpRequest, sendBeacon, WebSocket, or new external URL.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the game file plus the CACHE bump as single owner, and the dev record states the name.

**Scenario 2: Fresh load renders zero.**
Given a fresh browser with empty storage, when the page loads, then the setup screen shows `Plays on this browser: 0`. (RED anchor: no such text exists on base.)

**Scenario 3: First Start counts once.**
Given the empty state above, when the player deals a wall and presses Start, then the setup hides, the run starts, and after returning to setup the line reads `Plays on this browser: 1`.

**Scenario 4: Second run counts again.**
Given a stored total of 1, when the player starts a second run, then the line reads `Plays on this browser: 2`.

**Scenario 5: Reload never increments.**
Given a stored total of 2, when the player reloads the page without starting, then the line still reads `Plays on this browser: 2`.

**Scenario 6: Restart counts.**
Given a run in progress, when the player presses Restart wall, then a new run starts and the total increments by exactly 1.

**Scenario 7: Replay counts.**
Given a finished run on the end screen, when the player presses Replay wall, then a new run starts and the total increments by exactly 1.

**Scenario 8: Change wall never counts.**
Given a finished run on the end screen, when the player presses Change wall, then no increment occurs and the setup line shows the unchanged total.

**Scenario 9: Failed Start never counts.**
Given the setup screen with empty paste and no random wall dealt, when the player presses Start, then the note shows, the game stays in SETUP, and the total does not change.

**Scenario 10: WIN and LOSE never count.**
Given a run that reaches WIN or LOSE, when the end screen shows, then the total is unchanged from the run start (the run was already counted at its start).

**Scenario 11: Blocked storage stays silent.**
Given storage blocked (throws on read and write), when the player loads and starts two runs, then the line shows in-memory counts 0 then 1 then 2, no error note appears, and no page-attributable console error is raised.

**Scenario 12: Corrupt value sanitizes.**
Given a corrupt stored value (the key holds `not-json` or `-4` or `3.5`), when the page loads and one run starts, then the line shows a clean integer total and no garbage renders.

**Scenario 13: Render both viewports.**
Given desktop 1280x800 and mobile 375x667, when the setup screen renders, then the plays line is present and readable with no horizontal overflow on both viewports.

**Scenario 14: CACHE ownership.**
Given the repo `website/sw.js`, when the merged diff is inspected, then the version line reads 20 to 21 with the game change in the same diff.

**Scenario 15: No-network grep.**
Given the merged diff, when grepped for fetch, XMLHttpRequest, sendBeacon, WebSocket, and new external URLs, then no added call exists.

**Scenario 16: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one game file plus the CACHE bump line, and every other game, app, site, schedule, noon, checker, and FPS path shows no diff.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Fresh load shows `Plays on this browser: 0` (Scenario 2).
**AC-3.** First Start counts exactly once (Scenario 3).
**AC-4.** Second run counts again (Scenario 4).
**AC-5.** Reload without starting never increments (Scenario 5).
**AC-6.** Restart increments by exactly 1 (Scenario 6).
**AC-7.** Replay increments by exactly 1 (Scenario 7).
**AC-8.** Change wall never increments (Scenario 8).
**AC-9.** Failed Start never increments (Scenario 9).
**AC-10.** WIN and LOSE never increment (Scenario 10).
**AC-11.** Blocked storage stays silent with in-memory counting and zero page-attributable errors (Scenario 11).
**AC-12.** Corrupt, negative, or non-numeric values reset to 0 and never render garbage (Scenario 12).
**AC-13.** Plays line present and readable both viewports with overflow 0 (Scenario 13).
**AC-14.** `CACHE_VERSION` 20 to 21 in the same PR (Scenario 14).
**AC-15.** No-network grep clean (Scenario 15).
**AC-16.** Diff limited per the scope guard (Scenario 16).
**AC-17.** RED on the current tree (key absent, text absent, exit 1) then GREEN on the merged tree (exit 0).
**AC-18.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Scenario script plus its RED run (exit 1 on the current tree, key absent plus text absent recorded) and GREEN run (exit 0, all passing); local-serve command plus URL; both-viewport real-input runs with exit codes; overflow readings both viewports; console-error counts with page-attributable versus environmental split; the copy text verbatim; storage readout showing the total under `flambeee-typewreck-plays`; the `CACHE_VERSION` readout before and after; the no-network grep command plus output. Numbers, not adjectives.

## Non-Goals

- The other 7 games, any site registry or modal/detail view work (M-2), win or share counters, analytics, network calls, aggregation, or visuals (Palette owns them).
- The 2-player game idea, M-1, M-4, a second mechanic, or a second persisted field or key.
- A new precache entry, a GAME_ORDER change, a What's New edit, or a `pending-post.txt` touch.
- Cutting a version (release wave owns the cut decision and the tag).
