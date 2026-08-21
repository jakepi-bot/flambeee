# Story 016 — Wordfire Hard Mode

**Status:** Stretch goal (Session 10, v0.10.0) — create only if Story 015 lands early
**Author:** Ember + Quinn
**Priority:** Low (stretch, deferrable)
**Assigned to:** Kai (game logic, word list) + Riven (UI/frontend, mode selector)

## Summary

Wordfire gets a Hard mode for players who want a tougher daily word. Where the standard daily word is drawn from the full `WORDFIRE_ANSWERS` list, Hard mode draws from a smaller, harder subset of words (letters that are common in everyday answers show up less, or words with tricky letter patterns — repeated letters, uncommon letters, low-frequency combinations).

The exact design depends on a UX decision (see Open Questions): a difficulty selector in the Wordfire UI, or a global site setting. The session plan leaves this to the team. This story is intentionally smaller than Story 015 and must not block it.

## Business value

- Retention: difficulty tiers give veteran players a reason to come back after they have mastered standard Wordfire
- Consistency with the rest of the catalog: Simon and Minesweeper both have difficulty tiers; Wordfire is the only game without one
- Low effort: the daily-seed and practice-seed machinery already exists; hard mode is a second word pool plus a picker

## Requirements

1. A Hard mode exists for Wordfire with its own word pool, harder than the standard pool (common-letter-weighted: the answers skew toward letters/patterns that are harder to guess).
2. The daily puzzle in Hard mode uses the same UTC-day seeding as standard mode, but from the hard pool (same word for everyone playing Hard that day).
3. Practice mode in Hard mode picks random hard-pool words, no streak impact (same as standard practice).
4. Streak, stats, and guess distribution are isolated between standard and Hard where it matters (a Hard win must not be silently recorded as a standard win unless the team decides to merge them; see Open Questions).
5. The player can choose standard or Hard before starting a round, per the UX decision.

## Acceptance Criteria (BDD)

### Scenario 1: Hard mode is selectable
- **Given** I open Wordfire
- **When** I look for the difficulty control
- **Then** I can choose between Standard and Hard before starting a round

### Scenario 2: Hard daily puzzle is seeded from the hard pool
- **Given** it is a given UTC day
- **When** I play the daily puzzle in Hard mode
- **Then** the answer is the same for everyone playing Hard that day, and is drawn from the hard word pool

### Scenario 3: Hard practice is isolated
- **Given** I play practice mode in Hard
- **When** I win or lose
- **Then** my streak, lifetime stats, and guess distribution are not affected (matching standard practice behavior)

### Scenario 4: Mode choice persists
- **Given** I chose Hard mode
- **When** I reload the page or come back later
- **Then** my mode choice is remembered (localStorage) until I change it

### Scenario 5: Hard pool is actually harder
- **Given** the hard word pool
- **When** I compare it to the standard answer pool
- **Then** the hard pool is a non-empty subset of (or distinct from) the standard answers, with measurably less common letter patterns (e.g. fewer answers with the most common starting letters), and every word in it is a valid 5-letter word in the guess list

### Scenario 6: Stats stay honest
- **Given** I won a Hard daily puzzle
- **When** I look at my stats and share results
- **Then** the win is recorded in a way that does not falsely inflate standard-mode stats or streak, per the decision in Open Questions

## Technical notes (Quinn)

- Wordfire source: `src/wordfire.html`, words in `src/wordfire-words.js` (`WORDFIRE_ANSWERS` ~1432 entries, `WORDFIRE_GUESSES` ~4656).
- Daily seed: `dailyAnswer()` returns `WORDFIRE_ANSWERS[dayIndex() % WORDFIRE_ANSWERS.length]`. Hard mode needs a parallel `WORDFIRE_HARD_ANSWERS` (or a filtered view) plus `dailyHardAnswer()` with the same modulo-seeding on the hard pool length.
- Hard pool construction: either a curated list or a programmatic filter (e.g. exclude answers containing the most common letters like E/A/R/I/O/T in high counts, or weight toward repeated-letter words). Kai picks the mechanism; Scout needs to verify every hard word is in the guess list (otherwise it can never be guessed).
- Streak/stats isolation: standard mode keys (`flambeee-stats-wordfire`, `flambeee-wordfire-streak`, `flambeee-wordfire-distribution`) must not be written by Hard wins unless the team explicitly decides to merge. Either new keys per mode, or a mode field. This needs a decision before implementation (see Open Questions).
- Practice mode today: `practiceAnswer()` picks random answers, no streak impact. Hard practice mirrors that with the hard pool.
- Mode persistence: reuse the localStorage pattern (`flambeee-wordfire-colorblind` is the precedent for a boolean preference key).
- UX decision required: modal difficulty selector on Wordfire (per session plan) vs global site setting. Either way it must be touch-friendly and keyboard-accessible, consistent with the v0.7.0 mobile baseline.
- UI (Riven): the selector must be visible before the first guess, not mid-round, and the current mode should be obvious in the header/legend.

## Open questions

1. **UX: mode selector placement.** Session plan suggests a modal difficulty selector on Wordfire; alternative is a global setting shared across games. Which one? (Ember + Palette + Riven to decide; CEO sign-off if it changes the site.)
2. **Stats/streak isolation.** Do Hard-mode wins share the standard streak and guess distribution, or are they tracked separately? Recommendation: separate per-mode stats, shared or separate streak is the open call. This changes the acceptance criteria for Scenario 6.
3. **Hard pool size.** How many words in the hard pool? Too few makes the daily puzzle repeat weekly. Minimum sensible: same order as standard (hundreds), enough that `dayIndex() % pool.length` does not repeat within a month or two. Kai proposes, Scout verifies.
4. **Hard mode in the daily lockout.** If a player solves the standard daily, can they also play the Hard daily that day? Recommendation: no — one daily puzzle per player per day, mode chosen up front (keeps streak semantics simple).
