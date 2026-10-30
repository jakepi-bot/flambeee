# Story 109: FPS decision record, docs only (Session 46, P2)

**Status:** Ready for development (Session 46, 2026-10-30).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (docs only; rides along, does not justify a cut).
**Assigned to:** **Kai** (docs owner). No witness run required. No shared ownership.
**Tracked by:** Session 46 plan, Story 109. Follows Story 068 (mechanic), Story 071 (probe shape), Story 074 (decision plus gate), Story 089 (mouse leg), Story 091 (playable echo-rounds slice, Session 40 green), Story 097 (mapping layer with keyboard fallback, shipped v0.36.0), Story 104 (FPS keyboard leg, Session 44, NOT DOING per roadmap v0.38.0 entry).
**Depends on:** Nothing code. Reads the Session 46 plan jakebot section and VERDICT.md pointer-lock state. No code dependency on Story 108.

## Summary

Write the FPS input decision record jakebot called for: path A (physical gamepad on the box, closes the 15-session gate) versus path B (state keyboard-only as the shipped web input, reopening 104's NOT DOING under its own clause). Docs only. No probe code, no site edits, no `website/` or `dev/fps-probe/` diff. Rides along with Session 46; a docs-only session does not justify a version cut (Sessions 38/40 precedent).

## jakebot decision (advisory only, recorded)

Session 46 Wave 1 priorities per jakebot (session local-2ffe00df485cab745a80f806f53302872f3f936738fdb6dd20264b0c99fe09bf, proceeded on its read): point 2, no code story this session. A pointer-lock look leg through the 097 layer cannot be live-proven here, so it would be a structural claim dressed as a test. It is plumbing between two already-green parts (089 mouse look, 097 layer), and a seam that cannot be exercised is not worth a session. The FPS is blocked on a decision, not on missing work: path A or path B as stated in the Summary. Until one is stated, every FPS session is a restatement. If FPS must appear, make it a docs-only decision record with the two paths and their costs, no probe code.

**Citation:** `flambeee-team/session-plan.md`, Session 46 (2026-10-30), section "jakebot decisions (advisory only, recorded)".

## Story 104 pointer-lock correction (stated plainly, binding on this story)

Story 104 requirement 2 says "alongside the proven Pointer Lock look path." That claim is false and must not be copied. Pointer lock was never proven: headless runs record a pointerLock "error" on both browsers, and there is no X on the build box (DISPLAY unset, no Xvfb, no xvfb-run, no weston, chromium headless only). This story records the correction verbatim and treats pointer lock as unproven until a headed run proves it.

## Decision paths with costs

**Path A: physical gamepad on the box.**

- What closes: the gamepad gate, OPEN-BLOCKED-ON-HARDWARE for the 16th session running, closes only when a physical gamepad is present on the box and a headed run reads its input.
- Cost: needs Jake to provide hardware plus a headed environment (X or equivalent) on or reachable from the build box. No code can close it. Until hardware lands, every gamepad session is a restatement.
- Outcome if taken: gamepad becomes a proven input path with run numbers, and the FPS input question reopens on evidence.

**Path B: keyboard-only as the shipped web input.**

- What it states: keyboard (WASD move plus click fire plus arrow-key look through the 097 layer) is the shipped web input for the FPS, and Story 104's NOT DOING is reopened under its own clause only if a headed environment later allows a live-proven look leg.
- Cost: concedes pointer-lock look and gamepad stay unproven; the FPS ships keyboard-only on web with that limitation recorded, not implied away. Any future pointer-lock or gamepad claim needs its own live run.
- Outcome if taken: the FPS input question is closed for web until hardware or headed capacity changes, and sessions stop restating it.

The decision record states both paths and recommends one. It does not implement either. The decision itself is owned by the product owner and Jake; this story only writes the record.

## Requirements

### 1. Docs-only diff

New or changed files are docs only (the decision record itself, for example under `docs/`). Zero new lines in `website/`, `dev/fps-probe/`, `src/`, `games/`, `scripts/`, or `share/`. No probe code, no harness, no site edits, no test-plan edits.

### 2. Record contents

The record states: the two paths with their costs as above; the 104 pointer-lock correction verbatim in substance (never proven, headless error, no X on build box); the gamepad gate status OPEN-BLOCKED-ON-HARDWARE, 16th session; the Sessions 38/40 precedent that a docs-only session does not justify a version cut; and one recommendation (A or B) with a one-line reason.

### 3. Scope guard

No `website/` diff. No `dev/fps-probe/` diff. No checker, schedule, noon, pending-post.txt, jobs, jakebot, or cron change. No version cut follows from this story.

## Acceptance checks (verifiable doc assertions, no runs)

**AC-1.** The decision record file exists under `docs/` and is the only functional change in the Story 109 diff.
**AC-2.** The record names path A (physical gamepad, closes the 15-session gate) and path B (keyboard-only as shipped web input) with a cost line for each.
**AC-3.** The record states the 104 pointer-lock correction: never proven, headless error on both browsers, no X on the build box.
**AC-4.** The record states the gamepad gate as OPEN-BLOCKED-ON-HARDWARE, 16th session.
**AC-5.** The record states that a docs-only session does not justify a version cut.
**AC-6.** The record carries exactly one recommendation (A or B) with a one-line reason.
**AC-7.** Diff inspection shows zero changed lines under `website/` and zero changed lines under `dev/fps-probe/`.
**AC-8.** Diff inspection shows zero changed lines under `src/`, `games/`, `scripts/`, and `share/`.
**AC-9.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

The record file path; the recommendation line quoted; the diff file list showing docs-only scope; the `git diff --stat` output pasted into the dev record. Numbers, not adjectives. No harness output is required or accepted as proof for this story.

## Non-Goals

- Any probe code, harness run, RED/green cycle, or frame-number claim.
- Any website, app, card, CACHE, or precache change (Story 108 owns those).
- Any game, schedule, noon, checker, pending-post.txt, jobs, jakebot, or cron change.
- Cutting a version or reopening Story 104 beyond the cited clause.
- Touching `pending-post.txt` or any noon pipeline path.
