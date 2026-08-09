# Story 005 — Game Stats Tracking

**Status:** Ready for development (v0.5.0)
**Author:** Ember (PM) + Quinn (BA)
**Priority:** High

## Summary

Players want a reason to come back. Right now each game only remembers a single best score. This story adds per-game stats (games played, wins, best time) so players can see their progress and we can watch for retention signals.

## User Story

As a player,
I want to see my stats for each game (games played, wins, best time),
So that I can track my progress and have a reason to come back.

## Acceptance Criteria (BDD)

### Scenario 1: Stats persist across sessions
Given I have played a game at least once,
When I close the browser and come back later,
Then my games-played count is still there.

### Scenario 2: Minesweeper counts a completed game
Given I am playing Minesweeper,
When I win or lose a game,
Then the games-played counter increments by 1.

### Scenario 3: Minesweeper records a win
Given I am playing Minesweeper,
When I clear the board,
Then the win counter increments by 1.

### Scenario 4: Minesweeper records best time
Given I am playing Minesweeper,
When I win a game,
Then my best time is updated if this win was faster than my previous best.

### Scenario 5: Simon counts a completed game
Given I am playing Simon,
When a game ends (wrong pad pressed),
Then the games-played counter increments by 1.

### Scenario 6: Simon records best round
Given I am playing Simon,
When a game ends,
Then my best round is updated if this run beat my previous best.

### Scenario 7: 2048 counts a completed game
Given I am playing 2048,
When the game ends (game over or win),
Then the games-played counter increments by 1.

### Scenario 8: 2048 records a win
Given I am playing 2048,
When I reach the 2048 tile,
Then the win counter increments by 1.

### Scenario 9: Stats survive private mode
Given localStorage is unavailable (private mode),
When I play a game,
Then the game still works normally and no error is shown.

### Scenario 10: Stats display on the game hub
Given I have played games,
When I open the Game Hub,
Then I can see my stats for each game.

## Notes for Developers

- Storage: `localStorage` under a `flambeee-stats` key (single JSON object per game, e.g. `flambeee-stats-minesweeper`).
- Stats shape: `{ plays: number, wins: number, bestTime: number|null }` (bestTime only for Minesweeper; Simon/2048 keep their existing best-score keys).
- All reads/writes wrapped in try/catch (private mode must not break gameplay).
- Hub display: small stats line under each game card, e.g. "12 plays · 3 wins · best 47s".
- No PII, no network calls. Everything stays in the browser.
