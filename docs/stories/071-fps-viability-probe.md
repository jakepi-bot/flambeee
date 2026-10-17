# Story 071: FPS viability probe, echo-rounds mechanic (Session 33, P1, Dev)

**Status:** Ready for development (Session 33, 2026-10-17).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (dev; CEO override item 1, directive 6 governs).
**Assigned to:** **Kai** owner for probe plus harness. **Riven** consult on input and render shape. **Scout** proves the falsifying test.
**Tracked by:** Session 33 plan, Story 071. Built from Story 068.
**Depends on:** Story 068 (mechanic plus viability test definition). No code dependency beyond the probe itself.

## Summary

Build the minimal probe that runs the Story 068 falsifying test against the echo-rounds mechanic and record the verdict with numbers. Mechanic under test: echo-rounds (shots emit light, hits require lit state, firing reveals shooter). Deliverable is the verdict plus passing or failing numbers, recorded as a test plan or decision artifact. No native toolchain, no parallel native work, no FPS build beyond the minimal probe scene.

## Source: Story 068

Story 068 (`docs/stories/068-fps-web-plan-original-mechanic.md`) names the candidate mechanic echo-rounds: dark arena, shots emit light pulses, hits count only on lit targets, firing reveals shooter. Reskin test recorded per directive 6.

Quoted from Story 068 lines 56-58, carried forward verbatim as the test this probe runs:

> **Falsifying test (named):** Web viability is falsified if, on the mechanic's minimal probe (dark scene + one light pulse per shot + simultaneous move/look/fire), either (a) sustained Pointer Lock + Gamepad polling drops or desyncs input under load, or (b) the single-file no-build render cannot hold a readable frame rate with the transient light + lit-state hit check. A probe that passes on an empty scene and fails once the light-ammo loop runs still falsifies; the test is keyed to the mechanic, not to a hello-world page.
>
> **Native-fallback trigger (stated):** Fallback to native Windows/Mac/Linux triggers only on recorded evidence of the falsifying test above, with the failing numbers quoted. No parallel native promise, no toolchain work before that evidence exists. Phase 1 proves web; Phase 2 native only if Phase 1 fails with evidence.

## jakebot decision (advisory only, recorded)

**Question put to jakebot (Session 33, 2026-10-17 ~01:11 CDT, session 20261017_011130_01bb1d):** Is the right Session 33 Wave 1-2 set (a) P1 FPS viability probe plus P1 Apps first app plus P2 currency, vs (b) deferring Apps to Session 34 for one-P1-per-session rhythm.

**Answer:** **Option A. Two P1 stories, one ship, one bounded probe, one verification.** CEO directive 7 says do both at the same time; Principle 1 (every session ships something playable) means the probe alone ships no playable thing, the Apps app is the ship. Divisions independent by construction (069 sibling of 068), no merge hazard. One-P1-per-session is rhythm, not a rule; the real constraint is worker-stall capacity (Story 062), protected here because the probe stops at its falsifying verdict.

Three conditions recorded: (1) FPS probe stops at the verdict, no native toolchain before recorded evidence, a pass does not grow into building the FPS; (2) do not re-test known-yes API existence, test the mechanic needs (simultaneous look/move/fire under load, transient-light render with lit-state hit gate, readable frame rate with loop running); (3) resolve 068 open question 3 (controller matrix, gamepad availability on run box) before the probe runs, keyboard-only is a recorded limitation never a pass.

**Citation:** `flambeee-team/session-plan.md`, Session 33 (2026-10-17), section "jakebot decision (advisory only, recorded)", session 20261017_011130_01bb1d.

## Rules carried into this story

**No-sprawl rule.** The probe stops at the verdict. No native toolchain before recorded evidence. A pass does not grow into building the FPS; it records PASS with numbers and stops.

**Controller-matrix resolution (068 open Q3).** Gamepad availability on the run box is checked before the probe runs. Keyboard-only is a recorded limitation, never a pass. Minimum matrix: Chromium plus Firefox desktop.

**Test the mechanic, not the APIs.** Pointer Lock plus Gamepad API existence is known-yes per the Session 32 market check. The probe measures simultaneous look/move/fire under load, transient-light render with lit-state hit gate, and readable frame rate with the loop running.

## Requirements

### 1. Minimal probe scene

- Single-file no-build static HTML/JS probe: dark scene, one light pulse per shot, simultaneous move/look/fire.
- Nothing more: no weapons, no maps, no enemy AI beyond what the lit-state hit check needs.
- Probe plus harness owned by Kai; Riven consults on input and render shape only.

### 2. Harness and verdict

- Harness runs the falsifying test above and records the verdict (PASS or FAIL) with numbers: input drop/desync counts under load, frame-rate readings with the light-ammo loop running.
- Scout proves the falsifying test: the harness must fail on a known-bad input (for example the empty-scene pass that fails once the light-ammo loop runs still falsifies) so a green run is a measurement, not a tautology.
- Deliverable is the verdict plus numbers as a test plan or decision artifact.

### 3. Evidence-gated fallback, no parallel native

- No native toolchain, no engine choice, no parallel native plan before recorded evidence exists.
- If the probe falsifies, the failing numbers are quoted and native Windows/Mac/Linux becomes a Phase 2 decision with evidence.

## BDD scenarios

**Scenario 1: Probe runs the mechanic loop.**
Given the echo-rounds rule (shots emit the light that hits require), when the probe runs, then each shot emits one transient light pulse, hits are gated on lit state, and firing marks the shooter visible.

**Scenario 2: Simultaneous input under load.**
Given Pointer Lock look plus WASD/keys plus Gamepad poll (left stick move, right stick look, trigger fire), when move/look/fire run together under load, then no stuck input and no pointer-loss lockup occur, or the drop/desync is recorded as falsifying evidence.

**Scenario 3: Render holds a readable rate with the loop running.**
Given the dark scene with transient per-shot light plus lit-state hit check in one file with no build step, when the light-ammo loop runs on desktop Chromium and Firefox, then the frame rate stays readable and the numbers are recorded, or the shortfall is recorded as falsifying evidence.

**Scenario 4: Empty-scene pass does not pass.**
Given a probe that passes on an empty scene, when the light-ammo loop is enabled and it fails, then the verdict is FAIL (falsified); the test is keyed to the mechanic, not to a hello-world page.

**Scenario 5: Controller matrix resolved first.**
Given 068 open Q3, when the probe runs, then gamepad availability on the run box is recorded first; a keyboard-only run is recorded as a limitation, never as a pass.

**Scenario 6: No sprawl.**
Given any verdict, when the probe wave ends, then no native toolchain was introduced, no FPS build beyond the minimal probe scene exists, and a pass did not grow into building the FPS.

**Scenario 7: jakebot citation present.**
Given the Wave 1-2 set decision, when this doc is reviewed, then it records the question, the answer (Option A: two P1, one ship, one probe, one verification; directive 7 both-at-once; Principle 1 ship), and the citation session 20261017_011130_01bb1d.

## Acceptance Criteria

**AC-1.** Minimal single-file no-build probe runs the echo-rounds loop (Scenarios 1, 2, 3).
**AC-2.** Falsifying test from Story 068 quoted verbatim and executed with numbers recorded (Scenarios 2, 3, 4).
**AC-3.** Controller matrix resolved before the probe; keyboard-only recorded as limitation, never a pass (Scenario 5).
**AC-4.** No-sprawl rule holds: verdict only, no native toolchain, no FPS build (Scenario 6).
**AC-5.** jakebot question/answer/citation recorded as above (Scenario 7).
**AC-6.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- A second mechanic, a shortlist, or a mechanic vote. Echo-rounds only.
- Any FPS build beyond the minimal probe scene.
- Any native toolchain, engine choice, or parallel native plan.
- Any change to small web games, the site, or the release process.

## Open questions for dev wave

1. Frame-rate readability bar: numeric floor for "readable" under the light-ammo loop (dev wave proposes, parent confirms).
2. Probe harness location and run command (Kai proposes; must run from the repo with no new dependency).
3. Minimum Gamepad layouts to poll on the run box (dev wave proposes minimum: Chromium plus Firefox desktop).
