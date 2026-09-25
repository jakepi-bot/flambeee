# Story 045: Cinder Welcome-Back Reload-Guard Proof on a Genuinely Stale Record, and Correcting Every Artifact That Claims More Than the Code Does (Session 24, P2)

**Status:** Ready for verification (Session 24, first half, 2026-09-25). Verification-shaped. **A return of "no code defect, public claim corrected" is a valid and expected PASS.**
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (truthfulness: the code behaves correctly, and the release notes and roadmap assert more than the code does; the artifacts are the defect).
**Assigned to:** **Kai** - the recorded proof of reload behaviour on a record stale by exactly 1 day and by 3+ days, with command, exit code, and auditable output. **Riven** - the copy surfaces: release notes text, the roadmap line, website What's New if it repeats the claim, and the commit message. **Scout** owns the negative cases and the test plan (including the case where the claim has to be narrowed). **Vigil** confirms the corrected claim matches the proof and that nothing is asserted without evidence.
**Tracked by:** Session 24 plan Priority 2. Verifies the behaviour Story 042 shipped in v0.21.0. Related to Story 040 (the one-time guard and its disclosed limits), Story 039 (the decision record the release notes cite), and Story 043 (the recording pattern this story reuses).

## Summary

v0.21.0's core claim was that a same-day reload no longer re-shows the welcome-back panel. **That claim is stronger than the code.**

It holds when the reload lands on `todayIdx === raw.dayIndex + 1`, which is the reload of a record stale by exactly one day. It does **not** hold for a record already stale by **more than one day**, which is the normal state of a player who has been away for a while. On the first load of such a record, `checkDailyReset()` (`src/cinder.html:656`) rebuilds `dayState` wholesale and writes the fresh record, which stamps today into storage. The reload then loads a record whose `dayIndex` is today, `computeAwayWindow()`'s own candidates make `lastPlayIdx === today`, `gapDays === 0`, `awayWindow.shouldShow` is false, and `shouldShowWelcomeBack()` returns false with no additional guard at all. The player lands on the town hub.

**That is the correct behaviour.** The panel appears once per gap, which is what Story 042 required and what Story 040 specified. The defect is not in `src/cinder.html`. The defect is that the **release notes and the roadmap line** state a broader "no longer re-shows on a same-day reload" than the code delivers in the multi-day case, and no artifact records the two cases separately.

This story therefore does two things:
1. **Prove it.** Record reload behaviour on a record stale by **exactly 1 day** and on a record stale by **3+ days**, each with the command, the exit code, and auditable output.
2. **Make every public claim match the proof.** Every claim about reload behaviour - release notes text, the roadmap line, website What's New if it repeats the claim, and any commit message - is either backed by that proof or corrected to the narrower true statement.

**Explicit, and important: if the proof shows the code is correct in both cases, the correct outcome for this story is "no code defect found, claim corrected". That is a PASS. No code change is mandatory.** Shipping a code change the proof does not require would violate the story, not satisfy it.

## Business value

- Truthfulness is a company rule, not a polish item. The last release asserted something the code only half did, and the assertion is still published.
- The proof makes the reload behaviour auditable: two staleness cases, two commands, two exit codes, on the record. Anyone can re-run them.
- The recording requirement prevents the same class of defect next session. A claim without a run behind it is what this story exists to stop.
- It is nearly free: no product surface, and the likely outcome is a copy correction rather than any code change.

## User Story

As the Flambeee team that shipped v0.21.0,
I want the same-day reload guard proven on a record stale by 1 day and by 3+ days and every public claim about it matched to that proof,
So that the release notes and roadmap describe what the game actually does, and nobody has to guess which staleness case the claim was about.

## Requirements

### 1. Recorded proof of reload behaviour, both staleness cases

- **Case A, record stale by exactly 1 day.** Seed a day record whose `dayIndex` is `T - 1` (one fully missed day), load Cinder, dismiss or observe the welcome-back panel, then reload on the same UTC day `T`. Record the observed behaviour.
- **Case B, record stale by 3 or more days.** Seed a day record whose `dayIndex` is `T - 3` or earlier (the normal state of a player who has been away), load Cinder, then reload on the same UTC day `T`. Record the observed behaviour.
- Each case is recorded with: the exact **command** that produced it, the **exit code**, and **auditable output** (the rendered state or the assertions printed by the harness). A screenshot alone is not auditable output; the recorded artifact must show the command and its result.
- The proof must state plainly, per case, whether the panel appeared on the **second** load (the reload). "Did not appear" is a result and must be recorded as such.
- The proof must **not** be constructed to force a particular outcome. Its job is to report what the shipped build does.

### 2. Every public claim about this behaviour is backed or corrected

- Identify every published or committed artifact that makes a claim about the same-day reload guard, at minimum: the **v0.21.0 GitHub release notes**, the **roadmap line** for v0.21.0 in `docs/roadmap.md`, the **website What's New** block on `share/Flambeee/index.html` if it repeats the claim, and the **commit messages** on `main` for the v0.21.0 release.
- For each artifact, either:
  - **(a) cite the recorded proof** and show the claim is exactly what the proof shows, or
  - **(b) correct the claim** to the narrower true statement: the panel does not re-show on a same-day reload **when the reload lands on a record stale by one day** (`todayIdx === raw.dayIndex + 1`, the case the guard covers), and the multi-day case is handled by the daily reset's own write, which stamps today on the first load - so the reload finds `gapDays === 0` and the panel is not eligible.
- **Do not weaken a claim that the proof supports.** If Case A and Case B both show the panel stays quiet, the claim can stand, with the proof cited.
- Corrections go through the normal SDLC: branch, PR, peer review, never direct to `main`. A correction to the roadmap or to release notes is a small docs PR. A correction to the website What's New is a website edit that must be synced to the live file and then re-verified under Story 046's run 2.

### 3. The outcome "no code defect, claim corrected" is a valid and expected PASS

- This story **does not require a code change**. If the proof shows the shipped behaviour is correct in both staleness cases (panel shown once per gap, quiet on the reload), the story passes on the proof plus the corrected claim.
- A code change is required **only** if the proof shows the behaviour is actually wrong in a reachable case - for example, if the panel **re-appears** on a same-day reload in Case B. In that event, the fix is a Story 044/042-class read-only presentation fix, and it brings its own constraints: no new persisted field, no write on the summary path, `checkDailyReset()` unchanged, and the Story 039 escalation rule if a persisted field turns out to be the only correct fix.
- The story must **not** be read as authorizing a mechanism. Changing the guard, adding a flag, adding a gap stamp, or changing `checkDailyReset()` is out of scope. If the proof shows a mechanism is needed, that is a Story 039 decision-record amendment plus CEO sign-off: escalate, do not implement.

### 4. No new persisted field, no writes, no mechanic change

- No new field on the character save or on the day record, and no new persisted value of any kind.
- This story's proof runs must not leave a write in the shipped code path. Seeding a record is a test fixture, not a product change.
- `checkDailyReset()`, `computeAwayWindow()`, `shouldShowWelcomeBack()`, and `computeQuestStreak()` are not changed by this story. If a change is genuinely required by the proof, it follows requirement 3's constraints, not a new mechanism.
- No economy, balance, reward, rotation, or difficulty change. No new hub row, panel, banner, notification, push, permission prompt, or install nag.

### 5. Copy discipline on any corrected or added text

- Any corrected claim uses plain punctuation, no em dashes, and no heavy emoji, in the CEO's direct tone with no AI tells. This applies to the release-note edit, the roadmap line, the website copy, and PR titles and bodies.
- The corrected claim states the narrow true behaviour and names the case it covers. It does not hedge into vagueness ("usually", "normally") where the code is deterministic.

### 6. Recording and truthfulness

- The proof is written where the session records verification results (the QA results file for this session), with both cases side by side.
- Every recorded exit code and output line is the real output of the command that produced it. Nothing is reported green that was not green, and a case that shows the panel appearing is recorded as exactly that.
- If a case could not be run, it is recorded as not run with the reason, never as a pass.

## Out of scope

- Any new persisted field, gap stamp, version marker, or seen flag. **No new state of any kind.**
- Any change to `checkDailyReset()`, `computeAwayWindow()`, `shouldShowWelcomeBack()`, or `computeQuestStreak()` as a **requirement** of this story. Those are unchanged unless requirement 3's conditional applies, and then only under its constraints.
- Any change to the welcome-back panel's content, wording, rows, or styling. The panel is not in scope to redesign.
- Multi-day welcome-back suppression on a later UTC day inside one gap as a **feature**. Still a Story 039 amendment plus CEO sign-off, as recorded in v0.21.0.
- Any offline resource accrual, balance change, or new mechanic.
- Any website redesign, layout change, or new What's New feature beyond correcting the claim if it repeats it.
- Any change to `scripts/verify-website-currency.sh`. Story 046 owns the checker runs.
- Any change to the noon Bluesky posting flow, the deploy pipeline, or the service worker cache version.
- Any cron configuration, and any file under `jobs/`, `jobs-refactor-team/`, or `jakebot/`.

## Acceptance Criteria (BDD)

### Scenario 1: Reload behaviour proven on a record stale by exactly 1 day (P2, Kai)
- **Given** a seeded day record whose `dayIndex` is `T - 1`, one fully missed day
- **When** the record is loaded and Cinder is reloaded on the same UTC day `T`
- **Then** the second load's behaviour is recorded with the exact command, the exit code, and auditable output, and the record states plainly whether the panel appeared on the reload

### Scenario 2: Reload behaviour proven on a record stale by 3 or more days (P2, Kai)
- **Given** a seeded day record whose `dayIndex` is `T - 3` or earlier, the normal state of a returning player
- **When** the record is loaded and Cinder is reloaded on the same UTC day `T`
- **Then** the second load's behaviour is recorded with the exact command, the exit code, and auditable output, and the record states plainly whether the panel appeared on the reload

### Scenario 3: Both proofs are auditable and re-runnable (P2, Kai + Scout)
- **Given** the two recorded cases
- **When** a reviewer re-runs each command
- **Then** each reproduces the recorded result, and each record shows the command, the exit code, and the output, not a screenshot alone

### Scenario 4: "No code defect, claim corrected" is accepted as a PASS (P2, Kai + Vigil)
- **Given** the proof shows the shipped build shows the panel once per gap and stays quiet on the reload in both staleness cases
- **When** the story is closed
- **Then** it closes on the proof plus the corrected claim, **no code change is made**, and the closure is recorded as a legitimate PASS, not as an incomplete story

### Scenario 5: Each claim is backed by the proof or corrected (P2, Riven + Vigil)
- **Given** the v0.21.0 release notes, the roadmap line, the website What's New block, and the v0.21.0 commit messages
- **When** each claim about the same-day reload guard is reviewed against the recorded proof
- **Then** each one either cites the proof and matches it exactly, or is corrected to the narrower true statement naming the one-day case the guard covers

### Scenario 6: A supported claim is not weakened (P2, Riven + Vigil)
- **Given** the proof shows the panel stays quiet on the reload in Case A and Case B
- **When** the artifacts are reviewed
- **Then** no claim is weakened beyond what the proof shows, and the proof is cited where the claim stands

### Scenario 7: The corrected claim is precise, not vague (P2, Riven + Vigil)
- **Given** a corrected claim
- **When** it is read
- **Then** it names the case it covers (a reload on a record stale by one day, against the daily reset's own stamping of today on the first load of a longer gap) and uses no hedging where the behaviour is deterministic

### Scenario 8: Corrections follow the SDLC (P2, Riven + Kai)
- **Given** any artifact that needs correcting
- **When** the correction is made
- **Then** it lands on a branch, in a PR, with peer review, and never directly on `main`, and a website copy correction is synced to `/home/jake/.openclaw/workspace/share/Flambeee/index.html` and re-verified

### Scenario 9: A real defect, if the proof finds one, gets a separate constrained fix (P2, Kai + Vigil)
- **Given** the proof shows the panel **re-appears** on a same-day reload in the multi-day case
- **When** the story is closed
- **Then** the defect is recorded with its reproduction, and the fix is a read-only presentation fix with no new persisted field, no write on the summary path, and `checkDailyReset()` unchanged, or it is escalated as a Story 039 amendment plus CEO sign-off if a persisted field would be the only correct fix

### Scenario 10: No new state, no write, no mechanic change (P2, Kai, proof)
- **Given** this story's artifact (the proof and the corrected copy)
- **When** the repository is inspected
- **Then** `src/cinder.html` is byte-identical to its v0.21.0 state (unless Scenario 9 applied), no new persisted field exists anywhere, and no economy, balance, rotation, or difficulty behaviour changed

### Scenario 11: Truthful recording (P2, Vigil)
- **Given** the two recorded cases and the corrected artifacts
- **When** Vigil compares them against the actual command output and the actual repository state
- **Then** the recorded exit codes and outputs are truthful, nothing is reported green that was not green, and a case that showed the panel appearing is recorded as exactly that

### Scenario 12: Tone and no-AI-tells on corrected copy (P2, Vigil)
- **Given** any corrected or added claim text
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and reads in the CEO's direct tone with no AI tells

### Scenario 13: The checker and other surfaces are untouched (P2, Kai + Vigil)
- **Given** this story's session
- **When** the repository is inspected
- **Then** `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state, no new verification script was added by this story, and no cron configuration, `jobs/`, `jobs-refactor-team/`, or `jakebot/` file was touched

## Technical notes (Quinn)

Verified against the shipped `src/cinder.html` at v0.21.0 by reading the code and the published artifacts, not by trusting the release notes. Repo `main` at `d290f82`.

- **Why Case A and Case B differ, precisely.**
  - **Case A (`dayIndex === T - 1` on the first load):** `checkDailyReset()` (`:656-666`) sees `dayState.dayIndex !== today`, rebuilds the record, and calls `saveDayState()`, which writes `dayIndex: T`. The **first** load shows the panel (`awayWindow.shouldShow` is true: `gapDays = 1`, `daysAway = 0`... note `daysAway = gapDays - 1 = 0`, so `shouldShow` is **false** in this case and no panel appears at all; the reload also finds `dayIndex === T`, `gapDays 0`, quiet). This is the case the v0.21.0 claim was written about: the guard holds.
  - **Case B (`dayIndex <= T - 3` on the first load):** the first load shows the panel (`gapDays >= 3`, `daysAway >= 2`, `shouldShow` true), and `saveDayState()` inside the reset stamps `dayIndex: T`. The **reload** loads `dayIndex === T`, `computeAwayWindow()` takes `lastPlayIdx = T`, `gapDays = 0`, `daysAway = -1` clamped to 0, `shouldShow` false; `shouldShowWelcomeBack()` returns false; the player lands on the town hub. **Behaviour correct, claim overstated.** Kai must confirm each of these by running them, and must record the actual observed values rather than these expectations.
- **The claim sites to check:** the v0.21.0 GitHub release notes (title "Cinder says welcome back, and now it means it", published 2026-09-22T15:03:20Z), the `docs/roadmap.md` v0.21.0 entry (its **one-time guard** paragraph, which reads "a same-day reload re-showed the summary. It now also reads the loaded day record...", a true statement about the one-day case that can be read as covering every reload), the website What's New block on `/home/jake/.openclaw/workspace/share/Flambeee/index.html`, and the commit messages between the v0.20.0 and v0.21.0 tags.
- **Suggested proof shape (Kai owns the final form).** A node harness that seeds `flambeee-cinder-day` with each case's record, extracts the shipped `computeAwayWindow()` and `shouldShowWelcomeBack()` into the sandbox (the Story 040/042 proof pattern), simulates the reset's write, and prints, per case, the first-load and second-load `shouldShow` values and the observed outcome. Plus a real-browser run (Scout) that seeds localStorage, loads, reloads, and reads the rendered DOM. Both are recorded for each case.
- **Existing state to read (do not change):** `checkDailyReset()` at `:656`; `computeAwayWindow()` at `:416` with the `gapDays = todayIdx - lastPlayIdx`, `daysAway = gapDays - 1`, `out.shouldShow = daysAway >= 1` derivation; `shouldShowWelcomeBack()` at `:509`; the `init()` load path at `:1300-1320`; `returnShown` at `:592`; `saveDayState()` / `loadDayState()`.
- **The honest limitation this story is adjacent to, and must not be confused with:** Story 042 recorded that literal multi-day suppression on a **different UTC day inside the same gap** cannot be achieved with zero persisted state, because the reset's write is what closes the window. Case B is the **same-day** reload of a record already stale by more than a day, which the reset's own write handles. Both facts belong in the corrected claim so the artifacts do not trade one overstatement for another.
- **Recording target:** the session's QA results file, as its own section with both cases side by side. Story 046 records the release-chain steps; this story records the proof.
- **What a PASS looks like:** both cases recorded with command, exit code, and auditable output; the panel shown once per gap and quiet on the reload in both; the claim in each artifact either citing the proof or corrected; no code change to `src/cinder.html`; `scripts/verify-website-currency.sh` untouched.
- **Peer review:** Kai and Riven review each other's work in the usual direction before merge, if any PR lands. A copy-only PR is small; it still gets the review.
- **Worktree rule (Session 24, fourth session running):** if Kai's proof produces a code change (Scenario 9), Kai and Riven work in separate git worktrees. A proof-only or copy-only outcome does not need a worktree.

## Visual Description (Quinn)

No visual change is promised by this story. The welcome-back panel keeps the styling and content Story 042 shipped: dark `#1a1a2e` panel, `2px solid #444` border, centered yellow `#ffcc00` `.header`, dashed `.divider`, the days-away and quests-missed sentences, the streak sentence, the today's-quest line, and the two `data-action` rows.

```
+------------------------------------------------+
|            === WELCOME BACK ===                |   <- unchanged (Story 042)
|   You were away for 3 days.                    |   <- unchanged
|   2 quests went uncompleted while you were     |   <- unchanged
|   gone.                                        |
|   Your streak survived.                        |   <- unchanged (Story 042 anchored this)
|   ------------------------------------------   |
|   Today's quest: Defeat 5 monsters             |   <- unchanged
|   ------------------------------------------   |
|   1. Back to Town                              |   <- unchanged
|   2. Go to today's quest                       |   <- unchanged
+------------------------------------------------+
```

- **The only visible behaviour this story touches is when the panel appears:** once per gap, and not on a same-day reload. That behaviour is already shipped; this story proves it and corrects the claim about it.
- **Unchanged:** every element of the panel, the town hub, and the rest of Cinder. If Scenario 9 applies and a fix lands, the fix is read-only presentation and is described in that fix's own PR, under requirement 3's constraints.

## Open questions

1. **Whether a code change is required at all.** Expected answer: no. Requirement 3 and Scenario 4 make "no code defect, claim corrected" a PASS. CEO input is needed only if the proof contradicts the expectation and a persisted field would be the only correct fix, in which case the Story 039 amendment path applies. This is the one genuine escalation branch.
2. **Scope of the claim correction (Riven/parent).** Recommendation: correct the release notes and the roadmap line (both published claims), and check the website What's New; if it does not repeat the guard claim, record that it was checked and needs no edit. If it does repeat it, correcting it triggers Story 046's run 2.
3. **Whether the v0.21.0 release notes can be edited at all (parent/CEO).** GitHub release notes for a published tag can be edited in place. Recommendation: edit the body to the narrower true statement and record the edit; do not delete and re-publish the release. If editing historical release notes is judged undesirable, the alternative is a correction note in the next release plus a roadmap fix, and that choice needs CEO input.
4. **Where the proof is recorded (Scout/parent).** Recommendation: the session's QA results file, one section, both cases side by side, per requirement 6.
5. **Session 23 worker-write-up risk (parent, not a dev question).** Write proof output to disk as work completes, poll output files every 60-120 seconds, and never fabricate a result.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 2 and the shipped code and published artifacts it names.
