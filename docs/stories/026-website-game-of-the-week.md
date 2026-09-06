# Story 026 — Website: Game of the Week (Session 16, v0.15.0)

**Status:** Ready for development (Session 16, v0.15.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** P1 (brand surface + roadmap Future item; ships after the P0 Cinder quest)
**Assigned to:** Riven (frontend: weekly rotation rule, banner/card, mobile-safe layout). Palette (design review: brand check on the card visuals). Peer review: Kai reviews Riven's change. QA by Scout (real click on the card + mobile viewport check per the Session 14 QA bar).
**Tracked by:** Roadmap Future item "Game of the week rotation"; Session 16 plan Priority 2 (brand-surface directive).

## Summary

flambeee.com's home page currently shows a static grid of the five games. This story makes the surface feel fresh each week without shipping a new game: a small **"Game of the Week"** banner/card on `share/Flambeee/index.html` highlights one of the five games per a deterministic weekly rotation rule (by ISO week), with a relative play link to the featured game (`games/<name>.html`). It is on-brand, causes no layout break on mobile, and degrades gracefully (hidden or unobtrusive) if anything is missing.

The live site lives at the ABSOLUTE path `/home/jake/.openclaw/workspace/share/Flambeee/` (outside the repo). The repo mirror `website/index.html` must stay byte-identical to it (standing practice from v0.12.0/v0.13.1). No new game, no service-worker change, no redesign.

## Business value

- Returning visitors see a rotating highlighted game each week with zero new content shipped, keeping the brand surface fresh and driving repeat play toward a featured title.
- Cheap, deterministic freshness: same rule for everyone, no per-visitor logic, no backend, no write path.
- Complements the retention-first lean: the weekly rhythm mirrors the daily-habit loop, just at a longer cadence.

## User Story

As a returning visitor to flambeee.com,
I want to see which game is featured this week, with a link to play it,
So that the site always has something fresh to highlight and I have a clear recommendation.

## Requirements

1. **Weekly rotation rule.** A small "Game of the Week" banner/card on the home page highlights one of the five games per a deterministic rule keyed to the ISO week (so the same featured game shows for everyone that week, and it changes week to week). All five games (Wordfire, Minesweeper, Simon, 2048, Cinder) must be reachable by the rotation over time.
2. **Featured-game card/banner.** On-brand visual (Palette brand check) that names the game and links relatively to `games/<name>.html`.
3. **Relative play link.** The card links to the featured game's relative path (e.g. `games/cinder.html`), consistent with the existing Play links, so localStorage/stats work on the same origin.
4. **No mobile layout break.** The card renders cleanly on mobile/touch viewports; no horizontal overflow, no broken grid, no new scroll issue. Content scales with the existing responsive layout.
5. **Hidden/graceful handling.** If the featured game reference is missing or invalid, the card degrades gracefully (hidden or unobtrusive), never breaking the rest of the page and never throwing an unhandled error.
6. **Deploy both copies, byte-identical.** The change lands in BOTH `share/Flambeee/index.html` (live, ABSOLUTE path) and the repo mirror `website/index.html`. `cmp` must pass.
7. **What's New / roadmap** unchanged this story; no service-worker or manifest changes.

### Out of scope

- Any new game, redesign, spacing overhaul, or unrelated website layout change.
- Per-visitor or per-user "recommendations" (deterministic weekly rule only).
- Wordfire leaderboards, guess-count stats, multiplayer, community games (all deferred by session plan).

## Acceptance Criteria (BDD)

### Scenario 1: One game is featured per ISO week (P1, Riven)
- **Given** I load flambeee.com in a given ISO week
- **When** the page renders
- **Then** exactly one game is shown as the Game of the Week, and it is the same game for any other visitor that same week

### Scenario 2: The featured game matches the deterministic rule (P1, Riven)
- **Given** the current ISO week
- **When** I compute the rotation rule output and compare it to the rendered featured game
- **Then** they match, and the featured game changes to the rule's next value at the next ISO week boundary (all five games reachable over time)

### Scenario 3: Card links to the featured game (P1, Riven)
- **Given** I see the Game of the Week card
- **When** I click its play link
- **Then** it navigates to the relative `games/<name>.html` of the featured game and the game loads and is playable with its localStorage stats readable (same-origin)

### Scenario 4: Mobile renders without layout break (P1, Riven)
- **Given** I view the site on a mobile/touch viewport
- **When** the Game of the Week card is present
- **Then** the layout has no horizontal overflow or broken grid, the card is fully visible and tappable, and no new scroll/jump issue appears

### Scenario 5: Missing/invalid featured game degrades gracefully (P1, Riven)
- **Given** the featured-game reference or its asset is missing or invalid
- **When** the page loads
- **Then** the card is hidden or rendered unobtrusively, the rest of the site functions normally, and no unhandled error or console break occurs

### Scenario 6: On-brand visuals (P1, Riven + Palette)
- **Given** the Game of the Week card renders
- **When** Palette reviews it against the brand palette (navy `#1a1a2e`, flame `#e94560`) and typography
- **Then** the card is on-brand with the rest of the site, and any external-facing link in it is a real clickable link (not bare text), per the Palette UX directive

## Technical notes (Quinn)

- **Live site:** `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE path; `share/` is outside the repo). **Repo mirror:** `website/index.html` in this repo, kept byte-identical (verify with `cmp`). If the repo mirror is present it gets the same change; if not, only the live file changes in the dev wave.
- **Weekly seed:** use the ISO week number (four-digit year + week, e.g. `2026-W37`) from the current UTC date as the deterministic input to the rotation, so everyone sees the same featured game that week and it changes at the Monday boundary. Compute client-side; no server, no persistence.
- **Placement:** as a small banner/card near the top of the home content (see visual description), above or beside the existing game grid, without disturbing the grid or hero layout. Riven confirms the exact spot against the live DOM.
- **Game pool:** all five games listed by their canonical slug (`wordfire`, `minesweeper`, `minesweeper`, `simon`, `2048`, `cinder`) pointing to existing `games/*.html` files. Verify each named game page exists before relying on the rule.
- **QA bar (Session 14):** real browser click on the card to the featured game is mandatory; mobile render checked on a narrow viewport, not just claimed.
- **Accessibility:** card text readable, link clearly a link, sufficient contrast. No on-brand change that harms readability.
- **Tone:** no AI tells in any external copy (plain punctuation, no em dashes, no heavy emoji).

## Visual Description (Quinn)

A compact banner/card at the top of the games section, visually distinct from the grid cards so it reads as a highlight:

- **Placement:** directly above the "Pick your poison" game grid (or in a narrow banner slot between the hero and the grid), full container width on desktop, stacking cleanly with the grid below.
- **Content:** a small "Game of the Week" eyebrow label (uppercase, letter-spaced, muted), the featured game's name in the brand heading weight, a one-line description (reuse the existing game-card description text), and a prominent primary Play button (`games/<name>.html`) styled with the existing flame-gradient `.btn-primary` (`#e94560` to `#ff5a75`).
- **Brand:** navy `#1a1a2e` background with flame accent; the featured game's screenshot thumbnail can be reused as a leading visual if it stays crisp at card size (Palette confirms).
- **Examples:**
  ```
  ┌────────────────────────────────────────────┐
  │ GAME OF THE WEEK                            │
  │ Cinder — a BBS-style text RPG               │
  │ Fight monsters, bank your gold, level up.   │
  │                        [ Play ]             │
  └────────────────────────────────────────────┘
  ```
- **Mobile:** the banner becomes a full-width stacked card (title, one-line description, full-width Play button), no horizontal scroll, consistent with the existing card-gap and touch-target sizing from v0.7.0.

## Open questions

1. **Banner placement.** Above the grid is recommended. Confirm whether the CEO prefers it as a full-width banner above the "Pick your poison" heading or a narrower strip; Riven will note the choice in the PR.
2. **Use of game screenshot thumbnail.** Whether to include the featured screenshot (4:3 crop) or keep it text-only for the smaller banner. Palette visual check decides; a text-only card still meets the story.
3. **Rotation start alignment.** The rule is deterministic by ISO week; the first featured game and the exact ordering (e.g. alphabetical vs spread) are not specified. Recommend a simple fixed order over the five games so all are shown within five weeks; confirm the starting game with the CEO if a specific opener is preferred.