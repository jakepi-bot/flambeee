# Story 155: LIGHTFARE game (Session 70, P0)

**Status:** Ready for development (Session 70, 2026-11-23).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (user-visible; release gate for v0.57.0).
**Assigned to:** **Riven**, sole code owner. One PR shared with Story 156 (site card) and Story 158 (pattern-doc section 10).
**Base commit:** `23674a2` (main, v0.56.0 released).
**Scope:** `website/games/lightfare.html` (new single file: 5 hand-authored levels, look economy, counters, best) plus exactly one line in `website/sw.js` (`CACHE_VERSION` 32 to 33, shared with Story 156). No other website bytes.
**Design contract:** `flambeee-team/design-handoff.md`, Story 155 sections 1 through 6, plus level layouts in section 7 and decision record `docs/design-decisions/006-lightfare-retry-and-score-session70.md`. Design-owned observable criteria live in contract section 5 and are mapped here one for one.
**Pattern source:** `docs/play-counter-pattern.md` (Story 122, v0.45.0) as built by Stories 121/145/153.

## Summary

LIGHTFARE is the Session 70 product bet: a dark maze where information is the priced resource. The board is dark except for a 3x3 halo around the player; one full-board look costs light at a doubling price (1, 2, 4, 8); the light left at the exit is the score. Five hand-authored 7x7 levels, states TITLE / RUN / LEVELCLEAR / WIN / LOSE, one screen, keyboard plus on-screen pad, play counter plus best total, no network after load. Riven builds the game file; the exact copy and counting rule below are verbatim from the contract and must not be paraphrased.

## Exact copy (verbatim, do not reword)

- One-liner on TITLE: `Every look costs. Reach the exit with light to spare.`
- Look refused: `Not enough light.`
- LOSE line: `Out of moves.`
- WIN line: `Run complete. Total light: T.` (T is the run total)
- LEVELCLEAR line: `Level N clear. Light kept: X.`
- Plays line: `Plays on this browser: N`

Plain text, plain punctuation, no em dash, no emoji.

## Counting rule (verbatim, do not reword)

One play equals one Start from TITLE that begins level 1 of a new run. Retries after LOSE, advances after LEVELCLEAR, reloads, tab restores, WIN, and LOSE themselves never increment.

## Functional requirements

FR-1 (contract section 1, transitions 1-2). Boot loads plays and best (0 on first visit), renders both, lands on TITLE showing the one-liner. Boot never counts a play. Start from TITLE (`Enter` or button) loads level 1 with `moves_used = 0`, `light = 15`, enters RUN, and counts exactly 1 play through a single `enterRun()` helper carrying the one and only `bumpPlays()` call.

FR-2 (contract section 1, transition 3). RUN movement: stepping into a non-wall cell moves the player and `moves_used += 1`. Stepping into a wall is refused silently: position unchanged, `moves_used` unchanged, no message. Reaching E banks `score_L` and enters LEVELCLEAR.

FR-3 (contract section 1, transition 4; section 2 formulas). RUN look: if affordable, deduct the price, reveal the full board (every wall and E) for 1.0 s, then hide. A look pressed during an active reveal is ignored with no charge and no timer restart. A look pressed with insufficient light is refused with `Not enough light.`, no deduction, stay in RUN. Prices: 1st look 1, 2nd 2, 3rd 4, 4th 8 light (`lookPrice(k) = 2^(k-1)`); cumulative spend `2^n - 1` (0, 1, 3, 7, 15); the (n+1)-th look is allowed iff `lightLeft >= 2^n`. A 5th look is never affordable.

FR-4 (contract section 1, transitions 5-6; section 2 formulas). LEVELCLEAR shows `Level N clear. Light kept: X.` plus `Enter` hint. Advancing loads level N+1 fresh (`moves_used = 0`, `light = 15`) and re-enters RUN; never counts a play. After level 5's exit the run total is computed, best updated only if beaten, and WIN shows `Run complete. Total light: T.`. `score_L = lightLeft_L` at exit (0..15); `runTotal = sum(score_L, L = 1..5)` (0..75); `best = max(bestStored, runTotal)` evaluated once at WIN, persisted as a JSON number under `flambeee-lightfare-best`.

FR-5 (contract section 1, transition 7; decision 006 call 1). `moves_used` reaching 80 without reaching E enters LOSE immediately; LOSE shows `Out of moves.` plus retry hint. Retry resets the current level only (`moves_used = 0`, `light = 15`, same level index, banked scores from cleared levels kept) and re-enters RUN; never counts a play.

FR-6 (contract section 1, transition 8). Reload / tab restore follows the boot path only: re-read stored totals, land on TITLE, never count. A mid-run reload abandons the run; banked level scores are session-only, never persisted.

FR-7 (contract section 1, readable-state spec). The 3x3 halo around the player always shows the true content (wall / floor / exit) of those 9 cells; cells outside the halo expose no content. The currently banked total, current-level light, and moves used are readable as text at all times during RUN. No game meaning is carried by color alone. (Palette owns visuals; this is behavior and readable state only.)

FR-8 (contract section 2-3, counter discipline). Keys `flambeee-lightfare-plays` and `flambeee-lightfare-best`; cap 9007199254740991; helpers `playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays` matching the pattern-doc section 2 snippet (try/catch read plus sanitize, capped increment, try/catch write, boot load then render once including 0). Blocked/throwing storage: silent memory-only mode, plays and best count/track in memory for the session, no notice, no page-attributable console error. Corrupt values sanitize to 0. Formulas: `plays_new = min(plays_old + 1, 9007199254740991)` per Start-from-TITLE entry, no other term.

FR-9 (contract section 1, inputs). Keyboard: arrows/WASD move, Space looks, Enter starts/advances. Touch: on-screen pad (4-dir + LOOK) is the normative touch path; swipe, if shipped, steps exactly one cell per fling and never moves during reveal (ungated enhancement). Enter/Space auto-repeat on TITLE: first key enters RUN via `enterRun()`; repeats land in RUN where Enter has no run-start binding (single-transition guard).

FR-10 (contract section 3). Tuning table honored exactly: GRID 7x7 fixed, LEVEL_COUNT 5, LIGHT_BUDGET 15, LOOK_PRICES [1,2,4,8], REVEAL_MS 1000 (allowed range 500-2000, but ship 1000), MOVE_LIMIT 80, HALO_RADIUS 1, COUNT_KEY `flambeee-lightfare-plays`, BEST_KEY `flambeee-lightfare-best`, COUNT_CAP 9007199254740991. Widening REVEAL_MS or LIGHT_BUDGET is a Rook decision, not a dev tweak.

FR-11 (contract section 7). The five shipped layout strings, byte-exact (`#` wall, `.` floor, `S` start, `E` exit, 7 rows of 7):

L1 (BFS 8, par 1, open-pillars):
```
#######
#S....#
#.##..#
#..##.#
#..#..#
#....E#
#######
```
L2 (BFS 10, par 1, split):
```
#######
#S#..E#
#.#.#.#
#.#.#.#
#...#.#
#.###.#
#######
```
L3 (BFS 12, par 2, comb):
```
#######
#S#...#
#.#.#.#
#...#.#
#.#.#.#
#...#E#
#######
```
L4 (BFS 14, par 2, offset-columns):
```
#######
#S.#..#
#.#...#
#.#.#.#
#.#.#.#
#...#E#
#######
```
L5 (BFS 16, par 3, snake):
```
#######
#S....#
#####.#
#.....#
#.#####
#....E#
#######
```

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in contract section 5; AC-1 through AC-8 map them directly. AC-9 onward pin the formulas, inputs, storage discipline, and structural requirements. Each is verifiable from the product surface with real keys, clicks, and taps.

1. Given a fresh profile on TITLE, when the page loads, then the line `Every look costs. Reach the exit with light to spare.` is visible before the first input, plays and best read 0, and no play is counted. (design 5.1; FR-1)
2. Given RUN on any level with no look used, when the player has not looked, then exactly the 3x3 halo around the player shows true wall/floor/exit content and every other cell shows nothing. (design 5.2; FR-7)
3. Given RUN with full light (15), when the player looks once, then the whole board including E is revealed, it hides after about 1.0 s, and light reads 14. (design 5.3; FR-3)
4. Given RUN with 0 light left, when the player presses look, then the line `Not enough light.` shows, light stays 0, and play continues. (design 5.4; FR-3)
5. Given RUN, when the player walks into a wall, then position and moves used do not change and no message shows. (design 5.5; FR-2)
6. Given RUN with 80 moves used and no exit reached, when the state settles, then the screen reads LOSE with `Out of moves.`, and retry restarts the same level with light 15 while banked scores are kept. (design 5.6; FR-5)
7. Given level 5's exit reached, when the run ends, then WIN shows `Run complete. Total light: T.` where T is the sum of the five banked level scores, and best updates only if T beats it. (design 5.7; FR-4)
8. Given a counted run in progress, when the player reloads, then the plays line keeps its number, the page lands on TITLE, and the run is abandoned. (design 5.8; FR-6)
9. Given RUN with light 15, when the player looks four times, then light reads 0 (14, 12, 8, 0); when the player presses look a fifth time, then the refusal line shows, light stays 0, and the level remains completable halo-to-halo. (prices/spends; FR-3)
10. Given LEVELCLEAR after level N (N < 5), when the player advances, then level N+1 loads with moves 0 and light 15, the banked total is unchanged, and the plays number does not change. (FR-4; counting rule)
11. Given a zero-look solve of any level, when the exit is reached, then the level banks 15 (documented mastery edge; the plan's 0-14 holds for all play using at least one look). (decision 006 call 3; FR-4)
12. Given a reveal overlay showing, when the player presses any move or look input, then the inputs are ignored: position, moves used, and light do not change, and no second charge occurs. (decision 006 call 2; FR-3)
13. Given the on-screen pad on a touch viewport, when the player taps a direction, then the player steps exactly one cell (or is silently refused by a wall); when the player taps LOOK, then the FR-3 reveal runs. (decision 006 call 4; FR-9)
14. Given storage blocked for the site, when the player starts a run, looks, and finishes levels, then plays and best still track in memory for the session, no notice is shown, play continues, and no page-attributable console error is raised. (FR-8)
15. Given stored plays or best values of `"abc"`, bad JSON, a float, `null`, a negative, `NaN`, `Infinity`, an absent key, or an over-cap integer, when the page boots, then the corresponding line reads 0; given a stored numeric string (`"3"`), then the line shows that value. (FR-8 sanitizer)
16. Given the cap reached (9007199254740991), when a new run starts, then the count stays at the cap and never wraps. (FR-8)
17. Given `git diff main -- website/games/lightfare.html`, when the counter hunks are inspected, then there is exactly one `bumpPlays()` call site inside one `enterRun()` helper, the Start path routes through it, the LOSE-retry and LEVELCLEAR-advance paths do not, and no network API (fetch, XMLHttpRequest, sendBeacon, WebSocket, new external URL) appears. (FR-1; FR-8)
18. Given the merged tree, when `website/sw.js` is read, then `CACHE_VERSION` is 33 and the sw.js diff against main shows exactly the one-line bump shared with Story 156. (cache; shared with 156)
19. Given `git diff main --stat`, when the changed files are listed, then only `website/games/lightfare.html`, `website/sw.js` (one line), `website/index.html` (Story 156 card), and `docs/play-counter-pattern.md` (Story 158 section 10) changed; `GAME_ORDER` is byte-identical; no new storage key beyond the plays and best keys; no tuning constant differs from the contract table. (scope)
20. Given the five layout strings in the shipped file, when each is BFS-solved, then the shortest paths read exactly 8, 10, 12, 14, 16 and the designed par look counts (1, 1, 2, 2, 3) each stay within the 4-look cap. (contract section 6; FR-11)

## Edge cases

- Reveal timer vs hidden tab: `setTimeout` fires late under throttle; the board hides whenever the callback runs and no input is accepted meanwhile. Never extend the reveal to compensate. (contract section 4)
- Boot on a cached old shell: the old shell has no LIGHTFARE bytes until the Story 156 cache bump activates; versioned-out, not a bug. (contract section 4)
- Enter/Space auto-repeat on TITLE: single-transition guard, same shape as the Empty Hands double-click rule. (contract section 4; FR-9)

## Out of scope

No enemies, no timer beyond the 80-move limit, no daily seed, no streak, no meta-progression, no new storage key beyond plays and best, no `GAME_ORDER` change, no detail modal, no website redesign, no backlog merges except this docs PR. No visual decisions beyond readable state (Palette owns visuals). No mechanic, tuning, level, or copy invention beyond the contract.

## Traceability

Every contract clause is covered: section 1 transitions 1-8 map to FR-1 through FR-6 plus FR-9 (AC-1, AC-6 through AC-8, AC-10, AC-13); readable-state spec maps to FR-7 (AC-2); section 2 formulas map to FR-3, FR-4, FR-8 (AC-3, AC-4, AC-7, AC-9, AC-11, AC-14 through AC-16); section 3 tuning table maps to FR-10 (AC-19); section 4 edge cases map to AC-12, AC-13 and the Edge cases list above; section 5 design criteria map to AC-1 through AC-8; section 6 balance plan maps to AC-20 (executed by Story 157); section 7 layouts map to FR-11 (AC-20). Decision 006 calls 1-4 map to FR-5, FR-3, FR-4, and FR-9 (AC-6, AC-12, AC-11, AC-13).

## Evidence the dev must paste (in the PR)

- Fresh-profile boot: one-liner visible, plays 0, best 0, TITLE shown.
- Start: plays 1; reload keeps 1 on TITLE; LEVELCLEAR advance +0; LOSE retry +0 with same level and light 15, bank kept.
- Four looks spend 15 to 0; 5th refused with the verbatim line; level still completable.
- `enterRun()` grep: one helper, one `bumpPlays()` call site; retry/advance paths clean; network grep clean.
- `sw.js` diff: exactly one line, 32 to 33.
- BFS lengths 8/10/12/14/16 from the shipped strings; zero page-attributable console errors both viewports.

## Definition of done

- AC-1 through AC-20 all hold on the branch.
- PR contains only the new game file, the one `website/sw.js` line, the Story 156 card, and the Story 158 doc section; diff confirms zero other website bytes.
- Scout QA GO and Rook design review NO BLOCKING FINDINGS.
- Release wave reads back `CACHE_VERSION` 33 in the final tree.
- v0.57.0 may be cut on this story plus Story 156.
