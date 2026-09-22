# Story 042: Cinder Welcome-Back Summary, Honest Streak Line and One-Time-Per-Gap Guard (Session 23, P1)

**Status:** Ready for development (Session 23, second half, 2026-09-22). Corrects two disclosed limitations of Story 040 (shipped v0.20.0) without amending the Story 039 decision record.
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (retention: the welcome-back summary currently misleads a returning player on their first return, and it reappears on a same-day reload).
**Assigned to:** **Kai** - pure-read gate and proof: the correct streak source, the gap-guard derivation, the reset hazard proven directly against the shipped code, and the no-write proof. **Riven** - the view and messaging: the streak line's user-facing wording and the guard's user-facing behavior (no second panel, no nag). **Both devs work in separate git worktrees** (Session 23 process requirement, third session running; see the requirements handoff). Scout owns the test plan and the real-browser checks. Palette checks the panel for brand and mobile consistency. Vigil checks copy and truthfulness.
**Tracked by:** Session 23 plan Priority 1. Corrects `docs/stories/040-cinder-welcome-back-summary.md` (both limitations were disclosed at the time and left live). Constrained by `docs/stories/039-cinder-away-time-decision-record.md`. Grounded in Story 025 (daily quest), Story 033 (daily-return preview), Story 035 (quest log + streak), Story 037 (app-icon badge), and the v0.13.1 `data-action` delegation pattern.

## Summary

Story 040 shipped the welcome-back return summary in v0.20.0. It works, and it shipped with two limitations that were written down at the time and are still live in `src/cinder.html`. Both of them hit a returning player on their **first** return, which is exactly the player the retention work exists to recover.

1. **The streak line normally reads "broken" on a real return.** `computeAwayWindow()` reads the streak status from `computeQuestStreak(rawDayState)` (`src/cinder.html:416`, helper at `:382`). On a genuine multi-day return the stored day record is **stale**, so `checkDailyReset()` (`src/cinder.html:632`) rebuilds the record wholesale, with `completedQuests: []`. The streak anchor is therefore yesterday with no recorded completion, the helper returns 0, and the summary tells a player whose recorded run is fully intact that their streak is broken. The history that proves the run is intact sits in `completedQuests`, and `computeAwayWindow` already reads it for `questsMissed` and for the last play day - it just never consults it for the streak.
2. **A same-day page reload re-shows the summary.** The one-time guard is `returnShown`, an in-memory flag for the life of the page (`src/cinder.html:592`, read and set in `init()` at `:1292-1299`). Reload the page on a gap day and Cinder says welcome back a second time, and again on every reload for the rest of that day.

This story fixes the two things the summary **reports** and **re-shows**. It changes no mechanic:

- The streak line is reported from the **last recorded completion run**. A player whose run is intact is told it survived. A player whose run was genuinely ended by the gap is told it is broken. Both branches are explicit.
- The summary is shown **once per gap window**. No repeat on a same-day reload, and no repeat on any later visit within the same gap. The guard is derived from state that already exists on the page: the summary's load-time flag plus the loaded record.

Nothing else changes. The day record shape is unchanged, `checkDailyReset()` is not touched, no streak history is banked or preserved as a mechanic, no new history field is added, and no persisted field of any kind is introduced. The away-window gate semantics from Story 040 stay exactly as they are: a same-day return and a next-day return both stay quiet, and only a fully missed UTC day fires the summary.

## Business value

- Closes the two first-return defects in the retention surface shipped as v0.20.0. The player the loop is designed to recover is currently told something untrue about their streak, and is then nagged by the same panel every time the tab reloads.
- Zero new product surface. This is presentation and re-show behavior on an existing view. No new row, no new panel, no new economy, no new save field, no balance change.
- Keeps the byte-safety discipline intact: the fix is provable to read only and to write nothing, and the deploy mirror stays byte-identical after the merge.
- Truthfulness is a company rule, not a polish item. Telling an intact player their streak is broken is an accuracy defect, and fixing it removes a compliance risk that the current build carries.

## User Story

As a Cinder player returning after one or more missed days,
I want the welcome-back summary to tell me the truth about my streak, and to say it once,
So that I trust what the game tells me about my own progress and I am not nagged by the same panel every time I reload.

## Requirements

### 1. Streak line reports the last recorded completion run

- The streak status must be derived from the **last recorded completion run** in the loaded day record's `completedQuests` history: the trailing run of consecutive day indexes ending at the last recorded play day, where the last recorded play day is the maximum valid candidate drawn from `dayState.dayIndex` and the history entries (the same candidates `computeAwayWindow` already uses for the away window).
- **Intact run -> "Your streak survived."** A recorded run that reaches the last recorded play day is intact, including when the run is a single recorded day.
- **Ended run -> "Your streak is broken."** The run is broken only when it genuinely does not reach the last recorded play day: the player actually missed a day **between** recorded completions (a hole in the run before the last play day), or the history records no completion at all.
- The status is **never** taken from a post-reset record for the purpose of this line. The wholesale rebuild in `checkDailyReset()` is exactly what makes the current line wrong, and the summary must not depend on a value the rebuild produces.
- The helper may reuse the **shape** of the existing trailing-run scan in `computeQuestStreak()` (`src/cinder.html:382-410`), anchored on the last recorded play day instead of on "today or yesterday". It must not use that function's outcome as the answer, and it must not modify that function.

### 2. One-time per gap, no repeat reload

- The summary renders at most **once per gap window**, and a gap window is a contiguous run of UTC days on which the player did not play (the span from the last recorded play day to today).
- **No repeat on a same-day reload.** After the summary has been shown and dismissed (Back to Town, or into today's quest), a page reload on the same UTC day must not show it again.
- **No repeat on any later visit within the same gap window.** If the player returns, dismisses the summary, and visits the game again later in the same gap (for example the next day, still inside the window, without recording a completion), the summary must not reappear.
- The guard must be **derived from existing state only**: the summary's in-memory load flag (`returnShown`, `src/cinder.html:592`) combined with the loaded day record. No persisted flag, no gap stamp, no version marker.
- "Derived from existing state" is satisfied in the shipped state by the existing persistence of the day record: `checkDailyReset()` writes a fresh record on the first load of each stale day, so a second load on that same UTC day finds the record already stamped with today and is not a real return. The dev must **verify that derivation in the proof and in a real browser**, and must not assume it (see requirement 6 and Technical notes).
- A **new** gap (a new block of fully missed days) is a genuinely new absence and may show the summary again, once, exactly as Story 040 specified.

### 3. No new persisted field, no writes from the summary path

- **No new field** on the character save or on the day record. Not `seenReturnSummary`, not `welcomeBackShown`, not `lastGapStamp`, not a version marker, nothing.
- **Never write to `flambeee-cinder-save` or `flambeee-cinder-day` from the summary path.** No `saveCharacter()`, no `saveDayState()`, no direct `localStorage.setItem`.
- The **stored day record shape is unchanged.** `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }` stays exactly as it is today; no field is added, renamed, or removed.
- **Do not change `checkDailyReset()`.** Its behavior and its writes are untouched by this story. No banked streak, no preserved history, no history field as a mechanic.
- `ensureQuestState()` (`src/cinder.html:249`) keeps its existing backfill behavior and its existing writes. It runs on the load path before the summary is computed; that is pre-existing behavior and this story adds nothing to it.
- Existing saves load clean with no field loss. A legacy save (written before this story) loads and plays with level, gold, XP, bank, and wins unchanged; a newer save read by an older build is unaffected.

### 4. Away-window gate semantics from Story 040 stay intact

- Same-day return (**gapDays 0**): no summary. Next-day return (**gapDays 1**, nothing fully missed): no summary. The Story 033 come-back-tomorrow preview keeps working exactly as it does today.
- Only a gap of **at least one fully missed day** (`daysAway >= 1`) fires the summary, with the same `daysAway`, `questsMissed`, and today's-quest pointer content as Story 040.
- This story changes what the summary reports and when it re-shows. It does not change when the summary is eligible to appear at all.

### 5. No economy, no UI surface, no notifications

- No change to gold, XP, level, bank, wins, quest progress, rewards, fight counts, quest rotation, or monster pools. The summary pays nothing and grants nothing, and the streak line pays nothing.
- No new town-hub row, no banner, no notification dot, no push, no service worker message, no permission prompt, no install prompt or nag. The only surface remains the welcome-back panel inside Cinder, reached by input row 1 or 2.
- No new colors, fonts, images, or brand elements. The panel keeps the existing boxed-menu styling described in the visual section.

### 6. Mobile-safe, boxed-menu pattern, no inline onclick

- The summary remains a `boxed-menu` block consistent with the other Cinder views, and the guard changes nothing about its rendering.
- All interactive controls keep the v0.13.1 `data-action` event delegation pattern (`src/cinder.html:1326-1331`). No inline `onclick`, ever (issue #46).
- No horizontal overflow at 375x667, and both rows stay reachable and tappable.

### 7. Copy: plain punctuation, no em dashes, no heavy emoji

- Only the streak line's wording is in scope for change (requirement 1). Every new or changed user-visible string uses plain punctuation, no em dashes, and no heavy emoji, in Cinder's dry voice, matching the existing helper wording at `src/cinder.html:441` and `:445`.
- The rest of the panel's copy (days away, quests missed, today's-quest pointer) is unchanged.

### 8. Graceful degradation

- Corrupt or missing history (`completedQuests` not an array, entries with non-numeric `dayIndex`), a non-object day record, private mode, and unavailable storage must all degrade to either a correct summary from whatever valid state exists or no summary at all. Missing data is never a crash and never a blocking error.
- A failed guard computation must never leave the player stuck without the hub: the fallback is the normal town render.

### 9. Escalation rule (binding)

- **If the only correct fix requires a persisted field, that is a Story 039 decision-record amendment plus CEO sign-off, not an implementation.** Escalate to the CEO and stop. Do not add the field, do not write it "temporarily", and do not ship a partial version of it.
- Likewise, if the only correct streak line requires changing the stored day history or `checkDailyReset()`, that is a separate decision record, not this story.

## Out of scope

- Any change to `checkDailyReset()` - its logic, its writes, or the shape of the record it builds.
- Any banked, preserved, or restored streak as a mechanic. This story changes what the summary **reports**, never what the game **keeps**.
- Any new history field, any extension of `completedQuests`, and any change to the stored day record shape.
- Any new persisted field of any kind, including a `seen` flag, a gap stamp, or a version marker.
- Any offline resource accrual (gold, XP, quests, boss fights). Decided against in Story 039; reversal requires CEO sign-off.
- Any balance, reward, rotation, payout, monster-pool, or level-curve change.
- Any notification, push, email, permission prompt, or install nag.
- Any new town-hub row, banner, tooltip, or notification dot.
- Any change to the Story 033 come-back-tomorrow preview, the Story 035 quest log or streak display, or the Story 037 app-icon badge, beyond not regressing them.

## Acceptance Criteria (BDD)

### Scenario 1: Streak line reads "survived" when the recorded run is intact (P1, Kai + Riven)
- **Given** a player who returns after a gap of at least one fully missed day
- **And** the day record loaded at startup carries a recorded run that reaches the last recorded play day (for example `completedQuests` entries for day indexes T-4, T-3, T-2 and `dayIndex: T-2`, where T is today)
- **When** the welcome-back summary renders
- **Then** the streak line reads "Your streak survived.", and no part of the render path reports the run as broken

### Scenario 2: Streak line reads "broken" when the gap ended the run (P1, Kai + Riven)
- **Given** a player who returns after a gap of at least one fully missed day
- **And** the recorded run genuinely does not reach the last recorded play day (for example `completedQuests` entries for day indexes T-6 and T-5 and `dayIndex: T-2`, so T-4 is missing between recorded completions)
- **When** the welcome-back summary renders
- **Then** the streak line reads "Your streak is broken."

### Scenario 3: A single recorded day counts as an intact run (P1, Kai + Scout)
- **Given** a player whose history holds exactly one recorded completion, on the last recorded play day (`completedQuests: [{ dayIndex: T-3, ... }]`, `dayIndex: T-3`)
- **When** the summary renders for the gap from T-3 to T
- **Then** the streak line reads "Your streak survived.", because that recorded run reaches the last recorded play day

### Scenario 4: Streak source is the recorded history, never a post-reset record (P1, Kai, proof)
- **Given** a stale stored day record (its `dayIndex` is not today) that carries recorded completions
- **When** the summary is computed on the load path before `checkDailyReset()` replaces the record, and again from the rebuilt record
- **Then** the reported streak status comes from the loaded record's history and is unchanged by the rebuild, and the rebuilt record's empty `completedQuests` plays no part in the answer

### Scenario 5: No repeat on a same-day reload (P1, Riven + Scout)
- **Given** the summary has been shown for a gap and the player has returned to town
- **When** the player reloads the page on the same UTC day
- **Then** the summary does not render again, the town hub renders, and nothing about quest progress, streak, or save state changed as a result of the reload

### Scenario 6: No repeat on a later visit within the same gap window (P1, Riven + Scout)
- **Given** the summary has been shown for a gap window and dismissed, and the player recorded no completion that day
- **When** the player opens the game again inside the same gap window (a later UTC day before any new completion is recorded)
- **Then** the summary does not render again, and the player goes straight to the town hub

### Scenario 7: A genuinely new gap still shows the summary once (P1, Riven + Scout)
- **Given** the player played on day T and returns on day T+1 (next-day return, no summary, Story 033 flow intact)
- **When** the player then returns again on day T+4 with days T+2 and T+3 fully missed
- **Then** the summary renders exactly once for the new gap, with the correct days-away, quests-missed, streak line, and today's-quest pointer

### Scenario 8: The summary path writes nothing and adds no field (P1, Kai, proof)
- **Given** any state that produces a summary
- **When** the summary is computed and rendered, and when the guard decides to suppress it
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical before and after, a static scan of the summary path finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, or state-mutating `character.` / `dayState.` writes, and no field name matching a seen flag, gap stamp, or version marker appears anywhere in the diff

### Scenario 9: The day record shape is unchanged (P1, Kai + Scout)
- **Given** a save written by v0.20.0 and a save written by the build with this story applied
- **When** each is loaded and played, and the raw JSON is compared
- **Then** the stored day record has exactly the same field set as before (`dayIndex`, `fightsUsed`, `innHealsUsed`, `quest`, `completedQuests`), with no added, removed, or renamed field

### Scenario 10: `checkDailyReset()` is not changed (P1, Kai, proof)
- **Given** the diff for this story in `src/cinder.html`
- **When** the code is inspected
- **Then** `checkDailyReset()` (`src/cinder.html:632`) is textually unchanged from v0.20.0, and the story adds no history field, no reset-time streak carry, and no change to the record it builds

### Scenario 11: Same-day and next-day returns stay quiet (P1, Kai + Scout, regression)
- **Given** a player who played earlier today, or whose last recorded play day is yesterday with nothing fully missed
- **When** the player opens or reloads Cinder
- **Then** no welcome-back summary renders in any of those cases, and the hub renders exactly as the pre-story build renders it

### Scenario 12: Story 033 come-back-tomorrow preview not regressed (P1, Scout, regression)
- **Given** a player who completes and collects today's quest
- **When** the quest view renders
- **Then** the "Tomorrow: ..." preview and its "Come back after midnight to start it." line render exactly as before, and no summary or guard state interferes with that view

### Scenario 13: Story 035 quest log and streak not regressed (P1, Scout, regression)
- **Given** a player with history, opening the Quest Log (hub row 9)
- **When** the log renders
- **Then** the Current streak line and the recent-quests list render from `computeQuestStreak(dayState)` and `dayState.completedQuests` exactly as before, and `computeQuestStreak()` itself is byte-identical to v0.20.0

### Scenario 14: Story 037 app-icon badge not regressed (P1, Scout, regression)
- **Given** an installed player with the quest pending, and again after completing and collecting it
- **When** the game loads, plays, and the quest completes
- **Then** the badge path behaves exactly as before (1 while pending, cleared on completed and rewarded), and the summary path neither calls the badge helper differently nor leaves the badge stale

### Scenario 15: Legacy and corrupt day records still load clean (P1, Kai + Scout, regression)
- **Given** a legacy day record with no `quest` and no `completedQuests`, and separately a corrupt record (`completedQuests` a string, an entry with a non-numeric `dayIndex`, `dayIndex` not a number, `dayState` null)
- **When** the game loads
- **Then** it loads without error, the summary either renders a correct summary from the valid parts or does not render, no exception is raised, and no corrupt field is rewritten beyond the existing `ensureQuestState()` backfill

### Scenario 16: The guard's state is existing state only (P1, Kai, proof)
- **Given** the full render path for a gap day
- **When** the loaded day record and the live page state are compared before and after the guard decides
- **Then** the guard's decision is derivable from `awayWindow` (the load-time window value), `returnShown` (the load-time flag), and the loaded record alone, and the decision is identical on a repeat read of the same state

### Scenario 17: Private mode and unavailable storage (P1, Kai)
- **Given** the browser is in private mode or storage is unavailable, so the existing localStorage helpers are throwing and swallowing
- **When** the game loads on a gap day and the player plays
- **Then** the game runs from in-memory state, the summary and the guard behave the same as with storage, and nothing throws

### Scenario 18: No notifications, no push, no permission prompt, no install nag (P1, Vigil + Scout)
- **Given** this story's code
- **When** it is scanned and exercised in a browser
- **Then** it contains no `Notification` permission request, no `pushManager`, no subscription code, and no permission prompt or install prompt appears at any point in load, summary, guard, or play

### Scenario 19: Mobile-safe, both rows tappable, no inline onclick (P1, Riven + Scout)
- **Given** the summary rendered at 375x667 and on desktop
- **When** the player taps Back to Town and, separately, the row into today's quest
- **Then** both taps are handled by the delegated `data-action` listener, the hub and the quest view render, there is no horizontal overflow, and no inline `onclick` appears anywhere in the markup

### Scenario 20: Escalation, not implementation, if a persisted field is needed (P1, Vigil + Kai)
- **Given** the whole story's code and diff
- **When** it is reviewed
- **Then** it proves the fix was achieved with existing state only, and if any part of the design had required a persisted field the team escalated it as a Story 039 amendment instead of implementing it, with no persisted field shipped

### Scenario 21: Tone and no-AI-tells (P2, Vigil)
- **Given** any new or changed user-visible copy introduced by this story
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and matches the plain-punctuation, dry-humor Cinder voice

## Technical notes (Quinn)

Verified against the shipped `src/cinder.html` at v0.20.0 (1394 lines, sha256 `dde7125b99bb2ac32660d453ed714933e1ab988f639b516b1a16110125763482`), repo `main` at `06bcd61`.

- **Single game file:** `src/cinder.html` is the source of truth. The deploy mirror is a **separate file outside the repo** at the ABSOLUTE path `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. It must end the session byte-identical to `src/cinder.html` (`cmp` exit 0). Both read sha256 `dde7125b99bb2ac32660d453ed714933e1ab988f639b516b1a16110125763482` at the start of this session, and `cmp` exits 0.
- **The defect, precisely.** On a genuine multi-day return the stored day record is stale. `init()` (`src/cinder.html:1285-1294`) loads it, captures it as `rawDayState`, and computes `awayWindow` from it; `checkDailyReset()` (`:632-640`) then sees `dayState.dayIndex !== today` and reassigns `dayState` to a brand-new object with `completedQuests: []`, and calls `saveDayState()`. `computeAwayWindow()` reads the streak at `:416` as `computeQuestStreak(rawDayState) > 0`. `computeQuestStreak()` (`:382-410`) anchors on today when today is complete and on **yesterday** otherwise (`cursor = live ? todayIdx : todayIdx - 1`), and walks back only while `done[cursor]` is true. A stale record never has `quest.completed` true for the new day, so the anchor is `todayIdx - 1`; on a gap of two or more missed days that day carries no recorded completion, so the loop exits immediately and the answer is 0. Result: "Your streak is broken." for a player whose recorded history is a continuous run ending at the last play day.
- **The fix shape (Kai owns the final form).** Derive the status from the **last recorded completion run** in `rawDayState.completedQuests`: build the set of recorded day indexes, take `lastPlayIdx` exactly as `computeAwayWindow()` already does (max of the valid `rawDayState.dayIndex` and the valid history entries), walk back from `lastPlayIdx` while each successive index is present, and report survived when the run length is at least 1. Reuse the **shape** of the trailing-run scan in `computeQuestStreak()`; do not call it for the answer, do not modify it, and do not touch `checkDailyReset()`. Keep the helper pure and extractable, matching the Story 033/035/037/040 proof pattern.
- **Where the current streak line is produced:** `computeAwayWindow()` sets `out.streakSurvived` at `src/cinder.html:416`. The copy helper `awayStreakSentence(streakSurvived)` is at `:441`, returning "Your streak survived." or "Your streak is broken.". `renderWelcomeBack()` (`:493-514`) emits the line. `awayWindow` is computed once at load (`:1292`) and is never recomputed.
- **The one-time guard, precisely.** `returnShown` is declared at `src/cinder.html:592` (`let returnShown = false;`), read at `:1298` (`awayWindow.shouldShow && !returnShown`), and set at `:1299` only by a `return` into the summary. Because the flag's lifetime is the page, a reload rebuilds it as `false`.
- **The derivation available for the gap guard (Kai must verify, not assume).** `checkDailyReset()` writes the fresh record on the first load of a stale day. So on a same-day reload inside a gap window, the stored record already carries `dayIndex === today`; `computeAwayWindow()`'s own candidates then make `lastPlayIdx === today`, so `gapDays === 0`, `daysAway === 0`, and `shouldShow` is false with no additional guard at all. The second load therefore falls through to the normal town render. The dev must **prove this directly** (Scenario 5 and Scenario 16) and confirm it in a real browser, because it rests on the pre-existing `saveDayState()` call inside `checkDailyReset()` (`:634`) rather than on a new mechanism. If the proof shows a same-day reload still re-shows the summary, the escalation rule in requirement 9 applies before any new mechanism is considered.
- **Scope guard for Kai:** do not change `checkDailyReset()`, do not bank or preserve streak history, do not add history fields, and do not add any persisted value. Scenarios 8, 9, and 10 are the tripwires.
- **Existing state to read (do not change):** `getDayIndex()` at `:625` (`Math.floor(Date.now() / 86400000)`); `loadDayState()` / `saveDayState()` at `:608` / `:616` as the only `flambeee-cinder-day` accessors; `dayState.completedQuests` entries each carrying a numeric `dayIndex` plus `label` / `objective` (`completeQuest()`, `:317-321`); `ensureQuestState()` at `:249`; `getQuestState()` at `:259`; `getActiveQuest()` at `:240` / `determineQuestForDay()` at `:234` for the today's-quest pointer; `computeQuestStreak()` at `:382` as the Story 035 streak for the Quest Log (unchanged by this story); `syncAppBadge()` at `:280`; `handleWelcomeBackInput()` at `:1247` (row 1 -> town, row 2 -> quest); `case 'welcomeback'` in the input switch at `:1133`; the delegated click listener at `:1326-1331`.
- **What "no writes" means here.** The load path legitimately runs `checkDailyReset()` (which may call `saveDayState()` for the new day) and `ensureQuestState()` (which may call `saveDayState()` when a legacy record lacks `quest` or `completedQuests`). Those are **pre-existing v0.20.0 behaviors** and are not part of the summary path this story owns. Scenario 8's byte-identity claim is therefore scoped to the summary and guard computation itself: with a well-formed day record already stamped for today (the same-day reload case) the load path writes nothing, and neither the summary render nor the guard decision may add any write.
- **Proof expectation (Session 14 bar):** Kai provides a node-based proof script plus a static scan (same pattern as the Story 033/035/037/040 proofs, extracting the shipped functions into a sandbox). It must assert: "survived" for an intact run ending at the last play day; "broken" for a hole in the run; "survived" for a single recorded day; identical status before and after the wholesale rebuild; no summary for gapDays 0 and 1; summary for gaps of 2+; the guard suppressed on a same-day reload and on a later visit inside the same gap; a new gap showing once; no forbidden writes; no new field name in the diff; `checkDailyReset()` textually unchanged. Expected exit code 0.
- **QA bar:** real browser at desktop and 375x667 with real taps on both rows, a seeded multi-day gap run for each streak branch, a reload run on the gap day, a second-day run inside the same gap, a control run against the pre-042 build for the regression scenarios, and raw `flambeee-cinder-save` / `flambeee-cinder-day` values captured before and after every step.
- **Worktree rule (Session 23, third session running):** Kai and Riven must each work in a **separate git worktree** (`git worktree add` under a temp dir outside the main tree). Story 042 again puts both devs on the same single file (`src/cinder.html`), which is the highest-risk story shape in the repo. The two halves here are separable: Kai owns the pure-read gate, the streak source, the guard derivation, and the proof; Riven owns the rendered line and the guard's user-facing behavior. Sessions 20 and 21 both had branch collisions from the shared working tree; Session 22 used worktrees and had none.
- **Peer review:** Kai and Riven review each other's work in the usual direction before merge.

## Visual Description (Quinn)

The panel is the existing Story 040 welcome-back view. It keeps Cinder's boxed-menu styling exactly as shipped: dark `#1a1a2e` panel, `2px solid #444` border, centered yellow `#ffcc00` `.header`, dashed `.divider`, plain body text, `.menu-row` rows with `<span class="num">` number prefixes.

```
+------------------------------------------------+
|                                                |
|            === WELCOME BACK ===                |   <- yellow .header, centered (unchanged)
|                                                |
|   You were away for 3 days.                    |   <- days away (unchanged)
|   2 quests went uncompleted while you were     |   <- quests missed (unchanged)
|   gone.                                        |
|   Your streak survived.                        |   <- CHANGED: truthful status, same style
|                                                |
|   ------------------------------------------   |   <- .divider (unchanged)
|   Today's quest: Defeat 5 monsters             |   <- today's objective (unchanged)
|                                                |
|   ------------------------------------------   |   <- .divider (unchanged)
|   1. Back to Town                              |   <- .menu-row, data-action="1" (unchanged)
|   2. Go to today's quest                       |   <- .menu-row, data-action="2" (unchanged)
|                                                |
+------------------------------------------------+
```

What changes, and what does not:

- **Changes (copy only, one line):** the streak line. It is still a single plain sentence in the same position, the same style, and the same length class. Today it says "Your streak is broken." on a real return even when the run is intact; after this story it says "Your streak survived." whenever the last recorded completion run reaches the last recorded play day, and "Your streak is broken." only when the run genuinely ended. Both strings already exist in the shipped build (`awayStreakSentence()`), so this is a correctness change to which string is chosen, not new wording.
- **Changes (behavior, nothing visible):** on a same-day reload, and on any later visit inside the same gap window, the panel does not appear at all and the player lands on the town hub. Previously the panel reappeared.
- **Unchanged:** the header, the days-away sentence, the quests-missed sentence, the divider, the today's-quest line, both menu rows, the `data-action` delegation, the colors, the fonts, the layout, the 375x667 behavior, and the absence of any new hub row, banner, dot, or nag.
- **Never shown:** the word "streak" is never printed with a number, a flame icon, or any flourish. It is one plain sentence, stated, per the Story 040 rule.

Palette checks that the panel still reads as one Cinder view at 375x667 and that the changed line does not disturb the layout, the wrapping, or the contrast of the surrounding text. Vigil checks that the line is true in both branches and that the panel promises nothing the game does not do (no restored streak, no payout).

## Open questions

1. **The exact anchor for the streak line (Kai/Riven, confirm in review).** Recommendation: the last recorded play day, the same anchor `computeAwayWindow()` already uses for `daysAway` and `questsMissed` (max of the valid `rawDayState.dayIndex` and the valid history day indexes). This keeps every number and the streak line describing the same window. If Riven judges that the line reads oddly when the anchor day is today's stale record rather than a completion, the fallback is the last **recorded completion** day; the two differ only when `rawDayState.dayIndex` is newer than the newest history entry, which the proof should cover either way.
2. **One-day run wording (Riven/Palette).** Recommendation: "Your streak survived." for a single recorded day, as it stands today and per Scenario 3. If Riven prefers a gentler variant for a one-day streak, it must stay a single plain sentence with no em dash and no emoji, and the same truth conditions.
3. **Second affordance (Riven/Palette).** The panel currently offers Back to Town and Go to today's quest. Recommendation: keep both, unchanged; neither is in scope for this story. Flagging it only so the story is not read as authorizing a panel redesign.
4. **Guard derivation confirmation (Kai + Scout, mandatory, not blocking).** The same-day reload behavior rests on the existing `saveDayState()` call inside `checkDailyReset()`. Confirm it directly in the proof and in a real browser before treating Scenario 5 as satisfied. If it does not hold, **escalate per requirement 9** rather than adding a mechanism.
5. **Session 22 operational risk (parent, not a dev question).** Session 22 lost Kai and Scout to provider errors **after** their artifacts were correct. Devs should follow the Wave 3 brief, poll their own output files, and write their results to disk as they go rather than holding them to the end of the run.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 1 and the two Story 040 limitations it names; nothing beyond those was invented.
