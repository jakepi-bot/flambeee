# Story 165: lightfare-proof short-viewport legs (Session 72, P1)

**Status:** Ready for development (Session 72, 2026-11-25).
**Author:** Quinn, Business Analyst.
**Priority:** P1 (the instrument half of the defect day; per the session plan this story is the only thing that proves 163/164 live. Never cut).
**Assigned to:** **Kai**, sole code owner. File: `dev/lightfare-proof.py` only. Zero website bytes.
**Base commit:** `12cf383` (main, v0.58.0).
**Scope:** Two new browser legs at 375x600 and 320x568 asserting TITLE board visibility and ends `scrollHeight <= innerHeight`, plus one screenshot artifact per viewport per state and a RED anchor that fails against the pre-163 file.
**Design contract:** `flambeee-team/design-handoff.md`, Section 3 (Story 165, subsections 3.1 through 3.6). Design-owned observable criteria live in contract subsection 3.5 and are mapped here one for one.
**Non-blocking rule:** Story 165 is never cut, not for the fold fit, not for the release gate. If driving the full L1-clear plus L2-exhaust flow proves flaky at 320x568, Kai fixes the wait/retry inside the new leg (longer `wait_state` timeout, same transitions) and records it; the assertions, screenshots, and RED anchor do not shrink.

## Summary

`dev/lightfare-proof.py` is the LIGHTFARE harness, and today it cannot see either #292 defect: Session 71 gave it port ownership (Story 161 preflight plus child-PID cleanup), but it has no viewport leg at 375x600 or 320x568, so a fix for the short heights would pass the harness without ever being looked at. This story adds the two short legs. Each leg loads TITLE and asserts the TITLE-board check, screenshots it, presses Start, drives the L1 BFS path to LEVELCLEAR and asserts the ends-fit check, screenshots it, advances to L2, exhausts 80 moves to LOSE, and asserts the ends-fit check again with both states named in the detail. The console gate (zero page-attributable errors) applies to the short legs exactly as it does to the existing legs. The existing desktop and mobile legs do not change shape: no existing CHECK is renamed, removed, or reworded. A RED anchor run from a `git worktree` at `12cf383` with only this harness file copied over must show exactly the 4 new checks FAIL (board `display: none`, ends document taller than the viewport) with exit 1, so tomorrow has a regression gate. Exit discipline is unchanged: PASS 0, FAIL 1, RED 2, SKIP 3.

## Baseline measured at Session 72 planning (Wave 1, 2026-11-25)

| Check | Value |
|---|---|
| Base commit | `12cf383` (main, v0.58.0) |
| Harness file | `dev/lightfare-proof.py` (Story 161 port ownership: `_preflight_port_free`, child-PID cleanup, no `fuser -k`) |
| Viewport gap | no leg at 375x600 or 320x568, so neither #292 defect is visible to the harness |
| Viewport table | gains two appended entries; existing `desktop` 1280x800 and `mobile` 375x667 entries byte-untouched |
| `--viewport=` set | grows from `desktop\|mobile` to `desktop\|mobile\|mobile-600\|mobile-568`; unknown values stay FAIL exit 1 |
| `--sim-only`, `--port=N`, argv-order SKIPPED lines | Story 152 semantics preserved; FAIL dominates SKIP |

## Functional requirements

FR-1 (contract 3.1, viewport table). Two appended entries: tag `mobile-600` (width 375 px, height 600 px, touch True, is_mobile True) and tag `mobile-568` (width 320 px, height 568 px, touch True, is_mobile True). No existing entry changes. `--viewport=` valid set becomes `desktop|mobile|mobile-600|mobile-568`; unknown values FAIL exit 1; `--port=N` range and `--sim-only` narrowing keep Story 152 semantics.

FR-2 (contract 3.1, short-leg flow). Per new tag, normative flow on a fresh profile in real Chromium with real input (reuse `run_viewport` helpers, pad-click fallback lines, and console/page-error gates): load TITLE and run the TITLE-board assert (FR-3) plus the TITLE screenshot; press Start (Enter-first, click fallback with FALLBACK line as today), drive the L1 BFS path to LEVELCLEAR and run the ends-fit assert (FR-4) plus the ends screenshot; advance to L2, exhaust 80 moves to LOSE, run the ends-fit assert again under the same check name with both states in the detail; console gate of zero page-attributable errors across the short leg (same `attributable_errors` rule as existing legs). No existing CHECK is renamed, removed, or reworded; the two new legs add new CHECK rows only. LOSE arrival uses the debug-free path already in the harness (`drive_exhaust` on L2); no new shortcut may be invented.

FR-3 (contract 3.2, TITLE-board check). `browser-<tag>-title-board`, FAIL names the tag and the clause: `getComputedStyle(#board).display != 'none'` (the clause that fails against 12cf383 line 136 at both short sizes); `#board` rect width at least 140 px (the TITLE_BOARD_W min from contract 1.3; post-fix actual 150) and height above 0 px; oneliner byte-present in body text (harness ONELINER constant, unchanged); `#startBtn` rect top at least 0 px and bottom at most `innerHeight` px (the design guarantee at 600 and 568 per contract 1.4, locked by the harness). All four read at `scrollY = 0`.

FR-4 (contract 3.2, ends-fit check). `browser-<tag>-ends-fit`, one row per tag covering LEVELCLEAR and LOSE with both states named in the detail: `document.documentElement.scrollHeight` at most `window.innerHeight`, read at `scrollY = 0`, separately after LEVELCLEAR arrival and after LOSE arrival; `#againBtn` rect top at least 0 px and bottom at most `window.innerHeight` px at both arrivals, rect height at least 44 px. The retry path after LOSE is still asserted by the shared flow (Enter reaches RUN, light 15, moves 0, plays unchanged); the fit check does not replace it.

FR-5 (contract 3.2, screenshots). 4 files total, 2 per new tag: `lightfare-proof-<tag>-title.png` after the TITLE-board assert, `lightfare-proof-<tag>-ends.png` after the LOSE ends-fit assert. Directory is the OS temp dir (`tempfile.gettempdir()/lightfare-proof-<tag>-<state>.png`), never the repo tree (keeps the worktree clean and the zero-website-bytes proof trivial). Each path printed as `ARTIFACT: <absolute path>` on stdout. Full-page screenshots (`full_page=True`) so the fold claim is visible in the artifact. Viewport pixel sizes exact: 375x600 and 320x568 CSS px, `device_scale_factor` default 1. Artifact write failure is a CHECK FAIL with cause `artifact-write: <path>: <error>`; a leg without its artifact does not pass, and the repo is never the fallback.

FR-6 (contract 3.2 RED anchor, plus 3.3-3.4 constants). Procedure: `git worktree add /tmp/lf-red-163 12cf383`, copy the NEW harness file over the worktree copy (`cp dev/lightfare-proof.py /tmp/lf-red-163/dev/lightfare-proof.py`, the only file that differs in behavior), run the two short legs from the worktree (`python /tmp/lf-red-163/dev/lightfare-proof.py --viewport=mobile-600` and `--viewport=mobile-568`, free port), then `git worktree remove --force /tmp/lf-red-163`; the repo worktree is never mutated by the RED run. Expected: exit 1 (FAIL, not RED 2: the file exists and reads; the checks fail). Exactly the 4 new checks FAIL: both `title-board` rows (display none, zero rect) and both `ends-fit` rows (pre-fix ends document taller than the viewport). All pre-existing checks keep their 12cf383 outcome (desktop and mobile legs PASS as in v0.58.0, static and trial legs PASS). Kai pastes the 4 FAIL lines plus the exit code into the PR. Post-fix run on the PR tree: all checks PASS, exit 0 (or exit 3 only under an explicit narrowing flag with its SKIPPED line). Exit codes unchanged (0/1/2/3); port-ownership refusal stays exit 1 and dominates SKIP. `BROWSER_PORT` 8943, spawn attempts 3, poll 50x0.2 s, preflight timeout 2 s: all untouched. Balance anchors (BFS [8,10,12,14,16], spends 1/3/7/15, 250 wrong-turn trials, par [1,1,2,2,3]) reproduce byte-identical report lines apart from the added rows.

## Acceptance criteria (BDD, observable in harness runs)

Design-owned observable criteria are in contract subsection 3.5; AC-1 through AC-6 map them directly. AC-7 pins the structural scope requirement.

1. Given a clean tree with the fix, when the operator runs the full harness on a free port, then both `browser-mobile-600-title-board` and `browser-mobile-568-title-board` print PASS and 4 artifact files exist at the printed `ARTIFACT:` paths showing a visible TITLE board. (design 3.5.1; FR-2, FR-3, FR-5)
2. Given the same run, when the operator reads the report, then both `browser-mobile-600-ends-fit` and `browser-mobile-568-ends-fit` print PASS with LEVELCLEAR and LOSE named in the detail, and no pre-existing CHECK changed its outcome versus 12cf383. (design 3.5.2; FR-2, FR-4)
3. Given the pre-163 file at commit 12cf383 under the RED procedure, when the operator runs the two short legs, then exactly the 4 new checks FAIL (board display none, ends document taller than the viewport) and the process exits 1. (design 3.5.3; FR-6)
4. Given the patched file, when the operator runs `--sim-only`, then no new leg runs, the SKIPPED line prints, and the exit is 3 on full pass (narrowing preserved). (design 3.5.4; FR-1)
5. Given the patched file, when the operator runs `--viewport=bogus`, then the run FAILs with exit 1 naming the bad value (validation preserved). (design 3.5.5; FR-1)
6. Given the merged PR, when the reviewer runs `git diff --stat` against main, then only `dev/lightfare-proof.py` changed (zero website bytes) and no `fuser`/`pkill` strings were reintroduced. (design 3.5.6; scope)
7. Given a stranger holding the port during a short leg, when the operator runs the harness, then the Story 161 REFUSED path fires (exit 1, stranger untouched, no screenshot written) and refusal dominates any `--viewport` narrowing. (FR-6 regression guard)

## Out of scope

No new game, no new mechanic, no new storage key, no #265 items, no website redesign. Zero website bytes: no `website/` path may appear in this story's diff. No tuning-constant change, no economy change, no baseline-anchor change, no narrowing-discipline change, no new CLI flag, no port-ownership regression. No touch of the Story 161 preflight plus child-PID cleanup.

## Non-blocking rule

Story 165 is never cut: per the session plan it is the only thing that proves 163/164 live. If the L1-clear plus L2-exhaust drive proves flaky at 320x568, Kai fixes the wait/retry inside the new leg (longer `wait_state` timeout, same transitions) and records it in the PR; the assertions (board visibility, `scrollHeight` bound, again-button rect, screenshots, RED anchor) do not shrink under Plan B.

## Defects/risks

- Harness leg that cannot see the defect: mitigated by the RED anchor, which must FAIL against `12cf383` before the fix counts as proven; the anchor is mandatory, not advisory, and no alternative evidence is accepted.
- Touch tap below the fold (pad at 600/568 TITLE): `click_handle` already scrolls into view before tapping; asserts always re-read at `scrollY` 0 afterwards, so no helper change is needed.
- Reveal freeze mid-drive (1000 ms): the existing `look_step` already waits REVEAL_MS plus 150 ms; short legs reuse it unchanged.
- Playwright missing: same as today, per-tag CHECK FAIL naming the import error. RED worktree unavailable (no git): FAIL the story, not a waiver.
- Verification plan (per contract 3.6): 1 full PASS run post-fix (exit 0, all CHECKs green, 4 artifacts), 1 RED run pre-fix per the worktree procedure (exit 1, exactly 4 new FAILs), 1 narrowing matrix (`--sim-only` expect 3, `--viewport=mobile-600` expect 3 on pass, `--viewport=bogus` expect 1), 1 stranger-on-port refusal (expect exit 1, stranger alive, Story 161 behavior intact). Pass thresholds: 4/4 new checks PASS post-fix; 4/4 FAIL pre-fix with named causes; narrowing 3/3 as specified; zero website bytes; pre-existing CHECK set identical to the 12cf383 baseline run. One deviation is FAIL.
