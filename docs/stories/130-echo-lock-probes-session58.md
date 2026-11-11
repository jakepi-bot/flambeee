# Story 130: Echo Rounds lock-acquisition probes, no guard (Session 58, P0, user-invisible)

**Status:** Ready for development (Session 58, 2026-11-11).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P0 (ships tonight; the one instrument the release needs).
**Assigned to:** **Riven**, sole owner. No other dev touches either file.
**Base commit:** `f029493`.
**Design contract:** `flambeee-team/design-handoff.md`, Session 58, Section A (Rook; the contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 58 (2026-11-11), priorities item 1.
**Tracked by:** Session 58 plan, Story 130. QA finding F2.
**Supersedes:** `docs/stories/130-f2-lock-snap-guard-session57.md` (Session 57 version, which specced a guard; retained for history, not buildable).

## HELD by ruling (read first)

Per jakebot ruling 2026-11-11 (recorded in `session-plan.md`, decision record): the `GUARD_PX` threshold guard does **not** ship tonight. The 91.7 degree yaw snap was measured in headless Chromium only and has never been reproduced headed, and this box has no X server. **This story ships read-only probes only.** The figure 200 px survives solely as a post-hoc analysis threshold applied to recorded probe data, never as code. A headed reproduction on 2 of 3 runs makes the guard P1; a headed non-reproduction closes F2 as environment-specific. See also `docs/design-decisions/004-session58-lock-probe-schema.md`.

## Summary

Echo Rounds became a first-person shooter yesterday, and one test run showed the view swinging hard the instant the mouse locks to the screen. Nobody has seen that swing happen in a real browser yet, so fixing it now would mean changing how the flagship game feels on a guess. This story adds four small readouts that record exactly what the first mouse movement after each lock looks like: how many locks happened, the size of that first movement, and whether it has arrived yet. They change nothing about how the game plays. A person with a real display then runs three short checks, and the numbers decide whether a fix is ever needed.

## Files

| File | Change | Owner |
|---|---|---|
| `website/games/echo-rounds.html` | Four additive read-only getters on `window.__echo` (`lockAcqs`, `firstMx`, `firstMy`, `lockPending`) plus probe state transitions in the `pointerlockchange` listener (line 618) and the `mousemove` listener (line 582). Zero behavior change. | Riven |
| `website/sw.js` | Line 21 only: `CACHE_VERSION` 24 to 25, same PR (shell-asset rule: `echo-rounds.html` is precached). | Riven |

No other file. `dev/echo-fps-proof.py` is **not** edited: it must run 11/11 at the built head byte-identical to `be55a43`. If a check fails, the probe edit is wrong, not the harness.

## Functional requirements

### 1. Probe field spec (A3)

- FR-1. `lockAcqs`: int, >= 0, count of canvas pointer-lock acquisitions since page load. Starts 0, increments by exactly 1 per acquisition (T2), never otherwise.
- FR-2. `firstMx` / `firstMy`: int or null, CSS px (`movementX`/`movementY` as delivered). Value of the first evaluated mousemove after the latest acquisition. Null until T5, reset to null on every T2.
- FR-3. `lockPending`: bool, true only between an acquisition and its first evaluated mousemove. Set true on T2, false on T3/T4/T5.
- FR-4. All four are additive read-only getters on `window.__echo`. No setter, no control method, nothing else added.
- FR-5. Distinguishing rule: `lockPending == true` with a null pair means armed-but-unmoved; `lockPending == false` with a non-null pair means moved.
- FR-6. Baseline key count at `f029493` is 29 (27 getters plus `target` and `targetCount`); after this story it is 33.

### 2. State transitions (A1)

- FR-7. T1 boot: fields at zero/null/false.
- FR-8. T2 acquisition (`pointerlockchange` with `document.pointerLockElement === canvas`): `lockAcqs += 1`, `lockPending = true`, pair reset to null. First acquisition and every re-lock; never on a foreign element.
- FR-9. T3 unlock (change to null): `lockPending = false`; pair and counter kept readable after the fact.
- FR-10. T4 stale-clear (`pointerlockerror`, lock denied path, round start, round end): `lockPending = false`; pair and counter kept.
- FR-11. T5 first evaluated mousemove while pending: pair recorded, `lockPending = false`. Evaluated means it passed both existing gates (`started && !over`, `(mx,my) != (0,0)`). Later moves never overwrite the pair until the next T2.
- FR-12. T6 zero-delta or out-of-round events: no probe field touched. `(0,0)` bursts and events while `!started` or `over` are not first moves.

### 3. Read-only invariant (A4)

- FR-13. No probe field is read by any input, rendering, timing, or tuning path. The `mousemove` handler records the pair and clears the flag, then runs its existing math unchanged; no branch consults a probe value.
- FR-14. `lockPending == true` implies `locked && started && !over` on every read.
- FR-15. v0.48.0 shipped bytes stay behaviorally identical: same input handling, same look math (`MOUSE_SENS` 0.0025 rad/px, `PITCH_MAX` 1.2 rad), same states. Any change in `lookEvents`, yaw, or pitch for an identical input sequence against the base build fails this story.

### 4. Tuning constants (A5)

| Name | Value | Location |
|---|---|---|
| `MOUSE_SENS` | 0.0025 rad/px, fixed | `website/games/echo-rounds.html`, tuning block line 70 |
| `PITCH_MAX` | 1.2 rad, fixed | `website/games/echo-rounds.html`, line 74 |
| `CACHE_VERSION` | 24 to 25 | `website/sw.js` line 21, same PR |

- FR-16. No new tunable constant. The probe fields are not tunable. Conversion for observers: `firstYaw_rad = firstMx_px * 0.0025`; combined `L1_px = abs(firstMx) + abs(firstMy)`; 200 px prices at 0.5000 rad combined, 28.65 deg.
- FR-17. No `GUARD_PX`-like constant appears anywhere in the file. The analysis threshold lives in the handoff, not in code.

### 5. Edge cases (A6)

- FR-18. `(0,0)` bursts after lock never recorded; flag stays true until a real move.
- FR-19. 15 rapid lock/unlock cycles: `lockAcqs == 15`, each T2 nulls the pair, no throw.
- FR-20. Round ends while pending: flag cleared, pair stays null, no between-rounds event writes the pair.
- FR-21. Keyboard-only or pad-only round: T2 never fires, `lockAcqs == 0`, pair null, flag false on every read.
- FR-22. Lock denied (missing API, throw, rejected promise, 1000 ms `acqTimer` expiry): never armed, counter 0, `lockDenied` true as today.
- FR-23. Foreign-element lock: no count, no flag.
- FR-24. High-DPI pointer: event units recorded verbatim, no `devicePixelRatio` factor.
- FR-25. Canvas resize / CSS scaling: same verdict at 1280x800, 1024x768, 375x667.

## BDD acceptance criteria (observable in the product or a named measurement, never by reading source)

- AC-1. Given a fresh load, when the probe is read before any lock, then `lockAcqs` is 0, `firstMx` and `firstMy` are null, `lockPending` is false, and all 29 pre-existing keys answer as at base. (D130-P1)
- AC-2. Given a running round with lock acquired, when one synthetic `mousemove` (100, 0) is dispatched, then yaw advances 0.2500 rad within 1 percent, `firstMx` reads 100, `firstMy` reads 0, `lockPending` is false, and `lookEvents` increments by exactly 1. (D130-P2)
- AC-3. Given a fresh acquisition, when the probe is read before any mousemove, then `lockPending` is true and the pair is null. (D130-P3)
- AC-4. Given the PENDING state, when two `(0,0)` events arrive, then yaw, pitch, and `lookEvents` are unchanged, `lockPending` is still true, and the pair is still null. (D130-P4)
- AC-5. Given the PENDING state, when a synthetic (-640, -433) is dispatched, then the game applies it exactly as v0.48.0 does (yaw -1.6000 rad, pitch under the existing 1.2 rad clamp), the pair reads (-640, -433), and nothing is dropped or suppressed. (D130-P5)
- AC-6. Given a second acquisition in the same page, when it fires, then `lockAcqs` is 2, the pair is null again, and the previous pair is gone. (D130-P6)
- AC-7. Given a Space-started keyboard-only round run to a loss, when the probe is read throughout, then `lockPending` is false on every read, `lockAcqs` is 0, and the pair stays null. (D130-P7)
- AC-8. Given any probe read during play, when `lockPending` is true, then `locked` is true, `started` is true, and `over` is false. Zero violations across every run. (D130-P8)

## Required proof

- R1, headless synthetic matrix: 5 lock cycles at 3 viewport sizes (1280x800, 1024x768, 375x667), 15 acquisitions. Pass: `lockAcqs` equals the cycle count, at most one pair write per acquisition, flag false after every unlock, pair values exactly equal injected magnitudes, zero page errors.
- R2, existing harness: `python3 dev/echo-fps-proof.py --target website/games/echo-rounds.html` at the built head, harness byte-identical to `be55a43`. Pass: 11/11, exit 0, same 11 check names. RED anchor: on base `f029493` the four new fields are absent.
- R3, headed confirmation a human runs in under 5 minutes on a machine with a display: fresh load, read yaw/pitch and `lockAcqs` (call it N), click the canvas to start and lock, wait 500 ms without touching the mouse, read `lockAcqs`, `lockPending`, pair, yaw, pitch. 3 runs. Instrument PASS per run: `lockAcqs == N+1`, `lockPending == false`, pair non-null, `yaw_after - yaw_before` equals `firstMx * 0.0025` within 1 percent. Warp verdict per run (analysis only): `abs(firstMx)+abs(firstMy) > 200` with matching yaw jump means the warp reproduced; 2 or more of 3 means F2 reproduces headed and the guard becomes P1; 0 of 3 means F2 is headless-only in the tested browser, recorded without publishing.

## Out of scope

The `GUARD_PX` guard, any drop predicate, any `guardArmed`/`guardDrops` field, any change to `MOUSE_SENS`, `PITCH_MAX`, look math, states, ammo, timer, or cones; any edit to `dev/echo-fps-proof.py`; any second website file; `GAME_ORDER`; card copy; touch controls; release artifacts; public copy naming F2 or claiming camera smoothness.

## Definition of done

R1 passes 15/15 acquisitions with zero page errors; R2 passes 11/11 with the harness byte-identical to `be55a43`; R3 instrument check passes on a headed box (or is handed to the release wave with the exact protocol above if no display is reachable tonight); `CACHE_VERSION` reads 25 with the game change in the same PR; diff limited to the two files in the table; all eight AC scenarios recorded pass or fail in the PR body.
