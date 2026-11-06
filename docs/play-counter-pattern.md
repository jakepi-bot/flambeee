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

One game-agnostic shape. Copy it, rename nothing but the
slug, the element, and the hook call site:

```js
var COUNT_KEY = 'flambeee-<slug>-plays';
var COUNT_CAP = 9007199254740991; /* max safe integer, increment stops here, never wraps */
var plays = 0;

function loadPlays() {
  try {
    var raw = localStorage.getItem(COUNT_KEY);
    if (raw === null || raw === undefined || raw === '') return 0;
    var v = JSON.parse(raw);
    if (typeof v !== 'number' || !isFinite(v) || Math.floor(v) !== v || v < 0) return 0;
    return Math.min(v, COUNT_CAP);
  } catch (e) { return 0; }
}

function renderPlays() {
  playsEl.textContent = 'Plays on this browser: ' + plays;
}

function countPlay() {
  plays = Math.min(plays + 1, COUNT_CAP);
  try { localStorage.setItem(COUNT_KEY, JSON.stringify(plays)); } catch (e) {}
  renderPlays();
}

/* boot: load, then render once (renders 0 on a first visit) */
plays = loadPlays();
renderPlays();

/* run-start hook, after the validation gate (Typewreck: inside startAiming()): */
countPlay();
```

Notes on the snippet:

- `loadPlays` parallels `loadBest`: try/catch read, sanitize, 0 fallback.
- `countPlay` parallels `saveBestIfBeats`: try/catch write, then render.
- `renderPlays` runs on boot and after every increment. No other render site.
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
| 3 | Run-start hook name | `startAiming()` (typewreck.html line 425), single `countPlay()` call after the validation gate | That game's function that resets score and enters play. Never a click handler, never a page-load path |
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
| Corrupt stored value (bad JSON, wrong shape, float, string, null) | Treat as 0, apply the current increment normally, overwrite with the clean value. Never renders garbage |
| Negative stored value | Treat as 0, same path as corrupt |
| Absurd but valid integer (for example 999999999) | Accept and increment from it. Only non-finite, non-integer, or negative values reset to 0. The cap bounds growth |
| Two tabs open at once | Last write wins. Each tab holds its own in-memory P. At most one count lost. Documented as acceptable; never add locking |
| Storage cleared between sessions | Counter restarts at 0. Defined, no recovery, no error |
| Cached old shell served | Expected until the CACHE_VERSION bump activates. Old shell shows no plays line; that is the versioned-out state, not a bug |
| `?start=1` autostart | Counts as a play. It is a real run start through the same hook. Harness authors must account for it |

## Consistency

This doc is consistent with Story 121 as specified in
design-handoff.md sections 1-10. Story 121 was still in progress
when this doc was written; any conflict between this doc and
Story 121 as built resolves in favor of Story 121 as built.
