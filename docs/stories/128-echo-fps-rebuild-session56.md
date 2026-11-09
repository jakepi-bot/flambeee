# Story 128: Echo Rounds first-person rebuild with pointer lock and gamepad (Session 56, P1, user-visible)

**Status:** Ready for development (Session 56, 2026-11-09).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible; carries the release).
**Assigned to:** **Riven** (sole code owner per Story 048; holds all three files together).
**Base commit:** `d1b085e`.
**Design contract:** `flambeee-team/design-handoff.md`, Story 128 sections 1-6 (Rook; contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 56 (2026-11-09), priorities item 1, acceptance bar, file ownership, public copy rule, degrade rule.
**Dependencies:** None this session. Story 129 (Kai, harness) proves this story; it does not block it.
**Tracked by:** Session 56 plan, Story 128. Follows the shipped top-down prototype at `website/games/echo-rounds.html` (v0.40.0, Story 110).

## Summary

Rebuild Echo Rounds in place as a real first-person shooter. Same light-ammo rule (one dark room, 4 echo cells, shots are the only light, a hit scores only on a target lit at fire time, every shot reveals the shooter, ammo budget 16 with `?ammo=` override, 60 s timer), new first-person vector-room renderer with exact pitch rotation, pointer lock mouse-look with yaw and pitch, yaw-relative WASD, a complete keyboard-only path, and standard-mapping gamepad input proven structurally only. Three files, no new file, no new precache entry.

## Files

| File | Change |
|---|---|
| `website/games/echo-rounds.html` | Full rewrite in place (321-line top-down retired). First-person renderer, pointer lock, keyboard path, gamepad polling, `window.__echo` read-only probe surface. Mechanic constants and win/lose rules preserved per the contract. |
| `website/index.html` | Line 718 only: Echo Rounds card description, one short line. Suggested: `Fire light in a dark room. Only lit targets count, and firing reveals you. Now in first person.` The word controller must not appear on the card. |
| `website/sw.js` | Line 21 only: `CACHE_VERSION` 23 to 24, one line. |

No other file. No new file, no new precache entry, `GAME_ORDER` untouched.

## Functional requirements

### 1. Rules preserved (contract sections 1, 6)

- FR-1. One dark room, 4 echo cells at contract positions, player starts at (120,300) yaw 0 pitch 0.
- FR-2. A shot scores only on a target lit at fire time (`litNow` true). Unlit candidates stand, cost ammo, and still reveal.
- FR-3. Every shot reveals the shooter (`visibleUntil = now + REVEAL_MS`, default 600 ms) regardless of hit or miss.
- FR-4. Ammo budget 16 default with `?ammo=` override retained; 60 s timer with `?time=` override retained.
- FR-5. WIN on all 4 cleared (overlay `ROOM CLEAR. Every echo answered.`). LOSE on spent ammo or expired timer with cells standing (overlay `OUT OF LIGHT` plus the reason line). Final-shot clear beats same-frame ammo/timer expiry.
- FR-6. Pulse lighting preserved: every shot boosts uncleared targets with fwd in (0, 700] and bearing within 0.35 rad for 500 ms, hit or miss. Cycle 1400 ms lit / 1400 ms dark preserved.

### 2. First-person renderer (contract sections 2, 3)

- FR-7. Filled floor plane (dark gray fill, not lines only) plus grid lines every 48 units, four filled walls darker than the floor, 2 px horizon line, depth-sorted echo-cell billboards, near-plane clipping at NEAR 1.0.
- FR-8. Exact pinhole projection with pitch as a rotation (contract section 2). No small-angle shear. Points with fwd at or behind NEAR produce no coordinate and are skipped, never drawn.
- FR-9. Internal resolution stays 960x600. Dark palette and brand colors unchanged. No ceiling; wall tops open to black void.

### 3. Pointer lock and mouse look (contract section 1)

- FR-10. Trusted canvas click requests pointer lock AND starts the round. `pointerlockchange` with element equal to canvas sets LOCKED; null or `pointerlockerror` sets UNLOCKED.
- FR-11. While locked, mousemove deltas drive look: yaw += movementX * 0.0025, pitch -= movementY * 0.0025. Pitch clamps to +-1.2 rad; yaw wraps to (-PI, PI].
- FR-12. Escape releases lock (browser reserved); the round keeps running and arrows take over. Clicking the canvas mid-round re-locks without restarting.
- FR-13. Lock denied (throw, rejected promise, or `pointerlockerror` in the acquire window) latches a session fallback flag: arrows always look, page never throws, status line reads `Pointer lock unavailable. Arrow keys look.`

### 4. Keyboard-only path

- FR-14. WASD moves relative to yaw (forward = (cos yaw, sin yaw)), 180 units/s, normalized when combined intents exceed length 1, clamped to the room inset by 12 px.
- FR-15. Arrow keys look at 1.8 rad/s yaw and 1.2 rad/s pitch while held. Space or Enter starts without lock. F fires along the crosshair (150 ms cooldown, edge-triggered, no repeat while held). R restarts from WIN or LOSE without reload.
- FR-16. A keyboard-only player with no mouse and no pad can start, fight, and win a full round.

### 5. Gamepad (structural proof only, no hardware claim)

- FR-17. Standard mapping polled every frame: left stick (axes 0/1) moves, right stick (axes 2/3) looks at 2.5 / 1.8 rad/s, RT / button 7 above 0.25 fires, A / button 0 restarts. Deflection under deadzone 0.15 reads 0.
- FR-18. `gamepadconnected` shows `Controller detected. Controller support is new and unverified on physical hardware.` `gamepaddisconnected` mid-round keeps the round running, clears pad intents, shows `Controller disconnected. Keyboard and mouse active.`
- FR-19. Non-standard mapping polls by index identically and appends `non-standard layout` to the status line.
- FR-20. Input mode label is last-input-wins (keyboard/mouse/pad) and never drops a summed intent.

### 6. Probe surface and robustness

- FR-21. Read-only `window.__echo` with every required field in contract section 7 (started, over, outcome, loseReason, ammoLeft, shots, litHits, unlitShots, unlitHits, reveals, player x/y/yaw/pitch, locked, lockDenied, inputMode, gamepadConnected, projectedNaNCount, frames, p95ms, slowFrames, floorCoverage, horizonPresent, moveSteps, lookEvents, target(i), targetCount). Getters or pure queries only; no setters, no control methods.
- FR-22. Tab blur / hidden clears key state, trigger latch, and pad intents; next dt clamps to 0.10 s; timer continues on wall clock. Escape as keydown is ignored. Cooldown drops extra shots without ammo loss.

## BDD scenarios (observable in the product)

**Scenario 1: Start on click.** Given the IDLE overlay `Click to enter the dark room`, when the player clicks the canvas, then the round starts, the timer runs, and the first-person room renders.

**Scenario 2: Lock acquire.** Given the round starting from a trusted click, when lock engages, then the probe reports locked true and the status shows the locked state.

**Scenario 3: Lock release and re-lock.** Given lock acquired, when the player presses Escape, then lock releases and the round continues on arrows; when the player clicks the canvas, then lock returns without restarting and without resetting ammo or timer.

**Scenario 4: Lock-denied fallback.** Given pointer lock denied or unsupported, when the player plays, then arrows look, WASD moves, F fires, the fallback status line shows, and no error is thrown.

**Scenario 5: Mouse look.** Given the round running with lock, when the player moves the mouse right, then the view turns right; when the player moves it up, then the view tilts up.

**Scenario 6: Pitch clamp and yaw wrap.** Given the view at full-up pitch, when the player keeps pushing up, then the view stops at the clamp and never flips; when yaw turns past PI, then it wraps and control never inverts or sticks through a full pitch sweep.

**Scenario 7: Yaw-relative movement.** Given yaw 0 then yaw 90 deg, when the player holds W for the same duration in each, then the player travels along different room axes matching the facing direction.

**Scenario 8: Lit-hit gate.** Given a lit echo cell under the crosshair, when the player fires, then the cell clears with a light pulse and the reveal ring shows; given an unlit cell, when the player fires at it, then it stands, ammo drops by 1, and the reveal still shows.

**Scenario 9: Keyboard-only win.** Given no mouse and no pad, when the player starts with Space, moves with WASD, looks with arrows, and fires with F, then a full round can be started, fought, and won.

**Scenario 10: Gamepad move, look, fire, restart.** Given a connected controller, when the player pushes the left stick, then the player moves; when the player pushes the right stick, then the view turns; when the player pulls RT, then a shot fires; when the player presses A on the end screen, then the round restarts.

**Scenario 11: Disconnect mid-round.** Given a pad connected and the round running, when the pad disconnects mid-round, then play continues on keyboard with no stuck movement and the disconnect line shows.

**Scenario 12: Win.** Given 3 cells cleared, when the final cell falls to a lit shot, then `ROOM CLEAR. Every echo answered.` shows and the timer and ammo stop.

**Scenario 13: Lose on ammo and on timer.** Given uncleared cells with 1 shot left, when the player fires without clearing, then `OUT OF LIGHT` shows with the ammo reason; given a fresh round with the timer forced short, when it expires with cells standing, then `OUT OF LIGHT` shows with the timer reason.

**Scenario 14: Restart.** Given WIN or LOSE showing, when the player presses R, Space, Enter, clicks the canvas, or presses pad A, then a new round starts immediately with full ammo, reset timer, and uncleared targets, with no reload.

**Scenario 15: Mobile no-overflow.** Given a 375x667 viewport, when the page loads and a round starts, then there is no horizontal overflow, lock denial degrades instead of throwing, and no touch UI is added.

**Scenario 16: Yaw-only degrade.** Given the pitch-cut degrade build, when the player plays, then the view is still first-person with yaw look, Up and Down do nothing harmful, the round remains winnable, and the top-down view never appears.

## Acceptance criteria

- AC-1. Full rewrite in place at `website/games/echo-rounds.html`; no new file, no new precache entry.
- AC-2. Same light-ammo mechanic and win/lose rules (Scenarios 1, 8, 12, 13).
- AC-3. Filled floor plus grid, four filled walls, horizon line, depth-sorted billboards, near-plane clipping, exact pitch rotation (Scenario 1; bar checks 1-3).
- AC-4. Pointer lock acquire, release, re-lock, denied fallback (Scenarios 2, 3, 4; bar checks 6, 7).
- AC-5. Mouse look with clamped pitch and wrapped yaw (Scenarios 5, 6; bar check 3).
- AC-6. Yaw-relative WASD movement (Scenario 7; bar check 4).
- AC-7. Lit-hit gate preserved, Story 089 behavior (Scenario 8; bar check 5).
- AC-8. Keyboard-only full win path (Scenario 9; bar check 8).
- AC-9. Gamepad move, look, fire, restart plus mid-round disconnect (Scenarios 10, 11; bar check 9).
- AC-10. Win, both lose reasons, restart without reload (Scenarios 12, 13, 14).
- AC-11. Mobile 375x667 no horizontal overflow, no throw (Scenario 15; bar check 10).
- AC-12. Yaw-only degrade stays first-person and winnable (Scenario 16).
- AC-13. Card line 718 is one short line with no controller wording; `CACHE_VERSION` reads 24 on the merged tree.
- AC-14. Read-only `window.__echo` surface complete per contract section 7; harness fails loudly on any missing field.
- AC-15. Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required proof (RED/GREEN)

Riven records RED on base `d1b085e` (top-down file, no lock, no pad, no probe surface; the harness names the failing checks) and GREEN on the branch (all ten bar checks plus contract D1-D11 pass, exit 0). Proof bundle: serve command, viewport readings, 300-frame NaN/Infinity assertion, floor-coverage fraction, horizon presence, pitch-sweep upright readout, yaw-relative axis readings, lit/unlit shot counts, lock acquire/release/re-lock log, denied-fallback zero-error run, keyboard-only winning round log, synthetic pad move/look/fire/disconnect log, p95 frame time, mobile overflow reading, card line verbatim, `CACHE_VERSION` before and after.

## Out of scope

Touch controls, `GAME_ORDER`, GOTW promotion, new game cards, native builds, Apps, Cinder edits, `src/` archival, release artifacts, `pending-post.txt`, BLOG.md, website What is New. The 02:55 job owns release artifacts.

## Public copy rule (binding)

No `full controller support` anywhere public: not the card, not the game page, not the release title, not the release notes, not the Bluesky post. The card carries no controller wording at all. The in-game controls line says a controller is detected when one is present and states that controller support is new and unverified on physical hardware. Pointer lock, mouse look, and keyboard-only play are proven and may be claimed.

## Risks and degrade path

Risk 1: exact pitch rotation or floor-coverage math misses the bar in the window. Path: cut pitch and ship yaw-only first-person (PITCH_MAX forced 0, horizon fixed, bearing-only hit test, Up/Down and stick-y inert). Never ship top-down and call it the FPS.
Risk 2: pointer lock behaves differently in headed versus headless browsers. Path: the DENIED fallback is the same code path in both; arrows always work.
Risk 3: no physical pad on the box. Path: structural synthetic proof only, labeled NOT HARDWARE every run; the hardware gate stays OPEN-BLOCKED-ON-HARDWARE until the 003 protocol runs on a real device.
If yaw-only first-person is not green either, the game is held and no release cuts on it.

## References

- `flambeee-team/session-plan.md`, Session 56 (2026-11-09): priorities item 1, ten-check acceptance bar, file ownership table, public copy rule, degrade rule, jakebot advisory session `local-5f3e24ee1bd1ebb6139eea8b3b6a4a904fd70c5987ede1e02278bde839ff886b` (Option A).
- `flambeee-team/design-handoff.md`, Session 56 (Rook): Story 128 sections 1-6, tuning table, edge cases, D1-D11 design acceptance, balance rationale, open questions.
