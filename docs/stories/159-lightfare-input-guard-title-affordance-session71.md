# Story 159: LIGHTFARE input guard and TITLE affordance (Session 71, P0)

**Status:** Ready for development (Session 71, 2026-11-24).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (user-visible input defect plus first-time-player dead end; ships in v0.58.0).
**Assigned to:** **Riven**, sole code owner. File: `website/games/lightfare.html` only. Zero other files.
**Base commit:** `582171b` (main, v0.57.0).
**Scope:** Issue #285 items 2 and 3: `preventDefault` for arrow/WASD keys in every state, and a plain readable message plus state-safe response when the pad or LOOK is tapped on TITLE.
**Design contract:** `flambeee-team/design-handoff.md`, Section 1 (Story 159, subsections 1.1 through 1.6). Design-owned observable criteria live in contract subsection 1.5 and are mapped here one for one.
**Non-blocking rule:** none for this story; 159 is never cut. If Story 160 runs long, its HUD item may be cut, never this story.

## Summary

LIGHTFARE shipped with two input defects from design review finding #285. First, the keydown handler returns at `if (!isMove || state !== 'RUN') return;` before `preventDefault()`, so arrow and WASD keys scroll the page in every non-RUN state. Second, the on-screen pad and LOOK button are visible but inert on TITLE with no message, a dead end for a first-time player at second three. This story closes both: all 12 move keys (4 arrows plus WASD in both cases) call `preventDefault()` in all 5 states (TITLE, RUN, LEVELCLEAR, WIN, LOSE) while keeping every existing transition unchanged, and a pad or LOOK tap on TITLE renders the exact string `Press Start to play. Use the pad once your run begins.` in the existing `#msg` element without starting a run, changing state, counting a play, moving the player, or spending light. Plan A is the tap-driven message; Plan B (static TITLE-panel sentence) applies only if the render path forces it, and Riven records the pick in the PR.

## Baseline measured at Session 71 planning (Wave 1, 2026-11-24)

| Check | Value |
|---|---|
| Base commit | `582171b` (main, v0.57.0) |
| Game file | `website/games/lightfare.html`, 593 lines |
| `CONFIG` | `LIGHT_BUDGET 15`, `LOOK_PRICES [1,2,4,8]`, `MOVE_LIMIT 80` at lines 167-170 (untouched) |
| Keydown handler | lines 503-538; returns before `preventDefault()` when `state !== 'RUN'` (the defect) |
| HUD | 7 items (Level, Light, Moves, Looks, Bank, Best, Plays) |
| `#board` | `max-width: 336px`; pad is 3x58 px cells; `#btnLook` follows the pad; body padding 12 px |
| `#msg` element | `#msg { min-height: 22px; ... color: #ff9a9a; }`, line 63 CSS, line 134 DOM |
| TITLE tap message string | `Press Start to play. Use the pad once your run begins.` (53 characters) |
| Guarded keys | 14 distinct `e.key` values (`ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, `w`, `W`, `a`, `A`, `s`, `S`, `d`, `D`, `Enter`, ` `) |
| Viewports for verification | desktop 1280x800, mobile 375x667 with touch |

## Functional requirements

FR-1 (contract 1.1, transitions 1-2). In RUN with no reveal active, arrows and WASD call `move()` exactly as today, and `e.preventDefault()` fires for every one of the 12 move keys whenever `state === 'RUN'`, including while a reveal is active (movement stays ignored, scroll stays suppressed). In TITLE, LEVELCLEAR, WIN, and LOSE, every one of the 12 move keys calls `e.preventDefault()` and does nothing else: no move, no state change, no message, no scroll.

FR-2 (contract 1.1, transition 3). Enter behavior is unchanged: with no button focused, Enter on TITLE calls `enterRun()`, on LEVELCLEAR `advance()`, on LOSE `retry()`, on WIN `backToTitle()`, and does nothing in RUN. With a button focused, the native control activates and the handler returns early (no double fire). Space behavior is unchanged: outside RUN with a button focused, the control activates on its own; in RUN `preventDefault()` plus `look()` when no reveal is active.

FR-3 (contract 1.1, transitions 4-5). Pad tap or LOOK tap on TITLE: `move()` and `look()` both no-op on TITLE (their `state !== 'RUN'` guards stay). The tap produces the exact string `Press Start to play. Use the pad once your run begins.` in `#msg`. It never starts a run, never changes state, never increments plays, never moves the player, never spends light. Pad tap or LOOK tap on LEVELCLEAR, WIN, or LOSE: silent no-op as today, no message required.

FR-4 (contract 1.1, transition 6, plus focus behavior). Reveal active: all input frozen as shipped; presses during a reveal change nothing, restart nothing, and do not retrigger or extend anything. Riven keeps both `onButton` early returns: Enter with `onButton` true returns before `preventDefault()`; Space with `onButton` true and `state !== 'RUN'` returns before `preventDefault()`. In RUN, Space with pad focus still triggers `look()` via the handler path as today (the one deliberate exception, unchanged). Ctrl/Meta/Alt modified presses are never intercepted (existing early return stays).

FR-5 (contract 1.2, message persistence). The TITLE message stays until replaced by a later `setMsg()` call (run start clears it via `enterRun()`; a successful RUN move clears it). It does NOT auto-expire on a timer (no `setTimeout` clears it; `REVEAL_MS` is unrelated). Repeat taps re-set the same string: idempotent, no counter, no stacking, no state change. Message appears within 1 frame of the tap (synchronous `setMsg` in the click path, 0 ms added latency). Single line at 375 px width, fits inside `#screen` max-width 420 px without wrapping past two lines at 0.9rem. Pad buttons keep their `aria-label`s; the message is announced once per tap via the `aria-live="polite"` `#msg`.

FR-6 (contract 1.3, constants). TITLE tap message string is the fixed copy above (not tunable). Message site is `#msg`. Move-key prevent set is exactly 12 keys in all 5 states. Focus exception, reveal freeze as specified. No new tunable constant. `CONFIG`, `REVEAL_MS`, `MOVE_LIMIT` untouched.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 1.5; AC-1 through AC-7 map them directly. AC-8 pins the structural scope requirement.

1. Given state TITLE at 1280x800, when the tester presses each of ArrowUp, ArrowDown, ArrowLeft, ArrowRight, w, a, s, d (and capitals), then the page does not scroll by any px and state stays TITLE and `#msg` stays empty. (design 1.5.1; FR-1)
2. Given state LEVELCLEAR, WIN, or LOSE, when the tester presses any arrow or WASD key, then the page does not scroll and state does not change. (design 1.5.2; FR-1)
3. Given state TITLE on a touch viewport, when the tester taps `#btnUp`, then `#msg` reads exactly `Press Start to play. Use the pad once your run begins.` and state stays TITLE and plays count is unchanged and player position is unchanged. (design 1.5.3; FR-3)
4. Given state TITLE, when the tester taps `#btnLook`, then the same string appears in `#msg` and state stays TITLE and light stays 15 and looks stay 0. (design 1.5.4; FR-3)
5. Given state TITLE, when the tester taps the pad five times in a row, then the message reads the same single string (no stacking, no counter) and state stays TITLE. (design 1.5.5; FR-5)
6. Given state TITLE with `#startBtn` focused, when the tester presses Enter, then exactly one run starts (plays +1, state RUN) with no double fire. (design 1.5.6; FR-2)
7. Given a RUN with an active reveal, when the tester presses arrows or taps the pad, then nothing changes (no move, no timer restart) and no scroll occurs. (design 1.5.7; FR-4)
8. Given `git diff main --stat` for this story, when the changed files are listed, then only `website/games/lightfare.html` changed; zero `website/sw.js` bytes (the cache rider belongs to Story 160), zero other files. (scope)

## Out of scope

No new mechanic, no new storage key, no other game file, no `GAME_ORDER` change, no `website/index.html` change (there is no new game card today), no backlog issues beyond #281/#285/#287, no FPS/app work. No touch to `CONFIG`, `move()`, `look()`, the level table, `enterRun()`, `advance()`, `retry()`, `backToTitle()`, the play-counter trio, or either storage key. No HUD readout change (that is Story 160). No fold-fit layout change (that is Story 160).

## Non-blocking rule

Story 159 is never cut. If Story 160 runs long, its HUD readout item (contract item 4) may be cut and the fold fit kept; this story ships whole regardless.

## Defects/risks

- Key repeat (held arrow on TITLE): every repeat preventDefaults, no scroll creep, no message, no state change. Verified by holding a key and reading `window.scrollY` delta 0 px.
- Enter auto-repeat landing in RUN: single-transition guard holds (RUN has no run-start binding, no double count, pattern-doc section 10 shape).
- Screen reader TITLE user: pad buttons keep `aria-label`s; `#msg` is `aria-live="polite"`, announced once per tap.
- Tap pad during RUN reveal: ignored silently (frozen reveal, shipped); TITLE message not shown because state is RUN.
- `setMsg` collision with `Not enough light.`: TITLE message only fires on TITLE where `look()` cannot set the refusal line; no collision path.
- Verification plan: 2 viewports x 5 states x 14 keys, plus tap matrix (tap each of 5 controls once on TITLE, read `#msg` textContent byte-equal, `__lightfare.state()` TITLE, `__lightfare.plays()` and `__lightfare.pos()` unchanged). Pass threshold: 100 percent of key presses show 0 px scroll; 5/5 TITLE taps show the exact string with no state change.
