# Story 130: Pointer-lock acquisition view-snap guard (Session 57, story filed today, no code today)

**Status:** Story written 2026-11-10. NO CODE TODAY.
**Author:** Quinn, Business Analyst (requirements). Mechanic contract: Rook, `flambeee-team/design-handoff.md`, Session 57, Story 130 sections 0-8. The contract wins on mechanic and input detail.
**Priority:** P1b.
**Owner:** Riven, next non-release dev window. Riven is sole code owner when built.
**Base:** `b918475` (main). Carrier heads, verify only, never edit: PR #230 `204bb7d` (Story 128), PR #229 `be55a43` (Story 129).
**Scope rule:** story written today, no code today. The only code edit, when built, is `website/games/echo-rounds.html`. `dev/echo-fps-proof.py` is not edited by this story: its 11 checks must go green against the guarded file with the harness byte-identical to `be55a43`. If a check fails, the guard is wrong, not the harness.
**Public copy rule:** public copy must not name F2. No camera-smoothness claim, no known-issue note about the snap. F2 is an unconfirmed headed behavior (no X server on this box), not a publishable fact.

## 0. Player problem, and the observable before and after

Click-to-start is one trusted canvas `mousedown`: start the round, then request pointer lock. The intended start view is `PLAYER_START` yaw 0 / pitch 0: level, facing +x, crosshair on the room.

In any browser that dispatches the pointer-lock acquisition warp, the first `mousemove` after lock carries `movementX`/`movementY` equal to minus the click-point offset, and the handler applies raw deltas whenever a round is running. Measured by QA in headless Chromium 156: trusted click at canvas point (640,433) produces `movementX -640, movementY -433` with `lockedAtDispatch=True`, and the game applies it: `lookEvents 1`, yaw **-1.600000 rad (-91.67 deg)**, pitch **+1.082500 rad (+62.02 deg)**, which is 1.0825 / 1.2 = **90.2 percent of the pitch clamp**. The player's first frame in the dark room is aimed 91.7 degrees off axis and 62 degrees above level, and where it points depends on where the cursor happened to sit.

| Observable | Today, browser with the warp (measured headless 156) | After the fix |
|---|---|---|
| start yaw | -1.600000 rad (-91.67 deg) | 0.000000 rad |
| start pitch | +1.082500 rad (+62.02 deg, 90.2% of clamp) | 0.000000 rad |
| look events credited to the acquisition | 1 | 0 |
| `guardDrops` | n/a | 1 (when a >200 px first event arrives) |
| start view depends on pre-lock cursor position | yes: start = f(click point) | no, within the guard's operating range |
| combined look applied by the acquisition event | 2.6825 rad (1073 px) | 0, or at most 0.5000 rad if the warp sits at or below the threshold (E9) |

## 1. Threshold guard rule (normative)

Drop exactly one `mousemove` after lock acquisition, and only when it is big:

```
DROP  <=>  guardArmed AND started AND NOT over AND (abs(mx_px) + abs(my_px) > GUARD_PX)
```

with `GUARD_PX` default 200 px. Never drop a small move (at or below 200 px L1 applies normally). Never drop more than one event per acquisition (the guard disarms on the first evaluated mousemove either way). Placement is part of the contract: the predicate sits after both existing early returns (`if (!started || over) return;` and `if (!mx && !my) return;`) and before `inputMode = 'mouse'`, `lookEvents++`, and the yaw/pitch updates. On drop: `guardArmed = false`, `guardDrops += 1`, return, no look state touched. On pass-through while armed: `guardArmed = false`, then the normal math runs.

Guard states: `DISARMED` (inert) and `ARMED` (waiting for one evaluated mousemove). Two pieces of state: a boolean and a counter. Arm on `pointerlockchange` with `document.pointerLockElement === canvas` (first acquisition and every re-lock; arm only on the canvas, never on a foreign element). Disarm on unlock to null (Escape), on `pointerlockerror`, when lock is denied (no lock event can have armed it), on `startRound()`, and on round end. Zero-delta `(0,0)` events never consume the guard, so the Firefox/Safari 0-delta class sees a no-op guard. A `mousemove` while `!started` or `over` returns through the existing gate first and leaves the guard untouched.

Invariant, assertable on every probe read: `guardArmed` implies `locked && started && !over`. Also: `guardDrops` never increases by more than 1 per lock acquisition, and never while `guardArmed` was false.

Path notes: re-lock mid-round arms again with one drop for that acquisition, and the `if (locked) fire()` branch of `mousedown` still fires without re-arming. Lock-denied fallback (arrows look), pad-only play, and keyboard-only play never arm, so `guardDrops` stays 0 and mouse look still works at 0.0025 rad/px. Round ends while locked still disarm, so no stale arm crosses into the restart.

## 2. Formulas with units

Look math, unchanged from Story 128 (rad): `Δyaw = mx_px * MOUSE_SENS_rad_per_px`, `Δpitch = -my_px * MOUSE_SENS_rad_per_px`, then `clampLook()`: pitch clamped to [-1.2, +1.2] rad, yaw wrapped to (-PI, PI].

Units: `mx_px` and `my_px` are the event's own `movementX`/`movementY` values as delivered (CSS pixels). No `devicePixelRatio` factor, no canvas CSS-scale factor. The threshold is in event units and is device- and size-independent.

Threshold priced in radians (`GUARD_PX * MOUSE_SENS`, at MOUSE_SENS 0.0025 rad/px):

| GUARD_PX | L1 px | combined rad | degrees |
|---|---|---|---|
| 80 (min) | 80 | 0.2000 | 11.46 |
| 200 (default) | 200 | 0.5000 | 28.65 |
| 600 (max) | 600 | 1.5000 | 85.94 |

Defect event: `abs(-640) + abs(-433) = 1073 px > 200`, so it is dropped. The 2.6825 rad of combined look (1.6000 yaw + 1.0825 pitch) that the handler would apply in a single event never reaches the camera.

Residual bound when a warp sits at or below the threshold: `abs(mx)+abs(my) <= 200 px` is applied by design, so `abs(Δyaw) + abs(Δpitch) <= 200 * 0.0025 = 0.5000 rad` combined, each axis individually also `<= 0.5000 rad`, against today's 1.6000 / 1.0825. Worst-case acquisition error falls from 2.6825 rad to 0.5000 rad combined, a 5.4x bound, with zero change to sensitivity or to any steady-state number.

Why a threshold and not an unconditional first-event drop (jakebot ruling, 2026-11-10): a threshold wrongly drops 0 events when the browser sends no warp for first events at or below 200 px, while an unconditional drop always swallows the player's entire first look move after every lock. Kai's check-06 (injects `movementX 100`, asserts `dyaw 0.2500` within 1 percent) stays green under the threshold (100 <= 200 applies) but goes red in warp-free environments under an unconditional drop, which would force an edit to Story 129's frozen harness. Accepted risk, stated plainly: the guard drops a genuine first event whenever that event exceeds 200 px L1 after lock acquisition; the worst plausible mistake costs one event priced at about 0.5000 rad at the threshold edge, recoverable on the very next event.

## 3. Tuning constants table (Story 130)

Every constant for this story lives in `website/games/echo-rounds.html`, in the tuning constants block beside `MOUSE_SENS` (line 70 at `204bb7d`). One declaration, one file, read by the `mousemove` handler.

| Name | Default | Min | Max | Location |
|---|---|---|---|---|
| GUARD_PX | 200 px (L1, `abs(mx)+abs(my)`) | 80 px | 600 px | `website/games/echo-rounds.html`, tuning constants block beside `MOUSE_SENS` (line 70) |

Derived, not tunable: `GUARD_RAD = GUARD_PX * MOUSE_SENS` (0.5000 rad at default). Explicitly unchanged: `MOUSE_SENS` 0.0025 rad/px and `PITCH_MAX` 1.2 rad stay exactly as Story 128 shipped them. No `GUARD_ENABLED` flag: a disabled guard is an untested path.

Probe additions (same file, read-only getters on `window.__echo`): `guardArmed` (bool, true only between a lock acquisition and the first evaluated mousemove) and `guardDrops` (int, cumulative dropped events since page load). Both are additive; the harness `REQUIRED_PROBE` name list checks presence, so adding keys cannot break 11/11.

## 4. Edge cases E1-E6

| # | Case | Disposition |
|---|---|---|
| E1 | Guard never fires (no warp delivered, or a corner-click warp at or below threshold): snap persists | residual is bounded by the 0.5000 rad formula. If a headed run still shows a jump with `guardDrops` 0 and a magnitude outside the residual bound, the guard is not the cause: reopen the story with the trace, do not chase it by raising `GUARD_PX` (600 px = 1.5000 rad of false-positive room is the wrong direction) |
| E2 | Guard eats a legitimate first flick | accepted, bounded: one event, threshold-priced, next event restores control. Field signal: a report that the first mouse move after clicking does nothing. Levers in order: `GUARD_PX` 200 -> 300 -> 400 -> 600 (each step also raises the E9 residual), then a 250-500 ms arm window as a new story |
| E3 | Guard leaks across rounds or lock/unlock cycles | disarmed on unlock, lock error, lock denied, round start, and round end. Observable: the invariant `guardArmed => locked && started && !over` on every probe read, and `guardDrops <= number of acquisitions since page load` |
| E4 | Firefox or Safari deliver a 0 delta warp | `(0,0)` never consumes the guard, so no stutter, no lost look input, `guardArmed` stays true until a real move, and a <=200 px real move applies. The guard is a no-op in this browser class. Pass: `guardDrops` 0, `lookEvents` increments once per real move |
| E5 | High-DPI pointer | predicate uses the event's own units, no `devicePixelRatio` factor. Pass: identical drop verdict at `deviceScaleFactor` 1 and 2 for the same injected magnitudes. If the handler scales by DPR, a DPR-2 machine gets an effective 400 px threshold and D130-3 fails; do not scale |
| E6 | Escape release then re-lock (headed only: headless Chromium 156 does not release on Escape) | disarm on release, arm on re-lock, exactly one drop for the new acquisition, round never restarts, ammo unchanged |

Further cases E7 (resize and CSS scaling), E8 (mobile with no lock API), E9 (sub-threshold warp, residual at most 0.5000 rad), E10 (synthetic harness events), E11 (guard placement after the zero-delta gate, normative), E12 (rapid lock/unlock cycling), and E13 (lock on a non-canvas element) live in the contract and bind the build window. Rejected plans: recenter-on-lock (Plan C, hides the artifact instead of removing it) and time-windowed arm (Plan D, tight window misses late moves, loose window is a second tunable with no evidence).

## 5. Design acceptance criteria (player and operator observable BDD, D130-1 through D130-12)

These read `window.__echo` plus real or explicitly labeled synthetic input; none of them is verified by reading source.

- **D130-1.** Given a fresh load and a trusted click on the canvas at (640,433) that starts the round, when lock acquires, then within 500 ms `abs(Δyaw) < 0.05` rad and `abs(Δpitch) < 0.05` rad against the pre-click reading, `guardDrops` increases by at most 1, and `lookEvents` is 0 for the acquisition. QA records which branch occurred: 1 means the drop did the work, 0 means this browser delivered no warp.
- **D130-2.** Given lock acquired and the guard armed, when a synthetic `mousemove` of `movementX 100, movementY 0` is dispatched, then yaw advances 0.2500 rad within 1 percent, `guardDrops` is unchanged, and `guardArmed` becomes false.
- **D130-3.** Given armed, when synthetic events `(200,0)` and `(150,50)` are dispatched (both L1 = 200 px), then both apply: `abs(Δyaw)+abs(Δpitch)` = 0.5000 rad for the first, no drops, `guardArmed` false after the first.
- **D130-4.** Given armed, when a synthetic `(201,0)` is dispatched, then yaw and pitch are unchanged, `lookEvents` is unchanged, `guardDrops` increases by exactly 1, and `guardArmed` is false.
- **D130-5.** Given the guard disarmed after D130-4, when a synthetic `(1000,0)` is dispatched, then it applies (yaw +2.5000 rad, wrapped) and `guardDrops` is unchanged: never more than one event dropped per acquisition.
- **D130-6.** Given a running round with lock released by `document.exitPointerLock()`, when the player clicks the canvas to re-lock, then the round does not restart, `shots` and `ammoLeft` are unchanged, `guardArmed` becomes true for the new acquisition, and at most one event is dropped for it.
- **D130-7.** Given a Space start (keyboard only) or a synthetic-pad round, when either round runs to a loss, then `guardArmed` is false on every probe read and `guardDrops` is 0 at the end.
- **D130-8.** Given `requestPointerLock` rejects (harness override), when the round runs, then `lockDenied` is true, `guardArmed` false, `guardDrops` 0, arrows look, zero page errors.
- **D130-9.** Given the guard armed at lock and the round ending before any mousemove, when the probe is read on the end screen and again after restart, then `guardArmed` is false in both reads and no event between rounds incremented `guardDrops`.
- **D130-10.** Given lock acquired and `(0,0)` mousemoves delivered first (the Firefox/Safari class), when two `(0,0)` events arrive, then yaw and pitch are unchanged, `lookEvents` is unchanged, `guardArmed` is still true, and the next <=200 px real move applies.
- **D130-11.** Given any probe read during play, when `guardArmed` is true, then `locked` is true, `started` is true, and `over` is false. Zero violations across every run in section 6.
- **D130-12.** Given a human in a headed browser following section 6, when 5 click-to-start runs complete, then all 5 pass the 0.05 rad bar on both axes with zero page errors, and the outcome does not depend on where the pre-lock cursor sat.

## 6. Headed confirmation protocol R7 (run before the build to confirm F2 and after the build to accept the fix)

5 click-to-start runs in a headed browser on a machine with a display (this box has no X server). Click points, all with L1 offset above `GUARD_PX`: (640,433), (300,150), (100,150), (800,400), (200,60). For each run record yaw and pitch immediately before the click and again 500 ms after lock. Pass: `abs(Δyaw) < 0.05` rad and `abs(Δpitch) < 0.05` rad on both axes for all 5 runs, zero page or console errors, the game remains playable immediately after (look, move, fire all respond), and repeating with the pre-lock cursor parked in two different places (top-left of the viewport, bottom-right) gives the same verdict, because the pre-lock mouse position must not matter. Interpretation: pre-fix 0/5 pass means F2 reproduces headed and per jakebot's rule becomes P1 for the next non-release dev window with this guard; pre-fix 5/5 pass means F2 is headless-only in the tested browser and the result is recorded without publishing it (public copy rule); post-fix 5/5 pass closes the story, and any post-fix red run blocks the merge of Story 130 only, never the release. Firefox is worth one pass if available: it is the 0-delta class and should pass with `guardDrops` 0.

Full verification plan R1 (lock-cycle matrix, 15 acquisitions), R2 (threshold boundary legs, 4/4), R3 (invariant sweep, 0 violations), R4 (existing harness 11/11 with the harness byte-identical to `be55a43`), R5 (QA suite 39/40 with the only red line the stale `scout-23c` expectation), and R6 (inertness over 8 keyboard and pad rounds) lives in the contract and binds the build window.
