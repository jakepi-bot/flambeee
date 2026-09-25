# Test Plan: Story 045 - Cinder Welcome-Back Reload-Guard Proof and Corrected Claims (Session 24)

**Story:** `docs/stories/045-cinder-welcomeback-reload-guard-proof.md` (13 BDD scenarios)
**Code under test:** `src/cinder.html` at v0.21.0 / `fac7c32`. **This story requires no code change.** Its likely and expected PASS is "no code defect, claim corrected".
**Baseline artifact:** `src/cinder.html`, 1421 lines, 60754 bytes, sha256 `e48a1040083013f8e153cf8262074e20115d23245200b36502054f4e9febb56e`.
**Harness:** `/home/jake/.openclaw/workspace/flambeee-team/scout-qa-session24.py`, `/home/jake/.openclaw/workspace/.venv/bin/python3`, extracting the shipped `checkDailyReset()`, `computeAwayWindow()` and `shouldShowWelcomeBack()` into a node `vm` sandbox.

## What is being tested

v0.21.0 claims a same-day reload no longer re-shows the welcome-back panel. That claim is stronger than the code.

- **Case A, record stale by exactly 1 day.** `dayIndex === T-1` on the first load. `checkDailyReset()` sees `dayState.dayIndex !== today`, rebuilds the record, and calls `saveDayState()`, which writes `dayIndex: T`. `gapDays = todayIdx - lastPlayIdx`. With `lastPlayIdx = T-1`, `gapDays = 1`, `daysAway = gapDays - 1 = 0`, so `shouldShow = (daysAway >= 1)` is **false**: no panel appears at all on either load.
- **Case B, record stale by 3+ days.** `dayIndex <= T-3` on the first load. `lastPlayIdx = T-3`, `gapDays = 3`, `daysAway = 2`, `shouldShow` is **true**: the panel appears on the first load. `saveDayState()` inside the reset stamps `dayIndex: T`. The **reload** loads `dayIndex === T`, so `lastPlayIdx = T`, `gapDays = 0`, `daysAway = -1` clamped to 0, `shouldShow` false; `shouldShowWelcomeBack()` returns false. The player lands on the town hub.

**Case B is the behaviour the code delivers and the claim does not describe.** The behaviour is correct: the panel appears once per gap, which is what Story 042 required. The defect is in the published claim, not in `src/cinder.html`.

## Method

Each case seeds a day record relative to the live UTC day index `T`, then evaluates the **real shipped helpers** extracted from the file. `checkDailyReset()` is applied between load 1 and the reload for the reload evaluation, so the reset's write is exercised rather than simulated by hand. The harness prints, per case, the first-load and second-load `shouldShow` values and the observed outcome.

A case that shows the panel appearing is recorded as exactly that. A case that cannot be run is recorded as not run with the reason, never as a pass.

## Scenario coverage

### S1 Reload behaviour proven on a record stale by exactly 1 day (P2)
Seed `dayIndex: T-1` with recorded completions. Load, apply the reset, reload on the same UTC day.
**Assert:** the case is recorded with the exact command, exit code and auditable output; the record states plainly whether the panel appeared on the reload.
**Expected:** panel quiet on both loads (`daysAway = 0`). This is the case the v0.21.0 guard covers.

### S2 Reload behaviour proven on a record stale by 3 or more days (P2)
Seed `dayIndex: T-3` (and a second seed at `T-6`) with recorded completions. Load, apply the reset, reload on the same UTC day.
**Assert:** same recording requirement; the reload's outcome stated plainly.
**Expected:** panel appears on load 1 (`daysAway = 2`), quiet on the reload (`gapDays = 0` because the reset's own write stamped today). A panel re-appearing on the reload is Scenario 9 and a real defect.

### S3 Both proofs are auditable and re-runnable (P2)
Re-run each command and confirm the recorded result reproduces. Each record shows the command, the exit code, and the output, not a screenshot alone.
**Expected:** PASS, both cases reproduce.

### S4 "No code defect, claim corrected" is accepted as a PASS (P2)
If the proof shows correct behaviour in both cases, the story closes on the proof plus the corrected claim with **no code change**, recorded as a legitimate PASS.
**Expected:** PASS. A manufactured code change would violate the story, not satisfy it.

### S5 Each claim is backed by the proof or corrected (P2)
Artifacts to inspect, each either citing the proof exactly or corrected to the narrower true statement:
- the v0.21.0 GitHub release notes (title "Cinder says welcome back, and now it means it", published 2026-09-22T15:03:20Z),
- the `docs/roadmap.md` v0.21.0 one-time-guard paragraph,
- the website What's New block on `/home/jake/.openclaw/workspace/share/Flambeee/index.html` **if it repeats the claim**,
- the commit messages between the v0.20.0 and v0.21.0 tags.
**Expected:** PASS if each artifact either matches the proof or names the one-day case the guard covers. The live website summary currently reads "the panel no longer reappears when you reload the page the same day", which is the overstatement to check.

### S6 A supported claim is not weakened (P2)
If both cases show the panel quiet on the reload, assert no claim is weakened beyond what the proof shows and the proof is cited where a claim stands.
**Expected:** PASS. Over-correction is a defect in this story too.

### S7 The corrected claim is precise, not vague (P2)
Assert the corrected claim names the case it covers (a reload on a record stale by one day, against the daily reset's own stamping of today on the first load of a longer gap) and uses no "usually"/"normally" hedging where the behaviour is deterministic.
**Expected:** PASS.

### S8 Corrections follow the SDLC (P2)
Assert any correction lands on a branch, in a PR, with peer review, and never directly on `main`. A website copy correction is synced to `/home/jake/.openclaw/workspace/share/Flambeee/index.html` and re-verified.
**Expected:** PASS. A direct-to-main edit is a blocking process defect.

### S9 A real defect, if found, gets a separate constrained fix (P2)
If the proof shows the panel **re-appears** on a same-day reload in the multi-day case, assert the defect is recorded with reproduction, the fix is read-only presentation with no new persisted field, no write on the summary path, `checkDailyReset()` unchanged, or it is escalated as a Story 039 amendment plus CEO sign-off.
**Expected:** not triggered (both cases are expected quiet). Recorded here so the negative branch is covered.

### S10 No new state, no write, no mechanic change (P2)
Assert `src/cinder.html` is byte-identical to its v0.21.0 state unless S9 applied, no new persisted field exists, and no economy, balance, rotation, or difficulty behaviour changed.
**Expected:** PASS. Baseline sha256 `e48a10...`; the candidate must match unless S9 applied.

### S11 Truthful recording (P2)
Compare the recorded exit codes and outputs against the real command output and the real repository state. Assert nothing is reported green that was not green, and a case that showed the panel appearing is recorded as exactly that.
**Expected:** PASS.

### S12 Tone and no-AI-tells on corrected copy (P2)
Scan corrected and added claim text for em dashes and heavy emoji; assert the CEO's direct tone.
**Expected:** PASS.

### S13 The checker and other surfaces are untouched (P2)
Assert `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state (sha256 `bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92` at session entry), no new verification script was added, and no cron config, `jobs/`, `jobs-refactor-team/`, or `jakebot/` file was touched.
**Expected:** PASS.

## Negative and boundary matrix

| Case | Input | Expected |
|------|-------|----------|
| Same-day, record stamped `T` | `gapDays 0` | no panel on load, no panel on reload |
| 1-day stale | `dayIndex: T-1` | no panel on load (`daysAway 0`), no panel on reload |
| 2-day stale | `dayIndex: T-2` | panel on load, quiet on reload |
| 3-day stale | `dayIndex: T-3` | panel on load, quiet on reload |
| 6-day stale | `dayIndex: T-6` | panel on load, quiet on reload |
| Long gap, 30 days | `dayIndex: T-30` | panel on load, phrased sentence, quiet on reload |
| Corrupt `dayIndex` (string/NaN/null) | unreadable stamp | no throw, no panel |
| `null` record | no record at all | no throw, no panel |
| Completions newer than the day stamp | completion inside the nominal gap | anchor moves to the newer completion, no throw |

## Verdict

**Test plan status: written 2026-09-25. Execution results are recorded in `/home/jake/.openclaw/workspace/flambeee-team/qa-results.md`, Session 24 section (both staleness cases side by side).**

QA verifies and reports. QA does not fix product code and does not edit release notes or website copy.
