# Story 157: LIGHTFARE proof harness (Session 70, P1b, tooling)

**Status:** Ready for development (Session 70, 2026-11-23).
**Author:** Quinn, Business Analyst.
**Priority:** P1b (tooling, zero website bytes; non-blocking for v0.57.0).
**Assigned to:** **Kai**, sole code owner. File: `dev/lightfare-proof.py` only. Zero website bytes.
**Base commit:** `23674a2` (main, v0.56.0 released).
**Scope:** `dev/lightfare-proof.py` only: static BFS plus cost-sequence plus wrong-turn-trial legs and browser legs on both viewports. No game file, no `website/` file, no `scripts/` file, no doc file in this story.
**Design contract:** `flambeee-team/design-handoff.md`, Story 157 sections 1 through 6. Design-owned observable criteria live in contract section 5 and are mapped here one for one.
**Non-blocking rule:** if this harness is not green by the release gate, v0.57.0 still ships on Stories 155/156 and the harness defers with a note (tooling never holds a user-visible cut).

## Summary

Story 155 adds the LIGHTFARE game; this story is the durable instrument for it. The harness proves the balance evidence before blessing anything: the five shipped layout strings BFS to exactly 8, 10, 12, 14, 16; the look-cost sequence reads 1, 2, 4, 8 against budget 15 with the 5th look refused; 250 seeded wrong-turn trials (50 per level, seed = levelIndex * 1000 + t) all complete within 80 moves with median looks at par (1, 1, 2, 2, 3) and no trial above 4 looks; and the browser legs confirm counting (Start +1, LOSE-retry +0, LEVELCLEAR-advance +0, reload keeps), the 4-look spend-to-0 with refused 5th and a still-completable level, storage probes matching, corrupt seeds sanitizing to 0, blocked storage staying silent, the touch-pad path on the mobile viewport, and zero page-attributable console errors on both viewports. The Story 152 narrowing discipline (SKIPPED plus exit 3, FAIL dominates SKIP, RED anchor exit 2) applies unchanged, and a green run against a one-wall-drifted layout is a harness defect, not a pass.

## Baseline measured at Session 70 planning (Wave 1, 2026-11-23)

| Check | Value |
|---|---|
| Base commit | `23674a2` (main, v0.56.0) |
| Harness file | `dev/lightfare-proof.py` does not exist (new file) |
| Game file on base | absent: no `website/games/lightfare.html` (RED anchor must fire here) |
| Expected BFS lengths | [8, 10, 12, 14, 16] moves, exact |
| Trials | 50 per level, seed `L*1000+t`, t 0..49, L 1..5; wrong-turn probability 0.25 per junction |
| Trial thresholds | 50/50 completions within 80 moves per level; median looks <= par [1,1,2,2,3]; max looks <= 4 |
| Narrowing discipline (Story 152) | each flag prints `SKIPPED: <what> (reason: <flag>)` and exits 3; FAIL dominates SKIP; RED anchor (game file or read absent) exits 2 |
| Viewports | 1280x800 and 375x667, real input on fresh profiles |
| Browser port | new, no clash with 8932 (`--port=` override) |

## Functional requirements

FR-1 (contract section 1, static legs). Extract the 5 layout strings from the shipped game file and BFS each: lengths must read exactly [8, 10, 12, 14, 16]. Check the cost sequence [1, 2, 4, 8], partial spends [1, 3, 7, 15], budget 15, and the unaffordable-5th-look refusal. Exact match or FAIL.

FR-2 (contract section 1, trial legs). Wrong-turn trials: an agent follows the BFS path but takes a random legal wrong step with p = 0.25 per junction (seeded PRNG, seed = levelIndex * 1000 + t, t = 0..49, 50 trials per level). It may look only when its remembered snapshot contradicts the halo, and it banks the BFS remainder after each look. Pass thresholds: 50/50 trials complete within 80 moves on every level; median looks per level <= par [1, 1, 2, 2, 3]; no trial uses more than 4 looks. Any breach is FAIL.

FR-3 (contract section 1, browser legs). Both viewports (1280x800 and 375x667), real input on fresh profiles, in this order:

```
fresh 0/0 -> Start 1 -> reload keeps 1 -> clear L1, advance no increment
  -> exhaust moves to LOSE, retry no increment, same level, light 15, bank kept
  -> 4 looks spend to 0, 5th refused with verbatim line, level still completable
  -> storage-probe match (localStorage plays/best == probe), corrupt seeds to 0, blocked storage silent
  -> touch pad path on mobile viewport: pad moves, LOOK button looks
  -> zero page-attributable console errors both viewports
```

FR-4 (contract section 1-2, exit discipline). Harness states: `RED-absent (exit 2) | FAIL (exit 1) | PASS (exit 0) | SKIP-narrowed (exit 3)`. CLI flags keep the Story 152 discipline: `--sim-only`, `--viewport=desktop|mobile`, `--port=N`; each narrowing flag prints `SKIPPED: <what> (reason: <flag>)` in argv order, exit 3 when all executed checks pass; FAIL dominates SKIP; invalid flag values are FAILs. RED anchor (game file absent) exits 2. `matchAssertion: JSON.parse(localStorage['flambeee-lightfare-plays']) == probe.plays()`, same for best.

FR-5 (contract section 4, mutation control). Run the static checks against a one-wall-drifted layout and require a length FAIL, proving the check is not tautological. A green-on-drift run is a harness FAIL: rewrite the check, never waive it.

FR-6 (contract section 3, tuning). Harness constants honored exactly: expected BFS lengths [8, 10, 12, 14, 16]; TRIALS_PER_LEVEL 50; trial seed schedule L*1000+t; WRONG_TURN_P 0.25; viewports exactly 1280x800 and 375x667; browser port new with no clash. Key-vs-click degradation prints a loud `FALLBACK` line per step, never debug-gated (Story 152 discipline). Playwright missing or a bad port is a named CHECK FAIL, exit 1; never stay green.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in contract section 5; AC-1 through AC-5 map them directly. AC-6 onward pin the structural requirements.

1. Given the pre-155 tree, when the harness runs, then it exits 2 (RED anchor: no target, no blessing a counterless tree). (design 5.1; FR-4)
2. Given the post-155 tree, when the static legs run, then BFS lengths read exactly 8, 10, 12, 14, 16 and the cost sequence reads 1, 2, 4, 8 against 15. (design 5.2; FR-1)
3. Given a fresh profile, when Start is pressed, then plays reads 1; LOSE-retry and LEVELCLEAR-advance never change it on either viewport. (design 5.3; FR-3)
4. Given 4 looks spent, when a 5th look is pressed, then the refusal line shows, light stays 0, and the level remains completable. (design 5.4; FR-3)
5. Given narrowing flags with all executed checks green, when the run ends, then it prints `SKIPPED:` and exits 3; any CHECK FAIL with the same flags exits 1. (design 5.5; FR-4)
6. Given the trial legs, when all 250 trials run, then every level shows 50/50 completions within 80 moves, per-level median looks at or under par [1,1,2,2,3], and no trial above 4 looks. (FR-2)
7. Given a one-wall-drifted layout, when the static checks run, then at least one length check goes red (mutation control); a green-on-drift run is a harness FAIL. (FR-5)
8. Given `git diff main --stat` for this story, when listed, then only `dev/lightfare-proof.py` changed; zero website bytes, zero `scripts/` bytes, zero doc bytes. (scope)
9. Given the full Story 155 game on the branch, when the harness runs the browser legs on both viewports, then storage probes match, corrupt seeds sanitize to 0, blocked storage stays silent, the pad path works on mobile, and zero page-attributable console errors are raised. (FR-3)

## Edge cases

- Key-vs-click degradation: loud `FALLBACK` line per step, never debug-gated. (contract section 4; FR-6)
- Playwright missing / bad port: CHECK FAIL, exit 1, cause named; never stay green. (contract section 4; FR-6)
- Narrowing flag plus all pass: `SKIPPED:` lines in argv order, exit 3; FAIL still dominates SKIP. (contract section 4; FR-4)

## Out of scope

The game file (Story 155), the site card (Story 156), the pattern-doc section (Story 158), any `website/` or `scripts/` change, any tuning-constant change, any release text.

## Traceability

Every contract clause is covered: section 1 check legs map to FR-1 through FR-3 (AC-2 through AC-4, AC-6, AC-9); non-blocking rule maps to the header note; section 2 formulas map to FR-1 and FR-4 (AC-2); section 3 tuning table maps to FR-6; section 4 edge cases map to FR-4, FR-5, FR-6 and the Edge cases list (AC-1, AC-5, AC-7); section 5 design criteria map to AC-1 through AC-5; section 6 balance rationale maps to FR-1, FR-2, FR-5 (AC-2, AC-6, AC-7: exact lengths prove the ramp, trial thresholds prove the economy is completable with paid recovery, drifted-layout red proves the instrument is not tautological).

## Evidence the dev must paste (in the PR)

- RED anchor: exit 2 on the pre-155 tree.
- Static legs: BFS 8/10/12/14/16, costs 1/2/4/8, spends 1/3/7/15, refusal rule.
- Trials: per-level 50/50 within 80 moves, medians at/under par, max looks <= 4.
- Mutation control: drifted layout goes red.
- Browser legs both viewports: Start 1, retry/advance +0, 4-look spend with refused 5th, probe match, corrupt to 0, blocked silent, pad path mobile, zero page errors.
- Scope: `git diff main --stat` shows only `dev/lightfare-proof.py`.

## Definition of done

- AC-1 through AC-9 all hold on the branch.
- File changes are limited to `dev/lightfare-proof.py`; zero website bytes verified by diff.
- Failure to reach green by the release gate defers with a note; v0.57.0 ships on 155/156 regardless.
