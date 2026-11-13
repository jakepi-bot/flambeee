# Story 137: SALTLINE site integration (Session 60, P0b)

**Status:** Ready for development (Session 60, 2026-11-13).
**Author:** Quinn (Business Analyst), Wave 1.
**Priority:** P0b (site integration; rides in Riven's SALTLINE PR, same PR as Story 133 by construction).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds Story 133's game file plus this story's site surfaces together). No shared ownership.
**Base commit:** `c73c4af`.
**Design contract:** `flambeee-team/design-handoff.md`, Session 60, Section C (Rook; behavior only, Palette owns visual direction).
**Depends on:** Story 133 (the game file must exist in the same PR; card target, precache entry, and proof all resolve against it). No code dependency outside that pair.

## Summary

Integrate the Story 133 SALTLINE game into the site: exactly one site card on `website/index.html` following the Echo Rounds / Typewreck icon-card pattern, `CACHE_VERSION` 25 to 26 plus exactly one new `sw.js` precache entry for the game file, `GAME_ORDER` untouched, What's New heading left to the release wave. Same PR as Story 133 by construction; the split into two stories is for review clarity, not for separate ownership or separate merges.

## Baseline measured at Session 60 planning (HEAD `c73c4af`)

| Check | Value |
|---|---|
| `CACHE_VERSION` (`website/sw.js:21`) | 25 (run must read the line, not assume it) |
| Precache block (`website/sw.js`) | 21 entries, ending with `./games/typewreck.html` |
| Card target | `website/games/saltline.html` absent on base (RED anchor, resolves in the same PR) |
| `GAME_ORDER` (`website/index.html:1169`) | 6 entries (`cinder`, `wordfire`, `minesweeper`, `simon`, `2048`, `afterglow`), untouched by this story |
| `website/index.html` | 48,482 bytes |
| Website What's New heading | v0.49.0 (release wave owns it; this story does not touch it) |

## Files in scope

| File | Change | Owner |
|---|---|---|
| `website/index.html` | Exactly one new game card, icon-card pattern, no other section touched. | Riven |
| `website/sw.js` | `CACHE_VERSION` 25 to 26 plus exactly one new precache line. | Riven |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding Story 133's game file plus this story's card, cache bump line, and precache entry together in one PR, so overlap is impossible by construction. Kai peers the PR and holds no build story this session. No shared ownership with the jobs pipeline or any outside team.

### 2. Site card (exactly one)

- Exactly one new game card on `website/index.html` following the Echo Rounds / Typewreck icon-card pattern: a `game-card` div with a `game-icon` glyph div (no screenshot asset), a `game-name` div, a `game-desc` div, and a `play-btn` anchor.
- Card name `SALTLINE`. One-line description stating the verb: `Hold to charge, release to push back the sea.` (46 characters, under 80).
- Play link `games/saltline.html`. Card target resolving: the link target exists in the same PR and returns GET 200 over local serve.
- The icon glyph is a build choice consistent with existing icon cards. Palette owns visual direction; the build must not invent new art.
- `GAME_ORDER`: stays exactly the six existing entries in order. No GAMES object modal entry (the GAMES object has five keys and neither Echo Rounds nor Typewreck has one). The new game is reachable by card and direct link only.
- No other index section is redesigned.

### 3. Cache ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (25 to 26) and exactly one new precache entry: `  './games/saltline.html'`, positioned after the `'./games/typewreck.html'` line (line 45 at base).
- No other service-worker behavior change. No other precache line added, moved, or edited.

### 4. Scope guard: must not change

- No screenshot asset for the card.
- No GAMES object modal entry.
- `GAME_ORDER` unchanged (6 entries, same order).
- What's New heading stays v0.49.0 until the release wave owns it.
- No other card, game, or app touched. No other `website/index.html` section touched.
- No `website/sw.js` change beyond the version bump and the single precache line.
- No service-worker behavior change of any kind.

### 5. BDD acceptance criteria (design-handoff Section C, observable)

- **C-1.** Given the shipped index, when the games grid is read, then a SALTLINE card exists with name `SALTLINE`, the verb description, and a Play anchor whose href resolves to `games/saltline.html` with GET 200.
- **C-2.** Given `website/sw.js`, when it is read, then `CACHE_VERSION` is 26 and the precache list contains exactly one `saltline.html` line, positioned after the `typewreck.html` line.
- **C-3.** Given one online visit to the page followed by offline mode, when `games/saltline.html` is loaded, then it plays fully offline with zero network fetches.
- **C-4.** Given the shipped index at 375 px width, when `scrollWidth` is read, then it is <= 375 (no horizontal overflow attributable to the new card).
- **C-5.** Given the shipped index and game page, when the console is read after load and one full run, then zero errors are attributable to the new card or page.

## Definition of done

Card present and resolving (C-1), `CACHE_VERSION` reads 26 with the single precache line after the typewreck line (C-2), offline load proven (C-3), 375 px overflow clean (C-4), console clean (C-5), diff limited to the one card plus the bump plus the one precache line (plus Story 133's one game file in the same PR), copy in plain punctuation. Docs only in this story file; zero code, zero website bytes here.

## Non-goals

- Any second card, any index redesign, any `GAME_ORDER` change, any GAMES modal entry.
- Any game logic change (Story 133 owns the game file).
- Any screenshot or art asset (Palette owns visual direction).
- Any service-worker behavior change beyond the version bump and the single precache line.
- Cutting a version or touching the What's New heading (release wave owns those).
