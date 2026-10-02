# Story 053: Cinder Day-Record Load Normalization (Session 27, P1, Corrective)

**Status:** Ready for development (Session 27, 2026-10-02).
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P1 (corrective; closes the read-path family on the write/load side).
**Assigned to:** **Kai** owns the pure normalization helper and the proof script. **Riven** owns the call-site line in the load path if the fix lands there (the parent names the exact lines before either dev starts, per the Story 048 protocol).
**Tracked by:** Session 27 plan, Story 053. Extends the family of Stories 042, 044, 045, 047 and 050, each of which hardened one read surface against a corrupt or partial day record.

## Summary

Sessions 23 through 26 hardened Cinder's **read** surfaces one at a time so that a corrupt or
partial day record cannot throw and cannot make one screen contradict another:

- `computeQuestLogStreak()` (`src/cinder.html:432`) guards and clamps and returns 0 on bad input.
- `computeRecentQuestEntries()` (`src/cinder.html:495`) filters non-object entries and returns `[]`.
- `computeAwayWindow()` (`src/cinder.html:522`) degrades to "show nothing".
- `dayLabelForIndex()` (`src/cinder.html:664`) preserves a corrupt-input fallback form.
- `checkDailyReset()` (`src/cinder.html:797`) replaces a stale record wholesale and calls
  `ensureQuestState()` for a same-day record that is missing quest state.

The remaining gap is the **load** path itself. `loadDayState()` (`src/cinder.html:778`) does
`JSON.parse` and returns whatever it gets: a value of any shape, or `null`. It does **not** ensure
the parsed value matches the documented day-record shape
`{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }`. `ensureQuestState()`
(`src/cinder.html:244-263`) patches only `quest` and `completedQuests`, and only when it is called.

So today the record's shape integrity is enforced **piecemeal by each reader**, and only for the
fields each reader happens to touch. `dayIndex` is never normalized: `checkDailyReset()` compares
`dayState.dayIndex !== today` and, on a match, keeps a record whose `dayIndex` may be a string, a
float, `NaN`, or absent. `fightsUsed` and `innHealsUsed` are never bounded at load: the counters
are only clamped at the point of use (`src/cinder.html:862`, `:982`, `:1067`, `:1380`), so a
hand-edited or truncated record can reach a reader with a negative or absurd count. The read
helpers each survive on their own, but the record they read is never validated once.

This is the same family, seen from the other end: the screens were taught to tolerate a bad record,
but the record is never checked. Story 053 normalizes the record **once, on load, in memory**, so
every reader reads the documented shape and no reader owns a private guard for a shared problem.

## Business value

- One place owns record integrity. Today each reader carries its own defensive guard; a future
  reader that forgets one reintroduces the exact defect class Sessions 23-26 spent four sessions
  closing.
- The empty-state and fallback behavior the team has proven for read surfaces becomes a property of
  the **record**, not of each screen, so the proofs stay valid as screens are added.
- Cheap: one pure helper, called once, proven by a pure-function script. No new persisted field,
  no write, no shape change, no migration.
- Grounded in a real failure class already observed: a record written by an older build, a record
  truncated mid-write, or a hand-edited record reaches the render paths today.

## User Story

As a Cinder player whose saved day record was written by an older build, truncated mid-write, or
edited by hand,
I want the game to normalize the record once on load into the documented shape,
So that every screen renders the existing empty state or fallback instead of throwing, showing a
negative count, or letting one screen describe a different record than another.

## Requirements

### 1. Normalize once on load, in memory

- Add a pure normalization helper, `normalizeDayRecord(raw)`, near the other record helpers (the
  exact insertion point is named by the parent before dev starts, per Story 048).
- The helper returns either a valid normalized record or `null` (the caller keeps its existing
  `!dayState` behavior for `null`).
- The helper takes an arbitrary parsed value and returns a record whose shape is exactly
  `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }`.
- Call it once from the load path, immediately after `loadDayState()` and before
  `checkDailyReset()` runs (the record must be normalized before the reset compares `dayIndex`).
- The helper is pure: no reads or writes of `localStorage`, no mutation of its argument, no global
  mutation, no new persisted field.

### 2. Field rules (documented shape)

- `dayIndex`: a finite number. A non-number, `NaN`, or infinite value is rejected; if the whole
  record cannot yield a usable `dayIndex`, the helper returns `null`. A finite number is passed
  through unchanged.
- `fightsUsed`, `innHealsUsed`: integers clamped to `[0, MAX_FIGHTS_PER_DAY]` and
  `[0, MAX_INN_HEALS_PER_DAY]` respectively. A non-number, `NaN`, negative, or fractional value
  normalizes to a safe value (`0` for non-numeric/NaN/negative; `Math.floor` for fractional), and
  an over-max value clamps to the max.
- `quest`: the documented `{ progress, completed, rewarded }` object. If missing or malformed, use
  the value `ensureQuestState()` already produces (`{ progress: 0, completed: false, rewarded: false }`).
  If present, keep the object; do not add fields.
- `completedQuests`: an array. A missing or non-array value normalizes to `[]`. If it is an array,
  keep only entries that are objects (the same filter `computeRecentQuestEntries()` applies); a null
  or non-object entry is dropped. Within kept entries, do not invent fields; a missing or
  non-numeric `dayIndex` on an entry may be left as-is (the read helpers already guard it), or
  dropped, whichever the parent names as the single rule before dev starts.

### 3. No behavior change for a valid record

- For a record that already matches the documented shape exactly, `normalizeDayRecord()` returns a
  field-by-field equal record. Every screen renders exactly as it does in v0.24.0.
- No regression on the same-day reload, next-day return, or long-absence flows.

### 4. No write, no stored shape change, no migration

- Nothing is written back to storage by the normalization. `saveDayState()` is not called from the
  helper or from the load-normalization step. Both localStorage keys are byte-identical across a
  load-and-render cycle, including with a corrupt input.
- The stored day-record shape is unchanged. No new persisted field.

### 5. Frozen functions (binding)

The fix must not be achieved by editing a read helper. These stay **byte-identical to v0.24.0**,
proven by extraction:

```
checkDailyReset()                 src/cinder.html:797
computeQuestLogStreak()           src/cinder.html:432
computeRecentQuestEntries()       src/cinder.html:495
shouldShowWelcomeBack()           src/cinder.html:615
dayLabelForIndex()                src/cinder.html:664
```

### 6. Escalation rule

If the only correct fix requires a persisted field or a change to the stored shape, that is a Story
039 decision-record amendment plus CEO sign-off. Escalate; do not implement.

## Acceptance Criteria (Given/When/Then)

**Scenario 1: null or non-numeric day index**
- Given a stored record whose `dayIndex` is absent, null, a string, or `NaN`,
- When the game loads,
- Then `normalizeDayRecord()` returns `null` (or a record with no usable index), the existing
  `!dayState` path runs, and no read surface throws; the existing empty state renders.

**Scenario 2: missing or non-array completedQuests**
- Given a stored record missing `completedQuests` or with it set to a non-array,
- When the game loads,
- Then the normalized record carries `[]` (or the filtered array) and the quest log renders its
  empty-state line `"No quests recorded yet. Finish today's quest to start your log."` unchanged,
  and the streak number reads 0.

**Scenario 3: out-of-range or wrong-type counters**
- Given a stored record with `fightsUsed` or `innHealsUsed` set to a negative, fractional, `NaN`, or
  over-max value,
- When the game loads,
- Then each counter is clamped to the documented range and no surface renders a negative or
  over-max count.

**Scenario 4: valid record (control, no regression)**
- Given a valid v0.24.0 record,
- When the game loads,
- Then the normalized record equals the parsed record field by field, and every read surface
  (quest log number, quest log list, quest-log labels, welcome-back panel) renders exactly as
  v0.24.0.

**Scenario 5: corrupt entries in an otherwise valid array**
- Given a `completedQuests` array containing a null and a non-object entry,
- When the game loads and the quest log opens,
- Then the non-object entries are skipped, the remaining entries render, and the render does not
  throw.

**Scenario 6: no write**
- Given any of the inputs above,
- When the game loads and renders,
- Then both localStorage keys are byte-identical before and after, and `saveDayState()` is not
  called by the normalization.

**Scenario 7: frozen functions**
- Given the merged change,
- When the five frozen functions are extracted from the candidate and from tagged v0.24.0,
- Then they are byte-identical.

## Required Proof

- **Pure-function proof script:** `src/kai-story053-record-normalize-proof.py`, following Kai's
  established pattern (extract the helper, run it against a matrix of inputs).
- Input matrix: null record; missing `dayIndex`; string `dayIndex`; `NaN` `dayIndex`; valid
  `dayIndex`; missing `completedQuests`; `completedQuests` as a string; `completedQuests` containing
  null and non-object entries; negative / fractional / `NaN` / over-max counters; a fully valid
  record.
- The script asserts the normalized shape for each case, asserts the valid case is field-by-field
  unchanged, and asserts a load-and-render cycle writes nothing.
- **The script must fail against shipped v0.24.0** for at least the throwing/corrupt cases (to
  isolate that a real defect existed), and pass against the merged candidate.
- **Real-browser isolation:** the pre-fix build must throw or render a bad count for at least one
  corrupt input in real Chromium; Scout records the before/after.
- Scout re-runs the proof against the merged candidate.

## Non-Goals (out of scope for this story)

- No new persisted field, no stored-shape change, no migration.
- No change to `checkDailyReset()`, the reset semantics, or the stored history.
- No offline accrual, no cross-day streak mechanic, no welcome-back suppression change (all blocked
  on the Story 039 amendment plus CEO sign-off).
- No UI or copy redesign. No new feature.
- No touching `jobs/`, `jobs-refactor-team/`, `jakebot/`, or any cron configuration.
