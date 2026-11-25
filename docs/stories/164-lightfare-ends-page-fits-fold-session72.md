# Story 164: LIGHTFARE ends page fits the fold (Session 72, P0b)

**Status:** Ready for development (Session 72, 2026-11-25).
**Author:** Quinn, Business Analyst.
**Priority:** P0b (second half of the #292 defect; ships in the same PR as Story 163 in v0.59.0).
**Assigned to:** **Riven**, sole code owner, same PR as Story 163. Files: `website/games/lightfare.html` (ends layout) plus the `website/sw.js` rider (`CACHE_VERSION` 34 to 35, exactly one changed line, 24 precache entries byte-identical).
**Base commit:** `12cf383` (main, v0.58.0).
**Scope:** Issue #292 NB-2: LEVELCLEAR, WIN, and LOSE document height at most the viewport height at 375x667, 375x600, and 320x568, so no vertical scroll; `#againBtn` fully visible with the retry path unchanged.
**Design contract:** `flambeee-team/design-handoff.md`, Section 2 (Story 164, subsections 2.1 through 2.6). Design-owned observable criteria live in contract subsection 2.5 and are mapped here one for one.
**Non-blocking rule:** the cache bump is not optional. `CACHE_VERSION` 35 ships in this PR even if an ends layout item moves to Plan B; the bump plus the served-copy check in the release wave is what defeats the usual liar artifact.

## Summary

The ends pages scroll. Measured at Session 72 planning, the ends document reads `scrollHeight` 750 px at 375x667 while `#againBtn` sits at 487-531 px: the button is reachable but the page moves 83 px past the fold, so the release billed as polish is the one place where the layout still shifts under the thumb. The cause is layout, not content: the ends panel renders through `#end` inside `#panel` with full panel padding, the board still shows behind it, and the advisory `.keys` help line still takes its row. This story compacts only the ends-states box inside the existing short-viewport media query: on ends states only, `#board` is hidden (the final maze position is one tap away again in RUN via retry or advance), the `.keys` help line is hidden, and the end panel stays compact (padding 10, tight margins, no copy change). The retry path is behavior-identical: `#againBtn` keeps its three bindings (LEVELCLEAR advances, LOSE retries the current level with light 15 and bank kept and no count, WIN returns to TITLE) and `retry()`, `advance()`, `backToTitle()` are untouched. Tall phones and desktop keep the ends board. The PR carries the one-line cache rider so returning visitors actually receive the fix.

## Baseline measured at Session 72 planning (Wave 1, 2026-11-25)

| Check | Value |
|---|---|
| Base commit | `12cf383` (main, v0.58.0) |
| Ends defect | ends `scrollHeight` 750 px at 375x667 on LEVELCLEAR/LOSE; `#againBtn` at 487-531 px; page scrolls 83 px past the fold |
| Ends DOM | `#end` inside `#panel` (lines 200-204), `#againBtn` at line 203 |
| RUN panel rule | short-query rule at lines 142-145 collapses `#panel` to zero padding in RUN only; ends gets full panel padding again (the gap this story closes) |
| Ends budget post-fix | about 501 px typical at 375 wide, 516 px worst case at 320 wide (contract 2.2 line items) |
| Cache rider | `website/sw.js` line 21 `CACHE_VERSION` 34 to 35; precache stays 24 entries, every byte identical |
| Viewports for verification | 375x667, 375x600, 320x568 (must-fit), 390x844 (regression: keeps the ends board), real headless Chromium, `scrollY = 0` |

## Functional requirements

FR-1 (contract 2.1, layout 1-3). On ends states only (LEVELCLEAR, WIN, LOSE, all rendering through `#end` with `#title` hidden) at short viewports: `#board` is hidden (`display: none` scoped by `#screen:has(#end:not([hidden]))`); the `.keys` help line is hidden (advisory line; the again button and the result line are the content); the end panel stays compact (padding 10, h2 margin-bottom 4, paragraph margin-top 6, line-height 1.5, button margin-top 8, per lines 138-141, no copy change). Desktop and tall phones keep the ends board. The result strings are unchanged (`Level N clear. Light kept: L.`, `Run complete. Total light: B.`, `Out of moves.`).

FR-2 (contract 2.1, layout 4-5, plus transitions). The HUD keeps all 8 items including the plays line and the next-look readout on ends at every viewport in this story; nothing hidden, nothing dropped. `#againBtn` keeps min-height 44 px and full-width block styling. No input change: the three `#againBtn` bindings, `retry()` (same level, light 15, bank kept, plays unchanged), `advance()`, and `backToTitle()` are behavior-identical; only boxes move.

FR-3 (contract 2.2, budgets and rects). Ends vertical budget at short viewports: BODY_PAD 20 + BACK_LINK 20 + H1 31 + HUD 98 + MSG 30 + END_PANEL 145 + PAD_ROW 162 + BODY_PAD_BOTTOM 10 = 516 px worst case (320 wide, wrapped end line); typical 375 wide budgets END_PANEL 130 (single-line result), ends document about 501 px. Hard ceilings: `documentElement.scrollHeight` at most the viewport height at 375x667, at 375x600, and at 320x568. Rect assertions (`scrollY = 0`, every ends state, all three short viewports): `#againBtn` rect top at least 0 and bottom at most the viewport height, rect height at least 44 px, zero vertical scroll, and horizontal `scrollWidth` at most the viewport width.

FR-4 (contract 2.2 cache rider). `CACHE_VERSION = 35 (34 + 1)`. Precache count stays 24 entries, every byte identical including `./games/lightfare.html` in the list. `git diff main -- website/sw.js` shows exactly one changed line. Any further sw.js diff line is FAIL and blocks the PR. No ms changes: retry timing, reveal timing, and message timing are all unchanged.

FR-5 (contract 2.4 Plan B, ordered). If any ends ceiling fails in measurement with board and keys hidden: first hide the empty `#msg` box on ends states at short viewports (ends always clear it via `setMsg('')`, so hiding saves the full 30 px block with zero content loss). If still failing, shrink pad cells to 44 px on ends states only (saves 12 px, stays at the 44 touch floor). Riven records which step was needed. Never hide a HUD item and never touch the again-button size. Font blowup pushing HUD past 3 rows is covered by slack (about 151 px at 375x667, 84 px at 375x600, 52 px at 320x568); at 320x568 a miss moves to Plan B.

FR-6 (contract 2.3, constants). Ends board hidden at short ends states (fixed); ends keys line hidden at short ends states (fixed); END_PANEL ceiling 145 px asserted not coded; ends doc ceiling equals viewport height (667 / 600 / 568); again-button fold bound (rect bottom at most viewport height, height at least 44 px); HUD items on ends 8 shown 0 hidden; `CACHE_VERSION` 35; precache entries 24 lines byte-identical.

## Acceptance criteria (BDD, observable in product)

Design-owned observable criteria are in contract subsection 2.5; AC-1 through AC-7 map them directly. AC-8 pins the structural scope requirement.

1. Given viewport 375x667 in LEVELCLEAR, when the player arrives at the clear panel, then the page does not scroll and the whole again button (`Next level (Enter)`) is visible above the fold. (design 2.5.1; FR-1, FR-3)
2. Given viewport 375x667 in LOSE, when the player arrives at the game-over panel, then the page does not scroll and the whole retry button is visible above the fold. (design 2.5.2; FR-1, FR-3)
3. Given viewport 375x600 in LEVELCLEAR and in LOSE, when the player arrives, then `scrollHeight` is at most the viewport height and the again button is fully visible with zero scrolling. (design 2.5.3; FR-3)
4. Given viewport 320x568 in LEVELCLEAR and in LOSE, when the player arrives, then the page does not scroll and the again button is fully visible. (design 2.5.4; FR-3)
5. Given an ends panel at any short viewport, when the player presses Enter with nothing focused, then the run continues exactly as before (advance to next level, or retry of the same level with light 15 and bank kept and plays unchanged). (design 2.5.5; FR-2)
6. Given the merged PR diff for `website/sw.js`, when the reviewer inspects it, then exactly the `CACHE_VERSION` line changed from 34 to 35 and all 24 precache entries are byte-identical. (design 2.5.6; FR-4)
7. Given viewport 390x844 in any ends state, when the player arrives, then the board still shows behind the panel as today (tall phone keeps the board). (design 2.5.7; FR-1)
8. Given `git diff main --stat` for this story, when the changed files are listed, then only `website/games/lightfare.html` and `website/sw.js` (one line) changed; zero other files. (scope)

## Out of scope

No new game, no new mechanic, no new storage key, no #265 items, no website redesign. No touch to `retry()`, `advance()`, `backToTitle()`, pricing (`lookPrice`), the refusal line, the LOSE line, any result string, the HUD item set, or the again-button bindings and size. No RUN or TITLE layout change beyond sharing the media query (those are Story 163). No `website/index.html` change (there is no new game card today). No landscape promise (portrait matrix only).

## Non-blocking rule

The cache bump ships regardless. If an ends layout item needs Plan B, the Plan B step ships and the bump still lands in the same PR; a fix that returning visitors never receive because the worker still serves the cached shell is not a fix. #292 closes only when both defects pass live at 375x667 and the short height; if only one lands, Riven ships it and names the other open in the report.

## Defects/risks

- Cached old shell after deploy still scrolls: versioned-out, not a bug; the release wave must verify the served copy over HTTPS with `CACHE_VERSION` 35 live.
- Precache diff noise beyond the version line: separate gate, FAIL, blocks the PR.
- Result line wrapping to 2 lines at 320 wide: budgeted (END_PANEL 145 covers it); still must satisfy doc at most 568.
- Pad tap on ends: silent no-op as shipped (Story 159); no message, no scroll side effect. Keyboard Enter with the again button focused: native single fire, layout independent.
- Verification plan: 3 short viewports times 3 ends states (LEVELCLEAR via L1 clear, LOSE via 80-move exhaust, WIN via full clear path) = 9 sets, plus 390x844 ends regression (LEVELCLEAR and LOSE) = 11 sets; each set records `scrollY` (forced 0), `#againBtn` rect top/bottom/height, `#end` panel height, HUD rows, `scrollHeight` and `scrollWidth`, plus the retry/advance outcome; each set read once live plus the retry-path outcome verified after every LOSE set (Enter reaches RUN with light 15 and unchanged plays): 11 reads, 4 retry confirmations (one per viewport). Pass thresholds per contract 2.6: 9/9 short sets satisfy `scrollHeight` at most viewport height with the again button fully inside; 2/2 regression sets show the board and fit as today; 4/4 retry confirmations behave identically to 12cf383. One miss is FAIL.
