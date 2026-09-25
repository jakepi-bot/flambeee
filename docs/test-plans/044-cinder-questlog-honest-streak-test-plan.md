# Test Plan: Story 044 - Cinder Quest Log, Honest Streak Line and Recent-Quests Count on a Return Day (Session 24)

**Story:** `docs/stories/044-cinder-questlog-honest-streak.md` (22 BDD scenarios)
**Code under test:** `src/cinder.html`. Story 044 puts **two devs on one file**: Kai's half is `computeQuestLogStreak(dayState, rawDayState)`; Riven's half is the rendered `Current streak: N days` line in `renderQuestLog()`.
**Baseline for regressions:** `main` at `fac7c32`, tag `v0.21.0`.
**Baseline artifact:** `src/cinder.html`, 1421 lines, 60754 bytes, sha256 `e48a1040083013f8e153cf8262074e20115d23245200b36502054f4e9febb56e`.
**Harness:** `/home/jake/.openclaw/workspace/flambeee-team/scout-qa-session24.py`, `/home/jake/.openclaw/workspace/.venv/bin/python3`, extracting the shipped helpers into a node `vm` sandbox the way `scout-qa-session20-035.py` extracts `computeQuestStreak`.
**Artifact rule:** the code under test is read from the shipped file or from `git show <commit>:src/cinder.html`, never from a mutable worktree, so a test cannot pass against uncommitted code.

## The defect this plan targets

`renderQuestLog()` computes its streak with `computeQuestStreak(dayState)`. That helper anchors on today when today's quest is complete and on yesterday when it is not. On the load of a gap day, `checkDailyReset()` has already rebuilt `dayState` wholesale with `completedQuests: []` and today's quest is not complete, so the anchor is yesterday, that index has no recorded completion, and the loop exits with **0**. The welcome-back panel on the same screen says **"Your streak survived."** from the loaded record's history. Two surfaces, one file, contradictory, and the zero is the false one.

## Method

Day indexes are seeded relative to the live UTC day index `T` (`getDayIndex() = Math.floor(Date.now() / 86400000)`). Each case seeds a known day record, then drives the shipped helpers and, where the scenario is a render, the real page as a returning player would. Assertions read rendered text and printed values. Nothing is stubbed. A `localStorage.setItem` wrapper is used only by the no-write checks and records calls without changing them.

Two halves are tested **separately and then together**:

- Kai's half: `computeQuestLogStreak(dayState, rawDayState)` value correctness, purity, degradation.
- Riven's half: the rendered line, the list order and cap, the panel, mobile.
- Together: Scenario 2 agreement is the story's core assertion and is tested on the merged candidate.

## Scenario coverage

### S1 Intact recorded run reads the true streak in the log (P1)
Seed `completedQuests` for `T-4, T-3, T-2` with `dayIndex: T-2`, gap day load. Assert the log's `Current streak` reads **3**, not 0.
**Expected:** PASS after the fix, FAIL on the v0.21.0 baseline (baseline reads 0).

### S2 The log and the welcome-back panel agree on the same day (P1, core assertion)
Same seed as S1. Assert the panel renders "Your streak survived." **and** the log reads a number `>= 1` equal to the recorded run length.
Assert the negative: the log does not read 0 while the panel says survived.
**Expected:** PASS after the fix, FAIL on baseline.

### S3 A genuine gap resets to 0 in both surfaces and they agree (P1)
Seed `completedQuests` for `T-6, T-5` with `dayIndex: T-2` (T-4 is a hole between recorded completions). Assert the panel reads "Your streak is broken." and the log reads 0.
**Expected:** PASS on both baseline and candidate (this case is correct today).

### S4 First-ever player reads 0 with no crash (P1)
Seed no `completedQuests`, `dayIndex` today, today's quest not complete. Assert the log reads 0, the empty-state line "No quests recorded yet. Finish today's quest to start your log." renders, and nothing throws.
**Expected:** PASS on both.

### S5 The streak source is the recorded history, never a post-reset record (P1)
Take a stale record carrying completions. Compute the log's streak from the loaded record's history, then from the same record after `checkDailyReset()` has rebuilt it (which replaces `completedQuests` with `[]`). Assert the rendered value comes from the loaded history and is **unchanged by the rebuild**.
**Expected:** PASS after the fix, FAIL on baseline (baseline reads the rebuilt record).

### S6 In-progress today still reads the preserved run (P1)
Today's quest not complete, yesterday carries a recorded completion with the run continuing back. Assert the log reads the preserved run length, not 0.
**Expected:** PASS on baseline and candidate. **Regression guard** for `computeQuestStreak()` behaviour that must not be lost.

### S7 Completed today joins the run (P1)
Today's quest completed and rewarded, days before it carry recorded completions. Assert the log reads one more than the run ending yesterday.
**Expected:** PASS on both.

### S8 The recent-quests list stays correct (P1)
Seed 7 recorded completions. Assert the list shows the last 5 most recent first with their relative day labels, and is **identical to the pre-story rendering** for the same history.
**Expected:** PASS on both. Any difference is a Riven-half regression.

### S9 Legacy, corrupt, and partial records degrade cleanly (P1)
Cases: no `completedQuests`; `completedQuests` a string; `completedQuests` a number; an array of junk entries; an entry with a non-numeric `dayIndex`; negative day indexes; `dayIndex` not a number; whole record garbage/string/number/empty object; `dayState` null.
Assert: renders without error, the streak reads a correct value from the valid parts or 0, the list renders or falls back to the empty-state line, **no exception raised**, the hub still reachable.
**Expected:** PASS on both. Any throw is a blocking defect.

### S10 Storage unavailable or private mode (P1)
`localStorage.getItem`/`setItem` throwing. Load on a gap day, play, open the log. Assert the game runs from in-memory state, the log behaves the same as with storage, and nothing throws.
**Expected:** PASS on both.

### S11 The quest-log read path writes nothing and adds no field (P1)
With a well-formed record already stamped for today: instrument `localStorage.setItem`, open row 9, render the log. Assert zero writes to `flambeee-cinder-save` and `flambeee-cinder-day`, byte-identity of both keys before and after, and a static scan of the added lines finding no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, and no new field name (`seenReturn`, `lastStreak`, gap stamp, version marker).
Scope note per story technical notes: the load path's pre-existing `checkDailyReset()` / `ensureQuestState()` writes are v0.21.0 behaviour and are **not** part of the read path this plan owns.
**Expected:** PASS. Any write on the row-9 path is a blocking defect.

### S12 The day record shape is unchanged (P1)
Compare the stored day record field set against baseline. Assert exactly `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }`, no added, removed, or renamed field.
**Expected:** PASS.

### S13 `checkDailyReset()` is byte-identical to v0.21.0 (P1)
Extract the `checkDailyReset()` block from baseline and candidate and compare blob hashes. Assert textually unchanged.
**Expected:** PASS. Any change is a blocking defect.

### S14 `computeQuestStreak()` is unchanged (P1)
Extract the `computeQuestStreak()` block from baseline and candidate and compare blob hashes. Assert textually unchanged, and that it returns the same value for the same inputs (the 15 Story 035 node assertions still pass).
**Expected:** PASS. Any change is a blocking defect.

### S15 Story 042 welcome-back panel not regressed (P1)
A multi-day gap with an intact recorded run, and separately one with a genuine hole. Assert the panel reads "Your streak survived." and "Your streak is broken." respectively, with the days-away and quests-missed sentences and both `data-action` rows unchanged from Story 042.
**Expected:** PASS.

### S16 Story 033 come-back-tomorrow preview not regressed (P1)
Complete and collect today's quest, open the quest view. Assert the "Tomorrow: ..." preview and "Come back after midnight to start it." render exactly as before.
**Expected:** PASS.

### S17 Story 037 app-icon badge not regressed (P1)
Instrument `navigator.setAppBadge`/`clearAppBadge`. Assert 1 while the quest is pending and cleared on completed-and-rewarded.
**Expected:** PASS.

### S18 Same-day and next-day returns stay quiet (P1)
Record stamped `T` (same-day), record stamped `T-1` (next-day, nothing fully missed). Assert no welcome-back panel, the log renders its streak, and the hub renders as the pre-story build renders it.
**Expected:** PASS.

### S19 Escalation, not implementation, if a persisted field is needed (P1)
Review the diff. Assert the fix uses existing state only, no persisted field shipped. If any design required one, assert it was escalated as a Story 039 amendment instead of implemented.
**Expected:** PASS (no persisted field). Failure here is a process defect, not a code defect.

### S20 No notifications, no push, no permission prompt, no install nag (P1)
Static scan for `Notification`, `pushManager`, `requestPermission`, `serviceWorker` messages, `beforeinstallprompt`, `onclick=`. Browser run asserting no dialog appears and no permission or install text is in the DOM.
**Expected:** PASS.

### S21 Mobile-safe, Back to Town tappable, no inline onclick (P1)
Render the log at 375x667 and on desktop. Assert the Back to Town tap is handled by the delegated `data-action` listener and renders the hub, no horizontal overflow, and no inline `onclick` in the markup.
**Expected:** PASS.

### S22 Tone and no-AI-tells (P2)
Scan new and changed user-visible copy for em dashes and heavy emoji. Assert the streak line is one plain line with a number and the singular/plural handling is unchanged.
**Expected:** PASS. Only the number changes.

## Boundary and negative matrix

| Input | Boundary tested | Expected |
|-------|-----------------|----------|
| `completedQuests` empty, `dayIndex: T` | zero history | 0, empty-state line, no throw |
| Single completion at `T-2`, `dayIndex: T-2` | run length 1 | log 1, singular "day" |
| Completions `T-4..T-2`, `dayIndex: T-2` | contiguous run, gap day | log 3 |
| Completions `T-6, T-5`, `dayIndex: T-2` | hole before last play day | log 0, panel broken |
| `dayIndex: T` but no completion | stamped-but-idle day | 0 in log, no panel |
| Today completed, `T-1, T-2` completed | live join | run includes today |
| 7 completions | list cap | last 5, most recent first |
| `completedQuests` = `"T-2"` (string) | type corruption | 0 or valid parts, no throw |
| entry `{ dayIndex: "x" }` | non-numeric index | entry ignored, no throw |
| `dayIndex: NaN` / `null` / `"2"` | non-finite stamp | 0 or valid parts, no throw |
| `dayIndex` in the future | out-of-range | no bogus run, no throw |
| `dayState` null / string / number | whole-record corruption | hub renders, no throw |
| unparseable JSON in the day key | parse failure | hub renders, no throw |
| storage throwing on read and write | private mode | in-memory play, no throw |

## Regression control run

S3, S4, S6, S7, S15, S16, S17, S18 are run against the **baseline build** with the same seeds, so a rendering difference is attributable to this story rather than to pre-existing state. S1, S2, S5 are run against the baseline too and are **expected to FAIL** there: those three failures are the Story 044 defect.

## Verdict

**Test plan status: written 2026-09-25. Execution results are recorded in `/home/jake/.openclaw/workspace/flambeee-team/qa-results.md`, Session 24 section.**

QA verifies and reports. Any defect found is reported with reproduction steps and is never fixed here.
