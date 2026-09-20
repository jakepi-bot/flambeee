# Test Plan: Story 040 - Cinder Welcome-Back Return Summary (Session 22)

**Story:** `docs/stories/040-cinder-welcome-back-summary.md` (14 BDD scenarios)
**Code under test:** `src/cinder.html`, Riven's branch `feature/040-cinder-welcome-back-riven`, pinned commit `28e5c49` (PR #83)
**Gate contract:** `flambeee-team/state/040-gate-spec.md`
**Harness:** `qa-story040.py` (Playwright, real Chromium, venv python at `/home/jake/.openclaw/workspace/.venv/bin/python3`)
**Run command:** `QA_PORT=8771 /home/jake/.openclaw/workspace/.venv/bin/python3 qa-story040.py`
**Result:** 167 checks, 0 failed, exit 0 (run twice on 2026-09-20, identical output both runs)

The artifact is extracted from the pushed commit with `git show 28e5c49:src/cinder.html`, never read from the mutable worktree, so the test cannot pass against uncommitted code.

## Method

Each scenario seeds a known localStorage state (`flambeee-cinder-save`, `flambeee-cinder-day`) before page load, then drives the real page. Assertions read the rendered DOM and the stored keys. No behaviour is stubbed; the only instrumentation is a `localStorage.setItem` wrapper used by the no-write checks, which records calls without changing them.

## Scenario coverage

### S1 Return after one fully missed day shows the summary once
Seed a save whose day record is `TODAY - 2`. Assert the summary renders, the header appears exactly once, and all four facts are present: days away (one-day phrasing), quests missed, streak status explicit, and today's quest pointer naming an objective. Assert the Back to Town action exists and no page errors occur.
**Result:** 11 checks PASS.

### S2 Same-day return and next-day return show no summary
Seed `TODAY` and `TODAY - 1`. Assert no summary, the town hub renders with all 9 rows intact, and no page errors. This is the regression guard for the Story 033 come-back-tomorrow flow.
**Result:** 7 checks PASS.

### S3 One-time per gap, no repeat nagging
From a seeded summary, dismiss to the hub, enter today's quest, return, then round-trip four further views (bank 4/3, inn 5/1, tavern 7/2, quest log 9/1). Assert no re-show at any point, then reload the page and assert the hub renders without a re-nag.
**Result:** 17 checks PASS.

### S4 The summary path writes nothing
Instrument `localStorage.setItem` inside the page. Assert the only load-time write is the pre-existing daily reset of `flambeee-cinder-day`, that no write originates in the summary path (stack-trace attributed), zero writes occur across the summary interaction, and both stored keys are byte-identical before and after.
**Result:** 10 checks PASS. The daily reset write is pre-existing behaviour and is attributed to `saveDayState` in `checkDailyReset`, not to Story 040.

### S5 Legacy save loads clean with no field loss
Seed a pre-040 save with no return-summary fields. Assert the summary shows, days away is derived correctly from a pre-040 record, the save gains no new key, and level, gold, XP, bank, wins are unchanged. Control run against the pre-040 build (`cinder-main.html`) asserts the character save and day record are byte-identical between the two builds for the same seed.
**Result:** 15 checks PASS.

### S6 No economy or balance change on return
Assert gold, XP, level, bank, wins, hp, deaths and the whole character save are identical at and after the summary, and that day-record dayIndex, fightsUsed, innHealsUsed, quest and completedQuests are identical. Confirms the fresh-day quest state comes from the pre-existing reset, not from Story 040.
**Result:** 18 checks PASS.

### S7 Quests missed is accurate
Sweep gaps 2, 3, 6 and 13 and assert the reported count is exactly `gapDays - 1`. Also assert a known 3-day window with no completion inside reports exactly 3 and that no count is invented.
**Result:** 7 checks PASS.

### S8 Streak status is stated, not implied
Seed a state that selects the broken branch and one that selects the survived branch. Assert each renders its explicit line and is not the other line.
**Result:** 6 checks PASS. Both branches exercised, no branch claimed without a run.

### S9 Private mode / storage unavailable
(a) Storage absent entirely: assert the game boots to character creation and in-memory play reaches the hub with a live character and no thrown errors. (b) Storage unreadable but state readable: assert the summary renders with intact facts and play continues.
**Result:** 8 checks PASS.

### S10 Corrupt day state and negative inputs
Garbage in `quest` (missing, string, null), `completedQuests` (not an array, a number, junk entries), `dayIndex` (non-numeric, NaN, future), the whole record as garbage, string, number, empty object, and unparseable JSON. For each: assert no exception, a view renders, and no summary appears where the window cannot be trusted. Also assert a corrupt `completedQuests` still yields a correct summary from the valid parts.
**Result:** 36 checks PASS.

### S11 Returning many days later
Seed a 30+ day gap. Assert the phrased sentence is used, the count is carried inside a sentence, no bare counter sits alone on a line, today's quest is named, the streak line is explicit, and there is no horizontal overflow at desktop width.
**Result:** 8 checks PASS.

### S12 No notifications, push, permission prompt or install nag
Static scan of the artifact for `Notification`, `pushManager`, `requestPermission`, `serviceWorker`, `beforeinstallprompt`, `onclick=`. Plus a DOM scan for install/permission text and an assertion that no permission dialog appeared during load, summary or play.
**Result:** 10 checks PASS.

### S13 Mobile safe, Back to Town tappable
At 375x667: assert no horizontal overflow, the panel fits the viewport, no inline `onclick` in the new markup, and that a **real tap** on Back to Town renders the hub. The row measures 297x41.5 px, fully on screen.
**Result:** 10 checks PASS.

### S14 Tone, no AI tells
Assert the rendered summary and the survived-branch copy contain no em dash and no heavy emoji.
**Result:** 4 checks PASS.

## Boundary and edge cases covered beyond the scenarios

- Gap 0 and gap 1 both suppressed; the gate flips exactly at gap 2 (verified by the sweep in S7 and the unit-level sweep in Kai's proof).
- `questsMissed <= daysAway` across the swept windows.
- Future `dayIndex` never produces a summary.
- Corrupt `completedQuests` degrades to a correct summary rather than no summary.
- Same-day reload after the daily reset does not re-nag.
- The pre-040 build control run isolates Story 040 as the only difference.

## Known, accepted limitations (recorded, not hidden)

1. **Same-day page reload re-shows the summary.** The one-time guard is in memory for the life of the page, which the gate spec and Story 040 open question 1 explicitly accept. A persisted flag would change the save shape, which Story 039 forbids. Back-navigation within the session does not re-show it (S3).
2. **The streak line normally reads "broken" on a real return.** `checkDailyReset()` rebuilds the day record, so the post-reset streak helper reads 0. Both branches exist and both are exercised (S8); preserving cross-day history across the reset is a separate decision, out of this story's scope.

## Verdict

No blocking defects. GO for release.
