# Story 095: Website currency and deploy mirror verification, Session 41 (P3, Standing Verification)

**Status:** Ready for development (Session 41, 2026-10-25).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P3 (standing per-release verification; no product behaviour change; no new release implied).
**Assigned to:** **Riven** (frontend/site owner). Run 2 executes at v0.35.0 with CACHE 11 if the tag lands, else N/A by design.
**Tracked by:** Session 41 plan, Story 095. Follows Stories 049, 052, 054, 057, 061, 065, 067, 070, 073, 076, 078, 080, 084, 087, 090, and 093 in the standing series. Modeled on Story 093.
**Depends on:** None. No code dependency. Checker frozen.

## Summary

Standing run-1 check that the repo mirror and the release tag agree after the Session 41 stories land, plus a conditional run 2. No new code and no new script. The checker already exists at `scripts/verify-website-currency.sh` and is frozen. Run 1 executes pre-merge against the v0.34.0 baseline. Run 2 executes post-tag at v0.35.0 with CACHE 11 if the release wave cuts the tag (per the Story 093 precedent: run 2 verifies the new heading and the new CACHE value); if no release cuts this session, run 2 is N/A by design. Explicit check items: CACHE_VERSION 10 baseline, Play links plus GAME_ORDER measured at run time, and the live-path absence observed at planning.

## jakebot decision (advisory only, recorded)

Session 41 Wave 1 priorities per jakebot session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c: standing website currency Session 41 as P3, run 1 pre-merge plus run 2 post-tag at v0.35.0 with CACHE 11 if the tag lands, run 2 N/A with no release. No gamepad run on this box; live path not invented.

**Citation:** `flambeee-team/session-plan.md`, Session 41 (2026-10-25), section "jakebot decision (advisory only, recorded)", session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c.

## Baseline measured at Session 41 planning (2026-10-25 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.34.0 ("Day Pad clears Saved while you type") |
| Latest tag / release | v0.34.0 |
| Heading vs tag | MATCH |
| Open issues / open PRs | 0 / 0 |
| Play links | measured at run time, not assumed here (6 expected: `games/wordfire, games/minesweeper, games/simon, games/2048, games/cinder, games/afterglow`) |
| `GAME_ORDER` rotation list | measured at run time, not assumed here (6/6 including afterglow expected) |
| Apps entry | `website/apps/index.html` present (Day Pad, prefix `flambeee-apps-`, N/280 count with Saved-clear-on-input, maxlength 280) |
| `sw.js` `CACHE_VERSION`, repo mirror | 10 (baseline; run 1 must read 10; run 2, if the tag lands, must read 11) |
| Live path `/home/jake/share/Flambeee/` | **Not present from this box** (absent 13th session running; same environmental finding as Sessions 31-40). Run 1 must confirm by measurement, not assume green. |

## Requirements

### 1. Run 1, pre-merge

Run `scripts/verify-website-currency.sh` **before** the Session 41 stories merge. Expected: record exact exit code and output. If it fails on the live-path absence, that is a real finding about the current state; report it, resolve by measurement, do not proceed quietly.

### 2. Run 2, conditional on the release wave

If the release wave cuts v0.35.0 (Story 094 green and the cut decided), run 2 executes post-tag: heading must name **v0.35.0**, `CACHE_VERSION` must read **11**, tag-vs-heading MATCH recorded. If no release cuts this session, run 2 is N/A by design: no post-tag heading check, no deploy sync, no tag resolution. The dev record states "Run 2: N/A, no release" and stops. No v0.35.0 cut exists to verify against in that branch.

### 3. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not assume the deployed copy is stale.** `share/` is outside version control, so an edit there is unrecoverable. Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write into either.
4. Re-run `cmp`, record both sha256.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. If it reports a genuine failure, fix the thing it reports, not the checker. Verify with `git diff --stat` on that path, which must be empty.

### 5. Noon-tail note (not a wave, not this story)

The 082 matrix plus mirror checker re-run belongs to the tail (~10 min, Scout or parent), not to this story. If either re-run goes non-zero it becomes the session and bumps P1/P2. This story does not execute or record the tail; it only notes the interaction so currency findings are not confused with pipeline findings.

## BDD scenarios

**Scenario 1: Heading-vs-tag, run 1.**
Given the pre-merge tree, when the checker runs, then the What's New heading names the entering latest tag (v0.34.0 vs tag v0.34.0 MATCH) and the run result with exit code is recorded.

**Scenario 2: Run 2 fork.**
Given the release-wave outcome, when run 2 comes due, then either the post-tag check records heading v0.35.0 with CACHE 11 and MATCH, or the dev record states "Run 2: N/A, no release" with no tag resolution and no sync.

**Scenario 3: Play links measured.**
Given the site, when the Play links are read at run time, then the count plus targets are recorded (6 relative `games/*.html` links expected) and every target exists.

**Scenario 4: Rotation plus Apps entry measured.**
Given the site, when `GAME_ORDER` is read at run time, then coverage is recorded (6/6 including afterglow expected), and the Apps entry (`website/apps/index.html` with N/280 count, `flambeee-apps-` prefix, Saved-clear-on-input) is present. If Story 094 merged, the timer page plus its card are noted as additive facts, not as currency requirements.

**Scenario 5: CACHE_VERSION baseline and conditional.**
Given the repo `website/sw.js`, when the version line is read pre-merge, then `CACHE_VERSION` is 10; when read post-tag (tag branch only), then it is 11.

**Scenario 6: Live-path absence explicit.**
Given the planning-measured absence of the live path from this box, when run 1 executes, then it records the `ls` result by measurement and records the mirror status as deferred to the serving host instead of assuming green.

## Acceptance Criteria

**AC-1.** Run 1 executed pre-merge with exit code and output recorded, live-path result measured (Scenarios 1, 6).
**AC-2.** Run 2 fork resolved by measurement: post-tag v0.35.0/CACHE 11 check, or recorded N/A with no release, no tag resolution, no sync (Scenario 2).
**AC-3.** Play-link count plus targets measured at run time with every target existing (Scenario 3).
**AC-4.** `GAME_ORDER` coverage measured at run time, Apps entry present with count plus prefix plus Saved-clear behavior noted (Scenario 4).
**AC-5.** `CACHE_VERSION` 10 baseline recorded run 1; 11 recorded run 2 in the tag branch only (Scenario 5).
**AC-6.** `scripts/verify-website-currency.sh` byte-identical to its entering state. Verified with `git diff --stat` on that path, which must be empty.
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Run 1 with real exit code, the `CACHE_VERSION` line from the repo sw.js, the `GAME_ORDER` line, the Play-link count plus targets, the tag-versus-heading comparison, the live-path `ls` measurement, and the run-2 fork outcome with its evidence. Numbers, not adjectives.

## Non-Goals

- Any website design or content change beyond a parent-owned What's New update. The What's New copy is not this story's step.
- Changing the checker.
- Writing to `/home/jake/share/Flambeee/` before the mirror is confirmed authoritative. See requirement 3.
- Advancing the FPS slice or scheduling a gamepad run on this box. The gate stays deferred until a pad exists on the named rig.
- Cutting v0.35.0 or deciding the cut (release wave owns that; this story only verifies whichever branch lands).
