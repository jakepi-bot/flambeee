# Test Plan: Story 047 - Cinder Quest Log, the Recent-Quests List and the Day-Record Read Path (Session 25)

**Story:** `docs/stories/047-cinder-recent-quests-read-path.md` (25 BDD scenarios)
**Code under test:** `src/cinder.html` at the merged candidate (post-merge `main`). The read expressions are:
- streak number: `computeQuestLogStreak(dayState, questLogAnchor)` (`src/cinder.html:629`), reads the **pre-reset anchor**;
- recent-quests list: `dayState.completedQuests.slice(-5).reverse()` (`src/cinder.html:627-637`), reads the **post-reset `dayState`**.
**Owners:** Kai (read-path proof, helper if a defect is proven), Riven (list expression, call site, copy corrections). Scout owns this plan, the real-browser checks, and the D1/D2 scan on the **merged** candidate.
**Harness:** `/home/jake/.openclaw/workspace/flambeee-team/scout-qa-session25-047.py` (drives the extracted shipped helpers through a node vm sandbox), plus the Playwright browser run.
**Baseline:** `src/cinder.html` 64445 bytes, sha256 `0dd0c0104ccc6a361ed56e05d01f749ea1cc742295c3055bac954fa7bc88efa5` at session entry.

## What is being verified

Whether the recent-quests list and the Current streak line describe **the same record**. The list reads the post-reset `dayState` (which `checkDailyReset()` rebuilds with `completedQuests: []` on the first load of a gap day); the number reads the pre-reset anchor `questLogAnchor`. The story hunts the contradiction (nonzero streak beside an empty list) and accepts "no code defect found, proof recorded, public claim narrowed" as a valid PASS.

## Method

- The node harness extracts `computeQuestStreak`, `computeQuestLogStreak`, `computeAwayWindow`, `shouldShowWelcomeBack`, `checkDailyReset`, `dayLabelForIndex`, `renderQuestLog`, `ensureQuestState` **verbatim** from the candidate file and runs the real `init()` order (capture, window, guard, reset, then render). It does not re-implement the helpers under test.
- The browser run seeds each state via `localStorage` and performs a real tap on hub row 9 and Back to Town at desktop and 375x667, reading **both** the rendered panel and the console log.
- QA verifies and reports. No product code is changed by this plan or harness.

## Scenario coverage

### S1 First run, no record (P1)
No stored day record, or a record with no `completedQuests`. Assert the empty-state line renders, the streak reads 0, and both agree; nothing thrown.
**Expected:** PASS.

### S2 A record stale by exactly 1 day (P1)
Stored `dayIndex = T-1` with recorded completions. Record the list and number together, assert they describe the same history.
**Expected:** PASS (or a recorded defect under requirement 4).

### S3 A record stale by 3 days (P1)
Stored `dayIndex = T-3` with completions. Record the list, the number, and the welcome-back panel together; assert all three agree on the same page state.
**Expected:** PASS.

### S4 A record stale by 6 days (P1)
`dayIndex = T-6`. Assert list and number agree; the list shows at most the last 5 entries, most recent first.
**Expected:** PASS.

### S5 A record stale by 30 days (P1)
`dayIndex = T-30`. Assert list and number agree, with no exception and no blocking error.
**Expected:** PASS.

### S6 Same-day reload (P1)
A record already stamped today, loaded then reloaded on the same UTC day. Assert the reload values match the first load for the same history.
**Expected:** PASS.

### S7 The list reads the recorded history, not the rebuilt record (P1)
Render the list from the loaded record's history and again after `checkDailyReset()` rebuilt it. Assert the rendered list comes from the recorded history and is not emptied by the rebuild (or the emptying is a recorded defect).
**Expected:** PASS. This is the story's core assertion.

### S8 "No code defect found, claim narrowed" is a PASS (P1)
If the proof shows correctness in all five states, closure on the recorded proof plus any narrowed claim is legitimate. Assert the harness reports no defect and the closure is recorded as a PASS.
**Expected:** PASS.

### S9 A proven defect is fixed with a pure-read helper only (P1)
Conditional: only if a disagreement is proven. Assert any fix is a pure-read helper with no writes, no new field, called from the render path.
**Expected:** covered by the harness's read-only scan; not triggered if S7 is green.

### S10 The read path writes nothing and adds no field (P1)
Open row 9 / render the log; assert `flambeee-cinder-save` and `flambeee-cinder-day` byte-identical before and after, static scan finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, or state-mutating writes in the list/streak path, and no new field name in the diff.
**Expected:** PASS.

### S11 The day record shape is unchanged (P1)
Assert the reset-built record field set is exactly `{dayIndex, fightsUsed, innHealsUsed, quest, completedQuests}`.
**Expected:** PASS.

### S12 `checkDailyReset()` and `computeQuestStreak()` byte-identical to v0.22.0 (P1)
Extract both functions from the candidate and from `git show v0.22.0:src/cinder.html`; assert identical text.
**Expected:** PASS.

### S13 The list contract is unchanged for the same history (P1)
Render the list by the pre-story build and the story build for the same history; assert identical: same order, cap 5, labels, empty-state behaviour.
**Expected:** PASS.

### S14 Legacy, corrupt, and partial records degrade cleanly (P1)
Legacy (no `completedQuests`), corrupt (`completedQuests` a string, non-numeric `dayIndex`, `dayIndex` not a number, `dayState` null). Assert no throw, correct render or empty-state fallback, correct-or-0 streak, agreement as far as valid state allows.
**Expected:** PASS.

### S15 Storage unavailable or private mode (P1)
With storage throwing/swallowing, assert the game runs from in-memory state and the log behaves the same; nothing throws.
**Expected:** PASS.

### S16 Story 042/044 welcome-back panel and streak source not regressed (P1)
Intact run and a genuine hole on a multi-day gap: panel reads "survived"/"broken" respectively and the log's streak matches the run the panel describes.
**Expected:** PASS.

### S17 Story 033 preview and Story 037 badge not regressed (P1)
Assert the "Tomorrow: ..." preview renders as before, and the badge path behaves as before (1 while pending, cleared on completed and rewarded).
**Expected:** PASS.

### S18 Same-day and next-day returns stay quiet (P1)
Assert no welcome-back panel in those cases, the log renders its list and streak, the hub renders as the pre-story build renders it.
**Expected:** PASS.

### S19 Escalation, not implementation, if a persisted field is needed (P1)
Assert the outcome was achieved with existing state only; no persisted field shipped.
**Expected:** PASS (no field added).

### S20 Out-of-scope references and forbidden fallbacks absent (P1, D1/D2 class)
On the **merged** candidate: no variable referenced outside its owning scope (D1); no read path falling back to the post-reset record when the loaded record is unavailable (D2); where the loaded record is unavailable the helper returns 0, not the rebuilt record.
**Expected:** PASS.

### S21 No notifications, push, permission prompt, or install nag (P1)
Static scan for `Notification`, `pushManager`, subscription code; browser: no permission/install prompt in load or the log path.
**Expected:** PASS.

### S22 Mobile-safe, Back to Town tappable, no inline onclick (P1)
At 375x667 and desktop: tap handled by the delegated `data-action` listener, town hub renders, no horizontal overflow, no inline `onclick`.
**Expected:** PASS.

### S23 Any narrowed claim matches the proof (P1)
Assert a narrowed public claim names the state it covers, is not weaker or stronger than the proof, and cites it.
**Expected:** PASS (or recorded as "no claim narrowing required" if the claim is already supported).

### S24 Tone and no-AI-tells (P2)
Any new/changed copy and any narrowed claim: no em dashes, no heavy emoji, plain-punctuation Cinder/CEO voice.
**Expected:** PASS.

### S25 The worktree and ownership rule was followed (P1)
Assert separate worktrees, one owner per helper and per call-site line named before dev, each PR body states its owned line range, and Scout's checks ran against the merged candidate.
**Expected:** PASS. Verified against the dev PR bodies and the merge history.

## Negative and boundary matrix

| Case | Condition | Expected |
|------|-----------|----------|
| Empty list, zero streak | first run, no record | consistent: empty list + 0 |
| Stale record, first load | `dayIndex = T-3`/`T-6`/`T-30` | list from recorded history, number nonzero, agree |
| Stale record, reload | stamped today, reloaded | values match the first load |
| Hole in the run | gap before last play day | number 0 and panel "broken" agree |
| `completedQuests` is a string | corrupt | no throw, empty-state or valid-part render |
| `completedQuests` entry `dayIndex` non-numeric | partial | invalid entry ignored, valid parts counted |
| `dayState` null | corrupt | no throw, empty-state line |
| `rawDayState` null / non-object | helper input | helper returns 0, never the rebuilt record (D2) |
| Storage throws | private mode | in-memory state, no throw |
| List > 5 entries | long history | capped at 5, most recent first |
| Variable used outside owning scope | merged candidate | absent (D1) |
| Inline `onclick` | any markup | absent |
| Horizontal overflow at 375px | mobile | none |

## Verdict

**Test plan status: written 2026-09-27. Executed against the merged candidate at Wave 3 time; results recorded in `/home/jake/.openclaw/workspace/flambeee-team/qa-results.md`.**

QA verifies and reports. No product code is modified by this plan.
