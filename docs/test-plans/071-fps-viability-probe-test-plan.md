# Test Plan: Story 071 FPS viability probe (echo-rounds)

Source: `docs/stories/071-fps-viability-probe.md`. Code under test: PR #138 branch `feat/session33-071-fps-probe` (3 new files under `dev/fps-probe/`), tested from worktree `/home/jake/.hermes/flambeee/wt-pr138`.

## Setup
- Base: `54925ce`. Heads: pr137 `4394348`, pr138 `d655655`.
- `git fetch origin pull/137/head:pr137 --force; git fetch origin pull/138/head:pr138 --force`
- `git diff 54925ce..pr137 --stat` => 3 files, 197 insertions, 2 deletions.
- `git diff 54925ce..pr138 --stat` => 3 files, 442 insertions, 0 deletions.
- Overlap: none (`website/apps/index.html, website/index.html, website/sw.js` vs `dev/fps-probe/VERDICT.md, echo-rounds-probe.html, run-probe.js`).
- Toolchain: `node v26.10.0`, `chromium 155.0.8059.79`, `firefox 158.0` (scratch tarball).

## Cases
1. T1 diff-vs-base: file sets match PR bodies, no overlap, checker untouched (`git diff 54925ce..pr137 -- scripts/verify-website-currency.sh --stat` empty). PASS.
2. T2 harness chromium mechanic-loop: `node dev/fps-probe/run-probe.js chromium`. Expect fpsMean >= 30, p95 <= 33.4ms, inputDrops 0. Got `fpsMean 59.9, p95 16.7, drops 0/244, hold 100%, pointerLock error, gamepadNonEmpty 0`. PASS.
3. T3 harness firefox mechanic-loop: `node dev/fps-probe/run-probe.js firefox`. Got `fpsMean 60, p95 17.18, drops 0/244, hold 100%`. PASS (p95 17.18 vs PR-claimed 17.16, run-to-run jitter, still far above floor).
4. T4 sabotage chromium: `node dev/fps-probe/run-probe.js chromium sabotage=1`. Must FAIL floor. Got `fpsMean 19.6, p95 66.6, slowFrames 196`. FAIL as required. PASS (negative control works).
5. T5 sabotage firefox: `node dev/fps-probe/run-probe.js firefox sabotage=1`. Got `fpsMean 19.9, p95 50.48, slowFrames 199`. FAIL as required. PASS.
6. T6 empty-scene controls: `... chromium empty=1` => 59.9 FPS pass; `... firefox empty=1` => 60 FPS pass. Loop also passes so Scenario 4 does not trigger. PASS.
7. T7 controller matrix: `ls /dev/input/js*` => No such file; `/proc/bus/input/devices` => keyboard/mouse only, 0 joystick matches; probe JSON `gamepadNonEmpty 0` all runs, `pointerLock error` headless. VERDICT.md records keyboard-only as binding limitation, gamepad leg OPEN. PASS.
8. T8 falsifying test verbatim: Story 068 lines 56-58 text equals VERDICT.md lines 15/17 quote (both paragraphs). PASS.
9. T9 no-sprawl: `git diff 54925ce..pr138 --stat -- package.json package-lock.json node_modules src/ website/ scripts/ docs/` empty; only `dev/fps-probe/` touched; no native toolchain strings. PASS.
10. T10 copy/jakebot: VERDICT.md cites `20261017_011130_01bb1d`, no em dashes (`grep -P` empty). PASS.

## Verdict
CONDITIONAL PASS on measurable axes (render + input-event), with binding limitations (keyboard-only, headless Pointer Lock error, headless FPS is compute headroom). Matches PR #138 claim.
