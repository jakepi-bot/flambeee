# Story 118: GAME_ORDER six-vs-seven question (Session 51 fallback, docs only)

**Status:** Ready for development (Session 51, 2026-11-04).
**Author:** Quinn-carried, written by the release wave as Rook's named fallback.
**Priority:** Fallback (no version, no site change, docs only).
**Assigned to:** Release wave (single docs file, no code owner needed).
**Tracked by:** Session 51 plan (fallback, triggered only if Rook's mechanic
fails the reskin gate), requirements-handoff (Story 118 conditional),
design-handoff (fail branch: stop, take Story 118, no hybrid rule).
**Depends on:** Nothing. Touches one new file under `docs/stories/`.

## Summary

Rook's Snapline spine failed its falsifying balance thresholds after the
Plan B numerics were applied (greedy 4/200 vs bar 120, 165/200 seeds more
than 3 loads from snapping at start; release wave's independent re-runs on
the PR head). Per the contract fail branch the spine is rejected and this
fallback triggers instead of a hybrid rule or a v0.44.0 cut. This story
answers the shelved question and nothing else.

## Baseline measured 2026-11-04

| Check | Value |
|---|---|
| `GAME_ORDER` (`website/index.html`) | 6 entries in order: `cinder`, `wordfire`, `minesweeper`, `simon`, `2048`, `afterglow` |
| Hub game cards | 7 (the six above plus Echo Rounds, card only per Story 111) |
| Echo Rounds in rotation or modal | No (Story 111 precedent: card only, no rotation change, no modal entry) |
| Snapline (PR #206) | Open, unmerged; spine rejected, not shipping |

## Requirement

One-line answer, recorded here: GAME_ORDER stays six by standing
precedent (Story 111: catalog listing and rotation membership are separate
product decisions; a card does not earn a rotation slot). Echo Rounds
remains shelf-listed until a rotation-change story says otherwise, and any
future game (including a reworked Snapline) follows the same rule. No code
change, no CACHE bump, no What's New entry, no version cut.

## BDD scenario

**Scenario 1: Deliberate, not stale.**
Given the hub page, when GAME_ORDER is read and the card list is counted,
then GAME_ORDER holds exactly the six existing entries in order and the
Echo Rounds card exists without a rotation slot, which matches the Story
111 precedent and is therefore deliberate.

## Acceptance Criteria

**AC-1.** This file exists under `docs/stories/` and states the one-line
answer verbatim: GAME_ORDER stays six by standing precedent.
**AC-2.** No site, app, game, schedule, noon, checker, or config path shows
a diff from this story. Docs file only.
**AC-3.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Diff showing only the one new file; GAME_ORDER readout (6 of 6 in order);
card count readout. Numbers, not adjectives.

## Non-Goals

- A rotation change, a modal entry, or a seventh slot.
- Any statement about Snapline beyond: PR #206 stays open as the rework
  base; nothing from it merges until a new design clears its thresholds.
- Cutting a version (no release this session per the release wave's cut
  decision and jakebot advisory).
