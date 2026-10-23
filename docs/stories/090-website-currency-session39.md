# Story 090: Website currency and deploy mirror verification, Session 39 (P3, Standing Verification)

**Status:** Ready for development (Session 39, 2026-10-23).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P3 (standing per-release verification; no product behaviour change; no new release implied).
**Assigned to:** **Riven** (frontend/site owner). **Scout** may execute run 2 if the release wave cuts v0.34.0, else run 2 is N/A.
**Tracked by:** Session 39 plan, Story 090. Follows Stories 049, 052, 054, 057, 061, 065, 067, 070, 073, 076, 078, 080, 084, and 087 in the standing series.

## Summary

Standing run-1 check that the repo mirror and the release tag agree after the Session 39 stories land. No new code and no new script. The checker already exists at `scripts/verify-website-currency.sh` and is frozen. This session runs run 1 only; run 2 is N/A by design unless the release wave cuts v0.34.0 on the back of Story 088. Explicit check items: CACHE_VERSION 9 baseline, Play links plus GAME_ORDER measured at run time, Day Pad count plus prefix, and the live-path absence observed at planning.

## jakebot decision (advisory only, recorded)

Session 39 Wave 1 priorities per session 20261023_011104_76722e: standing website currency Session 39 as P3, run 1 only, run 2 N/A with no release. No FPS playable advancement; no gamepad run on this box; live path not invented.

**Citation:** `flambeee-team/session-plan.md`, Session 39 (2026-10-23), section "jakebot decision (advisory only, recorded)", session 20261023_011104_76722e.

## Baseline measured at Session 39 planning (2026-10-23 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.33.0 ("Day Pad cache fix, returning visitors get the count") |
| Latest tag / release | v0.33.0 |
| Heading vs tag | MATCH |
| Open issues / open PRs | 0 / 0 |
| Play links | measured at run time, not assumed here (6 expected: `games/wordfire, games/minesweeper, games/simon, games/2048, games/cinder, games/afterglow`) |
| `GAME_ORDER` rotation list | measured at run time, not assumed here (6/6 including afterglow expected) |
| Apps entry | `website/apps/index.html` present (Day Pad, prefix `flambeee-apps-`, N/280 count, maxlength 280) |
| `sw.js` `CACHE_VERSION`, repo mirror | 9 (baseline; Story 088 bumps to 10 in its own diff, so run 1 pre-merge must read 9) |
| Live path `/home/jake/share/Flambeee/` | **Not present from this box** (absent 9th session running; same environmental finding as Sessions 31-38). Run 1 must confirm by measurement, not assume green. |

## Requirements

### 1. Run 1, pre-merge (the only run unless a release cuts)

Run `scripts/verify-website-currency.sh` **before** the Session 39 stories merge. Expected: record exact exit code and output. If it fails on the live-path absence, that is a real finding about the current state; report it, resolve by measurement, do not proceed quietly.

### 2. Run 2, N/A by design unless the release wave cuts v0.34.0

No release is implied by planning (mechanism plus polish stories plus currency only). Run 2 is N/A: no post-tag heading check, no deploy sync, no new tag resolution. If the release wave cuts v0.34.0 on Story 088, Scout executes run 2 per the Story 084 procedure (heading-vs-tag MATCH at v0.34.0, `cmp` exit 0 with equal sha256 on index, sw.js, apps page, and all 6 game files at the absolute paths, CACHE_VERSION 10 on both sides). Otherwise the dev record states "Run 2: N/A, no release" and stops.

### 3. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not assume the deployed copy is stale.** `share/` is outside version control, so an edit there is unrecoverable. Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write into either.
4. Re-run `cmp`, record both sha256.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. If it reports a genuine failure, fix the thing it reports, not the checker. Verify with `git diff --stat` on that path, which must be empty.

### 5. Day Pad check (Session 39 explicit)

Day Pad count plus prefix are check items: run 1 records the N/280 count label presence on the source path plus the `flambeee-apps-` prefix. maxlength 280 unchanged. If Story 088 has merged before run 1, run 1 additionally records the cleared-on-input status behavior as present; it does not re-prove it (Scout owns that under Story 088).

### 6. Live-path check (Session 39 explicit)

The planning-measured absence of `/home/jake/share/Flambeee/` from this box is a check item: run 1 records `ls` exit code and path result; if still absent, the dev wave verifies the live mirror from the host that serves it rather than assuming green. Live mirror status is recorded as deferred to the serving host, not phrased as a pass.

## BDD scenarios

**Scenario 1: Heading-vs-tag, run 1.**
Given the pre-merge tree, when the checker runs, then the What's New heading names the entering latest tag (v0.33.0 vs tag v0.33.0 MATCH) and the run result with exit code is recorded.

**Scenario 2: Run 2 N/A.**
Given no release this session, when run 2 comes due, then the dev record states "Run 2: N/A, no release" with no tag resolution and no sync. If v0.34.0 cuts, Scout runs the Story 084 procedure instead.

**Scenario 3: Play links measured.**
Given the site, when the Play links are read at run time, then the count plus targets are recorded (6 relative `games/*.html` links expected) and every target exists.

**Scenario 4: Rotation plus Apps entry measured.**
Given the site, when `GAME_ORDER` is read at run time, then coverage is recorded (6/6 including afterglow expected), and the Apps entry (`website/apps/index.html` with N/280 count and `flambeee-apps-` prefix) is present.

**Scenario 5: CACHE_VERSION 9 baseline.**
Given the repo `website/sw.js`, when the version line is read pre-merge, then `CACHE_VERSION` is 9, with no bump from a docs-only diff (Story 088 carries its own 9-to-10 bump).

**Scenario 6: Live-path absence explicit.**
Given the planning-measured absence of the live path from this box, when run 1 executes, then it records the `ls` result by measurement and records the mirror status as deferred to the serving host instead of assuming green.

## Acceptance Criteria

**AC-1.** Run 1 executed pre-merge with exit code and output recorded, live-path result measured (Scenarios 1, 6).
**AC-2.** Run 2 recorded as N/A with no release, or executed per the Story 084 procedure if v0.34.0 cuts (Scenario 2).
**AC-3.** Play-link count plus targets measured at run time with every target existing (Scenario 3).
**AC-4.** `GAME_ORDER` coverage measured at run time, Apps entry present with count plus prefix (Scenario 4).
**AC-5.** `CACHE_VERSION` 9 baseline recorded run 1, no bump from docs-only diff (Scenario 5).
**AC-6.** `scripts/verify-website-currency.sh` byte-identical to its entering state. Verified with `git diff --stat` on that path, which must be empty.
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Run 1 with real exit code, the `CACHE_VERSION` line from the repo sw.js, the `GAME_ORDER` line, the Play-link count plus targets, the tag-versus-heading comparison, and the live-path `ls` measurement. Numbers, not adjectives.

## Non-Goals

- Any website design or content change beyond a parent-owned What's New update. The What's New copy is not this story's step.
- Changing the checker.
- Writing to `/home/jake/share/Flambeee/` before the mirror is confirmed authoritative. See requirement 3.
- Advancing the FPS slice or scheduling a gamepad run on this box. The gate stays deferred until a pad exists on the named rig.
