# Story 063: Afterglow daily UTC-seeded mode (Session 29, P5, OPTIONAL / DEFER-FIRST)

**Status:** OPTIONAL. Defer-first. **Written to be deferred unless Wave 3 has room.**
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P5 (optional; not a dependency of the Story 059 mechanic).
**Assigned to:** **Riven** (game file + integration) if it ships; **Kai** on the seed proof.
**Tracked by:** Session 29 plan, Story 063. Depends on Story 059.

## Summary

A daily mode for Afterglow: one level sequence per UTC day, the same for every player, seeded from
the UTC day index the way Wordfire's daily word works. It is on-brand (the daily habit is the
product's proven pull signal) and cheap once Story 059's seeded generator exists.

**It is optional.** The mechanic leads. The session plan names this an optional second story, not a
dependency. If Wave 3 has room it ships; if not, it is deferred explicitly and stated in the
handoff. Nothing else in Session 29 depends on it.

## Requirement (only if it ships)

- A UTC-day-seeded level sequence: `seed = dayIndex` (the same `Math.floor(Date.now() / 86400000)`
  the other games use), so every player sees the same levels that UTC day.
- The existing Story 059 phase machine, grid, budget and input are unchanged. Only the seed source
  differs from a free-play mode.
- Stats: a separate daily record if one is kept, or the same key with a daily sub-record. The key
  must remain `flambeee-afterglow-stats` (or a clearly named daily sibling) and stay empty-state and
  private-mode safe.
- No streak, no lockout, no notification, no push, no account. If a lockout is wanted it is a CEO
  decision and is out of scope here.
- Deterministic and testable exactly as Story 059's generator is: same UTC day, same sequence.

## Acceptance Criteria (only if it ships)

**AC-1.** Given the same UTC day, when two players load the daily mode, then they get the same level
sequence.

**AC-2.** Given UTC midnight passes, when the daily mode reloads, then the sequence advances to the
new day and free-play is unaffected.

**AC-3.** Given a fresh browser, when daily mode loads, then no zeros are shown and nothing crashes.

**AC-4.** Given a store that throws, when daily mode plays, then nothing crashes and no console
error is logged.

**AC-5.** Given the change set, when it lands, then Story 059's free-play mode behaviour is
byte-identical.

## Required Proof (only if it ships)

Extend Story 059's harness with a daily-seed case: the same day index yields the same sequence, a
different day yields a different one. Quote the day indices and the resulting level signatures.

**If deferred:** the deferral is stated in `requirements-handoff.md` and recorded in the roadmap's
Future section. No code, no partial implementation, no stub.

## Decision rule

- **Default: defer.** Ship only if Wave 3 has room after Story 059 and the required verification
  stories.
- **Do not** let this story gate the release, delay Story 059, or pull effort from the proof that
  Story 059 requires.

## Non-Goals

- Streaks, lockouts, reminders, notifications, or accounts.
- Any change to the Story 059 mechanic. The daily mode is a seed source, not a new loop.
- Any CEO-gated item (Story 058, offline accrual, welcome-back suppression).
