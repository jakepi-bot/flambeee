# Story 006 — Simon Difficulty Levels

**Status:** Ready for development (v0.5.0)
**Author:** Ember (PM) + Quinn (BA)
**Priority:** Medium

## Summary

Minesweeper has three difficulties, 2048 has board size selection, but Simon is one-speed. This story adds Easy/Classic/Hard difficulty to Simon, completing the difficulty rollout across all games.

## User Story

As a player,
I want to choose a difficulty for Simon,
So that I can play at a pace that suits me.

## Acceptance Criteria (BDD)

### Scenario 1: Difficulty selector is visible
Given I open Simon,
When the game loads,
Then I see Easy, Classic, and Hard difficulty buttons.

### Scenario 2: Easy mode is slower
Given I select Easy,
When the sequence plays,
Then the flash and gap durations are longer than Classic.

### Scenario 3: Hard mode is faster
Given I select Hard,
When the sequence plays,
Then the flash and gap durations are shorter than Classic.

### Scenario 4: Difficulty persists
Given I select a difficulty,
When I reload the page,
Then my selection is remembered.

### Scenario 5: Changing difficulty starts a fresh game
Given a game is in progress,
When I change the difficulty,
Then the game resets to a new sequence.

### Scenario 6: Best score is per difficulty
Given I have a best score on Classic,
When I play on Hard,
Then Hard tracks its own best score.

## Notes for Developers

- Difficulty presets (flash duration / gap duration at round 1, and per-round speed-up):
  - Easy: flash 800ms, gap 300ms, speed-up 20ms/round (floor 350ms flash, 120ms gap)
  - Classic: current behavior (600ms flash, 200ms gap, 30ms/round, floor 200ms/80ms)
  - Hard: flash 450ms, gap 150ms, speed-up 40ms/round (floor 120ms/50ms)
- Storage: `flambeee-simon-difficulty` key; best scores per difficulty under `flambeee-simon-best-<difficulty>` (keep `flambeee-simon-best` as the Classic value for backward compatibility).
- All localStorage access wrapped in try/catch.
