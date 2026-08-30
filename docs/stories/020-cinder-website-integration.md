# Story 020 — Cinder: Website Integration (Hub Card + Game Detail Modal)

**Status:** Ready for development (Session 13, v0.13.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** MEDIUM (required for v0.13.0 — build after the game file exists)
**Assigned to:** Riven (frontend/website). Peer review by Kai. QA by Scout.

## Summary

Story 018 + 019 build the Cinder game file. This story puts Cinder on the website: a 5th game card in the grid, an entry in the game detail modal system (`GAMES` object), the "Games shipped" stat updated from 4 to 5, and a What's New entry for v0.13.0. This is a pure website change, following the exact pattern established by Story 015 (games page) and Story 017 (modal stats).

## Business value

- The game is only discoverable if it is on the hub. The card + modal is the standard entry point for every Flambeee game.
- The "Games shipped" stat and What's New section are the visible proof of momentum for the community (and for issue #41's author, who will be pointed at the game).
- Consistent with the v0.10.0 games page pattern: every game card opens a detail view with rules, screenshot, personal stats, and a Play link.

## Requirements

1. **Game card:** Cinder appears as the 5th card in the game grid on the website home page, matching the other cards (title, description, screenshot/placeholder, Play link).
2. **Game detail modal:** Cinder is added to the `GAMES` object so its card opens a detail view with rules, screenshot, and a relative Play link to `games/cinder.html`.
3. **Stats in the modal:** the modal shows the player's Cinder stats from localStorage (e.g. level, gold, wins, deaths) when data exists, with the standard empty state when it does not (never played, private mode, corrupt data).
4. **"Games shipped" stat:** updated from 4 to 5.
5. **What's New:** a v0.13.0 entry announcing Cinder (written by the parent in Wave 4, per the established pattern — Riven does not write the copy, but the section must be ready to receive it).
6. **Screenshot/placeholder:** a game card image for Cinder. A real in-game capture is preferred (Story 014 pattern: Playwright capture of the actual game HTML in a scripted state); a styled placeholder is acceptable if a capture is not feasible this session.
7. **Source of truth:** all changes in `share/Flambeee/index.html` (CEO directive: share/Flambeee is the ONLY website source of truth). The repo mirror `flambeee/website/index.html` must be kept in sync.
8. **No other game's card, modal, stats, or behavior changes.**

## Acceptance Criteria (BDD)

### Scenario 1: Cinder card in the grid
- **Given** the website home page is loaded
- **When** I look at the game grid
- **Then** Cinder appears as the 5th card with a title, description, image, and a Play link, matching the other cards' layout

### Scenario 2: Card opens the detail modal
- **Given** the website home page is loaded
- **When** I click the Cinder card
- **Then** a game detail modal opens with Cinder's rules, screenshot, and a Play link to `games/cinder.html`

### Scenario 3: Modal shows Cinder stats when data exists
- **Given** I have played Cinder on this device (localStorage has Cinder save data)
- **When** I open the Cinder detail modal
- **Then** it shows my Cinder stats (e.g. level, gold, wins, deaths) from the save data

### Scenario 4: Modal empty state
- **Given** I have never played Cinder on this device (or localStorage is unavailable/corrupt, e.g. private mode)
- **When** I open the Cinder detail modal
- **Then** it shows the standard friendly empty-state message and does not crash or show zeros

### Scenario 5: Play link is same-origin
- **Given** the Cinder detail modal is open
- **When** I click Play
- **Then** the game opens at a relative same-origin URL (`games/cinder.html`) so localStorage stats work on flambeee.com

### Scenario 6: Games shipped stat updated
- **Given** the website home page is loaded
- **When** I read the "Games shipped" stat
- **Then** it says 5

### Scenario 7: What's New ready for v0.13.0
- **Given** the website home page is loaded
- **When** I read the What's New section
- **Then** it includes a v0.13.0 entry announcing Cinder (copy supplied by the parent in Wave 4)

### Scenario 8: Other games unaffected
- **Given** the website home page is loaded
- **When** I open the Minesweeper, Simon, 2048, and Wordfire cards and modals
- **Then** each looks and behaves exactly as before this change

## Technical notes (Quinn)

- **Primary file:** `share/Flambeee/index.html` (deployed website, source of truth per CEO directive). **Repo mirror:** `flambeee/website/index.html` must receive the same changes and stay in sync.
- **Do NOT touch** `flambeee/src/index.html` (stale repo hub, not the website) or any other game's files.
- **Game file location:** `share/Flambeee/games/cinder.html` (deployed) + `flambeee/src/cinder.html` (repo copy). The Play link is relative: `games/cinder.html`.
- **GAMES object:** add a `cinder` entry following the existing shape (desc, rules array, getStats, formatStats, screenshot). Follow the Story 017 pattern for labeled stats blocks if Cinder has multiple stat groups.
- **Cinder save key:** `flambeee-cinder-save` (JSON character state, see Story 018). The modal's getStats reads it and returns displayable stats (e.g. level, gold, wins, deaths). All reads wrapped in try/catch; corrupt/absent data falls through to the empty state.
- **Screenshot:** Story 014 pattern — Playwright capture of `cinder.html` in a scripted in-game state (e.g. a combat or town screen), 4:3, alt text. If a capture is not feasible, a styled placeholder consistent with the other cards is acceptable; flag which was used.
- **Accessibility:** the modal already meets the v0.7.0/v0.10.0 baseline (dialog role, focus trap, Escape close, focus return). The Cinder entry must not regress it.
- **What's New copy:** written by the parent in Wave 4 (established pattern from v0.12.0). Riven prepares the section slot; the parent fills the copy.

## Visual Description (Quinn)

- **Card:** identical layout to the other four cards — title "Cinder", a one-line description (e.g. "A BBS-style text RPG. Fight monsters, bank your gold, level up."), the screenshot/placeholder image, and a Play button in the flame accent (#e94560).
- **Modal:** same structure as the other game modals — title, screenshot, "How to play" rules list (plain language, e.g. "Explore the town, fight up to 15 monsters a day in the Wilderness, and bank your gold before you die."), stats block (level, gold, wins, deaths when data exists), and a Play link.
- **What's New:** a v0.13.0 entry in the existing format, announcing Cinder as the fifth game.

## Open questions

1. **Screenshot vs placeholder.** A real in-game capture is preferred (Story 014 pattern). If the game is not in a capturable state when the website work happens, a styled placeholder is acceptable. Riven + Palette to confirm; flag which was used in the PR.
2. **Which stats the modal shows.** The session plan does not specify. Recommendation: level, gold, wins, deaths (the most "character-like" stats). Riven's call within the existing modal layout; CEO sign-off only if it changes the layout.
3. **Card description wording.** Written by Riven in the CEO's voice (direct, dry humor, no AI tells). Ember reviews; Vigil checks compliance.
4. **What's New copy.** Parent writes it in Wave 4. Riven only prepares the slot.
