# Story 153: EMPTY HANDS counts plays and drops the dead BUST arm (Session 69, P0, #276)

**Status:** Ready for development (Session 69, 2026-11-22).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (user-visible; release gate for v0.56.0).
**Assigned to:** **Riven**, sole code owner (Story 048 protocol). One PR shared with the cache line and the pattern-doc section only.
**Base commit:** `7ee3571` (main, v0.55.0 released).
**Scope:** `website/games/empty-hands.html` (counter block, one HUD element, one `enterRun()` helper with the single `bumpPlays()` call, `window.__empty.plays()` probe, #276 dead-arm cleanup in `showEnd()`) plus exactly one line in `website/sw.js` (`CACHE_VERSION` 31 to 32) plus one section in `docs/play-counter-pattern.md` (Empty Hands instance, section 9). No other website bytes.
**Design contract:** `flambeee-team/design-handoff.md`, Story 153 sections 1 through 11. Design-owned observable criteria live in contract section 10 and are mapped here; the functional AC below test the same behavior from the product surface.
**Pattern source:** `docs/play-counter-pattern.md` (Story 122, v0.45.0) and Story 121 as built (PR #220), plus the Cinder instance (Story 145, Session 66).

## Summary

EMPTY HANDS is the only modern game without a local play counter, so the team cannot tell a played game from an unplayed one and L4+ findability stays a guess (#265 item 2). Add the proven local play counter: one play equals one entry into RUN that begins a new run, with exactly two entries (the Start click from TITLE on the boot-dealt level-1 board, and the BUST restart with a fresh seed), both routed through a single `enterRun()` helper carrying the one and only `bumpPlays()` call. The persistent HUD shows `Plays on this browser: N`, always including 0 on a first visit. The same file loses the dead `kind == 'WIN'` arm that #276 recorded, and the same PR bumps the service-worker cache so returning visitors get the new file.

## Baseline measured at Session 69 planning (Wave 1, 2026-11-22)

| Check | Value |
|---|---|
| Base commit | `7ee3571` (main, v0.55.0) |
| Plays key on base | `flambeee-empty-hands-plays` absent (RED anchor) |
| Plays text on base | no `Plays on this browser:` in `empty-hands.html` or its DOM (RED anchor) |
| Other plays keys on base | `flambeee-empty-hands-best` (integer) only; no plays line, no plays key, no plays helper |
| Shipped counters elsewhere | `flambeee-typewreck-plays`, `flambeee-afterglow-plays`, `flambeee-cinder-plays` |
| States | `TITLE/RUN/WIN/BUST` (`empty-hands.html:244`) |
| Boot path | `newRun(false)` (line 529) deals a level-1 board via `startBoard()`, lands on TITLE |
| Start path | Start click (`elStart`, line 459) flips TITLE to RUN on the pre-dealt board |
| BUST restart path | `elAgain` (line 468) calls `newRun(true)`: fresh run seed, level 1, RUN |
| WIN advance path | `advance()` (line 450) deals the next level inside the same run |
| Probe on base | `window.__empty` (line 488), 19 members, no plays getter |
| `showEnd()` dead arm | line 350 sits inside the `else` branch of `if (kind === 'WIN')`, so the `kind == 'WIN'` arm can never be true; behavior correct today, cleanup only (#276) |
| `website/sw.js` `CACHE_VERSION` | 31 (bump to exactly 32) |
| `./games/empty-hands.html` precache | present (`sw.js:47`), so the game edit needs the bump |
| `GAME_ORDER` | byte-identical; no tuning change |

## Requirements

### 1. Counting rule (the one thing that needs care)

One play equals one entry into RUN that begins a new run. Exactly two entries:

(a) the Start click from TITLE, which plays the level-1 board dealt at boot;
(b) the BUST restart (`New run (Enter)`), which draws a fresh seed and deals level 1.

Both go through a single `enterRun()` helper carrying the one and only `bumpPlays()` call. Not counted: page load and boot deal, the TITLE preview, `advance()` after a WIN (same run, next row), reload, tab restore, `window.__empty.reset()`. BUST and WIN themselves never increment; the run was counted at its start. `give()`, `endBoardWin()`, `endRunBust()`, and `render()` never call `bumpPlays()`.

Verbatim contract rule, kept in this file so the dev cannot implement it two ways: one play equals one entry into RUN that begins a new run. Exactly two entries: (a) the Start click from TITLE, which plays the level-1 board dealt at boot; (b) the BUST restart, which draws a fresh seed and deals level 1. Both go through a single `enterRun()` helper carrying the one and only `bumpPlays()` call. Not counted: page load/boot deal, TITLE preview, `advance()` after WIN, reload, tab restore, `__empty.reset()`.

State diagram (contract section 1, normative):

```
[load] --newRun(false)--> TITLE --enterRun()/bumpPlays()--> RUN
  RUN --give() clears row--> WIN --advance() (no count)--> RUN (level+1, same R)
  RUN --neither affordable / purse out--> BUST --newRun(true) via enterRun()/bumpPlays()--> RUN (level 1, fresh R)
  any --reload/restore/reset()--> TITLE (no count)
```

### 2. Display element and exact copy

- One persistent HUD element: `<span class="item">Plays on this browser: <span id="plays">0</span></span>` (preferred form), inside `.hud`, outside `#panel` so title/end swaps cannot erase it.
- Exact copy: `Plays on this browser: N`. Plain text, plain punctuation, no em dash, no emoji.
- Always rendered, including `Plays on this browser: 0` on a first visit. Boot loads then renders once before any autostart-equivalent path.
- No second plays line on the end panel. No wording implying cross-device or global data (never `Total plays`, `Players`, or similar).
- Readable-state note (Palette owns visuals): the line is a HUD item like Level/Purse/Score/Best; no color-only meaning is attached to it.

### 3. Persistence shape

- Key: `flambeee-empty-hands-plays`. Single key. No second key, no per-level key, no save-schema change. Best stays at `flambeee-empty-hands-best`, untouched.
- Cap: `COUNT_CAP = 9007199254740991` (max safe integer). Increment never wraps.
- Helpers (pattern names, game file only): `playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`.
- Sanitizer, exactly the pattern-doc section 2 rule:

```js
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
```

- `loadPlays`: try/catch read of `COUNT_KEY`, `null`/`undefined` yields 0, `JSON.parse` in inner try/catch (bad JSON yields 0), `sanitizePlays` on the parsed value, outer catch yields 0.
- `bumpPlays`: `playsMem = Math.min(playsMem + 1, COUNT_CAP)`, try/catch `localStorage.setItem(COUNT_KEY, JSON.stringify(playsMem))`, then `renderPlays()`.
- `renderPlays` sets the `#plays` line to `Plays on this browser: N` at the current `playsMem`.

Formulas with units (contract section 7): `plays_new [plays, integer] = plays_old [plays, integer] + 1 [play per run-start entry]`; cap `plays_new = min(plays_old + 1, 9007199254740991) [plays]`; sanitize mapping: integer `v` in `[0, 9007199254740991]` passes through, non-empty numeric string `s` with `Number(s)` an integer in range passes at that value, everything else maps to `0 [plays]`; displayed `N [plays, integer] = playsMem` at render time.

### 4. Probe addition

Add `plays: function () { return playsMem; }` to `window.__empty` (read-only; 19 members become 20). No other probe change. `reset()` keeps its current behavior and never counts.

### 5. #276 rider (same PR, same file)

In `showEnd()`'s bust branch, replace the dead ternary with:

```js
elEndTitle.textContent = (purse <= 0) ? 'OUT OF COINS' : 'PURSE SHORT';
```

Behavior-identical: `purse` is always >= 0 (the only spend point returns early when `cost > purse`, and BUST is entered with 0 or more coins), so `purse <= 0` and `purse == 0` agree on every reachable state. Do not touch the BUST entry predicate in `give()`, `endLines`, or the WIN arm. The `if (kind === 'WIN')` structure is unchanged; only the dead `kind == 'WIN'` arm inside the else branch goes.

### 6. Cache

`CACHE_VERSION` 31 to 32 in `website/sw.js`, exactly one line, same PR. Load-bearing: `./games/empty-hands.html` is precached (`sw.js:47`); without the bump, returning visitors keep the old shell with no plays line.

### 7. Docs rider (same PR)

`docs/play-counter-pattern.md` gains a section 9 "Empty Hands instance (Story 153, Session 69)": counting unit (one new run: Start or BUST restart), the boot-deal nuance (the level-1 board is dealt before Start; boot itself never counts), display rule (persistent HUD item, exact copy, always rendered), key/cap/helper names, and the WIN-advance non-count.

### 8. Boundaries

- No change to scoring, ladder, purse, slack, N_PER_LEVEL, VMIN/VMAX, animation timings, or any tuning constant. `GAME_ORDER` byte-identical. No new storage key other than `flambeee-empty-hands-plays`. No animation change.
- Exact copy strings only: `Plays on this browser: N`, `OUT OF COINS`, `PURSE SHORT`, `ROW CLEAR`. Plain punctuation, no em dash, no emoji.
- Inputs unchanged: Start click, Enter/Space keydown (no ctrl/meta/alt), Again click, Give L/R, page load/reload/tab restore, `__empty.reset()`.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 10; AC-1 through AC-7 map them directly. AC-8 onward pin the section 9 unhappy paths and the structural requirements. Each is verifiable from the product surface with real clicks and keys.

1. Given a fresh browser profile on the game page, when the page finishes loading, then the HUD shows `Plays on this browser: 0`, the title panel is visible, `__empty.plays()` is 0, and no plays key need exist in storage. (design 10.1; first visit)
2. Given a fresh profile on TITLE, when the player clicks Start, then the HUD shows `Plays on this browser: 1`, `__empty.plays()` is 1, `localStorage['flambeee-empty-hands-plays']` is the JSON number `1`, and the run begins on the previewed board. (design 10.2)
3. Given a counted run in progress, when the player reloads the page (or the tab is restored), then the HUD shows the same number as before the reload, the page lands on TITLE, and nothing increments. (design 10.3; boot path never calls `bumpPlays()`)
4. Given a run that ends in WIN, when the player clicks `Next row (Enter)` (or presses Enter/Space on the WIN panel), then the next level begins in RUN in the same run and the plays number does not change. (design 10.4)
5. Given a run that ends in BUST, when the player clicks `New run (Enter)` (or presses Enter/Space on the BUST panel), then a new level-1 run begins with a fresh seed and the plays number increases by exactly 1. (design 10.5)
6. Given a BUST end panel with an empty purse, when the panel renders, then its title reads `OUT OF COINS`; given a BUST end panel with coins left but neither end affordable, then its title reads `PURSE SHORT`. (design 10.6; #276)
7. Given storage blocked for the site, when the player starts a run, then the HUD still increments for the session, no error message is shown, play continues, and no page-attributable console error is raised. (design 10.7)
8. Given a fresh profile, when the page boots and the TITLE preview board is dealt, then the count stays 0; given any state, when `__empty.reset()` runs, then the page returns to TITLE on a fresh preview board and the count does not change. (boot deal and reset never count)
9. Given TITLE, when the player double-clicks Start (or the Enter key auto-repeats on TITLE), then the count increases by exactly 1: the second activation lands on RUN where Start has no run-start binding. (single-transition guard)
10. Given a BUST panel, when the player restarts via the Again button versus via Enter, then either path increases the count by exactly 1 and both route through the same `enterRun()` path. (no per-input counting)
11. Given any play session, when BUST or WIN renders, then rendering alone never increments; `give()`, `endBoardWin()`, `endRunBust()`, and `render()` contain no `bumpPlays()` call. (the run was counted at its start)
12. Given stored values `"abc"`, bad JSON, a float (1.5), a non-numeric string, `null`, a negative (-1), `NaN`, `Infinity`, an absent key, or an over-cap integer, when the page boots, then the line shows `Plays on this browser: 0`; given a stored numeric string (`"3"`), then the line shows that value; given a stored absurd but valid integer (999999999), then the line shows it and the next entry increments from it. (sanitizer rule)
13. Given the cap reached (9007199254740991), when a new run starts, then the count stays at the cap and never wraps; given quota exceeded on write, when a run starts, then in-memory `playsMem` still increments and renders while the write drops silently, and the next boot re-reads the last persisted value. (cap and quota)
14. Given storage cleared between sessions, when the page boots, then the counter restarts at 0 with no error and no recovery. (defined restart)
15. Given the merged tree, when I read `website/sw.js`, then `CACHE_VERSION` is 32 and `git diff main -- website/sw.js` shows exactly one changed line (31 to 32). (cache)
16. Given the merged tree, when I inspect `window.__empty`, then it exposes 19 members including a read-only `plays()` getter returning `playsMem`, and `reset()` behavior is unchanged. (probe)
17. Given `git diff main -- website/games/empty-hands.html`, when I inspect the counter hunks, then there is exactly one `bumpPlays()` call site inside one `enterRun()` helper, the Start path and the BUST restart path both route through it, the display element sits in the persistent HUD outside `#panel`, and there is no second plays line in the end panel. (single helper, placement)
18. Given the merged tree, when I read `docs/play-counter-pattern.md`, then its new Empty Hands section states the counting unit (one new run: Start or BUST restart), the boot-deal nuance, the display rule with exact copy, the key/cap/helper names, and the WIN-advance non-count. (docs rider)
19. Given `git diff main --stat`, when I list changed files, then only `website/games/empty-hands.html`, `website/sw.js` (one line), and `docs/play-counter-pattern.md` (one section) changed; `GAME_ORDER` is byte-identical; no new storage key other than `flambeee-empty-hands-plays`; a network-API grep of the diff reads clean. (scope)
20. Given the full existing EMPTY HANDS proof harness on the branch, when it runs on both viewports, then gates 1 through 7 stay green with zero page-attributable console errors. (no game movement)

## Evidence the dev must paste (in the PR)

- Fresh-profile boot: line reads `Plays on this browser: 0`, `__empty.plays()` 0, title panel visible.
- Start click: line reads 1, probe 1, `localStorage` JSON number 1; reload keeps 1 on TITLE.
- WIN advance: count unchanged; BUST restart: exactly +1, fresh level-1 seed.
- `enterRun()` grep: one helper, one `bumpPlays()` call site; `give()`, `endBoardWin()`, `endRunBust()`, `render()` clean.
- `__empty` member count: 19 with read-only `plays()`.
- `sw.js` diff: exactly one line, 31 to 32.
- Pattern-doc section 9 present with the five required contents.
- Existing harness green on both viewports, zero page-attributable console errors.

## Definition of done

- AC-1 through AC-20 all hold on the branch; counts exact on every path, sanitizer cases all resolve as stated.
- PR contains only `website/games/empty-hands.html`, the one `website/sw.js` line, and the pattern-doc section; diff confirms zero other website bytes.
- Scout QA GO and Rook design review NO BLOCKING FINDINGS.
- Release wave reads back `CACHE_VERSION` 32 in the final tree.
- v0.56.0 may be cut on this story only if the counter is visible and correct in the shipped tree (session-plan release gate).

## Out of scope

- Echo Rounds / SALTLINE counters, Empty Hands detail view (follow-up B), any tuning constant, any scoring change, `GAME_ORDER`, any other website bytes, any `BLOG.md` or release text in this half.
- The proof-harness gate (Story 154, Kai) rides in its own file and never blocks this story.
