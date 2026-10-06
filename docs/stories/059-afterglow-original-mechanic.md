# Story 059: Afterglow — the original mechanic (Session 29, P1, Feature)

**Status:** Ready for development (Session 29, 2026-10-06).
**Author:** Quinn (Business Analyst), Wave 2. Brief from `flambeee-team/session-plan.md`, Session 29.
**Priority:** P1 (the release headline; answers CEO directive 6, originality over imitation).
**Assigned to:**
- **Riven** owns `src/afterglow.html` and the entire site integration surface (hub card on
  `share/Flambeee/index.html` and `flambeee/website/index.html`, the `GAMES` entry, the card
  dispatch chain, the deploy mirror `share/Flambeee/games/afterglow.html`, the screenshot asset,
  the `sw.js` `CACHE_VERSION` bump on both sides).
- **Kai** owns the deterministic seeded generator and the phase machine **as extracted functions
  plus the proof script**, and does **not** edit `src/afterglow.html`.

**Tracked by:** Session 29 plan, Story 059. References the Story 015 (games detail modal) and
Story 020 (Cinder website integration) patterns.

**Ownership is named before dev starts, per `docs/integration-ownership-protocol.md` (Story 048).**
If both devs must touch `src/afterglow.html`, the parent cuts the ownership ranges explicitly and
re-cuts any overlapping branch rather than merging both.

## Summary

Afterglow is a memory-and-motion puzzle built on one rule: **you never act while you can see the
board.** The information window (lit) and the input window (dark) are disjoint by design. You
perceive, then act blind from memory, then see what you did.

This is the release's headline because it answers CEO directive 6 (`CEO-DIRECTIVES.md` section 6,
2026-10-04): do something original, not a knockoff. The directive asked for **one genuinely
original mechanic**, priority 1 on the plan. Afterglow is that mechanic.

## The directive this story serves

Quoted, not paraphrased, from `CEO-DIRECTIVES.md` section 6 (the traceable source):

> Do not get fixated on it being doom. Keep the small web games. You just need to do
> something original and creative for a game instead of knockoffs of other games.
> This should be number 1 on your plan for the next build.

Readings that are wrong and must not leak into stories, PR copy, blog copy or site copy:

- It is **not** "build a Doom-like." Doom was the sender's example, never the requirement.
- It is **not** "replace the small web games." They stay.
- It is **not** satisfied by a reskin. A well-executed clone of an existing game does not meet it.

## Why this is original, stated precisely

Memory mazes and "memorise the grid" puzzles exist. Acting under uncertainty exists. What is **not
shipped as a core loop** is the rule that the information window and the input window are disjoint
by design: perceive, then act with no sight, then see the result. The mechanic is the seam between
those two phases, not the maze.

**Honest risk, recorded not hidden.** This story cannot exhaustively prove no one has ever shipped
a blind-input memory puzzle. The claim that must be true, and is, is that this is a mechanic and
not a clone of our own games or of a named title. If the playtest reads as "memory maze," the fix
is to sharpen the seam (shorter lit window, reveal-only-on-stop), not to add a reskin layer.

## Core loop (the phase machine)

A level is a small grid with walls, hazards and an exit.

1. **Lit phase.** The board is fully visible for a short, shrinking window (start about 2.0s).
   **No input is accepted.**
2. **Dark phase.** The board goes dark. **Input is accepted only now**, moving blind from memory
   of the lit frame. The lit frame is not redrawn. Input outside the window is **ignored, not
   queued.**
3. **Reveal phase.** The board lights for a beat and shows the result: where you ended, what you
   hit. Then the next lit phase begins.

Clear a level by reaching the exit. A hazard resets the **level**, not the run. Move budget per
level is finite, so blind wandering costs you.

## Requirements

### 1. The phase machine (binding)

- Three states: `lit`, `dark`, `reveal`. One state active at a time.
- Input (tap, swipe, key) is accepted **only** in `dark`. In `lit` and `reveal`, input events are
  discarded. They are not buffered and replayed; a key pressed during `lit` does nothing.
- The lit window shrinks with progress: starts about 2.0s and shortens toward a floor as levels
  advance. The floor is a named constant, not a magic number scattered in the file.
- The lit frame is a snapshot. During `dark`, the rendered board does not show current position,
  walls, hazards or exit; it renders the memorised frame or an empty dark field, per Riven's
  chosen presentation (see the dark-phase visual description in the handoff). It is not redrawn
  as the player moves.
- Transitions are on a timer plus the input budget, and must be deterministic given the same
  seed and the same input sequence.

### 2. Grid, walls, hazards, exit, budget

- Levels are a small grid (recommended 7x7 to 11x11). Cells are floor, wall, hazard, exit, or
  the player.
- The player starts at a seeded start cell, away from the exit and not on a hazard.
- A hazard cell resets **the level** on contact: position returns to start, the level's move
  budget resets, the run (levels cleared) persists.
- The exit ends the level and advances to the next.
- **Finite move budget per level.** Each dark-phase move decrements it. Exhausting it without
  reaching the exit resets the level (same as a hazard). The budget value is data per level, not
  hardcoded at the call site.

### 3. Deterministic generation

- Levels are generated from a **seed**. Same seed, same sequence of levels, every run, every
  browser. This is what makes them replayable and testable.
- Levels are **data** (a seeded generator or a data list), not hand-authored one-off HTML.
- The generator is a pure function of the seed and the level index: `generateLevel(seed, index)`
  returns a level object. It reads no global mutable state and writes none. Kai owns this function
  and its proof; Riven calls it from the game file.
- No `Math.random()` on the level path. Any randomness must derive from the seed.

### 4. Input: mobile-first, plus keyboard

- **Mobile-first tap and swipe** during the dark phase. Swipe in a direction moves one or more
  cells (direction-based; exact gesture threshold is Riven's call). Tap is supported as the
  accessibility fallback.
- **Keyboard** for desktop: arrow keys and WASD.
- No double-tap zoom, no tap delay, no page scroll while playing (reuse the v0.7.0 mobile touch
  baseline applied to the other games).
- Input must be ignored, not queued, outside the dark window.

### 5. Local storage (new key, safe on every path)

- A **new** localStorage key, recommended `flambeee-afterglow-stats`. Do not reuse another game's
  key.
- **Empty-state safe.** A first-time visitor sees no zeros. No stat block renders until there is
  real data.
- **Private-mode safe.** Every read and write is wrapped so a blocked or throwing store degrades
  to an in-memory session with no crash and no console error. Reuses the hardened patterns from
  Stories 034, 046 and 057.
- Stats are additive only; the game writes the new key and no other key.

### 6. Site integration surface (Riven, explicit)

All of the following, matching the Story 015 and Story 020 patterns:

- **Hub card** on **both** `share/Flambeee/index.html` and `flambeee/website/index.html`: a 6th
  `.game-card` with title, one-line description, screenshot/alt, and a relative Play link
  (`games/afterglow.html`), matching the other five cards.
- **`GAMES` entry** in the website `index.html` script (the `GAMES` object begins around line 837
  and runs to about line 1250): name, desc, screenshot, screenshotAlt, playLink, rules array,
  `getStats`, `formatStats`. `getStats` reads `flambeee-afterglow-stats`; `formatStats` returns
  `null` on empty data so the modal shows the standard empty-state line, never zeros.
- **Card dispatch chain:** the game-card click handler maps `href === 'games/afterglow.html'` to
  `gameKey = 'afterglow'`, which flows into the modal open path (`openModal(gameKey)` reading
  `GAMES[key]`, the same chain the other five games use; the task brief calls this the
  `openGame` dispatch chain). Without this line the card does nothing.
- **Deploy mirror:** `share/Flambeee/games/afterglow.html`, byte-identical to `src/afterglow.html`
  after the merge, copied **from the committed side** (see the `cmp` rule in Story 061).
- **Screenshot asset:** a screenshot/placeholder following the Story 014 (v0.9.0) capture pattern
  or the Story 020 fallback, referenced from both index copies.
- **Service worker:** add `./games/afterglow.html` to the `PRECACHE_URLS` array in `sw.js` and
  **bump `CACHE_VERSION` on BOTH sides** (`flambeee/website/sw.js` and
  `share/Flambeee/sw.js`, currently `4`). Miss the bump and returning visitors keep the cached
  shell and never see Afterglow.
- **"Games shipped" stat:** update from `5` to `6` on both index copies.
- **What's New:** a `v0.27.0` entry announcing Afterglow, ready to receive the parent's Wave 4
  copy (Story 020 pattern; Riven prepares the slot, the parent writes the copy).

### 7. Single file, no dependencies, on brand

- `src/afterglow.html` is one HTML file with inline CSS and JS. No external libraries, no build
  step, no downloads, no accounts.
- Dark theme native (navy `#1a1a2e`, flame accent `#e94560`), consistent with the other games.
- Copy plain punctuation, no em dashes, no heavy emoji.

## Acceptance Criteria (Given/When/Then)

**AC-1, disjoint windows (the headline).** Given a level in the lit phase, when the player presses
a move key or swipes, then the board position does not change and the input is discarded, not
queued. Given the same level in the dark phase, when the player swipes the same direction, then the
player moves (or is blocked) blind.

**AC-2, no sight in the dark.** Given the dark phase, when the player moves, then the rendered
board does not reveal the current position, the walls, the hazards or the exit relative to the lit
frame.

**AC-3, reveal shows the result.** Given the dark phase ends, when the reveal phase runs, then the
board lights and shows where the player ended and what they hit.

**AC-4, hazard resets the level, not the run.** Given the player contacts a hazard, when the level
resets, then position returns to start and the level's move budget resets, while levels already
cleared in the run persist.

**AC-5, finite budget.** Given a level, when the player exhausts the move budget without reaching
the exit, then the level resets.

**AC-6, deterministic levels.** Given a fixed seed, when `generateLevel(seed, index)` runs twice,
then it returns a deep-equal level object each time; and given the same seed and the same input
sequence, the phase machine reaches the same outcome.

**AC-7, input ignored outside dark.** Given any phase other than dark, when a tap, swipe or key
arrives, then no move is applied.

**AC-8, mobile input.** Given a touch device at 375x667, when the player swipes during the dark
phase, then one move in the swipe's direction is applied, with no page scroll and no double-tap
zoom.

**AC-9, keyboard input.** Given a desktop viewport, when the player presses arrow keys or WASD
during the dark phase, then the corresponding move is applied.

**AC-10, empty state.** Given a fresh browser with no Afterglow data, when the game and its modal
load, then no zeros are shown and no crash occurs.

**AC-11, private-mode safe.** Given a store that throws on read and write, when the game plays a
full level, then nothing crashes and no console error is logged.

**AC-12, stats key isolation.** Given a full session, when the game writes stats, then only
`flambeee-afterglow-stats` is written and every other game's key is byte-identical.

**AC-13, site integration.** Given the live and mirror index copies, when the home page loads,
then Afterglow appears as a 6th card, its card opens the detail modal with rules and stats, the
Play link is relative (`games/afterglow.html`), and "Games shipped" reads `6`.

**AC-14, deploy mirror.** Given the merge, when the mirror is synced, then `cmp
share/Flambeee/games/afterglow.html src/afterglow.html` is exit 0 with equal sha256 on both sides.

**AC-15, cache bump.** Given the shell changed, when `sw.js` is read on both sides, then
`CACHE_VERSION` is `5` on both `website/sw.js` and `share/Flambeee/sw.js`, and both files agree.

**AC-16, no other game changes.** Given the other five games, when the change lands, then their
files, keys and rendered behaviour are byte-identical to pre-059.

## Required Proof

**A script that executes the real extracted generator and phase machine.**

- Run 1 against the **pre-059 tree** (no Afterglow): **exit 1**, because the behaviour does not
  exist.
- Run 2 against the **merged candidate** on main: **exit 0**, all invariants hold.
- Both runs mandatory. A script that passes on both targets proves nothing.

The harness executes the actual extracted functions, not a re-implementation: `generateLevel`
determinism (same seed twice, deep-equal), the phase gate (input ignored outside dark, applied in
dark), hazard and budget resets, and the stats-key isolation check. Quote the numeric output, not
adjectives.

Plus a **real-browser check** (Playwright, real Chromium) of the lit/dark/reveal loop at desktop
1280x800 and mobile 375x667, with real swipes and taps during the dark window.

**A green exit is a claim about the script, not about the product.** The parent reads the diff and
the numbers, not the worker's status line.

## Non-Goals

- The UTC-seeded **daily mode**. That is Story 063, explicitly OPTIONAL and defer-first.
- Any change to Cinder, Wordfire, Minesweeper, Simon or 2048.
- Any behaviour change under Story 058 (unreadable storage). Blocked on a CEO ruling.
- Multiplayer, leaderboards, accounts, or a build step.
- Cinder offline accrual and welcome-back suppression. Both need CEO sign-off.

## Open questions

1. **Grid size and lit-window floor.** Recommended 9x9 with a lit floor of about 0.8s. Riven's
   call within the tested range; the value must be a named constant.
2. **Dark rendering.** Empty dark field versus a dimmed memorised frame. Recommended: a fully dark
   field, because "you act blind" is the mechanic; see the handoff's dark-phase visual
   description. If the playtest reads as a memory maze, sharpen the seam rather than adding a
   visible frame.
3. **Move semantics.** One cell per swipe versus multiple cells until blocked. Recommended: one
   cell per input, so each blind decision is deliberate and the budget is legible.
