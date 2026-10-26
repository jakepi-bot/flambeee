# Story 099: Website currency and deploy mirror verification, Session 42 (P3, Standing Verification)

**Status:** Ready for development (Session 42, 2026-10-26).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P3 (standing per-release verification; no product behaviour change; no new release implied).
**Assigned to:** **Riven** (frontend/site owner). Run 2 is conditional on the release wave's cut decision (see section 2).
**Tracked by:** Session 42 plan, Story 099. Follows Stories 049, 052, 054, 057, 061, 065, 067, 070, 073, 076, 078, 080, 084, 087, 090, 093, and 095 in the standing series. Modeled on Story 093.
**Depends on:** None. No code dependency. Checker frozen.

## Summary

Standing check that the repo mirror and the release tag agree after the Session 42 stories land. No new code and no new script. The checker already exists at `scripts/verify-website-currency.sh` and is frozen. Run 1 records the entering state (heading v0.35.0 vs tag v0.35.0, timer card present). Run 2 is conditional: if the release wave cuts a version on the back of Story 098, run 2 verifies the new heading; if no cut (harness-only session, Session 40 precedent), run 2 is N/A by design. Explicit check items: CACHE_VERSION measured not assumed, Play links plus GAME_ORDER measured at run time, timer card present, and the live-path absence observed at planning.

## jakebot decision (advisory only, recorded)

Session 42 Wave 1 priorities per jakebot (session local-ed66cc3b157bcdcdbd66f8c796fc4, proceeded on its read): standing website currency Session 42 as P3, heading-vs-tag plus Play links plus GAME_ORDER plus CACHE_VERSION against the repo mirror, live-path absence as an explicit check item. Release lean from session local-c2fc5af6c3776a47493ffb5ae3c36f977871147cc937c6cb015b2b5efd7a0d7a: harness-only work does not warrant a cut; any Story 098 user-visible landing reopens the question for the release wave, not for this story.

**Citation:** `flambeee-team/session-plan.md`, Session 42 (2026-10-26), sections "jakebot decisions (advisory only, recorded)" and "Priorities (in order)".

## Baseline measured at Session 42 planning (2026-10-26 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.35.0 ("Countdown Timer joins the Apps shelf") |
| Latest tag / release | v0.35.0 |
| Heading vs tag | MATCH |
| Open issues / open PRs | 0 / 0 |
| Play links | measured at run time, not assumed here (6 expected: `games/wordfire, games/minesweeper, games/simon, games/2048, games/cinder, games/afterglow`) |
| `GAME_ORDER` rotation list | measured at run time, not assumed here (6/6 including afterglow expected) |
| Apps entries | `website/apps/index.html` present (Day Pad) plus `website/apps/timer.html` present (timer card links `apps/timer.html`) |
| `sw.js` `CACHE_VERSION`, repo mirror | 11 (measured at planning; run 1 must read the line, not assume it) |
| Live path `/home/jake/share/Flambeee/` | **Not present from this box** (absent 15th session running; same environmental finding as Sessions 31-41). Run 1 must confirm by measurement, not assume green. |

## Requirements

### 1. Run 1, pre-merge

Run `scripts/verify-website-currency.sh` **before** the Session 42 stories merge. Expected: record exact exit code and output. If it fails on the live-path absence, that is a real finding about the current state; report it, resolve by measurement, do not proceed quietly. Repo-side facts (heading vs tag, Play links, GAME_ORDER, CACHE_VERSION, timer card) are each measured at run time and recorded with values, never assumed from this baseline table.

### 2. Run 2, conditional on the release wave

If the release wave cuts a version on the back of Story 098, run 2 verifies post-tag: heading names the new tag, mirror still byte-identical, CACHE_VERSION reads the bumped value. If no cut (harness-only session), the dev record states "Run 2: N/A, no release" and stops. This story does not decide the cut; the release wave does.

### 3. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not assume the deployed copy is stale.** `share/` is outside version control, so an edit there is unrecoverable. Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write into either.
4. Re-run `cmp`, record both sha256.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. If it reports a genuine failure, fix the thing it reports, not the checker. Verify with `git diff --stat` on that path, which must be empty.

### 5. Noon-tail note (not a wave, not this story)

The 082 matrix plus mirror checker re-run belongs to the tail (Scout or parent), not to this story. If either re-run goes non-zero it becomes the session and bumps P1/P2. This story does not execute or record the tail; it only notes the interaction so currency findings are not confused with pipeline findings.

## BDD scenarios

**Scenario 1: Heading-vs-tag, run 1.**
Given the pre-merge tree, when the checker runs, then the What's New heading names the entering latest tag (v0.35.0 vs tag v0.35.0 MATCH) and the run result with exit code is recorded.

**Scenario 2: Run 2 conditional.**
Given the release wave's cut decision, when run 2 comes due, then either the new heading-vs-tag plus mirror plus CACHE values are recorded (cut happened) or the dev record states "Run 2: N/A, no release" with no tag resolution and no sync.

**Scenario 3: Play links measured.**
Given the site, when the Play links are read at run time, then the count plus targets are recorded (6 relative `games/*.html` links expected) and every target exists.

**Scenario 4: Rotation plus Apps entries measured.**
Given the site, when `GAME_ORDER` is read at run time, then coverage is recorded (6/6 including afterglow expected); the Day Pad entry (`website/apps/index.html`) and the timer entry (`website/apps/timer.html`, card links `apps/timer.html`) are both present.

**Scenario 5: CACHE_VERSION measured.**
Given the repo `website/sw.js`, when the version line is read pre-merge, then the value is recorded as measured (11 at planning), with no assumption from this doc.

**Scenario 6: Live-path absence explicit.**
Given the planning-measured absence of the live path from this box, when run 1 executes, then it records the `ls` result by measurement and records the mirror status as deferred to the serving host instead of assuming green.

**Scenario 7: Checker frozen.**
Given the story diff, when `git diff --stat` on `scripts/verify-website-currency.sh` is read, then it is empty.

## Acceptance Criteria

**AC-1.** Run 1 executed pre-merge with exit code and output recorded, live-path result measured (Scenarios 1, 6).
**AC-2.** Run 2 recorded as conditional: new-tag values after a cut, or "Run 2: N/A, no release" (Scenario 2).
**AC-3.** Play-link count plus targets measured at run time with every target existing (Scenario 3).
**AC-4.** `GAME_ORDER` coverage measured at run time; Day Pad and timer Apps entries both present with the timer card target recorded (Scenario 4).
**AC-5.** `CACHE_VERSION` value recorded as measured from the repo sw.js, not assumed (Scenario 5).
**AC-6.** `scripts/verify-website-currency.sh` byte-identical to its entering state. Verified with `git diff --stat` on that path, which must be empty (Scenario 7).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Run 1 with real exit code; the `CACHE_VERSION` line from the repo sw.js; the `GAME_ORDER` line; the Play-link count plus targets; the tag-versus-heading comparison; the timer-card link target; the live-path `ls` measurement; run 2 values or the N/A statement. Numbers, not adjectives.

## Non-Goals

- Any website design or content change beyond a parent-owned What's New update. The What's New copy is not this story's step.
- Changing the checker.
- Writing to `/home/jake/share/Flambeee/` before the mirror is confirmed authoritative. See requirement 3.
- Advancing the FPS slice or scheduling a gamepad run on this box. The gate stays deferred until a pad exists on the named rig.
- Deciding any version cut or running any post-tag verification beyond the conditional run 2.
