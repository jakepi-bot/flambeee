# Story 102: Website currency and deploy mirror verification, Session 43 (P3, Standing Verification)

**Status:** Ready for development (Session 43, 2026-10-27).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P3 (standing per-release verification; no product behaviour change; no new release implied).
**Assigned to:** **Riven** (frontend/site owner). Run 2 is conditional on the release wave's cut decision (see section 2).
**Tracked by:** Session 43 plan, Story 102. Follows Stories 049, 052, 054, 057, 061, 065, 067, 070, 073, 076, 078, 080, 084, 087, 090, 093, 095, and 099 in the standing series. Modeled on Story 099.
**Depends on:** None. No code dependency. No dependency on Stories 100 or 101 except that run 1 measures the tree they have not yet touched.

## Summary

Standing check that the repo mirror and the release tag agree after the Session 43 stories land, with the live leg rewritten: the absent local path `/home/jake/share/Flambeee/` is retired as a check item, replaced by an HTTPS fetch-and-compare against the repo mirror, verified working at planning. Repo-side facts are re-measured at run time, never assumed. The checker edit that installs the HTTPS leg is this story's own recorded change, not drift.

## jakebot decision (advisory only, recorded)

Session 43 Wave 1 priorities per jakebot (session local-73eab48a611ea40ed30626c7f362c9b89726a8066f4c59c571213edeade85142, proceeded on its read): P3 rewritten so it can pass. The live leg becomes HTTPS fetch-and-compare (verified working, sha256 match below); the absent local path stops being measured a 17th time. Declared N/A-by-absence is no longer accepted either; the HTTPS leg replaces it.

**Citation:** `flambeee-team/session-plan.md`, Session 43 (2026-10-27), section "jakebot decisions (advisory only, recorded)".

## Baseline measured at Session 43 planning (2026-10-27 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.36.0 ("Timer stops eating your input") |
| Latest tag / release | v0.36.0 Timer stops eating your input (2026-10-26 07:58 UTC) |
| Heading vs tag | MATCH |
| Open issues / open PRs | 0 / 0 |
| Play links | measured at run time, not assumed here (8 expected: 6 game plus 2 Apps) |
| `GAME_ORDER` rotation list | measured at run time, not assumed here (6/6 including afterglow expected) |
| Apps entries | `website/apps/index.html` present (Day Pad) plus `website/apps/timer.html` present (timer card links `apps/timer.html`) |
| `sw.js` `CACHE_VERSION`, repo mirror | 11 (measured at planning; run 1 must read the line, not assume it) |
| Live leg (new) | `curl https://flambeee.com/` returns 200; served index.html byte-identical to the repo mirror, sha256 `04a6bbbc85c9905e2451299de8e24bcb1e5dfa962707cef7d4fcf716a1597b9f` both sides (measured 01:10) |
| Live path `/home/jake/share/Flambeee/` | **Retired as a check item** (absent from this box 16 sessions running). Not re-measured; run 1 does not `ls` it. |

## Requirements

### 1. Run 1, pre-merge

Run `scripts/verify-website-currency.sh` **before** the Session 43 stories merge. Expected: record exact exit code and output. Repo-side facts (heading vs tag, Play links, GAME_ORDER, CACHE_VERSION, timer card) are each measured at run time and recorded with values, never assumed from the baseline table above.

### 2. Run 2, conditional on the release wave

If the release wave cuts a version on the back of Story 100 (patch candidate v0.36.1) or Story 101, run 2 verifies post-tag: heading names the new tag, mirror still byte-identical, CACHE_VERSION reads the bumped value (12). If no cut, the dev record states "Run 2: N/A, no release" and stops. This story does not decide the cut; the release wave does.

### 3. The live leg (rewritten this session)

The checker fetches `https://flambeee.com/` and compares the served index.html against the repo mirror (`website/index.html`), recording the HTTP status plus sha256 of both sides. The planning measurement (200, sha256 `04a6bbbc85c9905e2451299de8e24bcb1e5dfa962707cef7d4fcf716a1597b9f` both sides) is the baseline, not the result; run 1 re-fetches and re-records. On mismatch, the `cmp` rule in section 4 applies before any copy.

### 4. The `cmp` rule, which is the whole point of the mirror check

When a comparison between the served copy and the repo mirror reports a difference, **do not assume the served copy is stale.** Procedure, in order:

1. `git log --oneline -3 -- website/index.html` and `git status --short website/index.html`.
2. `git show HEAD:website/index.html | grep <version-heading>`.
3. Only then copy. Restore the stale side **from** the committed side. Never hand-write into either.
4. Re-run the comparison, record both sha256.

### 5. The checker edit is this story's own recorded change

Unlike every prior story in this series, `scripts/verify-website-currency.sh` **is** modified by this story: the absent-local-path item is removed and the HTTPS fetch-and-compare leg is installed. The diff on that path must show exactly that change and nothing else; the dev record quotes the new live-leg block verbatim. This edit is deliberate and recorded, not drift. Any future story that touches the checker again must say so in its own text.

### 6. Noon-tail note (not a wave, not this story)

The 082 matrix plus mirror checker re-run belongs to the tail (Scout or parent), not to this story. If either re-run goes non-zero it becomes the session and bumps P1/P2. This story does not execute or record the tail; it only notes the interaction so currency findings are not confused with pipeline findings.

## BDD scenarios

**Scenario 1: Heading-vs-tag, run 1.**
Given the pre-merge tree, when the checker runs, then the What's New heading names the entering latest tag (v0.36.0 vs tag v0.36.0 MATCH) and the run result with exit code is recorded.

**Scenario 2: Run 2 conditional.**
Given the release wave's cut decision, when run 2 comes due, then either the new heading-vs-tag plus mirror plus CACHE values are recorded (cut happened) or the dev record states "Run 2: N/A, no release" with no tag resolution and no sync.

**Scenario 3: Play links measured.**
Given the site, when the Play links are read at run time, then the count plus targets are recorded (8 relative links expected: 6 game plus 2 Apps) and every target exists.

**Scenario 4: Rotation plus Apps entries measured.**
Given the site, when `GAME_ORDER` is read at run time, then coverage is recorded (6/6 including afterglow expected); the Day Pad entry (`website/apps/index.html`) and the timer entry (`website/apps/timer.html`, card links `apps/timer.html`) are both present.

**Scenario 5: CACHE_VERSION measured.**
Given the repo `website/sw.js`, when the version line is read pre-merge, then the value is recorded as measured (11 at planning), with no assumption from this doc.

**Scenario 6: HTTPS live leg.**
Given network access, when the checker fetches the live site, then the HTTP status plus served sha256 plus mirror sha256 are recorded, and MATCH/MISMATCH is stated from the measured bytes, not from the planning baseline.

**Scenario 7: Absent path retired.**
Given the story diff and the run-1 record, when they are inspected, then neither references an `ls` of `/home/jake/share/Flambeee/` as a check item.

**Scenario 8: Checker diff is exactly the live-leg rewrite.**
Given the story diff, when `git diff --stat` on `scripts/verify-website-currency.sh` is read, then it is non-empty and shows only the removal of the absent-path item plus the addition of the HTTPS leg.

## Acceptance Criteria

**AC-1.** Run 1 executed pre-merge with exit code and output recorded (Scenarios 1, 6).
**AC-2.** Run 2 recorded as conditional: new-tag values after a cut, or "Run 2: N/A, no release" (Scenario 2).
**AC-3.** Play-link count plus targets measured at run time with every target existing (Scenario 3).
**AC-4.** `GAME_ORDER` coverage measured at run time; Day Pad and timer Apps entries both present with the timer card target recorded (Scenario 4).
**AC-5.** `CACHE_VERSION` value recorded as measured from the repo sw.js, not assumed (Scenario 5).
**AC-6.** HTTPS live leg recorded with status plus both sha256 plus MATCH/MISMATCH from measured bytes (Scenario 6).
**AC-7.** No `ls` of the retired local path as a check item in diff or record (Scenario 7).
**AC-8.** Checker diff shows exactly the live-leg rewrite, quoted verbatim in the dev record (Scenario 8).
**AC-9.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Run 1 with real exit code; the `CACHE_VERSION` line from the repo sw.js; the `GAME_ORDER` line; the Play-link count plus targets; the tag-versus-heading comparison; the timer-card link target; the HTTPS fetch record (status, both sha256, MATCH/MISMATCH); run 2 values or the N/A statement; the checker diff. Numbers, not adjectives.

## Non-Goals

- Any website design or content change beyond a parent-owned What's New update. The What's New copy is not this story's step.
- Restoring the absent-path check item.
- Writing to any deploy path before the mirror is confirmed authoritative. See requirement 4.
- Advancing the FPS slice or scheduling a gamepad run on this box. The gate stays deferred until a pad exists on the named rig.
- Deciding any version cut or running any post-tag verification beyond the conditional run 2.
