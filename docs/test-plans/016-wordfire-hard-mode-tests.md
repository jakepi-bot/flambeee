# Test Plan: Story 016 — Wordfire Hard Mode

This document defines the QA test cases for the implementation of Wordfire Hard Mode.

## Overview
Wordfire Hard Mode introduces a second, more difficult word pool for both daily and practice games, with isolated stats and mode persistence.

## Test Scenarios

### Scenario 1: Hard Mode Selectability
**Goal:** Verify the user can toggle between Standard and Hard before starting a round.
- **Test Case 1.1: Visibility**
  - **Action:** Open Wordfire.
  - **Check:** Ensure a Standard/Hard toggle is visible in the header/legend area before the first guess.
- **Test Case 1.2: Toggle Functionality**
  - **Action:** Click the "Hard" button.
  - **Check:** Verify the button becomes active (visually indicated) and the game state updates to Hard mode.
- **Test Case 1.3: Keyboard Accessibility**
  - **Action:** Tab to the mode buttons and use Space/Enter to toggle.
  - **Check:** Verify mode changes correctly via keyboard.
- **Test Case 1.4: Touch Responsiveness**
  - **Action:** Tap the mode buttons on a mobile viewport.
  - **Check:** Verify immediate and accurate mode switching.

### Scenario 2: Hard Daily Seeding
**Goal:** Verify the Hard daily puzzle is deterministic, synchronized across users, and drawn from the hard pool.
- **Test Case 2.1: Deterministic Seeding**
  - **Action:** Start a Hard daily game, note the word (via console or solve). Reload page.
  - **Check:** The answer remains the same for the same UTC day.
- **Test Case 2.2: Hard Pool Source**
  - **Action:** Play Hard daily.
  - **Check:** Verify the answer is a member of `WORDFIRE_HARD_ANSWERS`.
- **Test Case 2.3: Cross-User Sync**
  - **Action:** (Simulated) Compare `dayIndex() % WORDFIRE_HARD_ANSWERS.length` across different environments.
  - **Check:** Results are identical.

### Scenario 3: Hard Practice Isolation
**Goal:** Verify Hard practice does not affect long-term stats or streaks.
- **Test Case 3.1: Win Isolation**
  - **Action:** Select Hard mode $\rightarrow$ Practice $\rightarrow$ Win.
  - **Check:** Verify `flambeee-stats-wordfire` (standard) and `flambeee-wordfire-streak` are unchanged.
- **Test Case 3.2: Loss Isolation**
  - **Action:** Select Hard mode $\rightarrow$ Practice $\rightarrow$ Lose.
  - **Check:** Verify no changes to standard stats or streaks.
- **Test Case 3.3: Distribution Isolation**
  - **Action:** Win a Hard practice game.
  - **Check:** Verify `flambeee-wordfire-distribution` (standard) is unchanged.

### Scenario 4: Mode Persistence
**Goal:** Verify the selected mode survives page reloads.
- **Test Case 4.1: Persistence Check**
  - **Action:** Select Hard mode. Reload page.
  - **Check:** The game starts in Hard mode by default.
- **Test Case 4.2: localStorage Verification**
  - **Action:** Change mode to Hard.
  - **Check:** Verify `localStorage.getItem('flambeee-wordfire-mode') === 'hard'`.

### Scenario 5: Hard Pool Integrity
**Goal:** Verify the hard pool is appropriately difficult and logically valid.
- **Test Case 5.1: Valid Guessability (CRITICAL)**
  - **Action:** Iterate through every word in `WORDFIRE_HARD_ANSWERS`.
  - **Check:** Every word must exist in `WORDFIRE_GUESSES`.
- **Test Case 5.2: Hardness Heuristic**
  - **Action:** Compare `WORDFIRE_HARD_ANSWERS` vs `WORDFIRE_ANSWERS`.
  - **Check:** Hard pool is a non-empty subset/distinct list. (Manual check for "tricky" patterns).

### Scenario 6: Stats Integrity & Isolation
**Goal:** Verify Hard wins use dedicated keys and do not pollute standard stats.
- **Test Case 6.1: Hard Stats Storage**
  - **Action:** Win a Hard daily puzzle.
  - **Check:** Verify `flambeee-stats-wordfire-hard`, `flambeee-wordfire-streak-hard`, and `flambeee-wordfire-distribution-hard` are updated.
- **Test Case 6.2: Standard Stats Protection**
  - **Action:** Win a Hard daily puzzle.
  - **Check:** Verify `flambeee-stats-wordfire` and `flambeee-wordfire-streak` are UNCHANGED.
- **Test Case 6.3: Share Text Accuracy**
  - **Action:** Win a Hard daily. Click Share.
  - **Check:** The shared text must include "Hard" (e.g., "Wordfire Hard 3/6").
- **Test Case 6.4: Distribution Panel Accuracy**
  - **Action:** Toggle to Hard mode.
  - **Check:** The distribution panel shows data from `flambeee-wordfire-distribution-hard`.

## Edge Cases & Boundary Conditions
- **Invalid localStorage:** Manually set `flambeee-wordfire-mode` to "extreme". Verify game defaults to "standard" gracefully.
- **Private Mode:** Play in a browser with `localStorage` disabled. Verify game functions without crashing (using in-memory state).
- **Daily Lockout:** Solve Standard daily. Verify Hard daily is still playable (per requirements: lockout is per-mode).
- **Rapid Toggle:** Switch between Standard and Hard rapidly before first guess. Verify state consistency.
- **Colorblind Mode:** Enable colorblind mode. Verify shapes appear correctly in both Standard and Hard modes.
