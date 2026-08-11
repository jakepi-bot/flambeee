# Story 007 — Wordfire (Daily Word Game)

**Status:** Ready for development (v0.6.0)
**Author:** Ember (PM) + Quinn (BA)
**Priority:** High

## Summary

Flambeee's fourth game: a daily 5-letter word game. One puzzle per day, same for every player, with a streak counter that gives players a reason to come back tomorrow. Practice mode for unlimited play. Completes the "fourth game" roadmap item and adds a built-in retention loop (daily streak), per the PMF notes.

Game name: **Wordfire**. Brand: navy board, flame-accent letter tiles, dark theme matching the rest of the arcade.

## User Story

As a player,
I want one word puzzle per day with a streak counter and unlimited practice games,
So that I have a daily reason to come back and can sharpen my skills between puzzles.

## Acceptance Criteria (BDD)

### Scenario 1: Daily puzzle loads
Given I open Wordfire,
When the page loads,
Then a 5-letter word puzzle is shown with 6 rows of 5 empty tiles.

### Scenario 2: Same puzzle for everyone each day
Given two players open Wordfire on the same day,
When they play,
Then they get the same puzzle word (seeded by the calendar date).

### Scenario 3: Guess validation
Given I enter a 5-letter word,
When I submit it,
Then the game accepts it if it is a valid word, and shows a shake/error if it is not in the word list.

### Scenario 4: Correct tile coloring
Given I submit a guess,
When the guess is evaluated against the answer,
Then each tile shows the correct state: green if the letter is in the right position, yellow if the letter is in the answer but wrong position, gray if the letter is not in the answer.

### Scenario 5: Duplicate letter handling
Given the answer has a repeated letter (e.g. "eerie"),
When I guess a word that reuses that letter,
Then the tile colors follow standard Wordle duplicate rules: a letter is only colored green/yellow as many times as it appears in the answer.

### Scenario 6: Win detection
Given I guess the answer,
When all 5 tiles are green,
Then the game shows a win, records the number of guesses taken, and stops accepting input.

### Scenario 7: Loss detection
Given I have used 6 guesses without solving,
When the 6th guess is submitted,
Then the game ends and reveals the answer.

### Scenario 8: Daily streak increments on win
Given I solve the daily puzzle,
When the game ends,
Then my current streak increments by 1 and my best streak updates if this beats it.

### Scenario 9: Streak persists across days
Given I solved yesterday's puzzle,
When I open Wordfire the next day,
Then my streak is still there and continues if I solve today's puzzle.

### Scenario 10: Streak does not require solving the same day
Given I solved a puzzle two days ago but skipped yesterday,
When I open Wordfire today,
Then my streak is reset to 0 (a missed day breaks the streak).

### Scenario 11: Practice mode
Given I want unlimited play,
When I click Practice,
Then I get a random puzzle that does not affect my daily streak, and my plays are counted.

### Scenario 12: Practice mode never touches streak
Given I play practice games,
When I win or lose,
Then my daily streak is unchanged, but my games-played stat increments.

### Scenario 13: Stats integration
Given I play Wordfire,
When a game ends (daily or practice),
Then `flambeee-stats-wordfire` counts the play, and wins increment for daily and practice wins.

### Scenario 14: Keyboard support
Given I am playing on a desktop,
When I type letters on the physical keyboard,
Then the on-screen keyboard reflects my input, and Enter submits, Backspace deletes.

### Scenario 15: Mobile support
Given I am playing on a phone,
When I tap on-screen keyboard keys,
Then input works the same as the physical keyboard.

### Scenario 16: Colorblind accessibility
Given I have trouble distinguishing colors,
When I enable colorblind mode,
Then tile states are also shown with shape symbols (circle/diamond/cross) in addition to color.

### Scenario 17: Private mode safe
Given localStorage is unavailable (private mode),
When I play a game,
Then the game still works normally, streaks just do not persist.

### Scenario 18: Brand consistency
Given I open Wordfire,
When I look at the page,
Then it uses the Flambeee brand palette (navy background, flame accent) matching the other games.

## Notes for Developers

- **Word list:** embed a curated list of common 5-letter words in the HTML. Answers: a subset of common words, seeded by date. Practice: random words from the same list.
- **Date seed:** daily puzzle index = floor of (UTC date / 86400000) so all timezones agree. Puzzle word = answers[dayIndex % answers.length].
- **Storage keys:**
  - `flambeee-wordfire-streak` — `{ current: number, best: number, lastSolvedDay: number }`
  - `flambeee-wordfire-daily-<dayIndex>` — solved state for the day (guess count), so reloads do not re-allow solving
  - `flambeee-stats-wordfire` — `{ plays: number, wins: number }` (same shape as other games)
  - `flambeee-wordfire-colorblind` — `"1"` when colorblind mode is on
- **Duplicate letters:** count answer letters, decrement on each match (green first, then yellow), standard Wordle algorithm.
- **Hub card:** add Wordfire card to `src/index.html` with stats line "X plays · Y wins · streak N".
- All localStorage access wrapped in try/catch (private mode must not break gameplay).
- No PII, no network calls. Everything stays in the browser. Single HTML file like the other games.

## Visual Description (Quinn)

Desktop layout (matches existing games):
- Header: "Wordfire" title with flame accent, subtitle "One word a day. Light it up."
- Streak bar under the header: "🔥 3-day streak · best 7" (single flame emoji is on-brand; hidden until a streak exists).
- Board: 6 rows x 5 tiles, centered. Tiles: 62px, 2px border, rounded corners, navy surface with subtle border. Filled states: gray (#3a3a4a), yellow (#f5a623), green (#4caf7d or brand-aligned green), with white lettering.
- On-screen keyboard: 3 rows (QWERTY layout), keys ~34px, dark surface, active state highlights.
- Buttons: "New Daily" (plays today's puzzle), "Practice" (random puzzle). Flame-red accent (#e94560), matching hub play buttons.
- Colorblind toggle: small switch in the corner; when on, tiles show a shape overlay (circle = green, diamond = yellow, cross = gray).
- Message area above the board: feedback ("Not in word list", "Splendid!", "Streak: 4").
- Footer: "Built by Flambeee" link back to the hub, matching other games.
