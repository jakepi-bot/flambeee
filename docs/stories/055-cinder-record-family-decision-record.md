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
| Day-record load normalization | 053 (this session, **pending merge**) | The record is normalized once on load; readers read the documented shape |

Story 053 is listed as **in-flight, not shipped**. Until its PR merges and Scout re-runs the proof
against the merged candidate in real Chromium, the load-normalization row is a claim under test. If
Story 053 lands no code change (its story explicitly allows a verified no-change outcome), this row
is corrected to say so before this record merges. A decision record that claims an unmerged story's
result is the exact defect class this family exists to prevent.

Kai confirms the code read matches; if a surface's proof does not exist or does not hold, the record
says so.

### 2. The one remaining candidate

State plainly:

- **Candidate:** welcome-back **suppression** across a later visit on a different UTC day inside the
  same gap (the Story 042 recorded limitation). Today the panel can fire again on a new UTC day
  inside one absence, because the "already shown" guard is in-memory (`returnShown`,
  `src/cinder.html:754`) and is not persisted.
- **Code read confirming the candidate is real (Quinn, verified against v0.24.0):** `returnShown` is
  declared `let returnShown = false; // Story 040: in-memory one-time guard for this page`
  (`src/cinder.html:754`), so it is re-initialized to `false` on every page load.
  `shouldShowWelcomeBack(windowState, shownThisPage, loadedRecord)` (`src/cinder.html:615`) returns
  `false` only when `shownThisPage` is already `true`. `init()` (`src/cinder.html:1472-1477`) passes
  the module-level `returnShown`, which it sets to `true` only after showing the panel. Therefore
  the guard suppresses a **second show within one page load**, and nothing at all across reloads.
  A player who closes the tab on the day they return, does not play, and opens it again two UTC
  days later sees the welcome-back panel fire a second time for the same absence. The gap is
  genuinely unclosed, not a stale note.
- **Why it is not in scope this session:** closing it for good requires a **persisted field** (a
  record of the last gap for which the panel was shown). A persisted field is a change to the stored
  day-record shape, which is a Story 039 decision-record amendment plus CEO sign-off.
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

**Scenario 2: the remaining candidate is named**
- Given the parent's Wave 1 read of the Story 042 limitation,
- When the record is written,
- Then the suppression candidate is named, its blocker (a persisted field) is stated, and the
  escalation condition (Story 039 amendment plus CEO sign-off) is attached.

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
- Kai's code read recorded in the file (which functions and lines back each claim).
- Vigil's confirmation that the record is truthful.

## Non-Goals (out of scope for this story)

- No code change of any kind.
- No Story 039 amendment (that is a CEO decision, not this story).
- No implementation story for the suppression candidate.
- No touching `jobs/`, `jobs-refactor-team/`, `jakebot/`, or any cron configuration.
