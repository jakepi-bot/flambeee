# Story 015 — Website Full Games Page

**Status:** Ready for development (Session 10, v0.10.0)
**Author:** Ember + Quinn (+ Palette for wireframe/brand review)
**Priority:** High (primary story this session)
**Assigned to:** Riven (frontend). Kai: no backend needed — static content + localStorage reads. Peer review by Kai.

## Summary

The Flambeee website gains a full games view. Today the hub shows a game card grid: screenshot, name, one-line description, and a Play button. Clicking a card goes straight into the game, so a first-time visitor gets no rules, no detail, and no idea what their own record is before they play.

This story adds a per-game detail view (recommended: a modal/overlay on `index.html`, single-file, no build step) that shows, for each of the four games (Wordfire, Minesweeper, Simon, 2048):

- Game name
- Description (one or two lines)
- Rules / how to play (plain language, accurate to real game behavior)
- Real screenshot of the game in action (reuse the v0.9.0 `assets/game-*.png` captures)
- Stats summary read from localStorage (plays, wins, bests, streak as available per game)
- A link to play the game

This is the natural next step after v0.9.0 landed game-card screenshots, and it sets up future work (leaderboards, rules pages, game-of-week) without building any new product.

## Business value

- Brand surface: a visitor can learn a game and see their own record before committing to a click
- Conversion: rules reduce the "I don't know how to play" bounce on first visit
- Retention: visible personal stats reward returning players (consistent with v0.5.0 stats and v0.8.0/v0.9.0 retention plays)
- Foundation for leaderboards, rules pages, and game-of-week (roadmap candidates)

## Requirements

1. From the hub, each game card opens the detail view for that game (recommended: modal overlay on `index.html`; a dedicated section is an acceptable alternative — CEO/dev decision, see Open Questions).
2. The detail view shows, per game: name, description, rules/how-to-play, real screenshot, stats summary from localStorage, and a Play link.
3. Rules text is plain-language, accurate to how the game actually behaves, on-brand tone, no AI tells (no em dashes, minimal emoji).
4. Screenshots are the real in-play captures from v0.9.0 (`assets/game-wordfire.png`, `game-minesweeper.png`, `game-simon.png`, `game-2048.png`), each with descriptive alt text.
5. Stats read the same localStorage keys the games write. Empty state (no stats, corrupt data, or private mode) renders a friendly message, never zeros or a crash.
6. The Play link uses the same link pattern as the hub cards (see Open Question 3 — htmlpreview vs relative).
7. The detail view is accessible: keyboard-openable, focus managed, Escape closes it, focus returns to the triggering card, mobile-first layout.
8. Everything stays on-brand (existing palette, nav, typography) and no links break.

## Acceptance Criteria (BDD)

### Scenario 1: Opening a game detail view from the hub
- **Given** the website home page is loaded
- **When** I click a game card (e.g. Wordfire)
- **Then** a detail view opens for that game showing its name, description, screenshot, how-to-play rules, a stats summary, and a Play link

### Scenario 2: Rules match the real game
- **Given** the Wordfire detail view is open
- **When** I read the "How to play" section
- **Then** it explains the real mechanics: guess the 5-letter word in 6 tries, green/yellow/gray tile feedback, one UTC-seeded daily word shared by everyone, streak that resets on a missed day, practice mode that does not touch the streak
- **And** the same accuracy applies to Minesweeper (clear grid, number hints, flagging, Easy/Medium/Hard boards, first click safe), Simon (repeat the sequence, difficulty levels), and 2048 (merge tiles, reach 2048, arrow/WASD/swipe, 4x4/5x5)

### Scenario 3: Stats summary comes from localStorage
- **Given** I have played games on this device and origin (stats exist in localStorage)
- **When** the detail view opens
- **Then** it shows the stats the game actually records, using the real keys and shapes:
  - Wordfire: plays and wins from `flambeee-stats-wordfire`, current streak from `flambeee-wordfire-streak`
  - Minesweeper: total plays/wins plus best times per difficulty (Easy/Medium/Hard) from `flambeee-stats-minesweeper`
  - Simon: plays and wins from `flambeee-stats-simon`, best round from `flambeee-simon-best`
  - 2048: plays and wins from `flambeee-stats-2048`, best score from `flambeee-2048-best`

### Scenario 4: Empty state
- **Given** no stats exist for a game (first visit, cleared storage, or private mode)
- **When** its detail view opens
- **Then** it shows a friendly "no games played yet" message (e.g. "Play your first round to see your stats here") instead of zeros, errors, or a blank box

### Scenario 5: Screenshot is shown with alt text
- **Given** any game detail view is open
- **When** it renders
- **Then** the real screenshot for that game is displayed with a non-empty alt attribute describing it

### Scenario 6: Play link launches the game
- **Given** the detail view is open
- **When** I click the Play link
- **Then** the game opens using the same link behavior as the hub cards, and the detail view closes or is left without blocking the game

### Scenario 7: Close behavior
- **Given** the detail view is open
- **When** I press Escape or click the close control
- **Then** the detail view closes and I am back at the hub with my scroll position preserved

### Scenario 8: Responsive and accessible
- **Given** a phone-width viewport
- **When** I open a game detail view
- **Then** all content fits without horizontal scroll and the Play link is tappable
- **And** with a keyboard, focus moves into the detail view when it opens, Escape closes it, and focus returns to the card that opened it

### Scenario 9: Accuracy and links
- **Given** the page is rendered
- **When** I check every image and link in the detail views
- **Then** all images resolve to existing assets, all links work, and no content contains PII or claims that are not true

## Technical notes (Quinn)

- Source of truth: `src/index.html` (per session plan; see Open Question 1 about the newer live site at `share/Flambeee/index.html`).
- Screenshot assets from v0.9.0 live at `share/Flambeee/assets/game-*.png` (captured via `dev/capture-game-shots.py`, real game HTML, truthful in-play states). If the site is rebuilt in `src/`, copy the assets into the repo (e.g. `src/assets/`) so the page is self-contained.
- localStorage access must be private-mode safe (`try/catch`), matching the pattern already used in the games and hub.
- Minesweeper stats may be in the legacy flat shape `{plays, wins, bestTime}` if the player has not played since v0.8.0 migration, or the per-difficulty shape `{plays:{}, wins:{}, bestTime:{}}`. Handle both defensively (the hub's `renderMinesweeper` already does this; mirror it).
- Modal overlay keeps the single-file philosophy (one HTML file, no build step, no dependencies). Focus trap + Escape close + `role="dialog"`/`aria-modal` for accessibility.
- No changes to any game file. This touches only the website source.

## Rules content draft (Quinn, to be reviewed by Riven for accuracy)

- **Wordfire:** One word a day, the same word for everyone, reset at UTC midnight. You get 6 tries to guess the 5-letter word. Green means right letter in the right spot, yellow means right letter in the wrong spot, gray means not in the word. Solve the daily word every day to grow your streak; miss a day and it resets. Practice mode gives you unlimited random puzzles and never touches your streak. Colorblind mode swaps colors for shapes.
- **Minesweeper:** Clear the board without hitting a mine. Numbers tell you how many mines touch that cell. Right-click on desktop (long-press on mobile) to flag a suspected mine. Three board sizes: Easy 9x9, Medium 16x16, Hard 30x16. Your first click is always safe.
- **Simon:** Watch the sequence of lights, then repeat it. Each round adds one more step and the pace picks up. Three difficulties: Easy, Classic, Hard.
- **2048:** Slide tiles to merge matching numbers. Two 2s make a 4, two 4s make an 8, keep going. Reach the 2048 tile to win. Arrows or WASD on desktop, swipe on mobile. Classic 4x4 board or Hard 5x5.

## Wireframe description (Palette)

```
┌──────────────────────────────────────────────┐
│ [X] Wordfire                          [Play] │
├──────────────────────┬───────────────────────┤
│                      │  Description...       │
│  [ game-wordfire.png]│                       │
│  (real screenshot)   │  HOW TO PLAY          │
│                      │  • ...                │
│                      │  • ...                │
│                      │  YOUR RECORD          │
│                      │  12 plays · 8 wins ·  │
│                      │  streak 4             │
└──────────────────────┴───────────────────────┘

Desktop: two columns (screenshot left, content right).
Mobile: stacked, screenshot on top, content below, no horizontal scroll.
Surface: var(--surface), 1px var(--border), radius var(--radius),
close button top-right, Play button accent (#e94560).
```

## Open questions

1. **Website source of truth.** The session plan says the site is `src/index.html`, but the live site (and the newer design with screenshots, What's New, and nav) currently lives at `share/Flambeee/index.html` (outside the repo). Which file is canonical for this story? Recommended: bring the current live design into `src/index.html` in the repo, then build the games view on top. CEO decision needed.
2. **Origin and stats visibility.** Live Play links point to `htmlpreview.github.io`, a different origin than the site. localStorage is per-origin, so stats recorded while playing via htmlpreview will NOT appear on a games page served from flambeee.com (and vice versa). Options: (a) serve games from the same origin as the site, (b) accept per-origin stats and document it, (c) drop the stats summary from this story. CEO/dev decision needed before this can be fully verified.
3. **Play link pattern.** Relative links (`wordfire.html`) work when the site and games are hosted together; absolute htmlpreview links are what the live site uses today. The detail view should follow whatever the hub uses after Question 1/2 are resolved.
4. **Modal vs section.** Recommended modal overlay (single-file, least disruption). A dedicated section on the page is acceptable if the team prefers no overlay.
