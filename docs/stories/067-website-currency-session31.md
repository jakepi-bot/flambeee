# Story 067: Website currency and deploy mirror verification, Session 31 (P2, Standing Verification)

**Status:** Ready for development (Session 31, 2026-10-15).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (standing per-release verification; no product behaviour change).
**Assigned to:** **Riven** (frontend/site owner). **Scout** may execute run 2.
**Tracked by:** Session 31 plan, Story 067. Follows Stories 049, 052, 054, 057,
061, and 065 in the standing series.

## Summary

Standing two-run check that the live website, the repo mirror, and the release
tag agree after the Session 31 build lands. No new code and no new script. The
checker already exists at `scripts/verify-website-currency.sh`. This story is
about **running it twice at the right moments** (heading-vs-tag before and
after release) plus the deploy-mirror byte-identical checks, so the Story 066
release lands on a current site. Expected outcome: **PASS**.

## Baseline measured at Session 31 planning (2026-10-15 07:25 CDT)

| Check | Value |
|---|---|
| Games section heading | "Six games, one arcade", 6 cards |
| Website What's New heading | v0.28.0 ("Afterglow gets a daily level, same for everyone") |
| `GAME_ORDER` rotation list | 6/6 including afterglow |
| Play links | 6 (`games/*.html`) |
| `sw.js` `CACHE_VERSION`, live and mirror | 6 on both sides |
| Deploy mirrors | `cmp` exit 0 on index, sw.js, all 6 game files |
| Latest tag / release | v0.28.0 |
| Open issues / open PRs | 0 / 0 |

Clean baseline. Run 1 should pass against this state, before Story 066 lands.

## Requirements

### 1. Run 1, pre-release

Run `scripts/verify-website-currency.sh` **before** the Story 066 merge.
Expected: **PASS, exit 0.** Record the exact exit code and output. If it
fails, that is a finding about the current state; report it, do not proceed
quietly.

### 2. Run 2, post-release

After the tag exists and the release is published (expected v0.29.0 if the dev
wave ships it; resolve with `git ls-remote --tags origin` at run time, never
hardcode):

- Origin's latest tag matches the live What's New heading.
- `cmp /home/jake/share/Flambeee/index.html website/index.html` is exit 0,
  with equal sha256 on both sides **at the absolute path**.
- All 6 game-file deploy mirrors re-synced **after** the merge, copied from
  the committed side, and `cmp` against `src/` is exit 0 with equal sha256.
- `sw.js` `CACHE_VERSION` agrees on both `website/sw.js` and
  `/home/jake/share/Flambeee/sw.js` (record the version line from both files
  either way). If the shell changed and this is not bumped, returning visitors
  keep the stale shell and the release reads as a no-op.

### 3. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a
difference, **do not assume the deployed copy is stale.** `share/` is outside
version control, so an edit there is unrecoverable. Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never
   hand-write into either.
4. Re-run `cmp`, record both sha256.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. If it
reports a genuine failure, fix the thing it reports, not the checker.

## BDD scenarios

**Scenario 1: Heading-vs-tag, run 1.**
Given the pre-release tree, when the checker runs, then the What's New heading
names the entering latest tag and the run passes exit 0.

**Scenario 2: Heading-vs-tag, run 2.**
Given the tag published and the live sync done, when the checker runs, then
the What's New heading names the true latest tag and the run passes exit 0.

**Scenario 3: Mirrors byte-identical.**
Given the merged commit, when `cmp` runs on index, sw.js, and all 6 game files
at the absolute paths, then every pair is exit 0 with equal sha256 recorded.

**Scenario 4: Play links.**
Given the live site, when the Play links are read, then 6 relative
`games/*.html` links exist and every target exists.

**Scenario 5: Rotation covers all games.**
Given the live site, when `GAME_ORDER` is read, then it contains all 6 games
(6/6) including afterglow.

## Acceptance Criteria

**AC-1.** Run 1 passes, exit 0, before the Story 066 merge, output recorded
(Scenario 1). Expected PASS.

**AC-2.** Run 2 passes, exit 0, after tag + release + live sync;
heading-vs-tag match recorded (Scenario 2). Expected PASS.

**AC-3.** `cmp` exit 0 with equal sha256 pairs for `index.html` (live vs
mirror), `sw.js` (live vs mirror, version line quoted from both), and all 6
game files (deploy mirror vs `src/`) after the merge (Scenario 3).

**AC-4.** 6 Play links present, all targets exist (Scenario 4).

**AC-5.** `GAME_ORDER` 6/6 including afterglow (Scenario 5).

**AC-6.** `scripts/verify-website-currency.sh` byte-identical to its entering
state. Verified with `git diff --stat` on that path, which must be empty.

## Required Proof

Both runs with their real exit codes, both `cmp` results with the sha256
pairs, the `CACHE_VERSION` line from both sw.js files, the `GAME_ORDER` line
showing 6/6, the 6 Play links, and the tag-versus-heading comparison. Numbers,
not adjectives. "Deployed copy refreshed" is not evidence; two equal sha256
values are.

## Non-Goals

- Any website design or content change beyond the What's New update. The What's
  New copy is the parent's Wave 4 step.
- Changing the checker.
- Writing to `/home/jake/share/Flambeee/` before the mirror is confirmed
  authoritative. See requirement 3.
