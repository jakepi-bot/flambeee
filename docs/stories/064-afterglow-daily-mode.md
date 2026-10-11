# Story 064: Afterglow daily UTC-seeded mode (Session 30, P1, Feature)

**Status:** Ready for development (Session 30, 2026-10-11).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (feature; answers Session 29 log item 1 and CEO directive 6 originality bar for the next build).
**Assigned to:** **Riven** (game file + site integration). **Kai** (seed proof harness).
**Tracked by:** Session 30 plan. Supersedes-deferred Story 063 (`docs/stories/063-afterglow-daily-mode-OPTIONAL.md`); 063 stays as the deferred record and is NOT edited by this story.
**Depends on:** Story 059 (Afterglow mechanic, shipped v0.27.0).

## Summary

One level sequence per UTC day for Afterglow, the same for every player, seeded from the UTC day
index exactly as Wordfire's daily word is (`Math.floor(Date.now() / 86400000)`). The Story 059
phase machine, grid, budget, and input gating are unchanged; only the seed source differs from
free play. The Session 30 plan names this the build-ready original-adjacent slot for the next
build: a second original mechanic has no design on record, this one does (Story 063).

## Context and constraints

- CEO directive 6 (originality over imitation, 2026-10-04) still governs the feature slot. The
  daily mode is a seed source on top of the original Story 059 mechanic, not a reskin and not a
  new loop. It must not change how the lit/dark/reveal phases play.
- Story 063 is the deferred OPTIONAL record. This story promotes it to a build story. Reference
  063 for rationale; all build requirements live here.
- Target release: v0.28.0 (dev wave decides).

## Requirements

### 1. Daily seed source

- Daily mode derives its level sequence from `dayIndex = Math.floor(Date.now() / 86400000)`,
  the same UTC-day index the other daily games use.
- `generateLevel(seed, index)` (Story 059) is called with the day-derived seed. The generator
  itself is unchanged.
- Free-play mode keeps its existing seed behaviour untouched.

### 2. Mechanic freeze

- Lit window, dark window, reveal, move budget, hazard/reset semantics, and input gating
  (input outside the dark phase ignored, not queued) are unchanged from Story 059.
- `darkWindowMs()` (3000ms) behaviour unchanged. Running out of time is still not a failure.
- The `AFTERGLOW-PURE` block stays pure: no DOM, storage, or timer references added.

### 3. Stats and storage

- Stats key remains `flambeee-afterglow-stats` (or a clearly named daily sibling such as
  `flambeee-afterglow-daily-stats`). Daily and free-play records must not clobber each other.
- Empty-state safe (fresh browser shows no zeros, nothing crashes) and private-mode safe
  (a store that throws never crashes the game and logs no console error).

### 4. Non-goals (explicit)

- No streak, no lockout, no reminder, no notification, no push, no account. A lockout is a
  CEO decision and out of scope.
- No CEO-gated item (Story 058 unreadable storage, offline accrual, welcome-back
  suppression).

## BDD scenarios

**Scenario 1: Same UTC day, same sequence.**
Given two players load daily mode on the same UTC day, when each generates the daily
sequence, then both sequences are identical level for level.

**Scenario 2: UTC midnight advances the day.**
Given daily mode loaded before UTC midnight, when the mode reloads after midnight, then the
sequence advances to the new day's sequence and free-play mode is unaffected.

**Scenario 3: Different days differ.**
Given two distinct UTC day indices, when the daily sequences are generated, then the
sequences differ (quoted day indices and level signatures in the proof).

**Scenario 4: Fresh browser empty state.**
Given a fresh browser with no stored stats, when daily mode loads, then no zeros are shown
and nothing crashes.

**Scenario 5: Hostile storage.**
Given a store that throws, when daily mode plays a full level, then nothing crashes and no
console error is logged.

**Scenario 6: Free play untouched.**
Given the merged change set, when free-play mode is exercised against the Story 059
behaviour, then it is byte-identical (generator, phase gate, move resolution, budget,
lit window).

**Scenario 7: Phase gating preserved in daily mode.**
Given daily mode active, when input arrives during the lit phase, then the board does not
move; when input arrives during the dark phase, then it moves; when the dark window
expires, then the board reveals and the next lit phase begins with position and remaining
budget kept.

## Acceptance Criteria

**AC-1.** Same UTC day index yields the same daily level sequence for every player
(Scenarios 1, 3; Kai proof, exit 0, day indices and level signatures quoted).

**AC-2.** Post-midnight reload advances to the new day's sequence; free play unaffected
(Scenario 2).

**AC-3.** Fresh-browser load shows no zeros and crashes nothing (Scenario 4).

**AC-4.** Throwing store plays clean: no crash, no console error (Scenario 5).

**AC-5.** Story 059 free-play behaviour byte-identical after the change set lands
(Scenario 6; frozen-function extraction or equivalent measurement).

**AC-6.** Phase-gating semantics hold in daily mode exactly as in free play (Scenario 7;
real-Chromium check at desktop 1280x800 and mobile 375x667, mirroring the Story 059
9/9 bar).

## Required Proof

- Extend `dev/afterglow-proof.py` (or a clearly named sibling) with a daily-seed case:
  same day index yields the same sequence (deep-equal), a different day yields a
  different one. Quote the day indices and the resulting level signatures.
- Run 1 against the pre-064 tree must show the absence (no daily entry point); run 2
  against the merged candidate must be exit 0. A green run without the failing baseline
  is a claim about the script, not the product.
- Real-browser Playwright check for Scenario 7, both viewports, with input-in-lit,
  input-in-dark, and dark-expiry-reveal cases.

## Ownership (Story 048 protocol)

- **Riven:** `src/afterglow.html` daily entry point + site integration (card/modal copy
  only if the dev wave decides daily needs a surface; otherwise no site change).
- **Kai:** proof harness only, no game-file change outside the pure block extraction.
- Ranges disjoint. PR body must name the exact line ranges against the base commit.

## Open questions for dev wave

1. Does daily mode need a site surface (card note, modal line), or is in-game entry
   enough? Default: in-game only; site copy only if it names the true shipped behaviour.
2. Separate daily stats key vs daily sub-record under the existing key? Either is
   acceptable if the isolation invariant (AC) holds.
