# Story 051: Cinder Welcome-Back Day Count, Resolved Definition and Verification (Session 26, P2)

**Status:** Ready for verification and decision (Session 26, 2026-09-29). **Decision record plus a verification story.** The story plan's "corrective" shape is not implemented as a code change: reading the code against the Story 039 decision record and the Story 040 acceptance criteria shows the current arithmetic is **correct per the authoritative record**, with one cross-surface presentation disagreement that is a **CEO decision**, not a dev fix. No code change is authorised by this story unless the CEO rules otherwise (see "CEO decision required").
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P2 (truthfulness across surfaces and a permanent decision record; the working behaviour itself is not a defect).
**Assigned to:** **Kai** owns the verification proof (`src/kai-story051-away-window-proof.py`) and the frozen-function extraction; no helper change is expected. **Riven** owns any copy or label change **only if** the CEO rules the cross-surface numbers must match by a code change; the default outcome needs no Riven code. **Scout** re-runs the proof on the merged candidate. **Vigil** verifies that this story does not change working behaviour, that the recorded decision matches the code, and that no claim is made the proof does not support. **Quinn** owns the decision text below and the handoff.
**Tracked by:** Session 26 plan, Story 051. Grounded in Story 039 (the away-time decision record: D3 defines the welcome-back summary, "days away" among its facts), Story 040 (the summary's acceptance criteria: "the last recorded play day is two UTC days ago (one whole day fully missed)", and the days-away sentence), Story 042 (the streak line and the once-per-gap guard), Story 045 (the verification-shaped proof pattern and the corrected-claim pattern), Story 050 (the quest-log labels, the other surface for the same span), and the roadmap's recorded Story 042 limitation about multi-day suppression.

## Summary

The session plan flagged `computeAwayWindow()` (`src/cinder.html:522-588`) as a suspected off-by-one: `const daysAway = gapDays - 1` (`src/cinder.html:555`) means a player back after two calendar days (`gapDays = 2`) sees `"You were away for a day."` while `questsMissed` is 1 and the quest-log label reads `2 days ago` (after Story 050, that label becomes relative to the record anchor). The plan asked Quinn to resolve the definition of "days away" against the Story 039 decision record before shaping the story.

**Quinn's resolution.** The arithmetic is **correct**, and it is load-bearing. It implements the definition the authoritative records fix:

- **Story 039, D3:** days away is "how many UTC days have passed since the player last played", inside a summary that fires "when a player returns after at least one **fully missed** day".
- **Story 040, requirement 4 and Scenario 1:** the days-away fact is phrased as the missed-day gap, with the explicit worked example "the last recorded play day is two UTC days ago (**one whole day fully missed**)" rendering as the one-day phrasing ("You were away for a day.").
- **Story 040, Scenario 5 / the Session 22 QA (`session22-story040-qa.py:324`):** a record stamped `TODAY - 2` asserts `"You were away for 2 days."` only in the multi-missed-day case; the one-missed-day case asserts the one-day phrasing.

So the definition the record fixes is: **`daysAway` = the number of fully missed UTC days in the gap = `gapDays - 1`.** The gap is exclusive at both ends by design (`computeAwayWindow()` comment at `src/cinder.html:561-563`: "Today is in progress, not missed, so the window is exclusive at both ends"), and the `questsMissed` loop (`src/cinder.html:565-568`) walks `lastPlayIdx + 1` to `todayIdx - 1`, which is the same `gapDays - 1` days. The two numbers therefore agree by construction, and the invariant `questsMissed <= daysAway` (Story 040, the Session 22 QA) holds.

**Therefore this story changes no behaviour.** The correct outcome is the one the plan already allows: "if Quinn concludes the current arithmetic is in fact correct against the Story 039 decision record, that is a valid outcome". It ships as a verification story with the decision recorded (below), a proof that the boundary cases behave as documented, and **no code change**. Changing `daysAway` to `gapDays` would make the panel contradict its own `questsMissed` count and would reverse a decision the CEO's delegated record already fixed; per `AGENTS.md`, "when a fix would sacrifice a valued property, it's ruled out - not traded off."

**One genuine open item, escalated not fixed (see "CEO decision required").** The quest-log label after Story 050 will read the newest entry relative to the record anchor, so for the `gapDays = 2` span the label's difference will be 0 (the anchor day itself) while the panel says "away for a day". These are two different, each-correct measures of one span: the label names the day of the last play relative to the record; the panel names how many days were missed. The plan asks that "two surfaces must not describe one gap with different numbers". Whether that requires a code change or is a documentation matter is a product-judgment call about which value a player should see, and it is not decided by the Story 039 record. It is recorded in "CEO decision required" and in the handoff as an open question. **No code change is made under this story while it is open.**

## Business value

- Closes the off-by-one suspicion permanently: the decision is recorded with its evidence, so the next session does not re-litigate it. That is the whole point of writing the resolution into the story file.
- Protects a working behaviour. The panel's numbers are consistent with each other and with the record; a "fix" driven by the story title alone would have broken that.
- Identifies the one real cross-surface question and routes it to the CEO rather than guessing a product answer.
- Costs nothing to implement in code: the deliverable is the proof and the record.

## Resolved definition (record, do not re-litigate)

**Definition of "days away" (Story 051, resolved against Story 039 D3 and Story 040 requirements 1 and 4):**

`daysAway` is the count of **fully missed UTC days** in the gap between the last recorded play day and today, exclusive at both ends. With `gapDays = todayIdx - lastPlayIdx`:

```
daysAway = gapDays - 1     (clamped at 0)
```

- `gapDays` 0 (same-day) and 1 (next-day, nothing fully missed): the panel stays quiet, and `daysAway` is 0. This is the control, and behaviour must not change.
- `gapDays` 2: exactly one fully missed day (`T-1`). Panel fires, reads `"You were away for a day."`, `questsMissed` is 1. Both numbers agree.
- `gapDays` n (n >= 2): `daysAway = n - 1`, `questsMissed <= n - 1`, and the long-absence phrasing (`daysAway >= 14`) is unchanged.

**This is the definition fixed by Story 039/040. Story 051 reaffirms it and does not change it.**

### Distinguish the two values (so the next session does not confuse them)

| Value | Meaning | Where it is used | Correct expression |
|---|---|---|---|
| Days elapsed between play sessions | `todayIdx - lastPlayIdx` (`gapDays`) | Not displayed as "days away"; it is the raw gap | `gapDays` |
| Days away / fully missed days | The count of complete days with no play | `daysAway`, the days-away sentence, and `questsMissed`'s upper bound | `gapDays - 1` |

The quest-log label after Story 050 is a **third** thing: it names a recorded day relative to the record's anchor, not a count of missed days. Story 050 owns the label's reference point; this story owns the panel's count.

## CEO decision required

**Question:** For one gap of two or more calendar days, should the welcome-back panel's "days away" number and the quest-log label for the same span be made to name the same number, and if so, which definition wins?

**The disagreement, worked example.** Last played Monday (index `D`), returns Wednesday (`D+2`), so Tuesday is fully missed.

- The panel: `"You were away for a day."` and `"1 quest went uncompleted while you were gone."` (`gapDays = 2 -> daysAway = 1`, `questsMissed = 1`).
- The quest-log list, after Story 050: the newest entry is the anchor day itself and reads `today`; any entry for `D-1` reads `yesterday`; and so on. The list does not print the string "2 days ago" for this span, because after Story 050 no entry in this record has a difference greater than 1 from the anchor.

So there is no literal "1" versus "2" on one screen after Story 050. The remaining question is whether a player, reading "away for a day" beside a list whose newest entry is labelled `today`, is being told two different stories. Quinn's read is that they are two correct measures (missed-day count versus record-relative day), not a contradiction, and that no code change is warranted. **This is a product-judgment call and it goes to the CEO, per the authority gate.** It is not decidable by the Story 039 record, which fixes only the missed-day count.

**Options for the CEO:**

1. **Leave as is (dev recommendation).** The panel counts missed days; the log labels are record-relative. They are different measures and each is correct. Story 051 closes as a verification story, no code change. The decision is recorded here.
2. **Unify on the missed-day count everywhere a number is shown.** Requires Story 050 and Story 051 to coordinate: the label for the anchor entry would need to express "1 day missed" rather than `today`. This is a real copy change and a real code change in `renderQuestLog()`, and it collides with Story 050's ownership. It needs the CEO to say so before either dev starts.
3. **Unify on the elapsed gap (`gapDays`).** Change `daysAway = gapDays - 1` to `daysAway = gapDays`, which makes `daysAway = 2` for this span. This **contradicts** `questsMissed` (1) and the Story 039/040 records, and reverses an approved decision. Ruled out unless the CEO explicitly reopens Story 039.

If the CEO does not answer in this session, option 1 stands (no code change) and the question is carried in the handoff.

## Requirements

### 1. Record the resolved definition

- This story file states the definition of "days away" (`gapDays - 1`, the count of fully missed UTC days), the two values it must not be confused with, and the authority it comes from (Story 039 D3; Story 040 requirements 1 and 4; the Session 22 QA). It is the written record so the next session does not re-litigate it.

### 2. Verify the boundary cases behave as documented, with no code change

- A proof script covers `gapDays` **0, 1, 2, 3, 7, 14 and 30**, asserting for each: the `daysAway` value, the `questsMissed` count, the `shouldShow` flag, and the rendered sentence.
- The proof asserts the invariant `questsMissed <= daysAway` holds across the sweep.
- The proof asserts the control cases (`gapDays` 0 and 1) stay quiet.

### 3. No behaviour change

- `computeAwayWindow()` is **not modified**. `daysAway = gapDays - 1` stands.
- The same-day (`gapDays` 0) and next-day (`gapDays` 1) quiet cases are the control and do not change. Story 042's limitation note stays true.
- The long-absence phrasing (`awayDaysSentence()`, `src/cinder.html:590-594`) is unchanged.

### 4. Frozen functions stay byte-identical to v0.23.0

The following are frozen for this story and proven by extraction:

- `shouldShowWelcomeBack()` (`src/cinder.html:615-624`)
- `checkDailyReset()` (`src/cinder.html:762-773`)

They must be byte-identical to their v0.23.0 shipped text. `computeAwayWindow()` is also unchanged (requirement 3), so it is byte-identical as well; it is a "no change" rather than a "frozen against a change", and the proof states which.

### 5. Copy stays in the CEO tone

- No copy change is expected. If any copy change is made under a CEO ruling, it uses plain punctuation, no em dashes, no emoji.

### 6. Cross-surface question routed to the CEO

- The panel-versus-log question in "CEO decision required" is recorded and routed. No code change is made under this story while it is open.

### 7. Graceful degradation (unchanged, verified)

- Corrupt or missing history, a non-object record, an unreadable day index, private mode, and unavailable storage all continue to degrade to "show nothing" rather than throw, exactly as v0.23.0. The proof covers these.

## Out of scope

- Any change to `computeAwayWindow()`'s arithmetic. It is reaffirmed, not changed.
- Any change to the days-away sentence (`awayDaysSentence()`), the quests-missed sentence (`awayQuestsSentence()`), or the streak sentence (`awayStreakSentence()`).
- Any change to the Story 042/044 once-per-gap guard or `shouldShowWelcomeBack()`.
- Any change to `checkDailyReset()`.
- Any change to the quest-log labels. That is Story 050, and this story must not touch it.
- Multi-day welcome-back suppression (a later visit on a different UTC day inside the same gap). It remains blocked on a Story 039 amendment plus CEO sign-off, as the roadmap records for Story 042.
- Any offline resource accrual, boss-day balance change, or cross-day streak mechanic. All remain blocked on the Story 039 amendment plus CEO sign-off.
- Any new persisted field, any change to the stored day record shape, and any write on the summary path.
- Any balance, reward, rotation, payout, monster-pool, or level-curve change.
- Any notification, push, email, permission prompt, or install nag.
- Any new town-hub row, banner, tooltip, or notification dot.
- Any new game, leaderboard, multiplayer, or community-submitted game.
- Any change to `scripts/verify-website-currency.sh` (Story 052 owns the checker runs) or to the website.
- Any cron configuration, and any file under `jobs/`, `jobs-refactor-team/`, or `jakebot/`.

## Acceptance Criteria (BDD)

### Scenario 1: The definition is recorded and unambiguous (P2, Quinn + Vigil)
- **Given** this story file
- **When** I read the "Resolved definition" section
- **Then** it states that `daysAway = gapDays - 1` is the count of fully missed UTC days, names its authority (Story 039 D3; Story 040 requirements 1 and 4; the Session 22 QA), and distinguishes it from `gapDays` and from the quest-log label

### Scenario 2: A two-day gap shows the one-missed-day panel consistently (P2, Kai + Scout)
- **Given** a record whose last recorded play day is 2 UTC days before today (one fully missed day)
- **When** the welcome-back panel renders
- **Then** it reads `"You were away for a day."` and `"1 quest went uncompleted while you were gone."`, `daysAway` is 1, `questsMissed` is 1, and `questsMissed <= daysAway` holds

### Scenario 3: Same-day and next-day returns stay quiet (P2, Kai + Scout, control)
- **Given** `gapDays` 0 (same-day reload) and `gapDays` 1 (next-day return, nothing fully missed)
- **When** the game loads
- **Then** the panel stays quiet exactly as in v0.23.0, and `daysAway` is 0 in both cases

### Scenario 4: The boundary sweep is correct for every documented gap (P2, Kai, proof)
- **Given** the proof script `src/kai-story051-away-window-proof.py`
- **When** it sweeps `gapDays` 0, 1, 2, 3, 7, 14 and 30
- **Then** for each it asserts the `daysAway` value (`gapDays - 1` clamped at 0), the `questsMissed` count, the `shouldShow` flag, and the exact sentence, and the invariant `questsMissed <= daysAway` holds

### Scenario 5: The long-absence phrasing is unchanged (P2, Kai + Vigil)
- **Given** `daysAway >= 14`
- **When** the panel renders
- **Then** the copy is the existing form (`"You were away for a while."`), unchanged from v0.23.0, with plain punctuation and no emoji

### Scenario 6: No code change was made (P2, Kai + Vigil, this story's core assertion)
- **Given** the diff for this story in `src/cinder.html`
- **When** it is inspected
- **Then** `computeAwayWindow()`, `shouldShowWelcomeBack()` and `checkDailyReset()` are byte-identical to v0.23.0, and no other line changed for this story

### Scenario 7: The frozen functions are byte-identical to v0.23.0 (P2, Kai, proof)
- **Given** the extraction of `shouldShowWelcomeBack()` and `checkDailyReset()`
- **When** they are compared to v0.23.0
- **Then** they are textually identical

### Scenario 8: The summary path writes nothing and adds no field (P2, Kai, proof)
- **Given** any state that renders the welcome-back panel
- **When** the panel renders
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical across the render, and no new field name appears anywhere in the (empty) diff

### Scenario 9: Corrupt and partial records degrade cleanly (P2, Kai + Scout, regression)
- **Given** a legacy record with no history, a corrupt record (`completedQuests` a string, an entry with a non-numeric `dayIndex`), a `null` record, and storage unavailable
- **When** the game loads
- **Then** the panel shows nothing rather than throwing, exactly as v0.23.0, and the town hub renders normally

### Scenario 10: The cross-surface question is routed, not silently resolved (P2, Quinn + Vigil)
- **Given** the panel's days-away value and the quest-log label for the same span
- **When** the session closes
- **Then** the question is recorded in "CEO decision required" and in `requirements-handoff.md`, no code change was made to force agreement, and the default (no change) is stated as what stands until the CEO rules

### Scenario 11: Story 050 and Story 051 do not collide (P2, Kai + Riven + parent)
- **Given** both stories touch Cinder's display of one gap
- **When** the work is reviewed
- **Then** Story 050 changed only the quest-log label's reference point, Story 051 changed no code, `computeAwayWindow()` is untouched by both, and the ownership lines are disjoint

### Scenario 12: Tone and no-AI-tells (P2, Vigil)
- **Given** any new or changed user-visible copy, and the decision text
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and matches the plain-punctuation, dry-humour Cinder and CEO voice

## Wireframe / visual description

Welcome-back panel, `gapDays = 2` (last played Monday, returns Wednesday, Tuesday fully missed), unchanged from v0.23.0 and confirmed correct by this story:

```
=== WELCOME BACK ===
You were away for a day.
1 quest went uncompleted while you were gone.
Your streak is broken.
-----------------
Today's quest: Slay the cave bat
-----------------
1. Back to Town
2. Go to today's quest
```

The one-day phrasing is the intended output for one fully missed day (Story 040, Scenario 1). This story verifies it and records the definition; it does not change the panel.

## Proof / evidence required

1. **Pure-function proof (Kai):** `src/kai-story051-away-window-proof.py`, extracting `computeAwayWindow()`, `awayDaysSentence()`, `awayQuestsSentence()` and `awayStreakSentence()` from the shipped file, sweeping `gapDays` 0, 1, 2, 3, 7, 14 and 30, asserting `daysAway`, `questsMissed`, `shouldShow`, the sentence, and `questsMissed <= daysAway`. Expected exit code 0. Against shipped v0.23.0 it passes (there is no defect), and the proof **states** that it passes against v0.23.0 because no code change is intended.
2. **Frozen-function extraction (Kai):** `shouldShowWelcomeBack()` and `checkDailyReset()` byte-identical to v0.23.0, plus `computeAwayWindow()` shown unchanged.
3. **No-write / no-new-field proof (Kai):** both localStorage keys byte-identical across the summary path; static scan clean.
4. **Real-browser check (Scout):** the panel rendered in real Chromium at desktop and 375x667 on a seeded `gapDays = 2` record and a `gapDays = 0` control, on the merged candidate (which, per Story 050, is the label-changed build); the panel output matches this story's recorded expectation.
5. **The decision record:** this story file, verified by Vigil against the code and the Story 039/040 text.

## Open questions / ambiguities (need CEO input)

1. **Cross-surface numbers (the CEO decision required section).** Leave as is, unify on missed days, or unify on the elapsed gap. Recommendation: leave as is. Default if no ruling: no code change, question carried.
2. **None blocking.** The definition of days away itself is resolved and recorded and needs no CEO input; only the cross-surface presentation question does.
