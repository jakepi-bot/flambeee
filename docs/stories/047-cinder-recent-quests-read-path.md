# Story 047: Cinder Quest Log, the Recent-Quests List and the Day-Record Read Path (Session 25, P1)

**Status:** Ready for development (Session 25, 2026-09-27). Corrective or verification-shaped. **A return of "no code defect found; proof recorded and public claim narrowed" is a valid and expected PASS.** Does not amend the Story 039 decision record.
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (truthfulness and trust: sessions 23 and 24 each shipped a correction for the same class of bug on this screen, the streak number source. The related surface not yet audited is the list the screen also renders and the day-record read path that feeds it).
**Assigned to:** **Kai** - the read-path proof: the first-run path, the stale-by-1-day case, the stale-by-3/6/30-day cases, the same-day reload, the reset hazard proven directly against the shipped code, and the no-write / no-new-field proof. If a defect is found, Kai owns the pure-read helper. **Riven** - the quest-log view and the recent-quests list rendering, the call site, and any copy correction the proof requires. **Both devs work in separate git worktrees** (see the collision guard in requirement 8). **Scout** owns the test plan, the real-browser checks, and the out-of-scope-reference and forbidden-fallback scan on the **merged** candidate. **Palette** checks the list for brand and mobile consistency. **Vigil** checks that any narrowed public claim matches the proof and that nothing is asserted without evidence.
**Tracked by:** Session 25 plan Priority 1. Grounded in Story 035 (the quest log, `renderQuestLog()`, the recent-quests list and `computeQuestStreak()`), Story 040 (the welcome-back window and its `lastPlayIdx` anchor), Story 042 (the honest streak line), Story 044 (the honest quest-log streak source, `computeQuestLogStreak()`, and its `questLogAnchor`), Story 045 (the verification-shaped proof pattern and the corrected-claim pattern), Story 033 (the come-back-tomorrow preview), and Story 037 (the app-icon badge). Constrained by `docs/stories/039-cinder-away-time-decision-record.md`.

## Summary

Story 044 fixed the quest log's **streak number** to read the player's recorded history through the pre-reset record (`rawDayState`, held as `questLogAnchor` at `src/cinder.html:1386`). Its scope note left the **recent-quests list itself** explicitly untouched, and no story has verified the list renders the recorded history rather than the record rebuilt by `checkDailyReset()`.

The list and the streak number read the same underlying object today, but they are two separate expressions over it:

- the streak number is `computeQuestLogStreak(dayState, questLogAnchor)` (`src/cinder.html:629`), which reads the **pre-reset anchor**;
- the list is `dayState.completedQuests.slice(-5).reverse()` (`src/cinder.html:627-637`), which reads the **post-reset `dayState`**.

On the load of a gap day, `checkDailyReset()` (`src/cinder.html:727`) has already rebuilt `dayState` wholesale with `completedQuests: []`. If the streak helper and the list do not agree on which record they describe, the same screen can print a nonzero streak beside an empty list. That is the same class of read-path contradiction Story 044 fixed for the number, and it is now a **standing property** of this file (Sessions 23 and 24 both needed a parent-side reconcile of two dev halves on one line of `src/cinder.html`).

This story does two things:

1. **Prove the read path.** Establish, with recorded commands and exit codes, what the recent-quests list and the streak number actually render in five states: first run (no record), a record stale by exactly 1 day, a record stale by 3, 6 and 30 days, and a same-day reload.
2. **Fix it, or narrow the claim.** If a state is found where the list and the number describe different records, fix it with the same minimal pattern Story 044 used. If no defect is found, record the proof and narrow any public claim that overstates what the screen does.

**Explicit, and important: if the proof shows the read path is correct in every reachable state, the correct outcome is "no code defect found, proof recorded and public claim narrowed". That is a PASS. No code change is mandatory.** Shipping a code change the proof does not require violates the story, not satisfies it.

## Business value

- The quest log is the screen a returning player opens to check whether their history survived. A nonzero streak printed beside an empty list is the same trust failure Story 044 removed for the number, on the same screen, in the same file.
- The last two sessions each shipped a correction for the same read-path confusion. Auditing the adjacent surface while the reasoning is fresh costs one session and closes the class instead of waiting for the third instance.
- The proof makes the read path auditable: five states, recorded commands, recorded exit codes. Anyone can re-run them.
- It is nearly free when correct: no new product surface, and the likely outcome is a recorded proof rather than any code change.
- Keeps the byte-safety discipline intact: read-only is provable, and the deploy mirror stays byte-identical after the merge.

## User Story

As a Cinder player returning after one or more missed days,
I want the Quest Log's recent-quests list to show the quests I actually recorded, in agreement with the streak number above it,
So that the game never shows me an empty history beside a live streak, and I can trust the whole log, not just the number.

## Requirements

### 1. The recent-quests list is proven for the five named states

- The proof must cover, at minimum:
  - **First run, no record.** No stored day record at all, or a record with no `completedQuests`.
  - **A record stale by exactly 1 day.** Stored `dayIndex` is `T - 1`, carrying recorded completions.
  - **A record stale by 3 days.** Stored `dayIndex` is `T - 3` or earlier, carrying recorded completions.
  - **A record stale by 6 days.** Same shape, `T - 6`.
  - **A record stale by 30 days.** Same shape, `T - 30`.
  - **A same-day reload.** A record already stamped today, loaded, then reloaded on the same UTC day.
- Each state is recorded with the exact **command**, the **exit code**, and **auditable output** (the rendered list and the rendered streak number, or the assertions the harness prints). A screenshot alone is not auditable output.
- The proof must **not** be constructed to force a particular outcome. Its job is to report what the shipped build does.

### 2. The list and the streak number describe the same record

- On every state the proof covers, the recent-quests list and the Current streak line must be **consistent with each other**: a nonzero streak implies a non-empty list drawn from the same recorded run, and an empty list implies a streak of 0 (or the documented first-run empty state).
- Where the two surfaces read different records and that produces a visible contradiction (a nonzero streak beside an empty list, or a list that disagrees with the number), that is a **defect** and requirement 4's fix applies.
- Where the two surfaces are consistent in every reachable state, that is the **expected PASS outcome** and requirement 3 applies.

### 3. "No code defect found" is a valid and expected PASS

- This story **does not require a code change**. If the proof shows the read path is correct in all five states, the story passes on the recorded proof plus any narrowed public claim.
- In that outcome, identify any published or committed artifact that claims more about this screen than the proof supports - at minimum the **v0.22.0 release notes**, the `docs/roadmap.md` v0.22.0 entry, and the website What's New block on `/home/jake/.openclaw/workspace/share/Flambeee/index.html` if it repeats a claim about the list - and either cite the proof or narrow the claim to what the proof shows. Follow the Story 045 corrected-claim pattern exactly.
- **Do not weaken a claim the proof supports.** If the proof shows the list is correct, the claim stands, with the proof cited.

### 4. If a defect is found, the fix is minimal and read-only

- Any fix uses the **same minimal pattern as Story 044**: a **pure-read helper** with no writes, no global mutation, and no new field, following the shape of `computeQuestLogStreak()` (`src/cinder.html:432-469`). The helper is called from `renderQuestLog()` with the pre-reset anchor already held in `questLogAnchor`, or with whatever read-only mechanism Kai states in the proof.
- **No new persisted field** on the character save or on the day record. Not a cache, not a version marker, not a history extension, nothing.
- **No write on the read path.** Opening row 9 and rendering the log must leave `flambeee-cinder-save` and `flambeee-cinder-day` byte-identical.
- **`checkDailyReset()` and `computeQuestStreak()` stay byte-identical** to the v0.22.0 shipped text. Neither function is modified by this story.
- **The stored day record shape is unchanged:** `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }`, no field added, renamed, or removed.
- Escalation rule (binding): **if the only correct fix requires a persisted field, that is a Story 039 decision-record amendment plus CEO sign-off. Escalate; do not implement it.** Do not add the field "temporarily", and do not ship a partial version of it.

### 5. The list keeps its existing rendering contract

- The list keeps rendering the last entries **most recent first**, capped at 5, with their relative day labels (`today` / `yesterday` / `N days ago`) from `dayLabelForIndex()` (`src/cinder.html:613`).
- The empty-state line ("No quests recorded yet. Finish today's quest to start your log.") is unchanged.
- Whatever this story does to the read path, the same history must produce the same list before and after, on every state the proof covers.

### 6. Away-window gate semantics and the Story 042/044 surfaces stay intact

- The welcome-back panel keeps rendering exactly as Story 042/044 shipped it, including its streak sentence and its anchor.
- `computeQuestLogStreak()` keeps its current return values on every input it handled before this story; if a defect fix changes its call site, the helper's own behavior for the same inputs is unchanged, or the change is stated and proven in the proof.
- Same-day and next-day returns stay quiet, and the Story 033 come-back-tomorrow preview and the Story 037 app-icon badge are not regressed.

### 7. No economy, no UI surface, no notifications

- No change to gold, XP, level, bank, wins, quest progress, rewards, fight counts, quest rotation, or monster pools. The log pays nothing and grants nothing.
- No new town-hub row, no banner, no notification dot, no push, no service worker message, no permission prompt, no install prompt or nag. Row 9 stays the only entry point and the panel keeps its existing `boxed-menu` styling.
- No new colors, fonts, images, or brand elements. No leaderboard, no guess-count stats, no multiplayer, no community-submitted game, no new game, no economy or balance change.
- No website redesign. The site is current and on-brand.

### 8. Collision guard: one owner per helper and per call-site line, separate worktrees

- Story 047 touches **one file** (`src/cinder.html`) from two directions, which is the highest-risk story shape in this repo (Sessions 23 and 24 both needed a parent-side reconcile).
- **Kai and Riven each work in a separate git worktree** (`git worktree add` under a temp dir outside the main tree).
- **One owner per helper and per call-site line, agreed before dev starts.** Kai owns `computeQuestLogStreak()` and the proof helper; Riven owns the `renderQuestLog()` list expression and the rendered line. Name the exact line range each owns in the Wave 3 brief before either dev starts.
- **Watch the duplicate-solution hazard:** agree on one helper name and one owner before either dev starts, or the parent's reconciliation step becomes explicit before merge.
- Each dev states the exact line range it owns in its **PR body**(requirement in Story 048).

### 9. Mobile-safe, boxed-menu pattern, no inline onclick

- The quest log remains a `boxed-menu` block consistent with the other Cinder views.
- All interactive controls keep the v0.13.1 `data-action` event delegation pattern (`src/cinder.html:1326-1331`). No inline `onclick`, ever (issue #46).
- No horizontal overflow at 375x667, and Back to Town stays reachable and tappable.

### 10. Copy: plain punctuation, no em dashes, no heavy emoji

- Any new or changed user-visible string uses plain punctuation, no em dashes, and no heavy emoji, in Cinder's dry voice.
- Any narrowed public claim uses the same discipline, and names the state it covers without hedging where the behaviour is deterministic.

### 11. Graceful degradation

- Corrupt or missing history (`completedQuests` not an array, entries with a non-numeric or non-finite `dayIndex`), a non-object day record, private mode, and unavailable storage must all degrade to a correct render from whatever valid state exists, or to the empty-state line, and never to an exception or a blocking error.
- Legacy day records (no `completedQuests`), partial records, and `null` must load the log cleanly, exactly as they do today.
- A failed render must never leave the player stuck without the hub: the fallback is the normal town render.

## Out of scope

- Any change to the **recent-quests list's rendering contract** (order, cap of 5, labels, empty-state line). This story may change **which record** the list reads if a defect is proven; it does not change what the list looks like for the same history.
- Any change to `checkDailyReset()` - its logic, its writes, or the shape of the record it builds.
- Any change to `computeQuestStreak()` or its return value.
- Any change to the Story 042/044 welcome-back panel, its wording, or its anchor.
- Any banked, preserved, or restored streak as a mechanic. This story changes what the log **reports**, never what the game **keeps**.
- Any new history field, any extension of `completedQuests`, any change to the stored day record shape, and any new persisted field of any kind.
- Any offline resource accrual (gold, XP, quests, boss fights). Decided against in Story 039; reversal requires CEO sign-off.
- Any Cinder offline accrual, boss-day balance, cross-day streak mechanic, or multi-day welcome-back suppression. All four remain blocked on the Story 039 amendment plus CEO sign-off and stay deferred.
- Any balance, reward, rotation, payout, monster-pool, or level-curve change.
- Any notification, push, email, permission prompt, or install nag.
- Any new town-hub row, banner, tooltip, or notification dot.
- Any new game, new feature category, leaderboards, guess-count stats, multiplayer, or community-submitted games.
- Any website redesign, layout change, or new What's New feature beyond narrowing a claim the proof does not support.
- Any change to `scripts/verify-website-currency.sh`. Story 049 owns the checker runs.
- Any cron configuration, and any file under `jobs/`, `jobs-refactor-team/`, or `jakebot/`.

## Acceptance Criteria (BDD)

### Scenario 1: First run, no record (P1, Kai + Riven)
- **Given** a player with no stored day record at all (first-ever load), or a record with no `completedQuests`
- **When** the player opens the Quest Log (hub row 9)
- **Then** the recent-quests list renders the existing empty-state line, the Current streak line reads 0, and the two are consistent with each other, with nothing thrown

### Scenario 2: A record stale by exactly 1 day (P1, Kai + Riven)
- **Given** a stored day record whose `dayIndex` is `T - 1`, carrying recorded completions
- **When** the player loads Cinder and opens the Quest Log on day `T`
- **Then** the list and the streak number are recorded together, and they describe the same recorded history, or the contradiction is recorded as a defect under requirement 4

### Scenario 3: A record stale by 3 days (P1, Kai + Scout)
- **Given** a stored day record whose `dayIndex` is `T - 3` or earlier, carrying recorded completions
- **When** the player loads Cinder and opens the Quest Log on day `T`
- **Then** the list, the streak number, and the welcome-back panel are recorded together, and all three are consistent on the same page state

### Scenario 4: A record stale by 6 days (P1, Kai + Scout)
- **Given** a stored day record whose `dayIndex` is `T - 6` or earlier, carrying recorded completions
- **When** the player loads Cinder and opens the Quest Log on day `T`
- **Then** the list and the streak number are recorded together and are consistent, and the list still shows at most the last 5 recorded entries, most recent first

### Scenario 5: A record stale by 30 days (P1, Kai + Scout)
- **Given** a stored day record whose `dayIndex` is `T - 30` or earlier, carrying recorded completions
- **When** the player loads Cinder and opens the Quest Log on day `T`
- **Then** the list and the streak number are recorded together and are consistent, with no exception and no blocking error

### Scenario 6: Same-day reload (P1, Kai + Riven)
- **Given** a day record already stamped for today, loaded once and then reloaded on the same UTC day
- **When** the player opens the Quest Log after the reload
- **Then** the list and the streak number are recorded for the reload, and they match the values from the first load for the same recorded history

### Scenario 7: The list reads the recorded history, not the rebuilt record (P1, Kai, proof)
- **Given** a stale stored day record that carries recorded completions
- **When** the list is rendered from the loaded record's history and again from the record after `checkDailyReset()` has rebuilt it
- **Then** the rendered list comes from the recorded history and is not emptied by the rebuild, or the emptying is recorded as a defect under requirement 4

### Scenario 8: "No code defect found, claim narrowed" is accepted as a PASS (P1, Kai + Vigil)
- **Given** the proof shows the read path is correct in all five states
- **When** the story is closed
- **Then** it closes on the recorded proof plus any narrowed public claim, **no code change is made**, and the closure is recorded as a legitimate PASS, not as an incomplete story

### Scenario 9: A proven defect is fixed with a pure-read helper only (P1, Kai)
- **Given** the proof shows a state where the list and the streak number disagree on the record they describe
- **When** the fix lands
- **Then** it is a pure-read helper with no writes and no new field, called from the log's render path, and the defect is recorded with its reproduction

### Scenario 10: The read path writes nothing and adds no field (P1, Kai, proof)
- **Given** any state that renders the Quest Log
- **When** the player opens row 9 and the log renders
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical before and after, a static scan of the list and streak path finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, or state-mutating `character.` / `dayState.` writes, and no new field name appears anywhere in the diff

### Scenario 11: The day record shape is unchanged (P1, Kai + Scout)
- **Given** a save written by v0.22.0 and a save written by the build with this story applied
- **When** each is loaded and the raw JSON is compared
- **Then** the stored day record has exactly the same field set as before (`dayIndex`, `fightsUsed`, `innHealsUsed`, `quest`, `completedQuests`), with no added, removed, or renamed field

### Scenario 12: `checkDailyReset()` and `computeQuestStreak()` are byte-identical to v0.22.0 (P1, Kai, proof)
- **Given** the diff for this story in `src/cinder.html`
- **When** the code is inspected
- **Then** `checkDailyReset()` and `computeQuestStreak()` are textually unchanged from v0.22.0, and the story adds no history field and no change to the record the reset builds

### Scenario 13: The list contract is unchanged for the same history (P1, Riven + Scout)
- **Given** any history the proof covers
- **When** the list is rendered by the pre-story build and by the story build
- **Then** the two renders are identical: same order, same cap of 5, same relative day labels, same empty-state behaviour

### Scenario 14: Legacy, corrupt, and partial records degrade cleanly (P1, Kai + Scout, regression)
- **Given** a legacy day record with no `completedQuests`, and separately a corrupt record (`completedQuests` a string, an entry with a non-numeric `dayIndex`, `dayIndex` not a number, `dayState` null)
- **When** the game loads and the player opens the Quest Log
- **Then** it renders without error, the list renders or falls back to the empty-state line, the streak reads a correct value from the valid parts or 0, and both agree as far as the valid state allows

### Scenario 15: Storage unavailable or private mode (P1, Kai)
- **Given** the browser is in private mode or storage is unavailable, so the existing localStorage helpers are throwing and swallowing
- **When** the game loads and the player opens the Quest Log
- **Then** the game runs from in-memory state and the log behaves the same as with storage, and nothing throws

### Scenario 16: Story 042/044 welcome-back panel and streak source not regressed (P1, Scout, regression)
- **Given** an intact recorded run and a genuine hole, each on a multi-day gap
- **When** the welcome-back panel and the Quest Log render on the same page state
- **Then** the panel reads "Your streak survived." and "Your streak is broken." respectively, the log's streak matches the run the panel describes, and the two surfaces do not contradict each other

### Scenario 17: Story 033 preview and Story 037 badge not regressed (P1, Scout, regression)
- **Given** a player who completes and collects today's quest, and an installed player with the quest pending then completed
- **When** the quest view and the badge path run
- **Then** the "Tomorrow: ..." preview renders as before, and the badge behaves exactly as before (1 while pending, cleared on completed and rewarded)

### Scenario 18: Same-day and next-day returns stay quiet (P1, Kai + Scout, regression)
- **Given** a player who played earlier today, or whose last recorded play day is yesterday with nothing fully missed
- **When** the player loads or reloads Cinder and opens row 9
- **Then** no welcome-back panel renders in those cases, the log renders its list and streak, and the hub renders as the pre-story build renders it

### Scenario 19: Escalation, not implementation, if a persisted field is needed (P1, Vigil + Kai)
- **Given** the whole story's code and diff
- **When** it is reviewed
- **Then** it proves the outcome was achieved with existing state only, and if any part of the design had required a persisted field the team escalated it as a Story 039 amendment instead of implementing it, with no persisted field shipped

### Scenario 20: Out-of-scope references and forbidden fallbacks are absent (P1, Scout, the Session 24 D1/D2 defect class)
- **Given** the merged candidate's diff for `src/cinder.html`
- **When** Scout scans it
- **Then** no variable is referenced outside the scope that owns it (the Session 24 D1 class), and no read path falls back to the post-reset record when the loaded record is unavailable (the Session 24 D2 class), and where the loaded record is unavailable the helper returns 0 rather than reading the rebuilt record

### Scenario 21: No notifications, no push, no permission prompt, no install nag (P1, Vigil + Scout)
- **Given** this story's code
- **When** it is scanned and exercised in a browser
- **Then** it contains no `Notification` permission request, no `pushManager`, no subscription code, and no permission prompt or install prompt appears at any point in load or in the log path

### Scenario 22: Mobile-safe, Back to Town tappable, no inline onclick (P1, Riven + Scout)
- **Given** the Quest Log rendered at 375x667 and on desktop
- **When** the player taps Back to Town
- **Then** the tap is handled by the delegated `data-action` listener, the town hub renders, there is no horizontal overflow, and no inline `onclick` appears anywhere in the markup

### Scenario 23: Any narrowed claim matches the proof (P1, Riven + Vigil)
- **Given** the proof's per-state results
- **When** any narrowed public claim is reviewed against them
- **Then** it names the state it covers, is not weaker than what the proof shows, is not stronger, and cites the proof

### Scenario 24: Tone and no-AI-tells (P2, Vigil)
- **Given** any new or changed user-visible copy, and any narrowed claim text
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and matches the plain-punctuation, dry-humour Cinder and CEO voice

### Scenario 25: The worktree and ownership rule was followed (P1, Kai + Riven + parent)
- **Given** this story touched one file from two directions
- **When** the work is reviewed
- **Then** Kai and Riven each worked in a separate git worktree, one owner was named per helper and per call-site line before dev started, each dev's PR body states the exact line range it owns, and Scout's checks ran against the merged candidate rather than the two branches

## Technical notes (Quinn)

Verified against the shipped `src/cinder.html` at v0.22.0 (**64445 bytes**) by reading the code, not by inferring from the release notes. Repo `main` at `38ea83b` (Merge PR #98, release v0.22.0). Live deploy mirror `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` is byte-identical to `src/cinder.html` at session start (`cmp` exit 0, both 64445 bytes).

- **Single game file:** `src/cinder.html` is the source of truth. The deploy mirror is a **separate file outside the repo** at the ABSOLUTE path `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. It must end the session byte-identical to `src/cinder.html` (`cmp` exit 0, record the sha256). Never write a relative `share/...` path from inside the repo.
- **The two read expressions, precisely.** In `renderQuestLog()` (`src/cinder.html:624-646`):
  - the list, `src/cinder.html:627`: `const completed = (dayState && Array.isArray(dayState.completedQuests)) ? dayState.completedQuests : [];` then `src/cinder.html:633`: `const recent = completed.slice(-5).reverse();`
  - the streak, `src/cinder.html:629`: `const streak = computeQuestLogStreak(dayState, questLogAnchor);`
  The streak reads the **pre-reset anchor** (`questLogAnchor`, assigned at `src/cinder.html:1396` from `rawDayState`, captured at `src/cinder.html:1389` before `checkDailyReset()` at `src/cinder.html:1397`). The list reads the **post-reset `dayState`**. This asymmetry is the whole subject of the story: the two expressions currently read different objects.
- **Why the asymmetry can contradict.** `checkDailyReset()` (`src/cinder.html:727-737`) reassembles `dayState` wholesale when `dayState.dayIndex !== today`, setting `completedQuests: []`. On the load of a gap day the log is opened **after** that reset, so `dayState.completedQuests` is `[]` while `questLogAnchor.completedQuests` still holds the recorded history the streak helper reads. Whether this produces a visible contradiction (nonzero streak, empty list) on the shipped build is exactly what the proof must establish by running it, not by reasoning about it.
- **Expected shape of the finding (Kai to confirm, not to assume).** Reading the code, `dayState` on the shipped build is rebuilt with `completedQuests: []` only on the **first** load of a stale record; the reset's own `saveDayState()` stamps today, so a **reload** on the same day finds `dayState.dayIndex === today` and takes the `else` branch (`ensureQuestState()`), which preserves the array. So the first load of a stale-by-3/6/30-day record is the highest-probability contradiction state, and the same-day reload is the control. **Kai must confirm each by running, and must record the actual observed list and number, not these expectations.**
- **Fix shape if a defect is proven (Kai owns the final form).** Either (a) render the list from the same pre-reset anchor the streak helper uses (`questLogAnchor`, guarded with `Array.isArray`, falling back to the post-reset `dayState` only when the anchor is unusable), keeping the `slice(-5).reverse()` and `dayLabelForIndex()` rendering exactly as shipped; or (b) a pure-read helper following the `computeQuestLogStreak()` pattern that returns the list entries from the loaded record. Both are read-only, add no field, and write nothing. **Whichever shape is chosen, the escalation rule of requirement 4 stands: if the only correct fix needs a persisted field, escalate as a Story 039 amendment, do not implement.**
- **Existing state to read (do not change):** `renderQuestLog()` at `:624`; `computeQuestLogStreak()` at `:432-469`; `computeQuestStreak()` at `:382-404`; the recent-quests list and `dayLabelForIndex()` at `:613`; `getDayIndex()` at `:719`; `loadDayState()` / `saveDayState()` as the only `flambeee-cinder-day` accessors; `dayState.completedQuests` entries each carrying a numeric `dayIndex` plus `label` / `objective` (pushed in `completeQuest()`, `:317-321`); `ensureQuestState()` at `:244-258`; `computeAwayWindow()` at `:486` and its `lastPlayIdx` derivation; `shouldShowWelcomeBack()`; `renderWelcomeBack()`; the `init()` load path at `:1384-1404` where `rawDayState` and `questLogAnchor` are captured before `checkDailyReset()`; `handleTownInput` routing `case 9` to `renderQuestLog()` at `:1253`; `questLogAnchor` declared at `:690`; the delegated click listener at `:1326-1331`.
- **What "no writes" means here.** The load path legitimately runs `checkDailyReset()` (which may call `saveDayState()` for a new day) and `ensureQuestState()` (which may call `saveDayState()` when a legacy record lacks `quest` or `completedQuests`). Those are pre-existing v0.22.0 behaviours and are not part of the quest-log read path this story owns. Scenario 10's byte-identity claim is scoped to opening row 9 and rendering the log: with a well-formed day record already stamped for today, opening the log adds no write.
- **Proof expectation (Session 14 bar).** Kai provides a node-based proof script plus a static scan, same pattern as the Story 033/035/037/040/042/044 proofs (extracting the shipped functions into a sandbox). It must assert, for each of the five seeded states: the rendered list entries and their labels; the rendered streak number; consistency between the two; the first-load versus reload difference; the result after the wholesale rebuild; no forbidden writes; no new field name in the diff; `checkDailyReset()` and `computeQuestStreak()` textually unchanged; and the list identical to the pre-story rendering for the same history. Expected exit code 0.
- **QA bar.** Real browser at desktop and 375x667 with a real tap on row 9 and on Back to Town, a seeded record for each of the five states, a same-page-render check that reads **both** the panel and the log and asserts agreement, a control run against the pre-047 build for the regression scenarios, raw `flambeee-cinder-save` / `flambeee-cinder-day` values captured before and after opening the log, and the D1/D2 scan (out-of-scope references, forbidden fallbacks) run against the **merged** candidate.
- **Worktree rule (Session 25, fifth session running).** Kai and Riven must each work in a **separate git worktree** (`git worktree add` under a temp dir outside the main tree). Story 047 again puts both devs on one file (`src/cinder.html`), the highest-risk story shape in the repo. The two halves here are separable: Kai owns the read-path proof and, if needed, the list-source helper; Riven owns the rendered list expression and the rendered line. **Agree on one helper name and one owner in the Wave 3 brief, or make the reconciliation step explicit before merge.** This is the process defect Story 048 exists to remove.
- **Peer review:** Kai and Riven review each other's work in the usual direction before merge.

## Visual Description (Quinn)

The panel is Cinder's terminal text in a boxed menu, reached from the town hub as row 9. Story 047 does not change its styling: dark `#1a1a2e` panel, `2px solid #444` border, centered yellow `#ffcc00` `.header`, dashed `.divider`, plain body text, one `.menu-row` with `<span class="num">` for Back to Town. What the story audits is the **content** of the streak line and the list, and whether the two agree.

**State 1: first run, no record (unchanged, correct).**

```
+------------------------------------------------+
|            === QUEST LOG ===                   |   <- yellow .header, centered
|                                                |
|   Current streak: 0 days                       |
|                                                |
|   ------------------------------------------   |
|   Recent quests:                               |
|   No quests recorded yet. Finish today's       |   <- existing empty-state line (muted)
|   quest to start your log.                     |
|                                                |
|   ------------------------------------------   |
|   1. Back to Town                              |
+------------------------------------------------+
```

**State 2: stale record, list and number agree (the pass shape).**

```
+------------------------------------------------+
|            === QUEST LOG ===                   |
|                                                |
|   Current streak: 3 days                       |
|                                                |
|   ------------------------------------------   |
|   Recent quests:                               |
|   yesterday: Defeat 5 monsters                 |   <- most recent first, cap 5
|   2 days ago: Earn 50 gold from combat         |
|   3 days ago: Slay the boss                    |
|                                                |
|   ------------------------------------------   |
|   1. Back to Town                              |
+------------------------------------------------+
```

**State 3: stale record, list and number disagree (the defect this story hunts).**

```
+------------------------------------------------+
|            === QUEST LOG ===                   |
|                                                |
|   Current streak: 3 days                       |   <- number from the pre-reset anchor
|                                                |
|   ------------------------------------------   |
|   Recent quests:                               |
|   No quests recorded yet. Finish today's       |   <- list from the post-reset record: EMPTY
|   quest to start your log.                     |
|                                                |
|   ------------------------------------------   |
|   1. Back to Town                              |
+------------------------------------------------+
```

State 3 is the render the story must either prove does not occur on any reachable state, or fix. A live streak printed beside an empty list is the visible contradiction.

What changes, and what does not:

- **Changes only if a defect is proven:** the record the list reads, so that a nonzero streak cannot sit beside an empty list on a stale-record load. Same layout, same labels, same cap.
- **Unchanged:** the header, the streak line's text and style, the recent-quests label, the list order and cap of 5, the relative day labels, the divider, the Back to Town row, the `data-action` delegation, the colors, the fonts, the layout, the 375x667 behaviour, and the absence of any new hub row, banner, dot, or nag.
- **Never shown:** a list entry or a streak with an icon, a flame, or any flourish. Plain lines, as they render today.

Palette checks that the panel still reads as one Cinder view at 375x667 and at desktop, and that any change to the list does not disturb the layout, the wrapping, or the contrast of the surrounding text. Vigil checks that the list and the number are true in every branch, that the two cannot be read as contradicting each other, and that any narrowed claim matches the proof.

## Open questions

1. **Whether a code change is required at all (Kai, confirm in the proof).** Expected answer: to be determined by running, not by reasoning. Requirement 3 and Scenario 8 make "no code defect found, proof recorded and public claim narrowed" a PASS. Reading the code, the first load of a stale-by-3/6/30-day record is the highest-probability contradiction state, and the same-day reload is the control. Not a CEO question; a dev design decision recorded in the proof.
2. **The concrete list-source mechanism if a defect is proven (Kai, confirm in the proof).** Recommendation: render the list from the same pre-reset anchor the streak helper uses (`questLogAnchor`, `Array.isArray`-guarded), keeping the `slice(-5).reverse()` and `dayLabelForIndex()` rendering byte-identical to today. This keeps a single record for both expressions on the screen and makes non-contradiction provable on every input. Alternative: a pure-read helper following the `computeQuestLogStreak()` pattern. Either is read-only; not a CEO question.
3. **Scope of any claim narrowing (Riven/parent).** Recommendation: check the v0.22.0 release notes, the `docs/roadmap.md` v0.22.0 entry, and the website What's New block; narrow only where a claim is stronger than the proof. If the website copy needs editing, the edit lands before Story 049's run 2 so a single sync and a single run cover it.
4. **Singular day wording at 1 (Riven/Palette).** Recommendation: keep the existing `(streak === 1 ? ' day' : ' days')` behaviour unchanged. Not in scope to change.
5. **Session 23/24 duplicate-helper and collision hazard (parent/devs).** Requirement 8 is binding: separate worktrees, one owner per helper and per call-site line named before dev starts, and Scout reads the **merged** candidate. This is what Story 048 formalises.
6. **Escalation, if a persisted field turns out to be the only correct fix.** Per requirement 4 and Scenario 19: escalate as a Story 039 amendment plus CEO sign-off, do not implement. This is the only path in this story that needs CEO input, and only if the devs reach it.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 1 and the shipped code it names; nothing beyond that was invented.
