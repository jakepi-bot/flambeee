# Story 022 — Repo Presence: Cinder in README + flambeee.com Links (Issue #45)

**Status:** Ready for development (Session 14, v0.13.1)
**Author:** Quinn (Business Analyst)
**Priority:** MEDIUM (after Story 021; same release, README-only)
**Assigned to:** Riven (frontend/docs/website). Peer review by Kai. QA by Scout.
**Tracked by:** GitHub issue #45 "Cinder" (BigFunger, 2026-08-30; public fix-promise reply 2026-08-30 19:00 UTC)

## Summary

The README's game list covers only the four older games (Minesweeper, Simon, 2048, Wordfire). Cinder, shipped in v0.13.0, is not listed. Separately, every Play link in the README still points at stale `htmlpreview.github.io` URLs, while the real games have lived at flambeee.com (`/games/<name>.html`) since v0.10.0 per the CEO's same-origin directive. The README is now wrong in two directions: it hides the newest game and points players at a dead hosting path.

Fix both: add a Cinder section in the same format as the other games, and repoint the Game Hub link and every Play link to flambeee.com.

## Business value

- Issue #45 is a player telling us our storefront is wrong. That is free QA; the fix is cheap and visible.
- Same-origin links mean player stats and saves actually work when they arrive from the README (the reason for the v0.10.0 directive in the first place).
- Together with Story 021, this closes both open community issues in one patch release.

## Requirements

1. **Cinder section in README:** add Cinder to the game list in the same format as the other games: game title, a short description (BBS-style text RPG: fight monsters, bank your gold, level up), a few feature bullets, and a Play link.
2. **Play links point at flambeee.com:** every Play link in the README (all 5 games) points at `https://flambeee.com/games/<name>.html`. Specifically: `minesweeper.html`, `simon.html`, `2048.html`, `wordfire.html` (confirm the exact Wordfire filename on the site when editing), and `cinder.html`.
3. **Game Hub link:** the top-of-README Game Hub link points at `https://flambeee.com` (the hub is the site's games page), not htmlpreview.
4. **No stale htmlpreview URLs remain** anywhere in the README after this change.
5. **Format and tone:** match the existing README structure exactly (section order, heading style, emoji/link pattern of the current file). Copy in the CEO's voice: direct, no filler, dry humor, no AI tells (no em dashes, no heavy emoji).
6. **Scope:** README.md only. Do not touch game files, website files, or any other docs in this story.

### Out of scope (handled elsewhere, do not attempt in this story)

- **Repo About section** (description, homepage URL, topics): GitHub metadata, not a git file. The parent sets it via `gh repo edit` in Wave 4 of the release (homepage `https://flambeee.com`, description naming Cinder among the games). It is covered by Vigil's review with the rest of the release. Riven does not need to do anything for it; it is listed here so nobody thinks it was forgotten.

## Acceptance Criteria (BDD)

### Scenario 1: Cinder is listed
- **Given** I read README.md on the repo main page
- **When** I scan the games list
- **Then** Cinder appears with a description, feature bullets, and a Play link, in the same format as Minesweeper, Simon, 2048, and Wordfire

### Scenario 2: All Play links are same-origin
- **Given** I read README.md
- **When** I check every Play link for all 5 games
- **Then** each points at `https://flambeee.com/games/<name>.html` and each URL loads the correct game

### Scenario 3: Game Hub link updated
- **Given** I read the top of README.md
- **When** I click the Game Hub link
- **Then** it opens `https://flambeee.com`

### Scenario 4: No stale links survive
- **Given** README.md has been edited
- **When** I search the file for `htmlpreview`
- **Then** there are zero matches

### Scenario 5: Format consistency
- **Given** the README games list is rendered
- **When** I compare the Cinder section to the other game sections
- **Then** the heading style, description length, bullet style, and link pattern match, and the game order reads naturally (existing four games, then Cinder as the newest)

### Scenario 6: Tone compliance
- **Given** the new README copy
- **When** Vigil reviews it
- **Then** it reads in the CEO's voice with no AI tells (no em dashes, no heavy emoji) and contains no PII

## Technical notes (Quinn)

- **Verified current state (2026-09-01):** README.md has 4 stale htmlpreview URLs (Game Hub link at line 13; Play links at lines 19, 33, 47, and the Wordfire section) and no Cinder mention.
- **Play link filenames:** the deployed games live at `https://flambeee.com/games/<name>.html`. Confirm each filename against `share/Flambeee/games/` while editing (e.g. whether Wordfire Standard is `wordfire.html`); do not guess.
- **Cinder facts for the description** (from Story 018): BBS-style text RPG, explore the town, fight up to 15 monsters a day in the Wilderness, bank your gold before you die, persistent character with day counter, levels, weapons and armor.
- **This is a docs change.** No code, no website files, no game files. The website itself is governed by Stories 015/020 and is not touched here.

## Visual description

None. README text only. Match the existing section formatting; if the other games use an emoji or image pattern, Cinder's section follows it identically (within the no-heavy-emoji tone rule).

## Open questions

1. **Wordfire Play filename.** Standard vs Hard may share one file or have separate files on the site. Riven confirms against `share/Flambeee/games/` (absolute path; share/ is outside the repo) before writing the link. If the README currently describes both modes in one section, keep it that way and link once.
2. **Cinder description wording.** Riven drafts in the CEO's voice; Ember reviews; Vigil checks tone compliance. Quinn's seed copy is in Technical notes; Riven is free to improve it within tone rules.