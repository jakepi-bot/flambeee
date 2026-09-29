# Story 050: Cinder Quest Log, Day Labels Read the Record's Own Anchor (Session 26, P1)

**Status:** Ready for development (Session 26, 2026-09-29). Corrective. Single file: `src/cinder.html`. Does not amend the Story 039 decision record.
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (truthfulness and trust: this is the last surface of a family Sessions 23, 24 and 25 each corrected one at a time. The streak number reads the recorded history, the recent-quests list reads the recorded history, and the labels on that list still describe a different window).
**Assigned to:** **Riven** owns the label call site and the rendered line (the view and copy surface, `renderQuestLog()` and the label expression it feeds). **Kai** owns the pure-read label helper and the proof helper (`src/kai-story050-questlog-labels-proof.py`), the frozen-function extraction, and the no-write / no-new-field proof. **One owner per helper and per call-site line, named before dev starts** (Story 048 protocol); each PR body states its exact line range against the base commit. **Scout** owns the test plan, the real-browser checks, and the D1/D2 scan on the **merged** candidate. **Palette** checks the label text for brand and mobile consistency. **Vigil** checks that no claim is made the proof does not support, and that the frozen set is byte-identical.
**Tracked by:** Session 26 plan, Story 050. Grounded in Story 035 (the quest log, `renderQuestLog()`, `dayLabelForIndex()`), Story 040 (the welcome-back window and its `lastPlayIdx` anchor), Story 042 (the honest streak line and its anchor), Story 044 (`computeQuestLogStreak()` and `questLogAnchor`), Story 045 (the verification-shaped proof pattern), Story 047 (`computeRecentQuestEntries()` and the `questLogAnchor` read path), Story 033 (the come-back-tomorrow preview), and Story 048 (the single-file ownership protocol). Constrained by `docs/stories/039-cinder-away-time-decision-record.md`.

## Summary

Story 044 fixed the quest log's **streak number** to read the player's recorded history through the pre-reset record (`rawDayState`, held as `questLogAnchor` at `src/cinder.html:1431`). Story 047 fixed the **recent-quests list** to read the same anchor through `computeRecentQuestEntries(questLogAnchor, dayState)`. Both surfaces now describe one record.

The **relative day label printed on each list entry** still describes a different record. `renderQuestLog()` (`src/cinder.html:660-687`) renders each entry as `dayLabelForIndex(entry.dayIndex) + ': ' + title` (`src/cinder.html:671-674`), and `dayLabelForIndex()` (`src/cinder.html:649-655`) computes its difference against `getDayIndex()` - **today** - not against the anchor the list and the number use.

On a stale record this produces a visible contradiction inside one boxed menu. The number reads the recorded run (Story 044), the list reads the recorded run (Story 047), and the labels on that same list say every entry is as old as the whole absence. A player back after a 30-day gap whose recorded run ended on day D sees:

```
=== QUEST LOG ===
Current streak: 1 day
-----------------
Recent quests:
30 days ago: <last quest played>
```

The number and the list say the run ended at day D. The label says day D was 30 days ago, which is also true, but it is not what "recent quests" beside a 1-day streak means to a reader. The screen describes two windows at once, which is the defect class Sessions 23, 24 and 25 each closed one surface at a time.

**Note on scope correction (see "Hypothesis check" below).** The parent's hypothesis reads the label as the only remaining stale-anchor surface. Reading the code, that is correct for the list's labels, but the same `dayLabelForIndex()` function is also used **only** in `renderQuestLog()` (verified by grep, one call site), so the fix is confined to the quest-log render path and nothing else consumes the function.

## Hypothesis check (Quinn, evidence)

The session plan's hypothesis is **confirmed** as to the call site and the arithmetic:

- `dayLabelForIndex()` is called at exactly one place, `src/cinder.html:672`, inside `renderQuestLog()`. Verified by `grep -n "dayLabelForIndex" src/cinder.html` (definition at `:649`, call at `:672`).
- It computes `const diff = getDayIndex() - dayIdx;` (`src/cinder.html:650`), so `diff` is measured from **today**, while the number (`computeQuestLogStreak(dayState, questLogAnchor)`, `:664`) and the list (`computeRecentQuestEntries(questLogAnchor, dayState)`, `:663`) are measured from the record's own anchor (`lastPlayIdx`, derived in `computeQuestLogStreak()` and `computeRecentQuestEntries()`).
- The branch shape is as the plan states: `diff === 0 -> 'today'`, `diff === 1 -> 'yesterday'`, `diff > 1 -> diff + ' days ago'`, else `'day ' + dayIdx`.
- **One sharpening, not a correction:** `diff` is non-negative for every entry drawn from a valid record (an entry's `dayIndex` cannot exceed the anchor, and the anchor cannot exceed today for a record that was actually played), so the `'day ' + dayIdx` fallback is reached only for a `dayIndex` in the future relative to today, which a real record does not produce. The plan's parenthetical about `diff` in `(1, 2)` refers to the fact that `diff` is an integer, so no value falls between 1 and 2; the fallback is for `diff < 0`. The fix must **preserve** that fallback for corrupt or out-of-range input rather than remove it.

The defect is real and is a **label-anchor** defect, not a missing-information defect. It is the last surface of the read-path family.

## Business value

- The quest log is the screen a returning player opens to check whether their history survived. A run of entries all labelled `N days ago` beside a 1-day streak tells that player their recent history is as old as their absence, which is the third variant of the same trust failure in four sessions.
- The family is nearly closed. Fixing the label here closes a defect class the team has paid for three times, in the same single file, in one small change.
- Cheap and provable: one pure-read label helper, one call-site line, no new surface, no write, no new field, and the frozen set is untouched by construction.
- Keeps the byte-safety discipline intact: read-only is provable, and the deploy mirror stays byte-identical after the merge.

## User Story

As a Cinder player returning after one or more missed days,
I want the day label beside each recent quest to describe that quest relative to the same window the streak number and the list already describe,
So that a single boxed menu never tells me my run ended today and that it ended weeks ago at the same time.

## Requirements

### 1. Every label on the quest-log list is derived from the record's own anchor

- The relative label rendered for a list entry must be computed relative to the **anchor the list and the number already use**: the record's last recorded play day (`lastPlayIdx`), derived the same way `computeQuestLogStreak()` (`src/cinder.html:432-493`) and `computeRecentQuestEntries()` (`src/cinder.html:495-520`) derive it - the maximum valid candidate drawn from the record's `dayIndex` and the valid `completedQuests` entries' `dayIndex` values.
- Concretely: the label's difference is `anchor - entry.dayIndex`, not `getDayIndex() - entry.dayIndex`. The anchor is `lastPlayIdx`, which for a stale record is the day the player last played, not today.
- The label forms are unchanged in shape: difference `0` reads `today`, difference `1` reads `yesterday`, difference greater than `1` reads `N days ago`. The out-of-range fallback for an index the anchor does not cover is preserved (see requirement 3).
- The anchor must be passed in or derived read-only, in the same style Story 047 used. It must not be recomputed against `getDayIndex()` inside the label helper.

### 2. The number, the list and the labels describe one window

- With the loaded record at `docs/stories/047`'s anchor, the Current streak number (`computeQuestLogStreak`), the list contents (`computeRecentQuestEntries`) and the labels on that list must all describe the same recorded run.
- On any state the proof covers, the newest list entry's label must be consistent with the streak number for the same recorded history: a 1-day streak beside a single recorded entry whose day is the anchor reads as that day, not as the absence length.
- Where the labels are already correct for a same-day or next-day record, they must stay correct (control case, requirement 4).

### 3. Rendering contract otherwise unchanged

- The list keeps rendering the last entries **most recent first**, capped at 5 (`.slice(-5).reverse()`, `src/cinder.html:666`), with the same entry titles (`entry.objective || entry.label || ''`, escaped through `escapeHtml`).
- The empty-state line is unchanged: `"No quests recorded yet. Finish today's quest to start your log."` (`src/cinder.html:668`).
- The `Current streak: N days` line's shape and value are unchanged (`:677`).
- The out-of-range label fallback (`'day ' + dayIdx`) is preserved for any entry the anchor cannot place; the fix changes the **reference point**, not the set of label forms.

### 4. Same-day and next-day returns are the control and must not change

- A same-day reload (record stamped today) and a next-day return (record stamped `T-1`, nothing fully missed) must render exactly as v0.23.0 renders them, including every label.
- The Story 033 come-back-tomorrow preview and the Story 037 app-icon badge are not regressed.

### 5. Pure read: no new field, no write, no reset or anchor-function change

- Pure read. **No new persisted field** on the character save or on the day record. Not a cache, not a version marker, nothing.
- **No write on the read path.** Opening row 9 and rendering the log must leave `flambeee-cinder-save` and `flambeee-cinder-day` byte-identical.
- The **stored day record shape is unchanged**: `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }`, no field added, renamed, or removed.
- Escalation rule (binding): if the only correct fix requires a persisted field, that is a Story 039 decision-record amendment plus CEO sign-off. Escalate; do not implement it.

### 6. Frozen functions stay byte-identical to v0.23.0

The following are frozen for this story and proven by extraction, not assumed:

- `checkDailyReset()` (`src/cinder.html:762-773`)
- `computeQuestLogStreak()` (`src/cinder.html:432-493`)
- `computeRecentQuestEntries()` (`src/cinder.html:495-520`)

They must be byte-identical to their v0.23.0 shipped text. The label helper is a **separate** function or a changed call site; it must not be implemented by editing any frozen function.

### 7. Graceful degradation

- Corrupt or missing history (`completedQuests` not an array, entries with a non-numeric or non-finite `dayIndex`), a non-object record, private mode, and unavailable storage must all degrade to a correct render from whatever valid state exists, or to the empty-state line, and **never to an exception or a blocking error**.
- The label path must follow the existing filter/guard pattern in `computeRecentQuestEntries()` (skip non-object entries rather than throw).
- A `null` day index, a missing anchor, or an anchor that cannot be derived must fall back to the existing label form, not throw.

### 8. Collision guard: one owner per helper and per call-site line

- This story touches **one file** (`src/cinder.html`). Per the Story 048 protocol: **Riven** owns the rendered label expression inside `renderQuestLog()` (`src/cinder.html:660-687`); **Kai** owns any new pure-read label helper and the proof script. The exact line range each owns is stated in each PR body against the base commit. Overlap is not mergeable until re-cut.
- Kai and Riven each work in a separate git worktree.

### 9. Mobile-safe, boxed-menu pattern, no inline onclick

- The quest log remains a `boxed-menu` block consistent with the other Cinder views.
- All interactive controls keep the v0.13.1 `data-action` event delegation pattern. No inline `onclick`, ever (issue #46).
- No horizontal overflow at 375x667, and Back to Town stays reachable and tappable. A label that grows by one word must not overflow.

### 10. Copy: plain punctuation, no em dashes, no heavy emoji

- Any new or changed user-visible string uses plain punctuation, no em dashes, and no heavy emoji, in Cinder's dry voice. The label strings (`today` / `yesterday` / `N days ago`) already satisfy this and their spelling does not change.

## Out of scope

- Any change to the list's **rendering contract** (order, cap of 5, entry titles, empty-state line). This story may change **which reference point** the labels use; it does not change what the list looks like for the same history, except for the corrected reference.
- Any change to the streak **number** or its source (`computeQuestLogStreak`).
- Any change to the list **source** (`computeRecentQuestEntries`).
- Any change to `checkDailyReset()` - its logic, its writes, or the shape of the record it builds.
- Any change to the Story 042/044 welcome-back panel, its wording, its anchor, or `computeAwayWindow()`.
- Any change to the welcome-back **days-away sentence** or its definition. That is Story 051's surface; the two stories must not both touch `computeAwayWindow()`.
- Any banked, preserved, or restored streak as a mechanic. This story changes what the log **reports**, never what the game **keeps**.
- Any new history field, any extension of `completedQuests`, any change to the stored day record shape, and any new persisted field of any kind.
- Any offline resource accrual, boss-day balance change, cross-day streak mechanic, or multi-day welcome-back suppression. All remain blocked on the Story 039 amendment plus CEO sign-off.
- Any balance, reward, rotation, payout, monster-pool, or level-curve change.
- Any notification, push, email, permission prompt, or install nag.
- Any new town-hub row, banner, tooltip, or notification dot.
- Any new game, league, leaderboard, guess-count stat, multiplayer, or community-submitted game.
- Any website redesign, or any change to `scripts/verify-website-currency.sh` (Story 052 owns the checker runs).
- Any cron configuration, and any file under `jobs/`, `jobs-refactor-team/`, or `jakebot/`.

## Acceptance Criteria (BDD)

### Scenario 1: A 30-day-stale record shows its newest entry relative to the record, not to today (P1, Riven + Scout, the story's core assertion)
- **Given** a loaded day record whose last recorded play day is 30 days before today, carrying a recorded completion on that day
- **When** the player opens the Quest Log (hub row 9)
- **Then** the newest entry's label is relative to the record's anchor (the last recorded play day), so the entry is not labelled `30 days ago` solely because 30 days have passed since it, and the Current streak number, the list and the labels describe one window

### Scenario 2: The label uses the same anchor as the number and the list (P1, Kai + Riven)
- **Given** any recorded play day rendered in the list
- **When** it renders
- **Then** its label difference is measured from the same anchor `computeQuestLogStreak()` and `computeRecentQuestEntries()` derive, and the number, the list and the labels describe the same recorded run

### Scenario 3: Same-day reload renders exactly as v0.23.0 (P1, Riven + Scout, control)
- **Given** a day record already stamped for today, loaded and then reloaded on the same UTC day
- **When** the player opens the Quest Log after the reload
- **Then** every label, the streak number and the list are identical to the v0.23.0 render for the same recorded history

### Scenario 4: Next-day return renders exactly as v0.23.0 (P1, Kai + Scout, control)
- **Given** a day record stamped `T-1` with nothing fully missed
- **When** the player opens the Quest Log on day `T`
- **Then** every label reads as v0.23.0 renders it, and the Story 033 come-back-tomorrow preview and the Story 037 badge are not regressed

### Scenario 5: A stale-by-1 record labels its entry `today` (P1, Kai, proof)
- **Given** a stale-by-1 record whose newest recorded play day is yesterday relative to the record's own anchor semantics, seeded so the label difference is 0
- **When** the log renders from the record
- **Then** the newest entry reads `today` for that record, not `1 day ago`

### Scenario 6: The label difference is `anchor - entry`, never `today - entry` (P1, Kai, proof)
- **Given** the label helper extracted into a sandbox
- **When** it is called with an anchor and entry indexes the proof seeds (differences 0, 1, 3, 30)
- **Then** it returns `today`, `yesterday`, `3 days ago`, `30 days ago` respectively relative to the **anchor**, and the pre-fix build fails these assertions against shipped v0.23.0, isolating the fix

### Scenario 7: The proof fails against shipped v0.23.0 (P1, Kai, proof)
- **Given** the proof script `src/kai-story050-questlog-labels-proof.py`
- **When** it is run against shipped v0.23.0 and against the candidate build
- **Then** it **fails** against v0.23.0 and **passes** against the candidate, with the failing checks naming the stale-anchor labels, and exit code 0 on the candidate

### Scenario 8: Frozen functions are byte-identical to v0.23.0 (P1, Kai, proof)
- **Given** the diff for this story in `src/cinder.html`
- **When** the frozen functions are extracted
- **Then** `checkDailyReset()`, `computeQuestLogStreak()` and `computeRecentQuestEntries()` are textually unchanged from v0.23.0

### Scenario 9: The read path writes nothing and adds no field (P1, Kai, proof)
- **Given** any state that renders the Quest Log
- **When** the player opens row 9 and the log renders
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical before and after, a static scan of the label and render path finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, or state-mutating write, and no new field name appears anywhere in the diff

### Scenario 10: The list contract is unchanged for the same history (P1, Riven + Scout)
- **Given** any history the proof covers
- **When** the list is rendered by the pre-story build and by the story build
- **Then** the two renders are identical in order, cap of 5, entry titles and empty-state behaviour, and differ only where the label reference point is corrected

### Scenario 11: Legacy, corrupt, and partial records degrade cleanly (P1, Kai + Scout, regression)
- **Given** a legacy day record with no `completedQuests`, and separately a corrupt record (`completedQuests` a string, an entry with a non-numeric `dayIndex`, `dayIndex` not a number, `dayState` null)
- **When** the game loads and the player opens the Quest Log
- **Then** it renders without error, the list renders or falls back to the empty-state line, every label falls back to the existing label form for a day the anchor cannot place, and nothing throws

### Scenario 12: Storage unavailable or private mode (P1, Kai)
- **Given** the browser is in private mode or storage is unavailable, so the existing localStorage helpers throw and swallow
- **When** the game loads and the player opens the Quest Log
- **Then** the game runs from in-memory state and the log behaves the same as with storage, and nothing throws

### Scenario 13: Story 042/044 panel and welcome-back window not regressed (P1, Scout, regression)
- **Given** an intact recorded run and a genuine hole, each on a multi-day gap
- **When** the welcome-back panel and the Quest Log render on the same page state
- **Then** the panel's sentences and the log's streak are unchanged from v0.23.0, and the two surfaces do not contradict each other

### Scenario 14: Out-of-scope references and forbidden fallbacks are absent (P1, Scout, the Session 24 D1/D2 class)
- **Given** the merged candidate's diff for `src/cinder.html`
- **When** Scout scans it
- **Then** no variable is referenced outside the scope that owns it, no read path falls back to the post-reset record when the loaded record is unavailable, and the label helper returns the existing fallback form rather than throwing when the anchor cannot be derived

### Scenario 15: Mobile-safe, Back to Town tappable, no inline onclick (P1, Riven + Scout)
- **Given** the Quest Log rendered at 375x667 and on desktop, including a record with labels long enough to wrap
- **When** the player taps Back to Town
- **Then** the tap is handled by the delegated `data-action` listener, the town hub renders, there is no horizontal overflow, and no inline `onclick` appears anywhere in the markup

### Scenario 16: No notifications, no push, no permission prompt, no install nag (P1, Vigil + Scout)
- **Given** this story's code
- **When** it is scanned and exercised in a browser
- **Then** it contains no `Notification` permission request, no `pushManager`, no subscription code, and no permission prompt or install prompt appears at any point in load or in the log path

### Scenario 17: Tone and no-AI-tells (P2, Vigil)
- **Given** any new or changed user-visible copy
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and matches the plain-punctuation, dry-humour Cinder voice

### Scenario 18: The worktree and ownership rule was followed (P1, Kai + Riven + parent)
- **Given** this story touched one file
- **When** the work is reviewed
- **Then** Kai and Riven each worked in a separate git worktree, one owner was named per helper and per call-site line before dev started, each dev's PR body states the exact line range it owns, and Scout's checks ran against the merged candidate rather than the two branches

## Wireframe / visual description

Quest Log, stale record, before this story (the defect):

```
=== QUEST LOG ===
Current streak: 1 day
-----------------
Recent quests:
30 days ago: Slay the cave bat
-----------------
1. Back to Town
```

Quest Log, same stale record, after this story (the fix):

```
=== QUEST LOG ===
Current streak: 1 day
-----------------
Recent quests:
today: Slay the cave bat
-----------------
1. Back to Town
```

The single change is the reference point of the label's difference: the same record, the same list, the same number, and a label that now describes the day the record says the run ended.

## Proof / evidence required

1. **Pure-function proof (Kai):** an extractable proof script `src/kai-story050-questlog-labels-proof.py` that seeds records stale by **1, 3, 6 and 30 days** plus a **same-day control**, asserts the label set for each, and **fails against shipped v0.23.0** to isolate the fix. Expected exit code 0 on the candidate.
2. **Frozen-function extraction (Kai):** `checkDailyReset()`, `computeQuestLogStreak()` and `computeRecentQuestEntries()` byte-identical to v0.23.0, shown by extraction, not by inspection.
3. **No-write / no-new-field proof (Kai):** both localStorage keys byte-identical across the log path; static scan clean.
4. **Real-browser checks (Scout):** the Quest Log rendered in real Chromium at desktop and 375x667 on the merged candidate, on a stale record and a same-day record, with a tap on Back to Town; the pre-fix build fails the label checks, isolating the fix.
5. **D1/D2 scan (Scout):** on the merged candidate, per Scenario 14.
6. **Deploy-mirror note:** this story changes `src/cinder.html`, so the post-merge re-sync of `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` and its `cmp` / sha256 proof are required, and are recorded under Story 052.

## Open questions / ambiguities (need CEO input)

None that block development. The definition of a label's reference point is fixed by this story (the record's own anchor, the same one the number and the list use). The related question of a single definition of "days away" is Story 051's, and it is a different surface (`computeAwayWindow()`), which this story does not touch.
