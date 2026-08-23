# Test Plan: Story 015 — Website Full Games Page

**Project:** Flambeee Website
**Story:** 015 (Website Full Games Page)
**Analyst:** Scout (QA)

## Overview
This test plan verifies the implementation of the per-game detail view (modal) on the home page. The goal is to ensure that users can learn about the games, see their personal stats from localStorage, and launch the games without friction.

---

## Test Cases

### Scenario 1: Opening a game detail view from the hub
**TC-015-001: Open Detail View**
- **BDD Ref:** Scenario 1
- **Preconditions:** Home page is loaded.
- **Steps:** 
  1. Click on a game card (e.g., Wordfire).
- **Expected Result:** A modal opens showing Game Name, Description, Screenshot, How-to-Play Rules, Stats Summary, and a Play link.
- **Edge Cases:**
  - Clicking the card background vs. the name/image (both should trigger).
  - Rapidly clicking multiple cards.

### Scenario 2: Rules match the real game
**TC-015-002: Wordfire Rules Accuracy**
- **BDD Ref:** Scenario 2
- **Preconditions:** Wordfire detail view is open.
- **Steps:** Read "How to play" section.
- **Expected Result:** Must mention: 5-letter word, 6 tries, green/yellow/gray feedback, UTC-seeded daily word, streak resets on missed day, practice mode doesn't affect streak.
- **Edge Cases:** Ensure no AI tells (em dashes, excessive emojis).

**TC-015-003: Minesweeper Rules Accuracy**
- **BDD Ref:** Scenario 2
- **Preconditions:** Minesweeper detail view is open.
- **Steps:** Read "How to play" section.
- **Expected Result:** Must mention: Clear grid, number hints, flagging (right-click/long-press), Easy/Medium/Hard boards, first click safe.

**TC-015-004: Simon Rules Accuracy**
- **BDD Ref:** Scenario 2
- **Preconditions:** Simon detail view is open.
- **Steps:** Read "How to play" section.
- **Expected Result:** Must mention: Repeat the sequence, difficulty levels.

**TC-015-005: 2048 Rules Accuracy**
- **BDD Ref:** Scenario 2
- **Preconditions:** 2048 detail view is open.
- **Steps:** Read "How to play" section.
- **Expected Result:** Must mention: Merge tiles, reach 2048, Arrow/WASD/Swipe controls, 4x4 and 5x5 boards.

### Scenario 3: Stats summary comes from localStorage
**TC-015-006: Stats Display (Positive)**
- **BDD Ref:** Scenario 3
- **Preconditions:** localStorage contains valid game stats (e.g., `flambeee-stats-wordfire` = `{plays: 10, wins: 5}`).
- **Steps:** Open the corresponding game detail view.
- **Expected Result:** The stats summary displays the correct numbers read from storage.
- **Verification Keys:**
  - Wordfire: `flambeee-stats-wordfire`, `flambeee-wordfire-streak`.
  - Minesweeper: `flambeee-stats-minesweeper` (handle both legacy flat and new nested shapes).
  - Simon: `flambeee-stats-simon`, `flambeee-simon-best` (and difficulty variants).
  - 2048: `flambeee-stats-2048`, `flambeee-2048-best`.

### Scenario 4: Empty state
**TC-015-007: Stats Empty/Corrupt State**
- **BDD Ref:** Scenario 4
- **Preconditions:** localStorage is empty, stats keys are missing, or contain invalid JSON.
- **Steps:** Open any game detail view.
- **Expected Result:** Displays a friendly message (e.g., "Play your first round to see your stats here"). No zeros, no `NaN`, no `undefined`, no crash.
- **Edge Cases:** Private browsing mode (where localStorage might throw errors).

### Scenario 5: Screenshot with alt text
**TC-015-008: Screenshot Assets**
- **BDD Ref:** Scenario 5
- **Preconditions:** Any detail view is open.
- **Steps:** Inspect the screenshot image.
- **Expected Result:** Image src resolves to `assets/game-*.png` and has a non-empty, descriptive `alt` attribute.

### Scenario 6: Play link launches the game
**TC-015-009: Play Link Functionality**
- **BDD Ref:** Scenario 6
- **Preconditions:** Detail view is open.
- **Steps:** Click the "Play" link.
- **Expected Result:** Navigates to `games/<game>.html`. The modal should either close or not block the game execution.
- **Edge Cases:** Ensure relative path is used.

### Scenario 7: Close behavior
**TC-015-010: Close Modal**
- **BDD Ref:** Scenario 7
- **Preconditions:** Detail view is open.
- **Steps:** 
  1. Click the close (X) button.
  2. Press the Escape key.
- **Expected Result:** Modal closes. Page scroll position is preserved.

### Scenario 8: Responsive and accessible
**TC-015-011: Mobile Responsiveness**
- **BDD Ref:** Scenario 8
- **Preconditions:** Viewport width < 720px.
- **Steps:** Open a detail view.
- **Expected Result:** Content stacks vertically. No horizontal scroll. Play link is easily tappable.

**TC-015-012: Keyboard Accessibility**
- **BDD Ref:** Scenario 8
- **Preconditions:** Keyboard focus is on a game card.
- **Steps:** 
  1. Press Enter to open.
  2. Tab through elements.
  3. Press Escape to close.
- **Expected Result:** Focus moves into the modal on open (focus trap), and returns to the triggering card on close. `role="dialog"` and `aria-modal="true"` are present.

### Scenario 9: Accuracy and links
**TC-015-013: Global Integrity Check**
- **BDD Ref:** Scenario 9
- **Preconditions:** All detail views are checked.
- **Steps:** 
  1. Verify all `src` and `href` attributes.
  2. Scan for PII or false claims.
  3. Scan for em dashes (—).
- **Expected Result:** All links work, all images load, zero em dashes, zero PII.
