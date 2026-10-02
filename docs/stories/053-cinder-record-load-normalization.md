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

## Hypothesis check (Quinn, evidence)

The session plan's hypothesis is **confirmed**, and the code read turns it from a plausible class
into two **reproduced defects**. Both were executed against the shipped v0.24.0 logic before this
story was written. Neither is inside a frozen helper.

**Defect 1 (the headline, and a hard throw): a wrong-typed quest title reaches `escapeHtml()` and
throws.** `computeRecentQuestEntries()` (`src/cinder.html:495-511`) filters entries by
`entry && typeof entry === 'object'`. It does **not** check that `entry.objective` or `entry.label`
is a string. `renderQuestLog()` (`src/cinder.html:706`) then calls
`escapeHtml(entry.objective || entry.label || '')`, and `escapeHtml()` (`src/cinder.html:886-888`)
calls `str.replace(...)`. A stored entry whose `objective` is a number reaches that call as a
number and throws. Reproduced against v0.24.0 logic: `TypeError: str.replace is not a function`.
The string control case renders normally.

This defect is **reachable and persistent**, which is what makes it worth the session. Verified:

- The record survives the load path. `checkDailyReset()` (`src/cinder.html:797-807`) rebuilds the
  record **only when** `!dayState || dayState.dayIndex !== today`. A record stamped **today**
  takes the `else` branch, which calls `ensureQuestState()` (`src/cinder.html:249-259`). That
  helper patches only `quest` and `completedQuests`; it does not touch entry contents. Reproduced:
  a same-day record with a numeric `objective` reaches the quest-log render intact, **0 writes on
  the load path**, and the throw happens at render.
- The anchor is an **alias**, not a copy. `init()` (`src/cinder.html:1454-1466`) sets
  `const rawDayState = dayState` and `questLogAnchor = rawDayState`, then calls `checkDailyReset()`.
  On the same-day branch the reset does not reassign `dayState`, so `questLogAnchor === dayState`
  and the corrupted entry is what every read surface sees. Reproduced: `anchor === dayState` is
  `true`.
- It throws **inside the player's quest log**, on a screen reachable from town-hub row 9. That is
  the "recent quests" view a returning player opens to check their history.

Note the constraint this creates, which is why the requirement below places the fix in the
normalizer and **not** in the render path: the throw site is `renderQuestLog()` line 706, which is
**not** a frozen function, so the fix is available without touching the frozen set.

**Defect 2: out-of-range daily counters render a negative or inflated count.** `fightsUsed` and
`innHealsUsed` are never bounded at load. `renderStatus()` (`src/cinder.html:862`) computes
`MAX_FIGHTS_PER_DAY - dayState.fightsUsed` with no guard. Reproduced against v0.24.0 logic: a
stored `fightsUsed` of `99` renders **`Fights: -84`** on the status line. A stored `fightsUsed` of
`-5` renders **`Fights: 20`**, which is more than the daily maximum of 15.

Two honest limits on defect 2, recorded so the story is not oversold:

- The **gameplay** guard is fine in both directions. `enterWilderness()`
  (`src/cinder.html:1067`) blocks on `dayState.fightsUsed >= MAX_FIGHTS_PER_DAY`, so an inflated
  counter locks the player out of the wilderness for the day, and a negative counter does not
  grant extra fights through that gate. Reproduced: `99` blocks, `-5` does not block.
- So defect 2 is a **display and progression-state** defect, not an economy exploit. The status
  line lies, and the counters that gate progression are wrong. It is still in scope: the whole
  point of the load path is that a record should not reach a reader in a shape no reader expects.

**Sharpening, not correction:** the plan frames this as "whatever `JSON.parse` returns is handed to
the render paths." That is accurate. The added precision is that the readers' guards are
**field-level**, not **entry-level**: every one of them checks the container (`is an array`, `is an
object`, `is a finite number`) and none checks the leaf. `completedQuests` entries are the only
place in the record where the team stores free-form data written from game state
(`completeQuest()`, `src/cinder.html:321-325`), so they are also the most likely place for a
hand-edited or foreign-written record to carry a wrong-typed leaf. That is why requirement 2
normalizes the entry leaves and not just the array.

### Code read facts (Quinn, Session 27 Wave 2, verified against tagged v0.24.0)

The load path does no shape validation at all:

- `loadDayState()` (`src/cinder.html:778-785`) is `try { JSON.parse(data) } catch { return null }`.
  The parsed value is returned as-is, whatever its shape.
- `init()` (`src/cinder.html:1452-1468`) does `dayState = loadDayState()`, then
  `const rawDayState = dayState`, then `awayWindow = computeAwayWindow(rawDayState, getDayIndex())`,
  then `questLogAnchor = rawDayState`, then `checkDailyReset()`, then `ensureQuestState()`.
- `checkDailyReset()` (`src/cinder.html:797-807`) branches on `dayState.dayIndex !== today`.
- `ensureQuestState()` (`src/cinder.html:249-259`) patches only `quest` and `completedQuests`.

Three sharpenings the plan does not state, each load-bearing for how the fix is written:

1. **A corrupt `dayIndex` is already safe by accident; the counters and the entry leaves are not.**
   The reset's comparison is strict `!==`, so a string, `NaN`, `null` or absent index compares
   unequal and the record is rebuilt wholesale. The `dayIndex` half of this story is therefore
   hardening, not a live defect, and the story says so rather than inflating it. `fightsUsed` and
   `innHealsUsed` have **no** such guard: they are only ever read by subtraction at four sites,
   `renderStatus()` (`:862`), `renderInn()` (`:982`), `enterWilderness()` (`:1067`, a `>=` guard)
   and `handleInnInput()` (`:1380`). None clamps. That is defect 2 above. The entry leaves are
   defect 1 above, and they are the sharper half of the hole.
2. **The read guards are field-level, never entry-level.** Every guard in the family checks a
   container (`Array.isArray`, `typeof === 'object'`, `isFinite`) and none checks a leaf value.
   `completedQuests` entries are the only free-form data in the record, written from game state at
   `completeQuest()` (`src/cinder.html:321-325`), which makes them both the likely site of a
   hand-edited or foreign-written wrong-typed leaf and the place a future reader will forget to
   guard. Hence requirement 2 normalizes entry leaves, not just the array.
3. **`rawDayState` and `questLogAnchor` are the same object reference as `dayState`, captured
   before the reset rebinds it.** `checkDailyReset()` reassigns `dayState` to a fresh object rather
   than mutating, which is what preserves the pre-reset anchors. On the **same-day** branch it does
   not reassign at all, so all three names alias one object. Therefore normalization must run
   **before** the anchor capture, and the normalized object must be the single value assigned to
   `dayState`, `rawDayState` and `questLogAnchor`. If normalization were applied only to `dayState`
   after the anchors were captured, the anchors would still hold the un-normalized parse and every
   read surface would keep its old input. This is a correctness requirement on call-site placement,
   not a style preference; it is bound in requirement 1 and proven by Scenario 3b.

### Corrected shape of the session plan's hypothesis

The plan says the load path "has no equivalent normalization" and asks for the record to be
"normalized once on load". That is confirmed. What the plan does not say, and what this code read
changes about the story's shape, is that there is **one throw defect and one arithmetic defect**,
not one undifferentiated hardening class. The throw is the priority (Scenario 1a); the counter
clamp is the second (Scenario 3). Neither is reachable through a frozen function, so the frozen-set
rule costs this story nothing.

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
- Call it once from the load path. Placement is binding, for the reason given in the code read above:
  the normalized object must be the one value assigned to `dayState`, `rawDayState` **and**
  `questLogAnchor` in `init()` (`src/cinder.html:1452-1468`). It must therefore run after
  `loadDayState()` returns and **before** the anchor capture, which in turn is before
  `checkDailyReset()` (the reset compares `dayIndex`, so the record must be normalized before that
  comparison, and the anchors must hold the normalized record or the fix does nothing).
- The helper is pure: no reads or writes of `localStorage`, no mutation of its argument, no global
  mutation, no new persisted field.
- The helper must not depend on `MAX_FIGHTS_PER_DAY` / `MAX_INN_HEALS_PER_DAY` being readable at
  definition time in a way that breaks the existing pure-extraction proof pattern; the bounds are
  either referenced at call time or inlined as literals with the constants' values
  (`15` and `3`, `src/cinder.html:68-69`) and a comment naming the source. Kai names which in the
  PR body.

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
  or non-object entry is dropped.
- **Entry leaves (this is the reproduced throw).** For each kept entry, `objective` and `label`
  must normalize to a **string**. A non-string, `null`, `undefined`, or missing leaf becomes `''`.
  This rule is what prevents the `TypeError` at `src/cinder.html:706`. A record written by the game
  always has string leaves, so this normalization is a no-op for every legitimate record.
  It must be applied on the **load path**, not at the render call site: do not add a `String(...)`
  wrap, a `typeof` check, or a try/catch inside `renderQuestLog()` or `escapeHtml()`. The record is
  the thing that is malformed, so the record is where it is repaired, once.
- An entry's `dayIndex` may be left as-is (the read helpers already guard it) or dropped, whichever
  the parent names as the single rule before dev starts. Do not invent entry fields.

### 2b. What the normalizer must not do

- It must not repair the record by **writing**: no `saveDayState()`, no backfill, no migration of
  the stored value. A corrupt record stays corrupt on disk and is repaired in memory on every load.
- It must not drop a legitimately completed quest. For a well-formed history the normalized
  `completedQuests` array is element-for-element equal to the input, in the same order.
- It must not change what a **valid** record renders (requirement 3).

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

**Scenario 1a: a wrong-typed quest title does not throw in the quest log (P1, the headline defect)**
- Given a stored record stamped for today whose `completedQuests` holds an entry whose `objective`
  is a number rather than a string,
- When the game loads and the player opens the Quest Log (town-hub row 9),
- Then the quest log renders without an exception, the offending entry shows its label (or the
  empty title) rather than crashing the view, and no `TypeError` appears in the console.
- Against shipped v0.24.0 this scenario fails: the render throws
  `TypeError: str.replace is not a function` at `src/cinder.html:706`. Scout records the before
  render in real Chromium and the after render.

**Scenario 1b: a wrong-typed title on a stale record, through the anchors**
- Given the same entry shape in a record stamped for a **previous** day,
- When the game loads and the player opens the Quest Log,
- Then the list, the streak number and the day labels all render from the normalized record and
- no read surface throws. (On a stale day the reset rebuilds `dayState`, so this case exercises the
  path where the anchors and the live record differ; Scenario 1a exercises the same-day alias
  case. Both are in the proof matrix.)

**Scenario 2: null or non-numeric day index**
- Given a stored record whose `dayIndex` is absent, null, a string, or `NaN`,
- When the game loads,
- Then `normalizeDayRecord()` returns `null` (or a record with no usable index), the existing
  `!dayState` path runs, and no read surface throws; the existing empty state renders.
  (Record honestly: against v0.24.0 this path is already safe by accident, because the reset's
  strict `!==` rebuilds the record. This scenario is hardening, not a fix.)

**Scenario 3: missing or non-array completedQuests**
- Given a stored record missing `completedQuests` or with it set to a non-array,
- When the game loads,
- Then the normalized record carries `[]` (or the filtered array) and the quest log renders its
  empty-state line `"No quests recorded yet. Finish today's quest to start your log."` unchanged,
  and the streak number reads 0.

**Scenario 4: out-of-range or wrong-type counters (defect 2)**
- Given a stored record with `fightsUsed` or `innHealsUsed` set to a negative, fractional, `NaN`, or
  over-max value,
- When the game loads and the town hub renders,
- Then each counter is clamped to the documented range, the status line shows a fights-left value
  within `[0, 15]` and the inn shows a heals-left value within `[0, 3]`, and no surface renders a
  negative or over-max count.
- Against shipped v0.24.0 the two seeds Scout records are: `fightsUsed: 99` renders
  **`Fights: -84`**, and `fightsUsed: -5` renders **`Fights: 20`** on a game capped at 15. Those
  are the before values; the after values are within `[0, 15]`.

**Scenario 5: normalized record is the one the anchors read**
- Given a stored record with a corrupt `completedQuests` (non-array) and an out-of-range
  `fightsUsed`,
- When the game loads and the quest log opens,
- Then the streak, the recent-quests list and the day labels were all computed from the normalized
  record, not from the raw parse. Proven by showing that a record whose raw parse holds
  `completedQuests: "not-an-array"` and `fightsUsed: -3` produces the empty-state log line and a
  fights-left of 15, which is only reachable if the anchors hold the normalized value.

**Scenario 6: valid record (control, no regression)**
- Given a valid v0.24.0 record,
- When the game loads,
- Then the normalized record equals the parsed record field by field, and every read surface
  (quest log number, quest log list, quest-log labels, welcome-back panel) renders exactly as
  v0.24.0.

**Scenario 7: corrupt entries in an otherwise valid array**
- Given a `completedQuests` array containing a null and a non-object entry,
- When the game loads and the quest log opens,
- Then the non-object entries are skipped, the remaining entries render, and the render does not
  throw.

**Scenario 8: no write**
- Given any of the inputs above,
- When the game loads and renders,
- Then both localStorage keys are byte-identical before and after, and `saveDayState()` is not
  called by the normalization.

**Scenario 9: frozen functions**
- Given the merged change,
- When the five frozen functions are extracted from the candidate and from tagged v0.24.0,
- Then they are byte-identical.

## Required Proof

- **Pure-function proof script:** `src/kai-story053-record-normalize-proof.py`, following Kai's
  established pattern (extract the helper, run it against a matrix of inputs). Exit 0 on the
  candidate.
- **Input matrix (every case below is a named seed in the script):**
  - `null` record; record with no `dayIndex`; string `dayIndex`; `NaN` `dayIndex`; `Infinity`
    `dayIndex`; valid `dayIndex` (control).
  - `completedQuests` missing; `completedQuests` a string; `completedQuests` an object;
    `completedQuests` containing `null`, a number, and a string entry.
  - **wrong-typed entry leaves:** an entry whose `objective` is a number (the reproduced throw),
    whose `label` is a number, whose `objective` is `null`, and whose `objective` is missing.
    Both same-day and stale-day record stamps.
  - counters: negative, fractional, `NaN`, over-max, non-numeric, for both `fightsUsed` and
    `innHealsUsed`.
  - `quest` missing; `quest` a string; `quest` well-formed.
  - a fully valid record (the control that must be field-by-field unchanged).
- **Render assertion, not just shape assertion.** For the wrong-typed-leaf seeds the script must
  drive the real render expression (`escapeHtml(entry.objective || entry.label || '')`) on the
  normalized entries and assert it returns a string and does not throw. A shape-only assertion
  would pass on a fix that normalized the record but left a leaf that still breaks the view, so the
  render assertion is binding.
- **The script must FAIL against shipped v0.24.0.** This is the pattern Kai has used since Story
  047: a green proof that also passes against the unfixed build is a tautology, not a measurement.
  At minimum these seeds must fail on v0.24.0 and pass on the candidate:
  - wrong-typed `objective` leaf (throws `TypeError` on v0.24.0),
  - `fightsUsed: 99` (renders `Fights: -84` on v0.24.0),
  - `fightsUsed: -5` (renders `Fights: 20` on v0.24.0).
  Kai records the v0.24.0 failure output alongside the candidate run, so the isolation is
  auditable and not asserted.
- **Call-site placement proof.** The script must also demonstrate Scenario 5, that the anchors read
  the normalized record. This is the requirement most likely to be implemented wrong while still
  passing every field-shape assertion (normalize `dayState` after the anchors are captured and
  every field assertion still passes), so it gets an explicit case rather than a comment.
- **Frozen-function extraction.** The five frozen functions byte-identical to tagged v0.24.0, shown
  by extraction against `git show v0.24.0:src/cinder.html`, not by inspection of the diff.
- **No-write proof.** Both localStorage keys byte-identical across a load-and-render cycle with a
  corrupt input, plus a static scan showing the helper and the load-path call site contain no
  `saveDayState`, `localStorage.setItem`, or `saveCharacter`.
- **Real-browser isolation (Scout):** real Chromium, the quest log opened at desktop and 375x667,
  on a record seeded with a numeric `objective`. The v0.24.0 build must be shown **throwing** with
  the console error captured; the merged candidate must render. Scout records both, and re-runs
  Kai's proof against the merged candidate, not against the dev branch.

## Non-Goals (out of scope for this story)

- No new persisted field, no stored-shape change, no migration, no backfill write.
- No change to `checkDailyReset()`, the reset semantics, or the stored history.
- No change to `escapeHtml()` or `renderQuestLog()`. The record is repaired, not the renderer.
  If the fix is achieved by guarding the render path instead of the load path, it is out of scope
  and must be re-cut.
- No change to the character save (`flambeee-cinder-save`). This story normalizes the day record
  only. A corrupt character save is a separate story.
- No offline accrual, no cross-day streak mechanic, no welcome-back suppression change (all blocked
  on the Story 039 amendment plus CEO sign-off).
- No UI or copy redesign. No new feature. No economy or balance change: clamping a corrupt counter
  restores the documented cap, it does not change the cap.
- No notification, push, permission prompt, or install nag.
- No touching `jobs/`, `jobs-refactor-team/`, `jakebot/`, or any cron configuration.

## Open questions / ambiguities (need CEO input)

None that block development. The one judgement call inside the story is the entry `dayIndex` rule
(left as-is or dropped from a kept entry), and the session plan names the parent as the decider for
that, not the CEO, because both choices are inside the frozen-set constraints and neither changes
a valid record. If dev finds the choice forces a frozen-function edit, that is the escalation rule
in requirement 6, and it comes back to the CEO.
