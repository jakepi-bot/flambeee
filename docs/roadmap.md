# Flambeee Product Roadmap

## Vision

Flambeee builds snackable, instantly-playable web games. No downloads, no signups, no friction. Open source, community-driven, fun first.

## Current State

- **v0.13.1** — Cinder menu + combat patch (shipped 2026-09-01)
  - Player-reported fix session: issues #45 + #46 (BigFunger, within the hour post-launch)
  - Menu tap/click fix: event delegation replaces 28 unreachable inline handlers; mobile play restored
  - Combat routing fix: fight inputs reached the wilderness handler; combat was unwinnable by any input
  - QA bar raised: real browser taps on every menu row are now mandatory test proof
  - README lists all 5 games with flambeee.com links; repo About/description + homepage set

- **v0.13.0** — Cinder: BBS-Style Text RPG (shipped 2026-08-30)
  - Single-player BBS door game: town hub, wilderness combat, XP/leveling
  - 15 fights/day, UTC-midnight reset, localStorage persistence
  - 15 monsters, 20 events, 8 weapon/armor tiers, 10 levels, tavern rumors
  - Death loses carried gold, bank is safe. Built from community issue #41
  - Website: 5th game card + detail modal + What's New

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

### v0.13.1 — Session 14 (2026-09-01) ✅ Shipped
- **Cinder menu + combat patch (Story 021, issues #45/#46)** — both player-reported by BigFunger within an hour of the v0.13.0 launch. Menu rows rendered with inline handlers calling a function sealed inside the game's IIFE, so every tap threw a silent ReferenceError; mobile players had no keyboard fallback and could not play at all. Fixed with event delegation: 28 rows now carry data-action attributes and one listener on the display container. Second fix found under it: fight inputs were routed to the wilderness handler, making combat unwinnable by any input method; now Attack attacks, Run runs.
- **Repo presence (Story 022)** — README now lists all 5 games (Wordfire section added: it had never existed) with flambeee.com Play links, zero stale htmlpreview URLs; repo About/description + homepage set via gh repo edit.
- **QA bar raised** — QA drove v0.13.0 by keyboard only, so broken taps shipped invisible. Test plans now require real page.click()/page.tap() on every menu row on desktop and mobile viewports as proof.
- 74-check browser tap/click suite (Kai) + real-browser verification (Scout), 16/16 BDD scenarios PASS, peer reviews APPROVE both ways, QA test-plan PR #50.

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

### v0.10.0 — Session 10 (2026-08-21) ✅ Shipped
- **Website full games page (Story 015)** — every game card on flambeee.com opens a detail view: rules, real screenshot, personal stats from localStorage, relative Play link. Accessible (dialog role, focus trap, Escape close, focus return), responsive, private-mode safe, empty-state friendly.
- **Same-origin games (CEO directive)** — the 4 games + word list now live in `share/Flambeee/games/` and all Play links are relative, so localStorage stats are visible on flambeee.com itself (previously htmlpreview.github.io = different origin = invisible stats).
- Story 016 (Wordfire hard mode) written up and deferred to next session as planned (stretch).
- 9/9 BDD scenarios PASS (Scout), peer review APPROVE, Vigil APPROVE.

### v0.11.0 — Session 11 (2026-08-25) ✅ Shipped
- **Wordfire Hard mode (Story 016)** — Standard/Hard difficulty toggle (pre-round, touch + keyboard accessible, persisted in localStorage), hard daily seeded from a 330-word hard pool (same UTC-day seed, per-mode lockout), per-mode streak/stats/distribution isolation, "Wordfire Hard n/6" shares, mode-labeled record panel.
- Hard pool: programmatic filter on letter rarity + repeated letters + uncommon starts; 14.5% common-start vs 49.7% standard; every word verified in the guess list (Scout verifier PASS).
- 6/6 BDD scenarios PASS (Scout test plan + Playwright browser verification), peer review via PR #38, Vigil APPROVE.

### v0.12.0 — Session 12 (2026-08-28) ✅ Shipped
- **Wordfire modal shows Hard stats (Story 017)** — the Wordfire game detail view on flambeee.com now reads both the standard and hard localStorage keys and shows each mode's plays, wins, and streak, labeled Standard/Hard. Only modes with data appear (no zero-filled blocks). Card description and rules list mention Hard mode. Empty state preserved (never played, private mode, corrupt data).
- Pure website change: deployed `share/Flambeee/index.html` + repo mirror `website/index.html` in sync (byte-identical). 18/18 QA checks pass (8 BDD scenarios). Peer review + compliance PASS.
- Repo mirror What's New backfilled to v0.11.0 as part of the release.

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