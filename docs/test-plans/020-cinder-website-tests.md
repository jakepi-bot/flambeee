# Test Plan: Story 020 — Cinder Website Integration

## Objective
Verify Cinder's presence and integration on the Flambeee hub.

## Test Scenarios

### 1. Hub Card
- **Test:** Card visibility.
- **Expected:** Cinder is the 5th card with correct title, desc, image, and Play link.
- **Test:** Layout consistency.
- **Expected:** Matches existing game cards exactly.

### 2. Detail Modal
- **Test:** Modal opening.
- **Expected:** Cinder card opens modal with rules, screenshot, and Play link.
- **Test:** Play link destination.
- **Expected:** Relative path `games/cinder.html` (same-origin).

### 3. Stats Integration
- **Test:** Modal stats (with data).
- **Expected:** Level, Gold, Wins, Deaths correctly read from `flambeee-cinder-save`.
- **Test:** Modal stats (empty state).
- **Expected:** Friendly message, no crash, no zeros if no save exists.

### 4. Global Site Updates
- **Test:** "Games shipped" stat.
- **Expected:** Updated to "5".
- **Test:** "What's New" section.
- **Expected:** v0.13.0 entry present with Cinder announcement.
- **Test:** Regression check.
- **Expected:** Other 4 games' cards and modals are unchanged.
