# Story 152: Proof instruments cannot report green on a path they skipped (Session 68, P1, #254/#255/#265)

**Status:** Ready for development (Session 68, 2026-11-21).
**Author:** Quinn, Business Analyst.
**Priority:** P1 (tooling; rides along because "they're instruments that can lie" — a bugfix cut blessed by checks that report green on a skipped path is a false pass). Issues #254, #255, #265 items 7-8.
**Assigned to:** **Kai**, sole code owner. Two tool files, disjoint hunks. Zero website bytes.
**Base commit:** `afbf411` (main, v0.54.0 released).
**Scope:** `scripts/run-cinder-family.py` (baseline identity tokens + remediation line) and `dev/empty-hands-proof.py` (SKIPPED lines + exit 3 + FALLBACK lines). Nothing else.
**Design contract:** `flambeee-team/design-handoff.md`, Story 152 sections 1-7 plus contested calls C1-C4. Design-owned observable criteria live in contract section 6 and are mapped here; the functional AC below test the same behavior from the requirements side.

## Summary

Two proof instruments can report green on a path they skipped. The Cinder family runner collapses a missing baseline row and an invented baseline row into one coarse `BASELINE-MALFORMED (rows != 19)` message that names neither row, and its playwright-missing refusal tells the operator something is wrong without saying how to fix it. The EMPTY HANDS harness can skip its entire browser leg (`--sim-only`, `--viewport=`, `--port=`) yet still print a green-looking run, and when a key press silently degrades to a click nobody is told. Fix all four: per-row identity tokens that name every offending row, one remediation line naming the fix, loud SKIPPED lines with an unmistakable exit code, and loud FALLBACK lines for every input degradation. No game, site, or baseline content changes.

## Baseline measured at Session 68 planning (Wave 1, 2026-11-21)

| Check | Value |
|---|---|
| Runner baseline check | raises `BASELINE-MALFORMED (rows != 19)` for both a missing row and an orphan row, shadowing the I9 DA-9 row-identity tokens |
| Runner refusal path | exits 2 with `playwright missing under invoker /usr/bin/python3` and no remediation line |
| Harness flag parsing | `--sim-only`, `--viewport=`, `--port=` parsed positionally (`dev/empty-hands-proof.py:748-754`); a skipped browser leg can still produce a green-looking run |
| Harness keyboard leg | falls back to a click without naming the fallback |
| Family size | 19 scripts (`run-cinder-family.py:156`); `TIMEOUT` 300s, `PORT_BASE` 8765, `PORT_STRIDE` 1, `FAIL_LINES` 30; runner exits 0/1/2/3 with documented meanings |
| Harness exits today | 0 full green; 1 CHECK FAIL; 2 RED anchor (absent/unreadable game); 3 never used (free for the new SKIP meaning) |
| Harness defaults | `BROWSER_PORT` 8932, `SEED_BASE` 3000, `RUNS_PER_LEVEL` 200 |

## Requirements

### 1. Runner baseline identity tokens (#254; replaces the coarse count shadow)

Binding pipeline order; first failure wins:

1. Flag parse. Unknown flag or bad value: misuse, exit 3 (unchanged).
2. Repo/target resolve. Bad repo: exit 3. Missing target: exit 2 (unchanged).
3. Discovery. Zero scripts: exit 2 (unchanged).
4. Baseline load plus per-row schema validation. Unparseable file, non-object top, bad `family_size` field, bad generated date, non-list rows, or any per-row schema violation (non-object row, bad script value, duplicate script, bad expected, bad category, fail row without integer issue, pass row with non-null issue, bad note): `BASELINE-MALFORMED (<detail>)`, exit 2. The bare `rows != 19` count rejection is REMOVED here; count mismatch is exclusively stage 5 work.
5. Identity cross-check (fail-closed, before any probe executes). Let `missing = sorted(discovered rels minus baseline scripts)`, `orphan = sorted(baseline scripts minus discovered rels)`. If missing is non-empty, print `BASELINE-MISSING-ROW <r1> <r2> ...` naming every missing rel. If orphan is non-empty, print `BASELINE-ORPHAN-ROW <r1> <r2> ...` naming every orphan rel. Both lines print when both sets are non-empty, MISSING line first. Either case: exit 2, zero probe lines, zero execution.
6. Pre-flight dependency refusal (existing lines plus one; see section 2).
7. Execute, tally, drift verdict (unchanged, exits 0/1/2 per existing map).

Exact rules: missing non-empty implies stdout line `BASELINE-MISSING-ROW` + space-joined sorted missing AND exit 2 with zero executions. Orphan non-empty implies `BASELINE-ORPHAN-ROW` + space-joined sorted orphan AND exit 2. Both non-empty implies both lines, MISSING first, exit 2.

Filtered runs (`--include`/`--exclude`) and `--no-baseline-check` bypass stages 4-5 with the existing `FILTERED-NO-BASELINE-CERTIFY` / `OFF` labels; the identity tokens do not apply there and such runs are not citable as full-family green.

### 2. Runner remediation line (#255; one line, exit unchanged)

The playwright-missing refusal keeps all existing lines (`ENV-SKIP <rel> reason=env-skip` per-row lines, tally, STALE baseline line) and appends exactly one stdout remediation line naming the concrete fix, where `P = dirname(abspath(repo)) + '/.venv/bin/python'`:

- Child-missing branch: `remediation: rerun with --python P`.
- Invoker-missing branch: `remediation: invoke run-cinder-family.py with P (the playwright-bearing interpreter)`.

Exactly one remediation line per refusal. Exit stays 2. If the failing interpreter already is the sibling venv, the line still prints the sibling path (stable literal beats clever routing).

### 3. Harness skip discipline (#265 item 7; a skip is never green)

- Refusals keep existing codes: game absent/unreadable exit 2; manifest or config refusal exit 1. Skip flags never alter refusal codes.
- Sim gates 1-6 run always, even under `--sim-only` (that is the point of the flag).
- Browser gate 7 runs fully by default. Each narrowing flag prints its own stdout line BEFORE the report, exact shape `SKIPPED: <what> (reason: <flag>)`, one line per flag in argv order:
  - `--sim-only` gives `SKIPPED: browser leg (reason: --sim-only)`.
  - `--viewport=<v>` gives `SKIPPED: all viewports except <v> (reason: --viewport=<v>)`.
  - `--port=<p>` gives `SKIPPED: default-port serve (reason: --port=<p>)`.
- Final RESULT line: `RESULT: PASS (exit 0)` only when nothing was skipped and all checks green; `RESULT: SKIP (exit 3)` when any skip flag was present and every executed check passed; `RESULT: FAIL (exit 1)` when any CHECK failed. FAIL dominates SKIP: a failing sim under `--sim-only` exits 1 (still never 0), with the SKIPPED line still printed.
- Exact exit rule: `exit = refusal ? (2 absent/unreadable game; 1 manifest/config) : any CHECK FAIL ? 1 : (any skip flag ? 3 : 0)`. SKIP (3) is never 0 by construction.
- Invalid `--viewport=<v>` (v not `desktop`/`mobile`): record gate7-browser FAIL naming the bad value, exit 1 under the existing "any other failure" meaning. A vacuous zero-viewport PASS is banned. Unparseable `--port=` value: exit non-zero with a named reason line, never `RESULT: PASS`.
- Exit-code collision: the harness never used 3, so 3 is free in its namespace. The runner already uses 3 (misuse), but that is a separate binary with a separate documented map; no caller mixes the two namespaces.

### 4. Harness keyboard fallback is loud (#265 item 8; never silent)

- Whenever a key-press-first attempt at a gameplay step degrades to a click, print `FALLBACK key->click at <step>` on stdout immediately (never debug-gated), once per degraded step, where `<step> = <desktop|mobile> L<level> gift <n>` with n the 1-indexed gift attempt on the current board.
- The existing reverse branches (click degrades to key in `click_end`) print the symmetric `FALLBACK click->key at <step>`. No fallback in either direction is silent.
- A healthy run prints zero FALLBACK lines; absence of the line is the passing assertion.

### 5. Boundaries

- Zero website bytes. No change to the 19-row baseline itself, no tuning change (`FAMILY_SIZE` 19 frozen; `TIMEOUT`/`PORT_BASE`/`PORT_STRIDE`/`FAIL_LINES` ranges unchanged; `SEED_BASE` 3000 / `RUNS_PER_LEVEL` 200 frozen; `BROWSER_PORT` 8932 default frozen).
- Never renumber any existing exit code to make room. Old meanings (runner 0/1/2/3, harness 0/1/2) must still hold alongside the new harness 3.
- Plan B sequencing (same owner, same PR, only if needed): the remediation line plus the harness SKIPPED/FALLBACK lines may land first (disjoint hunks), with the stage-4/5 reorder following before merge. Never ship the reorder without the measured-fault rerun in the Evidence section.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 6; AC-1 through AC-5 map them directly, the rest pin the functional behavior. Each is verifiable by a test.

1. Given a baseline copy with one known row deleted, when I run the family runner unfiltered against it, then stdout contains `BASELINE-MISSING-ROW <that rel>`, the exit code is 2, and no probe script executes (zero PASS/FAIL per-script lines). (design: deleted row names itself)
2. Given a baseline copy with one invented row inserted, when I run the family runner unfiltered against it, then stdout contains `BASELINE-ORPHAN-ROW <that rel>`, the exit code is 2, and no probe script executes. (design: inserted row names itself)
3. Given playwright missing under the invoking or child interpreter, when the runner refuses, then stdout contains one remediation line naming the team venv python path, all existing ENV-SKIP and tally lines still print, and the exit code is still 2. (design: missing interpreter names the fix)
4. Given a healthy tree, when I run the harness with `--sim-only` (likewise `--viewport=desktop`, `--port=<free>`), then stdout contains `SKIPPED: <what> (reason: <flag>)` before the report and the final line reads `RESULT: SKIP (exit 3)`. (design: skipped browser leg cannot look green)
5. Given a gameplay step where the key press path cannot advance the board, when the harness degrades to a click at that step, then stdout contains `FALLBACK key->click at <step>` with the exact step echo, and a healthy full run prints zero FALLBACK lines. (design: degradation is loud)
6. Given a baseline copy with one row deleted AND one row inserted, when I run the runner unfiltered, then stdout contains both `BASELINE-MISSING-ROW <dropped rel>` and `BASELINE-ORPHAN-ROW <added rel>` in that order, and the exit code is 2.
7. Given an empty rows list, when I run the runner unfiltered, then stdout contains `BASELINE-MISSING-ROW` naming all 19 discovered rels and the exit code is 2.
8. Given a baseline copy with a duplicate script in rows (likewise truncated JSON, bad `family_size`, unparseable file, missing baseline file), when I run the runner, then stdout contains `BASELINE-MALFORMED` with the detail and the exit code is 2 (old meaning holds; count mismatch alone never produces MALFORMED).
9. Given a filtered run (`--include`/`--exclude`) or `--no-baseline-check`, when the runner runs, then the existing `FILTERED-NO-BASELINE-CERTIFY` / `OFF` labels print and the identity tokens do not apply.
10. Given `--sim-only` with a deliberately failing sim gate, when the harness runs, then the SKIPPED line still prints, the RESULT is FAIL, and the exit code is 1 (FAIL dominates SKIP; skip never masks failure, never 0).
11. Given `--viewport=desktop` with a green desktop leg (likewise mirrored for mobile), when the harness runs, then the SKIPPED line for the other viewport prints, RESULT is SKIP, exit 3.
12. Given `--viewport=bogus`, when the harness runs, then gate7-browser records FAIL naming the value and the exit code is 1 (vacuous PASS banned). Given an unparseable `--port=` value, when the harness runs, then it exits non-zero with a named reason line, never `RESULT: PASS`.
13. Given multiple skip flags at once, when the harness runs, then one `SKIPPED: <what> (reason: <flag>)` line prints per flag, in argv order, before the report.
14. Given the default full invocation on a healthy tree, when the harness runs with no skip flags, then RESULT is `PASS (exit 0)` with no SKIPPED lines and no FALLBACK lines (old green path unchanged).
15. Given the old exit meanings, when QA re-asserts them, then runner 0/1/2/3 and harness 0/1/2 still hold alongside the new harness 3 (absent game file gives RED exit 2; drifted CONFIG gives FAIL exit 1).
16. Given `git diff main --stat`, when I list changed files, then only `scripts/run-cinder-family.py` and `dev/empty-hands-proof.py` changed (zero website bytes).

## Evidence the dev must paste (in the PR)

- Runner fault injection, 5/5 exact, all exit 2 unless noted, each run twice (repeatability 2/2 identical token and code): (a) baseline copy minus the scout row gives `BASELINE-MISSING-ROW scout-qa-session24.py`, zero per-script lines; (b) baseline copy plus one invented rel gives `BASELINE-ORPHAN-ROW <rel>`; (c) copy with one deleted AND one inserted gives both tokens in order; (d) truncated-JSON copy gives `BASELINE-MALFORMED`; (e) regression: unfiltered run on the untouched tree keeps its established verdict shape (MATCH or the known content-drift FAILs), proving the reorder did not weaken the green path.
- Harness: `--sim-only` on a healthy tree gives SKIPPED plus exit 3 (run twice); `--viewport=desktop` and `--viewport=mobile` each give their SKIPPED line plus exit 3; `--port=` with a free port gives its SKIPPED line plus exit 3; one forced-fail-under-skip case exits 1; `--viewport=bogus` gives gate7 FAIL naming the value, exit 1; forced FALLBACK stub-page unit probe (no browser) asserting the exact `FALLBACK key->click at <step>` literal and step echo 1/1; one live full run asserting zero FALLBACK lines.
- Old codes re-asserted: absent game file gives RED exit 2; drifted CONFIG gives FAIL exit 1.
- `git diff main --stat` showing only the two tool files.

## Definition of done

- AC-1 through AC-16 all hold on the branch; measured-fault plan 5/5 exact with 2/2 repeatability; old exit meanings re-asserted.
- PR contains only `scripts/run-cinder-family.py` and `dev/empty-hands-proof.py`; diff confirms zero website bytes.
- Scout QA GO (including the old-meanings regression) and no new exit-code collision.
- The bare `rows != 19` MALFORMED rejection is gone from stage 4; count mismatch is exclusively identity work.

## Issue linkage

- #254: runner shadows the I9 DA-9 row-identity tokens behind the coarse row-count check; fixed by the identity cross-check (AC-1, AC-2, AC-6, AC-7).
- #255: playwright-missing refusal prints no remediation; fixed by the one remediation line (AC-3).
- #265 items 7-8: harness skips the browser leg yet looks green (item 7; AC-4, AC-10 through AC-14) and the keyboard fallback is silent (item 8; AC-5).

## Out of scope

- #259.1 `dev/echo-fps-proof.py` check-08 detail mislabel (follow-up, not this batch).
- #265 items 2 (L4+ findability re-check), 6 (`accepts()` guard), 9/10 (heuristic scan, mirror-vs-page coverage).
- #237/#238 manifest work, #206 Snapline, #217 cadence policy, any change to the 19-row baseline itself.
- Any website bytes, `BLOG.md`, release notes, Bluesky staging.
