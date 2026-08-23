# Test Plan: Story 016 — Wordfire Hard Mode (STRETCH)

**Project:** Flambeee Wordfire
**Story:** 016 (Wordfire Hard Mode)
**Analyst:** Scout (QA)

## Overview
This test plan verifies the implementation of Hard Mode for Wordfire. Key areas include the mode selection UI, the integrity of the hard word pool, seed isolation, and stats persistence.

---

## Test Cases

### Scenario 1: Hard mode is selectable
**TC-016-001: Mode Selection UI**
- **BDD Ref:** Scenario 1
- **Preconditions:** Wordfire is loaded.
- **Steps:** 
  1. Navigate to the round start/selector.
  2. Choose "Hard".
- **Expected Result:** Hard mode is selected and clearly indicated in the UI before the first guess.

### Scenario 2: Hard daily puzzle is seeded from the hard pool
**TC-016-002: Daily Seed Consistency**
- **BDD Ref:** Scenario 2
- **Preconditions:** Hard mode is active.
- **Steps:** 
  1. Open Wordfire on two different devices/browsers on the same UTC day.
  2. Identify the daily answer for Hard mode.
- **Expected Result:** Both devices have the same answer. The answer is drawn from the `WORDFIRE_HARD_ANSWERS` pool.

### Scenario 3: Hard practice is isolated
**TC-016-003: Practice Mode Isolation**
- **BDD Ref:** Scenario 3
- **Preconditions:** Hard mode is active; Practice mode is selected.
- **Steps:** 
  1. Complete a practice round (win or lose).
  2. Check standard streak and lifetime stats.
- **Expected Result:** Standard streak, lifetime stats, and guess distribution remain unchanged.

### Scenario 4: Mode choice persists
**TC-016-004: Preference Persistence**
- **BDD Ref:** Scenario 4
- **Preconditions:** User selects "Hard" mode.
- **Steps:** 
  1. Reload the page.
  2. Close and reopen the browser.
- **Expected Result:** "Hard" mode remains selected via localStorage.

### Scenario 5: Hard pool is actually harder
**TC-016-005: Pool Integrity and Difficulty**
- **BDD Ref:** Scenario 5
- **Preconditions:** Access to `WORDFIRE_HARD_ANSWERS` and `WORDFIRE_GUESSES`.
- **Steps:** 
  1. Verify `WORDFIRE_HARD_ANSWERS` is a non-empty subset/distinct list.
  2. Cross-reference every word in the hard pool against the `WORDFIRE_GUESSES` list.
- **Expected Result:** Every single hard-pool word must exist in the guess list. No "un-guessable" words.

### Scenario 6: Stats stay honest
**TC-016-006: Stats Isolation**
- **BDD Ref:** Scenario 6
- **Preconditions:** Hard mode is active.
- **Steps:** 
  1. Win a Hard daily puzzle.
  2. Inspect localStorage keys for standard Wordfire stats.
- **Expected Result:** The win is recorded in Hard-specific keys (or a mode-field). Standard stats/streaks are not falsely inflated.
