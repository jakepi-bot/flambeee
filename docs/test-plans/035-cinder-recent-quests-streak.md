# Test Plan 035: Cinder Recent Quests and Quest Streak View

Story: `docs/stories/035-cinder-recent-quests-streak.md` (P1)
QA: Scout. Written 2026-09-15 (Session 20).
Target code: `src/cinder.html` (repo source) and `share/Flambeee/games/cinder.html` (live mirror).
Test env: Playwright against the updated `cinder.html`, plus pure-function checks with `.venv/bin/python3` and `node`.

## Scope guard

Pure-read verification only. A defect is reported, not fixed. If the view path writes save data or mutates state, that is a blocking defect (fail).

## Environment prep

1. Confirm `src/cinder.html` and the live mirror are byte-identical before any test: `cmp src/cinder.html share/Flambeee/games/cinder.html` -> PASS, and `md5sum` equal.
2. Serve the game locally (e.g. `python3 -m http.server` in the repo dir) and load it in Playwright Chromium at a desktop (1280x720) and a narrow mobile (375x667) viewport.
3. Reset browser storage before each scenario so saves start clean.

## Preconditions / fixtures

- A completed-and-rewarded today quest: craft a save where `flambeee-cinder-day` has `quest.progress >= target`, `quest.completed=true`, `quest.rewarded=true`, and `completedQuests` contains today's entry.
- A multi-day history: craft `completedQuests` with consecutive prior `dayIndex` entries.
- A legacy save: `flambeee-cinder-day` with NO `completedQuests` field (predates Story 035).

---

## Scenario 1 (P1): Completed quests appear in the quest log

**Given** a player completed and rewarded today's quest and the additive history recorded it.
**When** the player opens the quest-log view from the town hub.
**Then** today's quest appears in the recent list (most recent first) with label/objective and day; the list shows at most the most recent N=5 entries.

### 1.1 Happy path
- Fixture: 6 completed quests across 6 days, today + 5 prior.
- Open quest log. ASSERT: the list shows exactly 5 entries, most recent (today) first, oldest entry cut.
- ASSERT: each row shows label/objective and a day/date.

### 1.2 Boundary: exactly 5
- Fixture: exactly 5 completed days. ASSERT: all 5 shown, no truncation, no scroll needed on desktop.

### 1.3 Boundary: 0 (empty history, legacy save)
- Fixture: legacy save, no field. Open the view.
- ASSERT: view renders without crash (no TypeError), shows an empty state or "no quests yet" copy, never throws.

### 1.4 Ordering
- Assert entries are sorted strictly most-recent-first by `dayIndex` descending. A shuffled fixture must come out ordered.

### 1.5 Negative: quest in progress, not completed
- Fixture: today quest not complete. The quest-log view must NOT list the incomplete today quest as completed. If completed-only is enforced, do not list it.

---

## Scenario 2 (P1): Streak is derived and reflects consecutive completions

**Given** a player completed the previous UTC day's quest and today's quest.
**When** the player opens the quest-log view.
**Then** the current streak shows 2, and an earlier completion with a missed day before today does not count toward the current run.

### 2.1 Consecutive days
- Fixture: completed days [today, today-1]. ASSERT: streak = 2.

### 2.2 Missed-day reset
- Fixture: completed days [today, today-2, today-4]; today-1 and today-3 missed.
- ASSERT: streak = 1 (only today's run counts; earlier isolated completions do not).

### 2.3 Completed yesterday, not yet today (open question 1)
- Fixture: completed yesterday (today-1), today NOT complete.
- Recommended behavior: streak stays live at the prior value (e.g. 3) until today's UTC day ends un-completed. ASSERT according to the confirmed CEO ruling. Negative: streak must NOT drop to 0 merely because today is not done yet within the same UTC day.

### 2.4 No completions
- Fixture: empty history, today incomplete. ASSERT: streak = 0, no negative number, no crash.

### 2.5 Gap at the boundary
- Fixture: a long-ago completed run (e.g. today-10) with many missed days, then today complete.
- ASSERT: streak = 1, not the old historical run length.

### 2.6 Pure-function determinism
- Extract `computeQuestStreak(dayState)` and assert:
  - Same input always yields the same output (run N=100).
  - No global mutation: the input object and `QUEST_TYPES` are unchanged after calls.
  - Handles a null/undefined `completedQuests` (legacy) returning 0 without throwing.

---

## Scenario 3 (P1): View is a pure read

**Given** the quest-log view is opened.
**When** recent list and streak are computed and rendered.
**Then** no save data is written and no state is mutated: `flambeee-cinder-save`, `flambeee-cinder-day`, dayState, quest state byte-identical before/after; level/gold/XP/wins unchanged.

### 3.1 Persistence no-op
- Capture JSON of `localStorage['flambeee-cinder-save']` and `['flambeee-cinder-day']` before opening the view.
- Open the quest-log view, wait for render, then capture again.
- ASSERT: both byte-identical before and after ("SaveStateNoop"). No `localStorage.setItem` fired on the view path.

### 3.2 Static scan (Kai proof, adapt `kai-story033-pure-read-proof.py`)
- Statically scan the quest-log view path (render function + `computeQuestStreak` + history derivation) for forbidden writes:
  `saveCharacter`, `saveDayState`, `localStorage.setItem`, `ensureQuestState`, `completeQuest`, `applyQuestProgress`, and any `character.` / `dayState.` assignment.
- ASSERT: none present on the view path. The ONLY persistence change in scope is the `completedQuests` append inside `completeQuest()` (Scenario 6).

### 3.3 State mutation
- Open the view on a save with nonzero level/gold/XP/wins; close/reopen.
- ASSERT: level, gold, XP, wins unchanged.

### 3.4 Negative: view-path write detection
- If any forbidden write appears on the view path, report as a blocking defect with the file line and the exact call.

---

## Scenario 4 (P1): Existing saves load clean; empty-history saves work

**Given** a player save that predates Story 035 (no `completedQuests` field).
**When** the player loads the game and opens the quest-log view.
**Then** the save loads without error, no field is required, recent list is empty (or shows only newly recorded completions), and level/gold/XP/wins unchanged.

### 4.1 Legacy load
- Fixture: legacy save, no field. Load game.
- ASSERT: no parse/TypeError, game renders, no loss of level/gold/XP/wins.
- Open quest log. ASSERT: renders, empty history tolerated.

### 4.2 ensureQuestState backfill
- ASSERT: `ensureQuestState()` / `checkDailyReset()` default `completedQuests` to `[]` when absent, without overwriting or re-keying any existing field. Verify the save still has its original quest/level data intact after backfill.

### 4.3 Corrupt/partial field negative
- Fixture: `completedQuests: null` and `completedQuests: "not-an-array"`.
- ASSERT: the view and streak do not crash; treated as empty (or safely coerced), no infinite loop, no data corruption.

---

## Scenario 5 (P1): Quest-log reachable and Back to Town works on mobile

**Given** a mobile/touch viewport with the town hub shown.
**When** the player taps the quest-log row and then taps Back to Town.
**Then** the view opens inside `boxed-menu` with no horizontal overflow, is fully readable, and Back to Town reliably returns to the town square via the delegated tap handler.

### 5.1 Reachability
- On mobile, town hub shows a quest-log row (recommended row 9 "Quest log"). Tap it.
- ASSERT: quest-log view opens, no horizontal scrollbar: `document.documentElement.scrollWidth <= clientWidth`.

### 5.2 Delegated handler, no inline onclick
- ASSERT: the quest-log row carries `data-action="N"` and NO inline `onclick` attribute (issue #46 regression guard). The single `#display` click listener (line ~1060) maps the tap.
- Assert no new `addEventListener` added for this view (reuse the existing one).

### 5.3 Back to Town
- Tap Back to Town row. ASSERT: returns to `renderTownMenu()` (town square rows visible). Repeat 5x; assert reliability (each tap returns correctly).

### 5.4 Narrow viewport overflow
- At 375x667, assert the recent list + streak block fit inside `boxed-menu` with no horizontal overflow and no clipping of the Back row.

### 5.5 Negative: tap on non-row gap
- Tap inside `boxed-menu` but on a non-row area. ASSERT: no navigation, no error.

---

## Scenario 6 (P1): Append happens exactly once per completed quest

**Given** a quest is completed and rewarded across a reload in the same UTC day.
**When** the daily reset does not occur and the player plays again that day.
**Then** the quest is recorded in history exactly once (guarded by the same completed/rewarded gate as payout-once).

### 6.1 Once gate
- Complete and reward today's quest. Reload the page in the same UTC day. Play again.
- ASSERT: `completedQuests` array length increased by exactly 1 for today; no duplicate entry; today's reward paid once.

### 6.2 Negative: repeated completeQuest call
- Call `completeQuest()` twice after completion. ASSERT: second call is a no-op for reward AND for history append (no duplicate).

### 6.3 Negative: re-append on reload, post-reset
- Complete today, reload same day (no append), confirm 1 entry; force a new UTC day, complete the new quest.
- ASSERT: old entry preserved + today's new entry appended (history accumulates across days, not truncated).

---

## Scenario 7 (P2): Tone and no-AI-tells

**Given** the new copy.
**When** any external-visible text from this story is reviewed.
**Then** it contains no em dashes, no heavy emoji, plain punctuation, dry-humor Cinder voice.

### 7.1 Copy scan
- Grep the new quest-log rows/streak copy for `—` (em dash) and heavy emoji sequences.
- ASSERT: none present. Only plain ASCII punctuation.

### 7.2 Visibility
- Assert the visual description matches: streak line in `#ffcc00` accent, entries in standard text color, relative day labels.

---

## Mirror sync (all scenarios)

After the change ships:
- `cmp src/cinder.html share/Flambeee/games/cinder.html` -> PASS (byte-identical), `md5sum` equal.
- If NOT synced, report as a release-blocking defect (standing deploy practice).

## Pass/fail summary format

Per scenario, record: PASS / FAIL / N/A (with reason). Overall = all PASS required for 035 go. Any FAIL is logged as a defect (severity, steps to reproduce, expected vs actual).
