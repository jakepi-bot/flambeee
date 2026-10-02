# Story 055: Cinder Record Family, Decision Record and Next Candidate Surface (Session 27, P3, Decision Record)

**Status:** Ready (Session 27, 2026-10-02). Documentation only. No code.
**Author:** Quinn (Business Analyst), with Kai (Developer) providing the code read.
**Priority:** P3 (record-keeping; prevents the family from being re-litigated from scratch next session).
**Assigned to:** **Quinn** writes the record. **Kai** supplies the code read (which surfaces are covered by proofs). **Vigil** confirms the record is truthful and matches the shipped code.
**Tracked by:** Session 27 plan, Story 055.

## Summary

Sessions 20 through 27 produced seven corrective or verification stories against one defect class in
Cinder: **a locally-sourced statistic must be reconstructed from what the player actually recorded,
not from whatever the app rebuilt in memory, and two surfaces must never describe one span with
different numbers.** Each session corrected or verified one surface. Story 055 writes it down, so
the next session starts from the record instead of re-deriving the family.

This story adds **no code**. Its deliverable is a short decision record:

1. The list of Cinder record surfaces now covered by proofs, with the story that covered each.
2. The **one remaining candidate** surface the parent's Wave 1 read identifies, and the reason it is
   not in scope this session.
3. The decision **not to implement** that candidate this session, and what it would require.

## Business value

- Continuity. Six sessions have touched this family; without a single record, each new session
  re-derives which surfaces are safe and which are still open.
- It makes the boundary explicit: what is proven, what is deliberately deferred, and why. A future
  dev reading only the stories folder can see the whole family in one file.
- It records the escalation condition (a persisted field needs a Story 039 amendment plus CEO
  sign-off) at the point where the next candidate hits it, so nobody attempts it silently.

## User Story

As a future Flambeee session picking up Cinder,
I want one record of which record surfaces are covered by proofs and which one candidate remains,
So that I do not re-derive the family or silently implement a change that needs a Story 039
amendment and CEO sign-off.

## Requirements

### 1. Covered surfaces (the record)

The record lists each covered surface, the story that covered it, and the proof that backs it. At
minimum:

| Surface | Story | What is proven |
|---|---|---|
| Streak number on the quest log | 042, 044 | The number reads the recorded pre-reset record; a hole ends the run |
| Reload guard on the welcome-back panel | 045 | The panel does not re-fire on a same-day reload |
| Recent-quests list | 047 | The list reads the same anchor as the number |
| Quest-log day labels | 050 | Labels are record-relative, not today-relative |
| Away-window day count | 051 | `daysAway = gapDays - 1`, the count of fully missed UTC days; verification only, no code change |
| Day-record load normalization | 053 (this session, **shipped in v0.25.0**) | The record is normalized once on load; readers read the documented shape |

One honest caveat on the Story 045 row: it proved the **same-day** reload case, and its own
disclosure says so. The cross-day case is the open candidate below. Do not read that row as "the
guard is proven for every reload".

Story 053 **shipped in v0.25.0**. Its PRs #110 (helper + proof) and #111 (call site) merged to
`main`; the merged candidate sha256 is `eb0123587d502ee2efde6786075298c618ff5c156f201a8e78144baf6c1c032b`;
Kai's pure-function proof re-ran green (22 checks, exit 0) against the merged candidate and exit 1
against tagged v0.24.0; and Scout re-ran the proof in real Chromium (32 checks, 0 failed). The
load-normalization row is therefore shipped, not a claim under test. This correction was applied at
release time, per the QA handoff, so the record does not claim an unmerged story's result, which is
the exact defect class this family exists to prevent.

Kai confirms the code read matches; if a surface's proof does not exist or does not hold, the record
says so.

### 2. The one remaining candidate

State plainly:

- **Candidate:** welcome-back **suppression** across a later visit on a different UTC day inside the
  same gap (the Story 042 recorded limitation). Today the panel can fire again on a new UTC day
  inside one absence, because the "already shown" guard is in-memory (`returnShown`,
  `src/cinder.html:759`) and is not persisted.
- **Code read confirming the candidate is real (Quinn, verified against v0.24.0):** `returnShown` is
  declared `let returnShown = false; // Story 040: in-memory one-time guard for this page`
  (`src/cinder.html:759`), so it is re-initialized to `false` on every page load.
  `shouldShowWelcomeBack(windowState, shownThisPage, loadedRecord)` (`src/cinder.html:615`)
  returns `false` only when `shownThisPage` is already `true`. `init()`
  (`src/cinder.html:1472-1477`) passes the module-level `returnShown`, which it sets to `true` only
  after showing the panel. Therefore the guard suppresses a **second show within one page load**,
  and nothing at all across reloads.
- **Reproduced by execution, not just read (Quinn, Wave 2).** Seeded a record last played on day
  100 with one completion on day 100, then drove the shipped `computeAwayWindow()` and
  `shouldShowWelcomeBack()` logic:
  - visit on day 102: `shouldShow` **true**, `daysAway` 1 (the load path's own reset write then
    stamps day 102 into the record),
  - reload the same day 102: `shouldShow` **false**, which is exactly the same-day case Story 045
    proved,
  - visit on day 104, same absence: `shouldShow` **true** again, `daysAway` 1.

  So the panel re-fires **once per new UTC day inside the same absence**. The gap is genuinely
  unclosed, not a stale note, and the frequency is worse than "occasionally": a player who opens
  Cinder on three days inside one long absence sees the return summary three times. That frequency is
  a product judgement about how often an interruption is acceptable, which is precisely why it
  belongs to the CEO rather than to a dev session.
- **Why it is not in scope this session:** closing it for good requires a **persisted field** (a
  record of the last gap for which the panel was shown). A persisted field is a change to the stored
  day-record shape, which is a Story 039 decision-record amendment plus CEO sign-off.
- **Note that Story 053 does not and cannot close this.** Story 053 normalizes the day record's
  **shape**; it adds no field and touches no suppression behavior. Do not let a merged 053 be read
  as having settled the suppression question.
- **Escalation condition:** if a future session wants it, the first step is the Story 039 amendment
  and CEO sign-off, not a code change.

### 3. The decision

- **Decision:** do not implement the candidate this session. Record it as the single open item in
  the family, with the escalation condition attached.
- **Valid alternative outcome:** if Kai's code read finds that no surface remains open (for example
  if the suppression limitation has since been closed or made unreachable), the record states that
  and closes the family explicitly. Either outcome is acceptable; the record must be true, not
  convenient.

### 4. No code, no scope creep

- No code change. No story is created to implement the candidate.
- No change to `checkDailyReset()`, the reset, the stored shape, or the Story 039 decision record.
- The record is documentation only.

## Acceptance Criteria (Given/When/Then)

**Scenario 1: covered surfaces recorded**
- Given the family of stories 042-053,
- When the record is written,
- Then each covered surface is listed with its story and its proof, and Kai's code read confirms the
  list.

**Scenario 2: the remaining candidate is named, with its blocker**
- Given the Wave 1 read of the Story 042 limitation, confirmed in Wave 2 by execution,
- When the record is written,
- Then the suppression candidate is named, its blocker (a persisted field) is stated, and the
  escalation condition (Story 039 amendment plus CEO sign-off) is attached.

**Scenario 2b: the candidate is reproduced, not asserted**
- Given a record last played on day 100 with one completion on day 100,
- When the shipped `computeAwayWindow()` and `shouldShowWelcomeBack()` logic are driven for a visit
  on day 102, a reload on day 102, and a visit on day 104,
- Then the first visit shows the panel, the same-day reload is quiet (the Story 045 case), and the
  day-104 visit shows the panel again, so the record states the candidate is open on reproduced
- behavior rather than on an inherited note

**Scenario 3: the decision is explicit**
- Given the candidate cannot be implemented without a persisted field,
- When the record is written,
- Then it records the decision not to implement this session, and does not create an implementation
  story.

**Scenario 4: truthful**
- Given the merged record,
- When Vigil reviews it,
- Then every claim about the code matches the shipped code, and no closed surface is claimed open or
  vice versa.

## Required Proof

- The decision-record file itself, committed to `docs/`.
- **The reproduction (Quinn, done in Wave 2):** the three-visit trace recorded in requirement 2,
  produced by driving the shipped helper logic with a seeded record. The numbers in the record are
  the outputs that trace produced, so Kai can re-run them independently.
- Kai's code read recorded in the file (which functions and lines back each claim). Every line
  reference in this record was re-verified against tagged v0.24.0 in Wave 2; one was corrected from
  `:754` to `:759` after the check (`:754` is `location`, not `returnShown`).
- Vigil's confirmation that the record is truthful.

## Non-Goals (out of scope for this story)

- No code change of any kind.
- No Story 039 amendment (that is a CEO decision, not this story).
- No implementation story for the suppression candidate.
- No change to `returnShown`, `shouldShowWelcomeBack()`, or `init()`.
- No touching `jobs/`, `jobs-refactor-team/`, `jakebot/`, or any cron configuration.

## Open questions for the CEO (routed from this record, not invented here)

1. **Should the welcome-back panel be suppressed for the whole absence, or once per UTC day
   inside it?** The current behavior is once per UTC day inside the absence, reproduced above. The
   three options are: keep it (no cost, but a returning player sees the same summary repeatedly and
   it stops feeling like a welcome), suppress for the whole gap (needs a persisted field, so a Story
   039 amendment plus CEO sign-off), or suppress only when the player has played since (no persisted
   field, but it changes what the panel means). This is a product decision, not a technical one, and
   the story does not pick one.
