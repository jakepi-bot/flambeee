# Story 085: Noon pre-start launcher (Session 38, P1, Mechanism)

**Status:** Ready for development (Session 38, 2026-10-22).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (mechanism; session ship first per parent call).
**Assigned to:** **Kai** backend owner (RED case plus launcher plus roadmap correction). **Scout** witness and QA.
**Tracked by:** Session 38 plan, Story 085. Follows Story 082 plus the Session 36 Bluesky gap finding.
**Depends on:** `scripts/flambeee-post-noon.py` live poster plus `scripts/test-noon-failure-alert.sh` (Session 37 matrix). No FPS dependency. No gamepad dependency.

## Summary

Close the pre-start hole the Oct 19 failure exposed. Story 082 hardened every failure mode inside the poster, but the Oct 19 exit 127 happened before the poster ever ran, so the 082 matrix never covered it. This story ships the scheduled entry as repo code: `scripts/run-noon-post.sh`, a launcher that resolves the interpreter, traps every pre-start failure, appends one `mode=launcher-<cause>` line to the same alert log, and exits non-zero. Zero user-visible change. No real post is sent by this story. Installing the launcher into the scheduler is Jake's job, one line, and is not a story step.

## jakebot decision (advisory only, recorded)

Session 38 Wave 1 priorities per session 20261022_011059_0b55b4: P1 close pre-start detection test first, roadmap correction as part of P1, P2 poster mirror plus pin, P3 standing currency run 1 only. No FPS playable advancement. No release implied.

**Citation:** `flambeee-team/session-plan.md`, Session 38 (2026-10-22), section "jakebot decision (advisory only, recorded)", session 20261022_011059_0b55b4.

## Failure mode cited verbatim (the hole)

1. **Oct 19 noon exit 127, missing venv interpreter.** The noon run exited 127 because the venv interpreter was missing. No post sent, no log entry written.
2. **Pre-start scope note.** The Oct 19 exit-127 (missing venv interpreter) happened OUTSIDE the poster, so 082's matrix never covered it. The 082 simulated missing-interpreter case runs the poster file with a bad venv path override, which proves the in-poster path only. A missing or unexecutable interpreter on the scheduled command line itself never reaches the poster, so nothing appends to the alert log today.

## Session 37 roadmap overclaim (corrected by this story)

The Session 37 roadmap entry for Story 082 claims the poster now alerts "on every failure mode (missing interpreter, missing creds, empty/stale/over-length buffer, API rejection)". That line overclaims: it covers the missing-interpreter mode only once the poster is already running. The pre-start mode (scheduled command invokes a nonexistent interpreter, exit 127, zero alert output) is not covered until this story lands. Dev corrects that line next to the new Session 38 entry; the overclaim does not stand. Record the exact before and after wording in the dev record.

## Requirements

### 1. RED failing case first (the hole proven real)

Before the launcher exists, dev records one failing run as the artifact: invoke the noon path through a nonexistent interpreter (for example `/nonexistent/python3 scripts/flambeee-post-noon.py` or the scheduled command with a bad interpreter path) and assert two things: non-zero exit AND one alert-log line. It fails today (exit 127, no alert line), and that failing run with command, exit code, and alert-log contents pasted into the dev record is the proof the hole is real. Code with no RED run is not done.

### 2. Launcher contract (`scripts/run-noon-post.sh`, in repo)

New file `scripts/run-noon-post.sh` is the scheduled entry. Contract:

- **Interpreter resolution.** Resolve the python3 interpreter at run time (explicit path or `command -v` lookup, record the rule). If resolution fails, go to the trap path, do not attempt the poster.
- **Pre-start trap.** Every failure before the poster starts (interpreter missing or not executable, poster file missing, required env scaffold missing) is trapped by the launcher itself.
- **Alert-log line.** On any pre-start failure, append one line to the same alert log Story 082 owns (`flambeee-team/state/noon-failure-alert.log` in production; scratch alert log in tests) in the form `mode=launcher-<cause>` plus exit code plus ISO timestamp. Cause is a short token (for example `no-interpreter`, `not-executable`, `no-poster`). Record the exact format in the dev record.
- **Non-zero exit.** The launcher exits non-zero on every pre-start failure. When the poster does start, the launcher passes through the poster exit code unchanged and adds no extra alert line of its own.
- **Poster path unchanged.** The launcher calls the poster, it does not duplicate poster logic. In-poster modes stay owned by the 082 path.

### 3. Verification runs (no real post sent)

Minimum proof, each run recorded with command, exit code, and alert-log contents:

- RED run (pre-launcher, nonexistent interpreter): exit non-zero, zero alert lines (fails as predicted).
- Launcher with nonexistent interpreter: exit non-zero AND one `mode=launcher-<cause>` line.
- Launcher with non-executable interpreter: exit non-zero AND one `mode=launcher-<cause>` line.
- Launcher happy path in dry-run or simulated mode: poster reached, exit code passed through, no launcher alert line.

All runs use scratch copies and scratch alert logs, never the live pending path. No schedule edit. No real post sent. Quarantine file and posted-posts.log untouched; record both sha256 before and after as Story 082 did.

### 4. Jake-owns-scheduler-install boundary

Authoring and testing the launcher is repo code and is in scope. Editing cron or any schedule is out permanently and stays deferred to the schedule owner, Jake. The story delivers the tested launcher plus the one install line documented in the dev record (the command the scheduler should run). Dev and QA never touch the schedule. Installing it is Jake's one line.

### 5. No-new-post rule

This story sends no real post. Dev must not create a live buffer, must not post, and must leave the quarantine file untouched. Simulated runs use scratch copies, never the live pending path.

### 6. No FPS advancement

No FPS or playable-slice change in this diff. No gamepad run on this box.

## BDD scenarios

**Scenario 1: RED case proves the hole.**
Given a scheduled command pointing at a nonexistent interpreter, when the noon path is invoked without the launcher, then exit is non-zero (127 class) and zero alert-log lines are written. This failing run is recorded as the artifact.

**Scenario 2: Launcher traps a missing interpreter.**
Given a nonexistent interpreter path, when `scripts/run-noon-post.sh` runs, then exit is non-zero and one `mode=launcher-<cause>` line with exit code is appended to the alert log.

**Scenario 3: Launcher traps a non-executable interpreter.**
Given an interpreter path that exists but is not executable, when the launcher runs, then exit is non-zero and one `mode=launcher-<cause>` line records the cause.

**Scenario 4: Launcher passes through the poster result.**
Given a working interpreter and poster in dry-run or simulated mode, when the launcher runs, then the poster executes, the launcher exits with the poster exit code, and no launcher alert line is written.

**Scenario 5: Roadmap overclaim corrected.**
Given the Session 37 roadmap line claiming 082 covers the missing-interpreter mode, when this story lands, then the roadmap carries the corrected line next to the Session 38 entry with before and after wording recorded, and the overclaim no longer stands.

**Scenario 6: Schedule untouched.**
Given the launcher merged, when the session ends, then no cron or schedule file has been edited by agents, and the dev record holds the one install line for Jake.

## Acceptance Criteria

**AC-1.** RED run recorded with command, exit code, and alert-log contents showing non-zero exit and zero alert lines (Scenario 1).
**AC-2.** Launcher at `scripts/run-noon-post.sh` resolves the interpreter, traps pre-start failures, appends one `mode=launcher-<cause>` line with exit code, and exits non-zero; pass-through on the happy path (Scenarios 2, 3, 4).
**AC-3.** All verification runs pasted into the dev record with real exit codes and real alert lines; scratch paths only (Scenarios 2, 3, 4).
**AC-4.** Session 37 roadmap overclaim corrected next to the Session 38 entry with before and after wording recorded (Scenario 5).
**AC-5.** No schedule edit, no real post, quarantine and posted-posts.log sha256 identical before and after (Scenarios 5, 6 plus section 5).
**AC-6.** Copy and log lines use plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Installing the launcher into the scheduler (Jake's one line; agents document it, never run it).
- Restoring the missing creds file (Jake's host file; the launcher detects loudly, same as 082).
- Re-hardening in-poster modes (Story 082 owns them; this story only adds the pre-start layer).
- Any website, game-file, or release change.
- Advancing the FPS playable slice before the gamepad gate has run.
- A gamepad run on this box. There is no pad here; see the note below.

## Notes (not stories)

1. **Headed gamepad gate: DEFERRED-UNTIL-PAD-EXISTS on rig jake-dev-desk.** Runnable gate verbatim lives in Story 074 in this dir. Returns only when a pad exists. Per Session 38 plan this line is not carried forward session to session.

## Open questions for dev wave

1. Interpreter resolution rule (explicit path vs lookup order; record the exact rule).
2. Exact alert-line format for `mode=launcher-<cause>` (field order; record one sample line).
3. Before and after wording of the roadmap correction plus quarantine and posted-posts.log sha256 pairs.
