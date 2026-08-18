# Story 014 — Website Game Cards with Screenshots

**Status:** Ready for development (Session 9, v0.9.0)
**Author:** Ember + Quinn + Palette
**Priority:** Medium

## Summary

The Flambeee home page (flambeee.com, source `share/Flambeee/index.html`) game cards get a visual upgrade: each of the four games (Wordfire, Minesweeper, Simon, 2048) shows a small screenshot preview of the actual game, replacing the plain emoji icon. This is the first step of the deferred "games page with per-game screenshots" idea and directly serves the CEO guidance (2026-08-14) that the website is a brand surface that must stay current and attractive.

The site remains a static single HTML file with no build step (Jake deploys from this workspace copy via Caddy).

## Business value

- Brand surface: a visual arcade lobby reads as a real product, not a link list
- Conversion: a screenshot of the game tells a player in half a second what they are getting
- Parity with how games are presented on Bluesky (release cards) and in the blog
- Palette owns the screenshots: consistent lighting, brand colors, no clutter

## Requirements

1. Each game card on the home page shows a small screenshot of the game in play (or the board state) above the game name.
2. Screenshots are on-brand: dark navy surface, brand accent colors, clean board state, no personal data.
3. Screenshots are local static assets in `share/Flambeee/assets/` (no external hosting).
4. Cards keep name, description, and Play button; the emoji icon is replaced by the screenshot.
5. Layout stays responsive: screenshots scale on mobile, cards keep equal height.
6. Alt text on each screenshot describes the game for accessibility.

## Acceptance Criteria (BDD)

### Scenario 1: Cards show game screenshots
- **Given** the home page is loaded
- **When** the Games section renders
- **Then** each of the four game cards shows a screenshot image above the game name

### Scenario 2: Screenshots match their game
- **Given** a viewer reads the Wordfire card
- **When** they look at its screenshot
- **Then** it shows the Wordfire board (5-letter rows with colored tiles)
- **And** similarly for Minesweeper (grid with cells), Simon (4 pads), and 2048 (numbered tiles)

### Scenario 3: Assets are local
- **Given** the home page source
- **When** inspecting the img src for each card
- **Then** each src points to a file under `assets/` in the same directory

### Scenario 4: Cards remain responsive
- **Given** a phone-width viewport
- **When** the Games section renders
- **Then** cards stack in one column and screenshots scale down without overflow

### Scenario 5: Accessibility
- **Given** the home page source
- **When** inspecting each game screenshot img
- **Then** each has a non-empty alt attribute describing the game

## Technical notes (Quinn)

- Screenshots captured from the real game HTML via Playwright at a fixed viewport (e.g. 420x560, game board area) so they are truthful to what players see.
- Naming: `assets/game-wordfire.png`, `game-minesweeper.png`, `game-simon.png`, `game-2048.png`.
- The What's New section and all existing links stay unchanged.
- No changes to game code; this touches only the website source.

## Wireframe description (Palette)

```
┌─────────────────────────┐   ┌─────────────────────────┐
│  [wordfire screenshot]  │   │ [minesweeper screenshot]│
│  Wordfire               │   │  Minesweeper            │
│  One word a day...      │   │  Classic mine-hunting.. │
│  [ Play ]               │   │  [ Play ]               │
└─────────────────────────┘   └─────────────────────────┘
┌─────────────────────────┐   ┌─────────────────────────┐
│  [simon screenshot]     │   │  [2048 screenshot]      │
│  Simon                  │   │  2048                   │
│  Memory challenge...    │   │  Merge the tiles...     │
│  [ Play ]               │   │  [ Play ]               │
└─────────────────────────┘   └─────────────────────────┘

Cards: same width/height, screenshot fills top ~55%, rounded corners,
1px border var(--border), hover raises card as today.
```
