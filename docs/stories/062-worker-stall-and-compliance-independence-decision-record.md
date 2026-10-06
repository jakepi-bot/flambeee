# Story 062: Worker-stall pattern and compliance independence decision record (Session 29, P4, Docs Only)

**Status:** Decision record. **No code, no scripts, no hooks, no CI, no cron.**
**Author:** Quinn (Business Analyst), Wave 2. Reviewed by Vigil.
**Priority:** P4 (records two carried decisions; ships nothing).
**Assigned to:** **Quinn** (docs) / reviewed by **Vigil**.
**Tracked by:** Session 29 plan, Story 062. Records Session 28's recommendations 2 and 3, carried
unacted across sessions.

## Summary

Two structural observations have been recorded and not acted on, more than once each. This story
writes them down as decisions so they stop being re-recorded as new. It changes nothing that runs.

The two items:

1. **The worker-stall pattern.** A worker ends its turn on a progress statement with no artifact
   written.
2. **Compliance independence.** The actor that writes an artifact is the actor that reviews it.

Both are recorded. Any change to how the job is scheduled, or which model workers use, requires CEO
sign-off and is out of scope here.

## Part 1: The worker-stall pattern

### What it is

A worker turn that ends on a sentence such as "Writing the stories now" or "Writing the five story
files now," having written nothing to disk: no files, no branch, no PR. The turn reads as progress
to a reader of the transcript and as nothing to the filesystem.

### The count, measured

- Session 28: four workers lost, all the same shape. Quinn in Wave 2 (stories), Scout in Wave 3
  (verification), and Kai mid-phase at 15m32s leaving an uncommitted working tree.
- Across the three sessions before Session 29: five workers total, same shape.
- Session 29: this very task is a retry of a run that ended on "Writing the five story files now"
  and wrote nothing. It is the sixth instance, and it is the reason the brief says "write each file
  to disk as you finish it."

### What has been tried

- **Explicit brief language.** The Session 29 brief for this task states plainly: do not end a turn
  on a progress statement, write each file as you finish it, do not batch. This is the current
  mitigation.
- **Parent fallback.** When a worker returns without artifacts, the parent writes the artifact
  itself. Session 28's parent wrote all three stories this way. It works, and it is what makes the
  session ship, but it removes the worker the wave was scheduled for.
- **Detection by filesystem.** The detection method has not changed and still works: read the
  filesystem, not the worker's status line. A `status: ok` from a worker with no file on disk is a
  claim, not evidence.

### What is not known

The open question the Session 28 note names: **whether the subagent model or the brief format is
the variable.** Both have changed across the affected sessions and neither has been isolated. The
honest state is that the cause is unidentified; the detection and the parent fallback are what
actually protect the release.

### Decision

- The detection method stays: **read the filesystem, never the status line.**
- The parent fallback stays: if a wave's worker produces no artifact, the parent writes it and
  records that it did.
- **No change to scheduling and no change to worker model is made in this story.** Either requires
  CEO sign-off, both being changes to how the job runs.

## Part 2: Compliance independence

### What it is

The parent writes the artifacts it then reviews. Wave 2 (stories) and the review of those stories
run in the same actor. This is a structural blind spot, not a style preference: a reviewer cannot
independently catch an error in its own authorship with the same actor's judgment.

### The constraint, named

The parent is the only actor with the full context of the session: the plan, the prior rulings, the
open items. Isolating the writer from the reviewer costs that context, which is why the arrangement
persists.

### Decision

- Recorded as a known limitation of the current wave structure.
- An independent compliance read is desirable where one can be arranged (a worker other than the
  writer), and Session 29's success criteria already ask for it.
- **No structural change to the wave split is made here.** Changing it is a CEO decision.

## Requirements

- This document is merged to `main` with **zero** code changes.
- No script, no hook, no CI job, no cron entry, no model change is introduced.
- Vigil records a review of the two recorded items.

## Acceptance Criteria

- [ ] Merged with zero code changes: `git diff --stat` on the merge shows only this file plus the
      other Session 29 story files and `requirements-handoff.md`.
- [ ] Contains no script, hook, CI or cron content.
- [ ] Vigil has reviewed and recorded a response on the compliance-independence item.
- [ ] The two items are stated as carried-and-recorded, so they stop being raised as new.

## Non-Goals

- Any change to job scheduling, worker count, wave split or worker model. CEO sign-off required.
- Any automated stall detector. That is a tool change, out of scope.
- Re-litigating the wave structure. This story records it; it does not redesign it.

## Open questions (for the CEO, not resolved here)

1. Is the worker-stall cause the model or the brief format? Isolating it needs a controlled test the
   team has not run.
2. Is an independent compliance read required every session, or only when a writer-and-reviewer
   conflict is flagged?
