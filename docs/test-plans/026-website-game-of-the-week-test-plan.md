# Test Plan: 026 - Website Game of the Week (v0.15.0)

**Story:** `docs/stories/026-website-game-of-the-week.md`
**Priority:** P1 (brand surface)
**QA analyst:** Scout
**Date:** 2026-09-06
**QA bar (Session 14):** Real browser click on the card is mandatory; mobile render checked on a narrow viewport, not merely claimed.

## Goal

Verify flambeee.com highlights exactly one of the five games per deterministic ISO week, with a relative play link to `games/<name>.html`, no mobile layout break, graceful degradation when the featured reference is missing/invalid, and on-brand visuals with real clickable links. The live file and repo mirror must be byte-identical.

## Test Environment

- **Live (ABSOLUTE path, outside repo):** `/home/jake/.openclaw/workspace/share/Flambeee/index.html`
- **Repo mirror (must be byte-identical):** `/home/jake/.openclaw/workspace/flambeee/website/index.html`
- **Game assets:** `/home/jake/.openclaw/workspace/share/Flambeee/games/<wordfire|minesweeper|simon|2048|cinder>.html`
- **Tooling:** Playwright (Chromium) via `/home/jake/.openclaw/workspace/.venv/bin/python3`
- **Viewports:** Desktop 1280x800; Mobile 375x812 and 390x844 (`has_touch: true`, `is_mobile: true`)
- **Automation note:** Rotation is keyed to ISO week (`YYYY-Www`, from current UTC date, Monday boundary). For boundary tests freeze `Date.now`.

## BDD Scenario Verification

| # | Scenario | Method (REAL input) | Success Criterion |
| :--- | :--- | :--- | :--- |
| 1 | One game featured per ISO week | Load the live page; read the featured game. Load in a second profile/session. | Exactly one Game of the Week shown; the SAME game for any visitor that week. |
| 2 | Featured game matches the deterministic rule | Compute the ISO-week rotation output in the harness; compare to the rendered card. | They match; verify the rule's next value differs at the next ISO-week boundary and all five games are reachable over five weeks. |
| 3 | Card links to the featured game | Real `page.click()` on the card's Play link. | Navigates to relative `games/<name>.html`; the game loads and is playable with same-origin localStorage stats readable. |
| 4 | Mobile renders without layout break | Mobile viewport with the card present. | No horizontal overflow (`document.scrollWidth <= viewport width`), card fully visible + tappable, no new scroll/jump issue, grid unchanged. |
| 5 | Missing/invalid featured game degrades gracefully | Point the rotation at a non-existent slug (or delete the asset in a throwaway copy); load the page. | Card hidden or unobtrusive; rest of site functions; no unhandled error and no console break. |
| 6 | On-brand visuals | Inspect the card against the brand palette and typography; click-test any link. | Navy `#1a1a2e` + flame `#e94560`/`#ff5a75` fit; every external-facing link is a real clickable link (not bare text), per the Palette UX directive. |

## Edge Cases & Boundary Conditions

- **ISO week boundary flip:** Freeze the clock on the last day of a week and then one day later (next week). Verify the featured game flips exactly at the Monday boundary.
- **All-five rotation:** Step the week forward across five ISO weeks; assert each of the five games (wordfire, minesweeper, simon, 2048, cinder) appears exactly once before repetition.
- **Same-origin stats:** After clicking through to the featured game, set a localStorage value on the origin, reload the game, and confirm it persists (same-origin read) — proves relative link, not an external/cross-origin jump.
- **Missing asset (graceful):** Featured slug that has no `games/*.html` file present. Load page -> card must not throw; site must render normally; console must be clean.
- **Mobile no-horizontal-scroll:** Assert `document.documentElement.scrollWidth <= innerWidth` on 375px and 390px; assert the Play button is at least 44x44px (touch target) and not overlapped.
- **Touch target / tap:** Real `page.tap()` on the mobile Play button must navigate (not just a hover).
- **Grid non-regression:** The existing "Pick your poison" grid (5 cards + detail modals) must be unchanged in count and links.
- **Both copies byte-identical:** `cmp share/Flambeee/index.html flambeee/website/index.html` exit 0.
- **No service-worker / manifest change:** diff against v0.14.0 for sw.js/manifest; none should be touched by this story.
- **Contrast/accessibility:** card text readable on navy; the link is visually and semantically a link; no bare-text URLs.

## Defect Reporting Format

Any failure recorded as: severity (Blocker / Major / Minor / Cosmetic), steps to reproduce, expected vs actual, environment (viewport, storage state), and attached console output. QA verifies and reports; QA does not fix.