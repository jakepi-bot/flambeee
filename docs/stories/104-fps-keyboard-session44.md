# Story 104: FPS keyboard-leg slice through the 097 mapping layer (Session 44, P2, Bounded mechanism)

**Status:** Ready for development (Session 44, 2026-10-28).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (bounded; dev wave runs only if hours remain after Stories 103 and 105. Deferral is an accepted outcome, recorded not failed).
**Assigned to:** **Kai** owner. **Scout** witness (numbers independently re-run).
**Tracked by:** Session 44 plan, Story 104. Follows Story 068 (mechanic), Story 071 (probe shape), Story 074 (decision plus gate), Story 089 (mouse leg), Story 091 (playable echo-rounds slice, Session 40 green), Story 097 (mapping layer with keyboard fallback, shipped v0.36.0).
**Depends on:** `dev/fps-probe/` Session 42 state: `input-mapping-layer-097.js` plus `echo-rounds-mapped-097.html` plus `mapping-layer-check-097.js`. No native toolchain.

## Summary

Drive a bounded keyboard-leg slice through the shipped 097 mapping layer: trusted key events (WASD move plus click fire) plus arrow-key look, resolved through the layer's intent resolvers end to end in the harness. Keyboard is the decided FPS input (Session 43 ask closed by silence; session plan section 17). Harness-only diff under `dev/fps-probe/`. No release cut follows (Session 40 precedent). If hours do not remain after Stories 103 and 105, the dev wave defers this story and records the deferral; that is an accepted outcome, not a fail.

## jakebot decision (advisory only, recorded)

Session 44 Wave 1 priorities per jakebot (session local-83c1f398af985ca091b172f0cd089e23eb336f49ed36e42a457088eab9b9f544, proceeded on its read): point 2, FPS becomes a bounded P2 only if hours remain, trusted key events plus arrow-key look through the 097 mapping layer, probe dir only; point 4, do not re-ask the keyboard question, Session 43 attached a default and a deadline and silence already decided it.

**Citation:** `flambeee-team/session-plan.md`, Session 44 (2026-10-28), section "jakebot decisions (advisory only, recorded)".

## Decided input (binding on this story)

Keyboard is the decided FPS input. The Session 43 ask to Jake carried a default (keyboard-only) and a deadline; silence accepted it. This story proves the keyboard leg and records nothing else as input. No acceptance criterion in this story names any other input device.

## Source: Story 097 probe state (quoted verbatim where reused)

Story 097 as shipped (roadmap v0.36.0 entry, Session 42 green), carried forward verbatim as the base this slice stands on:

> RED run exit 1 on pre-change tree; green exit 0 twice on Chromium headless 1280x800 DPR 1x: 691 counted frames, p95 16.7 in band, 0 slow, 301/301 look, 17/17 click-pulse-fade, lit 1 rate 1 unlit 0, 17/17 reveals, WIN.

The keyboard-leg slice must preserve these numbers within run jitter: the slice is reused, not rebuilt. A layer run that regresses the slice (look events dropped, pulse-fade broken, lit gate inverted) is a fail, not a new baseline.

## Requirements

### 1. RED run first

Before the keyboard-leg code exists, dev records one failing run: a harness asserting trusted key-event move plus arrow-key look resolve through the 097 layer to the slice, against the pre-change tree. It fails (no keyboard leg exists), and that failing run with command, exit code, and output pasted into the dev record is the proof the green run measures new code. Code with no RED run is not done.

### 2. Scope (dev/fps-probe only, keyboard leg plus harness proof)

- Trusted key events: WASD move plus click fire, driven through the 097 intent resolvers end to end in the harness at 1280x800 DPR 1x.
- Arrow-key look: arrow keys resolve to look intent through the same layer, alongside the proven Pointer Lock look path; both paths recorded with counts.
- Frame numbers recorded with the Story 074 settlement: warmup first 30 frames excluded, frame count at least 600, p95 checked against the 15.84ms to 17.50ms band, slow frames over 33ms reported. Numbers, not adjectives.
- New or changed files under `dev/fps-probe/` ONLY. Zero new lines in `src/`, `website/`, or `share/`. No game ships.
- No native toolchain, no dependency, no build step.

### 3. Scout witness

Scout independently re-runs the keyboard-leg harness on the merged tree and records matching values (pass/fail per check plus frame counts plus round outcome), same as the Story 091 two-run shape (RED pre-change exit non-zero, green merged exit 0).

### 4. No sprawl

No second room, no second enemy type, no weapon roster, no score persistence, no menus beyond the existing win/lose, no native toolchain, no dependency, no build step. Anything beyond key-event move plus arrow-key look plus the harness proof is a full build and waits.

### 5. Deferral rule

The dev wave runs this story only if hours remain after Stories 103 and 105. If deferred, the dev record states "Story 104: deferred, hours did not remain" and stops. Deferral is recorded, not failed, and carries to the next session plan.

## BDD scenarios

**Scenario 1: RED run fails first.**
Given the pre-change tree, when the keyboard-leg harness runs, then it exits non-zero (no keyboard leg exists) and the run is recorded as the artifact.

**Scenario 2: Trusted key events proven through the layer.**
Given the merged harness at 1280x800 DPR 1x, when WASD move plus click fire are driven through the 097 mapping layer, then move and fire intents resolve to the slice inputs, targets clear only through lit-state hits, and the round reaches a win or lose screen with no build step.

**Scenario 3: Arrow-key look proven through the layer.**
Given the merged harness, when arrow keys are driven through the layer, then look intent resolves per key press with counts recorded, alongside the Pointer Lock look path, with zero drops or desync; any drop is recorded as a fail.

**Scenario 4: Story 097 numbers preserved.**
Given the Story 097 slice reused under the layer, when the keyboard-leg run completes, then look events apply, click-pulse-fade holds, lit hits count at rate 1 with unlit at 0, and shooter reveal records per shot, within run jitter of the quoted numbers; a regression is a fail, not a new baseline.

**Scenario 5: Frame numbers in band.**
Given at least 600 frames with the first 30 excluded, when p95 is computed, then it falls inside 15.84ms to 17.50ms with slow frames over 33ms reported, or the miss is recorded as a finding, not rounded away.

**Scenario 6: Harness-only diff, no release.**
Given the story diff, when it is inspected, then every new or changed file sits under `dev/fps-probe/`, zero lines change under `src/`, `website/`, or `share/`, and no version cut follows (Session 40 precedent).

**Scenario 7: Deferral accepted.**
Given the dev wave clock, when hours do not remain after Stories 103 and 105, then the dev record states the deferral line from requirement 5 with no harness run required and no fail recorded.

## Acceptance Criteria

**AC-1.** RED run recorded with command, exit code, and output showing the missing keyboard leg (Scenario 1).
**AC-2.** Trusted key-event path proven through the layer, green exit 0 on the merged tree at 1280x800 DPR 1x with a win or lose screen reached (Scenario 2).
**AC-3.** Arrow-key look proven through the layer with counts recorded, zero drops, or the fail recorded plainly (Scenario 3).
**AC-4.** Story 097 numbers preserved within run jitter (Scenario 4).
**AC-5.** Frame numbers recorded with warmup, frame count, band check, and slow-frame count stated (Scenario 5).
**AC-6.** Scout independent re-run with matching values recorded (section 3).
**AC-7.** Harness-only diff, no native toolchain, no dependency, no version cut (Scenario 6).
**AC-8.** Deferral path recorded if taken: the requirement-5 line with no fail (Scenario 7).
**AC-9.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

RED command plus exit code plus output; green command plus exit code twice; frame counts plus p95 plus slow-frame count per run; key-to-intent resolution table (WASD/arrows/click to intent) with counts; Story 097 regression comparison (look, pulse-fade, lit/unlit, shooter reveal, outcome); deferral line if taken. Numbers, not adjectives.

## Non-Goals

- Any second room, second enemy type, roster, persistence, or menu beyond the existing win/lose.
- Any `src/` game file, website change, release cut, or schedule change.
- Any native toolchain, engine choice, or parallel native plan.
- Touching `pending-post.txt` or any noon pipeline path.
