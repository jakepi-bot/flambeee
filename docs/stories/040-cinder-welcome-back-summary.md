# Story 040: Cinder Welcome-Back Return Summary (Session 22, P1)

**Status:** Ready for development (Session 22, second half, 2026-09-20). Implements the Story 039 decision record.
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (retention: make the daily-return loop acknowledge the absence and point straight at today's quest).
**Assigned to:** **Kai** - backend/architecture: the pure-read proof (no save writes, no state mutation, no new persisted field) and wiring guidance for the return check. **Riven** - frontend/views: the return-summary view in Cinder's boxed-menu pattern, with a Back to Town action. **Both devs work in separate git worktrees** (Session 22 process requirement; see the requirements handoff). Scout owns the test plan and real-browser checks. Palette reviews the view for brand and mobile consistency. Vigil reviews the copy.
**Tracked by:** Session 22 plan Priority 2. Implements `docs/stories/039-cinder-away-time-decision-record.md` (decided: no offline accrual; a return summary instead). Grounded in Story 025 (daily quest), Story 033 (daily-return preview), Story 035 (quest log + streak), Story 037 (app-icon badge), and the v0.13.1 `data-action` event delegation pattern.

## Summary

Cinder gives one deterministic quest per UTC day. When a player is away for one or more days, everything about that gap is currently invisible: the game silently starts a new day, the streak is quietly zero, and the player gets no acknowledgement that time passed.

This story makes the game acknowledge the gap, once, the next time the player shows up. When a player returns after **at least one fully missed day**, Cinder shows a one-time welcome-back return summary:

- **Days away** - how many UTC days passed since the last day the player played.
- **Quests missed** - how many daily quests went uncompleted during the absence.
- **Streak status** - kept or broken, stated plainly.
- **Pointer to today's quest** - one line directing the player at today's objective.

Nothing else changes. Per Story 039, there is **no offline resource accrual**: no gold, no XP, no retroactive quest completion, no banked fights, no boss payouts for days the player was gone. The fight economy is untouched. This is **pure presentation**: it reads existing state, renders a boxed-menu view, and writes nothing.

The summary is shown once per gap. After the player dismisses it (or navigates to today's quest), it does not reappear for that same absence.

## Business value

- Closes the weakest link in the daily-return loop: the game now responds to the player coming back instead of pretending they never left.
- Strengthens retention without spending balance: the summary names the cost of the gap (streak broken, quests missed) and immediately points at today's quest, which is the strongest hook back into the habit.
- Zero economy risk. No payout, no progression change, no new persisted field, no balance surface touched.
- Additive and backwards-compatible by construction: legacy and corrupt saves load clean and unchanged, and the summary degrades to nothing when the gap data it needs is unavailable.

## User Story

As a Cinder player who has been away for a day or more,
I want Cinder to tell me how long I was gone, what I missed, whether my streak survived, and what today's quest is,
So that I know exactly where I stand and can pick the habit back up without guessing.

## Requirements

### 1. Trigger: at least one fully missed day

The summary renders only when the player has missed **at least one complete UTC day**. Concretely, let `todayIdx = getDayIndex()`:

- **Missed days = 1 or more** (the last recorded play day is `todayIdx - 2` or earlier, so a whole day passed with no play) -> show the summary **once**.
- **Returning the same day** (last play day is `todayIdx`, or the last play session was `todayIdx - 1` and today is in progress) -> no summary. This keeps the Story 033 "come back tomorrow" flow intact and does not nag a player who never actually left.
- The gate must be computed from state the game already persists. It must not introduce a new persisted field (see requirement 3).

### 2. One-time per gap

- The summary is shown at most once per absence. After the player views it and acts (back to town, or into today's quest), the same absence never re-shows it.
- "One-time" is achieved **without** adding a persisted `seenReturnSummary` flag. Acceptable approaches: render it into the town-hub render path once per session-load (in-memory guard for the life of the page), and/or scope it to the same render the welcome-back check produces. The rule the dev must satisfy: reloading the page during the same day must not produce a second nagging modal loop, and a dev-chosen in-memory guard is acceptable. Any persisted flag requires escalation first (it would change the save shape, which Story 039 forbids).

### 3. Pure read: no new save field, no writes

- **Never write to `flambeee-cinder-save` or `flambeee-cinder-day` from the summary path.** No `saveCharacter()`, no `saveDayState()`, no direct `localStorage.setItem`.
- **No new field** on the character save or the day record. Not `lastSeenReturn`, not `welcomeBackShown`, nothing.
- The summary is a pure reader of existing state (`dayState`, `completedQuests`, `computeQuestStreak`, `getQuestState`, `getDayIndex`).
- **Existing saves load clean with no field loss.** A legacy save (written before this story) loads and plays byte-identical; a newer save read by an older build is unaffected.

### 4. Content of the summary

Exactly these four facts, in this order:

1. **Days away** - the number of UTC days since the player last played. For a gap of one missed day, phrase it naturally ("You were away for a day"), not as a bare counter.
2. **Quests missed** - how many daily quests passed uncompleted during the absence.
3. **Streak status** - "Your streak is broken" when the gap reset it, or "Your streak survived" when it did not (for example the player completed yesterday and missed only today's in-progress day, or the summary fires on a gap that did not break a recorded run). The summary must state which, not imply it.
4. **Pointer to today's quest** - one line naming today's objective and directing the player at the "Today's quest" hub row, using the same quest text the hub already renders.

### 5. No economy or balance change

Per Story 039 (D1, D2): on return, gold, XP, bank, level, wins, quest progress, quest rewards, fight counts, and monster pools are **unchanged** by this story. The summary pays nothing and grants nothing. Reading the summary must not advance a quest, complete a quest, or touch the payout-once gate.

### 6. No notifications, no push, no permission prompt, no install nag

- No `Notification.requestPermission()`, no push subscription, no service worker message channel, no scheduled reminder.
- No install prompt, banner, modal, or nag promoting installation.
- The only new surface is the return summary **inside Cinder, after the player has already opened the game**.

### 7. Mobile-safe, boxed-menu pattern, no inline onclick

- The summary renders as a `boxed-menu` block, consistent with the existing Cinder views.
- All interactive controls use the v0.13.1 `data-action` event delegation pattern. No inline `onclick`, ever (issue #46).
- No horizontal overflow at 375x667. The primary action (**Back to Town**) must be reachable and tappable.

### 8. Copy: plain punctuation, no em dashes, no heavy emoji

All new user-visible strings use plain punctuation, no em dashes, and no heavy emoji, in Cinder's dry voice. At most a single emoji if it genuinely fits; preferred: none.

### 9. Graceful degradation

The summary must never block play and never throw. Private mode, unavailable storage, a corrupt day record, or an unreadable streak must all degrade to either a correct summary from whatever valid state exists, or no summary at all. Missing data is never a crash and never a blocking error.

## Out of scope

- Any offline resource accrual (gold, XP, quests, boss fights, banked or stacked fights). Decided against in Story 039; reversal requires CEO sign-off.
- Any balance, reward, rotation, payout, monster-pool, or level-curve change.
- Any new persisted field or save-shape change.
- Any notification, push, email, or reminder.
- Any install promotion.
- Any change to the Story 033 come-back-tomorrow preview or the Story 035 quest log, beyond not regressing them.
- Any hub redesign or new town-hub row.

## Acceptance Criteria (BDD)

### Scenario 1: Return after one fully missed day shows the summary once (P1, Kai + Riven)
- **Given** a player whose last recorded play day is two UTC days ago (one whole day fully missed)
- **When** the player opens Cinder today
- **Then** the welcome-back summary renders exactly once, naming 1 day away, the quests missed, the streak status, and today's quest

### Scenario 2: Same-day return shows no summary (P1, Kai + Scout)
- **Given** a player who played earlier today, or whose last play was yesterday and today is still in progress with no fully missed day
- **When** the player reloads or reopens Cinder
- **Then** no welcome-back summary appears, and the town hub renders exactly as it does today

### Scenario 3: One-time per gap, no repeat nagging (P1, Riven + Scout)
- **Given** the summary has been shown for a gap and the player has acted on it (Back to Town, or into today's quest)
- **When** the player navigates back to the town hub within the same session, and then reloads the page the same day
- **Then** the summary is not shown again as a nagging loop, and play continues normally

### Scenario 4: The summary path writes nothing (P1, Kai, proof)
- **Given** any state that produces a summary
- **When** the summary is computed and rendered
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical before and after, and a static scan of the summary path finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, or state-mutating `character.` / `dayState.` writes

### Scenario 5: Legacy save loads clean with no field loss (P1, Kai, regression)
- **Given** a legacy save written before this story (no return-summary-related fields anywhere)
- **When** the game loads
- **Then** it loads without error, level, gold, XP, bank, wins, and the day record are unchanged, and the only difference is whether the summary renders from existing state

### Scenario 6: No economy or balance change on return (P1, Kai + Scout)
- **Given** a player returning after several missed days
- **When** the summary is shown and dismissed
- **Then** gold, XP, level, bank, wins, quest progress, and fight counts are identical to their values immediately before the summary, and nothing was paid or granted

### Scenario 7: Quests missed is accurate (P1, Kai + Scout)
- **Given** a known absence window
- **When** the summary reports quests missed
- **Then** the count equals the number of UTC days in the window on which no quest was completed, derived from existing state and never invented

### Scenario 8: Streak status is stated, not implied (P1, Riven + Scout)
- **Given** an absence that broke a recorded streak
- **When** the summary renders
- **Then** it explicitly says the streak is broken; and given an absence that did not break the recorded run, it explicitly says the streak survived

### Scenario 9: Private mode / storage unavailable (P1, Kai)
- **Given** the browser is in private mode or storage is unavailable, so the existing localStorage helpers are throwing and swallowing
- **When** the game loads and the player plays
- **Then** the game runs from in-memory state, the summary path behaves the same as with storage, and nothing throws

### Scenario 10: Corrupt day state degrades gracefully (P1, Kai + Scout)
- **Given** a corrupt day record (`quest` missing or not an object, `completedQuests` not an array, non-numeric `dayIndex`)
- **When** the game loads
- **Then** the game loads clean, the summary either shows a correct summary from the valid parts or does not show at all, no exception is raised, and no corrupt field is rewritten beyond the existing `ensureQuestState()` backfill

### Scenario 11: Returning many days later (P1, Riven + Scout)
- **Given** a player returning after a long absence (for example 30 or more missed days)
- **When** the summary renders
- **Then** the wording stays sane and readable, the layout does not overflow, no unwieldy number is dumped as a bare counter, and the summary points at today's quest

### Scenario 12: No notifications, no push, no permission prompt, no install nag (P1, Vigil + Scout)
- **Given** the whole story's code
- **When** it is scanned and exercised in a browser
- **Then** it contains no `Notification` permission request, no `pushManager`, no subscription code, and no permission prompt or install prompt appears at any point in load, summary, or play

### Scenario 13: Mobile-safe, Back to Town tappable (P1, Riven + Scout)
- **Given** the summary is rendered at a narrow mobile viewport (375x667) and on desktop
- **When** the player taps or clicks the Back to Town action
- **Then** the tap is handled by the delegated `data-action` listener, the hub renders, there is no horizontal overflow, and there is no inline `onclick` anywhere in the new markup

### Scenario 14: Tone and no-AI-tells (P2, Vigil)
- **Given** any new user-visible copy introduced by this story
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and matches the plain-punctuation, dry-humor Cinder voice

## Technical notes (Quinn)

- **Single game file:** `src/cinder.html` is the source of truth. The deploy mirror `share/Flambeee/games/cinder.html` (ABSOLUTE path, outside the repo) must end the session byte-identical to `src/cinder.html` (`cmp` PASS). Verified identical at the start of this session.
- **Existing state to read (do not change):**
  - `getDayIndex()` = `Math.floor(Date.now() / 86400000)` (pure UTC day index).
  - `loadDayState()` / `saveDayState()` are the only `flambeee-cinder-day` accessors. The summary path must read, never write.
  - `dayState.completedQuests` is the additive history array (Story 035), `Array.isArray`-guarded, defaulted `[]` in `ensureQuestState()`, `checkDailyReset()`, and `createCharacter()`. Each entry carries a numeric `dayIndex` and the quest's `objective`/`label`.
  - `computeQuestStreak(dayStateRef)` is a pure helper that counts trailing consecutive completed day indexes. It is already the correct anchor for "kept or broken".
  - `getQuestState()` returns the live `dayState.quest` (`{ progress, completed, rewarded }`), backfilled by `ensureQuestState()`.
  - `getActiveQuest()` / `determineQuestForDay(dayIndex)` give the day's quest template (label, objective) for the today's-quest pointer.
  - `checkDailyReset()` builds a fresh day record when `dayState.dayIndex !== getDayIndex()`; at that moment the **previous** day record is overwritten, so the absence window must be computed **before** the new day record replaces it, or from `completedQuests` history, which survives the reset.
- **Important implementation hazard (flag for Kai):** `checkDailyReset()` replaces `dayState` wholesale. Any "days away" computation that reads `dayState.dayIndex` after the reset will read today's index, not the last play day. The dev must capture the last play day before the reset, or derive the window from `completedQuests` plus today's index. This is the single most likely defect in the story, and the proof should cover it explicitly.
- **Wiring point:** `init()` calls `checkDailyReset()` then `ensureQuestState()` before rendering the town menu. The welcome-back check belongs on that path, and the summary may render into the hub render or as its own boxed-menu view whose Back to Town action returns to `renderTownMenu()`. Riven owns the final presentation decision; Kai owns the pure-read gate and the proof that the gate writes nothing.
- **Recommended shape:** one small helper that (a) computes the last play day index from existing state (before the reset overwrites it), (b) computes days away and quests missed from `completedQuests` and the day index, (c) reads streak status from `computeQuestStreak(dayState)`, (d) returns a boolean "should show" plus the strings, and (e) never calls `saveCharacter` or `saveDayState`.
- **Proof expectation (Session 14 bar):** Kai provides a node-based proof script plus a static scan (same pattern as the Story 033/035/037 proofs). Extract the gate and the summary computation, assert: no summary for a same-day return; summary for a one-day gap; correct days-away and quests-missed counts across multi-day gaps; correct kept/broken streak status; the last-play-day capture is correct across `checkDailyReset()`; no-write assertions on the summary path. Expected exit code 0.
- **Worktree rule (Session 22):** Kai and Riven must each work in a **separate git worktree** (`git worktree add` under a temp dir outside the main tree). Sessions 20 and 21 both had branch collisions from the shared single working tree; this is the prescribed fix.
- **QA bar:** real browser render at desktop and 375x667 with a real tap on Back to Town, plus at least one run with a seeded multi-day gap and one run with a corrupt day record. Instrument or stub nothing that changes behavior; assert exact stored values before and after.

## Visual Description (Quinn)

The return summary uses Cinder's existing boxed-menu pattern, so it looks like every other Cinder view (dark `#1a1a2e` panel, `2px solid #444` border, yellow `#ffcc00` centered header, dashed divider, muted text).

```
+------------------------------------------------+
|                                                |
|            === WELCOME BACK ===                |   <- yellow .header, centered
|                                                |
|   You were away for 3 days.                    |   <- days away, plain sentence
|   2 quests went uncompleted while you were     |   <- quests missed
|   gone.                                        |
|   Your streak is broken.                       |   <- streak status, stated plainly
|                                                |
|   ------------------------------------------   |   <- .divider (dashed)
|   Today's quest: Defeat 3 monsters             |   <- today's objective, same text as row 8
|                                                |
|   [ Back to Town ]                             |   <- primary action, data-action delegated
|                                                |
+------------------------------------------------+
```

Rules for the visual:

- **One panel, four facts, one action.** No nested boxes, no carousel, no animation beyond what the existing menu views use. It is a summary, not a ceremony.
- **Back to Town is the primary and expected action**, rendered as a `boxed-menu` row with a `data-action` attribute, tappable at 375px width with no horizontal overflow. If a second affordance is offered (for example "Go to today's quest"), it is a second row in the same list, not a competing button style.
- **Numbers read as sentences.** For a one-day gap: "You were away for a day." For long gaps: "You were away for a while." A bare "30" is never dumped on its own line.
- **Streak line is explicit**: either "Your streak is broken." or "Your streak survived." Never implied, never guessed at.
- **Muted secondary text** uses the existing muted style; no new colors, no new fonts, no new brand elements. Palette reviews for brand consistency and mobile readability.
- **No new hub row, no banner, no notification dot, no install nag.** The town hub's existing rows are unchanged; the summary is a view the player sees once, then returns from.
- **Plain punctuation, no em dashes, no heavy emoji** anywhere in the panel.

## Open questions

1. **One-time guard mechanism (recommended, confirm in review).** Recommended: an in-memory guard for the life of the page, so the summary shows once per load and not on every hub render, with no persisted flag (a persisted flag would change the save shape, which Story 039 forbids). If the team decides a persisted flag is genuinely required, it must be escalated as a decision-record amendment first, not implemented in this story.
2. **Exact streak-status rule for a one-day gap.** Recommendation: report "survived" only when `computeQuestStreak(dayState)` is greater than zero at render time; otherwise "broken". This uses the shipped helper and invents no new rule. Confirm with Scout that the BDD scenario covers both branches.
3. **Second affordance ("Go to today's quest").** Recommendation: include it as a second row, since the pointer is part of the Story 039 decision. If Riven judges it adds clutter at 375px, Back to Town alone is acceptable and still satisfies requirement 4 item 4 (the pointer is then text, not a control). Parent to confirm during the dev wave rather than blocking requirements.

No other ambiguities. Every requirement here is grounded in `flambeee-team/session-plan.md` Priority 2 and the Story 039 decision record; nothing beyond those was invented.
