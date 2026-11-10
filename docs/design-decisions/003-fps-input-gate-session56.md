# 003 - Echo Rounds FPS input gate: physical gamepad verification protocol, Session 56 (2026-11-09)

Date: 2026-11-09. Session: 56 (NEW-GAME day). Status: OPEN-BLOCKED-ON-HARDWARE.
Story: 129 (Kai). Design contract: flambeee-team/design-handoff.md, Story 129 sections 1-7.

## Context

Session 56 ships Echo Rounds as a first-person shooter with pointer lock, keyboard, and gamepad input. The harness at `dev/echo-fps-proof.py` proves the first-person renderer, the pointer lock cycle, the lit-hit gate, keyboard-only play, and the gamepad code path end to end in headless chromium 156. The gamepad legs inject a synthetic `navigator.getGamepads` before page scripts. That proves polling, mapping, deadzone, fire, and disconnect handling in code. It proves nothing about a physical controller.

## The gate, stated plainly

**TODAY'S SYNTHETIC RUN IS NOT HARDWARE.** Every harness run prints `NOT HARDWARE` on its own line. The synthetic pad leg is a code-structure proof: axes, buttons, connect, disconnect, and the status line are exercised against a fake pad object. Zero physical pads are attached to the build box, and zero non-empty `getGamepads` samples have ever come from real hardware.

**Gate status: OPEN-BLOCKED-ON-HARDWARE.** The gate closes only when a human with a physical gamepad completes every step below in one session and the record block is filled in with PASS on all five steps. Until then, no public copy may state or imply that a controller is verified, tested, or supported on hardware. The allowed wording stays: controller support is new and unverified on physical hardware, plus the detected-controller line when a pad is present.

## Session record (fill in during the protocol run)

| Field | Value |
|---|---|
| Device string (exact `id` from `navigator.getGamepads()[0].id`) | |
| Mapping string (`standard` or other) | |
| Browser and version (chrome://version, full version string) | |
| OS and kernel | |
| Harness command and exit code | |
| Date and time (local) | |
| Operator | |
| Result: PASS or FAIL (all five steps) | |

Copy the device string exactly. A truncated or paraphrased id is not a record.

## Setup

1. Open `website/games/echo-rounds.html` in the browser named above, served from the repo (for example `python3 -m http.server` at the repo root, then `http://127.0.0.1:PORT/website/games/echo-rounds.html`).
2. Plug in the physical pad before the page loads so the connect event fires on load. If the pad is already plugged in, reload the page after plugging.
3. Run `env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/echo-fps-proof.py --target website/games/echo-rounds.html --label HARDWARE` and record the command and exit code in the record block. The harness still prints NOT HARDWARE; this protocol, not the harness, closes the gate.
4. Open the in-game status line area so the detected and disconnected messages are visible during the steps.

## Step 1: Device enumeration

Procedure: with the pad connected, read the status line and check `navigator.getGamepads()` in the console.

Pass thresholds, all required:
- At least one non-null pad returned by `navigator.getGamepads()` within 3 seconds of plugging in or of page load.
- Device string is non-empty and is recorded verbatim in the record block above.
- Status line shows `Controller detected. Controller support is new and unverified on physical hardware.`
- If `mapping` is not `standard`, the status line also appends `non-standard layout`, and steps 2 through 5 still pass with the same indices (axes 0/1 move, axes 2/3 look, button 7 fire, button 0 restart).

Fail if: no pad appears within 3 seconds, the device string is empty, or no detected-controller line appears.

## Step 2: Simultaneous move, look, and fire

Procedure: start a round (pad A, Space, or canvas click). In one continuous 2 second action, hold the left stick full forward, hold the right stick full right, and hold the right trigger.

Pass thresholds, all required:
- Player displacement of at least 100 world units during the 2 seconds, in the direction the camera faces (yaw-relative, not screen-relative).
- Yaw increases by at least 1.0 radian during the 2 seconds (right stick right turns right), with no roll and pitch clamped inside plus or minus 1.2 rad.
- Ammunition drops by at least 1 and a shot pulse appears (trigger fired while held).
- At least one lit target hit inside the 0.06 rad hit cone still clears while all three inputs are active.

Fail if: any axis is dead, any axis is inverted, movement is screen-relative instead of yaw-relative, the trigger does not fire, or a lit hit under the crosshair does not clear.

## Step 3: Deadzone

Procedure: in a running round, rest the pad, then make two small stick deflections.

Pass thresholds, all required:
- At rest for 5 seconds: player position drift at most 1 world unit, yaw drift at most 0.01 rad, zero shots fired.
- Deflection of 0.10 on the left stick (under PAD_DEADZONE 0.15) held 2 seconds: no movement, no look change.
- Deflection of 0.20 (above the deadzone) begins moving the player within 200 ms of the deflection.

Fail if: the pad drifts at rest, a sub-deadzone deflection moves the player, or an above-deadzone deflection does not respond within 200 ms.

## Step 4: Disconnect and reconnect

Procedure: during a running round, unplug the pad, wait, then plug it back in.

Pass thresholds, all required:
- Within 1 second of unplugging: status line shows `Controller disconnected. Keyboard and mouse active.` and the round keeps running with the timer on the wall clock.
- With hands off all controls for 2 seconds after disconnect: player position drift at most 1 world unit and yaw drift at most 0.01 rad (no stuck movement or look intent).
- Keyboard still plays immediately after disconnect: one W press moves the player, arrows look.
- Within 3 seconds of replugging: the detected-controller line returns without a page reload, and move, look, and fire all work again.

Fail if: the round stops on disconnect, any input sticks after disconnect, keyboard is dead after disconnect, or reconnect needs a reload.

## Step 5: Restart

Procedure: play a round to ROOM CLEAR or OUT OF LIGHT, then press pad A once.

Pass thresholds, all required:
- A single A press on the end screen restarts within 250 ms: round returns to running, ammo is full, timer resets to the full round, all four cells are standing.
- One press, one restart. A second press within 500 ms does not double-start, crash, or desync the state.
- Restart also works from the pad after a reconnect (step 4) without a reload.

Fail if: A does not restart, restart needs a reload, or a double press breaks the state.

## Verdict and what changes the gate

Gate closes to `VERIFIED-PHYSICAL-HARDWARE` only when all five steps PASS in one session on one recorded device, with the record block complete. Any FAIL reopens the gate as `OPEN-BLOCKED-ON-HARDWARE` with the failing step named.

What would change this record: a completed protocol run on a physical pad (closes the gate), or a change to the pad mapping, deadzone, or fire path in `website/games/echo-rounds.html` (reopens it and forces a rerun).

## Code impact

None. This file is documentation only. Zero bytes under `website/`. The harness `dev/echo-fps-proof.py` and this record are the Story 129 file set.
