# Story 082: Noon-job silent-failure alert (Session 37, P1, Mechanism)

**Status:** Ready for development (Session 37, 2026-10-21).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (mechanism; outward-facing first per parent call).
**Assigned to:** **Kai** backend owner (noon-job change plus simulated-failure proof). **Scout** witness and QA.
**Tracked by:** Session 37 plan, Story 082. Follows the Session 36 Bluesky gap finding (roadmap Current State, Session 36 entry).
**Depends on:** `scripts/flambeee-post-noon.py` (staged-only poster, exit non-zero on failure). No FPS dependency. No gamepad dependency.

## Summary

The noon poster must fail loudly on every failure mode, not just some of them. Session 36 found the gap: posted-posts.log shows no v0.32.0/v0.33.0 entries (last logged post v0.31.0, 2026-10-17) because the noon runs failed silently. This story adds the loud path: non-zero exit plus a durable log entry plus an alert artifact the next session can check. Zero user-visible change. No real post is sent by this story.

## jakebot decision (advisory only, recorded)

Session 37 Wave 1 set A-variant, per session 20261021_011108_21a235: noon-job hardening stories (failure alert plus version guard) as P1 plus standing currency as P2. B (advancing the FPS playable slice before the gamepad gate has run) waits on the gate. A is not close. P1 order per parent call: noon failure alert first (082, outward-facing), version guard second (083).

**Citation:** `flambeee-team/session-plan.md`, Session 37 (2026-10-21), section "jakebot decision (advisory only, recorded)", session 20261021_011108_21a235.

## Failure modes cited verbatim (in scope, all three)

1. **Oct 19 noon exit 127, missing venv interpreter.** The noon run exited 127 because the venv interpreter was missing. No post sent, no log entry written.
2. **Oct 18 no log entry.** The noon run produced no posted-posts.log entry at all. Nothing recorded, nothing alerted.
3. **7 straight creds-file failures (Oct 18-20).** Community-log newest entry 2026-10-20 14:05 CDT: Bluesky DM checks failing 7 consecutive runs on the missing credentials file (`~/.config/flambeee/.env` absent, whole dir gone). Venv exists with atproto, so the blocker is the missing creds file, not tooling. Last good check 2026-10-18 11:05 showed only known items, 0 unread DMs.

Root-cause note: creds restoration itself needs Jake (host file, not repo code). This story owns detection plus loud failure, not the file. The silent path is not fixed if the missing-creds mode is out of scope, so it is explicitly in scope here.

## Requirements

### 1. Loud failure on any failure mode

On any failure (missing venv interpreter as Oct 19, missing creds as Oct 18-20, API rejection, any other non-post path), the noon job must produce all three:

- Non-zero exit.
- A durable log entry recording date, failure mode, and exit code.
- An alert artifact at `flambeee-team/state/noon-failure-alert.log` (append one line per failure: ISO timestamp, mode, exit code) that the next session can check without re-running the job.

The existing success path (post plus verify plus archive to posted-posts.log plus clear pending) is unchanged.

### 2. Simulated-failure test matrix (no real post sent)

Tested by simulated failure runs, not by a real post. Minimum matrix, each run recorded with command, exit code, and artifact content:

- Missing interpreter (point the job at an absent venv path or equivalent).
- Missing creds file (creds path absent, as observed Oct 18-20).
- Empty or stale buffer (empty pending-post.txt; stale buffer per Story 083 is the guard story, here the requirement is only that the alert fires rather than silence).

Each simulated run must show non-zero exit plus the log entry plus the alert-artifact line. A code change with no simulated runs is not done.

### 3. Verifiable artifacts (per session plan constraint 1)

P1 must produce verifiable artifacts, not code alone: a live failure-alert test on the noon job. The proof is the simulated-run outputs (real exit codes, real artifact lines), pasted into the dev record. A real missed-run signal, not a stub.

### 4. No-new-post rule

This story sends no real post. The pending-post state at planning: quarantine file present (`state/pending-post.quarantine-2026-10-20-v0.32.0.txt`), no live buffer. Dev must not create a live buffer, must not post, and must leave the quarantine file untouched. The simulated runs use scratch copies, never the live pending path.

### 5. No FPS advancement

No FPS or playable-slice change in this diff. No gamepad run on this box.

## BDD scenarios

**Scenario 1: Missing interpreter fails loudly.**
Given the venv interpreter absent (Oct 19 mode), when the noon job runs, then exit is non-zero and the log entry plus the alert-artifact line record the mode and exit code.

**Scenario 2: Missing creds fails loudly.**
Given the creds file absent (Oct 18-20 mode, 7 straight failures), when the noon job runs, then exit is non-zero and the log entry plus the alert-artifact line record the mode and exit code.

**Scenario 3: API rejection fails loudly.**
Given the post API rejects the staged text, when the noon job runs, then exit is non-zero, no posted-posts.log success entry is written, and the log entry plus the alert-artifact line record the rejection.

**Scenario 4: Empty or stale buffer fails loudly.**
Given an empty or stale staged buffer, when the noon job runs, then no post is sent and the log entry plus the alert-artifact line record the mode.

**Scenario 5: Success path unchanged.**
Given a valid staged buffer with working interpreter, creds, and API, when the noon job runs, then it posts plus verifies plus archives to posted-posts.log plus clears pending, with exit 0 and no alert-artifact line.

**Scenario 6: Next session can check.**
Given a past failure, when the next session reads `flambeee-team/state/noon-failure-alert.log`, then it finds the ISO timestamp, mode, and exit code for each failure without re-running the job.

## Acceptance Criteria

**AC-1.** All three cited failure modes (exit 127 missing venv, Oct 18 no-log-entry, 7 straight creds-file failures) are in scope and each has a simulated run with command, exit code, and artifact content recorded (Scenarios 1, 2).
**AC-2.** API-rejection and empty/stale-buffer modes also fail loudly with all three signals (Scenarios 3, 4).
**AC-3.** Success path byte-equivalent to entering behavior: post plus verify plus archive plus clear, exit 0, no alert line (Scenario 5).
**AC-4.** Alert artifact at `flambeee-team/state/noon-failure-alert.log` holds one line per simulated failure (timestamp, mode, exit code), readable by the next session (Scenario 6).
**AC-5.** No real post sent: quarantine file untouched, no live buffer created, posted-posts.log gains no success entry from this story.
**AC-6.** Copy and log lines use plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Restoring the missing creds file (needs Jake, host file, not repo code).
- The version guard (Story 083 owns the stale-buffer refusal).
- Any website, game-file, or release change.
- Advancing the FPS playable slice before the gamepad gate has run.
- A gamepad run on this box. There is no pad here; see the note below.

## Notes (not stories, carried by this file)

1. **Headed gamepad gate: OPEN-BLOCKED-ON-HARDWARE.** Pointer to the Story 074 runnable gate verbatim (rig jake-dev-desk, headed mode, pass criteria, Kai runs plus Scout witnesses). Flip trigger: pad plus headed browsers available on the named rig. Carry-forward line: each subsequent session carries this note until it flips. Sixth session carrying.

## Open questions for dev wave

1. Exact log-entry format and location for the durable log (append to an existing state log or a new file; record the choice).
2. Simulated-run commands plus real exit codes plus artifact lines for the three required modes.
3. Confirmation that the quarantine file and posted-posts.log are untouched by the simulated runs.
