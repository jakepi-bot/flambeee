# Story 113: Checker live leg to post-deploy-only (Session 48, P2, mechanism)

**Status:** Ready for development (Session 48, 2026-11-01).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (mechanism; rides along, justifies nothing user-visible on its own).
**Assigned to:** **Kai** (single code owner per the Story 048 protocol, named before the wave starts; holds `scripts/` only). No shared ownership.
**Tracked by:** Session 48 plan, Story 113. Follows Story 038 (checker shipped), Story 041 (two-run release step), Story 102 (live leg rewritten to HTTPS fetch-and-compare), Story 105 (Checks 6/7/8), Story 107 (Check 7 predecessor compare).
**Depends on:** The shipped checker at `scripts/verify-website-currency.sh`. No code dependency on Story 112 except the no-conflict note below: Story 112 (Riven) owns the `website/sw.js` CACHE line and Kai never touches `website/`, so there is no sw.js conflict by construction.

## Summary

Convert the served-vs-mirror live leg (Check 1) of `scripts/verify-website-currency.sh` to post-deploy-only. Today Check 1 compares the live served copy against the repo mirror on every run, so every pre-merge run FAILs by construction: the live copy cannot hold the new bits until the Caddy sync lands after release. Twenty sessions of by-construction FAIL have been explained away each time, which means a FAIL no longer means anything. After this story, default pre-merge runs skip-or-note the live leg (printed NOTE, never PASS, never FAIL, run exit unaffected) and an explicit post-deploy mode enforces it exactly as today. Checks 2 through 8 keep byte-identical behavior. `scripts/` only; zero lines in `website/`, `src/`, `apps/`, `games/`.

## jakebot decision (advisory only, recorded)

Session 48 Wave 1 priorities per jakebot (session local-4fe265507574af9c9c587f97844a2ee0c668f23aa8a978b0f47bc54e5213a46f, proceeded on its read): P2 offered and accepted, convert the live served-vs-mirror check to post-deploy-only so its FAIL means something again (20 sessions of by-construction FAIL explained away each time).

**Citation:** `flambeee-team/session-plan.md`, Session 48 (2026-11-01), sections "jakebot decision (advisory only, recorded)" and "Priorities (in order)".

## Baseline measured at Session 48 planning (2026-11-01 01:10 CDT)

| Check | Value |
|---|---|
| Checker path | `scripts/verify-website-currency.sh` (Stories 102/105/107 shape: Check 1 served-vs-mirror, Checks 2-5 site checks, Checks 6-8 Story 105 assertions) |
| Live leg today | Check 1 fetches `${FLAMBEEE_LIVE_URL:-https://flambeee.com/}` and FAILs the run on served-vs-mirror mismatch |
| Pre-merge expectation today | FAIL by construction (live copy unsynced until the post-release Caddy sync) |
| Newest tag | v0.40.0; `CACHE_VERSION` 16 (Story 112 owns the 16 to 17 line; this story never touches it) |

## Requirements

### 1. Owner named before the wave (Story 048)

Kai is the single code owner for this story, holding `scripts/verify-website-currency.sh` only. Riven holds Story 112. The two stories share no file, so overlap is impossible by construction.

### 2. Post-deploy-only live leg (exactly one mechanism change)

- Default (pre-merge) runs skip-or-note Check 1: the script still fetches the live copy when reachable, prints one `NOTE:` line naming the served and mirror sha256 plus the reason (pre-merge run, live copy unsyncable by construction), and the live leg contributes neither a PASS nor a FAIL. The run exit code is decided by Checks 2 through 8 only.
- Explicit post-deploy mode enforces Check 1 exactly as today: served-vs-mirror byte compare, PASS on match, FAIL plus non-zero exit on mismatch. The opt-in mechanism (env var or flag) is named in the dev record before the wave; the default stays pre-merge-safe with no caller change.
- Unreachable live copy in default mode is a NOTE, not a FAIL. Unreachable live copy in post-deploy mode FAILs exactly as today.
- Suggested interface (dev may choose an equal shape and record it): `FLAMBEEE_POST_DEPLOY=1 scripts/verify-website-currency.sh` enforces Check 1; unset skips-or-notes it.

### 3. Checker otherwise frozen

- Checks 2 through 8 keep byte-identical behavior: same tag resolution (`git ls-remote --tags origin`, newest plus predecessor), same heading, summary, anchor, link, and precache assertions, same output lines apart from the Check 1 NOTE.
- No new check, no removed check, no renumbering. Check 1 keeps its number and its post-deploy behavior so release-wave Run 2 reads the same lines it always has.
- Zero lines changed under `website/`, `src/`, `apps/`, `games/`, or any scheduled, noon, or state path.

### 4. Scope guard

In scope: `scripts/verify-website-currency.sh` (the Check 1 mode change only). Untouched: `website/` (all of it, including `sw.js`), `src/`, `apps/`, `games/`, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, every story-112 surface, the FPS probe.

### 5. Proof bar

All five, or the change does not ship:

1. RED on the current tree: the current checker run pre-merge exits 1 by construction (Check 1 served-vs-mirror MISMATCH recorded with both sha256). Command, exit code, and per-check lines recorded.
2. GREEN default mode: the modified checker run pre-merge against the same tree exits 0 with repo-side Checks 2 through 8 genuinely green, and Check 1 prints its NOTE line (never PASS, never FAIL).
3. GREEN falsifying control: post-deploy mode against a served copy that differs from the mirror exits 1 with Check 1 FAIL named (for example a scratch served fixture, or the real pre-sync live copy; recorded with values).
4. GREEN positive control: post-deploy mode against byte-identical served and mirror copies exits 0 with Check 1 PASS.
5. Freeze proof: `git diff --stat` outside `scripts/` is empty (zero lines in `website/`, `src/`, `apps/`, `games/`), and Checks 2 through 8 output lines match the pre-change run check-for-check apart from Check 1.

Release implication, fixed: this story rides along and justifies no cut on its own. The v0.41.0 decision belongs to Story 112 green plus the release wave.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Kai holds `scripts/verify-website-currency.sh` as single owner, and the dev record states the name plus the chosen opt-in mechanism.

**Scenario 2: RED, current checker pre-merge.**
Given the current tree, when the unmodified checker runs pre-merge, then it exits 1 with Check 1 served-vs-mirror MISMATCH (both sha256 recorded), which is the by-construction FAIL this story retires.

**Scenario 3: Default mode skips-or-notes.**
Given the modified checker, when it runs pre-merge in default mode, then Check 1 prints one `NOTE:` line with both sha256 and the pre-merge reason, contributes no PASS and no FAIL, and the exit code is decided by Checks 2 through 8.

**Scenario 4: Post-deploy mode enforces.**
Given the modified checker, when it runs in explicit post-deploy mode, then Check 1 compares served-vs-mirror bytes exactly as today, printing PASS on match and FAIL plus non-zero exit on mismatch.

**Scenario 5: Falsifying control.**
Given post-deploy mode, when the served copy differs from the mirror, then the run exits 1 with Check 1 FAIL named.

**Scenario 6: Positive control.**
Given post-deploy mode, when the served and mirror copies are byte-identical, then the run exits 0 with Check 1 PASS.

**Scenario 7: Freeze.**
Given the scope guard, when `git diff --stat` is inspected, then no path outside `scripts/` changed, and Checks 2 through 8 print the same lines as the pre-change run apart from Check 1.

## Acceptance Criteria

**AC-1.** Single code owner Kai named before the wave per Story 048, opt-in mechanism recorded (Scenario 1).
**AC-2.** RED recorded: current checker exits 1 pre-merge on Check 1 MISMATCH with both sha256 (Scenario 2).
**AC-3.** Default pre-merge run exits 0 with repo-side checks green and Check 1 as NOTE only (Scenario 3).
**AC-4.** Post-deploy mode enforces Check 1 exactly as today (Scenario 4).
**AC-5.** Falsifying control exits 1 on differing bytes (Scenario 5).
**AC-6.** Positive control exits 0 on identical bytes (Scenario 6).
**AC-7.** Freeze held: zero lines outside `scripts/`, Checks 2 through 8 unchanged (Scenario 7).
**AC-8.** This story claims no cut; the v0.41.0 decision stays with Story 112 green plus the release wave.
**AC-9.** Script copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

RED run (command, exit 1, Check 1 MISMATCH with both sha256); GREEN default run (command, exit 0, NOTE line verbatim, Checks 2 through 8 lines); falsifying control (exit 1, Check 1 FAIL named); positive control (exit 0, Check 1 PASS); `git diff --stat` showing `scripts/` only; the opt-in mechanism name verbatim. Numbers, not adjectives.

## Non-Goals

- Any change under `website/`, `src/`, `apps/`, or `games/` (zero lines; the CACHE line belongs to Story 112).
- A new check, a removed check, renumbering, or any behavior change in Checks 2 through 8.
- Making the default run fetch-or-fail on the live copy in any new way; default mode never FAILs on the live leg.
- A currency one-liner rerun (standing release-wave leg, noted in the handoff, nobody re-proves it here).
- Cutting a version (release wave owns the cut decision and the tag).
