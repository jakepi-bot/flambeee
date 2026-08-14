# Story 009 — Wordfire color legend / how-to

**Status:** Ready for development (v0.7.0)
**Author:** Ember (PM) + Quinn (BA), 2026-08-14
**Priority:** P1 (community feedback, issue #26)
**Reporter feedback:** jakepi84 via issue #26 — "the colors are not intuitive. I am not sure what the colors during game play mean. Maybe some instructions on the front page under 'Play our Games' would be helpful. Or maybe a key during the game you can bring up with some instructions."

## Background

Wordfire colors tiles green/yellow/gray after each guess, but nothing on the page explains what the colors mean. New players (especially people new to word games) have to guess. Issue #26 explicitly asks for a legend or instructions. A compact, always-visible legend under the board is the lowest-friction fix; it must respect the existing colorblind mode (shape symbols).

## Business value

A game that explains itself in one glance converts first-time players into returning players. The legend is a tiny UI addition that removes a real onboarding stumble, and it directly addresses reported community feedback. Per PMF notes, removing friction from the first play session is a retention play.

## BDD Scenarios

### Scenario 1: Legend is visible during play
- **Given** a player opens Wordfire
- **When** the board is displayed
- **Then** a compact legend is visible showing:
  - Green tile: letter is in the word and in the right spot
  - Yellow tile: letter is in the word but in the wrong spot
  - Gray tile: letter is not in the word

### Scenario 2: Legend matches game colors exactly
- **Given** a player on the Wordfire page
- **When** they compare the legend swatches to the board/keyboard colors
- **Then** the swatches use the exact same green/yellow/gray values as the game tiles

### Scenario 3: Legend respects colorblind mode
- **Given** a player with colorblind mode enabled
- **When** the legend is displayed
- **Then** the legend swatches also show the shape symbols (✕ / ◇ / ●) matching the tiles

### Scenario 4: Legend does not push the board off-screen
- **Given** a player on a phone (viewport ≤ 420px)
- **When** the page is rendered
- **Then** the board, keyboard, and legend all fit without scrolling the game area unexpectedly

## Acceptance Criteria (summary)

1. Legend present on the Wordfire page, visible during normal play (no clicks required).
2. Legend uses exact game colors; in colorblind mode it also shows shapes.
3. No layout breakage on mobile; legend is compact (one line of three swatches + labels, or equivalent).

## Notes for developers

- The legend should be small and unobtrusive: three colored swatches with short labels (e.g. "In word + right spot", "In word", "Not in word") or the common shorthand.
- Place it between the board and the keyboard, or under the board — test both; must not push the keyboard out of reach.
- Reuse existing CSS variables (--green, --yellow, --gray) so it can never drift from the game colors.
