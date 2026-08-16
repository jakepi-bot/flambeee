# Story 010 — Wordfire: Shareable Results

**Status:** Ready for development (v0.8.0)
**Author:** Ember (PM) + Quinn (BA)
**Priority:** High

## Why

Word games grow by sharing. Wordle's emoji-grid share is the canonical example: a solved puzzle becomes a compact, spoiler-free summary that players post to their social feeds, and every share is a pull signal (per PMF notes, sharing is the most literal early "pull"). Wordfire currently ends at the overlay with no way to show off a solve. This story adds a one-tap share that works on mobile and desktop, with no PII and no answer spoilers.

## User story

As a Wordfire player,
I want to share my daily solve as a compact, spoiler-free summary,
So that I can show off my streak and invite friends to play.

## Acceptance criteria (BDD scenarios)

### Scenario 1: Share button appears on a daily win
Given I have solved today's daily puzzle,
When the win overlay is shown,
Then a "Share" button is visible on the overlay.

### Scenario 2: Share copies a spoiler-free summary
Given I solved today's daily puzzle in 3 guesses with a 5-day streak,
When I tap Share,
Then the clipboard contains a summary with:
- the game name "Wordfire"
- the guess count (e.g. "3/6")
- the streak (e.g. "streak 5")
- a grid of 6 rows of 5 tiles using only the characters ⬛ 🟨 🟩 (or the colorblind-safe equivalents when colorblind mode is on)
- no letters, no answer word, no date, no PII

### Scenario 3: Share works on mobile
Given I am on a phone browser,
When I tap Share,
Then the summary is copied to the clipboard (using the Web Share API when available, clipboard API with a textarea fallback otherwise),
And a confirmation message "Copied" is shown.

### Scenario 4: Share is not offered on a loss
Given I ran out of guesses on the daily puzzle,
When the loss overlay is shown,
Then no Share button is shown.

### Scenario 5: Share is not offered in practice mode
Given I am playing a practice puzzle,
When I win,
Then no Share button is shown (practice results do not affect streaks and are not share-worthy).

### Scenario 6: Clipboard failure is handled gracefully
Given the clipboard API is unavailable or denied,
When I tap Share,
Then the summary is shown in a small text box for manual copy,
And a message "Copy manually" is shown.

## Notes for developers

- Share text format (daily win, 3 guesses, streak 5, colorblind off):
  ```
  Wordfire 3/6 · streak 5
  ⬛🟨⬛🟩⬛
  ...
  ```
- Colorblind mode on: use the shape characters already used in the game (● ◇ ✕) instead of color squares, so the share stays readable for colorblind players.
- The grid must reflect the actual committed rows (committedRows) with their evaluated colors, padded to 6 rows.
- No answer word, no letters, no date, no PII. Ever.
- Use `navigator.share` (Web Share API) when available, else `navigator.clipboard.writeText`, else textarea + execCommand fallback.
- Keep the single-file philosophy: all in `src/wordfire.html`.
