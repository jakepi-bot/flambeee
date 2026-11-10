# Story 130: Pointer-lock acquisition view-snap guard (Session 57, P1b, story filed today, no code today)

**Status:** **Filed 2026-11-10, deliberately not built today.** The story exists so the finding cannot evaporate. Build it in the next dev window that is not shipping.
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** **P1b.** Escalates to **P1** on the condition in open question 1.
**Assigned to:** **Riven**, sole owner when built (Story 048 protocol). No other dev touches the file.
**Base commit:** `b918475`. Carrier heads, verify only, never edit: PR #230 `204bb7d` (Story 128), PR #229 `be55a43` (Story 129).
**Design contract:** `flambeee-team/design-handoff.md`, Session 57, Story 130 sections 0-8 (Rook; the contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 57 (2026-11-10), priorities item 3.
**Dependencies:** PR #229 must be merged first so `dev/echo-fps-proof.py` exists on main. The release wave owns that merge.
**Tracked by:** Session 57 plan, Story 130. QA finding **F2**, raised in `qa-results.md` Output 5, RUN B.

## Why this story is not built today

jakebot ruled on 2026-11-10 (session `local-5819f96678a190dc2bebdb5e6fd7fa360eb03f901d29540ff09fcfa53738dd26`, verdict Option C): **do not spend release risk on an unconfirmed headed behavior, but give F2 a story number now.** In its words, a new commit "voids yesterday's evidence - 39/40 harness, Kai's 11/11, Rook's 6/6 restart reproduction - and buys 45 minutes to re-earn all of it before a 02:55 gate. That is the exact shape of yesterday's failure." And on the defect itself: "there is no X server on this box. The 91.7 degree yaw and 62 degree pitch are measurements of headless Chromium, not of the product... Don't spend release risk on an unconfirmed headed behavior."

So: no code ships in this session. v0.48.0 goes out on `204bb7d` unchanged, and F2 gets a permanent home here instead of a shrug. The escalation rule attached to the ruling: **if a physical headed run reproduces the snap, this story becomes P1 for the next non-release dev window with the threshold guard.**

## Summary

Click-to-start can swing the view hard on the first frame after pointer lock, in any browser that dispatches the acquisition warp. This story adds a one-shot threshold guard: on each lock acquisition the next big `mousemove` is dropped instead of applied, so the player starts where the game intends. `GUARD_PX` 200 px, declared beside `MOUSE_SENS`. One file, two new read-only probe fields, no change to sensitivity, no change to any steady-state number.

The guard removes one input artifact. It changes no tuned quantity a player feels: `MOUSE_SENS`, `MOVE_SPEED`, ammo, timer, and cones are all untouched.

## Files

| File | Change |
|---|---|
| `website/games/echo-rounds.html` | The only edit when built. `GUARD_PX` constant beside `MOUSE_SENS` (line 70 at `204bb7d`), guard state, the drop predicate in the `mousemove` listener, disarm on round start and round end, and two read-only getters on `window.__echo`. |

No other file. No new file, no precache entry, no `GAME_ORDER` change.

`dev/echo-fps-proof.py` is **not** edited by this story. Its 11 checks must go green against the guarded file with the harness byte-identical to `be55a43`. If a check fails, the guard is wrong, not the harness.

## Functional requirements

### 1. Guard predicate (normative order inside the `mousemove` listener)

- FR-1. `DROP  <=>  guardArmed AND started AND NOT over AND (abs(mx_px) + abs(my_px) > GUARD_PX)`.
- FR-2. The predicate sits **after** both existing early returns (`if (!started || over) return;` and `if (!mx && !my) return;`) and **before** `inputMode = 'mouse'`, `lookEvents++`, and the yaw/pitch updates.
- FR-3. On drop: `guardArmed = false`, `guardDrops += 1`, return. No look state touched.
- FR-4. On pass-through while armed: `guardArmed = false`, then the unchanged normal math runs.
- FR-5. **Never drops at or below the threshold.** `abs(mx) + abs(my) <= GUARD_PX` applies normally.
- FR-6. **Never drops outside a running round.** The `started && !over` terms are part of the predicate, not just the placement.
- FR-7. **Never more than one drop per acquisition.** The guard disarms on the first evaluated mousemove either way.
- FR-8. Units are the event's own `movementX`/`movementY` in CSS pixels. **No `devicePixelRatio` factor, no canvas CSS-scale factor.** The threshold is device- and size-independent.
- FR-9. Zero-delta `(0,0)` events never consume the guard. A `(0,0)` burst between lock and the warp must not disarm it.

### 2. Arming and resetting

- FR-10. Arm on **every** `pointerlockchange` where `document.pointerLockElement === canvas`: first acquisition and every re-lock. Never arm on a foreign element.
- FR-11. One-shot disarm on the **first evaluated mousemove** after arming. Evaluated means the event passed both existing gates.
- FR-12. Reset to disarmed on round start (`startRound()`, both the IDLE start and the WIN/LOSE restart) and on round end (`over` true, win or either lose reason).
- FR-13. Disarm on unlock to null, on `pointerlockerror`, and on lock denied (a denied lock never armed it).
- FR-14. A `mousemove` while `!started` or `over` returns through the existing gate first and leaves the guard untouched.
- FR-15. Invariant, assertable on every probe read: `guardArmed` implies `locked && started && !over`. Also `guardDrops` never increases by more than 1 per acquisition, and never while `guardArmed` was false.

### 3. Tuning constants

Every constant for this story lives in `website/games/echo-rounds.html`, in the tuning constants block that the Story 128 contract section 3 describes.

| Name | Default | Min | Max | Location |
|---|---|---|---|---|
| `GUARD_PX` | 200 px (L1, `abs(mx)+abs(my)`) | 80 px | 600 px | tuning constants block, declared beside `MOUSE_SENS` (line 70 at `204bb7d`) |

- FR-16. Derived, not tunable: `GUARD_RAD = GUARD_PX * MOUSE_SENS`, 0.5000 rad at default.
- FR-17. **`MOUSE_SENS` stays 0.0025 rad/px and `PITCH_MAX` stays 1.2 rad**, exactly as Story 128 shipped them. The guard does not touch sensitivity.
- FR-18. **No `GUARD_ENABLED` flag.** A disabled guard is an untested path.
- FR-19. `GUARD_PX` may move only along the levers in the contract's E2 and E9, and only with headed evidence: 200 to 300 to 400 to 600 upward for a false-positive problem, or down to 80 for a residual problem.

Threshold priced in radians at `MOUSE_SENS` 0.0025 rad/px:

| `GUARD_PX` | L1 px | combined rad | degrees |
|---|---|---|---|
| 80 (min) | 80 | 0.2000 | 11.46 |
| 200 (default) | 200 | 0.5000 | 28.65 |
| 600 (max) | 600 | 1.5000 | 85.94 |

### 4. Probe surface

- FR-20. Two new **read-only** getters on `window.__echo`: `guardArmed` (bool, true only between a lock acquisition and the first evaluated mousemove) and `guardDrops` (int, cumulative dropped events since page load).
- FR-21. Both are additive. No setter, no control method, nothing else added.
- FR-22. **Authoritative baseline at `204bb7d` is 29 probe keys**, counted by Quinn for this story (the session brief said 28, Rook said 29; 29 is the record). After this story adds the two fields the count is 31. `dev/echo-fps-proof.py` `REQUIRED_PROBE` is a fixed 28-name list checked for presence, so adding keys cannot turn 11/11 into 10/11.

## BDD acceptance criteria (observable through real input plus the `__echo` probe)

None of these is verified by reading source.

**Scenario 1: Start view holds after click-to-start.** Given a fresh load and a trusted click on the canvas at (640,433) that starts the round, when lock acquires, then within 500 ms `abs(delta yaw) < 0.05` rad and `abs(delta pitch) < 0.05` rad against the pre-click reading, `guardDrops` increases by at most 1, and `lookEvents` is 0 for the acquisition. QA records which branch occurred: 1 means the drop did the work, 0 means this browser delivered no warp.

**Scenario 2: A small first move still applies.** Given lock acquired and the guard armed, when a synthetic `mousemove` of `movementX 100, movementY 0` is dispatched, then yaw advances 0.2500 rad within 1 percent, `guardDrops` is unchanged, and `guardArmed` becomes false.

**Scenario 3: Exactly at the threshold applies.** Given armed, when synthetic events `(200,0)` and `(150,50)` are dispatched, both L1 = 200 px, then both apply, `abs(delta yaw)+abs(delta pitch)` is 0.5000 rad for the first, there are no drops, and `guardArmed` is false after the first.

**Scenario 4: One pixel over the threshold drops.** Given armed, when a synthetic `(201,0)` is dispatched, then yaw and pitch are unchanged, `lookEvents` is unchanged, `guardDrops` increases by exactly 1, and `guardArmed` is false.

**Scenario 5: Never two drops in one acquisition.** Given the guard disarmed after Scenario 4, when a synthetic `(1000,0)` is dispatched, then it applies (yaw +2.5000 rad, wrapped) and `guardDrops` is unchanged.

**Scenario 6: Re-lock is a fresh acquisition.** Given a running round with lock released by `document.exitPointerLock()`, when the player clicks the canvas to re-lock, then the round does not restart, `shots` and `ammoLeft` are unchanged, `guardArmed` becomes true for the new acquisition, and at most one event is dropped for it.

**Scenario 7: Keyboard-only and pad-only rounds never arm.** Given a Space start (keyboard only) or a synthetic-pad round, when either round runs to a loss, then `guardArmed` is false on every probe read and `guardDrops` is 0 at the end.

**Scenario 8: Lock denied never arms.** Given `requestPointerLock` rejects under a harness override, when the round runs, then `lockDenied` is true, `guardArmed` false, `guardDrops` 0, arrows look, and there are zero page errors.

**Scenario 9: No stale arm crosses a round boundary.** Given the guard armed at lock and the round ending before any mousemove, when the probe is read on the end screen and again after restart, then `guardArmed` is false in both reads and no event between rounds incremented `guardDrops`.

**Scenario 10: The zero-delta browser class is untouched.** Given lock acquired and `(0,0)` mousemoves delivered first, as in Firefox and Safari, when two `(0,0)` events arrive, then yaw and pitch are unchanged, `lookEvents` is unchanged, `guardArmed` is still true, and the next move at or below 200 px applies.

**Scenario 11: The invariant holds on every read.** Given any probe read during play, when `guardArmed` is true, then `locked` is true, `started` is true, and `over` is false. Zero violations across every run.

**Scenario 12: Headed confirmation.** Given a human in a headed browser following the protocol below, when 5 click-to-start runs complete, then all 5 pass the 0.05 rad bar on both axes with zero page errors, and the outcome does not depend on where the pre-lock cursor sat.

## Required proof

- R1, lock-cycle matrix: 5 lock cycles at 3 viewport sizes, 15 acquisitions. Pass: at most 1 drop per acquisition, each acquisition's `abs(delta yaw)` and `abs(delta pitch)` under 0.05 rad, `guardArmed` false after every unlock, `guardDrops` at most the acquisition count, zero page errors.
- R2, threshold boundary legs, synthetic and labeled: `(200,0)` applies at +0.5000 rad with no drop and disarms; `(150,50)` applies with no drop; `(201,0)` drops with 0 rad change and `lookEvents` unchanged; then `(1000,0)` applies. Pass 4/4.
- R3, invariant sweep over R1, R2, and one full played round: 0 violations.
- R4, existing harness: `python3 dev/echo-fps-proof.py --target website/games/echo-rounds.html` at the built head, with `dev/echo-fps-proof.py` byte-identical to `be55a43`. **Pass: 11/11, exit 0, same 11 check names.** The two legs the guard could break are check-03 (clean-window look math) and check-06 (lock cycle, `dyaw 0.2500`).
- R5, QA suite: `scout56-bdd.py`. **Pass: 39/40, and the only red line is `scout-23c-keyboard-restart-rescue-with-pad-present`** with its stale `hudTime == "2"` expectation left unchanged. Any other line changing state is a regression in this story, not a new finding to absorb.
- R6, inertness: 5 keyboard-only rounds plus 3 synthetic-pad rounds (NOT HARDWARE). Pass: `guardArmed` false on every read, `guardDrops` 0 at the end, `lookEvents` identical to the `204bb7d` build for identical input sequences, delta 0.
- R7, headed confirmation, human, **run before the build to confirm F2 and after the build to accept the fix.** 5 click-to-start runs in a headed browser on a machine with a display, because this box has no X server. Click points, all with L1 offset above `GUARD_PX`: (640,433), (300,150), (100,150), (800,400), (200,60). Record yaw and pitch immediately before the click and again 500 ms after lock. Pass: `abs(delta yaw) < 0.05` rad and `abs(delta pitch) < 0.05` rad on both axes for all 5 runs, zero page or console errors, the game playable immediately after (look, move, fire all respond), and the same verdict with the pre-lock cursor parked top-left and bottom-right, because the pre-lock mouse position must not matter. Interpretation: pre-fix 0/5 means F2 reproduces headed and per jakebot's rule this story becomes P1 for the next non-release dev window; pre-fix 5/5 means F2 is headless-only in the tested browser and the result is recorded without publishing it; post-fix 5/5 closes the story, and any post-fix red run blocks the merge of Story 130 only, never the release. Firefox is worth one pass if available: it is the 0-delta class and should pass with `guardDrops` 0.

Run counts: 15 acquisitions, 4 boundary legs, 8 inert rounds, 1 harness run, 1 QA suite run, 5 headed runs. All deterministic, no seeds. If any leg randomizes its click point, seed = run index and record it in the log.

## Cache version and ownership

- Output is **one file**, `website/games/echo-rounds.html`. Riven is sole owner of it for this story (Story 048 protocol), and holds the file plus any `sw.js` line together in one PR if a bump turns out to apply.
- **No cache bump is needed by this story as scoped.** The page is already in `PRECACHE_URLS` and is already covered by `CACHE_VERSION` 24 once v0.48.0 ships from PR #230.
- If this story ships later than v0.48.0, the then-current version applies, and **the Story 048 bump rule holds**: one owner, file and bump in the same PR, the decision recorded in the PR body either way. Riven records the explicit no-bump or bump decision with its reason against the version number that is current at build time, rather than assuming 24.

## Out of scope

Any second file, `GAME_ORDER`, `PRECACHE_URLS`, the harness `dev/echo-fps-proof.py`, QA's suite, touch controls, `website/index.html`, `website/sw.js` unless a bump is decided, release artifacts, `pending-post.txt`, BLOG.md, website What is New, and all public copy naming F2. Release carriers PR #230 at `204bb7d` and PR #229 at `be55a43` are frozen and are verified, never edited.

## Public copy rule (binding)

Public copy must not name F2. No camera-smoothness claim, no known-issue note about the snap. F2 is an unconfirmed headed behavior, not a publishable fact. Pointer lock, mouse look, pitch, keyboard and mouse, and the light-ammo rule may be claimed. The word controller may not appear.

## Risks and degrade path

Risk 1: the guard eats a legitimate first flick. Accepted and bounded: one event, priced at about 0.5000 rad at the threshold edge, recovered on the very next event. Levers in order: `GUARD_PX` 200 to 300 to 400 to 600, each step also raising the residual, then a 250-500 ms arm window as a new story.

Risk 2: the guard never fires and the snap persists. The residual is bounded by the 0.5000 rad formula. If a headed run still shows a jump with `guardDrops` 0 and a magnitude outside that bound, the guard is not the cause: reopen the story with the trace, do not chase it by raising `GUARD_PX`.

Risk 3: a check in the frozen harness goes red. Path: the guard is wrong, not the harness. Fix the guard. Editing `dev/echo-fps-proof.py` is out of scope for this story and would be a second story with its own owner.

Risk 4: the build slips into a shipping window. Path: it does not go. This story waits for a dev window that is not shipping, by ruling.

## Open questions

1. **Build or hold after a negative headed result.** jakebot's rule makes this P1 only if a physical run reproduces the snap. If R7 passes 5/5 pre-fix, does the team build the guard as insurance or close F2 as environment-specific with the trace attached? Owner: Ember with jakebot. This story's default: written now, built in no window that is shipping, decided after R7. **A headed reproduction raises this story to P1.**
2. **Probe baseline.** Resolved by this story: 29 keys at `204bb7d`, counted by Quinn, 31 after the two additions. The session brief's 28 is superseded.
3. **`version` probe string.** Currently `'128'`. Rook's call: leave it, since nothing reads it. Changing it to track the story would be a harness change too, so decide once for both stories rather than in this one.
4. **`GUARD_PX` default 200, min 80, max 600 is fixed by jakebot's 2026-11-10 ruling.** Only the E2 and E9 levers may move it, and only with headed evidence.

## References

- `flambeee-team/design-handoff.md`, Session 57 (Rook): Story 130 sections 0-8, tuning table, edge cases E1-E13, design acceptance D130-1 through D130-12, verification R1-R7, rejected Plans C and D, open questions.
- `flambeee-team/session-plan.md`, Session 57 (2026-11-10): priorities item 3, public copy rule, jakebot decision record with session `local-5819f96678a190dc2bebdb5e6fd7fa360eb03f901d29540ff09fcfa53738dd26`.
- `docs/stories/128-echo-fps-rebuild-session56.md` and `docs/stories/129-fps-proof-harness-session56.md`: the look math, the tuning block, the probe surface, and the harness this story must not edit.
