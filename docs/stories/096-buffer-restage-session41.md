# Story 096: v0.35.0 buffer restage plus noon creds decision (Session 41, P2, Release-wave planning)

**Status:** Ready for the release wave (Session 41, 2026-10-25).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (release-wave planning; small, rides the release wave, not a wave of its own).
**Assigned to:** **Release-wave owner** (parent or release job). No dev code owner, no QA owner. Planning only: no post is sent from this story.
**Tracked by:** Session 41 plan, Story 096. Follows Story 083 (pending-post version guard) and the Session 40 noon state (v0.34.0 buffer staged but unposted, creds file absent 19 consecutive failures).
**Depends on:** The release-wave cut decision. If no v0.35.0 tag lands, the restage branch is N/A and the creds fork still records.

## Summary

Two small release-wave items, both owned by the release wave, neither sending a post. First, the restage rule: a new v0.35.0 tag makes the Story 083 guard REFUSE the queued v0.34.0 buffer, so the wave stages a fresh v0.35.0 buffer naming only what a visitor sees, with no cache talk, through the staging script. Second, the noon creds fork: either Jake drops the creds file or the wave pauses noon and records why, because a 20th identical failure line is worse than either. The noon cron owns posting; this story stages text and records a decision, nothing more.

## jakebot decision (advisory only, recorded)

Session 41 Wave 1 priorities per jakebot session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c: (3) P2, release-wave v0.35.0 buffer restage plus noon creds decision. Small, rides the release wave: write a v0.35.0 buffer naming only what a visitor sees, no cache talk; leave the v0.34.0 file for 083 to refuse; record the creds decision (Jake drops the file, or pause noon and record why; a 20th identical failure line is worse than either).

**Citation:** `flambeee-team/session-plan.md`, Session 41 (2026-10-25), section "jakebot decision (advisory only, recorded)", session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c.

## Entering state (measured at Session 41 planning)

- `flambeee-team/state/pending-post.txt` holds the staged v0.34.0 buffer ("Day Pad: the Saved note clears the moment you keep typing. v0.34.0 https://flambeee.com"). It has NOT posted: posted-posts.log last entry is v0.31.0-era.
- Bluesky checks are failing on the missing credentials file (`~/.config/flambeee/.env` absent, whole dir gone; 19 consecutive failures at planning).
- Newest tag is v0.34.0, so the guard currently ALLOWS the queued buffer; the only thing stopping the post is the missing creds.

## Requirements

### 1. The 083-guard interaction (why a restage is needed at all)

Story 083 resolves the newest tag via `git ls-remote --tags origin` at noon-run time and refuses any staged buffer naming an older version: no post sent, pending file kept, non-zero exit through the loud 082 path. The moment a v0.35.0 tag lands on origin, the queued v0.34.0 buffer becomes the stale class and the guard REFUSEs it. That refusal is correct behavior, not an error to work around. The restage rule below exists so the refusal does not leave noon with nothing true to say.

### 2. The restage rule (tag branch only)

If the release wave cuts v0.35.0, the wave stages a fresh v0.35.0 buffer to `flambeee-team/state/pending-post.txt`, replacing the queued v0.34.0 text:

- Names only what a visitor sees (the timer app from Story 094, in visitor words).
- No cache talk (no CACHE_VERSION, no sw.js, no precache; visitors do not care).
- Staged via the staging script (`/home/jake/.hermes/flambeee/scripts/flambeee-stage-post.py`), which validates the 300-grapheme Bluesky limit plus link rules at staging time. Never hand-write the pending file; a hand-written buffer can pass the release chain and then fail silently in the noon cron.
- Validator `--check` exit 0 recorded before the wave closes.

If no v0.35.0 tag lands (Story 094 slips), this branch is N/A: the v0.34.0 buffer stays queued, the guard never triggers, and the dev record states "Restage: N/A, no release" and stops. Planning (this half) does not touch `pending-post.txt` under either branch.

### 3. The noon creds fork (either branch)

Record one of exactly two outcomes before the wave closes:

- (a) Jake drops the creds file at `~/.config/flambeee/.env`, and the wave records the file present; or
- (b) noon stays paused (or check-only) and the wave records why, with the pause stated plainly instead of another silent failure line.

A 20th identical failure line is worse than either outcome, so the wave does not simply re-run and log the same miss. The missing creds file itself is Jake's; the decision record is the wave's.

### 4. No post sent from this story

Staging text is not posting. The noon cron owns posting. No dry-run post, no live post, no posted-posts.log entry comes out of this story. Quarantine and posted-posts.log sha256 identical before and after, verified and recorded.

## BDD scenarios (restage-rule and creds-fork completeness checks)

**Scenario 1: Guard interaction stated.**
Given Story 083 and a new v0.35.0 tag, when the noon job runs against the old queued buffer, then it REFUSEs (no post, pending kept, non-zero exit), and this story records that refusal as expected, not as a defect.

**Scenario 2: Restage rule, tag branch.**
Given a v0.35.0 cut, when the release wave restages, then the pending file holds fresh v0.35.0 text naming only the visitor-visible change with no cache talk, staged via the staging script with `--check` exit 0 recorded.

**Scenario 3: Restage rule, no-tag branch.**
Given no v0.35.0 cut, when the restage comes due, then the record states "Restage: N/A, no release", the v0.34.0 buffer stays queued untouched, and no staging script runs.

**Scenario 4: Creds fork, file branch.**
Given Jake provides the creds file, when the wave checks, then it records the file present and noon is unblocked on credentials.

**Scenario 5: Creds fork, pause branch.**
Given no creds file, when the wave closes, then it records the pause and the reason plainly, with no further identical failure line treated as an outcome.

**Scenario 6: No-post check.**
Given this story's execution, when quarantine and posted-posts.log are hashed before and after, then both sha256 are identical.

**Scenario 7: jakebot citation check.**
Given the Wave 1 set decision, when this doc is reviewed, then it records the P2 priority, the restage rule, the creds fork, the no-post boundary, and the citation session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c.

## Acceptance Criteria

**AC-1.** 083-guard interaction stated with the REFUSE-on-new-tag behavior recorded as expected (Scenario 1).
**AC-2.** Restage rule complete for both branches: staged v0.35.0 buffer per the rule with `--check` exit 0, or recorded N/A with the v0.34.0 buffer untouched (Scenarios 2, 3).
**AC-3.** Creds fork resolved to exactly one recorded outcome: file present, or pause with reason (Scenarios 4, 5).
**AC-4.** No post sent: quarantine and posted-posts.log sha256 identical before and after (Scenario 6).
**AC-5.** jakebot priority and citation recorded as above (Scenario 7).
**AC-6.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Guard behavior reference (083 negative/positive controls, no re-proof needed), the staged buffer text with grapheme count and `--check` exit code (tag branch) or the N/A record (no-tag branch), the creds-fork outcome with its evidence, and the before/after sha256 pair for quarantine plus posted-posts.log. Numbers, not adjectives.

## Non-Goals

- Sending any post, dry-run or live (noon cron owns posting).
- Touching `pending-post.txt` during planning (this half); only the release wave restages, and only in the tag branch.
- Fixing the creds gap with a workaround (no checked-in secrets, no alt path that bypasses the poster auth).
- Cutting v0.35.0 (the cut decision is the release wave's; this story only handles its consequences).
- Any website, game, FPS, or schedule change.

## Open questions for the release wave

1. Cut decision: v0.35.0 on Story 094 green, or no tag (drives the Scenario 2 vs 3 fork).
2. Buffer wording for the v0.35.0 text (visitor-visible only, one line, link included).
3. Creds fork outcome: file from Jake, or recorded pause with reason.
