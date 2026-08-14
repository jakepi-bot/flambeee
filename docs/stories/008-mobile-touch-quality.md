# Story 008 — Mobile Touch Quality Pass (all games)

**Status:** Ready for development (v0.7.0)
**Author:** Ember (PM) + Quinn (BA), 2026-08-14
**Priority:** P0 (CEO directive 2026-08-11 + community issue #26)
**Reporter feedback:** jakepi84 via issue #26 — "touching the keys tends to move the screen around... hitting the same letter in a row is interpreted by the browser as a request to zoom. IE: Type APPLE the double P will cause the browser to zoom in."

## Background

All four games (Minesweeper, Simon, 2048, Wordfire) are played heavily on mobile, but touch ergonomics have not been systematically addressed. iOS Safari ignores `user-scalable=no` and performs double-tap zoom on rapid repeated taps unless `touch-action: manipulation` is set. Wordfire's on-screen keyboard keys are also below comfortable tap-target size on small screens, and the 300ms tap delay is present anywhere `touch-action: manipulation` is missing. 2048 already implements the correct baseline (body `touch-action: manipulation`, board `touch-action: none`, `user-scalable=no`) — this story standardizes that pattern across all pages.

## Business value

Mobile players are the majority of our audience. Input that fights the browser (zoom, scroll-jump, tap delay) reads as broken. A word game where typing APPLE zooms the page is not a word game, it is a frustration simulator. Fixing this is the highest-leverage quality improvement available, and it directly responds to the CEO's directive and issue #26.

## BDD Scenarios

### Scenario 1: Rapid repeated taps never zoom (all games)
- **Given** a player on iOS Safari or any mobile browser
- **When** they tap the same on-screen key or button twice in quick succession (e.g. the double P in APPLE on Wordfire)
- **Then** the browser does NOT zoom in
- **And** both taps register as game input

### Scenario 2: Tapping game controls does not scroll or move the page
- **Given** a player on mobile
- **When** they touch Wordfire keyboard keys, Simon pads, or Minesweeper cells
- **Then** the page does not scroll, jump, or shift

### Scenario 3: No 300ms tap delay on interactive elements
- **Given** a player on a touch device
- **When** they tap any game control
- **Then** the input registers immediately (no perceptible delay)

### Scenario 4: Wordfire keyboard keys are comfortable tap targets
- **Given** a player on a phone (viewport ≤ 420px)
- **When** they use the on-screen keyboard
- **Then** each letter key is at least 36px tall and 32px wide
- **And** Enter/Backspace keys are at least 36px tall with adequate width
- **And** accidental adjacent-key presses are unlikely (adequate gap between keys)

### Scenario 5: Minesweeper touch flagging still works
- **Given** a player on mobile playing Minesweeper
- **When** they long-press a cell (≈400ms)
- **Then** the cell toggles flag without revealing
- **And** a normal quick tap reveals the cell
- **And** flag mode toggle still works as an alternative

### Scenario 6: Simon rapid pad taps register correctly
- **Given** a player on mobile playing Simon
- **When** they tap pads rapidly in sequence (as the game speeds up)
- **Then** every tap registers as a pad input
- **And** no tap is eaten by browser zoom or double-tap handling

### Scenario 7: Swipe games keep their gestures
- **Given** a player on mobile playing 2048
- **When** they swipe on the board
- **Then** the tiles move in the swipe direction
- **And** scrolling the page over the board does not trigger a move

### Scenario 8: Pinch-zoom for accessibility remains available where appropriate
- **Given** a player who needs to zoom for readability
- **When** they pinch on the page outside game controls
- **Then** zoom still works (we do not use `user-scalable=no` to lock out zoom entirely on pages that don't need it)
- **Note:** games with `touch-action: none` boards keep board-area gestures exclusive to the game; page-level pinch zoom remains available.

## Acceptance Criteria (summary)

1. `touch-action: manipulation` applied to body (or equivalent) on all four game pages and the hub.
2. Double-tap zoom cannot be triggered by game controls on any page.
3. Wordfire keyboard keys meet minimum 36px height / 32px width on ≤420px viewports.
4. No regression: Minesweeper long-press flag, 2048 swipe, Simon rapid taps, Wordfire typing all verified on touch.
5. Verified with automated touch-simulation checks where possible (see test plan) and a documented manual test plan for real devices.

## Notes for developers

- iOS Safari ignores `user-scalable=no` (since iOS 10); `touch-action: manipulation` is the robust fix and also removes the 300ms tap delay.
- `touch-action: none` on a board region prevents scrolling when touching the board — use deliberately only where the whole board is a game surface.
- Preserve accessibility: do not blanket-disable zoom where it is not needed (hub page).
