# Story 107: Check 7 predecessor-tag fix (Session 45, P1b, Required first leg)

**Status:** Ready for development (Session 45, 2026-10-29).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1b (mechanism, required first leg; must land before the v0.38.0 cut. Leads the ordering, not the session).
**Assigned to:** **Kai** (single owner; `scripts/` plus the two stale test-plan docs named below, nothing else).
**Tracked by:** Session 45 plan, Story 107. Follows Story 038 (checker), Story 100 (cache-staleness fix, shipped v0.36.1), Story 102 (HTTPS live leg, shipped v0.36.1), Story 105 (checks 6/7/8, shipped v0.37.0).
**Depends on:** None. No code dependency on Story 106 except the ordering rule: this story lands first so the v0.38.0 cut is born green.

## Summary

Fix Check 7 in `scripts/verify-website-currency.sh` so it compares `CACHE_VERSION` now against the predecessor tag (second-newest origin tag) instead of the newest tag. The current self-compare shape exits 1 on a clean tree post-tag by construction: origin latest is v0.37.0 and CACHE 13 equals 13 at v0.37.0, so the whole 1-8 run is poisoned by one tautology check. Disabling the check is explicitly out of scope. The same PR updates the stale byte-identity assertions in `docs/test-plans/041` and `046`. `scripts/` plus those two docs only; no site edits.

## jakebot decision (advisory only, recorded)

Session 45 Wave 1 priorities per jakebot (session local-7a29a7f762635dc1a941ae0ec7202a5cb509fa479491ecd0155b27589316af00, answered with live verification, proceeded on its read): point 2, P1b is a required first leg inside Session 45, done before the v0.38.0 cut. The fifth app bumps CACHE to 14; if Check 7 still compares against the tag just cut, v0.38.0 is born red on a check that cannot pass post-tag by construction. Fix: predecessor compare (resolve second-newest origin tag, compare CACHE_VERSION now against that). Preserves the property (a no-bump release still FAILs); disabling ruled out. Falsifying test: scratch clone tag cut, checker exits 0 against predecessor; simulated no-bump release still exits 1; re-run checks 6 and 8 in the same pass (shared tag-resolution block, lines 88-94).

**Citation:** `flambeee-team/session-plan.md`, Session 45 (2026-10-29), section "jakebot decisions (advisory only, recorded)".

## Why this story exists (one paragraph)

Story 105 put the CACHE rule in the script, but its Check 7 compares the working tree against the newest tag. The moment a release tag lands, that comparison is the tree against itself: same bytes, same CACHE, guaranteed FAIL. Session 45 planning verified this live (checker exits 1 on a clean tree, Check 7 FAIL, post-tag self-compare confirmed, not flaky). Story 106 bumps CACHE 13 to 14, which is exactly the change Check 7 asserts, so cutting v0.38.0 without this fix ships a red gate on day one. This story moves the comparison one tag back and proves the property still holds.

## Baseline measured at Session 45 planning (2026-10-29 01:10 CDT)

| Check | Value |
|---|---|
| Checker exit on clean tree | 1 (Check 7 FAIL, poisons the 1-8 run) |
| Origin latest tag | v0.37.0 (2026-10-28 07:59 UTC) |
| CACHE_VERSION now vs at v0.37.0 | 13 vs 13, "unchanged since v0.37.0" |
| Tag-resolution block | `scripts/verify-website-currency.sh` lines 88-94 (shared by checks 2, 6, 7) |
| Stale-doc seam | `docs/test-plans/041` and `046` still assert the checker is byte-identical to v0.19.0; Story 105 already broke that and v0.37.0 shipped it |

## Requirements

### 1. Predecessor-tag compare (the fix, bounded)

- In the shared tag-resolution block (`scripts/verify-website-currency.sh`, about lines 88-94), resolve the second-newest origin tag alongside the newest (same `git ls-remote --tags origin` source, same `vX.Y.Z` filter, same `sort -V` ordering; predecessor is the line above the tail).
- Check 7 compares `CACHE_VERSION` now against the value at the predecessor tag (`git show <predecessor>:website/sw.js`), not the newest tag. Both values print on failure, same as today, with the predecessor tag named.
- Check 6 (heading names newest tag) keeps comparing against the newest tag. Check 8 is untouched. Expected diff size is about 10 to 15 lines in the tag-resolution block.
- Disabling Check 7, skipping it post-tag, or pinning a hardcoded tag is explicitly out of scope. The property is preserved: a release that ships without a CACHE bump still FAILs (now against the predecessor, proven by the falsifying test below).

### 2. RED-then-green proof bar (falsifying test per jakebot)

All three, or the item does not merge:

1. **Green against predecessor:** in a scratch clone, cut a scratch tag on the fixed tree and show the checker exits 0 with Check 7 passing against the predecessor tag.
2. **No-bump still FAILs:** simulate a no-bump release in scratch (scratch tag with CACHE unchanged from its predecessor) and show Check 7 still exits 1 with both values printed. This is the falsification: the fix must not turn Check 7 into a rubber stamp.
3. **Checks 6 and 8 re-run green** in the same pass (they share the tag-resolution block; a shared-block edit gets a shared-block regression run).

The dev record pastes commands, exit codes, and the Check 7 plus Check 6 plus Check 8 lines for each run. Code with no falsifying run is not done.

### 3. Same-PR stale-doc update (041 plus 046)

- The same PR updates the byte-identity assertions in `docs/test-plans/041-website-currency-post-release-verification.md` and `docs/test-plans/046-website-currency-post-release-verification-test-plan.md`, which still claim the checker is byte-identical to v0.19.0. Story 105 already broke that claim and v0.37.0 shipped it, so QA would trip a false violation without this update.
- The update replaces the byte-identity assertion with the current rule: the checker carries the Story 105 checks 6/7/8 plus the Story 107 predecessor compare, and the doc asserts that rule instead of a frozen blob. No other test-plan content changes.

### 4. Scope guard (scripts plus the two docs only)

In scope: `scripts/verify-website-currency.sh` plus any fixture or harness file under `scripts/` the proof needs, plus the two test-plan docs named in requirement 3. Untouched: `website/` (no site edits, no sw.js edits, no card edits; Story 106 owns `website/sw.js`), `src/`, `games/`, the FPS probe, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`. This story never touches `website/sw.js`, so no conflict with Story 106 by construction.

### 5. Ordering rule

This story lands before the v0.38.0 cut. The release wave runs the merged checker post-merge as the cut gate; Check 7 green against the predecessor is necessary but not sufficient for the cut.

## BDD scenarios

**Scenario 1: Predecessor resolution.**
Given the fixed tag-resolution block, when the checker runs, then it resolves both the newest origin tag and the second-newest (predecessor) tag at run time from `git ls-remote --tags origin`, with nothing hardcoded, and both values are printed in the output.

**Scenario 2: Green against predecessor.**
Given a scratch clone with a scratch tag cut on the fixed tree, when the checker runs, then Check 7 passes (CACHE now differs from the predecessor value) and the exit code is 0.

**Scenario 3: No-bump release still FAILs.**
Given a simulated no-bump release in scratch (scratch tag with CACHE unchanged from its predecessor), when the checker runs, then Check 7 fails with both values printed and the exit code is non-zero.

**Scenario 4: Checks 6 and 8 regression green.**
Given the merged tree, when the checker runs, then Check 6 (heading names newest tag) and Check 8 (every app-card target precached) pass alongside the fixed Check 7 with measured values printed.

**Scenario 5: Stale-doc seam closed.**
Given the merged PR diff, when the 041 and 046 test-plan docs are inspected, then neither asserts byte-identity to v0.19.0, and both state the current checker rule (checks 6/7/8 plus predecessor compare).

**Scenario 6: Scope guard.**
Given the story diff, when it is inspected, then every changed file sits under `scripts/` or is one of the two named test-plan docs, and `website/`, `src/`, `games/`, and `dev/fps-probe/` show no diff.

## Acceptance Criteria

**AC-1.** Predecessor tag resolved at run time from origin alongside the newest tag, both printed (Scenario 1).
**AC-2.** Check 7 compares CACHE now against the predecessor tag with both values printed on failure; Check 6 still targets the newest tag (Scenarios 1-2).
**AC-3.** Scratch-clone tag-cut run recorded: command, exit 0, Check 7 passing line against the predecessor (Scenario 2).
**AC-4.** Simulated no-bump run recorded: command, non-zero exit, Check 7 failing line with both values (Scenario 3).
**AC-5.** Checks 6 and 8 re-run green in the same pass with passing lines recorded (Scenario 4).
**AC-6.** 041 and 046 byte-identity assertions updated in the same PR to the current checker rule (Scenario 5).
**AC-7.** Diff limited to `scripts/` plus the two named docs; no site edits (Scenario 6).
**AC-8.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

The tag-resolution block quoted verbatim in the dev record (before and after); predecessor and newest tag values printed; scratch tag-cut command plus exit 0 plus Check 7 passing line; no-bump simulation command plus non-zero exit plus Check 7 failing line; Check 6 plus Check 8 passing lines from the same pass; `git diff --stat` showing `scripts/` plus the two test-plan docs only. Numbers, not adjectives.

## Non-Goals

- Any edit under `website/`, including `sw.js` (Story 106 owns it).
- Disabling, skipping, or hardcoding around Check 7.
- Any change to the HTTPS live leg Story 102 installed or the Check 5 card-link logic (extend the tag block, do not rewrite neighboring checks).
- Deciding any version cut (release wave owns the cut decision and the tag).
- Touching `pending-post.txt` or any noon pipeline path.
