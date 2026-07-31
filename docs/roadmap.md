# Flambeee Product Roadmap

## Vision

Flambeee builds snackable, instantly-playable web games. No downloads, no signups, no friction. Open source, community-driven, fun first.

## Current State

- **v0.1.0** — Minesweeper (shipped 2026-07-29)
  - 3 difficulty levels (Easy 9x9, Medium 16x16, Hard 30x16)
  - Mobile support (long-press to flag, flag mode toggle)
  - First-click-safe, flood fill, win/lose detection, timer
  - Single-file HTML/CSS/JS, no dependencies

## Roadmap

### v0.2.0 — Session 2 (2026-07-31)
- **Simon memory game** — classic sequence-repeat game with increasing difficulty
- **Game hub/launcher** — central page to pick which game to play
- Polish: consistent theming across games, shared visual identity

### v0.3.0 — Session 3 (planned)
- Third game (candidate: 2048, Snake, or Tetris clone)
- High score persistence (localStorage)
- Difficulty selection from hub

### v0.4.0 — Session 4 (planned)
- Fourth game
- Game stats tracking (games played, best times, win rate)
- Community feedback integration (GitHub issues → feature requests)

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