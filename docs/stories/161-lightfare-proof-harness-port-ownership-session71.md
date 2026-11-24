# Story 161: proof harness port ownership (Session 71, P0)

**Status:** Ready for development (Session 71, 2026-11-24).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (lying instrument; a green run that tests a stranger's tree is worse than a red run. Never cut).
**Assigned to:** **Kai**, sole code owner. File: `dev/lightfare-proof.py` only (`browser_legs()`, lines 1288-1368, plus `main()` port handling). Zero website bytes.
**Base commit:** `582171b` (main, v0.57.0).
**Scope:** Issue #287: prove the port is free before spawn, own only the child PID, refuse to adopt a stranger's server with a named CHECK FAIL and non-zero exit, and clean up only what this run started.
**Design contract:** `flambeee-team/design-handoff.md`, Section 3 (Story 161, subsections 3.1 through 3.6). Design-owned observable criteria live in contract subsection 3.5 and are mapped here one for one.
**Non-blocking rule:** Story 161 is never cut, not for the fold fit, not for the HUD item, not for the release gate. If it runs long, the release waits or ships without the polish stories, never without this fix.

## Summary

`dev/lightfare-proof.py` is the instrument the team trusts to say LIGHTFARE still works, and right now it lies. `browser_legs()` sets `started = True` on any successful GET without ever checking that `srv` is the process answering, then cleans up with `fuser -k 8943/tcp`. If a stranger holds port 8943, the harness adopts the stranger's server, tests the wrong tree, blesses it, and then kills a process it did not start. Kai replaces the defect with a prove-then-own discipline: a PREFLIGHT bind-or-connect check proves the port free before any spawn; `started = True` requires BOTH a live child PID and a GET served while that child is alive; on a pre-occupied port the harness prints the exact refusal copy, exits 1, spawns nothing, and kills nothing; cleanup addresses only the spawned child PID handle, and the port-scoped `fuser`/`pkill` kills are deleted. Plan A (prove-then-own 8943) is preferred because CI scripts and docs cite 8943; Plan B (ephemeral port) applies only if PID-plus-preflight cannot prove `served_by_child` on the target platform, and Kai records the pick in the PR.

## Baseline measured at Session 71 planning (Wave 1, 2026-11-24)

| Check | Value |
|---|---|
| Base commit | `582171b` (main, v0.57.0) |
| Harness file | `dev/lightfare-proof.py`, 1512 lines |
| `BROWSER_PORT` | 8943, line 54 |
| `browser_legs()` | lines 1288-1368; sets `started = True` on any successful GET; cleanup uses `fuser -k 8943/tcp` |
| Narrowing discipline (Story 152, preserved) | exit 0 PASS; 1 any CHECK FAIL; 2 RED anchor (game file absent or unreadable); 3 SKIP-narrowed (every executed check passed and at least one narrowing flag printed its SKIPPED line); FAIL dominates SKIP |
| Baseline anchors (untouched) | 19-row table, trial seeds `L*1000+t`, BFS lengths [8,10,12,14,16], spends 1/3/7/15, 50/50 trials, par [1,1,2,2,3] |
| Poll loop (unchanged) | 50 x 0.2 s (10 s) per attempt, at most 3 spawn attempts |
| Flags (unchanged) | `--port=N` (default 8943), `--sim-only`, `--viewport=desktop|mobile` |

## Functional requirements

FR-1 (contract 3.1, transition 1, PREFLIGHT). Before spawning any server, the harness proves the port is free by attempting a bind on `127.0.0.1:port` (create socket, close immediately) OR equivalently by requiring a connect to fail (connection refused). Bind succeeds (or connect refused) means free: proceed to spawn. Bind fails with `EADDRINUSE` (or connect succeeds) means occupied: go to REFUSED, never spawn. Preflight cost budget: at most 2 s wall time, 1 socket, 0 side effects.

FR-2 (contract 3.1, transition 2, ownership predicate). `started [boolean] = child_alive [boolean: srv.poll() is None] AND served_by_child [boolean: preflight_was_free AND GET_ok_while_child_alive]`. No third term. Either term false means not started. A GET answered while the child is dead, or answered when preflight showed occupied, must never set `started`. The current defect (`started = True` on any successful GET, even a stranger's) is the exact line being replaced. Each of the at most 3 spawn attempts re-checks PID-alive on every poll tick; a GET success with a dead child aborts the attempt (treat as not started) instead of adopting.

FR-3 (contract 3.1, transition 3, REFUSED). On a pre-occupied port: print the exact refusal copy (FR-4), print `RESULT: FAIL (exit 1)`, exit code 1, spawn nothing, kill nothing. The stranger process is untouched. FAIL dominates SKIP: if the refusal fires alongside any narrowing flag, exit 1, never 3.

FR-4 (contract 3.2, refusal copy and exits). Refusal copy, exact ASCII on stdout: `FAIL: port-ownership: port <N> already occupied before spawn; refusing to adopt the stranger server (reason: --port=<N> or default 8943)` where `<N>` is the decimal port. Followed by the existing summary shape: the CHECK line `CHECK browser-legs: FAIL (exit 1) port <N> occupied at preflight; no server started, none killed` and `RESULT: FAIL (exit 1)`. Exit codes per Story 152 preserved: 0 PASS; 1 any CHECK FAIL including this refusal; 2 RED anchor; 3 SKIP-narrowed.

FR-5 (contract 3.1, transition 4, cleanup). Stop only the spawned child PID (`srv.terminate()`, wait, `srv.kill()` on timeout). The `fuser -k <port>/tcp` and `pkill -f http.server <port>` port-scoped kills are removed. No cleanup path may address a port; every cleanup path addresses the child PID handle, and only if this run spawned it. `killed [processes] = {child PID if spawned}`, cardinality 0 or 1. `killed_by_port [processes] = 0` always. Grep of the file for `fuser` and `pkill` must read clean.

FR-6 (contract 3.3-3.4, constants and edge cases). `BROWSER_PORT` 8943 (range 1-65535 for `--port=`); preflight timeout 2 s (range 1-5 s); spawn attempts 3 (range 1-3); poll ticks 50 x 0.2 s unchanged; baseline anchors (19-row table, seeds `L*1000+t`, manifest) untouched. Edge behavior: TOCTOU (port freed between preflight and spawn) surfaces as child `Popen` failure or instant child death caught by the PID-alive check, retried up to 3, then FAIL with cause named, nothing killed. Child crash mid-legs aborts with a CHECK FAIL naming child death. Bad `--port=` value keeps the existing validation FAIL exit 1. `--sim-only` with occupied port runs no browser leg, prints the narrowing SKIPPED line, needs no preflight, exits 3 if all else passes. `--viewport=` narrowing with occupied port refuses: exit 1, never 3. Two harness copies racing on one port: loser sees occupied at preflight and refuses; winner owns; no kill exchange.

## Acceptance criteria (BDD, observable in harness runs)

Design-owned observable criteria are in contract subsection 3.5; AC-1 through AC-6 map them directly. AC-7 pins the structural scope requirement.

1. Given a stranger static server holding port 8943 from a scratch tree (not the repo `website/`), when the operator runs `python dev/lightfare-proof.py` without `--port`, then stdout contains a line starting `FAIL: port-ownership:` naming port 8943, stdout ends with `RESULT: FAIL (exit 1)`, the process exit code is 1, and the stranger server still answers its own sentinel afterwards (operator re-GETs the stranger URL and gets 200). (design 3.5.1; FR-1, FR-3, FR-4)
2. Given no process on 8943, when the operator runs the harness, then preflight passes, the child serves, the legs run to the normal report, and after exit no `http.server 8943` process remains while no unrelated process was touched. (design 3.5.2; FR-1, FR-2, FR-5)
3. Given a stranger on 8943 and `--sim-only`, when the operator runs the harness, then the run prints the narrowing SKIPPED line, runs no browser leg, starts no server, kills nothing, and exits 3 on full pass (narrowing preserved, no refusal because nothing was served). (design 3.5.3; FR-6)
4. Given a stranger on 8943 and `--viewport=desktop`, when the operator runs, then the run refuses with the named FAIL and exits 1 (FAIL dominates SKIP even though a narrowing flag printed SKIPPED). (design 3.5.4; FR-3, FR-4)
5. Given the patched file, when Quinn greps for `fuser` and `pkill`, then zero matches; and when Quinn greps the browser-legs cleanup for the child handle, then termination addresses `srv` (the PID) and never a port number. (design 3.5.5; FR-5)
6. Given the patched harness on a free port, when the full run completes, then the 19-row baseline table, trial seeds, and manifest lines are byte-identical in shape to the pre-patch output on a passing tree (ownership adds lines, changes no existing CHECK semantics). (design 3.5.6; FR-6)
7. Given `git diff main --stat` for this story, when the changed files are listed, then only `dev/lightfare-proof.py` changed; zero website bytes. (scope)

## Out of scope

No new mechanic, no new storage key, no other game file, no `GAME_ORDER` change, no `website/index.html` change (there is no new game card today), no backlog issues beyond #281/#285/#287, no FPS/app work. Zero website bytes: no `website/` path may appear in this story's diff. No tuning-constant change, no baseline-anchor change, no narrowing-discipline change, no new CLI flag.

## Non-blocking rule

Story 161 is never cut. It is the P0 above the polish: a harness that adopts a stranger's server is a lying instrument, and a green run from it is a claim about a process, not about the product. If the fold fit or the HUD item runs long, cut those first, never this story.

## Defects/risks

- Harness fix that hides a real failure: an ownership check that returns SKIPPED on a busy port could mask a broken browser leg. Mitigation: the refusal is a named CHECK FAIL with exit non-zero, and AC-1 is a positive test (stranger holds 8943, harness refuses rather than adopts). A diff read is not a test.
- TOCTOU race between preflight and spawn: covered by the PID-alive check on every poll tick plus the 3-attempt retry, then a named FAIL.
- Two harness copies racing: loser refuses at preflight; no kill exchange possible because port-scoped kills are deleted.
- Verification plan (6 runs): (a) positive gate, stranger on 8943 without `--port`, expect named FAIL, exit 1 by `$?`, stranger sentinel GET 200 before and after; (b) negative control, free port full legs, expect normal report and exit 0 on a good tree with `ss -ltn` showing 8943 closed after; (c) narrowing matrix of 3 runs: `--sim-only` with stranger present expects exit 3 with SKIPPED and no refusal, `--viewport=desktop` with stranger present expects exit 1 REFUSED, `--port=<free>` with stranger on 8943 expects normal serve on the free port with the stranger untouched. Pass threshold: 6/6 runs as specified; stranger alive in every refusal case; `fuser`/`pkill` grep clean; zero website bytes.
