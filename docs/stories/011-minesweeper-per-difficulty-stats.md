# Story 011 — Minesweeper: Per-Difficulty Stats

**Status:** Ready for development (v0.8.0)
**Author:** Ember (PM) + Quinn (BA)
**Priority:** Medium

## Why

Carried from the v0.5.0 review nits. Minesweeper currently tracks one aggregate best time across all three difficulties, which makes the "best time" stat meaningless: a 40-second Easy clear and a 40-second Hard clear are not the same achievement, and the aggregate hides which difficulty a player is actually good at. Per-difficulty stats make the numbers honest and give players a reason to chase each board.

## User story

As a Minesweeper player,
I want my stats tracked separately for Easy, Medium, and Hard,
So that my best time reflects the difficulty I actually played.

## Acceptance criteria (BDD scenarios)

### Scenario 1: Stats are tracked per difficulty
Given I play a game on Medium,
When the game ends (win or loss),
Then the play is counted under Medium only, not under Easy or Hard.

### Scenario 2: Best time is per difficulty
Given I have a best time of 30s on Easy and 90s on Hard,
When I clear Easy in 25s,
Then the Easy best time updates to 25s,
And the Hard best time stays 90s.

### Scenario 3: Existing players keep their history
Given I have existing aggregate stats from before this change,
When I open the game,
Then my total plays and wins are preserved (migrated into the new structure),
And the old best time is attributed to the difficulty I last played, or dropped if unknown.

### Scenario 4: Hub shows per-difficulty best times
Given I have played all three difficulties,
When I open the Game Hub,
Then the Minesweeper card shows plays, wins, and the best time for each difficulty (e.g. "E 25s · M 90s · H 120s").

### Scenario 5: Difficulty switch does not corrupt stats
Given I am mid-game on Hard,
When I switch to Easy,
Then the Hard game is abandoned without recording a play,
And the Easy game starts with a fresh timer.

## Notes for developers

- New storage shape: `{ plays: {easy: n, medium: n, hard: n}, wins: {easy: n, medium: n, hard: n}, bestTime: {easy: s|null, medium: s|null, hard: s|null} }`.
- Migrate the old flat shape `{ plays, wins, bestTime }` on load: keep plays/wins as-is (attribute to the last-played difficulty if known, else to easy), and drop the ambiguous aggregate bestTime.
- Hub display must stay compact (one line per the existing stats bar style).
- Keep the single-file philosophy: all in `src/minesweeper.html` + hub in `src/index.html`.
