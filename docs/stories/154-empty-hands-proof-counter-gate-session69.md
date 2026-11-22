# Story 154: EMPTY HANDS proof harness covers the counter (Session 69, P1b, tooling)

**Status:** Ready for development (Session 69, 2026-11-22).
**Author:** Quinn, Business Analyst.
**Priority:** P1b (tooling, zero website bytes; non-blocking for v0.56.0).
**Assigned to:** **Kai**, sole code owner. File: `dev/empty-hands-proof.py` only. Zero website bytes.
**Base commit:** `7ee3571` (main, v0.55.0 released).
**Scope:** `dev/empty-hands-proof.py` only: one new browser-leg check `gate8-plays-counter` on both viewports. No game file, no `website/` file, no `scripts/` file, no doc file in this story.
**Design contract:** `flambeee-team/design-handoff.md`, Story 154 sections 1 through 6. Design-owned observable criteria live in contract section 5 and are mapped here one for one.
**Non-blocking rule:** if gate8 is not green by the release gate, v0.56.0 still ships on Story 153 and this story defers with a note (precedent: tooling never holds a user-visible cut).

## Summary

Story 153 adds the EMPTY HANDS play counter. This story is the durable instrument for it: the proof harness gains a browser-leg check that can bless a release only while the counter is absent-never, wrong-never, and double-counting-never. Fresh profile reads 0, first Start reads 1, reload keeps 1, WIN advance is a no-op, BUST restart is exactly +1, the stored `localStorage` value is a JSON number matching the probe, corrupt seeds sanitize to 0, and a blocked-storage context still increments in memory silently. The Story 152 narrowing discipline (SKIPPED plus exit 3, FAIL dominates SKIP, RED anchor exit 2) is unchanged, gates 1 through 7 and the 19-row baseline and seed manifest are untouched, and a green gate8 on the pre-153 game file is a harness defect, not a pass.

## Baseline measured at Session 69 planning (Wave 1, 2026-11-22)

| Check | Value |
|---|---|
| Base commit | `7ee3571` (main, v0.55.0) |
| Harness file | `dev/empty-hands-proof.py` (gates 1-7 shipped; browser leg gate7 green at 1280x800 and 375x667, zero page-attributable console errors) |
| Seed manifest | `dev/empty-hands-seeds.json`, SEED_BASE 3000, level L seeds `3000 + L*1000 + s`, 200 runs per level, 6 levels (unchanged) |
| Gate thresholds | solver solvable 200/200 every level; L6 greedy in [0.15, 0.60]; solver-greedy gap >= 25 pts; random <= 0.10; purse monotone 200/200; never-give 0/200 with clean static scan (all unchanged) |
| Counter on base tree | absent: no `#plays` line, no `plays()` probe (gate8 must go red here) |
| Narrowing discipline (Story 152) | each flag prints `SKIPPED: <what> (reason: <flag>)` and exits 3; FAIL dominates SKIP; default full run exits 0 on success; RED anchor (game file absent) exits 2 |
| Browser defaults | port 8932 (`--port=` override); viewports 1280x800 and 375x667 |

## Requirements

### 1. New browser-leg check `gate8-plays-counter`

One new check, both viewports (1280x800 and 375x667), real clicks and keys on a fresh profile, in this order:

```
fresh profile -> line reads 0, probe plays() == 0
  -> Start click -> line reads 1, probe == 1
  -> reload -> line still 1, re-rendered 1
  -> solve board to WIN -> advance -> line still 1
  -> force or play to BUST -> restart -> line reads 2 (exactly one increment)
  -> read localStorage['flambeee-empty-hands-plays'] -> JSON number, equals probe
  -> seed corrupt values ("abc", -1, 1.5, null, bad JSON) -> boot sanitizes to 0
  -> blocked-storage context -> increments in memory, no page-attributable console error, never throws
```

Formulas with units (contract section 2): `plays_counter_delta [plays] = +1` per Start-from-TITLE entry, `+1` per BUST-restart entry, `+0` for boot, TITLE preview, `advance()`, reload, restore, `reset()`. Match assertion: `JSON.parse(localStorage['flambeee-empty-hands-plays']) [plays, integer] == __empty.plays() [plays, integer]`.

### 2. Exit discipline (Story 152 stands, unchanged)

- Harness states: `RED-absent (exit 2) | FAIL (exit 1) | PASS (exit 0) | SKIP-narrowed (exit 3)`.
- Narrowing flags (`--sim-only`, `--viewport=desktop|mobile`, `--port=N`): each flag prints `SKIPPED: <what> (reason: <flag>)` in argv order and exits 3 when every executed check passes. FAIL dominates SKIP: any CHECK FAIL exits 1 even with skip flags present.
- Invalid `--viewport` / `--port` values are FAILs. Default full run exits 0 only when every check including gate8 passes on both viewports.
- RED anchor: game file (or read) absent exits 2 with `The gate has no target`.
- No change to gates 1 through 6, the 19-row baseline, the seed manifest, or the sim legs (manifest schedule, config drift run first and unchanged). The browser leg runs gate7 then gate8 per viewport; the report prints every CHECK line, then SKIP lines, then `RESULT`.

### 3. Failure behavior and Plan B

| Condition | Harness behavior | Plan B |
|---|---|---|
| Game file absent | RED anchor, exit 2 | Fix the tree, not the harness |
| Playwright missing / serve fails / viewport unknown / bad port | CHECK FAIL, exit 1, failing check named | Name the cause in the detail string; never stay green |
| Key-vs-click degradation in the browser leg | Loud `FALLBACK` line per degraded step, never debug-gated | Same Story 152 discipline as gate7 |
| Corrupt seeded values (`"abc"`, -1, 1.5, `null`, bad JSON) | Assert boot sanitizes to 0 | Sanitizer rule is the oracle; any garbage render is FAIL |
| Blocked-storage context | Assert in-memory increment, silent, no page-attributable console error, never throws | Console listener distinguishes page errors from environmental noise (for example a favicon 404 that reproduces on base) |
| Port collision | `--port=` override; server-start failure is FAIL with the port named | Same as the gate7 convention |
| Harness run against the pre-153 game file | gate8 must go red (no line, no probe getter, or wrong counts) | Mutation control below; a green gate8 on the old file invalidates the instrument |

### 4. Stacking note

If the new probe getter is needed before Riven's Story 153 branch lands, base the harness branch on Riven's story branch and record the stacked-merge order in the PR (precedent: #257/#258). QA verifies on the integrated tree. Story 154 never blocks the v0.56.0 cut.

### 5. Mutation / negative control (required)

Run the new harness against the pre-153 game file and require gate8 red (missing `#plays` line, missing `plays()` probe, or miscounted transitions). A green gate8 on the old file means the check is tautological and must be rewritten, not waived. This mirrors the Story 144 RED-anchor discipline and the Session 67 warning that a green proof script is a claim about the script, not the product.

### 6. Boundaries

- Zero website bytes. No new storage key. No gameplay constant changes. No tuning change.
- Viewport parity: gate8 asserts the full counter sequence at 1280x800 and 375x667 with real input and zero page-attributable console errors; overflow and no-network expectations follow the gate7 convention already in the file.
- Seeds and run counts inherited unchanged: SEED_BASE 3000, `L*1000+s`, 200 runs per level, 6 levels from `dev/empty-hands-seeds.json`; sim gates keep their shipped thresholds. Pass threshold: default full run exit 0 requires gate8 green on both viewports plus every prior gate green; any single FAIL fails the run.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 5; AC-1 through AC-8 map them one for one. AC-9 onward pin the exit discipline, failure behavior, and scope guards. Each is verifiable by running the harness.

1. Given the pre-153 game file, when the harness runs the full gate, then gate8 reports FAIL: the instrument cannot bless a counterless file. A green gate8 on the old file is a harness defect and the check must be rewritten. (design 5.1; mutation control)
2. Given the post-153 game file and a fresh profile, when the harness starts the browser leg, then the plays line reads `Plays on this browser: 0` and `__empty.plays()` is 0 on both viewports before any Start. (design 5.2)
3. Given a fresh profile, when the harness clicks Start once, then the line reads `Plays on this browser: 1`, the probe is 1, and reloading keeps it at 1 with the line re-rendered, on both viewports. (design 5.3)
4. Given a WIN end panel, when the harness advances via the advance path, then the plays number does not change on either viewport. (design 5.4)
5. Given a BUST end panel, when the harness restarts via the restart path, then the plays number increases by exactly 1 on either viewport. (design 5.5)
6. Given seeded corrupt, negative, fractional, null, and bad-JSON stored values, when the harness boots, then the line reads `Plays on this browser: 0` in every case on both viewports. (design 5.6)
7. Given a blocked-storage context, when the harness plays a run, then the in-memory count still increments with no page-attributable console error, nothing is thrown, and the harness side of the run exits 0. (design 5.7)
8. Given a narrowing flag (`--sim-only`, `--viewport=`, or `--port=`), when every executed check passes, then the harness prints `SKIPPED:` lines in argv order and exits 3; given any CHECK FAIL with the same flag, then it exits 1. (design 5.8; FAIL dominates SKIP)
9. Given invalid `--viewport` or `--port` values, when the harness runs, then the run is a FAIL (exit 1), never silent green and never a skip.
10. Given the game file absent, when the harness runs, then it exits 2 (RED anchor) with the target named.
11. Given any key-vs-click degradation in the browser leg, when it happens, then the harness prints one loud `FALLBACK` line per degraded step.
12. Given the post-153 game file, when gate8 reads storage, then `JSON.parse(localStorage['flambeee-empty-hands-plays'])` is a JSON number and equals `__empty.plays()`.
13. Given the merged tree, when `git diff main --stat` is inspected for this story's work, then only `dev/empty-hands-proof.py` changed: zero website bytes, no new storage key, no gameplay constant change, gates 1 through 7 and the seed manifest byte-identical in behavior.
14. Given the Story 153 branch unmerged, when this work needs the `plays()` probe, then the harness branch is based on Riven's story branch with the stacked-merge order recorded in the PR; QA verifies on the integrated tree, and this story never blocks the v0.56.0 cut.

## Evidence the dev must paste (in the PR)

- Full default run on the integrated tree: exit 0, gate8 CHECK lines green on both viewports, zero page-attributable console errors.
- Mutation run against the pre-153 game file: gate8 FAIL (RED), proving the instrument is not tautological.
- Narrowing runs: each flag prints its `SKIPPED:` line and exits 3 with all executed checks green; one FAIL-with-flag run exits 1.
- RED anchor run (game file absent): exit 2.
- Diff stat: `dev/empty-hands-proof.py` only.

## Definition of done

- AC-1 through AC-14 all hold; any single FAIL fails the run; FAIL dominates SKIP in every narrowing combination.
- Mutation control is red on the old file and green on the new file; without both halves the instrument is unproven.
- PR contains only `dev/empty-hands-proof.py`; diff confirms zero website bytes.
- Scout QA verifies on the integrated tree; Rook review notes the instrument pins the Story 153 contract.
- If gate8 is not green by the release gate, v0.56.0 ships on Story 153 alone and this story defers with a note.

## Out of scope

- Any `website/` file, any `scripts/` file, any doc file, any tuning constant, any seed-manifest change, any gate 1 through 7 threshold change, any `BLOG.md` or release text.
- Product behavior itself (Story 153, Riven). This story only proves it.
