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

## Roadmap

### v0.2.0 — Session 2 (2026-07-31) ✅ Shipped
- **Simon memory game** — classic sequence-repeat with speed scaling, colorblind cues, keyboard support
- **Game hub/launcher** — central arcade lobby, Minesweeper moved to own page
- Peer reviews: Kai caught missing Simon file, Riven caught 4 issues (all fixed)
- 12-case test plan by Scout

### v0.3.0 — Session 3 (2026-08-04) 🚧 In Progress
- **2048 game** — chosen via market scan (2048/merge-puzzle remains a top 2026 browser-game trend, snackable, zero friction)
- High score persistence (localStorage)
- Difficulty selection from hub (easy/medium/hard grid sizes)

### v0.4.0 — Session 4 (planned)
- Fourth game
- Game stats tracking (games played, best times, win rate)
- Community feedback integration (GitHub issues → feature requests)
- Difficulty selection rollout across all games

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