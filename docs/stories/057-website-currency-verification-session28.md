# Story 057: Website Currency and Deploy Mirror Verification, Session 28 (P2, Standing Verification)

**Status:** Ready for development (Session 28, 2026-10-04).
**Author:** Parent (written directly; see Story 056's author note for why).
**Priority:** P2 (standing per-release verification; no product behavior change).
**Assigned to:** **Kai**, or the parent if no worker reports in. **Scout** may execute run 2.
**Tracked by:** Session 28 plan, Story 057. Follows Stories 049, 052 and 054 in the standing series.

## Summary

Every release edits `share/Flambeee/index.html`, because that file carries the What's New
section, and the PWA shell means returning visitors can keep a stale copy. This story is the
standing two-run check that the live website, the repo mirror and the release tag agree with
each other after the release lands.

There is no new code in this story and no new script. The checker already exists at
`scripts/verify-website-currency.sh`. This story is about **running it twice at the right
moments** and about the one rule that prevents data loss.

## Baseline measured at Session 28 planning (09:13-09:20 CDT)

| Check | Value |
|---|---|
| `share/Flambeee/index.html` vs `flambeee/website/index.html` | `cmp` exit 0, byte-identical |
| `share/Flambeee/games/cinder.html` vs `flambeee/src/cinder.html` | `cmp` exit 0, byte-identical |
| `sw.js` CACHE_VERSION, live and mirror | `3` on both sides |
| Latest tag / release | `v0.25.0` |
| Website What's New heading | `v0.25.0: Cinder reads a damaged save without arguing with it` |
| Open issues / open PRs | 0 / 0 |

Clean baseline. Run 1 should pass against this state, before Story 056's fix lands.

## Requirements

### 1. Run 1, pre-release

Run `scripts/verify-website-currency.sh` **before** the Story 056 merge. Expected: **PASS, exit
0**. Record the exact exit code and output.

If run 1 fails, that is a finding about the current state, not a reason to proceed quietly. Report
it and fix it before continuing.

### 2. The `cmp` rule, which is the whole point of this story

When a `cmp` between the deployed copy and the repo mirror reports a difference, **do not assume
the deployed copy is stale.** On 2026-09-29 the mirror was already correct and the deployed copy
was the stale one. An agent that edited the deployed file first had to revert, and since `share/`
sits **outside** version control, that revert was only possible because the correct version was
still committed.

Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`. Is
   the mirror committed, clean, and carrying the new content?
2. `git show HEAD:website/index.html | grep <version-heading>`. Confirm which version the
   committed content actually names, rather than inferring it from file mtimes.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write new
   content into either file.
4. Re-run `cmp` and record the sha256 of both copies.

### 3. Run 2, post-release

After the tag exists and the release is published:

- Origin's latest tag matches the live What's New heading.
- `cmp share/Flambeee/index.html flambeee/website/index.html` is exit 0, with equal sha256 on
  both sides **at the absolute path**.
- The Cinder deploy mirror is re-synced **after** the merge, copied from the committed side.
- `sw.js` `CACHE_VERSION` bumped in **both** `flambeee/website/sw.js` and
  `share/Flambeee/sw.js`, currently `3` on both sides. If the shell changed and this is not
  bumped, returning visitors keep the stale shell and see the old What's New indefinitely. This
  is the single most common way a Flambeee release appears not to have shipped.

### 4. The checker is frozen

`scripts/verify-website-currency.sh` is **not** modified by this story. Sessions 24, 26 and 27 all
kept it unmodified. If it reports a genuine failure, fix the thing it is reporting, not the checker.

## Acceptance Criteria

**AC-1.** Run 1 passes, exit 0, before the Story 056 merge, with the output recorded.

**AC-2.** Run 2 passes, exit 0, after the tag and release exist.

**AC-3.** `cmp` on `share/Flambeee/index.html` vs `flambeee/website/index.html` is exit 0 in run 2,
with both sha256 values recorded and equal.

**AC-4.** `cmp` on `share/Flambeee/games/cinder.html` vs `flambeee/src/cinder.html` is exit 0
after the Story 056 merge, both sha256 values recorded and equal.

**AC-5.** `CACHE_VERSION` is incremented from `3` on **both** `website/sw.js` and
`share/Flambeee/sw.js`, and the two files agree.

**AC-6.** The live What's New heading names the new version, and origin's latest tag matches it.

**AC-7.** `scripts/verify-website-currency.sh` is byte-identical to its v0.25.0 state. Verified
with `git diff --stat` on that path, which must be empty.

## Required Proof

Both runs with their real exit codes, both `cmp` results with the sha256 pairs, the
`CACHE_VERSION` line from both files, and the tag-versus-heading comparison. Numbers, not
adjectives. "Deployed copy refreshed" is not evidence; two equal sha256 values are.

## Non-Goals

- Any website design or content change. The website's direction is a standing session
  consideration, not this story's job.
- Changing the checker.
- Writing to `share/Flambeee/` before the mirror is confirmed authoritative. See requirement 2.