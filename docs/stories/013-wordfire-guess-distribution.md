# Story 013 — Wordfire Guess Distribution Stats

**Status:** Ready for development (Session 9, v0.9.0)
**Author:** Ember + Quinn
**Priority:** High

## Summary

Wordfire players can now see how many guesses it takes them to solve the daily puzzle, across all their solved days. A compact distribution panel shows games won in 1 through 6 guesses as a bar list, alongside their overall record: games played, win count, win percentage, current streak, and best streak.

This is the classic daily-word companion to the shareable results shipped in v0.8.0. The share text already advertises "N/6"; now the player's own screen tells the same story for their full history. It is a retention play: a visible, slowly-growing personal record gives a returning player a reason to come back tomorrow.

## Business value

- Retention: gives daily players a personal record that only grows by returning
- Pull signal: distribution growth is a shareable, comparable number (same format as the share text)
- Parity: the format daily-word players already know from Wordle-style games
- No new accounts, no new pages: lives in the existing Wordfire page

## Requirements

1. When a player wins the **daily** puzzle, record the guess count (1-6) in a per-guess tally.
2. Practice-mode wins and losses of any kind are NOT recorded in the distribution.
3. The distribution panel renders as six bars (1 through 6 guesses) with counts and a bar-length scale proportional to the highest count.
4. The panel also shows: games played, wins, win %, current streak, best streak.
5. The panel renders from stored data on load; if no daily wins exist yet, it shows zeroed bars and a neutral empty state (no errors).
6. Storage is a new localStorage key; existing player data (stats, streak, daily solves) is untouched and continues to work.

## Acceptance Criteria (BDD)

### Scenario 1: Daily win records a guess count
- **Given** a player has solved the daily Wordfire in 3 guesses
- **When** the win overlay appears
- **Then** their distribution tally for 3 guesses increases by 1
- **And** the panel's played count increases by 1
- **And** the panel's win count increases by 1

### Scenario 2: Practice wins are not recorded
- **Given** a player wins a practice-mode game
- **When** the win overlay appears
- **Then** the distribution tally is unchanged

### Scenario 3: Losses are not recorded
- **Given** a player loses the daily puzzle
- **When** the loss overlay appears
- **Then** the distribution tally is unchanged
- **And** the played count increases by 1, win count stays the same

### Scenario 4: Panel renders existing distribution
- **Given** a player has solved daily puzzles in 2, 3, 3, and 5 guesses over past days
- **When** the Wordfire page loads
- **Then** the panel shows counts 0, 1, 2, 0, 1, 0 for guesses 1-6 respectively
- **And** bar lengths are proportional to the highest count (count 2 is full width)

### Scenario 5: Empty state is safe
- **Given** a new player with no daily wins
- **When** the Wordfire page loads
- **Then** the panel shows all zero counts without errors
- **And** played/wins show 0

### Scenario 6: Record and streak display
- **Given** a player with 10 plays, 7 wins, current streak 4, best streak 6
- **When** the panel renders
- **Then** it shows "10 played", "7 won", a win percentage of 70%, "4-day streak", and "best 6"

### Scenario 7: Existing data is preserved
- **Given** a player who already has stats and streak data from before this feature
- **When** they load Wordfire
- **Then** their existing stats and streak still render
- **And** their previous daily wins are not retroactively counted in the distribution (only new wins)

## Technical notes (Quinn)

- New localStorage key: `flambeee-wordfire-distribution`, shape `{ guesses: [0,0,0,0,0,0], played: 0, wins: 0 }` (guesses index 0 = 1 guess).
- **Scope refinement (during development):** the distribution tracks DAILY games only. `played`/`wins` count daily plays/wins, not practice. This makes the panel internally consistent with the guess bars (which only count daily wins) and matches the BDD scenarios literally: a practice win leaves the entire panel unchanged. The existing `flambeee-stats-wordfire` key is untouched and keeps counting all modes for the hub display.
- Increment rules: daily win -> played+1, wins+1, guesses[n-1]+1. Daily loss -> played+1 only. Practice games -> no change.
- Panel placement: directly under the streak bar, above the board. Compact horizontal bars, brand colors (green for the bar, accent for labels).
- No migration needed for existing players; distribution starts empty.

## Wireframe description (Quinn)

```
[ Wordfire ]                    [ flame ]  🔥 4-day streak · best 6

  Your record
  10 played · 7 won · 70%

  1 ▓          0
  2 ▓▓        1
  3 ▓▓▓▓▓▓▓▓▓▓  2      <- longest bar = highest count
  4 ▓          0
  5 ▓▓        1
  6 ▓          0

[board]
```
