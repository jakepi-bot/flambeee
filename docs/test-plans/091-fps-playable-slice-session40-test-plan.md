# Test Plan: Story 091 FPS Playable Echo-Rounds Slice (Session 40)

Source: `docs/stories/091-fps-playable-slice-session40.md`. P1 mechanism.
Base `7c1f2b9`. Prod diff under test: PR #161
(`feature/fps-playable-slice-091-session40`, 2 new files under
`dev/fps-probe/` only, 602 insertions, 0 deletions).

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee`.
- QA checks out the PR head (or fetches the pushed branch) and runs the
  harness from the repo root: `node dev/fps-probe/playable-slice-check-091.js`.
- Chromium present (`/usr/bin/chromium`). Firefox binary absent on this box
  (ENOENT, recorded by Kai); no Firefox run is claimed.
- Round geometry: 1280x800 DPR 1x (canvas backing store).

## Cases

1. T1 RED run pre-change (AC-1, Scenario 1). On the base tree without the
   slice files, run `node dev/fps-probe/playable-slice-check-091.js`.
   Expect exit non-zero with `slice HTML not found` plus the falsifying
   rule line. A zero exit here fails the plan.
2. T2 Green run merged, one round end to end (AC-2, Scenario 2). On the PR
   head, run the harness. Expect exit 0, outcome WIN, room cleared, win
   screen shown, no build step.
3. T3 Input survives the real loop (AC-3, Scenario 3). Expect 0 input drops,
   0 stuck, post-fire move window records input (`postFireInput` non-zero).
   Any drop is a recorded FAIL per the falsifying rule.
4. T4 Mouse-leg numbers preserved (AC-4, Scenario 4). Expect within run
   jitter of Story 089: about 691 counted frames, p95 16.7 inside the
   15.84-17.50 band, 0 slow frames over 33ms, 301/301 look applied,
   17/17 click-pulse-fade, litHits 1 at rate 1 with unlitHits 0, shooter
   reveal 17/17. A regression is a fail, not a new baseline.
5. T5 Frame numbers in band (AC-5, Scenario 5). Expect at least 600 counted
   frames with first 30 excluded, p95 inside 15.84-17.50, slow-frame count
   stated. A miss is recorded as a finding, not rounded away.
6. T6 Gamepad leg open-blocked (AC-7, Scenario 6). Expect the run to state
   OPEN-BLOCKED-ON-HARDWARE with `gamepadNonEmpty` 0 and no controller
   claim.
7. T7 Harness-only diff (AC-8, Scenario 7). `git diff --stat` against base
   shows only the 2 new files under `dev/fps-probe/`, zero lines in `src/`,
   `website/`, `share/`, no dependency, no native toolchain, no build step.
8. T8 Browser verification via Playwright (independent of the node
   harness). Load `dev/fps-probe/echo-rounds-slice-091.html` from a local
   file URL or local server in Chromium 1280x800 DPR 1x, exercise real
   input if the page supports it, paste real output. Firefox is NOT run
   (binary absent).
9. T9 Copy rule (AC-10). New files use plain punctuation, no em dashes,
   no heavy emoji.

## Real output

Pasted by QA at run time into `flambeee-team/qa-results.md` (Session 40):
full harness command plus exit code plus output for RED and green runs,
Playwright load/input evidence, and per-case pass/fail.

## Verdict

Recorded in `qa-results.md` after the re-run. Approve PR #161 only if
AC-1 through AC-10 hold on the merged tree.
