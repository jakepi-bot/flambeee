# Story 074: FPS build decision (Session 34, P1, Planning/Decision)

**Status:** Ready for review (Session 34, 2026-10-18).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (planning/decision; CEO override item 1, directive 6 governs).
**Assigned to:** Parent-owned doc. No code owner. **Kai/Riven** consult on threshold and gate shape only. No game-file change.
**Tracked by:** Session 34 plan, Story 074. References `flambeee-team/session-plan.md` Session 34, `docs/roadmap.md` Now section.
**Depends on:** Story 068 (mechanic plus falsifying test), Story 071 (probe numbers plus verdict). No code dependency.

## Summary

Decide whether the echo-rounds FPS proceeds to a minimal playable slice, and on what terms. This doc records the gamepad-open status honestly, settles the p95 threshold question with numbers, defines the minimal playable slice in one sentence, and writes a runnable headed gamepad re-run gate with named rig plus owner. Planning and decision only. No code, no build, no native toolchain.

## Source: Story 068 falsifying test (quoted verbatim)

Story 068 (`docs/stories/068-fps-web-plan-original-mechanic.md`, lines 56-58), carried forward verbatim as the test this decision answers:

> **Falsifying test (named):** Web viability is falsified if, on the mechanic's minimal probe (dark scene + one light pulse per shot + simultaneous move/look/fire), either (a) sustained Pointer Lock + Gamepad polling drops or desyncs input under load, or (b) the single-file no-build render cannot hold a readable frame rate with the transient light + lit-state hit check. A probe that passes on an empty scene and fails once the light-ammo loop runs still falsifies; the test is keyed to the mechanic, not to a hello-world page.
>
> **Native-fallback trigger (stated):** Fallback to native Windows/Mac/Linux triggers only on recorded evidence of the falsifying test above, with the failing numbers quoted. No parallel native promise, no toolchain work before that evidence exists. Phase 1 proves web; Phase 2 native only if Phase 1 fails with evidence.

## Source: Story 071 numbers (quoted verbatim)

Story 071 VERDICT (`dev/fps-probe/VERDICT.md`, Session 33 verdict section), carried forward verbatim:

> CONDITIONAL PASS with recorded limitations. Render axis: PASS on both browsers (Chromium 59.9 FPS mean, p95 16.8 ms; Firefox 60 FPS mean, p95 17.16 ms; 0 slow frames; floor is 30 FPS mean with p95 at or below 33.4 ms). Input-event axis: PASS (0 drops over 244 injected edges, 100 percent hold agreement, both browsers). Negative control: FAILS as required (19.5 and 19.9 FPS), so the harness is not a tautology. Falsification triggers: neither (a) nor (b) fired on the measurable axes. No native-fallback trigger: no recorded failing numbers, so no Phase 2 native decision. Binding limitations: keyboard-only (no gamepad on run box, 0 non-empty gamepad samples), headless Pointer Lock error, headless FPS is compute headroom not display proof. A pass here does not grow into building the FPS; the probe stops at this verdict per the no-sprawl rule.

## jakebot decision (advisory only, recorded)

**Question put to jakebot (Session 34, 2026-10-18 ~01:12 CDT, session 20261018_011238_406ef3):** Is the right Session 34 Wave 1-2 set (a) P1 FPS build-decision plus P1 small playable improvement plus P2 currency, vs (b) P1 gamepad-only re-run on this box (no pad) plus P1 Day Pad tweak plus P2 currency.

**Answer:** **Option A. Not close.** Option B item P1 is dead on arrival (no pad on this box reproduces the same OPEN result; rerun of a known environmental fact). Option B also puts the only shippable item second as an unevidenced tweak.

Five constraints recorded for the stories: (1) gamepad gate must be executable by someone else without the author present (named rig, headed mode, pass criteria, owner; if it cannot run in Session 35 it is a note not a gate); (2) settle the FPS threshold before calling the probe a pass (p95 16.8ms vs 16.67ms budget is 0.8 pct miss, Firefox 17.16 is 2.9 pct miss; state warmup exclusion, frame count, hard bar vs tolerance band); (3) minimal playable slice needs one sentence of acceptance (move, look, one interaction loop, win/lose state, playable end to end at target resolution; else it is a full build and waits); (4) small improvement must be verifiable without the share path (commit plus local serve plus headed check runnable on this box); (5) Day Pad daily-reuse validation does not disappear (fold into the improvement story or park by name with a trigger; carried twice).

**Citation:** `flambeee-team/session-plan.md`, Session 34 (2026-10-18), section "jakebot decision (advisory only, recorded)", session 20261018_011238_406ef3.

## Rules carried into this story

**No-sprawl rule.** This decision does not build the FPS. No native toolchain, no engine choice, no parallel native plan, no full build. A go decision authorizes exactly the minimal playable slice defined below, nothing more.

**Gamepad leg status: OPEN-BLOCKED-ON-HARDWARE.** The run box has no physical pad (0 non-empty gamepad samples, Session 33 VERDICT.md). A gamepad re-run on this box is forbidden: it reproduces a known environmental fact. The runnable gate below runs on a named rig with a pad, owned, in Session 35 or it is a note not a gate.

## p95 threshold settlement

Budget: 16.67ms per frame (60 FPS reference). Measured mechanic-loop p95: Chromium 16.8ms (0.8 pct miss), Firefox 17.16ms (2.9 pct miss). Frame counts: Chromium 600 frames, Firefox 601 frames over about 10 s runs. Warmup: first 30 frames excluded from the p95 computation (startup jitter, tab settle). Slow frames over 33ms: 0 on both browsers.

Settlement: tolerance band, not hard bar. The 16.67ms budget is the center of a plus or minus 5 pct tolerance band (15.84ms to 17.50ms) for headless compute-headroom runs; both measured p95 values fall inside it. Rationale: headless has no vsync or GPU path, so sub-millisecond misses against a hard 16.67ms bar measure timer granularity, not readability. The binding readability floor stays the Session 33 floor (30 FPS mean with p95 at or below 33.4ms), which both browsers clear by a wide margin. The headed gate below re-checks p95 against the same band with warmup excluded and frame count recorded; a headed p95 outside 17.50ms fails the gate.

## Minimal playable echo-rounds slice (one-sentence acceptance)

The slice is accepted when the player can move with WASD, look with Pointer Lock or right stick, fire light pulses that gate hits on lit state, clear one dark room of targets, and reach a win or lose screen end to end at 1280x800 with no build step.

Anything beyond that sentence (second room, second enemy type, weapon roster, score persistence, menus beyond win/lose) is a full build and waits.

## Runnable headed gamepad gate

Rig: jake-dev-desk (headed Chromium plus Firefox desktop, one physical Xbox-layout pad over USB, display attached). Mode: headed (not headless), mechanic-loop probe plus playable slice, 10 s scripted loop then 2 min human play. Pass criteria: (a) gamepad poll non-empty on every frame while pad connected, (b) 0 input drops over the scripted loop, (c) headed p95 inside the 15.84ms to 17.50ms band with first 30 frames excluded and frame count at least 600 recorded, (d) Pointer Lock acquires with gesture and survives fire-move-look, (e) one room cleared to win or lose screen by pad plus Pointer Lock input. Owner: Kai runs the gate in Session 35; Scout witnesses the numbers. If the gate cannot run in Session 35 on the named rig, it is a note not a gate and no ship claim follows.

## Requirements

### 1. Decision recorded, sources verbatim
- Story 068 falsifying test quoted verbatim above; Story 071 numbers quoted verbatim above.
- Threshold settled as tolerance band with warmup, frame count, and hard-vs-tolerance stated.

### 2. Gamepad leg honest
- Status OPEN-BLOCKED-ON-HARDWARE stated; no gamepad re-run scheduled on this box.
- Runnable gate names rig, mode, pass criteria, owner.

### 3. Playable slice bounded
- One-sentence acceptance above; expansion items named as out of scope.

### 4. Planning only
- No change to `src/`, `website/`, `share/Flambeee/`, `scripts/`, `dev/fps-probe/`, game files, sw.js, blog, or releases.
- No native toolchain, no dependency, no build step introduced by this story.

## BDD scenarios

**Scenario 1: Falsifying test cited verbatim.**
Given the Session 33 probe verdict, when this decision is read, then it quotes the Story 068 falsifying test and native-fallback trigger verbatim with attribution.

**Scenario 2: Probe numbers cited verbatim.**
Given the verdict, when this decision is read, then it quotes the Story 071 numbers verbatim (Chromium 59.9 FPS mean p95 16.8 ms, Firefox 60 FPS mean p95 17.16 ms, 0 slow frames, sabotage 19.5 and 19.9 FPS) with attribution.

**Scenario 3: p95 threshold settled.**
Given budget 16.67ms and measured p95 16.8ms Chromium (0.8 pct miss) and 17.16ms Firefox (2.9 pct miss), when the decision is recorded, then the threshold is settled as a plus or minus 5 pct tolerance band (15.84ms to 17.50ms) with warmup exclusion of the first 30 frames and frame counts 600 and 601 stated, and the hard-bar option rejected with the headless timer-granularity reason.

**Scenario 4: Gamepad leg OPEN-BLOCKED-ON-HARDWARE.**
Given 0 non-empty gamepad samples on the run box, when the gamepad question is asked, then the status is recorded as OPEN-BLOCKED-ON-HARDWARE and no re-run on this box is scheduled.

**Scenario 5: Runnable gate complete.**
Given the open gamepad leg, when the gate is read, then it names the rig (jake-dev-desk), the mode (headed), the pass criteria (non-empty poll every frame, 0 drops, p95 in band, Pointer Lock survives, one room cleared), and the owner (Kai runs, Scout witnesses, Session 35), or it is labeled a note not a gate.

**Scenario 6: Playable slice is one sentence.**
Given the slice definition, when acceptance is checked, then it is exactly the one sentence above (move, look, fire light, clear one room, win or lose screen, 1280x800, no build), and any second room, second enemy type, roster, persistence, or extra menu is out of scope.

**Scenario 7: No sprawl.**
Given any decision outcome, when the story diff is inspected, then it contains only this Markdown file, no native toolchain, no engine choice, no FPS build, and no website/blog/release edit.

**Scenario 8: jakebot citation present.**
Given the Wave 1-2 set decision, when this doc is reviewed, then it records the question, the answer (Option A, not close; B dead on arrival), the five constraints, and the citation session 20261018_011238_406ef3.

## Acceptance Criteria

**AC-1.** Story 068 falsifying test plus Story 071 numbers quoted verbatim with attribution (Scenarios 1, 2).
**AC-2.** p95 threshold settled as tolerance band with warmup, frame count, and hard-vs-tolerance stated (Scenario 3).
**AC-3.** Gamepad leg OPEN-BLOCKED-ON-HARDWARE with runnable gate naming rig, mode, pass criteria, owner (Scenarios 4, 5).
**AC-4.** One-sentence playable-slice acceptance with expansion out of scope (Scenario 6).
**AC-5.** Planning only: no code, no toolchain, no website/blog/release change (Scenario 7).
**AC-6.** jakebot question/answer/five constraints/citation recorded as above (Scenario 8).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Any FPS build beyond authorizing the bounded slice in a later dev story.
- Any native toolchain, engine choice, or parallel native plan.
- A second mechanic, a shortlist, or a mechanic vote.
- Any change to small web games, the site, or the release process.

## Open questions for dev wave

1. Slice target resolution confirmed at 1280x800, or counter-propose one resolution with reason.
2. Named-rig availability in Session 35 (Kai confirms jake-dev-desk pad plus headed browsers).
3. Headed p95 band re-check procedure (frame count floor, warmup length, recording format).
