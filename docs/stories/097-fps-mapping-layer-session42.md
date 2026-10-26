# Story 097: FPS controller-mapping-layer slice with keyboard fallback (Session 42, P1, Mechanism)

**Status:** Ready for development (Session 42, 2026-10-26).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (mechanism; next FPS step under the CEO top directive, buildable without hardware).
**Assigned to:** **Kai** owner. **Scout** witness (numbers independently re-run).
**Tracked by:** Session 42 plan, Story 097. Follows Story 068 (mechanic), Story 071 (probe shape), Story 074 (decision plus gate), Story 089 (mouse leg), Story 091 (playable echo-rounds slice, Session 40 green).
**Depends on:** `dev/fps-probe/` Session 40 state: `echo-rounds-slice-091.html` plus `playable-slice-check-091.js`. No gamepad dependency. No native toolchain.

## Summary

Build the controller-mapping layer on top of the Story 091 probe state: a standard gamepad layout (left stick move, right stick look, trigger fire) mapped to move/look/fire intents, with the keyboard path (WASD plus Pointer Lock plus click-to-shoot) kept as the proven fallback. The keyboard path is proven in the harness this session. The gamepad leg is recorded as a LIMITATION in the acceptance criteria, never claimed as controller support. Harness-only diff under `dev/fps-probe/`. No release cut follows (Session 40 precedent).

## jakebot decisions (advisory only, recorded)

Asked 2026-10-26 ~01:15 CDT (session local-ed66cc3b157bcdcdbd66f8c796fc4). Brief carried v0.35.0 state, clean GitHub, the three candidate priorities, and the hardware-gate framing.

Answer, proceeded on its read: Session 42 CAN build the mapping layer and CAN prove the keyboard path; it CANNOT close the controller gate (VERDICT.md: a keyboard-only run is a recorded limitation, never a pass for simultaneous look/move/fire plus gamepad leg). Any green described as controller support is the Story 082 overclaim again, one artifact later.

Asked 2026-10-26 ~01:20 CDT (session local-c2fc5af6c3776a47493ffb5ae3c36f977871147cc937c6cb015b2b5efd7a0d7a). Question: harness-only FPS slice with nothing visitor-visible, cut v0.36.0 or no-release like Session 40?

Answer: **no-release**. Version numbers exist for users; harness-only work does not warrant a cut. Session 40 precedent stands.

**Citation:** `flambeee-team/session-plan.md`, Session 42 (2026-10-26), section "jakebot decisions (advisory only, recorded)".

## Falsification test (binding, from the session plan)

Quoted from the Session 42 plan: if the mapping layer lands and the session still has no playable slice a visitor or a wire could drive end to end, then P1 was the wrong shape and the next session should be the mechanic, not the input.

Dev records the verdict on this test in the dev record: either the keyboard-driven slice plays end to end through the mapping layer, or P1 is declared the wrong shape and the finding goes to the next session plan.

## Source: Story 091 probe state (quoted verbatim where reused)

Story 091 as shipped (roadmap Session 40 entry, Session 40 green), carried forward verbatim as the base this layer stands on:

> RED run exit 1 on pre-change tree; green exit 0 twice on Chromium headless 1280x800 DPR 1x: 691 counted frames, p95 16.7 in the 15.84-17.50 band, 0 slow frames, 301/301 look, 17/17 click-pulse-fade, litHits 1 at rate 1 with unlitHits 0, shooter reveal 17/17, outcome WIN.

The mapping layer must preserve these numbers within run jitter: the slice is reused, not rebuilt. A layer run that regresses the slice (look events dropped, pulse-fade broken, lit gate inverted) is a fail, not a new baseline.

## Explicit gamepad statement (binding on this story, LIMITATION not support)

**Gamepad leg: OPEN-BLOCKED-ON-HARDWARE (15th session).** There is no physical controller on the run box, same as Sessions 33-41. No gamepad poll runs on this box, no gamepad sample is recorded, and no controller claim follows from the mapping-layer runs. The Story 074 gate stands unchanged and is not executed by this story. A keyboard-driven mapping-layer run never counts toward any gamepad criterion of that gate. The acceptance criteria below record this as AC-7 LIMITATION; any dev or QA text describing this story's green as controller support repeats the Story 082 overclaim and fails review.

The Session 42 ask to Jake (carried by the release wave, not this story): attach a pad to the run box, or authorize keyboard-only as the shipped input with controller support stated as a later addition.

## Requirements

### 1. RED run first

Before the mapping-layer code exists, dev records one failing run: a harness asserting intent mapping (move plus look plus fire intents resolve through the layer to the slice) against the pre-change tree. It fails (no layer exists), and that failing run with command, exit code, and output pasted into the dev record is the proof the green run measures new code. Code with no RED run is not done.

### 2. Scope (dev/fps-probe only, mapping layer plus keyboard proof)

- One mapping layer: standard layout intents. Left stick to move intent, right stick to look intent, trigger (or primary button) to fire intent. The layer resolves intents to the same slice inputs Story 091 drives (move, Pointer Lock look, click-to-shoot fire).
- Keyboard fallback preserved and proven: WASD move, Pointer Lock look, click fire, driven through the layer end to end in the harness at 1280x800 DPR 1x.
- Gamepad intents are structural only (mapping table plus unit-level resolution with synthetic poll frames, no hardware). Synthetic gamepad frames prove the table resolves; they prove nothing about hardware and are labeled as such.
- Frame numbers recorded with the Story 074 settlement: warmup first 30 frames excluded, frame count at least 600, p95 checked against the 15.84ms to 17.50ms band, slow frames over 33ms reported. Numbers, not adjectives.
- New or changed files under `dev/fps-probe/` ONLY. Zero new lines in `src/`, `website/`, or `share/`. No game ships.
- No native toolchain, no dependency, no build step.

### 3. Scout witness

Scout independently re-runs the mapping-layer harness on the merged tree and records matching values (pass/fail per check plus frame counts plus round outcome), same as the Story 091 two-run shape (RED pre-change exit non-zero, green merged exit 0).

### 4. No sprawl

No second room, no second enemy type, no weapon roster, no score persistence, no menus beyond the existing win/lose, no native toolchain, no dependency, no build step. Anything beyond mapping intents plus the keyboard proof is a full build and waits.

## BDD scenarios

**Scenario 1: RED run fails first.**
Given the pre-change tree, when the mapping-layer harness runs, then it exits non-zero (no layer exists) and the run is recorded as the artifact.

**Scenario 2: Keyboard path proven through the layer.**
Given the merged harness at 1280x800 DPR 1x, when WASD plus Pointer Lock plus click fire are driven through the mapping layer, then move/look/fire intents resolve to the slice inputs, targets clear only through lit-state hits, and the round reaches a win or lose screen with no build step.

**Scenario 3: Input survives the real loop.**
Given the full round running through the layer (room plus targets plus pulses plus hit gate), when move/look/fire run simultaneously, then zero inputs drop or desync, with no stuck input and no pointer-loss lockup; any drop is recorded as a fail.

**Scenario 4: Story 091 numbers preserved.**
Given the Story 091 slice reused under the layer, when the layer run completes, then look events apply, click-pulse-fade holds, lit hits count at rate 1 with unlit at 0, and shooter reveal records per shot, within run jitter of the quoted numbers; a regression is a fail, not a new baseline.

**Scenario 5: Synthetic gamepad table resolves, labeled as structural.**
Given synthetic poll frames (no hardware), when they are fed to the mapping table, then left stick resolves to move intent, right stick to look intent, and trigger to fire intent; the dev record labels this structural only with zero hardware samples.

**Scenario 6: Frame numbers in band.**
Given at least 600 frames with the first 30 excluded, when p95 is computed, then it falls inside 15.84ms to 17.50ms with slow frames over 33ms reported, or the miss is recorded as a finding, not rounded away.

**Scenario 7: Falsification test answered.**
Given the landed layer, when the session asks whether a wire can now drive the slice end to end through it, then the dev record answers yes with the run cited, or declares P1 the wrong shape and routes the next session to the mechanic, not the input.

**Scenario 8: Harness-only diff, no release.**
Given the story diff, when it is inspected, then every new or changed file sits under `dev/fps-probe/`, zero lines change under `src/`, `website/`, or `share/`, and no version cut follows (Session 40 precedent, jakebot session local-c2fc5af6c3776a47493ffb5ae3c36f977871147cc937c6cb015b2b5efd7a0d7a).

## Acceptance Criteria

**AC-1.** RED run recorded with command, exit code, and output showing the missing layer (Scenario 1).
**AC-2.** Keyboard path proven through the layer, green exit 0 on the merged tree at 1280x800 DPR 1x with a win or lose screen reached (Scenario 2).
**AC-3.** Zero input drops under the real loop, or the fail recorded plainly (Scenario 3).
**AC-4.** Story 091 numbers preserved within run jitter (Scenario 4).
**AC-5.** Synthetic gamepad table resolution recorded and labeled structural only, zero hardware samples (Scenario 5).
**AC-6.** Frame numbers recorded with warmup, frame count, band check, and slow-frame count stated (Scenario 6).
**AC-7. LIMITATION.** Explicit OPEN-BLOCKED-ON-HARDWARE statement (15th session) with zero gamepad samples and no controller claim; no text in dev or QA output describes the green as controller support (gamepad statement above).
**AC-8.** Falsification verdict recorded: wire-drivable slice cited, or P1 declared the wrong shape with the mechanic routed next (Scenario 7).
**AC-9.** Scout independent re-run with matching values recorded (section 3).
**AC-10.** Harness-only diff, no native toolchain, no dependency, no version cut (Scenario 8).
**AC-11.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

RED command plus exit code plus output; green command plus exit code twice; frame counts plus p95 plus slow-frame count per run; intent-resolution table (stick/button to intent) with synthetic-frame results labeled structural; Story 091 regression comparison (look, pulse-fade, lit/unlit, shooter reveal, outcome); falsification verdict with the cited run or the wrong-shape declaration; gamepad LIMITATION statement with sample count 0. Numbers, not adjectives.

## Non-Goals

- Any gamepad poll, gamepad sample, or controller claim on this box.
- Executing the Story 074 headed gate (named rig, needs a pad).
- Any second room, second enemy type, roster, persistence, or menu beyond the existing win/lose.
- Any `src/` game file, website change, release cut, or schedule change.
- Any native toolchain, engine choice, or parallel native plan.
- Touching `pending-post.txt` or any noon pipeline path.

## Open questions for the dev wave

1. Layer file path (extend the 091 slice in place vs new sibling under `dev/fps-probe/`; record the final path).
2. RED-run command plus exit code, and green-run frame counts plus round outcome per browser.
3. Synthetic poll frame shape used for the table check (record the exact fixture so the witness re-runs the same bytes).
