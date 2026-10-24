# Story 091: FPS playable echo-rounds slice in harness (Session 40, P1, Mechanism)

**Status:** Ready for development (Session 40, 2026-10-24).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (mechanism; first playable round of the CEO top-directive FPS, buildable without hardware).
**Assigned to:** **Kai** owner. **Scout** witness (numbers independently re-run).
**Tracked by:** Session 40 plan, Story 091. Follows Story 068 (mechanic), Story 071 (probe shape), Story 074 (decision plus gate), Story 089 (mouse leg).
**Depends on:** `dev/fps-probe/` harness shape plus the Story 089 mouse leg. No gamepad dependency. No native toolchain.

## Summary

Combine the proven mouse leg with the mechanic loop into one playable echo-rounds round under `dev/fps-probe/` ONLY. This is the Story 074 one-sentence playable slice, mouse-input edition: move, look, fire light pulses that gate hits on lit state, clear one dark room, reach a win or lose screen end to end at 1280x800 DPR 1x with no build step. RED run first on the pre-change tree. No game file ships; no native toolchain; no controller claim.

## jakebot decision (advisory only, recorded)

Session 40 Wave 1 priorities per jakebot session local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4: (a) FIRST, FPS playable echo-rounds slice, harness-only. Mouse leg proven; nothing in the slice needs a controller. Scope guard from VERDICT.md no-sprawl rule: one story, Story 074 one-sentence playable-slice acceptance at 1280x800 DPR 1x, new files under `dev/fps-probe/` only, zero lines in src/website/share, no native toolchain, no gamepad claim. Falsifying test named before code (slice that drops input under the real loop is a fail).

**Citation:** `flambeee-team/session-plan.md`, Session 40 (2026-10-24), section "jakebot decision (advisory only, recorded)", session local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4.

## Source: Story 068 mechanic (quoted verbatim where reused)

Story 068 (`docs/stories/068-fps-web-plan-original-mechanic.md`, lines 38-40), carried forward verbatim as the mechanic this slice plays:

> **Candidate name: echo-rounds (light-ammo FPS).**
>
> The arena is dark. You fire light, not bullets. Each shot emits a short light pulse that reveals geometry and targets while it lasts, then fades. Hits count only on lit targets. Movement is silent and keeps you hidden; firing reveals you as well as the target. The core loop is a tradeoff you manage every shot: see more, be seen more.

Story 068 viability-test scope (lines 52-53), bounding this slice:

> 1. Input: simultaneous Pointer Lock look + WASD/keys + Gamepad API poll (left stick move, right stick look, trigger fire) with no stuck input and no pointer-loss lockup during fire-move-look.
> 2. Render: dark first-person scene with transient per-shot light, lit-state hit gate, sustained readable frame rate on desktop Chromium and Firefox with no build step.

This story plays the Pointer Lock plus WASD plus click-to-shoot subset of item 1 with the full item 2, inside one clearable room. The Gamepad API poll clause is explicitly out of scope (see gamepad statement below).

## Source: Story 074 gate (quoted verbatim where reused)

Story 074 (`docs/stories/074-fps-build-decision.md`, lines 42, 58), carried forward verbatim:

> **Gamepad leg status: OPEN-BLOCKED-ON-HARDWARE.** The run box has no physical pad (0 non-empty gamepad samples, Session 33 VERDICT.md). A gamepad re-run on this box is forbidden: it reproduces a known environmental fact. The runnable gate below runs on a named rig with a pad, owned, in Session 35 or it is a note not a gate.
>
> Rig: jake-dev-desk (headed Chromium plus Firefox desktop, one physical Xbox-layout pad over USB, display attached). Mode: headed (not headless), mechanic-loop probe plus playable slice, 10 s scripted loop then 2 min human play. Pass criteria: (a) gamepad poll non-empty on every frame while pad connected, (b) 0 input drops over the scripted loop, (c) headed p95 inside the 15.84ms to 17.50ms band with first 30 frames excluded and frame count at least 600 recorded, (d) Pointer Lock acquires with gesture and survives fire-move-look, (e) one room cleared to win or lose screen by pad plus Pointer Lock input. Owner: Kai runs the gate in Session 35; Scout witnesses the numbers. If the gate cannot run in Session 35 on the named rig, it is a note not a gate and no ship claim follows.

Story 074 one-sentence playable-slice acceptance (line 52), the acceptance this story executes in mouse-input form:

> The slice is accepted when the player can move with WASD, look with Pointer Lock or right stick, fire light pulses that gate hits on lit state, clear one dark room of targets, and reach a win or lose screen end to end at 1280x800 with no build step.

Run condition added by the Session 40 plan: DPR 1x. The "or right stick" clause is not exercised (no pad on this box); WASD plus Pointer Lock plus click-to-shoot carry the slice.

## Source: Story 089 mouse-leg numbers (quoted verbatim where reused)

Story 089 as shipped (roadmap v0.34.0 entry, Session 39), carried forward verbatim as the proven leg this slice stands on:

> RED run exit 1 on pre-change tree; green exit 0 twice: 691 counted frames, p95 16.7 inside the 15.84 to 17.50 band, 0 slow frames, 301/301 look events applied, 17/17 click-pulse-fade, litHits 1 at rate 1 with unlitHits 0, shooter reveal 17/17. Scout witness re-ran with values matching exactly. Default mechanic-loop regression green (601 frames, p95 16.7).

The slice must preserve these numbers within run jitter: the mouse leg is reused, not rebuilt. A slice run that regresses the leg (look events dropped, pulse-fade broken, lit gate inverted) is a fail, not a new baseline.

## Explicit gamepad statement (binding on this story)

**Gamepad leg: OPEN-BLOCKED-ON-HARDWARE.** There is no physical controller on the run box, same as Sessions 33-39. No gamepad poll runs on this box, no gamepad sample is recorded, and no controller claim follows from the slice runs. The Story 074 gate above stands unchanged and is not executed by this story. A keyboard/mouse slice run never counts toward criteria (a), (b), or (e) of that gate.

## Requirements

### 1. RED run first, falsifying rule stated up front (the rule)

Before the slice code exists, dev records one failing run as the artifact: a harness asserting one playable round (move plus look plus fire plus lit-gated hits plus one room clear plus win/lose screen) against the pre-change tree. It fails (no slice exists), and that failing run with command, exit code, and output pasted into the dev record is the proof the green run measures new code. Code with no RED run is not done.

Falsifying rule, stated before code: **a slice that drops input under the real loop is a fail.** If, once the full round runs (dark room plus targets plus pulses plus hit gate), simultaneous move/look/fire drops or desyncs input, or the frame rate falls out of readability, the slice fails and no acceptance is claimed. A round that passes on an empty room and fails once targets plus pulses run still fails; the test is keyed to the played round, not to a hello-world page.

### 2. Scope (dev/fps-probe only, one playable round)

- One dark room of targets, entered with WASD move, Pointer Lock look, click-to-shoot fire.
- Each shot emits one transient light pulse; hits count only on lit targets; each shot sets the shooter-revealed flag (Story 068 loop, Story 089 gate, now played).
- Round ends on a win screen (room cleared) or a lose screen (budget or timer exhausted; dev records which). One room, one clear, one of two screens.
- New files under `dev/fps-probe/` ONLY. Zero new lines in `src/`, `website/`, or `share/`. No game ships.
- Frame numbers recorded with the Story 074 settlement: warmup first 30 frames excluded, frame count at least 600, p95 checked against the 15.84ms to 17.50ms band, slow frames over 33ms reported. Numbers, not adjectives.
- No native toolchain, no dependency, no build step.

### 3. Scout witness

Scout independently re-runs the slice harness on the merged tree and records matching values (pass/fail per check plus frame counts plus round outcome), same as the Story 089 two-run shape (RED pre-change exit non-zero, green merged exit 0).

### 4. No sprawl

No second room, no second enemy type, no weapon roster, no score persistence, no menus beyond win/lose, no native toolchain, no dependency, no build step. Anything beyond the Story 074 sentence is a full build and waits.

## BDD scenarios

**Scenario 1: RED run fails first.**
Given the pre-change tree, when the slice harness runs, then it exits non-zero (no playable round exists) and the run is recorded as the artifact.

**Scenario 2: One round plays end to end.**
Given the merged harness at 1280x800 DPR 1x, when the player moves with WASD, looks with Pointer Lock, and fires light pulses, then targets clear only through lit-state hits and the round reaches a win or lose screen with no build step.

**Scenario 3: Input survives the real loop.**
Given the full round running (room plus targets plus pulses plus hit gate), when move/look/fire run simultaneously, then zero inputs drop or desync, with no stuck input and no pointer-loss lockup; any drop is recorded as a fail per the falsifying rule.

**Scenario 4: Mouse-leg numbers preserved.**
Given the Story 089 leg reused in the slice, when the slice run completes, then look events apply, click-pulse-fade holds, lit hits count at rate 1 with unlit at 0, and shooter reveal records per shot, within run jitter of the quoted numbers; a regression is a fail, not a new baseline.

**Scenario 5: Frame numbers in band.**
Given at least 600 frames with the first 30 excluded, when p95 is computed, then it falls inside 15.84ms to 17.50ms with slow frames over 33ms reported, or the miss is recorded as a finding, not rounded away.

**Scenario 6: Gamepad leg stays open-blocked.**
Given no pad on the run box, when this story lands, then the dev record states OPEN-BLOCKED-ON-HARDWARE, records zero gamepad samples, and makes no controller claim.

**Scenario 7: Harness-only diff.**
Given the story diff, when it is inspected, then every new file sits under `dev/fps-probe/`, zero lines change under `src/`, `website/`, or `share/`, and no native toolchain or dependency appears.

## Acceptance Criteria

**AC-1.** RED run recorded with command, exit code, and output showing the missing slice, falsifying rule stated up front (Scenario 1, section 1).
**AC-2.** One playable round proven in the harness, green exit 0 on the merged tree at 1280x800 DPR 1x (Scenario 2).
**AC-3.** Zero input drops under the real loop, or the fail recorded plainly (Scenario 3).
**AC-4.** Story 089 leg numbers preserved within run jitter (Scenario 4).
**AC-5.** Frame numbers recorded with warmup, frame count, band check, and slow-frame count stated (Scenario 5).
**AC-6.** Scout independent re-run with matching values recorded (section 3).
**AC-7.** Explicit OPEN-BLOCKED-ON-HARDWARE statement with zero gamepad samples and no controller claim (Scenario 6).
**AC-8.** Harness-only diff, no native toolchain, no dependency (Scenario 7).
**AC-9.** Stories 068, 074, and 089 quoted verbatim with attribution; jakebot session local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4 recorded.
**AC-10.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Any gamepad poll, gamepad sample, or controller claim on this box.
- Executing the Story 074 headed gate (named rig, needs a pad).
- Any second room, second enemy type, roster, persistence, or menu beyond win/lose.
- Any `src/` game file, website change, release, or schedule change.
- Any native toolchain, engine choice, or parallel native plan.

## Open questions for dev wave

1. Slice file path (extend the Story 089 probe in place vs new sibling under `dev/fps-probe/`; record the final path).
2. RED-run command plus exit code, and green-run frame counts plus round outcome per browser.
3. Lose condition used (budget vs timer; record which and why it fits the light-ammo tradeoff).
