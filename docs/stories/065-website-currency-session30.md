# Story 065: Website currency and deploy mirror verification, Session 30 (P2, Standing Verification)

**Status:** Ready for development (Session 30, 2026-10-11).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (standing per-release verification plus three measured defects; no new product behaviour).
**Assigned to:** **Riven** (frontend/site owner). **Scout** may execute run 2.
**Tracked by:** Session 30 plan, Story 065. Follows Stories 049, 052, 054, 057, and 061 in the
standing series.

## Summary

The live website (`/home/jake/share/Flambeee/index.html`, measured 2026-10-11) has three real
currency/consistency defects, none invented. This story fixes those three and runs the standard
two-run currency check (heading-vs-tag before and after release) plus the deploy-mirror
byte-identical checks, so the Story 064 release lands on a current site.

No new code and no new script. The checker already exists at
`scripts/verify-website-currency.sh`. This story is about **fixing the three defects and
running the checker twice at the right moments**, plus the two rules that prevent data loss
and the silent-no-op failure.

## Baseline measured at Session 30 planning (2026-10-11, CDT)

| Check | Value |
|---|---|
| Games section heading | "Five games, one arcade" (WRONG: 6 cards on the page) |
| Website What's New heading | `v0.27.0` (BEHIND: live release is v0.27.1 hotfix, 2026-10-07) |
| `GAME_ORDER` rotation list | 5 games (`cinder, wordfire, minesweeper, simon, 2048`); `afterglow` MISSING |
| Latest tag / release | `v0.27.1` |
| Open issues / open PRs | 0 / 0 |

## Requirements

### 1. Defect 1: stale game count

- Games section heading says "Five games, one arcade" but the page carries 6 game cards
  (Afterglow added Session 29; the About stat row already says 6).
- Fix: heading must name **six** games. Exact copy at dev discretion; the number must match
  the card count. Verify the About stat row still agrees.

### 2. Defect 2: What's New behind the release

- Heading still `v0.27.0`; the live release is **v0.27.1** (hotfix, 2026-10-07). One release
  of drift at session start.
- Run 1 records this entering state honestly. Run 2 (post-release) must name the true
  latest tag at that time (expected v0.28.0 if the dev wave ships it; resolve with
  `git ls-remote --tags origin` at run time, never hardcode). Summary must describe only
  what the release actually shipped; no invented features.

### 3. Defect 3: Game of the Week never features Afterglow

- `GAME_ORDER` lists 5 games; `afterglow` is missing, so the rotation can never feature the
  newest game.
- Fix: add `afterglow` to `GAME_ORDER` so the rotation covers all 6 games. No other
  rotation-semantics change.

### 4. Run 1, pre-release

Run `scripts/verify-website-currency.sh` **before** the Story 064 site-integration merge.
Record the exact exit code and output. Run 1 is expected to surface defects 1-3 above;
that is a finding about the current state, not a checker bug. Report it, do not proceed
quietly, do not fix the checker.

### 5. Run 2, post-release

After the tag exists and the release is published:

- Origin's latest tag matches the live What's New heading.
- `cmp /home/jake/share/Flambeee/index.html flambeee/website/index.html` is exit 0, with
  equal sha256 on both sides **at the absolute path**.
- The Afterglow deploy mirror `/home/jake/share/Flambeee/games/afterglow.html` is re-synced
  **after** the merge, copied from the committed side, and `cmp` against
  `src/afterglow.html` is exit 0 with equal sha256.
- `sw.js` `CACHE_VERSION` bumped in **both** `flambeee/website/sw.js` and
  `/home/jake/share/Flambeee/sw.js` **iff** the shell changed (if unchanged, both sides
  must still agree; record the version line from both files either way). If the shell
  changed and this is not bumped, returning visitors keep the stale shell and the release
  reads as a no-op.

### 6. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not
assume the deployed copy is stale.** `share/` is outside version control, so an edit there
is unrecoverable. Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write
   into either.
4. Re-run `cmp`, record both sha256.

### 7. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. If it reports a
genuine failure, fix the thing it reports, not the checker.

## BDD scenarios

**Scenario 1: Game count agrees.**
Given the fixed site, when the games section heading and the card count are read, then the
heading names six and six cards exist, and the About stat row agrees.

**Scenario 2: What's New names the release.**
Given the release tag exists, when the What's New heading is read, then it names the true
latest tag (resolved at run time) with an accurate summary of what that release shipped.

**Scenario 3: Rotation covers Afterglow.**
Given the fixed site, when `GAME_ORDER` is read, then it contains all 6 games including
`afterglow`, and the Game of the Week banner can feature Afterglow.

**Scenario 4: Run 1 recorded.**
Given the pre-release tree, when the checker runs, then its exit code and full output are
recorded in the release chain (a defect finding is reported, not hidden).

**Scenario 5: Run 2 green.**
Given the tag published and the live sync done, when the checker runs, then it passes
exit 0 and the heading-vs-tag comparison agrees.

**Scenario 6: Mirrors byte-identical.**
Given the merged commit, when `cmp` runs on index, sw.js, and game files at the absolute
paths, then every pair is exit 0 with equal sha256 recorded.

## Acceptance Criteria

**AC-1.** Games heading names six; 6 cards present; About stat row agrees (Scenario 1;
defect 1 fixed).

**AC-2.** Run 2 What's New heading names the true latest tag with an accurate summary; no
invented features (Scenario 2; defect 2 fixed).

**AC-3.** `GAME_ORDER` contains all 6 games including `afterglow` (Scenario 3; defect 3 fixed).

**AC-4.** Run 1 exit code and output recorded before the site merge (Scenario 4).

**AC-5.** Run 2 exit 0 after tag + release + live sync; heading-vs-tag match recorded
(Scenario 5).

**AC-6.** `cmp` exit 0 with equal sha256 pairs for `index.html` (live vs mirror),
`sw.js` (live vs mirror, version line quoted from both), and `afterglow.html`
(deploy mirror vs `src/`) after the merge (Scenario 6).

**AC-7.** `scripts/verify-website-currency.sh` byte-identical to its entering state.
Verified with `git diff --stat` on that path, which must be empty.

## Required Proof

Both runs with their real exit codes, both `cmp` results with the sha256 pairs, the
`CACHE_VERSION` line from both sw.js files, the `GAME_ORDER` line showing `afterglow`,
and the tag-versus-heading comparison. Numbers, not adjectives. "Deployed copy
refreshed" is not evidence; two equal sha256 values are.

## Non-Goals

- Any website design or content change beyond defects 1-3 and the What's New update. The
  What's New copy is the parent's Wave 4 step.
- Changing the checker.
- Writing to `/home/jake/share/Flambeee/` before the mirror is confirmed authoritative.
  See requirement 6.
