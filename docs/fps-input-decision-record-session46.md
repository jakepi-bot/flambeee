# FPS input decision record (Session 46, Story 109)

**Status:** Record only. No implementation. Decision owned by the product owner and Jake.
**Date:** 2026-10-30. **Author of record:** Kai (docs owner).
**Sources:** Story 109 (`docs/stories/109-fps-decision-record-session46.md`); jakebot session local-2ffe00df485cab745a80f806f53302872f3f936738fdb6dd20264b0c99fe09bf, recorded in `flambeee-team/session-plan.md` Session 46; `dev/fps-probe/VERDICT.md` run lines.

## Context

The FPS is blocked on a decision, not on missing work. Proven green parts already exist: Story 089 (mouse look) and Story 097 (mapping layer with keyboard fallback, shipped v0.36.0). The unproven seam between them (a pointer-lock look leg through the 097 layer) cannot be live-proven on this box, so no session should claim it. Until one of the two paths below is stated, every FPS session is a restatement.

## Story 104 pointer-lock correction (binding)

Story 104 requirement 2 says "alongside the proven Pointer Lock look path." That claim is false and must not be copied. Pointer lock was never proven: headless runs record a pointerLock "error" on both browsers (HeadlessChrome and Firefox entries in VERDICT.md), and there is no X on the build box (DISPLAY unset, no Xvfb, no xvfb-run, no weston, chromium headless only). Pointer lock stays unproven until a headed run proves it.

## Path A: physical gamepad on the box

**What it closes:** the gamepad gate, currently OPEN-BLOCKED-ON-HARDWARE for the 16th session running. It closes only when a physical gamepad is present on the box and a headed run reads its input.
**Cost:** needs Jake to provide hardware plus a headed environment (X or equivalent) on or reachable from the build box. No code can close it. Until hardware lands, every gamepad session is a restatement.
**Outcome if taken:** gamepad becomes a proven input path with run numbers, and the FPS input question reopens on evidence.

## Path B: keyboard-only as the shipped web input

**What it states:** keyboard (WASD move plus click fire plus arrow-key look through the 097 layer) is the shipped web input for the FPS. Story 104's NOT DOING is reopened under its own clause only if a headed environment later allows a live-proven look leg.
**Cost:** concedes pointer-lock look and gamepad stay unproven; the FPS ships keyboard-only on web with that limitation recorded, not implied away. Any future pointer-lock or gamepad claim needs its own live run.
**Outcome if taken:** the FPS input question is closed for web until hardware or headed capacity changes, and sessions stop restating it.

## Recommendation

**Recommendation: Path B.** Reason in one line: keyboard through the 097 layer is the only input path already proven by green runs, so stating it as shipped closes the restatement loop without waiting on hardware that has been blocked for 16 sessions.

## Session precedent

This record is docs only and rides along with Session 46. Per the Sessions 38/40 precedent, a docs-only session does not justify a version cut, and no cut follows from this story.
