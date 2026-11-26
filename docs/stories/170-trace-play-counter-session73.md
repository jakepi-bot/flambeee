# Story 170: TRACE play counter (Session 73, P2, cut first)

**Status:** Ready for development (Session 73, 2026-11-26).
**Author:** Quinn, Business Analyst.
**Priority:** P2, cut first. If the wave runs short, this story is cut before anything else. It is instrumentation, not the game.
**Assigned to:** **Riven**, sole code owner. File: `website/games/trace.html` only, plus pattern-doc Section 11 in `docs/play-counter-pattern.md`. Rides the 166 PR; CACHE_VERSION rides the 168 bump (35 to 36).
**Base commit:** `d5e8b63` (main, v0.59.0).
**Scope:** One HUD line `Plays on this browser: N` following `docs/play-counter-pattern.md` sections 9 and 10 shape: one key `flambeee-trace-plays`, cap 9007199254740991, one `bumpPlays()` inside the single entry helper, boot/reload/advance/walk-again/new-line/win/lose/retry never count. Pattern doc gains section 11.
**Design contract:** `flambeee-team/design-handoff.md`, Section 5 (Story 170). Acceptance criteria map the contract one for one.
**Non-blocking rule:** this story is cut first and its cut is silent: the game ships whole without it. If it lands, Scout covers it in the release wave.

## Summary

This story counts how many runs this browser has started, nothing more. One line in the HUD always shows the count, starting at zero on a first visit. Pressing Start from the title screen adds exactly one. Nothing else adds to it: not restarting the same level, not drawing a new line, not winning or losing, not reloading the page. The count lives only in this browser under one key, stops at a fixed cap instead of wrapping, and fails silently to memory if storage is blocked. If the session runs short, this story is the first thing dropped and nobody misses it.

## Story

As a player, I see one persistent plays line so I know how many runs I have started on this browser.

## Functional requirements

FR-1 (contract Section 5, counting unit). One play equals one Start from TITLE that enters DRAW of a new run. Single `bumpPlays()` call inside the single run-entry helper `enterDraw()`, guarded by `if (state !== 'TITLE') return;`. Never count: boot, reload, tab restore, short-stroke refusal, Clear, FORGE, RUN moves, Walk again (same field), New line (DRAW from an end screen), WIN, LOSE, back to TITLE. Redraws within a run never count: the run was counted at its Start.

FR-2 (contract Section 5, display). One persistent HUD item outside the panel so title and end swaps cannot erase it: `<span class="item">Plays on this browser: <span id="plays">0</span></span>`. Exact copy `Plays on this browser: N`, always rendered including 0 on a first visit. Boot loads via loadPlays then renders once; renderPlays runs only on boot and after bumpPlays.

FR-3 (contract Section 5, key cap helpers). Single key `flambeee-trace-plays` beside BEST_KEY, cap 9007199254740991, helpers playsMem, sanitizePlays, loadPlays, renderPlays, bumpPlays. Sanitizer accepts plain numbers and plain numeric strings that are non-negative integers within cap, else 0. Capped increment `P := min(P + 1, 9007199254740991)`, try/catch write, silent memory fallback. Constants live on CONFIG as COUNT_KEY and COUNT_CAP. Formula: `plays_new [plays] = min(plays_old [plays] + 1 [play per Start from TITLE], 9007199254740991)`. No other term exists.

FR-4 (contract Section 5, pattern checklist). Key `flambeee-trace-plays`; display `#plays` in the persistent HUD item; hook `enterDraw()` single bumpPlays after the TITLE guard, never a click handler or page-load path; CACHE_VERSION rides the 168 bump (35 to 36) since it ships in the same PR; no-network grep over the new file reads clean. Pattern doc gains section 11 with the TRACE instance values.

## Acceptance criteria (BDD, observable in product)

1. Given TITLE, when the player starts, then the plays line increments by exactly 1. (contract Section 5.1)
2. Given WIN or LOSE, when the player picks Walk again or New line, then the plays line is unchanged. (contract Section 5.2)
3. Given boot with `flambeee-trace-plays` holding corrupt JSON, when the page loads, then the line reads `Plays on this browser: 0`. (contract Section 5.3)
4. Given boot with storage throwing, when the player starts twice, then the line reads 2 for the session and no error surfaces. (contract Section 5.4)
5. Given a first visit, when the page boots, then the line reads `Plays on this browser: 0` before any start.
6. Given RUN, when the player moves, wins, or loses, then the plays line is unchanged (the run was counted at its start).
7. Given the plays line at the cap 9007199254740991, when the player starts, then the line stays at the cap and never wraps.
8. Given the merged PR, when the reviewer runs the no-network grep over the new file, then it reads clean, and `docs/play-counter-pattern.md` holds the new section 11 with the TRACE instance values.

## Out of scope (NOT DOING)

No count on Walk again or New line. No count on boot, reload, tab restore, short-stroke refusal, Clear, FORGE, RUN moves, WIN, LOSE, or back to TITLE. No second key, no per-day key, no cross-device wording (never "Total plays" or "Players"). No plays line on end screens. No CACHE_VERSION bump of its own (rides the 168 bump). If cut, no stub ships in its place.

## Dependencies

Depends on: Story 166 (same PR; the `enterDraw()` hook and HUD slot this story fills). Cut first per the session cut order; the game ships whole without it.

## Notes

Normative source is contract Section 5; helper and copy discipline follows `docs/play-counter-pattern.md` sections 9 (Empty Hands instance) and 10 (LIGHTFARE instance), with TRACE values recorded as new section 11.
