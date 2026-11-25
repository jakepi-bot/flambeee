# Story 163: LIGHTFARE TITLE board at short heights (Session 72, P0)

**Status:** Ready for development (Session 72, 2026-11-25).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (first-ten-seconds readability defect; a TITLE with no board at the most common phone width. Ships in v0.59.0).
**Assigned to:** **Riven**, sole code owner. File: `website/games/lightfare.html` only. Zero other files.
**Base commit:** `12cf383` (main, v0.58.0).
**Scope:** Issue #292 NB-1: at phone widths up to 430 px and heights up to 800 px, TITLE shows a real board, never `display: none`, with Start fully above the fold at 375x667. Compact TITLE copy plus a capped TITLE board until the TITLE document sum fits 667 px at 375x667.
**Design contract:** `flambeee-team/design-handoff.md`, Section 1 (Story 163, subsections 1.1 through 1.6). Design-owned observable criteria live in contract subsection 1.5 and are mapped here one for one.
**Non-blocking rule:** if 163 cannot keep Start above the fold with a real readable board at 375x600, the floor is 375x667 plus 320x568 documented, and 163 ships with the shorter height recorded as the named limitation TITLE-SHORT-600. Never ship a board below the 140 px floor and never reintroduce `display: none`.

## Summary

At 375x667, the most common phone viewport, LIGHTFARE TITLE shows no board at all. The short-viewport media query (`max-width: 430px` and `max-height: 800px`, lines 125-164) hides it outright at line 136, because attract copy plus pad plus LOOK cannot sum under 667 px with the 210 px RUN board floor. A first-time player sees copy, a pad, and a LOOK button with nothing to look at. This story replaces the hide with a TITLE layout that shows a real 7x7 board: compact TITLE copy (the two explanatory paragraphs hidden by CSS at short viewports only, copy bytes unchanged), a fixed-width TITLE board at TITLE_BOARD_W 150 px default (floor 140 px), the pad row and LOOK kept as shipped, and Start fully above the fold with the whole TITLE document at most 667 px at 375x667. Desktop and 390x844 keep the full copy and the uncapped board. The TITLE to RUN transition switches the board from the fixed TITLE width to the existing RUN height-capped formula (line 134, untouched) in pure CSS `:has()` scoping, no JS.

## Baseline measured at Session 72 planning (Wave 1, 2026-11-25)

| Check | Value |
|---|---|
| Base commit | `12cf383` (main, v0.58.0) |
| Game file | `website/games/lightfare.html`, 665 lines |
| Short-viewport block | lines 125-164, `@media (max-width: 430px) and (max-height: 800px)` |
| Defect line | line 136: `#screen:has(#title:not([hidden])) #board { display: none; }` (deleted by this story, never moved) |
| RUN board rule | line 134 formula, floor 210 px (untouched) |
| TITLE budget at 375x667 | 648 px against the 667 px ceiling, slack 19 px (contract 1.2 line items) |
| TITLE board default | TITLE_BOARD_W 150 px (range 140-160); cells 17.1 px, glyph `font-size: 1rem`, `line-height: 1` |
| Viewports for verification | 375x667, 375x600, 320x568, 390x844, 1280x800, real headless Chromium, `scrollY = 0` |

## Functional requirements

FR-1 (contract 1.1, layout 1-2). On TITLE at short viewports, `#board` renders (`display: grid`, same element, same render path; the line-136 `display: none` rule is deleted). TITLE shows compact copy: `h2`, the oneliner `Every look costs. Reach the exit with light to spare.`, and `#startBtn` stay; the two explanatory paragraphs (halo, scoring) are hidden by CSS scoped to TITLE inside the short media query only. Desktop and tall phones keep the full copy. No copy byte in the file changes.

FR-2 (contract 1.1, layout 3, plus 1.4 limitations). The pad row and LOOK stay on TITLE as shipped (48 px cells, inline row, Story 159 tap message intact). At 375x667 the whole TITLE document fits (see FR-4). At heights at or below 600 px the pad row may sit below the fold and is reachable by scroll: 375x600 document at most 660 px, 320x568 at most 680 px, with the board visible and Start rect bottom at most the viewport height at both. These are named limitations (TITLE-SHORT-600, TITLE-SHORT-320), not FAILs, provided Start stays above the fold.

FR-3 (contract 1.1, layout 4, plus untouchables). TITLE to RUN switches the board cap from the fixed TITLE width to the existing RUN height-capped formula; RUN to TITLE (`reset()`, WIN return path) switches back. Pure CSS `:has()` state scoping, no JS. `CONFIG` (GRID 7, LIGHT_BUDGET 15, LOOK_PRICES, REVEAL_MS 1000, MOVE_LIMIT 80, HALO_RADIUS 1), `move()`, `look()`, the level table, `enterRun()`, `advance()`, `retry()`, `backToTitle()`, the play-counter trio, best persistence, and all shipped copy strings are untouched.

FR-4 (contract 1.2, budget and rects). TITLE vertical budget at 375x667: BODY_PAD 20 + BACK_LINK 20 + H1 31 + HUD 98 + TITLE_BOARD_W 150 + BOARD_CHROME 14 + MSG 30 + TITLE_PANEL 123 + PAD_ROW 162 + BODY_PAD_BOTTOM 10 = 648 px, ceiling 667 px. Rect assertions at 375x667 (`scrollY = 0`): `#board` display not `none`, rect width in [140, 160] px, rect height above 0; `#startBtn` rect top at least 0 and bottom at most 667; `document.documentElement.scrollHeight` at most 667. The HUD keeps all 8 items including the plays line at every viewport; nothing may hide a HUD item. If the measured stack exceeds 667 with the board at 150, Riven steps down toward the 140 min (each 1 px of board saves about 1 px of document) and records the shipped value in the PR.

FR-5 (contract 1.4 Plan B, ordered). If 150 px plus compact copy cannot hold 667 with Start above the fold in measurement: first keep the board at the 140 min and hide the back link on TITLE at short viewports only (saves about 20 px, navigation still one tap away via browser back and via every other state). If even that fails, ship 375x667 with the documented TITLE-SHORT-600 style limitation (named ceiling, Start still above fold, board at min) and name the taller shortfall in the PR. Ordering is fixed: smaller readable board first, back-link hide second, named limitation third. Never a board below 140, never `display: none` again.

FR-6 (contract 1.3, constants). TITLE_BOARD_W 150 px default (140 min, 160 max); TITLE cell `font-size: 1rem` fixed; TITLE explanatory paragraphs hidden at short viewports (fixed, not tunable); TITLE doc ceiling 667 px at 375x667 asserted not coded; Start fold bound (rect bottom at most viewport height) at all short TITLE viewports; RUN board rule, pad cells, and action min-heights untouched.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 1.5; AC-1 through AC-7 map them directly. AC-8 pins the structural scope requirement.

1. Given viewport 375x667 on TITLE, when the player loads the page, then a full 7x7 board is visible (maze walls, floor dots, exit mark, player mark) and Start is fully above the fold and the page does not scroll. (design 1.5.1; FR-1, FR-4)
2. Given viewport 375x667 on TITLE, when the player reads the panel, then it shows the LIGHTFARE heading, the oneliner, and Start, with no halo or scoring paragraph text. (design 1.5.2; FR-1)
3. Given viewport 375x600 on TITLE, when the player loads the page, then the board is visible and Start is visible without scrolling, and the pad row is reachable by a short scroll. (design 1.5.3; FR-2)
4. Given viewport 320x568 on TITLE, when the player loads the page, then the board is visible and Start is visible without scrolling. (design 1.5.4; FR-2)
5. Given viewport 390x844 on TITLE, when the player loads the page, then the full three-paragraph copy shows and the board shows at full width (tall phone unchanged). (design 1.5.5; FR-1)
6. Given any short viewport on TITLE, when the player taps a pad direction, then the exact line `Press Start to play. Use the pad once your run begins.` appears and no run starts and the board does not move. (design 1.5.6; FR-3)
7. Given a started run from short TITLE, when the player looks at the board, then it grows to the RUN cap and play proceeds exactly as at 12cf383 (same prices, same halo, same 1000 ms reveal). (design 1.5.7; FR-3)
8. Given `git diff main --stat` for this story, when the changed files are listed, then only `website/games/lightfare.html` changed; zero `website/sw.js` bytes (the cache rider belongs to Story 164), zero other files. (scope)

## Out of scope

No new game, no new mechanic, no new storage key, no #265 items, no website redesign. No touch to `CONFIG`, `move()`, `look()`, the 5-row level table, `enterRun()`, `advance()`, `retry()`, `backToTitle()`, the play-counter trio, best persistence, or any shipped copy string. No HUD readout change, no RUN layout change, no ends layout change (that is Story 164), no landscape promise (portrait matrix only). No `website/index.html` change (there is no new game card today).

## Non-blocking rule

This story is never cut to a hidden board. If the 150 px board plus compact copy cannot hold 667 with Start above the fold at 375x600, the floor is 375x667 plus 320x568 documented, and 163 ships with TITLE-SHORT-600 recorded as a named limitation. Below the 140 px board min the limitation path applies instead of a smaller unreadable board.

## Defects/risks

- Board shrunk until Start fits but too small to read the halo: mitigated by the 140 px floor and the ordered Plan B; Riven records the shipped width in the PR.
- Text-size zoom pushing HUD past 3 rows: fallback is board toward 140 min, then a recorded limitation; never hide a HUD item (the plays line is harness asserted).
- Tap message row breaking the 667 ceiling: verification reads every set twice (fresh load, and after one pad tap), 10 reads total; one MUST miss is FAIL.
- Verification plan: 5 TITLE viewports times 2 reads (fresh plus post-tap) with rectangle sets (`#board` display plus rect, `#startBtn` rect, `#msg` height, panel height, HUD rows, `scrollHeight`); pass thresholds per contract 1.6 (375x667 doc at most 667 with board in [140, 160] and Start inside; 375x600 doc at most 660 with Start inside; 320x568 doc at most 680 with Start inside; 390x844 and 1280x800 full copy unchanged). Screenshots of TITLE at 375x667 and 375x600 kept for the release wave.
