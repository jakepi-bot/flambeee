# Test Plan: Story 110 Playable Echo-Rounds Game (Session 47)

**Story:** `docs/stories/110-echo-rounds-game-session47.md` (P1, v0.40.0 vehicle, gated on green).
**Owner:** Riven. **QA:** Scout. **PR:** #187, branch `riven/story-110-111-echo-rounds`, base `27d6d43`.
**Artifact:** `website/games/echo-rounds.html` (single file, no build, keyboard-only, ratifies Story 109 Path B).

## Scope
In scope: the one new file `website/games/echo-rounds.html`. Out of scope:
site card, CACHE bump, precache entry, What's New heading (Story 111 owns
those); existing games, apps, GAME_ORDER, schedule, noon, pending-post.txt,
checker scripts, FPS probe, jobs, cron. Any diff there fails this plan.

## Checks (each maps to an AC / BDD scenario)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Riven holds 110+111 in one PR (Sc 1) | `gh pr view` + dev record | Owner named, one PR for both stories |
| 2 | AC-2 | One new no-build file, one room, one target type; WASD move, arrow look, click fire (Sc 2, 3) | Read file; drive with real keydown + click | New file only; moveSteps > 0, lookEvents > 0, shots > 0 |
| 3 | AC-3 | Hit gate: lit hits > 0, unlit hits 0 (Sc 4) | Click lit targets; click unlit target + empty space | litHits >= 4 across WIN leg, unlitHits 0 |
| 4 | AC-4 | Firing exposes player, reveal count recorded (Sc 5) | Fire one shot, read probe | reveals == shots, player red/ring visible |
| 5 | AC-5 | WIN on clear; LOSE on ammo spent; LOSE on timer expiry (Sc 6) | Clear 4 targets; `?ammo=1` one miss; `?time=1` wait | outcome win; lose/ammo; lose/timer |
| 6 | AC-6 | No audio, no menus past start line, no second mechanic | Read file, grep audio/menu/gamepad | One start line only, no audio element |
| 7 | AC-7 | Desktop 1280x800 + mobile 375x667, real input, overflow 0, zero page errors (Sc 7) | Serve + Chromium both viewports | overflow 0 both, page-attributable errors 0 both |
| 8 | AC-8 | No gamepad/controller/pointer-lock claim; keyboard-only stated | grep page + comments + dev record | 0 hits for gamepad/controller/pointer-lock except keyboard-only denial |
| 9 | AC-9 | Diff limited to the one game file for this story | `git diff --name-only` vs base | Only `website/games/echo-rounds.html` on the 110 side |
| 10 | AC-10 | Gate rule recorded (Sc 8) | Dev record + qa-results | Green keeps cut on table, slip means no tag |
| 11 | AC-11 | Copy tone | grep for em dash / heavy emoji | 0 em dashes, no heavy emoji |
| 12 | Neg | Unlit-target clicks score zero | Click a dark target, read counts | shots +1, litHits unchanged, unlitHits 0 |
| 13 | Neg | Empty-space clicks are misses | Click empty room, read counts | shots +1, litHits unchanged, outcome undecided |
| 14 | Edge | Promotion path stated in one line | Dev record | Prototype vs promotion named with reason |

## Result (Scout independent re-run, 2026-10-31)
Driver: own script, own static serve, playwright-core with cached Chromium,
real keydown (WASD/arrows) plus real mouse clicks on both viewports.
Pass/fail counts and full output in `flambeee-team/qa-results.md`.
