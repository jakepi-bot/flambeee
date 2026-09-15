# Story 035: Cinder Recent Quests and Quest Streak View (Session 20, P1)

**Status:** Ready for development (Session 20, first half, 2026-09-15).
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (retention: make the daily-return loop's progress persistent and visible in the town hub).
**Assigned to:** Riven (frontend: persistent recent-quests / streak view in the town hub, mobile tap polish). Kai (backend/logic: pure-read proof, backwards-compatible save extension, review).
**Tracked by:** Session 20 plan Priority 1 (Cinder retention polish). Grounded in Story 025 (daily quest), Story 033 (daily-return preview), and the v0.13.1 event delegation pattern.

## Summary

Cinder gives one deterministic quest per UTC day (Story 025). Story 033 added a tomorrow preview to the completed quest detail view, so a player who finishes today knows to come back after midnight. What a returning player still does not see is how often they actually came back: there is no persistent record of which quests they finished and no visible streak. This story adds a persistent **recent-quests / quest-streak view** in the town hub. It is a small read-only panel a player can reach from the hub that shows their last completed quests and their current consecutive-day completion streak.

This is a retention surface, not a new mechanic. It shows what the player already accomplished from existing save data (extended by a backwards-compatible additive record) and makes the daily habit legible and countable. No balance, no reward, no mechanic, no rotation change.

## Business value

- Retention loop becomes countable: a visible streak and recent history give a returning player a concrete reason to protect their run by coming back today.
- Rides the confirmed browser-game retention lever (daily-return / repeat-quest loops) without new product scope.
- Near-zero regression surface under the no-balance-change principle: the view is read-only, the only persistence change is an additive, backwards-compatible field with a graceful default for existing saves.
- Complements Story 033's completed-state preview with a standing, at-a-glance record the player can check any time from the hub.

## User Story

As a Cinder player who returns across days,
I want to see my recent completed quests and my current quest streak from the town hub,
So that I can see my progress over time and keep my daily streak alive.

## Requirements

### 1. Persistent, backwards-compatible history

The game must persist a record of completed quests so a returning player can see more than today. The existing save keys are:

- `flambeee-cinder-save` (JSON): `{ name, level, xp, hp, maxHp, attack, defense, gold, bank, weapon, armor, wins, losses, deaths }`
- `flambeee-cinder-day` (JSON): `{ dayIndex, fightsUsed, innHealsUsed, quest: { progress, completed, rewarded } }`

The current format keeps only today's quest state; past completions are not stored. So this story adds an **additive** history field (recommendation: `completedQuests` array on `flambeee-cinder-day`, each entry `{ dayIndex, label, objective }`, appended exactly once per completed-and-rewarded quest in `completeQuest()`). The field must be **optional**:

- Existing saves with no field load with an empty history and no loss of level, gold, XP, wins, or any current state (backwards-compatible).
- `ensureQuestState()` and `checkDailyReset()` must default the field to `[]` when absent, mirroring how `quest` is already defaulted.
- Appending is the single write on the completion path; the view itself is a pure read.

### 2. Recent-quests / streak view in the town hub

Add a readable view reachable from `renderTownMenu()` (the boxed-menu town square) that shows:

- **Recent quests:** the last N (5 recommended) completed quests, most recent first, each as `dayIndex` (or date) plus the quest label/objective.
- **Current streak:** the count of consecutive UTC days with a completed-and-rewarded quest ending on today or yesterday. A completion today keeps the streak live; a missed day resets it to the current run. The streak is derived from the `completedQuests` history plus today's `dayState.quest.completed`.

The view must be reachable by an added town-hub row (e.g. row 9 "Quest log") using the existing row + `data-action` markup, and must render inside the `boxed-menu` layout with a Back to Town row, matching the pattern used by `renderQuest()`.

### 3. Pure read; no balance or mechanic change

Opening the recent-quests / streak view must not write any save data, mutate state, or change quest progress, rewards, rotation, or payout. The only persistence change in scope is the additive `completedQuests` append at completion time (requirement 1). Kai must prove the view path is a pure read (adapt the `kai-story033-pure-read-proof.py` approach): extract the streak/history derivation, assert determinism and no global mutation, and statically scan the view path for forbidden write/mutation calls (`saveCharacter`, `saveDayState`, `localStorage.setItem`, `ensureQuestState`, `completeQuest`, `applyQuestProgress`, `character.`, `dayState.` writes).

### 4. Mobile / menu-tap safe

The view reuses the v0.13.1 event delegation pattern: rows carry `data-action="N"` and a single listener on the `#display` container maps taps to `handleMenuClick`. No inline `onclick` handlers (issue #46). On a narrow viewport the recent-quests list and streak block must fit inside `boxed-menu` with no horizontal overflow, and the Back to Town row must remain tappable (per the Session 14 tap bar).

### 5. Private-mode safe and robust

All persistence goes through the existing `localStorage` helpers with try/catch; if storage is unavailable (private mode) the view still renders from in-memory state and never crashes, mirroring existing behavior.

### 6. No AI tells

Any new copy uses plain punctuation, no em dashes, no heavy emoji, on-brand with the Cinder voice.

## Out of scope

- Any rebalance of quest rewards, rotation, boss-day selection, or XP/gold.
- Any new mechanic, new quest templates, or changes to how quests are won.
- Leaderboards, multiplayer, community-submitted games (all roadmap-gated).
- Retroactive backfill of a streak for a player's pre-existing history (they start their visible record from when this story ships). Streak "guessing" about days before a record existed is not attempted.
- Changes to the website, Wordfire, or any other game.

## Acceptance Criteria (BDD)

### Scenario 1: Completed quests appear in the quest log (P1, Riven + Kai)
- **Given** a player has completed and rewarded today's quest, and the additive history has been recorded on that completion
- **When** the player opens the quest-log view from the town hub
- **Then** today's quest appears in the recent list (most recent first) with its label/objective and day, and the list shows at most the most recent N entries

### Scenario 2: Streak is derived and reflects consecutive completions (P1, Kai + Riven)
- **Given** a player completed the previous UTC day's quest and today's quest
- **When** the player opens the quest-log view
- **Then** the current streak shows 2 (consecutive completed days ending today), and a completion on an earlier day with a missed day before today does not count toward the current run

### Scenario 3: View is a pure read (P1, Kai + Scout)
- **Given** the quest-log view is opened
- **When** the recent list and streak are computed and rendered
- **Then** no save data is written and no state is mutated: `flambeee-cinder-save`, `flambeee-cinder-day`, dayState, and quest state are byte-identical before and after opening the view, and level, gold, XP, and wins are unchanged

### Scenario 4: Existing saves stay intact and empty-history saves work (P1, Kai, regression)
- **Given** an existing player save that predates this story (no `completedQuests` field)
- **When** the player loads the game and opens the quest-log view
- **Then** the save loads without error, no field is required to be present, the recent list is empty (or shows only newly recorded completions), and level, gold, XP, and wins are unchanged

### Scenario 5: Quest-log reachable and Back to Town works on mobile (P1, Riven)
- **Given** a mobile/touch viewport with the town hub shown
- **When** the player taps the quest-log row and then taps Back to Town
- **Then** the view opens inside `boxed-menu` with no horizontal overflow, is fully readable, and Back to Town reliably returns to the town square via the delegated tap handler

### Scenario 6: Append happens exactly once per completed quest (P1, Kai + Scout)
- **Given** a quest is completed and rewarded across a reload in the same UTC day
- **When** the daily reset does not occur and the player plays again that day
- **Then** the quest is recorded in the history exactly once (the append is guarded by the same completed/rewarded gate used by the existing payout-once logic)

### Scenario 7: Tone and no-AI-tells (P2, Vigil)
- **Given** the new copy
- **When** any external-visible text from this story is reviewed
- **Then** it contains no em dashes, no heavy emoji, and matches the plain-punctuation, dry-humor Cinder voice

## Technical notes (Quinn)

- **Single game file:** `src/cinder.html` (the repo mirror of `share/Flambeee/games/cinder.html`, currently byte-identical by md5 `931d27f5...`). If a change ships, both copies receive it and are kept in sync (verify with `cmp`), per the standing deploy practice.
- **Additive field recommendation:** `dayState.completedQuests = []`, appended in `completeQuest()` only when `q.completed && !q.rewarded` flips to rewarded (same once gate), entry `{ dayIndex, label, objective }`. Default in `ensureQuestState()` / `checkDailyReset()` to `[]` when absent so existing saves work. Do not move or re-key any existing field.
- **Streak derivation:** count trailing consecutive completed day indexes from today's state + history. Today counts as live if today is completed; otherwise a completed yesterday keeps the streak at its prior value (not yet broken), and a gap resets it. Keep the derivation as a small pure helper (e.g. `computeQuestStreak(dayState)`) that Kai's proof script can extract and test, matching the `kai-story033-pure-read-proof.py` pattern.
- **View placement:** new town-hub row 9 "Quest log" in `renderTownMenu()`, a render function that shows the recent list + streak inside `boxed-menu`, plus a Back to Town row. Follow `renderQuest()`'s structure.
- **Event delegation:** reuse the existing single `#display` click listener; the new row just needs `data-action`. No new listeners, no inline handlers.
- **QA bar (Session 14):** real browser render of the quest-log view on desktop and a narrow mobile viewport with the rows actually tapped. Persistence no-op proven by comparing save state before and after opening the view. Streak correctness proven by simulating consecutive-day saves.
- **Accessibility:** readable at the existing font size, sufficient contrast, no layout regression.

## Visual Description (Quinn)

A new read-only panel reachable from the town square as a ninth row, rendered in the same `boxed-menu` style:

```
=== QUEST LOG ===
Current streak: 2 days
-
Recent quests:
  2 days ago:  Defeat 3 monsters
  1 day ago:   Earn 100 gold from combat
  today:       Defeat a boss (Shadow Knight or stronger)
-
[ 1. Back to Town ]
```

Streak line in the flame accent color (`#ffcc00`), recent-quest entries in the standard text color, day labels as relative dates. On mobile it stacks full-width inside `boxed-menu`, no horizontal scroll, Back to Town stays tappable.

## Open questions

1. **Streak for a missed-today, completed-yesterday player.** Should "yesterday completed, today not yet complete" show the streak as still live (recommended: yes, so the player has most of the day to keep it) or as broken at midnight? Recommend live until the UTC day ends un-completed. CEO/Ember to confirm.
2. **Recent-list length.** Recommend 5 entries. Confirm this matches the visual intent; a longer list adds scroll on mobile.
3. **Whether to record any label/objective copy in the history.** Recording the label/objective lets the log read naturally ("Earn 100 gold from combat"). Confirm we are comfortable persisting the objective text (it is already deterministic and same for all players that day, per Story 025).
4. **Backfill.** Existing players start their visible record from when this ships (no retroactive backfill). Confirm this is acceptable; true backfill is impossible from existing data because past completions are not stored.
