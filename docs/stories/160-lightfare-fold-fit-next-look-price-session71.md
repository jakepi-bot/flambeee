# Story 160: LIGHTFARE short-viewport fold fit and next-look price (Session 71, P0b)

**Status:** Ready for development (Session 71, 2026-11-24).
**Author:** Quinn, Business Analyst.
**Priority:** P0b (polish; ships in v0.58.0 in the same PR as Story 159).
**Assigned to:** **Riven**, sole code owner, same PR as Story 159. Files: `website/games/lightfare.html`, plus exactly one line in `website/sw.js` (`CACHE_VERSION` 33 to 34, all 24 precache lines byte-identical).
**Base commit:** `582171b` (main, v0.57.0).
**Scope:** Issue #285 items 1 and 4: at 375x667 and 360x740 the primary controls must be reachable without scrolling, and the RUN HUD gains the next-look price with an explicit exhausted state. Includes the `website/sw.js` `CACHE_VERSION` 33 to 34 rider.
**Design contract:** `flambeee-team/design-handoff.md`, Section 2 (Story 160, subsections 2.1 through 2.6). Design-owned observable criteria live in contract subsection 2.5 and are mapped here one for one.
**Non-blocking rule:** if the fold fit runs long, cut the HUD readout item (contract item 4) and keep the fold fit; never cut the fit to keep the readout. Story 161 is never cut by this story.

## Summary

Two #285 findings remain after Story 159. Item 1 is a phone-fold problem: at 375x667, Start and LOOK sit 110 to 140 px below the fold, so the primary control for the state is unreachable without scrolling. Item 4 is a readout gap: the next-look price is not on the RUN HUD even though the doubling curve (1, 2, 4, 8 against budget 15) is the whole game. Riven closes the fold gap with a board-shrink formula (board width capped by viewport height minus measured chrome, floor 210 px; pad cells shrink to a 48 px floor only if the rect test still fails; HUD wraps to at most 3 rows with a Plays-then-Best drop order that is expected to stay unused), verified by `getBoundingClientRect()` reads in a real Chromium viewport, not by reading CSS. The HUD gains one display-only item naming the next look price (`Next look: 1/2/4/8`, `Looks maxed` at exhaustion); pricing logic is untouched. The PR also carries the one-line `CACHE_VERSION` 33 to 34 rider in `website/sw.js`.

## Baseline measured at Session 71 planning (Wave 1, 2026-11-24)

| Check | Value |
|---|---|
| Base commit | `582171b` (main, v0.57.0) |
| Game file | `website/games/lightfare.html`, 593 lines |
| Fold gap at 375x667 | Start and LOOK sit 110 to 140 px below the fold |
| `#board` | `max-width: 336px`; body padding 12 px (24 px total) |
| Pad cells | 3x58 px cells; `button.action` min-height 44 px (never reduced) |
| HUD | 7 items (Level, Light, Moves, Looks, Bank, Best, Plays) |
| `CONFIG` at lines 167-170 | `LIGHT_BUDGET 15`, `LOOK_PRICES [1,2,4,8]`, `MOVE_LIMIT 80` (untouched) |
| `website/sw.js` | line 21 `CACHE_VERSION` 33; lines 24-49 hold 24 precache lines including `./games/lightfare.html` at line 48 |
| Short viewports | 375x667, 360x740 (portrait matrix only; landscape out of scope) |
| Regression viewport | 390x844 (already fits today; must still fit) |

## Functional requirements

FR-1 (contract 2.1, fold-fit rule). At the two short viewports, the primary control for the current state must be fully inside the visual viewport with zero scrolling required. TITLE primary control: `#startBtn` fully visible (whole border box, y 0 to viewport height) at load with zero scroll. RUN primary controls: `#pad` (all four direction buttons) and `#btnLook` (whole button), both fully inside the viewport with zero scroll. LEVELCLEAR/WIN/LOSE primary control: `#againBtn` fully inside the viewport with zero scroll. The `.keys` help line is advisory and may sit below the fold. Pass rule: `getBoundingClientRect().bottom [px] <= viewport_height [px]` AND `getBoundingClientRect().top [px] >= 0 [px]` for each primary-control rectangle, measured with `window.scrollY = 0` in a real Chromium viewport. `document.documentElement.scrollHeight <= viewport_height` is NOT required (the help line may overflow).

FR-2 (contract 2.1, ceilings). Document height ceilings: at 375x667, TITLE doc at most 667 px; RUN doc at most 667 px plus the `.keys` line only (keys line alone may add at most 60 px, so RUN doc at most 727 px). At 360x740, TITLE doc at most 740 px and RUN doc at most 800 px. At 390x844 no ceiling change; rects must still pass.

FR-3 (contract 2.2, board shrink). `#board` width rule: `board_width [px] = min(336 [px], 100 [vw percent as px] - 24 [px body padding])` (existing behavior kept), plus a viewport-height cap: `board_width [px] = min(board_width [px], floor((viewport_height [px] - chrome [px]) / 7 [cells]) - 5 [px])` where `chrome [px]` is the measured vertical budget of everything above and below the board in the current state (back link about 20, h1 about 30, HUD rows, `#msg` 22 plus margins, panel or pad-plus-look block, paddings and margins about 100 total; Riven measures chrome per state in a real viewport and records the number in the PR) and the 5 px covers gap plus board-padding share per row (3 px gap plus 12 px board padding over 7 rows, about 4.7 px per cell). Floor: `board_width_min [px] = 210 [px]` (cells about 26 px after gaps; below this the board must not shrink further and HUD wrapping carries the fit instead). Cell size: `cell [px] = (board_width [px] - 12 [px padding] - 18 [px gaps]) / 7 [cells]`; at floor 210: `(210 - 30) / 7 = 25.7 [px]` per cell, glyph at 1.3rem stays legible.

FR-4 (contract 2.2, pad and HUD). Pad cells stay 58 px until the board floor is reached; only if the rect test still fails at 375x667 may pad cells shrink, to a floor of `pad_cell_min [px] = 48 [px]`. `button.action` min-height stays 44 px (never reduced). HUD at 375x667 and 360x740 may wrap to at most 3 rows. If a cut is forced (rect test fails with 3 rows), drop order is: (1) `Plays on this browser` item first, (2) `Best` second, (3) never drop Level, Light, Moves, Looks, Bank, or the new Next-look item. Dropping means `display: none` below a measured breakpoint only at the two short viewports, restored at 390x844 and above. Expected outcome: no cut needed (7 items plus 1 new item wrap to 3 rows inside the ceiling). HUD at 390x844 wraps to at most 2 rows, nothing dropped.

FR-5 (contract 2.1-2.2, readout). The RUN HUD gains one item showing the price of the next look; display only, pricing logic (`lookPrice(k) = 2^(k-1)`, 5th look refused) untouched. Mapping: looks 0 shows `Next look: 1`; looks 1 shows `Next look: 2`; looks 2 shows `Next look: 4`; looks 3 shows `Next look: 8`; looks 4 (exhausted; budget 15, a 5th price would be 16 and no 5th price exists) shows `Looks maxed`. Exact byte copy, ASCII only. Placement: a new `.hud .item` span beside the existing Looks item, same styling, persistent across TITLE/RUN/ends (HUD is outside `#panel`); renders on boot and updates on every `render()`. When light is below the next price but looks remain (e.g. light 0 after spending), the readout still names the price; affordability is told by the existing `Not enough light.` refusal at press time, not by this readout. The readout reads `looks` and `CONFIG.LOOK_PRICES`; it never writes them.

FR-6 (contract 2.2, cache rider). `CACHE_VERSION [integer] = 34` (33 + 1) at `website/sw.js` line 21. Precache count stays 24 lines (lines 24-49), byte-identical including `./games/lightfare.html` at line 48. `git diff main -- website/sw.js` must show exactly one changed line; any other diff is FAIL.

FR-7 (untouchable list). `CONFIG` (including `LOOK_PRICES [1,2,4,8]` and `LIGHT_BUDGET 15`), `move()`, `look()`, the level table, `enterRun()`, counter helpers and keys, panel copy: all untouched.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 2.5; AC-1 through AC-7 map them directly. AC-8 pins the structural scope requirement.

1. Given viewport 375x667 and `window.scrollY = 0` on TITLE, when Scout reads `#startBtn.getBoundingClientRect()`, then `top >= 0` and `bottom <= 667` and TITLE document height is at most 667 px. (design 2.5.1; FR-1, FR-2)
2. Given viewport 375x667 in RUN, when Scout reads `#pad` and `#btnLook` rects, then all four pad buttons and the whole LOOK button satisfy `top >= 0` and `bottom <= 667` with zero user scrolling, and RUN document height is at most 727 px (keys line only overflow). (design 2.5.2; FR-1, FR-2)
3. Given viewport 360x740, when the same TITLE and RUN rect reads run, then TITLE doc is at most 740 px and RUN doc at most 800 px and every primary rect fits. (design 2.5.3; FR-1, FR-2)
4. Given viewport 390x844, when the same reads run, then every primary rect still fits (regression). (design 2.5.4; FR-1)
5. Given a fresh RUN (looks 0), when Scout reads the new HUD item, then it shows exactly `Next look: 1`; after one look `Next look: 2`; after two `Next look: 4`; after three `Next look: 8`; after four `Looks maxed`. (design 2.5.5; FR-5)
6. Given looks 4 with light below 16, when the tester presses LOOK, then the shipped refusal `Not enough light.` appears and the HUD still shows `Looks maxed` and light is unchanged. (design 2.5.6; FR-5)
7. Given the PR diff, when Quinn runs `git diff main -- website/sw.js`, then exactly the `CACHE_VERSION` line changed (33 to 34) and all 24 precache lines are byte-identical. (design 2.5.7; FR-6)
8. Given `git diff main --stat` for this story together with Story 159, when the changed files are listed, then only `website/games/lightfare.html` and `website/sw.js` (one line) changed; no `website/index.html` change, no new storage key, no `GAME_ORDER` change. (scope)

## Out of scope

No new mechanic, no new storage key, no other game file, no `GAME_ORDER` change, no `website/index.html` change (there is no new game card today), no backlog issues beyond #281/#285/#287, no FPS/app work. No touch to `CONFIG`, `look()`, `move()`, the level table, `enterRun()`, `advance()`, `retry()`, `backToTitle()`, the play-counter trio, or either storage key. Landscape short viewports (e.g. 667x375): portrait matrix only, no landscape promise. No input-guard change (that is Story 159). Story 159 ships in the same PR.

## Non-blocking rule

If the fold fit runs long, cut the HUD readout item (contract item 4, FR-5, AC-5/AC-6) and keep the fold fit; never cut the fit to keep the readout. Never cut Story 161 for this story. Plan B order if the shrink formula cannot close the 63 to 137 px gap at 375x667 without breaching the 210 px floor: first place `#btnLook` beside the pad row (same row, flex) instead of below it, saving about 58 px; only then cut the readout per this rule.

## Defects/risks

- 390x844 regression: rects already fit today; after the shrink formula they must still fit with the board at or near 336 px (formula caps, never enlarges).
- Text-size zoom / large fonts: HUD wraps to 3 rows; drop order applies only if the rect test fails.
- Board at 210 px floor but rect still fails: shrink pad to 48 px floor; if still failing, drop Plays item; record in PR.
- Price readout vs `look()` refusal: readout is advisory; the refusal line `Not enough light.` remains the affordability signal; no conflict.
- Looks exhausted display: `Looks maxed` shows on RUN HUD at looks 4; 5th look press still refused by `look()` guard as shipped.
- Cached old shell: expected until CACHE_VERSION 34 activates; old shell shows no readout (versioned-out, not a bug; pattern-doc rule).
- Verification plan: rect measurements 3 viewports x 5 states (TITLE, RUN, LEVELCLEAR, WIN, LOSE; 360x740 covers TITLE and RUN only) = 13 rect sets in real headless Chromium with fresh profiles, pass 13/13 with 0 px overflow on any primary rect; readout run driving looks 0 through 4 (spend 1+2+4+8 = 15 light, `__lightfare` getters confirm counts), 5/5 strings byte-equal plus 1 exhausted-press check; economy regression re-runs the Story 157 harness economy legs (BFS lengths [8,10,12,14,16], costs 1/2/4/8, spends 1/3/7/15, budget 15, 5th look refused, 50 wrong-turn trials per level) with identical PASS; one miss anywhere is FAIL.
