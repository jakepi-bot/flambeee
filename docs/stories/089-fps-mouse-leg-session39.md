# Story 089: FPS echo-rounds mouse leg plus lit-target hit gate (Session 39, P2, Mechanism)

**Status:** Ready for development (Session 39, 2026-10-23).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (mechanism; FPS mouse leg buildable without hardware).
**Assigned to:** **Kai** owner. **Scout** witness (numbers independently re-run).
**Tracked by:** Session 39 plan, Story 089. Follows Story 068 (mechanic), Story 071 (probe shape), Story 074 (decision plus gate).
**Depends on:** `dev/fps-probe/` harness shape. No gamepad dependency. No native toolchain.

## Summary

Build the FPS leg that needs no hardware: pointer-lock look plus click-to-shoot plus the lit-target hit gate, in the `dev/fps-probe/` harness shape. This is the original mechanic loop from Story 068 with the mouse input leg standing in for the blocked gamepad leg. RED run first on the pre-change tree. No game file ships; no native toolchain; no controller claim.

## jakebot decision (advisory only, recorded)

Session 39 Wave 1 priorities per session 20261023_011104_76722e: (c) SECOND, next FPS step buildable without hardware. FPS is the CEO top directive, gamepad gate open-blocked 7 sessions. Build the mouse/pointer-lock leg plus the lit-target hit gate (the original mechanic), which needs no pad. No fabricated controller claim; matrix stays OPEN-BLOCKED-ON-HARDWARE explicitly.

**Citation:** `flambeee-team/session-plan.md`, Session 39 (2026-10-23), section "jakebot decision (advisory only, recorded)", session 20261023_011104_76722e.

## Source: Story 068 mechanic (quoted verbatim where reused)

Story 068 (`docs/stories/068-fps-web-plan-original-mechanic.md`, lines 38-44), carried forward verbatim as the mechanic this leg implements:

> **Candidate name: echo-rounds (light-ammo FPS).**
>
> The arena is dark. You fire light, not bullets. Each shot emits a short light pulse that reveals geometry and targets while it lasts, then fades. Hits count only on lit targets. Movement is silent and keeps you hidden; firing reveals you as well as the target. The core loop is a tradeoff you manage every shot: see more, be seen more.

Story 068 viability-test scope (lines 52-53), bounding this leg:

> 1. Input: simultaneous Pointer Lock look + WASD/keys + Gamepad API poll (left stick move, right stick look, trigger fire) with no stuck input and no pointer-loss lockup during fire-move-look.
> 2. Render: dark first-person scene with transient per-shot light, lit-state hit gate, sustained readable frame rate on desktop Chromium and Firefox with no build step.

This story builds the Pointer Lock plus click-to-shoot subset of item 1 with the full item 2. The Gamepad API poll clause is explicitly out of scope (see gamepad statement below).

## Source: Story 074 gate (quoted verbatim where reused)

Story 074 (`docs/stories/074-fps-build-decision.md`, lines 42, 56-58), carried forward verbatim:

> **Gamepad leg status: OPEN-BLOCKED-ON-HARDWARE.** The run box has no physical pad (0 non-empty gamepad samples, Session 33 VERDICT.md). A gamepad re-run on this box is forbidden: it reproduces a known environmental fact. The runnable gate below runs on a named rig with a pad, owned, in Session 35 or it is a note not a gate.

> Rig: jake-dev-desk (headed Chromium plus Firefox desktop, one physical Xbox-layout pad over USB, display attached). Mode: headed (not headless), mechanic-loop probe plus playable slice, 10 s scripted loop then 2 min human play. Pass criteria: (a) gamepad poll non-empty on every frame while pad connected, (b) 0 input drops over the scripted loop, (c) headed p95 inside the 15.84ms to 17.50ms band with first 30 frames excluded and frame count at least 600 recorded, (d) Pointer Lock acquires with gesture and survives fire-move-look, (e) one room cleared to win or lose screen by pad plus Pointer Lock input. Owner: Kai runs the gate in Session 35; Scout witnesses the numbers. If the gate cannot run in Session 35 on the named rig, it is a note not a gate and no ship claim follows.

## Explicit gamepad statement (binding on this story)

**Gamepad leg: OPEN-BLOCKED-ON-HARDWARE.** There is no physical controller on the run box, same as Sessions 33-38. No gamepad poll runs on this box, no gamepad sample is recorded, and no controller claim follows from the mouse-leg runs. The Story 074 gate above stands unchanged and is not executed by this story. A keyboard/mouse run never counts toward criteria (a), (b), or (e) of that gate.

## Requirements

### 1. RED run first (the rule)

Before the mouse-leg code exists, dev records one failing run as the artifact: the harness asserting pointer-lock look plus click-to-shoot plus lit-state hit gating against the pre-change tree. It fails (no mouse leg exists), and that failing run with command, exit code, and output pasted into the dev record is the proof the green run measures new code. Code with no RED run is not done.

### 2. Scope (dev/fps-probe harness shape, no game-file ship)

- Pointer-lock look: acquire on gesture, yaw/pitch from mouse movement, survives fire-move-look with no stuck input and no pointer-loss lockup.
- Click-to-shoot: one click emits one light pulse; pulse reveals geometry and targets while it lasts, then fades.
- Lit-target hit gate: hits count only on lit targets; a shot against an unlit target registers no hit. Firing marks the shooter revealed (self-reveal flag recorded per shot).
- Frame numbers recorded with the Story 074 settlement: warmup first 30 frames excluded, frame count at least 600, p95 checked against the 15.84ms to 17.50ms band, 0 slow frames over 33ms reported. Numbers, not adjectives.
- Harness lives under `dev/fps-probe/` (extend in place, Story 071 shape). No file under `src/`, `website/`, or `share/` is created or modified. No game ships.

### 3. Scout witness

Scout independently re-runs the harness on the merged tree and records matching values (pass/fail per check plus frame counts), same as the Story 071 two-run shape (RED pre-change exit non-zero, green merged exit 0).

### 4. No sprawl

No second room, no second enemy type, no weapon roster, no score persistence, no menus beyond the probe readout, no native toolchain, no dependency, no build step. The Story 074 one-sentence slice acceptance still requires the gamepad leg and is not claimed here.

## BDD scenarios

**Scenario 1: RED run fails first.**
Given the pre-change tree, when the mouse-leg harness runs, then it exits non-zero (no pointer-lock look, no lit-hit gate) and the run is recorded as the artifact.

**Scenario 2: Pointer-lock look works.**
Given the merged harness, when mouse-look input runs through fire-move-look, then yaw/pitch track the input with no stuck input and no pointer-loss lockup.

**Scenario 3: Click emits one light pulse.**
Given the merged harness, when one click fires, then exactly one transient light pulse emits, reveals targets while it lasts, and fades.

**Scenario 4: Lit gate decides hits.**
Given a lit target and an unlit target, when shots land on each, then the lit shot counts a hit and the unlit shot counts no hit; each shot sets the shooter-revealed flag.

**Scenario 5: Frame numbers in band.**
Given at least 600 frames with the first 30 excluded, when p95 is computed, then it falls inside 15.84ms to 17.50ms with 0 slow frames over 33ms, or the miss is recorded as a finding, not rounded away.

**Scenario 6: Gamepad leg stays open-blocked.**
Given no pad on the run box, when this story lands, then the dev record states OPEN-BLOCKED-ON-HARDWARE, records zero gamepad samples, and makes no controller claim.

**Scenario 7: No game-file ship.**
Given the story diff, when it is inspected, then no file under `src/`, `website/`, or `share/` is created or modified, and no native toolchain or dependency appears.

## Acceptance Criteria

**AC-1.** RED run recorded with command, exit code, and output showing the missing leg (Scenario 1).
**AC-2.** Pointer-lock look plus click-to-shoot plus lit-target hit gate proven in the harness, green exit 0 on the merged tree (Scenarios 2, 3, 4).
**AC-3.** Frame numbers recorded with warmup, frame count, band check, and slow-frame count stated (Scenario 5).
**AC-4.** Scout independent re-run with matching values recorded (section 3).
**AC-5.** Explicit OPEN-BLOCKED-ON-HARDWARE statement with zero gamepad samples and no controller claim (Scenario 6).
**AC-6.** No game-file ship, no native toolchain, no dependency (Scenario 7).
**AC-7.** Story 068 mechanic and Story 074 gate quoted verbatim with attribution; jakebot citation 20261023_011104_76722e recorded.
**AC-8.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Any gamepad poll, gamepad sample, or controller claim on this box.
- Executing the Story 074 headed gate (named rig, needs a pad).
- Any playable slice, win/lose screen, room clear, or `src/` game file.
- Any native toolchain, engine choice, or parallel native plan.
- Any website, release, or schedule change.

## Open questions for dev wave

1. Harness file path (extend in place vs new sibling under `dev/fps-probe/`; record the final path).
2. RED-run command plus exit code, and green-run frame counts per browser.
3. Pointer Lock mode used in the harness (headless error is a known Story 071 limitation; record how look input was driven).
