# Story 143: EMPTY HANDS site integration (Session 65, P0b, site rider)

**Status:** Build-ready (Session 65, 2026-11-18).
**Author:** Quinn (Business Analyst), Wave 1.
**Priority:** P0b (site rider; ships in the Story 142 PR, same owner, same merge).
**Assigned to:** **Riven** (SOLE code owner; this story plus Story 142 ship as ONE PR with three changed paths total). Kai peers the PR.
**Base commit:** `1a7e7f6` (main, Session 64 merge of #261).
**Design contract:** `flambeee-team/design-handoff.md`, Section M (Rook; M.1 notes the card, copy, and precache line carry no mechanic change).
**Session plan:** `flambeee-team/session-plan.md`, Session 65 (2026-11-18), P0b item plus the floor list (one card, copy move, bump 27 to 28, one precache line).
**Dependencies:** Story 142 (the card Play link targets the Story 142 file; both land in one PR so the link resolves on the PR head).

## Context (why this story exists)

A new game with no card, no precache entry, and no cache bump is unreachable offline and invisible on the catalog. The standing rule (Session 63 plan, verified at Session 64 close) is that any new game ships one card, one precache line, and the cache bump in the same PR. This story is that rider, nothing more. The release wave owns versioning and What's New.

## Scope

Two shell edits plus the card block, inside the Story 142 PR: one card block in `website/index.html`, the "Nine games" copy moved to "Ten games", `CACHE_VERSION` 27 to 28 in `website/sw.js`, exactly one precache line after saltline. `GAME_ORDER` untouched. What's New untouched.

## Files (one PR with Story 142, Riven)

| File | Change | Owner |
|---|---|---|
| `website/index.html` | Card block appended after the SALTLINE card (last in the games grid); line 674 `Nine games, one arcade` to `Ten games, one arcade`; nothing else | Riven |
| `website/sw.js` | Line 21 `CACHE_VERSION` 27 to 28; exactly one precache line `'./games/empty-hands.html'` after the `'./games/saltline.html'` line (saltline line gains its trailing comma); nothing else | Riven |

Plus the Story 142 file `website/games/empty-hands.html` (new). Three changed paths total in the PR, zero deleted.

## Functional requirements

- FR-1. Card block follows the shipped `game-card` pattern (game-icon div, game-name, game-desc, play-btn link), placed after the SALTLINE card as the last games-grid entry. Name: Empty Hands. Description is verb-led and teaches the loop in one line (give away every coin; empty board wins). Play link targets `games/empty-hands.html`. Glyph is a plain geometric mark in the existing icon style; Riven picks one that does not collide with a shipped glyph.
- FR-2. Line 674 reads `Ten games, one arcade. All free, all in your browser.` Only the number word changes.
- FR-3. `website/sw.js` line 21 reads `var CACHE_VERSION = 28;`.
- FR-4. Exactly one precache line is added: `'./games/empty-hands.html'` immediately after the `'./games/saltline.html'` line, with the saltline line gaining a trailing comma. No other precache entry is added, removed, or reordered.
- FR-5. `GAME_ORDER` (6-entry weekly rotation at `website/index.html:1175`) is byte-identical. The catalog grows; the rotation does not change.
- FR-6. The What's New section is byte-identical (still v0.51.0 Echo Rounds). The release wave owns it.
- FR-7. No other line in either shell file changes. No new file, no new dependency, no copy claim about controllers, FPS, or timing.

## BDD acceptance criteria

Threshold: 7 of 7 on the PR head.

- AC-1 (card present and linked). Given the PR head, when the games grid is read, then an Empty Hands card sits after the SALTLINE card with the game name, a verb-led description, and a Play link to `games/empty-hands.html`, and GET on that path returns 200.
- AC-2 (copy moved). Given the PR head, when `website/index.html:674` is read, then it reads `Ten games, one arcade.`, and no other copy line in the file differs from base `1a7e7f6`.
- AC-3 (cache bump). Given the PR head, when `website/sw.js:21` is read, then it reads `var CACHE_VERSION = 28;`, and no other version token in the file differs.
- AC-4 (one precache line). Given the PR head, when the PRECACHE_URLS list is read, then it contains exactly one new entry `'./games/empty-hands.html'` immediately after `'./games/saltline.html'`, with 23 entries total and order otherwise preserved.
- AC-5 (rotation untouched). Given the PR head, when `GAME_ORDER` is read, then it is the identical 6-entry array as base (cinder, wordfire, minesweeper, simon, 2048, afterglow).
- AC-6 (What's New untouched). Given the PR head, when the What's New section is diffed against base, then it is byte-identical (v0.51.0 entry, no ten-game claim here; the release wave writes it post-tag).
- AC-7 (diff discipline). Given the PR head, when `git diff --stat` against base is read, then the PR holds exactly three paths (`website/games/empty-hands.html` new, `website/index.html`, `website/sw.js`), zero deleted, zero paths under `dev/`.

## Design criteria map (Rook M.8, by reference, not duplicated)

No M.8 scenario touches site integration (M.1 notes none of the turn-sequence contract changes index.html or sw.js except the card, copy, and precache line). The card description must still teach the shrink fantasy honestly; any wording that promises timing, holding back, or controller play fails review.

## Completion checklist

- [ ] Card block after SALTLINE; Play link GET 200 on the PR head
- [ ] Line 674 reads `Ten games, one arcade.`
- [ ] `CACHE_VERSION` reads 28; exactly one precache line after saltline
- [ ] `GAME_ORDER` byte-identical; What's New byte-identical
- [ ] AC-1 through AC-7 recorded pass in the build PR body with live pasted output, 7 of 7
- [ ] `git diff --stat` pasted in the PR body: three paths, zero deleted
- [ ] Kai peer review; Rook design review against Section M

## Cut line (binding, from session-plan)

This story is floor: card plus copy plus bump plus precache line, all in the game PR. Hard out 1 applies in full: gate not green by 02:45 means the release wave ships nothing, so no card, no precache line, and no half-done cache bump land anywhere. The PR is closed or reverted and the mechanic moves to Friday.

## Out of scope

- No game logic (Story 142, same PR).
- No proof harness or seed manifest (Story 144, Kai).
- No `GAME_ORDER` change, no Apps edits, no What's New edit, no version cut.
- No Cinder, cadence, FPS, or controller content.
- No visual redesign. Palette owns visual direction.

## Open questions

None. Glyph choice is Riven's call inside the existing icon style; any non-colliding geometric mark passes.

## References

- `flambeee-team/session-plan.md`, Session 65 (2026-11-18): P0b rider, floor list, hard out 1.
- `flambeee-team/design-handoff.md`, Section M (Rook), M.1 site note.
- Format precedent: Story 140 (`docs/stories/140-echo-rounds-run-structure-session63.md`) for the site-rider shape.
