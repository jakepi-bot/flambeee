# Test Plan: Story 042 - Cinder Welcome-Back Streak Truth and One-Time-Per-Gap Guard (Session 23)

**Story:** `docs/stories/042-cinder-welcomeback-streak-and-once-per-gap.md` (21 BDD scenarios)
**Code under test:** `src/cinder.html`, the integrated result of Kai's branch `feature/042-cinder-streak-proof-kai` and Riven's branch `feature/042-cinder-welcomeback-view-riven`, both based on `main` at `13597d7`.
**Baseline for regressions:** `main` at `13597d7`, `src/cinder.html` blob `3409b6da1da417d0671bc41630fcc6116d7c3f3e`, sha256 `dde7125b99bb2ac32660d453ed714933e1ab988f639b516b1a16110125763482` (identical to tag `v0.20.0`).
**Harness:** `qa-story042.py` (Playwright, real Chromium, `/home/jake/.openclaw/workspace/.venv/bin/python3`).
**Artifact rule:** the code under test is extracted from the merged branches with `git show <commit>:src/cinder.html`, never read from a mutable worktree, so the test cannot pass against uncommitted code.

Story 042 puts **two devs on one file**. Testing one branch alone proves nothing about the merged candidate, so this plan tests the integrated result: a QA worktree merges both branches and the artifact is pinned from that merge commit.

## Method

Each scenario seeds a known `localStorage` state (`flambeee-cinder-save`, `flambeee-cinder-day`) before page load, then drives the real page exactly as a returning player would. Assertions read the rendered DOM and the stored keys. Nothing is stubbed. The only instrumentation is a `localStorage.setItem` wrapper used by the no-write checks, which records calls without changing them. `getDayIndex()` is `Math.floor(Date.now() / 86400000)`, so the harness seeds indexes relative to the live UTC day index `T`.

## Scenario coverage

Story 042 puts two devs on one file. Testing one branch alone proves nothing about the merged candidate, so this plan tests the integrated result: a QA worktree merges both branches and the artifact is pinned from that merge commit.

### S1 Streak reads survived on an intact run
Seed `completedQuests` with `T-4, T-3, T-2`, `dayIndex: T-2`. Assert the summary renders, the streak line is "Your streak survived.", and the broken line is absent.
**Result:** PASS.

### S2 Streak reads broken on a genuine hole
Seed `completedQuests` with `T-6, T-5`, `dayIndex: T-2` (T-4 is a hole before the last play day). Assert the streak line is "Your streak is broken." and the survived line is absent.
**Result:** PASS.

### S3 A single recorded day counts as intact
Seed `completedQuests: [{ dayIndex: T-3 }]`, `dayIndex: T-3`. Assert the streak line is "Your streak survived.".
**Result:** PASS.

### S4 Streak source is the recorded history, never the post-reset record
Assert the streak status is identical before and after `checkDailyReset()` replaces the record wholesale, and that the rebuilt record's empty `completedQuests` is not the source. Proven directly in the browser by reading the stored day key (which `checkDailyReset()` rewrites with `completedQuests: []`) and confirming the rendered line still reflects the loaded history.
**Result:** PASS. The post-reset stored record has an empty history while the rendered line still reports the pre-reset run.

### S5 No repeat on a same-day reload
Show the summary, dismiss to town, then reload the page on the same UTC day. Assert the summary does not render, the town hub renders, and no quest, streak, or save state changed as a result of the reload.
**Result:** PASS. The suppression rests on the pre-existing `saveDayState()` call inside `checkDailyReset()`, which stamps today on the first load of a stale day; the reload therefore finds `dayIndex === today` and `awayWindow.shouldShow` is false.

### S6 No repeat on a later visit inside the same gap window
Show and dismiss the summary, then load the page again with the day record already stamped for today (the state a later visit inside the same gap finds). Assert no summary and a direct landing on the town hub.
**Result:** PASS.

### S7 A genuinely new gap still shows the summary once
Load on day `T` with a record stamped `T` (next-day-style quiet state), then load with a record stamped `T-3` so `T-2` and `T-1` are fully missed. Assert the summary renders exactly once with the correct days-away, quests-missed, streak line, and today's-quest pointer.
**Result:** PASS.

### S8 The summary path writes nothing and adds no field
Instrument `localStorage.setItem` for the duration of the summary interaction. Assert zero writes to `flambeee-cinder-save` and `flambeee-cinder-day` on the summary path, byte-identity of both keys before and after, and a static scan of the diff finding no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `completeQuest`, `applyQuestProgress`, or state-mutating `character.` / `dayState.` write, and no seen-flag, gap-stamp, or version-marker field name.
**Result:** PASS. See the static scan section for the exact commands.

### S9 The day record shape is unchanged
Compare the stored day record field set against the baseline. Assert exactly `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }`, with no added, removed, or renamed field.
**Result:** PASS.

### S10 `checkDailyReset()` is not changed
`git diff <baseline> <merged>` for the `checkDailyReset()` block, and a blob-hash comparison of the extracted block between the two revisions. Assert textually unchanged.
**Result:** PASS. See the static scan section for the block hash.

### S11 Same-day and next-day returns stay quiet
Seed a record stamped `T` (same-day) and a record stamped `T-1` (next-day, nothing fully missed). Assert no summary in either case and that the town hub renders exactly as the baseline build renders it.
**Result:** PASS.

### S12 Story 033 come-back-tomorrow preview not regressed
Complete and collect today's quest, open the quest view, and assert the "Tomorrow: ..." preview and its "Come back after midnight to start it." line render, and that no summary or guard state interferes.
**Result:** PASS.

### S13 Story 035 quest log and streak not regressed
Open the Quest Log (hub row 9) with history and assert the Current streak line and recent-quests list render from `computeQuestStreak(dayState)` and `dayState.completedQuests`. Assert `computeQuestStreak()` is byte-identical to the baseline.
**Result:** PASS. See the static scan section for the block hash.

### S14 Story 037 app-icon badge not regressed
Instrument `navigator.setAppBadge` / `clearAppBadge`, load with the quest pending (expect 1), then complete and collect it (expect cleared). Assert the summary path neither calls the badge helper differently nor leaves the badge stale.
**Result:** PASS.

### S15 Legacy and corrupt day records still load clean
Load a legacy record with no `quest` and no `completedQuests`, and separately corrupt records: `completedQuests` a string, an entry with a non-numeric `dayIndex`, an array of junk, negative indexes, `dayIndex` not a number, `dayState` null. Assert the game loads without error, the summary either renders correctly from the valid parts or does not render, no exception is raised, and no corrupt field is rewritten beyond the existing `ensureQuestState()` backfill.
**Result:** PASS. Every case loads clean with no page error. See the negative-test section.

### S16 The guard's state is existing state only
Assert the guard's decision is derivable from `awayWindow` (the load-time window value), `returnShown` (the load-time flag), and the loaded record alone, and is identical on a repeat read of the same state. Static scan confirms no persisted flag.
**Result:** PASS.

### S17 Private mode and unavailable storage
Load with `localStorage.getItem` / `setItem` throwing, on a gap day, and play. Assert the game runs from in-memory state, the summary and the guard behave the same as with storage, and nothing throws.
**Result:** PASS.

### S18 No notifications, no push, no permission prompt, no install nag
Static scan for `Notification`, `pushManager`, `requestPermission`, `serviceWorker`, `beforeinstallprompt`, `onclick=`, and a browser run asserting no dialog appears and no permission or install text is in the DOM.
**Result:** PASS. See the static scan section.

### S19 Mobile-safe, both rows tappable, no inline onclick
Render at 375x667, tap Back to Town and separately the row into today's quest. Assert both taps are handled by the delegated `data-action` listener, the hub and the quest view render, there is no horizontal overflow, and no inline `onclick` appears in the markup.
**Result:** PASS.

### S20 Escalation, not implementation, if a persisted field is needed
Review the diff and assert the fix was achieved with existing state only, that no persisted field shipped, and that no part of the design required escalation.
**Result:** PASS. No persisted field in the diff. Both devs' guard derivations use only the loaded record plus the load-time in-memory flag.

### S21 Tone and no-AI-tells
Scan new and changed user-visible copy for em dashes and heavy emoji, and check the rendered survived and broken lines against the plain-punctuation Cinder voice.
**Result:** PASS. Only the streak line's choice of existing string changed, and both strings are plain punctuation, no em dash, no emoji.

## Static scans

Run against the merged artifact, not a worktree file.

```
# forbidden write calls / field names in the diff
git diff <baseline> <merged> -- src/cinder.html | grep '^+' \
  | grep -nE "saveCharacter\(|saveDayState\(|localStorage\.setItem|completeQuest\(|applyQuestProgress\(|seenReturn|welcomeBackShown|lastGapStamp|versionMarker"

# inline onclick / notification surface
grep -c "onclick=" src/cinder.html
grep -c "Notification" src/cinder.html
grep -c "pushManager" src/cinder.html

# checkDailyReset() and computeQuestStreak() block identity baseline vs candidate
awk '/function checkDailyReset/,/^  }/' src/cinder.html | git hash-object --stdin
awk '/function computeQuestStreak/,/^  }$/' src/cinder.html | git hash-object --stdin
```

Baseline block hashes on `main` at `13597d7`:

```
checkDailyReset     9d6278b683588f3062132ceafd2f394ea42fb446
computeQuestStreak  352e7dcd107a16c4206661d35e5a6cfc9980aa96
```

## Negative tests

| Input | Expected | Result |
|-------|----------|--------|
| Legacy day record (no `completedQuests`, no `quest`) | Loads clean, backfill only, no exception, no summary or a correct one | PASS |
| `completedQuests` a string | No exception, no crash, hub or a correct summary renders | PASS |
| `completedQuests` a number | No exception | PASS |
| `completedQuests` an array of junk entries | No exception, entries ignored | PASS |
| Negative day indexes (`T-99999`, `-1`) | No exception, no bogus summary count | PASS |
| `dayIndex` non-numeric (string, NaN, null) | No exception, summary suppressed or correct | PASS |
| `dayIndex` in the future | No exception | PASS |
| Whole record garbage / string / number / empty object | No exception, hub renders | PASS |
| Unparseable JSON in the day key | No exception, hub renders | PASS |
| Character save corrupt | No exception, character creation offered | PASS |
| `localStorage` throwing on read and write | In-memory play, nothing throws | PASS |
| Storage entirely absent | Boots to character creation, in-memory play reaches the hub | PASS |

## Regression control run

The regression scenarios (S12 Story 033 preview, S13 Story 035 quest log and streak, S14 Story 037 badge) are also run against the baseline build for the same seeds, so a difference in rendering is attributable to this story rather than to a pre-existing state.

## Verdict

**Executed 2026-09-22. Shipping candidate is PR #92 `feature/042-integration-recon` (`4c531a4`), artifact sha256 `e48a1040083013f8e153cf8262074e20115d23245200b36502054f4e9febb56e`. 91 checks, 0 failed, 2 runs, exit 0.** Kai's 47-check proof also green on the same artifact. Baseline control (pre-042 build, same harness): 87/91, 4 failed, and the 4 failures are exactly the Story 042 defect the fix targets. QA's own merge candidate (`cb8c4a6`) was tested first and is behaviourally equivalent; #92 supersedes it with a single implementation. Full output: `flambeee-team/qa-results.md`, Session 23 section.

Per-scenario, static-scan, block-identity, negative-test and guard-equivalence evidence is pasted there. QA verifies and reports; any defect found is reported with reproduction steps, never fixed here.
