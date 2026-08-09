# Flambeee Product Roadmap

## Vision

Flambeee builds snackable, instantly-playable web games. No downloads, no signups, no friction. Open source, community-driven, fun first.

## Current State

- **v0.1.0** — Minesweeper (shipped 2026-07-29)
  - 3 difficulty levels (Easy 9x9, Medium 16x16, Hard 30x16)
  - Mobile support (long-press to flag, flag mode toggle)
  - First-click-safe, flood fill, win/lose detection, timer
  - Single-file HTML/CSS/JS, no dependencies

- **v0.2.0** — Game Hub + Simon (shipped 2026-07-31)
  - Game hub launcher at index.html with game cards
  - Simon memory game with 4 pads, Web Audio tones, speed scaling
  - Colorblind accessibility (shape symbols)
  - Keyboard support (QWAS)
  - localStorage best score persistence
  - BDD stories, test plan, roadmap docs added

- **v0.3.0** — 2048 (shipped 2026-08-04)
  - Merge-puzzle, 4x4 classic + 5x5 Hard, arrow/WASD keys, swipe
  - localStorage best score, win/game-over overlays, Game Hub card

- **v0.4.0** — 2048 Polish Pass (shipped 2026-08-07)
  - Brand palette alignment (navy #1a1a2e, flame #e94560) — CEO feedback
  - Mobile scroll fix (issue #12) — touch-action + overscroll-behavior
  - Precise merge animation (only actually-merged tiles pulse)
  - Board size persistence via localStorage
  - Game-over detection fix (no-op moves now trigger it)

## Roadmap

### v0.2.0 — Session 2 (2026-07-31) ✅ Shipped
- **Simon memory game** — classic sequence-repeat with speed scaling, colorblind cues, keyboard support
- **Game hub/launcher** — central arcade lobby, Minesweeper moved to own page
- Peer reviews: Kai caught missing Simon file, Riven caught 4 issues (all fixed)
- 12-case test plan by Scout

### v0.3.0 — Session 3 (2026-08-04) ✅ Shipped
- **2048 game** — merge-puzzle, 4x4 classic + 5x5 Hard, arrow/WASD keys, swipe, localStorage best score, win/game-over overlays
- **Game Hub** — 2048 card added
- Peer review (Kai): 2 non-blocking observations noted for next session (merge animation approximation, difficulty persistence)
- 4/4 core logic assertions passed; 18-case test plan by Scout

### v0.4.0 — Session 4 (2026-08-07) ✅ Shipped
- **2048 polish pass** — brand palette, mobile scroll fix, precise merge animation, size persistence, game-over detection fix
- Community feedback integrated: issue #12 (mobile scroll) closed, CEO brand-palette note addressed
- 22/22 logic checks passed; peer review APPROVE

### v0.5.0 — Session 5 (planned)
- **Game stats tracking** (games played, wins, best times) — retention play per PMF notes: watch for pull signals, give players a reason to come back
- **Simon difficulty levels** — completes the difficulty rollout across all games (Minesweeper has it, 2048 has board size, Simon gets Easy/Classic/Hard)
- Continue community feedback integration

### v0.6.0 — Session 6 (candidate)
- Fourth game (candidates: Snake, Tetris, Wordle-style)
- Game of the week rotation
- Continue community feedback integration

### Future
- Mobile app packaging (PWA)
- Multiplayer games (WebSocket-based)
- Game of the week rotation
- Community-submitted games

## Principles

1. **Ship small, ship often** — every session ships something playable
2. **Zero friction** — no downloads, no accounts, no build steps
3. **Mobile-first** — games must work on touch devices
4. **Single-file philosophy** — each game is one HTML file, no dependencies
5. **Dark theme** — consistent visual identity across all products
6. **Open source** — MIT licensed, community can contribute