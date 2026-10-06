# Story 061: Website currency and deploy mirror verification, Session 29 (P3, Standing Verification)

**Status:** Ready for development (Session 29, 2026-10-06).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P3 (standing per-release verification; no product behaviour change).
**Assigned to:** **Riven** (frontend/site owner). **Scout** may execute run 2.
**Tracked by:** Session 29 plan, Story 061. Follows Stories 049, 052, 054 and 057 in the standing
series.

## Summary

Every release edits `share/Flambeee/index.html`, because that file carries the What's New section,
and the PWA shell means returning visitors can keep a stale copy. This is the standing two-run
check that the live website, the repo mirror and the release tag agree with each other after the
Story 059 release lands.

No new code and no new script. The checker already exists at `scripts/verify-website-currency.sh`.
This story is about **running it twice at the right moments**, plus the two rules that prevent data
loss and the silent-no-op failure.

## Baseline measured at Session 29 planning (09:00 to 09:10 CDT)

| Check | Value |
|---|---|
| `share/Flambeee/index.html` vs `flambeee/website/index.html` | `cmp` exit 0, byte-identical |
| `sw.js` `CACHE_VERSION`, live and mirror | `4` on both sides |
| Latest tag / release | `v0.26.0` |
| Website What's New heading | `v0.26.0: Your hero's record survives a bad save` |
| Open issues / open PRs | 0 / 0 |

Clean baseline. Run 1 should pass against this state, before Story 059's site integration lands.

## Requirements

### 1. Run 1, pre-release

Run `scripts/verify-website-currency.sh` **before** the Story 059 site-integration merge. Expected:
**PASS, exit 0.** Record the exact exit code and output. If it fails, that is a finding about the
current state; report it, do not proceed quietly.

### 2. Run 2, post-release

After the tag exists and the release is published:

- Origin's latest tag matches the live What's New heading.
- `cmp share/Flambeee/index.html flambeee/website/index.html` is exit 0, with equal sha256 on both
  sides **at the absolute path**.
- The Afterglow deploy mirror `share/Flambeee/games/afterglow.html` is re-synced **after** the
  merge, copied from the committed side, and `cmp` against `src/afterglow.html` is exit 0 with
  equal sha256.
- `sw.js` `CACHE_VERSION` bumped in **both** `flambeee/website/sw.js` and `share/Flambeee/sw.js`
  (from `4` to `5`), and the two files agree. If the shell changed and this is not bumped,
  returning visitors keep the stale shell and Afterglow never appears. This is the single most
  common way a Flambeee release appears not to have shipped.

### 3. The `cmp` rule, which is the whole point of the mirror check

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not assume
the deployed copy is stale.** On 2026-09-29 the repo mirror was already correct and the deployed
copy was the stale one. `share/` is outside version control, so an edit there is unrecoverable.
Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write into
   either.
4. Re-run `cmp`, record both sha256.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. Sessions 24, 26, 27 and 28
all kept it unmodified. If it reports a genuine failure, fix the thing it reports, not the checker.

## Acceptance Criteria

**AC-1.** Run 1 passes, exit 0, before the Story 059 site merge, output recorded.

**AC-2.** Run 2 passes, exit 0, after the tag and release exist.

**AC-3.** `cmp` on `share/Flambeee/index.html` vs `flambeee/website/index.html` is exit 0 in run 2,
both sha256 recorded and equal.

**AC-4.** `cmp` on `share/Flambeee/games/afterglow.html` vs `src/afterglow.html` is exit 0 after
the merge, both sha256 recorded and equal.

**AC-5.** `CACHE_VERSION` is incremented from `4` to `5` on **both** `website/sw.js` and
`share/Flambeee/sw.js`, and the two files agree.

**AC-6.** The live What's New heading names `v0.27.0`, and origin's latest tag matches it.

**AC-7.** `scripts/verify-website-currency.sh` is byte-identical to its v0.26.0 state. Verified
with `git diff --stat` on that path, which must be empty.

## Required Proof

Both runs with their real exit codes, both `cmp` results with the sha256 pairs, the `CACHE_VERSION`
line from both files, and the tag-versus-heading comparison. Numbers, not adjectives. "Deployed
copy refreshed" is not evidence; two equal sha256 values are.

## Non-Goals

- Any website design or content change. The What's New copy is the parent's Wave 4 step.
- Changing the checker.
- Writing to `share/Flambeee/` before the mirror is confirmed authoritative. See requirement 3.
