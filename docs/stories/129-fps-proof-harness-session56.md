# Story 129: FPS proof harness plus physical-gamepad verification protocol (Session 56, P1b, tooling and docs only)

**Status:** Ready for development (Session 56, 2026-11-09).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1b (tooling and docs only; proves Story 128, carries no release bytes).
**Assigned to:** **Kai** (sole owner; `dev/` plus `docs/` only, zero website bytes).
**Base commit:** `d1b085e`.
**Design contract:** `flambeee-team/design-handoff.md`, Story 129 sections 1-6 plus section 7 probe surface (Rook; contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 56 (2026-11-09), priorities item 2, acceptance bar, file ownership, sequencing risk note.
**Dependencies:** Story 128 (Riven) supplies the branch file for the GREEN leg. RED on base has no dependency and runs first.
**Tracked by:** Session 56 plan, Story 129.

## Summary

Prove the Echo Rounds FPS in a real browser and record the hardware gate honestly. Kai ships a Playwright harness that serves the tree on a port-scoped local server, drives real input, prints every check, exits nonzero on any failure, and takes `--target` so it runs against base or a branch file; plus a design-decision doc with the physical-gamepad protocol (enumerate device, simultaneous move/look/fire, deadzone, disconnect/reconnect, restart, pass/fail thresholds, device-string record, and the recorded statement that synthetic `getGamepads` is NOT hardware). Zero website bytes. RED first on base, GREEN on Story 128's branch; if the branch is late, RED-only with a labeled SKIP and Scout runs GREEN in QA.

## Files

| File | Change |
|---|---|
| `dev/echo-fps-proof.py` | New. Playwright harness, stdlib plus the installed venv packages. Port-scoped local server, `--target` flag, prints every check, exits nonzero on failure. |
| `docs/design-decisions/003-fps-input-gate-session56.md` | New. Hardware verification protocol with steps, thresholds, device-string record, and the NOT HARDWARE statement. |

Nothing under `website/`. No game file, no card, no `sw.js`, no precache, no release artifact.

## Functional requirements

### 1. Harness runner

- FR-1. Serves the tree on a port-scoped local server (exact port printed; free-port fallback on collision; fails loudly, never silently tests the wrong tree).
- FR-2. Takes `--target` (base file or branch file path) plus viewport flags (desktop 1280x800 default, mobile 375x667 leg) and an optional seed. No flag changes game constants; `?ammo=` and `?time=` are instruments for specific legs only and are labeled in output.
- FR-3. Drives observed game states with real input: IDLE to RUNNING via Space/Enter/click, LOCKED via trusted click, UNLOCKED via Escape, DENIED via a `requestPointerLock` override that rejects, WIN via a scripted keyboard-only winning round, LOSE via ammo-drain and timer legs, restart via R/A/click.
- FR-4. Gamepad legs use a synthetic `navigator.getGamepads` injected before page scripts. Structural proof only: proves polling and mapping end to end, prints NOT HARDWARE every run.
- FR-5. Prints every check by name with PASS/FAIL, exits nonzero on any failure, prints partial results on exception. RED-only mode exits 0 after recording RED with a labeled SKIP for GREEN when the branch file is absent.

### 2. Checks (ten-point bar plus contract E1-E5)

- FR-6. Projection hygiene: zero NaN/Infinity in any projected coordinate, asserted every frame for 300 frames.
- FR-7. Floor coverage 0.25 to 0.90 at default camera plus horizon line present.
- FR-8. Camera upright through a full pitch sweep (up-vector dot world-up > 0), pitch clamped, yaw wraps.
- FR-9. Yaw-relative movement: W for 1 s at yaw 0 versus yaw PI/2, dominant axis swaps.
- FR-10. Lit gate: scripted unlit shot yields unlitShots +1 and 0 clears; scripted lit shot inside forced boost yields +1 clear (Story 089 behavior).
- FR-11. Pointer lock: acquires on trusted click, releases on Escape, re-locks on click, in-lock look changes yaw. Lock-denied fallback runs with zero page errors.
- FR-12. Keyboard-only winning round with no pad and no mouse.
- FR-13. Synthetic pad: injected axes move the player, right-stick deflects yaw, button 7 fires, re-injecting empty pads mid-round disconnects with no stuck intent. Non-standard mapping fixture asserts no throw plus the status line names it.
- FR-14. Performance: 60 fps headless, p95 frame under 20 ms over counted frames excluding 30 warmup. Mobile 375x667: scrollWidth <= 375, no horizontal overflow, lock denial degrades without throw.
- FR-15. Probe contract: the harness fails loudly if any required `window.__echo` field is missing, never silently defaults.

### 3. Protocol doc (003)

- FR-16. Enumerate-device step with a place to record the device string.
- FR-17. Simultaneous move/look/fire step with pass/fail thresholds.
- FR-18. Deadzone step, disconnect/reconnect step, restart step, each with pass/fail thresholds.
- FR-19. Records the statement that the synthetic run is NOT hardware and the gate stays OPEN-BLOCKED-ON-HARDWARE until a physical pad passes.

## BDD scenarios (observable in the harness and doc)

**Scenario 1: RED on base.** Given the base file at `d1b085e`, when the operator runs the harness with `--target` pointing at base, then it exits nonzero and the log names the failing checks with the command and exit code recorded.

**Scenario 2: GREEN on branch.** Given the Story 128 branch file, when the operator runs the harness with `--target` pointing at it, then every check prints PASS and the exit is 0.

**Scenario 3: Every named check prints.** Given the GREEN run, when the operator reads the log, then the 300-frame NaN check, floor band, horizon line, upright sweep, yaw-relative move, lit gate, lock acquire/release/re-lock, denied fallback, keyboard-only win, synthetic pad move/look/fire plus disconnect, p95 bound, and mobile overflow leg each appear as a named printed line.

**Scenario 4: NOT HARDWARE label.** Given any run with the synthetic pad, when the operator reads the log, then a NOT HARDWARE limitation line appears and no line claims controller support.

**Scenario 5: Mobile leg.** Given the mobile flag at 375x667, when the leg runs, then the log shows the scrollWidth reading at or under 375 with no horizontal overflow and lock denial degrading without a throw.

**Scenario 6: Port-scoped cleanup.** Given a run that starts its own server, when the run ends (pass or fail), then the log shows the exact port used and the server is released, leaving no listener behind.

**Scenario 7: Branch-late SKIP.** Given the branch file absent at GREEN time, when the operator runs the RED-only mode, then RED is recorded, GREEN shows a labeled SKIP, the exit is 0, and Scout runs GREEN in QA.

**Scenario 8: Protocol doc.** Given the 003 protocol doc, when a human with a physical pad follows it, then enumerate, simultaneous move/look/fire, deadzone, disconnect/reconnect, and restart each have pass/fail thresholds and a place to record the device string.

**Scenario 9: No website bytes.** Given the merged diff of this story, when it is inspected, then no file under `website/` changed and the file list is exactly the harness plus the protocol doc.

**Scenario 10: Missing probe fails loudly.** Given a target file without the full `window.__echo` surface, when the harness runs, then it reports the missing field by name and exits nonzero instead of defaulting.

## Acceptance criteria

- AC-1. Harness created at `dev/echo-fps-proof.py`, Playwright, stdlib plus installed venv packages only.
- AC-2. Protocol doc created at `docs/design-decisions/003-fps-input-gate-session56.md` with all five protocol steps, thresholds, device-string record, and the NOT HARDWARE statement.
- AC-3. RED on base `d1b085e` recorded with command, exit code, and failing check names (Scenario 1).
- AC-4. GREEN on the Story 128 branch with every check PASS and exit 0 (Scenario 2), or labeled SKIP with Scout owning GREEN in QA if the branch is late (Scenario 7).
- AC-5. Every named check prints as its own line (Scenario 3).
- AC-6. NOT HARDWARE prints every run with synthetic pad; no controller-support claim anywhere (Scenario 4).
- AC-7. Mobile leg and port-scoped cleanup hold (Scenarios 5, 6).
- AC-8. Zero website bytes (Scenario 9).
- AC-9. Missing probe fields fail loudly (Scenario 10).
- AC-10. Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required proof (RED/GREEN)

RED bundle: exact command with `--target` at base, exit code nonzero, failing check names, first 30 lines of output. GREEN bundle: exact command with `--target` at the branch file, exit 0, full check list with PASS per line, p95 readout, floor-coverage fraction, mobile overflow reading, NOT HARDWARE line quoted. If GREEN is skipped for a late branch, the log shows the labeled SKIP and the QA owner for the GREEN run. Protocol doc reviewed by reading: every step has a threshold and a record line.

## Out of scope

Any file under `website/`, any game logic change, touch controls, `GAME_ORDER`, GOTW, native builds, Apps, Cinder, `src/` archival, release artifacts, `pending-post.txt`, BLOG.md, website What is New. Balance simulation lives in Story 128; this harness reuses deterministic seeding for the win-script leg only.

## Public copy rule (binding)

No `full controller support` in the harness log, the protocol doc, or any output this story produces. The synthetic legs print NOT HARDWARE every run. The protocol doc states the gate stays OPEN-BLOCKED-ON-HARDWARE until a physical pad passes. Pointer lock and keyboard-only claims may repeat the proven wording; nothing here invents a hardware result.

## Risks and degrade path

Risk 1: the Story 128 branch is late (sequencing risk named in the plan). Path: RED-only with labeled SKIP for GREEN; Scout runs GREEN in QA. Never block RED on the branch.
Risk 2: synthetic `movementX` stays 0 under Playwright while locked, so device-level deltas are unmeasurable headless. Path: inject a synthetic MouseEvent for handler math and label the limitation in output.
Risk 3: flaky frame timing on a shared box. Path: p95 over counted frames excluding 30 warmup; a miss prints the distribution instead of rounding, rerun once, then file it.
This story has no product degrade: it is tooling and docs. If the harness cannot go green for tooling reasons, that is reported, never patched by touching `website/`.

## References

- `flambeee-team/session-plan.md`, Session 56 (2026-11-09): priorities item 2, ten-check acceptance bar, file ownership table, sequencing risk note, public copy rule, jakebot advisory session `local-5f3e24ee1bd1ebb6139eea8b3b6a4a904fd70c5987ede1e02278bde839ff886b` (Option A).
- `flambeee-team/design-handoff.md`, Session 56 (Rook): Story 129 sections 1-6, harness thresholds, edge cases, E1-E5 design acceptance, section 7 probe surface, open questions.
