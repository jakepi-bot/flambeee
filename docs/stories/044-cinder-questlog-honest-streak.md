# Story 044: Cinder Quest Log, Honest Streak Line and Recent-Quests Count on a Return Day (Session 24, P1)

**Status:** Ready for development (Session 24, first half, 2026-09-25). Corrective. Fixes the one live defect that makes the quest log contradict the welcome-back panel on the same screen, in the same session file. Does not amend the Story 039 decision record.
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (retention: the returning player is the player the loop exists to recover, and today the game tells that player their streak is 0 one keypress after telling them it survived).
**Assigned to:** **Kai** - pure-read streak source and proof: the recorded-history derivation, the reset hazard proven directly against the shipped code, and the no-write / no-new-field proof. **Riven** - the quest-log view and copy: the rendered Current streak line and the recent-quests list rendering. **Both devs work in separate git worktrees.** Scout owns the test plan and the real-browser checks. Palette checks the panel for brand and mobile consistency. Vigil checks the copy and the truthfulness of the number in both cases.
**Tracked by:** Session 24 plan Priority 1. Grounded in Story 035 (the quest log and `computeQuestStreak()`), Story 040 (the welcome-back window and its `lastPlayIdx` anchor), Story 042 (the honest streak line and the anchor it established), Story 033 (the come-back-tomorrow preview), Story 037 (the app-icon badge), and the v0.13.1 `data-action` delegation pattern. Constrained by `docs/stories/039-cinder-away-time-decision-record.md`.

## Summary

Story 042 fixed the welcome-back panel so it reports the streak from the player's **recorded completion history**, anchored on the last recorded play day. It left the quest log alone, on purpose, as a "do not regress" item. That was the right scope call for that story and it left a live contradiction behind.

`renderQuestLog()` (`src/cinder.html:554`) computes its streak with `computeQuestStreak(dayState)`. That helper (`src/cinder.html:382`) anchors on **today when today's quest is complete**, and on **yesterday when today is incomplete**. On the load of a gap day, `checkDailyReset()` has just rebuilt `dayState` wholesale with `completedQuests: []`, and today's quest is not complete. So the anchor is yesterday, that day carries no recorded completion, the loop exits immediately, and the streak reads **0**.

The welcome-back panel on the same screen says **"Your streak survived."** because Story 042 anchored it on `lastPlayIdx`, drawn from the loaded record's history. Two surfaces, one session file, directly contradictory, and the zero is the false one: the quest log is reporting the post-reset record instead of the history the player actually accumulated. Reachable by anyone who returns after a gap and opens row 9 from the town hub.

This story changes one thing: **which number the quest log renders, and where that number comes from.** No mechanic changes, no field is added, nothing is written, and `checkDailyReset()` is not touched.

## Business value

- Removes a contradiction the player can see in one sitting: the same screen, in the same session, currently tells a returning player their run survived and then tells them their streak is 0.
- The zero is the wrong number, and it is the number a returning player is most likely to read as "your history was lost". That is the exact trust failure the retention work exists to prevent.
- Zero new product surface. One read path, one derived number, no new row, panel, field, or write. The day record shape is untouched and the fix is provable to read only.
- Keeps the byte-safety discipline intact: read-only, provable, and the deploy mirror stays byte-identical after the merge.

## User Story

As a Cinder player returning after one or more missed days,
I want the Quest Log to show the same, true streak the welcome-back panel just showed me,
So that the game never tells me my own history was lost when it was not, and I can trust the number on my own log.

## Requirements

### 1. The quest log's streak is derived from the recorded completion history

- The Current streak value rendered by `renderQuestLog()` must come from the player's **recorded completion history** in the loaded day record (`dayState.completedQuests`), anchored on the **last recorded play day** - the same anchor Story 042 established in `computeAwayWindow()`: the maximum valid candidate drawn from `dayState.dayIndex` and the valid history entries' `dayIndex` values.
- Concretely: build the set of recorded completed day indexes, take the last recorded play day, walk back while each successive index is present, and report the run length. That value is the Current streak.
- **The quest log and the welcome-back panel must never disagree on the same day.** On any state where both surfaces are reachable, the streak the log prints and the survived/broken status the panel prints must describe the same recorded run. Where the panel says the run survived, the log's number is at least 1 and equals the run length; where the panel says the run is broken, the log's number is 0.
- The status must **never** be taken from the post-reset rebuilt record for the purpose of this line. The wholesale rebuild in `checkDailyReset()` is exactly what makes the current number wrong, and this line must not depend on a value the rebuild produces.
- The helper may reuse the **shape** of the trailing-run scan in `computeQuestStreak()` (`src/cinder.html:382-410`), anchored on the last recorded play day instead of on "today or yesterday". It must not change what `computeQuestStreak()` returns, and it must not modify that function. `computeQuestStreak()` stays exactly as shipped, because the Story 035 proof and its 15 node assertions ride on it.

### 2. The recent-quests list stays correct

- The recent-quests list must keep rendering the last entries **most recent first**, capped at 5, from `dayState.completedQuests` (`.slice(-5).reverse()`), exactly as it renders today.
- The list must be unaffected by whatever change this story makes to the streak derivation: the same history must produce the same list before and after this story, on every seeded case.
- Relative day labels (`today` / `yesterday` / `N days ago`) keep their existing behavior.

### 3. A genuine gap still reads 0, in both surfaces

- When the player's recorded run genuinely does not reach the last recorded play day - a hole between recorded completions, or no recorded completion at all - the quest log reads 0 **and** the welcome-back panel reads "Your streak is broken." The two agree.
- A first-ever player with no history reads 0 in the quest log, with the existing empty-state line, and no crash.

### 4. In-progress-today still reads the preserved run

- When today's quest is not yet complete and yesterday carries a recorded completion, the log keeps reading the preserved run (not 0). This is the case `computeQuestStreak()` handles today by anchoring on yesterday, and it must keep working after the change.
- When today's quest **is** complete, the run includes today, as it does today.

### 5. No new persisted field, no writes on the read path

- **No new field** on the character save or on the day record. Not a streak cache, not a `lastStreak`, not a version marker, nothing.
- **Never write to `flambeee-cinder-save` or `flambeee-cinder-day` from the quest-log read path.** No `saveCharacter()`, no `saveDayState()`, no direct `localStorage.setItem`. Opening row 9 must leave both stored values byte-identical.
- The **stored day record shape is unchanged.** `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }` stays exactly as it is today; no field is added, renamed, or removed.
- **Do not change `checkDailyReset()`.** Its behavior and its writes are untouched by this story.
- Escalation rule (binding): **if the only correct fix requires a persisted field, that is a Story 039 decision-record amendment plus CEO sign-off. Escalate; do not implement it.** Do not add the field "temporarily", and do not ship a partial version of it.

### 6. Away-window gate semantics and the Story 042 panel stay intact

- Same-day return and next-day return stay quiet, and the welcome-back panel keeps rendering exactly as Story 042 shipped it. This story changes the quest log only.
- The Story 042 panel's own streak line is not re-derived, re-worded, or re-anchored by this story. The two surfaces must agree; agreeing must be achieved by making the log read the recorded history, not by weakening the panel.

### 7. No economy, no UI surface, no notifications

- No change to gold, XP, level, bank, wins, quest progress, rewards, fight counts, quest rotation, or monster pools. The quest log pays nothing and grants nothing.
- No new town-hub row, no banner, no notification dot, no push, no service worker message, no permission prompt, no install prompt or nag. Row 9 stays the only entry point and the panel keeps its existing `boxed-menu` styling.
- No new colors, fonts, images, or brand elements.

### 8. Mobile-safe, boxed-menu pattern, no inline onclick

- The quest log remains a `boxed-menu` block consistent with the other Cinder views.
- All interactive controls keep the v0.13.1 `data-action` event delegation pattern (`src/cinder.html:1326-1331`). No inline `onclick`, ever (issue #46).
- No horizontal overflow at 375x667, and Back to Town stays reachable and tappable.

### 9. Copy: plain punctuation, no em dashes, no heavy emoji

- Only the streak **number** is in scope for change. The line's existing shape (`Current streak: N days`, singular `day` when N is 1) is unchanged, and every other string in the panel is unchanged.
- Every new or changed user-visible string uses plain punctuation, no em dashes, and no heavy emoji, in Cinder's dry voice.

### 10. Graceful degradation

- Corrupt or missing history (`completedQuests` not an array, entries with a non-numeric or non-finite `dayIndex`), a non-object day record, private mode, and unavailable storage must all degrade to a correct number from whatever valid state exists, or to 0, and never to an exception or a blocking error.
- Legacy day records (no `completedQuests`), partial records, and `null` must load the log cleanly, exactly as they do today.
- A failed streak computation must never leave the player stuck without the hub: the fallback is the normal town render.

## Out of scope

- Any change to `checkDailyReset()` - its logic, its writes, or the shape of the record it builds.
- Any change to `computeQuestStreak()` or its return value. It stays byte-identical to v0.21.0; the Story 035 proof rides on it.
- Any change to the Story 042 welcome-back panel, its wording, or its anchor.
- Any banked, preserved, or restored streak as a mechanic. This story changes what the log **reports**, never what the game **keeps**.
- Any new history field, any extension of `completedQuests`, any change to the stored day record shape, and any new persisted field of any kind.
- Any offline resource accrual (gold, XP, quests, boss fights). Decided against in Story 039; reversal requires CEO sign-off.
- Any balance, reward, rotation, payout, monster-pool, or level-curve change.
- Any notification, push, email, permission prompt, or install nag.
- Any new town-hub row, banner, tooltip, or notification dot.
- Any change to the Story 033 come-back-tomorrow preview or the Story 037 app-icon badge, beyond not regressing them.

## Acceptance Criteria (BDD)

### Scenario 1: Intact recorded run reads the true streak in the log (P1, Kai + Riven)
- **Given** a player who returns after a gap of at least one fully missed day
- **And** the loaded day record carries a recorded run that reaches the last recorded play day (for example `completedQuests` entries for day indexes T-4, T-3, T-2 and `dayIndex: T-2`, where T is today)
- **When** the player opens the Quest Log (hub row 9)
- **Then** the Current streak line reads the run length (3 in this example), not 0

### Scenario 2: The log and the welcome-back panel agree on the same day (P1, Kai + Riven, the story's core assertion)
- **Given** the same loaded day record used in Scenario 1
- **When** the welcome-back panel renders and, on the same page state, the Quest Log renders
- **Then** the panel reads "Your streak survived." and the log reads a streak of at least 1 equal to the recorded run length, and the two surfaces do not contradict each other

### Scenario 3: A genuine gap resets to 0 in both surfaces and they agree (P1, Kai + Scout)
- **Given** a player whose recorded run genuinely does not reach the last recorded play day (for example `completedQuests` entries for day indexes T-6 and T-5 and `dayIndex: T-2`, so T-4 is missing between recorded completions)
- **When** the welcome-back panel renders and, on the same page state, the Quest Log renders
- **Then** the panel reads "Your streak is broken." and the log reads 0, and the two agree

### Scenario 4: First-ever player reads 0 with no crash (P1, Kai + Scout)
- **Given** a player with no history at all (no `completedQuests`, `dayIndex` today, today's quest not complete)
- **When** the player opens the Quest Log
- **Then** the Current streak line reads 0, the existing empty-state line ("No quests recorded yet. Finish today's quest to start your log.") renders, and nothing throws

### Scenario 5: The streak source is the recorded history, never a post-reset record (P1, Kai, proof)
- **Given** a stale stored day record (its `dayIndex` is not today) that carries recorded completions
- **When** the quest log's streak is computed from the loaded record's history and again from the record after `checkDailyReset()` has rebuilt it
- **Then** the value the log renders comes from the loaded record's history and is unchanged by the rebuild, and the rebuilt record's empty `completedQuests` plays no part in the rendered number

### Scenario 6: In-progress today still reads the preserved run (P1, Kai + Scout)
- **Given** today's quest is not yet complete and yesterday carries a recorded completion (with the run continuing back from yesterday)
- **When** the player opens the Quest Log
- **Then** the Current streak line reads the preserved run length, not 0

### Scenario 7: Completed today joins the run (P1, Kai + Scout)
- **Given** today's quest is completed and rewarded, and the days before it carry recorded completions
- **When** the player opens the Quest Log
- **Then** the streak includes today, reading one more than the run ending yesterday

### Scenario 8: The recent-quests list stays correct (P1, Riven + Scout)
- **Given** a day record with 7 recorded completions
- **When** the player opens the Quest Log
- **Then** the list shows the last 5 entries most recent first, with their relative day labels, and the list is identical to the pre-story rendering for the same history

### Scenario 9: Legacy, corrupt, and partial records degrade cleanly (P1, Kai + Scout, regression)
- **Given** a legacy day record with no `completedQuests`, and separately a corrupt record (`completedQuests` a string, an entry with a non-numeric `dayIndex`, `dayIndex` not a number, `dayState` null)
- **When** the game loads and the player opens the Quest Log
- **Then** it renders without error, the streak reads a correct value from the valid parts or 0, the recent-quests list renders or falls back to the empty-state line, and no exception is raised

### Scenario 10: Storage unavailable or private mode (P1, Kai)
- **Given** the browser is in private mode or storage is unavailable, so the existing localStorage helpers are throwing and swallowing
- **When** the game loads and the player opens the Quest Log
- **Then** the game runs from in-memory state and the log behaves the same as with storage, and nothing throws

### Scenario 11: The quest-log read path writes nothing and adds no field (P1, Kai, proof)
- **Given** any state that renders the Quest Log
- **When** the player opens row 9 and the log renders
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical before and after, a static scan of the quest-log and streak path finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, or state-mutating `character.` / `dayState.` writes, and no new field name appears anywhere in the diff

### Scenario 12: The day record shape is unchanged (P1, Kai + Scout)
- **Given** a save written by v0.21.0 and a save written by the build with this story applied
- **When** each is loaded and the raw JSON is compared
- **Then** the stored day record has exactly the same field set as before (`dayIndex`, `fightsUsed`, `innHealsUsed`, `quest`, `completedQuests`), with no added, removed, or renamed field

### Scenario 13: `checkDailyReset()` is byte-identical to v0.21.0 (P1, Kai, proof)
- **Given** the diff for this story in `src/cinder.html`
- **When** the code is inspected
- **Then** `checkDailyReset()` is textually unchanged from v0.21.0, and the story adds no history field and no change to the record it builds

### Scenario 14: `computeQuestStreak()` is unchanged (P1, Kai, proof)
- **Given** the diff for this story in `src/cinder.html`
- **When** the code is inspected
- **Then** `computeQuestStreak()` is textually unchanged from v0.21.0 and returns the same values for the same inputs as before the story

### Scenario 15: Story 042 welcome-back panel not regressed (P1, Scout, regression)
- **Given** a multi-day gap with an intact recorded run, and separately one with a genuine hole
- **When** the welcome-back panel renders
- **Then** it reads "Your streak survived." and "Your streak is broken." respectively, exactly as Story 042 shipped, with the days-away and quests-missed sentences and both rows unchanged

### Scenario 16: Story 033 come-back-tomorrow preview not regressed (P1, Scout, regression)
- **Given** a player who completes and collects today's quest
- **When** the quest view renders
- **Then** the "Tomorrow: ..." preview and its "Come back after midnight to start it." line render exactly as before

### Scenario 17: Story 037 app-icon badge not regressed (P1, Scout, regression)
- **Given** an installed player with the quest pending, and again after completing and collecting it
- **When** the game loads, plays, and the quest completes
- **Then** the badge path behaves exactly as before (1 while pending, cleared on completed and rewarded)

### Scenario 18: Same-day and next-day returns stay quiet (P1, Kai + Scout, regression)
- **Given** a player who played earlier today, or whose last recorded play day is yesterday with nothing fully missed
- **When** the player opens or reloads Cinder and then opens row 9
- **Then** no welcome-back panel renders in those cases, the log renders its streak, and the hub renders exactly as the pre-story build renders it

### Scenario 19: Escalation, not implementation, if a persisted field is needed (P1, Vigil + Kai)
- **Given** the whole story's code and diff
- **When** it is reviewed
- **Then** it proves the fix was achieved with existing state only, and if any part of the design had required a persisted field the team escalated it as a Story 039 amendment instead of implementing it, with no persisted field shipped

### Scenario 20: No notifications, no push, no permission prompt, no install nag (P1, Vigil + Scout)
- **Given** this story's code
- **When** it is scanned and exercised in a browser
- **Then** it contains no `Notification` permission request, no `pushManager`, no subscription code, and no permission prompt or install prompt appears at any point in load or in the log path

### Scenario 21: Mobile-safe, Back to Town tappable, no inline onclick (P1, Riven + Scout)
- **Given** the Quest Log rendered at 375x667 and on desktop
- **When** the player taps Back to Town
- **Then** the tap is handled by the delegated `data-action` listener, the town hub renders, there is no horizontal overflow, and no inline `onclick` appears anywhere in the markup

### Scenario 22: Tone and no-AI-tells (P2, Vigil)
- **Given** any new or changed user-visible copy introduced by this story
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and matches the plain-punctuation, dry-humor Cinder voice

## Technical notes (Quinn)

Verified against the shipped `src/cinder.html` at v0.21.0 by reading the code, not by inferring from the release notes. Repo `main` at `d290f82`. Live deploy mirror `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` was byte-identical to `src/cinder.html` at session start (`cmp` exit 0).

- **Single game file:** `src/cinder.html` is the source of truth. The deploy mirror is a **separate file outside the repo** at the ABSOLUTE path `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. It must end the session byte-identical to `src/cinder.html` (`cmp` exit 0, record the sha256). Never write a relative `share/...` path from inside the repo.
- **The defect, precisely.** `renderQuestLog()` (`:554`) sets `const streak = computeQuestStreak(dayState);`. `computeQuestStreak()` (`:382-410`) reads `dayStateRef.quest.completed` to decide `live`, sets `cursor = live ? todayIdx : todayIdx - 1`, and walks back while `done[cursor]`. On the load of a gap day, `checkDailyReset()` (`:656`) has already reassigned `dayState` to `{ dayIndex: today, fightsUsed: 0, innHealsUsed: 0, quest: { progress: 0, completed: false, rewarded: false }, completedQuests: [] }`. So `live` is false, the anchor is `todayIdx - 1`, that index has no entry in the empty history, and the loop exits with 0. The log prints `Current streak: 0 days` while `renderWelcomeBack()` on the same screen prints "Your streak survived." from `awayWindow.streakSurvived`, which Story 042 derived from the loaded history anchored on `lastPlayIdx`.
- **The fix shape (Kai owns the final form).** Derive the log's number from the **last recorded completion run** in the loaded day record's `completedQuests`, anchored on `lastPlayIdx` exactly as `computeAwayWindow()` already computes it: `lastPlayIdx` = the max of the valid `dayState.dayIndex` and the valid history entries' `dayIndex` values; build the set of recorded day indexes; walk back from `lastPlayIdx` while each successive index is present; the run length is the number. Reuse the **shape** of the trailing-run scan in `computeQuestStreak()`; do not call it for this answer, do not modify it. Keep the helper pure and extractable, matching the Story 033/035/037/040/042 proof pattern.
- **The anchor, and one honest limit on agreement.** Story 042 anchored the panel on the **last recorded play day** (which includes the raw `dayIndex` stamp, i.e. a day the player loaded but did not complete). The quest log is opened **after** `checkDailyReset()`, so `dayState.dayIndex` is today. Anchoring the log on `lastPlayIdx` computed from the loaded record is therefore not literally the same anchor unless the anchor is taken from a record captured before the reset. Kai must choose the concrete mechanism and state it in the proof. Two viable shapes, both read-only: (a) compute the log's streak from the **loaded (pre-reset) record captured at init** and keep that number in memory, or (b) anchor the log on the **last recorded completion day** from `dayState.completedQuests` (post-reset, still intact for the history). Shape (a) reproduces the panel's anchor exactly and makes the agreement provable on every input. Shape (b) is simpler but is one day lower than the panel's number when the raw stamp is newer than the newest completion. Whichever Kai picks, the story's binding requirement stands: **the two surfaces must not contradict each other on the same day**, and Scenario 2 checks exactly that. If neither shape can produce non-contradiction without a persisted field, the escalation rule applies.
- **Where the log's number is produced:** `renderQuestLog()` at `:554` (`const streak = computeQuestStreak(dayState);`), rendered at `:572` as `Current streak: ' + streak + (streak === 1 ? ' day' : ' days')`. The recent-quests list is at `:556-568` (`completed.slice(-5).reverse()`, `dayLabelForIndex()` at `:528`).
- **Existing state to read (do not change):** `getDayIndex()` at `:625`; `loadDayState()` / `saveDayState()` as the only `flambeee-cinder-day` accessors; `dayState.completedQuests` entries each carrying a numeric `dayIndex` plus `label` / `objective` (`completeQuest()`, `:317-321`); `ensureQuestState()` at `:249`; `computeQuestStreak()` at `:382` (unchanged); `computeAwayWindow()` at `:416` and its `lastPlayIdx` derivation at `:427-446`; `shouldShowWelcomeBack()` at `:509`; `renderWelcomeBack()` at `:520`; the `init()` load path at `:1300-1320` where `rawDayState` is captured before `checkDailyReset()`; `handleMenuClick` routing to `case 'questlog'`; the delegated click listener at `:1326-1331`.
- **What "no writes" means here.** The load path legitimately runs `checkDailyReset()` (which may call `saveDayState()` for a new day) and `ensureQuestState()` (which may call `saveDayState()` when a legacy record lacks `quest` or `completedQuests`). Those are **pre-existing v0.21.0 behaviors** and are not part of the quest-log read path this story owns. Scenario 11's byte-identity claim is therefore scoped to opening row 9 and rendering the log: with a well-formed day record already stamped for today, opening the log adds no write.
- **Proof expectation (Session 14 bar):** Kai provides a node-based proof script plus a static scan (same pattern as the Story 033/035/037/040/042 proofs, extracting the shipped functions into a sandbox). It must assert: the log's number equals the recorded run length for an intact run ending at the last play day; 0 for a hole in the run; 0 for no history; the preserved run when today is incomplete and yesterday completed; today included when today completes; log and panel status non-contradiction on every seeded case; the log's number unchanged by the wholesale rebuild; the recent-quests list identical to the pre-story rendering; no forbidden writes; no new field name in the diff; `checkDailyReset()` and `computeQuestStreak()` textually unchanged. Expected exit code 0.
- **QA bar:** real browser at desktop and 375x667 with a real tap on row 9 and on Back to Town, a seeded multi-day gap run for each branch, a same-page-render check that reads **both** the panel and the log and asserts agreement, a control run against the pre-044 build for the regression scenarios, and raw `flambeee-cinder-save` / `flambeee-cinder-day` values captured before and after opening the log.
- **Worktree rule (Session 24, fourth session running):** Kai and Riven must each work in a **separate git worktree** (`git worktree add` under a temp dir outside the main tree). Story 044 again puts both devs on one file (`src/cinder.html`), which is the highest-risk story shape in the repo. The two halves here are separable: Kai owns the streak source and the proof; Riven owns the rendered line and the list rendering. **Watch the duplicate-solution hazard:** Session 23 had two devs independently produce correct but duplicate helpers in one file. Agree on one helper name and one owner in the Wave 3 brief, or make the reconciliation step explicit before merge.
- **Peer review:** Kai and Riven review each other's work in the usual direction before merge.

## Visual Description (Quinn)

The panel is Cinder's terminal text in a boxed menu, reached from the town hub as row 9. It keeps the existing Story 035 styling exactly: dark `#1a1a2e` panel, `2px solid #444` border, centered yellow `#ffcc00` `.header`, dashed `.divider`, plain body text, `.menu-row` rows with `<span class="num">` number prefixes. The changed element is one number inside one existing line.

```
+------------------------------------------------+
|                                                |
|            === QUEST LOG ===                   |   <- yellow .header, centered (unchanged)
|                                                |
|   Current streak: 3 days                       |   <- CHANGED: true value, same line, same style
|                                                |
|   ------------------------------------------   |   <- .divider (unchanged)
|   Recent quests:                               |   <- (unchanged)
|   yesterday: Defeat 5 monsters                 |   <- list, most recent first (unchanged)
|   2 days ago: Earn 50 gold from combat         |   <- (unchanged)
|   3 days ago: Slay the boss                    |   <- (unchanged)
|   4 days ago: Defeat 5 monsters                |   <- (unchanged)
|   5 days ago: Earn 50 gold from combat         |   <- capped at 5 (unchanged)
|                                                |
|   ------------------------------------------   |   <- .divider (unchanged)
|   1. Back to Town                              |   <- .menu-row, data-action="1" (unchanged)
|                                                |
+------------------------------------------------+
```

What changes, and what does not:

- **Changes (one number):** the value in `Current streak: N days`. Today it reads `0` on a return day even when the recorded run is intact; after this story it reads the recorded run length, and it reads `0` only when the run genuinely ended. The line's text, position, style, singular/plural handling, and length class are unchanged.
- **Unchanged:** the header, the recent-quests label and list (order, cap, labels), the divider, the Back to Town row, the `data-action` delegation, the colors, the fonts, the layout, the 375x667 behavior, and the absence of any new hub row, banner, dot, or nag.
- **Never shown:** the word "streak" with an icon, a flame, or any flourish. One plain line with a number, as it renders today.

Palette checks that the panel still reads as one Cinder view at 375x667 and that the changed number does not disturb the layout, the wrapping, or the contrast of the surrounding text. Vigil checks that the number is true in every branch and that the log and the welcome-back panel cannot be read as contradicting each other.

## Open questions

1. **The concrete anchor mechanism for the log's number (Kai, confirm in the proof).** See Technical notes: shape (a) keeps the loaded pre-reset record and reproduces the panel's anchor exactly; shape (b) anchors on the last recorded completion day from `completedQuests`. Recommendation: shape (a), because Scenario 2 (non-contradiction) is the story's core assertion and shape (a) makes it provable on every input rather than on the cases where the two anchors coincide. Not a CEO question; a dev design decision recorded in the proof.
2. **Singular day wording at 1 (Riven/Palette).** Recommendation: keep the existing `(streak === 1 ? ' day' : ' days')` behavior unchanged. Not in scope to change.
3. **Whether the Story 042 panel's own number is ever printed (Kai/Vigil).** The panel prints a sentence, not a number, so "agreement" is between a number and a status. Recommendation: Scenario 2 checks status-to-number consistency (survived implies `>= 1` and equal to the run length; broken implies `0`), not equality of two printed figures. If the CEO prefers the panel to also print the run length, that is a new copy decision and a separate story.
4. **Session 23 duplicate-helper hazard (parent/devs).** Recommend naming one helper and one owner in the Wave 3 brief before either dev starts, per the session plan's process requirement.
5. **Escalation, if a persisted field turns out to be the only correct fix.** Per requirement 5 and Scenario 19: escalate as a Story 039 amendment plus CEO sign-off, do not implement. This is the only path in this story that needs CEO input, and only if the devs reach it.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 1 and the shipped code it names; nothing beyond that was invented.
