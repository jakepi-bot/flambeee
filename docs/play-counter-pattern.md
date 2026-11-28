# Play counter pattern (local, per-browser)

Owner: Kai. Status: pattern for Story 121 (Typewreck) and the next 7 LEGACY sessions.
Scope: docs only. This file changes no code and bumps no cache version.

## 1. Key family

One key per game, alongside the existing best-score family:

- Best family: `flambeee-<slug>-best`
- Plays family: `flambeee-<slug>-plays`

Typewreck instance: `flambeee-typewreck-plays` (sits beside
`flambeee-typewreck-best` at typewreck.html line 131).

Per-game copies change only the middle slug (for example,
`flambeee-cinder-plays`). The `-plays` suffix never changes.
No other persisted field, no second key.

## 2. Load/increment/render trio

Mirror the existing best trio discipline in typewreck.html
(`loadBest` / `renderBest` / `saveBestIfBeats`, lines 306-327):
read with try/catch plus sanitize, write with try/catch,
render on boot and after each increment.

One shipped shape, copied from Typewreck as built (Story 121, PR 220).
Helper names below are the shipped Typewreck names: keep them,
change only the key slug, the display element, and the hook call site:

```js
var COUNT_KEY = 'flambeee-<slug>-plays';
var COUNT_CAP = 9007199254740991; /* max safe integer, increment stops here, never wraps */
var playsMem = 0;

function sanitizePlays(v) {
  if (typeof v === 'number') {
    if (!isFinite(v) || Math.floor(v) !== v || v < 0 || v > COUNT_CAP) return 0;
    return v;
  }
  if (typeof v === 'string' && v !== '') {
    var n = Number(v);
    if (!isFinite(n) || Math.floor(n) !== n || n < 0 || n > COUNT_CAP) return 0;
    return n;
  }
  return 0;
}

function loadPlays() {
  try {
    var raw = localStorage.getItem(COUNT_KEY);
    if (raw === null || typeof raw === 'undefined') return 0;
    var parsed;
    try { parsed = JSON.parse(raw); } catch (e) { return 0; }
    if (parsed === null || typeof parsed === 'undefined') return 0;
    return sanitizePlays(parsed);
  } catch (e) { return 0; }
}

function renderPlays() {
  playsEl.textContent = 'Plays on this browser: ' + playsMem;
}

function bumpPlays() {
  playsMem = Math.min(playsMem + 1, COUNT_CAP);
  try { localStorage.setItem(COUNT_KEY, JSON.stringify(playsMem)); } catch (e) {}
  renderPlays();
}

/* boot: load, then render once (renders 0 on a first visit).
   Boot load precedes any autostart, so autostart counts from the loaded total. */
playsMem = loadPlays();
renderPlays();

/* run-start hook, after the validation gate (Typewreck: inside startAiming()): */
bumpPlays();
```

Typewreck reference: COUNT_KEY is 'flambeee-typewreck-plays',
element is #plays beside #best, hook is bumpPlays() inside startAiming().

Notes on the snippet:

- `loadPlays` parallels `loadBest`: try/catch read, sanitize, 0 fallback.
- `bumpPlays` parallels `saveBestIfBeats`: capped increment, try/catch write, then render.
- `renderPlays` runs on boot, after every increment, and on
  return-to-setup (re-render of the unchanged total). No other render site.
- `sanitizePlays` accepts plain numbers and plain numeric strings
  that are non-negative integers within the cap. Anything else
  (bad JSON, wrong shape, float, non-numeric string, null,
  negative, over-cap) resets to 0.
- `COUNT_CAP` is 9007199254740991. The increment is
  `P := min(P + 1, 9007199254740991)` and never wraps.

## 3. Counting rule

Verbatim from design-handoff.md section 2 (Typewreck wording;
generalize only the hook name and the dealt thing per game):

> Rule: one play equals one entry into startAiming() that deals
> a wall and enters AIM. Page loads, setup views, preview renders,
> failed starts, wins, losses, returns to setup, reloads, and tab
> restores never increment.

Generalized: one play equals one entry into the game's run-start
function that deals and enters play.

Consequences, stated so a dev cannot implement them two ways:

- Restart and replay count. Restarting the same wall DOES count
  as a second play: a restart resets score and the dealt wall and
  grants a fresh budget, so it is a new run with its own outcome.
- Page load does NOT count. Opening the page and leaving
  without starting is not a play.
- Failed start does NOT count. The hook sits after the validation
  gate, inside the run-start function, never in a click handler.
- Reload does NOT count. Boot only re-reads the stored total.
- Tab restore does NOT count. Restore is not a boot and not a run start.
- WIN/LOSE does NOT count. The run was already counted at its start.
- Return-to-setup does NOT count. Returning to setup is not a run start.

Formula with units:

> plays_new [plays, integer] = plays_old [plays, integer]
> + 1 [play per run start]. No other term exists.

## 4. Copy rule

Verbatim from design-handoff.md section 5:

> Exact copy: `Plays on this browser: N` where N is D from section 3.

Rules:

- Always rendered on the setup surface, including 0 on a first visit.
  A first-time visitor sees `Plays on this browser: 0`.
- The words "on this browser" are mandatory. This is a per-browser
  local count, not a global total.
- Never render "Total plays", "Players", or any wording that implies
  cross-device or cross-player data.
- The best line keeps its own existing behavior; only the plays
  line always renders. No plays line on end screens.

## 5. Per-game checklist

Copy this table into the game PR. Every row must be filled before merge.

| # | Item | Typewreck value (worked example) | Per-game change |
|---|---|---|---|
| 1 | Key suffix (middle slug) | `flambeee-typewreck-plays` | Change only the slug: `flambeee-<slug>-plays` |
| 2 | Display element id and placement | `#plays` line on the setup screen, adjacent to `#best` | New id per game, placed on that game's setup surface next to its best line |
| 3 | Run-start hook name | `startAiming()`, single `bumpPlays()` call inside it, reached only after the Start click-handler validation gate | That game's function that resets score and enters play. Never a click handler, never a page-load path |
| 4 | CACHE_VERSION +1 bump in `website/sw.js` | 20 to 21, same PR as the game change | Bump by 1 in the same PR whenever a precached game file changes |
| 5 | No-network grep | `git diff` grepped for fetch, XMLHttpRequest, sendBeacon, WebSocket, new external URLs: clean | Must read clean on every copy. No network call, no aggregation, no identity |

What must change per game: the key suffix, the display element id
and placement, and the run-start hook name. What must NOT change:
the counting rule, the copy, the always-render-zero empty state,
and the silent-storage-failure discipline.

## 6. Unhappy paths

Summary of design-handoff.md section 6. Behavior per condition:

| Condition | Behavior |
|---|---|
| Storage blocked or throwing | Stay silent. Keep an in-memory P from 0, keep incrementing and rendering it for the session. No error note, no page-attributable console error |
| Quota exceeded on write | Same as blocked. In-memory P still increments and renders; the write drops silently. Next boot re-reads the last persisted value |
| Corrupt stored value (bad JSON, wrong shape, float, non-numeric string, null) | Treat as 0, apply the current increment normally, overwrite with the clean value. Never renders garbage. Plain numeric strings are accepted at their value by sanitizePlays |
| Negative stored value | Treat as 0, same path as corrupt |
| Absurd but valid integer (for example 999999999) | Accept and increment from it. Only non-finite, non-integer, or negative values reset to 0. The cap bounds growth |
| Two tabs open at once | Last write wins. Each tab holds its own in-memory P. At most one count lost. Documented as acceptable; never add locking |
| Storage cleared between sessions | Counter restarts at 0. Defined, no recovery, no error |
| Cached old shell served | Expected until the CACHE_VERSION bump activates. Old shell shows no plays line; that is the versioned-out state, not a bug |
| `?start=1` autostart | Counts as a play. It is a real run start through the same hook. Harness authors must account for it |

## Consistency

Reconciled against Story 121 as built (PR 220, peer-review pass):
helper names are the shipped typewreck.html names (playsMem,
sanitizePlays, loadPlays, renderPlays, bumpPlays), the snippet
matches the shipped logic including numeric-string sanitize and
the return-to-setup re-render, and the boot load precedes autostart.
Any remaining conflict between this doc and Story 121 as built
resolves in favor of Story 121 as built.

## 7. Cinder instance (Story 145, Session 66)

Counting unit: one play equals one entry into `enterWilderness()`
(`website/games/cinder.html`) that passes the daily-fight gate
(`dayState.fightsUsed < MAX_FIGHTS_PER_DAY`, 15) and deals an encounter.
Single `bumpPlays()` call inside `enterWilderness()`, placed after the
failed-start gate (which returns early without counting) and before the
encounter timer (`setTimeout(encounter, 800)`). Page load, reload, tab
restore, town renders, welcome-back renders, character creation, failed
starts at the cap, and WIN/LOSE accounting never increment.

Re-entry consequence (known, stated so review does not relitigate it):
`fightsUsed` increments only on a combat win, so a non-combat treasure
entry returns to the wilderness menu without spending a fight, and
re-entering calls `enterWilderness()` again and counts a second play.
A player who returns to town and enters again counts again. Bounded only
by player patience, same shape as the Typewreck restart rule above.

Persistent-shell display rule: the line lives in the persistent shell
beside `#statusLine`, outside `#display` (every menu render rewrites
`#display` innerHTML and would erase a line placed inside it). Exact copy
`Plays on this browser: N`, rendered on boot (0 on a first visit) and
after every increment. No plays line on end screens.

Single key: `flambeee-cinder-plays`, cap 9007199254740991, helpers
`playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`.
One key only. No second key, no per-day key, no save-schema change.
Counter stays out of `normalizeCharacterRecord` and
`normalizeDayRecord`. Sanitizer, boot-load-then-render, try/catch write,
and silent blocked-storage behavior match the snippet in section 2.

Re-scope note: #215's detail-view clause (plays rows on
`website/index.html`) is re-scoped to a follow-up issue covering the
three shipped counters (Cinder, Afterglow, Typewreck), owed in this
release wave with its number recorded when the wave opens it. #215 stays
open until that batch lands; the game-page line alone does not close it.

## 8. Detail-view rule (Session 67, Stories 148/149/150)

The home page (`website/index.html`) shows the shipped counters
read-only inside the game detail modals. No game file changed for this;
the modal only surfaces what the game already persisted.

Keys surfaced, all read per modal open with no caching across opens:

- `flambeee-cinder-plays` (Cinder `Plays` row, alongside the save record)
- `flambeee-afterglow-plays` (Afterglow `Plays` row, alongside the stats record)
- `flambeee-typewreck-plays` (Typewreck `Plays` row)
- `flambeee-typewreck-best` with shape `{score, seed}` (Typewreck `Best score`
  row; the modal shows the score only, never the seed)

Read-only site rule: `website/index.html` never calls
`localStorage.setItem` for these keys. Corrupt values display as absent
(0, or the empty state) and are never repaired or written back.

Shared sanitize rule (one `readPlaysCount` helper at IIFE scope, mirroring
the game pages' `sanitizePlays`): accept integer numbers 0..9007199254740991
and non-empty numeric strings converting to such an integer; yield 0 for
negative, fractional, NaN, Infinity, null, undefined, absent key, corrupt
JSON, wrong shape (object/array/boolean), empty string, and over-cap values.
Cap constant: 9007199254740991.

Empty-state rule: the modal shows `Play your first round to see your stats here`
iff every displayed stat including plays is 0 or absent. Any displayed stat
including plays non-zero renders the data block, including the Plays row, so
plays alone (with no save/stats record) flips the modal out of the empty state.

Modal-not-rotation note: Typewreck is a `GAMES` modal surface only.
`GAME_ORDER` stays 6 entries (`cinder`, `wordfire`, `minesweeper`, `simon`,
`2048`, `afterglow`); Typewreck never appears as Game of the Week
(Story 125 ruling stands).

Conflict rule: where this doc and a shipped game file disagree, the game
file wins (established pattern-doc rule).

## 9. Empty Hands instance (Story 153, Session 69)

Counting unit: one play equals one entry into RUN that begins a new run.
Exactly two entries, both routed through a single `enterRun()` helper
(`website/games/empty-hands.html`) carrying the one and only `bumpPlays()`
call: (a) the Start click from TITLE, which plays the level-1 board dealt
at boot; (b) the BUST restart (`New run (Enter)`), which draws a fresh run
seed and deals level 1.

Boot-deal nuance: `newRun(false)` deals the level-1 board via `startBoard()`
and lands on TITLE, but boot itself never counts. The TITLE preview board is
not a play. `newRun()` itself never calls `bumpPlays()`.

Display rule: one persistent HUD item inside `.hud`, outside `#panel` so
title/end swaps cannot erase it:
`<span class="item">Plays on this browser: <span id="plays">0</span></span>`.
Exact copy `Plays on this browser: N`, always rendered including 0 on a
first visit. Boot loads via `loadPlays()` then renders once. No second plays
line on the end panel, no cross-device wording.

Key, cap, helper names: single key `flambeee-empty-hands-plays` (sits beside
`flambeee-empty-hands-best`, untouched), cap 9007199254740991, helpers
`playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`.
Sanitizer, boot-load-then-render, try/catch write, and silent
blocked-storage behavior match the snippet in section 2 (constants live on
`CONFIG` as `COUNT_KEY`/`COUNT_CAP` in this file).

WIN-advance non-count: `advance()` after a WIN deals the next level inside
the same run and never increments. BUST and WIN themselves never increment;
the run was counted at its start. `give()`, `endBoardWin()`, `endRunBust()`,
`render()`, reload, tab restore, and `__empty.reset()` never count.

## 10. LIGHTFARE instance (Story 158, Session 70)

Counting unit, verbatim from Story 155 (`docs/stories/155-lightfare-game-session70.md`):

> One play equals one Start from TITLE that begins level 1 of a new run.
> Retries after LOSE, advances after LEVELCLEAR, reloads, tab restores, WIN,
> and LOSE themselves never increment.

Run-start hook: one entry point, `enterRun()` (`website/games/lightfare.html`),
carrying the one and only `bumpPlays()` call. Both of its callers are Starts
from TITLE: the `#startBtn` click and the `Enter` key while `state === 'TITLE'`.
Its state guard (`if (state !== 'TITLE') return;`) is the single-transition
guard, so an auto-repeating `Enter` that lands in RUN finds no run-start
binding and does nothing. `retry()` (after an 80-move LOSE), `advance()`
(after LEVELCLEAR), `backToTitle()` (after WIN), `look()`, `move()`,
`render()`, reload, tab restore, and `window.__lightfare.reset()` never reach
`enterRun()` and never increment.

Boot-deal nuance: none. Boot reads both counters, loads level 1 into memory
for the TITLE preview, and renders `Plays on this browser: 0` and `Best: 0`.
Nothing is pre-dealt into play; `enterRun()` is what loads level 1 fresh
(`moves_used = 0`, `light = 15`) and enters RUN. The TITLE preview board is
not a play.

Display rule: one persistent HUD item inside `.hud`, outside `#panel`, so
title and end-panel swaps cannot erase it:
`<span class="item">Plays on this browser: <span id="plays">0</span></span>`.
Exact copy `Plays on this browser: N`, always rendered including 0 on a first
visit. Boot loads via `loadPlays()` then renders once; `renderPlays()` runs
only on boot and after `bumpPlays()`. The best line sits in the same HUD as
`Best: <span id="best">0</span>`. No plays line on the LEVELCLEAR, WIN, or
LOSE panels and no cross-device wording.

Key, cap, helper names: single key `flambeee-lightfare-plays` (sits beside
`flambeee-lightfare-best`, persisted as a JSON number), cap 9007199254740991,
helpers `playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`.
Sanitizer, boot-load-then-render, try/catch write, and silent blocked-storage
behavior match the snippet in section 2 (constants live on `CONFIG` as
`COUNT_KEY` / `BEST_KEY` / `COUNT_CAP` in this file). `best` rides the same
integer-within-cap rule through the shared `sanitizeCount()` guard.

LOSE-retry non-count: `retry()` reloads the current level only
(`moves_used = 0`, `light = 15`, same level index) and keeps `bank`, the
scores of already-cleared levels. It never increments.

LEVELCLEAR-advance non-count: `advance()` loads level N+1 fresh
(`moves_used = 0`, `light = 15`) with `bank` unchanged and the plays number
unchanged. It never increments.

WIN: entering WIN never increments; the run was counted at its start.
`backToTitle()` returns to TITLE with `bank` reset, so the next run starts
from TITLE through `enterRun()` and counts like every other run. One play
stays one run.

Formulas with units:

> plays_new [plays, integer] = min(plays_old [plays, integer] + 1 [play per
> Start from TITLE], 9007199254740991 [COUNT_CAP]). No other term exists.
> best [points] = max(bestStored [points], runTotal [points, 0..75]) [points],
> evaluated once at WIN, persisted as a JSON number under
> `flambeee-lightfare-best`.

Tuning table (section 10, LIGHTFARE instance):

| Name | Default | Min | Max | File location |
|---|---|---|---|---|
| Pattern section | 10 (LIGHTFARE instance) | n/a | n/a | docs/play-counter-pattern.md (appended after section 9) |
| COUNT_KEY | flambeee-lightfare-plays | n/a | n/a | website/games/lightfare.html (`CONFIG.COUNT_KEY`) |
| BEST_KEY | flambeee-lightfare-best (JSON number) | n/a | n/a | website/games/lightfare.html (`CONFIG.BEST_KEY`) |
| COUNT_CAP | 9007199254740991 | 9007199254740991 | 9007199254740991 | website/games/lightfare.html (`CONFIG.COUNT_CAP`) |
| Run-start hook | `enterRun()`, single `bumpPlays()` inside it | n/a | n/a | website/games/lightfare.html |
| CACHE_VERSION +1 | 32 to 33, same PR as the game file | n/a | n/a | website/sw.js (Story 156) |

Conflict rules: where this section and the shipped game file disagree, the
game file wins (established pattern-doc rule); fix the doc, never the game.
Section numbering clash: the next free section number wins; content
normative, number administrative.

Per-game checklist (the section 5 rows, LIGHTFARE values; every row filled
before merge):

| # | Item | LIGHTFARE value |
|---|---|---|
| 1 | Key suffix (middle slug) | `flambeee-lightfare-plays`, beside `flambeee-lightfare-best` |
| 2 | Display element id and placement | `#plays` inside the persistent `.hud` item `Plays on this browser: N`, beside the `#best` item |
| 3 | Run-start hook name | `enterRun()`, single `bumpPlays()` inside it, reached only from a Start on TITLE (button click or Enter), never from a page-load path |
| 4 | CACHE_VERSION +1 bump in `website/sw.js` | 32 to 33, same PR as the game change, plus one precache line `./games/lightfare.html` (23 to 24 entries) |
| 5 | No-network grep | `git diff main -- website/games/lightfare.html` reads clean: no network call and no external URL anywhere in the new file |

## 11. TRACE instance (Story 170, Session 73)

Counting unit: one play equals one Start from TITLE that enters DRAW of a
new run. Exactly one entry point, `enterDraw()`
(`website/games/trace.html`), carrying the one and only `bumpPlays()` call,
guarded by `if (state !== 'TITLE') return;`.

Never count: boot, reload, tab restore, short-stroke refusal, Clear, FORGE,
RUN moves, Walk again (same field, `walkAgain()`), New line (DRAW from an end
screen, `newLine()`), WIN, LOSE, back to TITLE. Redraws within a run never
count: the run was counted at its Start.

Display rule: one persistent HUD item inside `.hud`, outside `#panel` so
title/draw/run/end swaps cannot erase it:
`<span class="item">Plays on this browser: <span id="plays">0</span></span>`.
Exact copy `Plays on this browser: N`, always rendered including 0 on a first
visit. Boot loads via `loadPlays()` then renders once; `renderPlays()` runs
only on boot and after `bumpPlays()`. The best line sits in the same HUD as
`Best today: <span id="best">0%</span>`. No plays line on the WIN or LOSE
panels and no cross-device wording.

Key, cap, helper names: single key `flambeee-trace-plays` (sits beside
`flambeee-trace-best`, a JSON `{day, pct}` number pair, untouched by the
counter), cap 9007199254740991, helpers `playsMem`, `sanitizePlays`,
`loadPlays`, `renderPlays`, `bumpPlays`. Sanitizer, boot-load-then-render,
try/catch write, and silent blocked-storage behavior match the snippet in
section 2 (constants live on `CONFIG` as `COUNT_KEY` / `BEST_KEY` /
`COUNT_CAP` in this file).

Formulas with units:

> plays_new [plays, integer] = min(plays_old [plays, integer] + 1 [play per
> Start from TITLE], 9007199254740991 [COUNT_CAP]). No other term exists.

Tuning table (section 11, TRACE instance):

| Name | Default | Min | Max | File location |
|---|---|---|---|---|
| Pattern section | 11 (TRACE instance) | n/a | n/a | docs/play-counter-pattern.md (appended after section 10) |
| COUNT_KEY | flambeee-trace-plays | n/a | n/a | website/games/trace.html (`CONFIG.COUNT_KEY`) |
| BEST_KEY | flambeee-trace-best (JSON {day, pct}) | n/a | n/a | website/games/trace.html (`CONFIG.BEST_KEY`) |
| COUNT_CAP | 9007199254740991 | 9007199254740991 | 9007199254740991 | website/games/trace.html (`CONFIG.COUNT_CAP`) |
| Run-start hook | `enterDraw()`, single `bumpPlays()` inside it | n/a | n/a | website/games/trace.html |
| CACHE_VERSION +1 | 35 to 36, same PR as the game file | n/a | n/a | website/sw.js (Story 168) |

Conflict rules: where this section and the shipped game file disagree, the
game file wins (established pattern-doc rule); fix the doc, never the game.
Section numbering clash: the next free section number wins; content
normative, number administrative.

Per-game checklist (the section 5 rows, TRACE values; every row filled before
merge):

| # | Item | TRACE value |
|---|---|---|
| 1 | Key suffix (middle slug) | `flambeee-trace-plays`, beside `flambeee-trace-best` |
| 2 | Display element id and placement | `#plays` inside the persistent `.hud` item `Plays on this browser: N`, beside the `#best` item |
| 3 | Run-start hook name | `enterDraw()`, single `bumpPlays()` inside it, reached only from a Start on TITLE (button click or Enter/Space), never from a page-load path |
| 4 | CACHE_VERSION +1 bump in `website/sw.js` | 35 to 36, same PR as the game change, plus one precache line `./games/trace.html` (24 to 25 entries) |
| 5 | No-network grep | `git diff main -- website/games/trace.html` reads clean: no network call and no external URL anywhere in the new file |
