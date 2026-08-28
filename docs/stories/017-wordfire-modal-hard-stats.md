# Story 017 — Wordfire Modal Shows Hard Mode Stats

**Status:** Ready for development (Session 12, v0.12.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** High (primary story this session)
**Assigned to:** Riven (frontend). Peer review by Kai. QA by Scout.

## Summary

v0.11.0 shipped Wordfire Hard mode: a Standard/Hard toggle, a harder daily word pool, and per-mode stats stored in separate localStorage keys (`flambeee-stats-wordfire-hard`, `flambeee-wordfire-streak-hard`). The website's Wordfire game detail modal was not updated to match. It still reads only the standard keys, so a player who plays Hard mode opens the modal and sees empty stats, or stats that silently ignore their Hard play.

This story updates the Wordfire entry in the website's game data (`GAMES.wordfire`) so the modal shows both Standard and Hard stats, and updates the game card description and rules list to mention Hard mode. It is a pure website change: no game code changes.

## Business value

- Honesty: a player's Hard-mode record is real and should be visible, not hidden. The modal currently implies they have no record.
- Retention: visible per-mode stats reward returning players in both modes (consistent with the v0.5.0 stats and v0.8.0/v0.9.0 retention plays).
- Discovery: the card description and rules list are the first thing a visitor reads. Hard mode is a headline feature of v0.11.0 and the site should say so.
- Consistency: Minesweeper and Simon already surface per-difficulty stats in the modal. Wordfire should match.

## Requirements

1. The Wordfire game detail modal shows Standard stats (plays, wins, streak) exactly as it does today, from the existing keys (`flambeee-stats-wordfire`, `flambeee-wordfire-streak`).
2. The modal also shows Hard stats (plays, wins, streak) from the Hard keys (`flambeee-stats-wordfire-hard`, `flambeee-wordfire-streak-hard`), labeled so the player can tell the two apart (e.g. "Standard: 5 plays, 3 wins, 2 streak | Hard: 2 plays, 1 win, 1 streak").
3. Each mode's stats are shown only when that mode has data. A player who never played Hard sees Standard stats only, no zero-filled Hard block. A player who only played Hard sees Hard stats only.
4. The empty state (no stats in either mode, corrupt data, or private mode) keeps the existing friendly message and never crashes or shows zeros.
5. The Wordfire game card description mentions Hard mode (e.g. "One word a day. Guess the 5-letter word, or flip to Hard mode for a tougher pool.").
6. The Wordfire rules list in the modal mentions Hard mode (e.g. a rule that Hard mode draws from a tougher word pool and keeps its own streak).
7. The change is made in the website source of truth `share/Flambeee/index.html` (CEO directive: share/Flambeee is the ONLY website source of truth), and the repo mirror `website/index.html` is kept in sync.
8. No other game's modal, stats, or behavior changes. No game files change.

## Acceptance Criteria (BDD)

### Scenario 1: Modal shows Standard stats as before
- **Given** I have played Wordfire in Standard mode on this device (stats exist in `flambeee-stats-wordfire` and `flambeee-wordfire-streak`)
- **When** I open the Wordfire game detail modal on the website
- **Then** the modal shows my Standard plays, wins, and current streak, labeled as Standard

### Scenario 2: Modal shows Hard stats
- **Given** I have played Wordfire in Hard mode on this device (stats exist in `flambeee-stats-wordfire-hard` and `flambeee-wordfire-streak-hard`)
- **When** I open the Wordfire game detail modal on the website
- **Then** the modal shows my Hard plays, wins, and current streak, labeled as Hard

### Scenario 3: Modal shows both modes together
- **Given** I have played Wordfire in both Standard and Hard mode on this device
- **When** I open the Wordfire game detail modal on the website
- **Then** the modal shows both a Standard block and a Hard block, each with its own plays, wins, and streak, and the two are clearly labeled so they cannot be confused

### Scenario 4: No zero-filled blocks for unplayed modes
- **Given** I have played Wordfire in only one mode (Standard or Hard) on this device
- **When** I open the Wordfire game detail modal on the website
- **Then** the modal shows stats only for the mode I played, with no zero-value block for the other mode

### Scenario 5: Empty state preserved
- **Given** I have never played Wordfire on this device (or localStorage is unavailable/corrupt, e.g. private mode)
- **When** I open the Wordfire game detail modal on the website
- **Then** the modal shows the existing friendly empty-state message and does not crash or show zeros

### Scenario 6: Card description mentions Hard mode
- **Given** the website home page is loaded
- **When** I read the Wordfire game card description
- **Then** it mentions Hard mode in plain language (e.g. "One word a day. Guess the 5-letter word, or flip to Hard mode for a tougher pool.")

### Scenario 7: Rules list mentions Hard mode
- **Given** the Wordfire game detail modal is open
- **When** I read the "How to play" rules list
- **Then** it includes a rule that explains Hard mode (tougher word pool, separate streak), accurate to how the game actually behaves

### Scenario 8: Other games unaffected
- **Given** the website home page is loaded
- **When** I open the Minesweeper, Simon, and 2048 game detail modals
- **Then** each modal shows the same stats, rules, and behavior as before this change

## Technical notes (Quinn)

- **Primary file:** `share/Flambeee/index.html` (deployed website, source of truth per CEO directive). **Repo mirror:** `website/index.html` in the flambeee repo must receive the same changes and stay in sync (it currently differs from the deployed file only in the What's New section, which lags at v0.10.0).
- **Do NOT touch** `src/index.html` (stale repo hub, not the website, per CEO directive) or any file in `share/Flambeee/games/` or `flambeee/src/` (game code, unchanged this session).
- **Current code** (in `GAMES.wordfire` in index.html):
  - `desc: 'One word a day. Guess the 5-letter word and keep your streak alive.'` (line ~718 in deployed file)
  - `rules: [...]` array of 7 plain-language rules (line ~722)
  - `getStats()` reads `flambeee-stats-wordfire` (JSON `{plays, wins}`) and `flambeee-wordfire-streak` (JSON `{current, best, lastSolvedDay}`), returns `{plays, wins, streak}`
  - `formatStats(s)` returns `[{label:'Plays',...},{label:'Wins',...},{label:'Streak',...}]` or `null` when all zero
- **Hard keys written by the game** (verified in `share/Flambeee/games/wordfire.html`):
  - `flambeee-stats-wordfire-hard` — JSON `{plays, wins}`
  - `flambeee-wordfire-streak-hard` — JSON `{current, best, lastSolvedDay}`
  - `flambeee-wordfire-mode` — string `"standard"` or `"hard"` (mode persistence; not needed for the modal, but confirms the key naming convention)
- **Suggested implementation (Riven's call):** extend `getStats()` to also read the two Hard keys and return both, e.g. `{ standard: {plays, wins, streak}, hard: {plays, wins, streak} }`; extend `formatStats()` to emit a labeled Standard block and a labeled Hard block (only for modes with data), or a single combined line like "Standard: 5 plays, 3 wins, 2 streak | Hard: 2 plays, 1 win, 1 streak". Keep the existing `modal-stats-data` / `modal-stat-item` markup and CSS so the modal layout and accessibility (dialog role, focus trap, Escape close) are untouched.
- **Labeling matters:** the two blocks must be visually and textually distinct (e.g. a "Standard" and "Hard" label on each block, or a "Standard:" / "Hard:" prefix). A player must be able to tell which record is which at a glance.
- **What's New:** the v0.12.0 What's New entry is handled by the parent in Wave 4, not by this story. Do not add it during development.
- **Accessibility:** the modal already meets the v0.7.0/v0.10.0 baseline (dialog role, focus trap, Escape close, focus return). The stats change must not regress any of it. New labels must be real text, not color-only cues.

## Open questions

1. **Presentation format.** Two labeled stat blocks (Standard block, Hard block) vs one combined line ("Standard: ... | Hard: ..."). Recommendation: two labeled blocks, matching the existing `modal-stat-item` layout and scaling cleanly to other games later. Riven + Palette to confirm the visual; CEO sign-off only if it changes the site layout.
2. **What's New wording.** The v0.12.0 entry is written by the parent in Wave 4. No action needed from Riven, but the entry should mention the modal now shows Hard stats.
3. **Repo mirror sync.** `website/index.html` in the repo lags the deployed file (What's New still says v0.10.0). Riven should apply the same changes to both files so the repo mirror stays current. Whether the parent also backfills the v0.11.0 What's New entry into the mirror is a release-time call, not part of this story.
