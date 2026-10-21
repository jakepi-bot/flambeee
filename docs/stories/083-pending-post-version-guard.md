# Story 083: Pending-post version guard (Session 37, P1, Mechanism)

**Status:** Ready for development (Session 37, 2026-10-21).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (mechanism; second per parent call).
**Assigned to:** **Kai** backend owner (guard change plus verification proof). **Scout** witness and QA.
**Tracked by:** Session 37 plan, Story 083. Follows the Session 36 stale-buffer containment (roadmap Current State, Session 36 entry).
**Depends on:** `scripts/flambeee-post-noon.py` (staged-only poster). Story 082 (failure alert; the guard refusal must also fail loudly through the 082 path). No FPS dependency. No gamepad dependency.

## Summary

Refuse a staged buffer older than the newest tag. Session 36 quarantined the stale v0.32.0 buffer (`state/pending-post.quarantine-2026-10-20-v0.32.0.txt`) so noon posts nothing stale, but nothing in code stops the next stale buffer from posting. This story adds the guard: at noon-run time, compare the buffer provenance against the newest tag and refuse to post stale text. Verified against the v0.33.0 tag with the quarantined v0.32.0 buffer as the negative control.

## jakebot decision (advisory only, recorded)

Session 37 Wave 1 set A-variant, per session 20261021_011108_21a235: noon-job hardening stories (failure alert plus version guard) as P1 plus standing currency as P2. B (advancing the FPS playable slice before the gamepad gate has run) waits on the gate. A is not close. P1 order per parent call: noon failure alert first (082, outward-facing), version guard second (083).

**Citation:** `flambeee-team/session-plan.md`, Session 37 (2026-10-21), section "jakebot decision (advisory only, recorded)", session 20261021_011108_21a235.

## Negative control cited verbatim

The quarantined v0.32.0 buffer at `flambeee-team/state/pending-post.quarantine-2026-10-20-v0.32.0.txt` (contents: "Day Pad counts your characters now: live N/280 on your daily line. Plus the FPS build decision is on record. v0.32.0 https://flambeee.com"). Newest tag at planning is v0.33.0. A v0.32.0 buffer against a v0.33.0 newest tag is stale by definition and must be refused.

## Requirements

### 1. Newest-tag resolution at run time, never hardcoded

The guard resolves the newest tag with `git ls-remote --tags origin` at noon-run time, the same resolution the website currency checker uses. No hardcoded version string anywhere in the guard path. A future v0.34.0 tag must be picked up with no code change.

### 2. Refusal behavior on stale buffer

When the staged buffer names a version older than the resolved newest tag (the v0.32.0 stale-buffer class), the noon job refuses to post: no post sent, pending file kept (not cleared, not archived to posted-posts.log), non-zero exit, plus the loud-failure signals from Story 082 (durable log entry plus alert-artifact line). Refusal is the pass behavior for a stale buffer, not an error to work around.

### 3. Verification against the v0.33.0 tag (per session plan constraint 1)

P1 must produce verifiable artifacts: the version guard running against the v0.33.0 tag. Minimum proof, each run recorded with command, exit code, and output:

- Negative control: the quarantined v0.32.0 buffer text (used as a scratch copy, quarantine file itself untouched) against newest tag v0.33.0 resolves to REFUSE, non-zero exit, no post, pending kept.
- Positive control: a scratch buffer naming v0.33.0 against newest tag v0.33.0 resolves to ALLOW (proceeds down the normal post path in dry-run or simulated mode; no real post sent by this story).

Both runs pasted into the dev record with real exit codes. Code with no runs is not done.

### 4. No-new-post rule

This story sends no real post. The quarantine file stays quarantined. Simulated runs use scratch copies under scratch, never the live pending path, and write no success entry to posted-posts.log.

### 5. No FPS advancement

No FPS or playable-slice change in this diff. No gamepad run on this box.

## BDD scenarios

**Scenario 1: Stale buffer refused.**
Given a staged buffer naming v0.32.0 and the newest tag resolving to v0.33.0 at run time, when the noon job runs, then no post is sent, the pending file is kept, and exit is non-zero.

**Scenario 2: Refusal is loud.**
Given the stale-buffer refusal, when the noon job exits, then the durable log entry plus the Story 082 alert-artifact line record the stale version, the newest tag, and the exit code.

**Scenario 3: Current buffer allowed.**
Given a staged buffer naming the resolved newest tag (v0.33.0), when the guard evaluates, then it allows the normal post path (no refusal from the guard; downstream success or failure is owned by the 082 path).

**Scenario 4: Tag resolution is live.**
Given a future newest tag on origin, when the guard runs, then it resolves that tag at run time with no code change and judges the buffer against it.

**Scenario 5: Quarantine untouched.**
Given the quarantined v0.32.0 file, when the verification runs complete, then the quarantine file is byte-identical to its entering state and posted-posts.log holds no new success entry.

## Acceptance Criteria

**AC-1.** Guard resolves newest tag via `git ls-remote --tags origin` at run time; no hardcoded version in the guard path (Scenario 4).
**AC-2.** Negative control (v0.32.0 scratch buffer vs v0.33.0 tag) REFUSES with non-zero exit, no post, pending kept, real output recorded (Scenario 1).
**AC-3.** Refusal emits the loud-failure signals (log entry plus alert-artifact line naming stale version, newest tag, exit code) (Scenario 2).
**AC-4.** Positive control (v0.33.0 scratch buffer vs v0.33.0 tag) ALLOWS with real output recorded and no real post sent (Scenario 3).
**AC-5.** Quarantine file untouched and no new posted-posts.log success entry (Scenario 5).
**AC-6.** Copy and log lines use plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- The failure-alert mechanism itself (Story 082 owns it; this story only routes refusal through it).
- Restoring creds, changing post copy, or touching the success archive format.
- Any website, game-file, or release change.
- Advancing the FPS playable slice before the gamepad gate has run.
- A gamepad run on this box. There is no pad here; see the note below.

## Notes (not stories, carried by this file)

1. **Headed gamepad gate: OPEN-BLOCKED-ON-HARDWARE.** Pointer to the Story 074 runnable gate verbatim (rig jake-dev-desk, headed mode, pass criteria, Kai runs plus Scout witnesses). Flip trigger: pad plus headed browsers available on the named rig. Carry-forward line: each subsequent session carries this note until it flips. Sixth session carrying.

## Open questions for dev wave

1. How buffer provenance is read (version token parse rule for the staged text; record the exact rule).
2. Negative and positive control commands plus real exit codes plus outputs.
3. Interaction detail with the 082 alert path (single shared refusal exit or two layered exits; record the choice).
