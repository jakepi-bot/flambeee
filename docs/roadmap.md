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

- **v0.5.0** — Game Stats + Simon Difficulty (shipped 2026-08-09)
  - Per-game stats tracking (plays, wins, best times) with Game Hub display
  - Simon difficulty levels (Easy/Classic/Hard) with per-difficulty bests
  - 25/25 logic checks; peer review caught 2 real bugs before merge

- **v0.6.0** — Wordfire (shipped 2026-08-11)
  - Fourth game: daily 5-letter word puzzle, UTC-seeded (same word for everyone)
  - Streak counter (gap reset + best), daily lockout after solve
  - Practice mode (random puzzles, no streak impact)
  - Colorblind mode (shape symbols), on-screen + physical keyboard, mobile-first
  - Stats integration + hub card; 1432 curated answers / 4656 guesses
  - 22/22 logic checks + DOM smoke test; peer review + brand + compliance APPROVE

- **v0.7.0** — Mobile Touch Quality Pass (shipped 2026-08-14)
  - CEO directive (2026-08-11) + community issue #26 (Wordfire iOS zoom/scroll): standardized the mobile touch baseline across all 4 games + hub
  - Wordfire: double-tap zoom fix (APPLE double-P), no tap delay, larger keys, color legend
  - Simon: zoom-safe rapid taps; Minesweeper: responsive cells, scrollable hard board, long-press flag fix
  - 32/32 static invariant checks + real-device manual test plan (B1-B8)
  - Story 008 + 009; issue #26 closed

- **v0.8.0** — Wordfire Share + Per-Difficulty Stats (shipped 2026-08-16)
  - Wordfire: shareable daily results (Story 010) — spoiler-free N/6 + streak + 6x5 grid, colorblind shapes, Web Share/clipboard/fallback
  - Minesweeper: per-difficulty stats (Story 011) — plays/wins/bestTime per difficulty, legacy migration, hub E/M/H bests
  - Website: What's New section (Story 012) on flambeee.com — latest release + Releases/Blog links
  - 23/23 static invariant checks + browser smoke tests (daily win share, no share on loss/practice, migration, per-diff recording)
  - Market note: puzzle games are the most-played browser category (23% of sessions); sharing is the most literal pull signal per PMF notes

- **v0.9.0** — Wordfire Guess Distribution + Website Screenshots (shipped 2026-08-18)
  - Wordfire: guess-distribution panel (Story 013) — bars for wins in 1-6 guesses, played/won/win%, daily-only, once per day, practice isolated
  - Website: game card screenshots (Story 014) — real board captures from actual game HTML, alt text, responsive 4:3, no more emoji icons
  - 29/29 static invariant checks + 6 browser smoke tests; peer review APPROVE + Palette APPROVE + Vigil APPROVE
  - Market note: word games growing ~31.7% (2023-2026, Wordle pipeline); daily-puzzle habits dominate browser gaming; distribution is the standard companion to shares

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

### v0.5.0 — Session 5 (2026-08-09) ✅ Shipped
- **Game stats tracking** (games played, wins, best times) — retention play per PMF notes: watch for pull signals, give players a reason to come back
- **Simon difficulty levels** — completes the difficulty rollout across all games
- Peer review caught 2 bugs before merge (2048 double-count, Simon sequence race), both fixed
- 25/25 logic checks passed

### v0.6.0 — Session 6 (2026-08-11) ✅ Shipped
- **Wordfire** — fourth game: daily 5-letter word game
  - UTC-seeded daily puzzle (same word for all players), streak counter with gap reset, practice mode
  - Colorblind shapes, full keyboard/mobile support, stats + hub card
  - Story 007 (18 BDD scenarios), 30-case test plan, 22/22 logic checks, DOM smoke test
  - Peer review APPROVE + Palette APPROVE + Vigil APPROVE
- Market note: instant-play browser games are a growing 2026 category; word/brain games rank top in roundups
- Retention thesis: a daily streak is the most literal pull signal per PMF notes

### v0.7.0 — Session 7 (2026-08-14) ✅ Shipped
- **Mobile Touch Quality Pass** — CEO directive (2026-08-11) + community issue #26: standardized the mobile touch baseline across all 4 games + hub
  - Wordfire: double-tap zoom fix, no tap delay, larger keys, color legend
  - Simon: zoom-safe rapid taps; Minesweeper: responsive cells, scrollable hard board, long-press flag fix
  - 32/32 static checks + real-device manual test plan; Stories 008 + 009; issue #26 closed

### v0.8.0 — Session 8 (2026-08-16) ✅ Shipped
- **Wordfire shareable results** — daily win overlay gets a Share button; spoiler-free summary (N/6 + streak + 6x5 tile grid), colorblind shapes, Web Share/clipboard/textarea fallback. Retention play: sharing is the most literal pull signal per PMF notes.
- **Minesweeper per-difficulty stats** — plays/wins/bestTime tracked per difficulty (carried from v0.5.0 review nits); legacy stats migrated; hub shows E/M/H bests.
- **Website What's New section** — flambeee.com home page now shows the latest release with Releases/Blog links (brand surface per CEO 2026-08-14).
- 23/23 static checks + browser smoke tests; peer review APPROVE + Palette APPROVE

### v0.9.0 — Session 9 (2026-08-18) ✅ Shipped
- **Wordfire guess distribution** — daily players get a record panel: bars for wins in 1-6 guesses + played/won/win% (daily only, once per day, practice isolated). Retention play: visible personal record that only grows by returning; matches the share grid format from v0.8.0.
- **Website game card screenshots** — flambeee.com game cards now show real board screenshots (Playwright captures of actual game HTML with scripted in-play states) instead of emoji icons; alt text on all 4, responsive 4:3 aspect. Brand surface per CEO 2026-08-14.
- Stories 013 (7 BDD scenarios) + 014 (5 BDD scenarios); 29/29 static checks + 6 browser smoke tests; peer review APPROVE + Palette APPROVE + Vigil APPROVE
- Market note: word games growing ~31.7% 2023-2026 (Wordle pipeline); puzzle retention benchmarks ~30% D1 / 14% D7; daily-puzzle habits dominate browser gaming. Guess distribution is the standard companion to shares.

### v0.10.0 — Session 10 (candidate)
- Wordfire leaderboards (if pull signal confirmed)
- Game of the week rotation
- Continue community feedback integration
- Website: full games page with per-game detail (screenshots landed in v0.9.0; next step is a dedicated page)

### Future
- Mobile app packaging (PWA)
- Multiplayer games (WebSocket-based)
- Game of the week rotation
- Community-submitted games
- Wordfire leaderboards (if pull signal confirmed)
- Wordfire guess-count stats (if pull signal confirmed)

## Principles

1. **Ship small, ship often** — every session ships something playable
2. **Zero friction** — no downloads, no accounts, no build steps
3. **Mobile-first** — games must work on touch devices
4. **Single-file philosophy** — each game is one HTML file, no dependencies
5. **Dark theme** — consistent visual identity across all products
6. **Open source** — MIT licensed, community can contribute