# Story 142: EMPTY HANDS game file (Session 65, P0, user-visible)

**Status:** Build-ready (Session 65, 2026-11-18).
**Author:** Quinn (Business Analyst), Wave 1.
**Priority:** P0 (the user-visible build story this session; builds in the 01:55 dev wave).
**Assigned to:** **Riven** (SOLE code owner; holds the game file plus the Story 143 site-rider lines in one PR). Kai peers the PR.
**Base commit:** `1a7e7f6` (main, Session 64 merge of #261).
**Design contract:** `flambeee-team/design-handoff.md`, Section M (Rook; the contract wins on states, inputs, the turn sequence, formulas, tuning table, ladder, edge cases, and Plan B).
**Session plan:** `flambeee-team/session-plan.md`, Session 65 (2026-11-18), P0 item.
**Dependencies:** None. The dev wave branches from main after this half's docs PR merges.

## Context (why this story exists)

The catalog has nine games and no win condition built on subtraction. Every current win is accumulation or clearance by destruction. EMPTY HANDS is a turn-based ordering puzzle: a row of coins, a purse that only goes down, and a win state that is an empty board. Each gift makes every remaining coin 1 lighter (floor 1), so the skill is choosing which end to give from. The session ships only if the 200-seed gate returns the non-degenerate band before 02:45; if not, the mechanic is retired with a written decision and nothing ships.

## Scope

One new file: `website/games/empty-hands.html`. Single inline script block, top-of-file CONFIG object holding every gameplay number (M.3 table). No dependencies, no network after load, keyboard and touch parity, seeded deal, `window.__empty` test surface, best in localStorage only.

## Files (one PR with Story 143, Riven)

| File | Change | Owner |
|---|---|---|
| `website/games/empty-hands.html` | New game: states, inputs, turn sequence, dealer, shrink rule, purse rule, DP plus purse formula, ladder, score, best, test surface, layout, copy | Riven |

No other file in this story. Site card, copy line, cache bump, and precache line belong to Story 143 in the same PR.

## Functional requirements

### 1. States and transitions (contract M.1)

- FR-1. Four states plus transition overlay: TITLE (locked preview of level 1 board, single start action), RUN (one board in progress with row values, purse remaining, turn index, level), WIN overlay (row empty; one-line result plus purse remainder; single advance input), BUST overlay (score and best; single restart input). Level transition: WIN dismiss deals the next level row from the seed schedule with purse reset, score carried, level counter plus 1. Purse never carries across boards.
- FR-2. BUST triggers when neither end is affordable, or purse is 0 with coins left. Restart goes to TITLE or directly to level 1 RUN; Riven picks one and the harness asserts it.

### 2. Inputs (contract M.1)

- FR-3. Keyboard: LeftArrow or A gives the left end. RightArrow or D gives the right end. Enter or Space confirms on TITLE, advances past WIN, restarts after BUST. No other key acts.
- FR-4. Pointer and touch: tapping the leftmost coin gives left, tapping the rightmost coin gives right. Taps on middle coins are no-ops (no purse change, logged as ignored in the test surface). TITLE start, WIN advance, and BUST restart are full-width tap targets at least 44px tall.
- FR-5. No timing input, no drag, no multi-touch, no keyboard-plus-pointer combos.

### 3. Exact turn sequence (contract M.1, normative order)

- FR-6. The turn runs in this order only: (1) player selects an end; if the selected end exceeds the purse, reject with feedback and consume no turn; if NEITHER end is affordable, transition to BUST without consuming a turn. (2) Cost equals the current value of the chosen end coin. (3) Purse minus cost; spent plus cost. (4) Remove the chosen coin. (5) If the row is now empty, transition to WIN overlay. (6) Else decrement every remaining coin by 1 (floor 1), increment the turn index, re-render, stay in RUN.
- FR-7. Purse has a single mutation point (`purse -= cost`). No refunds, no regen, no carryover top-up, no level bonus added to the purse.

### 4. Dealer and seeded deals (contract M.2)

- FR-8. PRNG is mulberry32. Coin i value is `1 + floor(rand() * 9)` (VMAX 9, range 1 to 9 all levels). Run seed R is drawn once per run from crypto.getRandomValues (one uint32) and shown on TITLE and in the test surface. Per-level deal seed is `seed(L) = (R + L * 7919) mod 2^32`, L 1-based. Row length n(L) and slack(L) come from the M.4 ladder.
- FR-9. The dealer rejects nothing. Every deal is solvable by construction because purse(L) is at least optimal spend for every level (slack is never negative).

### 5. Shrink rule (contract M.2)

- FR-10. `val_at(v, t) = max(1, v - (t - 1))`, t the 1-indexed turn number within the board. SHRINK_STEP 1, SHRINK_FLOOR 1. Applied to every remaining coin after each gift.

### 6. Optimal spend and purse (contract M.2)

- FR-11. Interval DP over dealt row c[0..n-1]: turn for interval [i..j] of length len is `t = n - len + 1`; base `f(i,i) = val_at(c[i], n)`; recurrence `f(i,j) = min(val_at(c[i], t) + f(i+1, j), val_at(c[j], t) + f(i, j-1))`; optimal is f(0, n-1). Board purse is `purse(L) = optimal_spend(deal(L)) + SLACK[L]`. Integer only. The page DP exists only to set the purse at deal time and expose the optimal number to the harness; no auto-play, no hint, no suggested-end highlight may read solver output.

### 7. Level ladder and endless shape (contract M.4)

- FR-12. Ladder: L1 n=8 slack 3, L2 n=9 slack 2, L3 n=10 slack 1, L4 n=11 slack 0, L5 n=12 slack 0, L6 n=12 slack 0. Exactly this ladder, no extra levels, no difficulty select. After L6: endless L6-shape boards (n=12 slack 0) with the seed schedule continuing (L=7, 8, ...). No fixed victory screen. The run ends only on BUST.

### 8. Score (contract M.5)

- FR-13. Score is coins gifted this run: plus 1 per completed gift. Never decreases. Resets to 0 on a new run. Survives level advance. Purse remainder is shown but never scored.

### 9. Best and persistence (contract M.5)

- FR-14. Best is the max score across runs on this browser. Key `flambeee-empty-hands-best`. localStorage only. On BUST and on each WIN overlay, if score exceeds best, set best and write through inside try/catch, silent failure.
- FR-15. Read and sanitize on load: parse to integer; if the stored value is corrupt, negative, non-integer, null, or absent, use 0 and overwrite lazily on next write. try/catch silent. If storage is blocked, keep best in memory for the session, never throw, never show an error.
- FR-16. TITLE shows best. BUST shows score and best, plus a NEW BEST line only when beaten.

### 10. Test surface (contract M.6)

- FR-17. Ship read-only getters on `window.__empty`: state(), level(), purse(), spent(), score(), row() (copy of current values, left to right), rowLen(), seed(), dealSeed(), optimal(), purse0(), lastResult() (null, WIN, or BUST plus per-board spent and level), best(), cleared(), config(), accepts(seed, level) or solve(seed, level) (pure: no DOM, no state mutation, no randomness outside mulberry32), reset() (harness-only reset to TITLE, wired to no player input).

### 11. Layout, timing, network (contracts M.3, M.4, M.7)

- FR-18. Single row always, no wrap. 375px math: 26px coin plus 2px gap, hit area extended vertically to 26px wide by 44px tall. Overflow 0 asserted at 375x667.
- FR-19. Animation total per turn stays under 300ms (gift anim at most 120ms, shrink tick at most 120ms). No tick loop, no countdown, no reaction window. Inputs arriving while the gift animation is in flight are ignored with no purse change; rapid double-tap consumes one turn.
- FR-20. Zero network requests after the first load. Zero page-attributable console errors.
- FR-21. TITLE copy teaches the shrink rule in one line. Adopted line: "Every gift makes every coin left 1 lighter, down to 1." (M.11 wording resolved; see requirements handoff.)

### 12. No waiting action (contract M.1, M.11)

- FR-22. No pass, hold, skip, or undo input exists anywhere in the file or the DOM. The only RUN actions are give-left and give-right. The shipped file contains no pass/hold/skip/undo handler.

## BDD acceptance criteria

Threshold: 16 of 16 on the PR head. Each Then is observable in the product or via `window.__empty`.

- AC-1 (TITLE on first load). Given a fresh browser with empty storage, when the page loads, then TITLE shows a row of locked coins, a purse number, best 0, the one-line shrink rule, and a single start action, with no network activity after load.
- AC-2 (start run). Given TITLE, when the start action fires via Enter or tap, then state() reads RUN, level() reads 1, rowLen() reads 8, and purse() equals purse0().
- AC-3 (first gift accounting). Given RUN with affordable ends, when the player gives one end coin by keyboard, then purse() drops by exactly the shown coin value, the gifted coin leaves, and score() ticks up by 1 within 300ms.
- AC-4 (shrink visible). Given RUN after one gift, when the remaining coins are read via row(), then every survivor shows exactly 1 lower than before (or 1 if already 1).
- AC-5 (unaffordable end rejected). Given RUN where one end costs more than the purse, when the player selects that end, then purse(), score(), and row() are unchanged, no turn is consumed, and the other end remains playable.
- AC-6 (bust). Given RUN where neither end is affordable, when the state evaluates, then the BUST overlay shows score and best with a single restart action, and no further gift is possible.
- AC-7 (win). Given RUN with one coin left and purse covering it, when the player gives it, then the WIN overlay shows within 300ms with the purse remainder and a single advance action.
- AC-8 (level advance). Given a WIN overlay on level L, when the player advances, then a new row of the M.4 ladder length appears with a fresh purse, level() reads L+1, and score() carries over.
- AC-9 (endless L6). Given a WIN overlay on level 6, when the player advances, then a fresh n=12 slack-0 board deals from the continuing seed schedule, level() reads 7, and the run continues until BUST.
- AC-10 (seeded determinism). Given run seed R, when accepts(R, L) is called twice for any level L, then both calls return the identical row, optimal, and purse, and the dealt board matches accepts(R, L).
- AC-11 (purse never rises). Given any full run watched through `window.__empty`, when any gift, level advance, or overlay transition happens, then the on-board purse number never increases; a fresh purse per board starts at its dealt value and only falls.
- AC-12 (best persistence). Given a run that sets a new best, when the player reloads the page, then TITLE shows the kept best number and best() agrees with storage.
- AC-13 (corrupt best sanitized). Given a stored best that is corrupt, negative, or non-integer, when the page loads, then best() reads 0, the game plays normally, and no error surfaces.
- AC-14 (keyboard-only path). Given TITLE, when the player uses only Left/Right/Enter keys, then a full board can be started, cleared or busted, and advanced past, with no pointer needed.
- AC-15 (touch parity and layout). Given a 375px viewport, when the player taps end coins, then each tap registers the correct end, middle-coin taps change nothing, and desktop 1280x800 plus mobile 375x667 both show overflow 0.
- AC-16 (no waiting action, no network, no errors). Given the shipped file, when the DOM and script are inspected, then no pass, hold, skip, or undo control or handler exists; when the page runs, then zero network requests fire after first load and zero page-attributable console errors appear.

## Design criteria map (Rook M.8, by reference, not duplicated)

Rook's twelve observable scenarios in M.8 are player-verifiable checks on this same build; the AC above is the developer-testable form. Map: M.8-1 first load by AC-1; M.8-2 first gift by AC-3; M.8-3 shrink by AC-4; M.8-4 unaffordable end by AC-5; M.8-5 win by AC-7; M.8-6 bust by AC-6; M.8-7 level advance by AC-8; M.8-8 best persistence by AC-12; M.8-9 keyboard by AC-14; M.8-10 touch by AC-15; M.8-11 no waiting action by AC-16; M.8-12 purse never rises by AC-11. Rook's design review runs M.8 after the PR opens; blocking findings gate the release wave.

## Completion checklist

- [ ] `website/games/empty-hands.html` created; no other file touched in this story
- [ ] CONFIG holds every M.3 number; purse has one mutation point
- [ ] Ladder L1-L6 plus endless L6-shape per FR-12
- [ ] `window.__empty` ships all M.6 getters; accepts/solve is pure
- [ ] AC-1 through AC-16 recorded pass in the build PR body with live pasted output, 16 of 16
- [ ] TITLE teaches the shrink rule in one line
- [ ] Zero network after load, zero console errors, overflow 0 both viewports
- [ ] Kai peer review; Rook design review against Section M

## Cut line (binding, from session-plan)

Floor: this file with the ruled states, seeded deal, visible strictly-decreasing purse, shrink rule, WIN/BUST, best in localStorage, plus the Story 143 site rider and the Story 144 gate green on all seven checks. Ceiling, in cut order: ladder beyond level 6, end-screen term breakdown, daily seed, share card, sound, extra mobile layout. Hard out: gate not green by 02:45 ships nothing; mechanic moves to Friday with the failure numbers written down.

## Out of scope

- No site card, copy change, cache bump, or precache line (Story 143, same PR).
- No proof harness or seed manifest (Story 144, Kai).
- No persistence beyond the single best key; no play counter (#215 stays open).
- No What's New edit (release wave owns it).
- No FPS or controller claim anywhere; `echo-rounds.html` byte-identical.
- No `cinder.html`, cadence, or `website/apps/` edits.
- No tick loop, timing bar, hold move, or difficulty select (a hold move is a new mechanic and a new gate, never a patch).
- No visual redesign. Palette owns visual direction; behavior and readable state only.

## Open questions

None blocking. The two M.11 wording points are resolved in the requirements handoff (distinct WIN/BUST verbs; TITLE shrink line adopted verbatim) so Riven is not blocked.

## References

- `flambeee-team/session-plan.md`, Session 65 (2026-11-18): P0 game file, jakebot advisory session `local-84a1083cf3d04ea1a1a87afcabcbd9cb70d5254a98a04b24c462b59d1a6be94`, cut line, hard outs, falsifying gate.
- `flambeee-team/design-handoff.md`, Section M (Rook): states and turn sequence (M.1), formulas (M.2), tuning table (M.3), ladder (M.4), scoring and best (M.5), test surface (M.6), edge cases and Plan B (M.7), design criteria (M.8), gate contract (M.9), originality (M.10), contested calls (M.11).
