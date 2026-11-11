# Story 132: Afterglow small-viewport horizontal overflow (Session 58, P1b, DROPPABLE, Riven)

**Status:** Ready for development (Session 58, 2026-11-11). **DROPPABLE: if not green by 02:30 it ships next session. Nothing about the release depends on it.**
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1b (drop if the window is tight).
**Assigned to:** **Riven**, sole owner. Same owner as Story 130; both land in one PR so the cache bump happens once.
**Base commit:** `f029493`.
**Design contract:** `flambeee-team/design-handoff.md`, Session 58, Section C (Rook; the contract wins on mechanic and input detail).
**Session plan:** `flambeee-team/session-plan.md`, Session 58 (2026-11-11), priorities item 3.
**Tracked by:** Session 58 plan, Story 132. Filed defects: 1 px overflow at 360x640, 21 px at 320x568 (after v0.47.0).

## Summary

On small phones the Afterglow game page is slightly wider than the screen: 1 pixel too wide on one common phone size, 21 on another, so players get a sideways scroll they should never see. This story tightens only the small-screen styling until the page fits, without touching the game itself, the button sizes, or the desktop layout. If the fix is not proven by 02:30 it is abandoned without consequence and the file stays untouched.

## Files

| File | Change | Owner |
|---|---|---|
| `website/games/afterglow.html` | Compaction values only (padding, gaps, margins, font sizes) inside the `@media (max-width: 600px)` block at line 78. | Riven |

The cache bump for this PR is owned by Story 130 (24 to 25, once). If Story 132 is dropped, the bump still happens once for 130.

## Functional requirements

### 1. Layout facts per viewport (C1)

- FR-1. At 320x568: `document.documentElement.scrollWidth <= 320`, no horizontal scrollbar. (Filed 21 px defect gone.)
- FR-2. At 360x640: `scrollWidth <= 360`, no horizontal scrollbar. (Filed 1 px defect gone.)
- FR-3. At 375x667: `scrollWidth <= 375` and the `#plays` line stays visible above the fold (`bottom_of_#plays_px <= 667`, the v0.47.0 result).
- FR-4. At 1280x800: pixel-identical to base (screenshot diff 0 differing px).
- FR-5. Overflow in px: `overflow_px = document.documentElement.scrollWidth - viewportWidth_px`. Pass means `overflow_px <= 0`.

### 2. Frozen values (C3)

- FR-6. Canvas stays 360x360 attribute px (line 108); DOM order stays hud, banner, board, modes, label, controls, stats, plays, hint; button padding stays 10px 18px; play counter logic (`COUNT_KEY`, `COUNT_CAP`, sanitize rules) untouched.
- FR-7. The fix may only adjust compaction values inside the line-78 media query block. Canvas, DOM order, button sizes, and counter logic are frozen.
- FR-8. Measure in CSS px (`scrollWidth` vs viewport width), not device px. Vertical scroll is allowed; only horizontal overflow is measured.

### 3. Edge cases (C4)

- FR-9. Any canvas shrink or DOM reorder fails the story.
- FR-10. Any nonzero desktop screenshot diff at 1280x800 fails the story.
- FR-11. A 375x667 `#plays` fold regression fails the story; path is revert, not a second patch past 02:30.

## BDD acceptance criteria (observable in the product, never by reading source)

- AC-1. Given the page loaded at 320x568, when `scrollWidth` is read, then it is <= 320 with no horizontal scrollbar visible. (D132-O1)
- AC-2. Given the page loaded at 360x640, when `scrollWidth` is read, then it is <= 360 with no horizontal scrollbar visible. (D132-O2)
- AC-3. Given the page loaded at 375x667, when the page is read without scrolling, then `scrollWidth <= 375` and the `#plays` line is visible above the fold. (D132-O3)
- AC-4. Given the page loaded at 1280x800, when screenshotted against the base build, then 0 px differ. (D132-O4)
- AC-5. Given the fixed page at any of the four viewports, when a full run is played (Start through one dark phase), then the canvas is 360x360, buttons respond, and the play counter increments by exactly 1. (D132-O5)

## Required proof

Headless Chromium, device scale factor 1, four viewports, 2 loads each (8 loads). Per load record `scrollWidth`, viewport width, `overflow_px`, and `#plays` bottom offset. Pass: all 8 loads show `overflow_px <= 0`; both 375x667 loads show `#plays` bottom <= 667; desktop screenshot diff 0 px on both loads; zero page errors. One failing load fails the story, and the story is dropped, not patched past 02:30.

## Out of scope

Canvas, DOM order, button sizes, counter logic, any script change, desktop styling, any second file, the cache bump (Story 130 owns it), touch controls, release artifacts, any Afterglow mechanic change.

## Definition of done

8/8 loads green with `overflow_px <= 0`; fold check green on both 375x667 loads; desktop diff 0 px on both loads; AC-5 full-run playthrough recorded; single-file diff inside the line-78 block only; or the story is dropped with the file untouched and this file marked dropped.
