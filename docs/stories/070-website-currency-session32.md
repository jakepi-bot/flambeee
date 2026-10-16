# Story 070: Website currency and deploy mirror verification, Session 32 (P2, Standing Verification)

**Status:** Ready for development (Session 32, 2026-10-16).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (standing per-release verification; no product behaviour change).
**Assigned to:** **Riven** (frontend/site owner). **Scout** may execute run 2.
**Tracked by:** Session 32 plan, Story 070. Follows Stories 049, 052, 054, 057, 061, 065, and 067 in the standing series.

## Summary

Standing two-run check that the live website, the repo mirror, and the release tag agree after the Session 32 docs land. No new code and no new script. The checker already exists at `scripts/verify-website-currency.sh`. This story is about **running it twice at the right moments** (heading-vs-tag before and after release) plus the deploy-mirror byte-identical checks. Session 32 is docs-only so the expected delta is small; the live-path absence observed at planning is an explicit check item, not an assumption. Expected outcome: **PASS with the live-path finding resolved by measurement**.

## Baseline measured at Session 32 planning (2026-10-16 01:10 CDT)

| Check | Value |
|---|---|
| Games section heading | "Six games, one arcade", 6 cards |
| Website What's New heading | v0.29.0 ("Cinder tells you when your save cannot be read") |
| `GAME_ORDER` rotation list | 6/6 including afterglow (`cinder, wordfire, minesweeper, simon, 2048, afterglow`) |
| Play links | 6 (`games/2048.html, games/afterglow.html, games/cinder.html, games/minesweeper.html, games/simon.html, games/wordfire.html`) |
| `sw.js` `CACHE_VERSION`, repo mirror | 7 |
| Latest tag / release | v0.29.0 |
| Open issues / open PRs | 0 / 0 |
| Live path `/home/jake/share/Flambeee/` | **Not present from this box** (ls exit 2 at 01:10 CDT; jakebot independently observed the same). Run 1 must confirm by measurement, not assume green. |

## Requirements

### 1. Run 1, pre-release

Run `scripts/verify-website-currency.sh` **before** the Session 32 docs merge.
Expected: record exact exit code and output. If it fails on the live-path absence, that is a real finding about the current state; report it, resolve by measurement, do not proceed quietly.

### 2. Run 2, post-release

After the tag exists and the release is published (resolve with `git ls-remote --tags origin` at run time, never hardcode):

- Origin's latest tag matches the live What's New heading.
- `cmp /home/jake/share/Flambeee/index.html website/index.html` is exit 0, with equal sha256 on both sides **at the absolute path**.
- All 6 game-file deploy mirrors re-synced **after** the merge, copied from the committed side, and `cmp` against `src/` is exit 0 with equal sha256.
- `sw.js` `CACHE_VERSION` agrees on both `website/sw.js` and `/home/jake/share/Flambeee/sw.js` (record the version line from both files either way). If the shell changed and this is not bumped, returning visitors keep the stale shell.

### 3. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not assume the deployed copy is stale.** `share/` is outside version control, so an edit there is unrecoverable. Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write into either.
4. Re-run `cmp`, record both sha256.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. If it reports a genuine failure, fix the thing it reports, not the checker.

### 5. Live-path check (Session 32 explicit)

The planning-measured absence of `/home/jake/share/Flambeee/` from this box is a check item: run 1 records `ls` exit code and path result; if still absent, the dev/release wave verifies the live mirror from the host that serves it rather than assuming green.

## BDD scenarios

**Scenario 1: Heading-vs-tag, run 1.**
Given the pre-release tree, when the checker runs, then the What's New heading names the entering latest tag (v0.29.0) and the run result with exit code is recorded.

**Scenario 2: Heading-vs-tag, run 2.**
Given the tag published and the live sync done, when the checker runs, then the What's New heading names the true latest tag and the run passes exit 0.

**Scenario 3: Mirrors byte-identical.**
Given the merged commit, when `cmp` runs on index, sw.js, and all 6 game files at the absolute paths, then every pair is exit 0 with equal sha256 recorded.

**Scenario 4: Play links.**
Given the live site, when the Play links are read, then 6 relative `games/*.html` links exist and every target exists.

**Scenario 5: Rotation covers all games.**
Given the live site, when `GAME_ORDER` is read, then it contains all 6 games (6/6) including afterglow.

**Scenario 6: Live-path check.**
Given the planning-measured absence of the live path from this box, when run 1 executes, then it records the `ls` result by measurement and resolves the mirror verification from the serving host instead of assuming green.

## Acceptance Criteria

**AC-1.** Run 1 executed pre-merge with exit code and output recorded, live-path result measured (Scenarios 1, 6).
**AC-2.** Run 2 passes exit 0 post-tag with heading-vs-tag match recorded (Scenario 2).
**AC-3.** `cmp` exit 0 with equal sha256 pairs for `index.html` (live vs mirror), `sw.js` (live vs mirror, version line quoted from both), and all 6 game files (deploy mirror vs `src/`) after the merge (Scenario 3).
**AC-4.** 6 Play links present, all targets exist (Scenario 4).
**AC-5.** `GAME_ORDER` 6/6 including afterglow (Scenario 5).
**AC-6.** `scripts/verify-website-currency.sh` byte-identical to its entering state. Verified with `git diff --stat` on that path, which must be empty.

## Required Proof

Both runs with their real exit codes, both `cmp` results with the sha256 pairs, the `CACHE_VERSION` line from both sw.js files, the `GAME_ORDER` line showing 6/6, the 6 Play links, the tag-versus-heading comparison, and the live-path `ls` measurement. Numbers, not adjectives. "Deployed copy refreshed" is not evidence; two equal sha256 values are.

## Non-Goals

- Any website design or content change beyond the What's New update. The What's New copy is the parent's Wave 4 step.
- Changing the checker.
- Writing to `/home/jake/share/Flambeee/` before the mirror is confirmed authoritative. See requirement 3.
