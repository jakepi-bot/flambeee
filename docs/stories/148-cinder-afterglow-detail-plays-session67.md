# Story 148: Cinder + Afterglow detail-view plays rows (Session 67, P0, #268)

**Status:** Ready for development (Session 67, 2026-11-20).
**Author:** Quinn, Business Analyst.
**Priority:** P0. Issue #268, milestone M-3 batch; gates #215 close.
**Assigned to:** **Riven**, sole code owner (Story 048 protocol). One PR shared with Stories 149 and 150.
**Base commit:** `8430f1d` (main, v0.53.0 released).
**Scope:** `website/index.html` only (Cinder + Afterglow `getStats`/`formatStats` hunks, one shared sanitize helper at IIFE scope). Zero game-file edits.
**Design contract:** `flambeee-team/design-handoff.md`, Story 148 sections 1-7 plus pinned P1/P2/P3. Design-owned observable criteria live in contract section 6 and are NOT repeated here; the functional AC below test the same behavior from the requirements side.

## Summary

The Cinder and Afterglow home-page detail modals currently ignore the shipped per-browser plays counters. Add one read-only `Plays` row to each modal, sourced from the existing keys (`flambeee-cinder-plays`, `flambeee-afterglow-plays`), under the pinned empty-state rule (P1) and shared sanitize rule (P2). Fresh browsers keep the friendly empty message; a player with plays but no save still sees the Plays row.

## Baseline measured at Session 67 planning (Wave 1, 2026-11-20)

| Check | Value |
|---|---|
| Base commit | `8430f1d` |
| `GAMES` entries | 6 (wordfire, afterglow, minesweeper, simon, 2048, cinder) |
| Cinder `getStats` reads | `flambeee-cinder-save` only; no plays read |
| Afterglow `getStats` reads | `flambeee-afterglow-stats` only; no plays read |
| Plays keys on disk | `flambeee-cinder-plays` (cinder.html:72), `flambeee-afterglow-plays` (afterglow.html:392) |
| Sanitize rule (game pages) | integer 0..9007199254740991, numeric strings accepted, everything else 0 |
| Empty-state copy | `Play your first round to see your stats here` (index.html ~1277) |
| `GAME_ORDER` | 6 entries, untouched by this story |

## Requirements

### 1. Plays reads (P0 core)
- Cinder `getStats` additionally reads `localStorage.getItem('flambeee-cinder-plays')` alongside the existing `flambeee-cinder-save` read.
- Afterglow `getStats` additionally reads `localStorage.getItem('flambeee-afterglow-plays')` alongside the existing `flambeee-afterglow-stats` read.
- Each modal open re-reads. No caching of stats across opens.

### 2. Shared sanitize helper (P2)
- One shared helper at IIFE scope (distinct name, no collision with per-game `sanitizePlays`).
- Accept: integer numbers 0..9007199254740991; non-empty numeric strings converting to such an integer.
- Yield 0 for: negative, fractional, NaN, Infinity, null, undefined, absent key, corrupt JSON (parse throws), wrong shape (object/array/boolean), empty string, over-cap values.
- Read-only: site never calls `localStorage.setItem` for these keys. Corrupt values display as absent, never written back.
- Plan B: if IIFE-scope placement is not clean, the identical expression may be inlined in each `getStats` with a PR note. No third variant of the rule under any circumstance.

### 3. Empty-state gate (P1)
- `formatStats` returns null (EMPTY) iff every displayed stat including plays is 0 or absent; existing copy `Play your first round to see your stats here` renders unchanged.
- Any displayed stat including plays non-zero renders DATA, including the Plays row.
- Consequence: plays > 0 with no save/stats record still flips the modal to DATA.

### 4. Row shape
- Cinder DATA rows in order: Level, Gold, Wins, Deaths, Plays (Plays appended last; existing four keep order/labels).
- Afterglow DATA rows in order: Levels cleared, Runs finished, Best level, Plays.
- Row DOM: `<div class="modal-stat-item"><span class="modal-stat-label">Plays</span><span class="modal-stat-value">N</span></div>`. Label exactly `Plays`. Value is integer-to-string, no abbreviation, no comma formatting.
- When DATA is active due to existing stats but plays is absent/0, render the Plays row with 0 (predictable presence).

### 5. Boundaries (P3)
- No edits to `website/games/*.html`, `BLOG.md`, release notes, Bluesky staging. No network calls, no aggregation, no identity, no new localStorage keys.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 6 and are not repeated here.

1. Given a browser with no flambeee keys stored, when I open the Cinder detail view, then I see `Play your first round to see your stats here` and no number, no `NaN`, no `undefined`, no exception. (P1 fresh-browser)
2. Given the same fresh browser, when I open the Afterglow detail view, then I see the same empty message with the same guarantees. (P1 fresh-browser, Afterglow)
3. Given localStorage holds `flambeee-cinder-plays` = 3 and no `flambeee-cinder-save`, when I open the Cinder detail view, then I see a row labeled `Plays` with value `3` and I do not see the empty message. (P1 plays-alone flips)
4. Given localStorage holds `flambeee-afterglow-plays` = 1 and no `flambeee-afterglow-stats`, when I open the Afterglow detail view, then I see a row labeled `Plays` with value `1` and no empty message. (P1 plays-alone flips, Afterglow)
5. Given a Cinder save with level 4 and no plays key, when I open the Cinder detail view, then I see Level, Gold, Wins, Deaths rows as today and the Plays row reads `0`. (P1 existing-stats drive DATA; predictable row presence)
6. Given stored plays value `"42"` (numeric string), when I open the matching detail view, then the Plays row reads `42`. (P2 numeric-string accepted)
7. Given stored plays values `-5`, `3.5`, `"NaN"`, `null`, `"not-json{{{"`, `[1]`, `{"n":1}`, `true`, `""`, or an integer above 9007199254740991, when I open the matching detail view with no save/stats record, then the modal shows the empty message, shows no error, and the stored value is byte-identical afterwards (read-only, P2 + P3).
8. Given stored plays value `999999999`, when I open the matching detail view, then the Plays row reads `999999999` as-is with no abbreviation or comma formatting. (P2 large-valid passthrough)
9. Given `localStorage.getItem` throws (private/blocked mode), when I open either detail view, then the modal still opens, treats the plays read as absent, and shows no error surface. (P1 storage-throws)
10. Given the modal open twice in a row with a changed plays key between opens, when I reopen, then the second open reflects the new value (re-read per open, no cross-open cache).
11. Given Escape / close button / overlay click, when I dismiss either modal, then it closes and focus returns to the invoking element (existing behavior unchanged).
12. Given the merged tree, when `git diff` is grepped for `localStorage.setItem` inside `website/index.html` detail-view hunks plus fetch/XMLHttpRequest/sendBeacon/WebSocket/new external URLs, then there are no matches (P3 read-only + no-network).
13. Given issue #268 acceptance, when Scout runs a real browser on desktop and mobile, then both modals render the specified states with exact copy (`Plays`, `Play your first round to see your stats here`) and zero modal-attributable console errors.

## Issue #268 / #215 linkage

This story plus Story 149 satisfy #268 acceptance: detail views show plays from the existing keys, friendly empty state, corrupt values sanitized like game pages, real-browser QA desktop+mobile, CACHE_VERSION bump (Story 150). #215 closes only when all three games' rows land.

## Out of scope

Typewreck surface (Story 149), cache bump + pattern-doc amendment (Story 150), `GAME_ORDER` change (forbidden, Story 125), screenshot asset, GOTW rotation membership, any game-file edit, any new storage key, second counter key, aggregation or identity.
