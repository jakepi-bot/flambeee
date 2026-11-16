# Story 140: Echo Rounds run structure, three rooms with carry-over ammo, run score, summary (Session 63, P0, user-visible)

**Status:** Build-ready (Session 63, 2026-11-16).
**Author:** Quinn (Business Analyst), Wave 1.
**Priority:** P0 (the only build story this session; builds in the 01:55 dev wave).
**Assigned to:** **Riven** (SOLE code owner per Story 048; holds the game file plus both site-rider lines in one PR). Kai peers the PR.
**Base commit:** `504d584` (main, Session 62 merge of #253).
**Design contract:** `flambeee-team/design-handoff.md`, Section J (Rook; the contract wins on rooms, transitions, ammo, score, summary, probe, edge cases, and Plan B).
**Session plan:** `flambeee-team/session-plan.md`, Session 63 (2026-11-16), P0 item plus P1 rider.
**Dependencies:** None. The dev wave branches from main at `504d584` after this half's docs PR merges.

## Context (why this story exists)

Echo Rounds shipped in v0.48.0 as a one-room proof: one dark room, one target type, WIN, dead end. It is the roadmap's number one product per the CEO's 2026-10-15 DM, and the last user-visible change is three days old (v0.50.0 SALTLINE, 2026-11-13; Sessions 61-62 were tooling-only). Three linked rooms with ammo carried across each boundary, a score summed across the run, and a run summary on the end screen turn a demo a visitor cannot fail at into a game a visitor can fail at and retry. That is the whole bet.

## Files (one PR, Riven)

| File | Change | Owner |
|---|---|---|
| `website/games/echo-rounds.html` | Run structure: three-room table (J1), transition state machine (J2), run ammo budget (J3), run clock (J4), score (J5), summary (J7), probe additions (J8). Renderer, projection, clipping, depth sort, pulse gate, and Story 128 target positions for room 1 stay byte-identical unless a new geometry table is required. | Riven |
| `website/index.html` | Line 674 only: `Seven games, one arcade` to `Nine games, one arcade`. Nothing else in the file changes. | Riven |
| `website/sw.js` | Line 21 only: `CACHE_VERSION` 26 to 27. One line. Both edited files are shell precache assets, so the bump is load-bearing. | Riven |

No other file. No new file, no new precache entry, `GAME_ORDER` untouched.

## Functional requirements

### 1. Rooms (contract J1)

- FR-1. Three rooms, 15 targets total. Room 1 First Light: 4 targets at [700,150], [820,320], [660,470], [480,300], start {120,300,0,0} (Story 128, unchanged). Room 2 Crossfire: 5 targets at [700,120], [840,300], [660,480], [480,220], [480,380], start {120,450,0,0}. Room 3 Long Dark: 6 targets at [700,100], [840,180], [840,420], [660,500], [480,300], [300,300], start {840,300,yaw PI,0}. No geometry change in any room: same footprint, walls, renderer constants, projection, clipping, depth sort. Phases deterministic per room-local index, `phase = (bi * 700) % CYCLE_MS`, no RNG.

### 2. State machine (contract J2)

- FR-2. States `TITLE`, `RUN` (carries `roomIndex` 1..3), `TRANSITION` (transient, no player input), `WIN` (terminal), `LOSE` (terminal). `ROOM_CLEAR` is an event, not a state: clearing room 1 or 2 routes to `TRANSITION`, clearing room 3 routes to `WIN`. Start input (click, Space, Enter, pad A) moves TITLE to RUN(1) with a full run reset. `TRANSITION_MS` elapse or skip input (Space, click, pad A) moves TRANSITION to RUN(i+1) with targets rebuilt, boosts zeroed, player placed at the next start. Restart input (R, Space, Enter, click, pad A) from WIN or LOSE performs the identical full reset with no reload.
- FR-3. The run clock does not advance during TRANSITION and resumes on entry to the next room. The player cannot act in TRANSITION.

### 3. Ammo (contract J3)

- FR-4. `RUN_AMMO_BUDGET = 40` shots for the whole run (replaces per-round 16). The `?ammo=` URL override is retained and now overrides the run budget. The only reset is a new run (T1/T6). Transition cost is exactly 0: ammo at room i+1 entry equals ammo at room i exit, asserted by probe. Arithmetic: floor 15, competent expectation 30 (2 per target), budget 40 = 15 + 15 + 10 spare. Per-room competent caps: room 1 <= 8, room 2 <= 10, room 3 <= 12.

### 4. Clock and HUD (contract J4)

- FR-5. One run-level clock, `RUN_MS = 180000` ms (180 s). The `?time=` URL override is retained and now sets run seconds. No per-room clock exists. HUD shows `Time: <run seconds remaining>s` plus `Room: <i>/3`. No per-room timer appears.

### 5. Score (contract J5)

- FR-6. One formula, stated once, summed across the run: `score = HIT_PTS * litHits + ROOM_BONUS * roomsCleared + (outcome == WIN ? AMMO_BONUS * ammoLeft + TIME_BONUS * ceil(secLeft) : 0)`. Defaults: `HIT_PTS = 100`, `ROOM_BONUS = 250`, `AMMO_BONUS = 25`, `TIME_BONUS = 5`. Integers only. Score is non-decreasing within a run. A retry resets score to 0; score never carries across runs. A LOSE keeps earned hit and room points and grants no ammo or time bonus.

### 6. Summary (contract J7)

- FR-7. The end screen renders J7 rows 1-14, every number read from the probe getter named in the contract at render time. No independently maintained display numbers. Accuracy is `litHits / shots`, guarded divide-by-zero, 1 decimal. Per-room rows show room targets and room entry ammo.

### 7. Probe surface (contract J8)

- FR-8. Additive read-only getters on `window.__echo` plus one pure query: `roomIndex`, `roomsTotal` (always 3), `roomsCleared`, `clearedTotal`, `targetsTotal` (always 15), `runScore`, `hitPoints`, `roomBonus`, `ammoBonus` (WIN-only, else 0), `timeBonus` (WIN-only, else 0), `secLeft`, `secUsed` (excludes frozen TRANSITION time), `transitionActive`, `roomEntryAmmo`, and `summary()` returning J7 rows 1-14 in one call. Getters and pure queries only: no setters, no control methods, never read by input, render, timing, or tuning paths.

### 8. Edge cases (contract J9)

- FR-9. Final-shot precedence: a shot that clears the last target of room 1 or 2 with ammo reaching 0 routes to TRANSITION, never LOSE; a clear resolved on the clock-expiry frame wins (TRANSITION for rooms 1-2, WIN for room 3). Pointer lock lost between rooms changes no state: TRANSITION proceeds on its timer, re-click re-locks without touching ammo, score, room, or clock. Pulses die with the old room: T3 rebuilds targets with zero boost, no shot fires inside TRANSITION. Pad A restarts from WIN/LOSE/summary and skips TRANSITION mid-room-break; disconnect mid-run keeps the run on keyboard. `?ammo=` and `?time=` overrides flow through carry, freeze, and summary paths with the probe reporting overridden totals.

### 9. Story 128 invariants preserved

- FR-10. Everything Story 128 proved still holds and the baseline harness still passes 11/11: the light gate (a shot scores only a target lit at fire time, evaluated BEFORE that shot's own pulse boost), reveal-on-fire (`visibleUntil = now + REVEAL_MS` on every shot), exact pinhole projection with pitch as rotation, near-plane clipping, pointer lock acquire/release/re-lock/denied fallback, keyboard-only full win path, structural-only gamepad path (never claimed as hardware-verified), mobile no-overflow with no touch UI added, and the binding public copy rule (no `full controller support` wording anywhere public; the card carries no controller wording at all).

## BDD acceptance criteria

Threshold: 12 of 12 on the PR head. Each Then is observable in the product or via `window.__echo`. Rook design criteria cited where they exist.

- AC-1 (R-AC-1, run progression). Given a new run, when rooms 1 and 2 are cleared, then the run continues through TRANSITION into the next room with `roomsCleared` reading 1 then 2, and WIN appears only after room 3 clears with `roomsCleared` 3.
- AC-2 (R-AC-2, ammo carry). Given room 1 exit with ammo A, when room 2 starts, then `roomEntryAmmo` equals A to the digit; same for room 2 exit to room 3 entry. Any reset at a boundary fails.
- AC-3 (R-AC-3, score sum). Given a lit hit in room 2, when the score is read, then `runScore` equals the room 1 subtotal plus the new hit value per J5; score never decreases inside a run and reads 0 after a retry.
- AC-4 (R-AC-4, summary truth). Given WIN or LOSE, when the summary is read, then every number on screen equals its J7 probe getter to the digit, including `summary()` snapshot agreement on all rows 1-14.
- AC-5 (R-AC-5, last-shot precedence). Given the last target of room 1 cleared by a shot that takes ammo to 0, when the frame resolves, then TRANSITION shows, never LOSE.
- AC-6 (R-AC-6, expiry-frame clear). Given the last target of room 3 cleared on the clock-expiry frame, when the frame resolves, then WIN shows, never LOSE.
- AC-7 (R-AC-7, restart). Given WIN or LOSE showing, when R, Space, Enter, canvas click, or pad A fires, then a full new run starts with ammo 40 (or the `?ammo=` override), score 0, room 1, and clock 180 s (or the `?time=` override).
- AC-8 (R-AC-8, lock across boundary). Given lock held in room 1, when lock is lost across the room 1 to 2 boundary, then the run continues, arrows look, and re-click re-locks without changing ammo, score, or room.
- AC-9 (R-AC-9, pulse isolation). Given TRANSITION entered with a pulse active from the last room-1 shot, when room 2 starts, then no room 2 target carries a boost and no room 2 clear is attributable to a room 1 shot.
- AC-10 (R-AC-10, HUD and freeze). Given any run, when the HUD is read, then it shows run seconds remaining and `Room i/3`; when TRANSITION is active, then the clock value is frozen and resumes on next-room entry. No per-room timer appears.
- AC-11 (Story 128 regression guard). Given the PR head, when the baseline harness runs, then it stays 11/11 exit 0 including the `check09` synthetic pad leg, and the keyboard, win, denied, and mobile legs re-run green with no behavior change.
- AC-12 (site rider and cleanliness). Given the PR head, when the site files and console are checked, then `website/index.html:674` reads `Nine games, one arcade`, `website/sw.js:21` reads `CACHE_VERSION = 27`, desktop 1280x800 and mobile 375x667 show overflow 0, and zero page-attributable console errors appear.

## Acceptance command list (the 01:55 dev wave runs and pastes all of these)

```
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/echo-fps-proof.py
```

Must stay 11/11 exit 0 including `check09` synthetic pad. If it breaks the pad path, stop: that is a regression, not a tradeoff.

New legs added to the harness for room progression, ammo carry, score sum, and summary truth, each with a RED anchor against base `504d584` (run the same leg against the base commit and show it fail, or state precisely why the base cannot express it). The keyboard, win, denied, and mobile legs re-run, not assumed. Viewport readings at desktop 1280x800 and mobile 375x667 with overflow 0. Zero page-attributable console errors.

## Definition of done

- AC-1 through AC-12 recorded pass in the build PR body with live pasted output, 12 of 12.
- The diff holds exactly three files: `website/games/echo-rounds.html`, `website/index.html` (one line), `website/sw.js` (one line). No fourth file.
- Stop conditions (Riven stops and returns to this story): any room transition that resets ammo ships nothing (binding failure per J10, never a tradeoff); any `CACHE_VERSION` value other than 27 on the merged tree; any What's New edit inside the build PR; any persistence, play counter, or best-score key; any public controller claim; any Story 128 light-gate or reveal regression.
- Kai peers the PR. Rook design review runs against Section J after the PR opens; blocking findings gate the release wave. Release wave cuts v0.51.0 by default (user-visible change); What's New names v0.51.0 post-tag in the release commit.

## Cut line (binding, from the 01:28 ruling)

If the wave compresses, the summary screen (J7 rendering) is dropped and rooms plus carry-over plus score ship alone. Minimum shippable end screen in that case is the existing one-line outcome plus three integers read from the same probe counters: rooms x/3, targets n/15, score N. An ammo reset at a room boundary is a failure, never a tradeoff.

## Out of scope

- No persistence, no play counter, no best-score key (#215 stays open and untouched).
- No hardware controller claim anywhere public (card, game page, release title, release notes, announcement). The pad path is structural only; the hardware gate stays OPEN-BLOCKED-ON-HARDWARE.
- No What's New edit by the dev wave. It names v0.51.0 in the release commit, post-tag, per the standing rule.
- No visual redesign. Palette owns visual direction; behavior and readable state only.
- No new game, no new game card, no `GAME_ORDER` change, no Apps, no Cinder edits, no manifest work (#237/#238), no diagnostics rulings (#249/#250, #254/#255), no cadence PRs (#206, #208, #211, #212, #217).

## Open questions

None. Section J binds every open point. The only lever order on a miss is J10: raise `RUN_MS` to 240000 first, then `RUN_AMMO_BUDGET` to 48, never cut targets or flatten the formula.

## References

- `flambeee-team/session-plan.md`, Session 63 (2026-11-16): P0 run structure, P1 rider, jakebot advisory session `local-eac9e724df19220e8e8ef7318de855f071691f8803f8fb00d00ee8e8af88c82` (option A), cut line, falsifying test.
- `flambeee-team/design-handoff.md`, Section J (Rook): rooms table, state machine, ammo economy, clock rule, score formula, tuning table, summary map, probe additions, edge cases, Plan B, R-AC-1 through R-AC-10, balance rationale.
- Story 128 (`docs/stories/128-echo-fps-rebuild-session56.md`): carried invariants in FR-10, public copy rule, degrade precedent.
