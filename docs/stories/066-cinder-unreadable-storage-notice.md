# Story 066: Cinder unreadable-storage visible notice (Session 31, P1, Corrective)

**Status:** Ready for development (Session 31, 2026-10-15).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (corrective feature; closes the 4-session Story 058 carry).
**Assigned to:** **Riven** (view/implementation). **Kai** (proof harness). **Vigil** (copy review).
**Tracked by:** Session 31 plan, Story 066. References Story 058
(`docs/stories/058-cinder-unreadable-storage-decision-record.md`); 058 stays as the
decision record and is NOT edited by this story.
**Depends on:** Story 058 (decision record, options analysis). Stories 053/056
(normalization behavior, unchanged by this story).

## Summary

Implement the Session 31 ruling on Story 058: when Cinder storage is unreadable,
show a visible non-blocking one-line notice and let the player play normally for
the session. Both records in scope. Pure presentation: no new persisted field,
no economy change.

## Decision record (jakebot, advisory, recorded)

**Question put to jakebot (Session 31, 2026-10-15 07:24 CDT):** Which Story 058
option for unreadable storage: Option 1 silent new game (today's behavior),
Option 2 visible notice with play still allowed, or Option 3 refuse to start?

**Answer:** **ACCEPT Option 2.** Silent new game wipes a save without telling
the player, which breaks the truthful-accurate standing; refusing to start
breaks zero friction. Visible non-blocking notice keeps both. Notice must state
unreadable as fact, offer no restore, fire at the storage catch not at render,
needs live test on real unreadable-storage path before ship. This ruling closes
the 4-session carry.

**Citation:** `flambeee-team/session-plan.md`, Session 31 (2026-10-15), section
"jakebot decisions (advisory only, recorded)", item 3, session
20261015_072436_2c479b.

## Context and constraints

- Scope is both records (character via `loadSave()`, day via `loadDayState()` /
  `normalizeDayRecord` returning `null`), since both route to the same silent
  new-game path per Story 058.
- `loadSave()` stays the raw reader; `normalizeCharacterRecord()` and
  `normalizeDayRecord()` behavior unchanged. This story adds a notice at the
  storage catch, not a normalization change.
- Copy needs Vigil review (truthful-accurate standing: state unreadable as
  fact, promise nothing) and plain punctuation per the no-AI-tells rule.
- Target release: v0.29.0 (dev wave decides).

## Requirements

### 1. Notice trigger

- Fire at the storage catch (the `try`/`catch` around the store read), not at
  render. Either record unreadable (character or day) triggers it once per
  load.
- Readable-but-malformed records stay owned by Stories 053/056 normalization;
  this story does not change that path.

### 2. Notice shape

- One line, non-blocking. Dismissible or passive; never a modal, never a gate.
- Copy states unreadable as fact (e.g. "Progress cannot be saved in this
  browser"), offers no restore, promises nothing.
- Mobile-safe: no horizontal overflow at 375px, no layout shift of the town hub.

### 3. Session play

- Play allowed for the session after the notice. No economy change, no new
  persisted field, no write on the notice path, stored shape unchanged.

### 4. Non-goals (explicit)

- No save-version field or migration mechanism.
- No change to daily reset, stored quest history, offline accrual, or
  welcome-back suppression.
- No CEO-gated item beyond this ruling.

## BDD scenarios

**Scenario 1: Unreadable character store shows notice, play allowed.**
Given storage throws on the character read, when Cinder loads, then a one-line
non-blocking notice is shown and the player can start a session.

**Scenario 2: Unreadable day store shows notice, play allowed.**
Given storage throws on the day-record read (or the normalizer rejects for a
missing day anchor on the unreadable path), when Cinder loads, then the same
one-line notice is shown and the player can play for the session.

**Scenario 3: Readable store shows nothing new.**
Given a readable store (well-formed or malformed-but-normalizable), when Cinder
loads, then no notice appears and behavior matches the pre-066 build exactly.

**Scenario 4: Notice copy.**
Given the notice is shown, when its text is read, then it states unreadable as
fact, offers no restore, uses plain punctuation, and carries Vigil sign-off.

**Scenario 5: Mobile-safe.**
Given the notice is shown at 375x667, when the town hub renders, then there is
no horizontal overflow and the notice does not block input.

**Scenario 6: No persistence change.**
Given the notice path runs, when the stored keys are compared before and after,
then no new field exists, no write fires from the notice, and the economy is
untouched.

## Acceptance Criteria

**AC-1.** Non-blocking one-line notice when storage unreadable on either record
(Scenarios 1, 2).

**AC-2.** Play allowed for the session after the notice (Scenarios 1, 2).

**AC-3.** Readable-store loads render byte-identical to the pre-066 build;
no notice on the normalizable path (Scenario 3).

**AC-4.** Copy states unreadable as fact, offers no restore, plain punctuation,
Vigil reviewed (Scenario 4).

**AC-5.** Mobile-safe at 375x667: no overflow, no blocked input (Scenario 5).

**AC-6.** No new persisted field, no write on the notice path, no economy
change (Scenario 6).

**AC-7.** Live test on a real unreadable-storage path before ship (real browser
with storage disabled/blocked, e.g. private mode or blocked localStorage; not
a mocked store alone). Real-Chromium check at desktop 1280x800 and mobile
375x667.

## Required Proof

- Kai proof: notice fires at the storage catch on the unreadable path, absent
  on the readable path; run 1 against the pre-066 tree shows the absence (no
  notice), run 2 against the merged candidate exit 0.
- Real-browser Playwright check on a real unreadable-storage configuration
  (both viewports): notice visible, session playable, no console errors.
- No-write check: stored keys byte-identical across the notice path.

## Ownership (Story 048 protocol)

- **Riven:** notice view + trigger wiring in `src/cinder.html`.
- **Kai:** proof harness only, no game-file change outside extraction.
- **Vigil:** copy review before merge.
- Ranges disjoint. PR body must name the exact line ranges against the base
  commit.

## Open questions for dev wave

1. Notice placement (town hub top line vs status row)? Default: least
   disruptive one-liner; Vigil confirms it reads as fact, not alarm.
2. Dismissible vs passive fade? Either acceptable if AC-1/AC-5 hold.
