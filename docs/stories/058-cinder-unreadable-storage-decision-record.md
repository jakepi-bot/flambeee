# Story 058: Unreadable Storage Across Both Records (Session 28, P3, Decision Record)

**Status:** Decision record. **No behavior change in this story.**
**Author:** Parent (written directly; see Story 056's author note for why).
**Priority:** P3 (records a decision; ships nothing).
**Assigned to:** **Vigil** to review the compliance surface, then **the CEO** to rule.
**Tracked by:** Session 28 plan, Story 058. Records defect E from the Session 28 harness, and the
same open question Story 055 flagged for the day record.

## Summary

Defect E is the seventh thing the Session 28 harness reproduced, and the only one this session is
**not** fixing. It is worth its own story because it is not a normalization detail. It is a
product decision about what the game should do when it cannot read a player's storage.

The measured behavior, against the real `loadSave()` extracted from `src/cinder.html:827`:

```
DEFECT-E  storage unavailable
  loadSave -> null
  init(): "if (!character) showCharacterCreation()"
```

`loadSave()` wraps its read in a `try`/`catch` that returns `null` on any throw. `init()` at
`src/cinder.html:1517-1535` assigns the result to `character`, and when `character` is falsy it
calls `showCharacterCreation()`. So a player with an unreadable store is shown character
creation, and creating a character overwrites whatever was there.

Nothing is logged, nothing is shown, and the player is given no indication that anything went
wrong. The game looks like it started fresh.

## The scope is both records, not just the character

This was partly found before, and Story 053 recorded it without closing it. The day record has the
same shape of problem:

- `normalizeDayRecord()` (`src/cinder.html:515`) returns `null` for an input that is not an
  object, or whose `dayIndex` is not a finite number.
- `checkDailyReset()` (`src/cinder.html:861`) replaces a stale record wholesale.
- `init()` at `src/cinder.html:1518` assigns `dayState = normalizeDayRecord(loadDayState())`, and
  a `null` day state routes to the same new-game path.

So there are **two** ways to reach "your progress is gone and you were not told":

1. `loadDayState()` throws or returns `null` (blocked storage, private mode, quota).
2. The day record parses but has no finite `dayIndex`, so the normalizer rejects it.

Story 053's decision to return `null` rather than substitute a fresh record was defensible at the
time: refusing to guess is better than inventing a record. But it left the consequence unexamined,
and the consequence is that the player loses progress silently. That gap is what this story exists
to close.

## When this actually happens in practice

This is not an exotic condition:

- **Private/incognito browsing** with storage blocked. Common on iOS Safari and in Firefox.
- **Third-party storage partitioning.** Modern browsers partition localStorage by top-level site.
  A player who played on `flambeee.com` and later visits an embedded or redirected context can
  see an empty store.
- **Quota exhaustion.** Rare for a game this small, but possible on a nearly full origin.
- **A corrupted store.** A half-written value from a killed tab, or a hand-edited save.
- **Site data cleared.** Expected, but it should be distinguishable from a first visit.

The relevant design question is not "can this happen" but "when it does, does the player find
out?" Today the answer is no.

## The options

Presented for Vigil's compliance review and the CEO's ruling. **This story records them. It does
not implement any of them.**

**Option 1: silent new game. (Today's behavior.)**
Zero friction, nothing to design, no user-facing copy. Cost: a returning player is silently
destroyed, and if they had spent real time in Cinder they have no way to know why their hero
vanished. Nothing in this option is defensible except its cost.

**Option 2: a visible notice, play still allowed.**
If storage is unreadable, show something like "Progress cannot be saved in this browser" and let
the player play normally for the session. Preserves zero friction for the player who does not
care, and tells the player who does. Cost: a user-facing message, which is a new surface for the
brand and needs Palette's input as well as the CEO's sign-off. Needs a decision about scope: a
one-line notice, a dismissible banner, or a modal.

**Option 3: refuse to start.**
If storage is unreadable, do not play. Maximum honesty, maximum friction, and it blocks players
in private mode who would happily play a throwaway session. Almost certainly wrong for a game
whose principles are "zero friction" and "no downloads, no accounts, no build steps" (see the
roadmap's Principles section). Recorded for completeness.

### What the decision needs to specify

Whichever option is chosen, it should answer:

1. Does it apply to the character record, the day record, or both? The recommendation is both,
   since both currently route to the same silent path.
2. Is the message shown once per session, once per load, or every load?
3. Does a read-only store differ from an unwritable one? A player who can read but not save is a
   third case, and arguably the most common one.
4. What does Vigil need to see for this to count as a culture-rule pass? Right now there is no
   violation, because nothing is disclosed and nothing is promised. A notice changes that.

## Compliance read (for Vigil to confirm or overrule)

The parent reads this story as **no violation today**, on the grounds that the game currently makes
no promise about persistence that it does not keep, and the failure is a graceful degradation to a
fresh game rather than a false claim. That reading is not free of doubt: silently discarding a
returning player's progress is arguably a truthful-but-unfriendly outcome, and Vigil may read it as
misleading by omission.

**Vigil's ruling is required either way.** This story records the parent's reading as a starting
point, not as a decision.

## Recommendation, for the CEO

Option 2, both records, treated as a small piece of work. It is the only option that keeps the
zero-friction principle while telling the truth, and the cost is a few lines of copy plus a
Palette review. Option 1 is free today and will keep being free until a player complains, which is
the same trade the project has already declined twice.

**This is a recommendation, not a decision. The CEO rules.**

## Non-Goals

- Implementing any option. Story 056 explicitly excludes defect E.
- A save-version field or migration mechanism.
- Changing what a *readable but malformed* record does. Story 056 owns that: it normalizes the
  character record in memory, once, on load.
- Any change to the daily reset or stored quest history.
- Cinder offline accrual and welcome-back suppression, both on the roadmap's Future list and both
  needing CEO sign-off independently.

## Acceptance Criteria

- [ ] This document is merged to `main` as a decision record with **zero** code changes.
- [ ] Vigil has recorded a compliance ruling on the "silent destruction of progress" question.
- [ ] The CEO has ruled on the option, or explicitly deferred it with a reason.
- [ ] Whichever option wins has a follow-up story number recorded here before it is implemented.
- [ ] The roadmap's Future section carries an entry for it if it is deferred rather than done.