# Test Plan: Story 073 Website Currency Session 33 (Run 1 only)

Source: `docs/stories/073-website-currency-session33.md`. Standing verification, no new code. Checker frozen at `scripts/verify-website-currency.sh`. Run 1 executed on `main` at base `54925ce`. Run 2 explicitly out of scope (not attempted).

## Setup
- Workdir: `/home/jake/.hermes/flambeee/flambeee` on `main` (`54925ce`).
- `git diff 54925ce..pr137 --stat -- scripts/verify-website-currency.sh` => empty (checker untouched in PR137).
- `git diff 54925ce..pr138 --stat -- scripts/verify-website-currency.sh` => empty.

## Cases
1. T1 Run 1 on main: `bash scripts/verify-website-currency.sh; echo EXIT_CODE:$?`. Expect exit 1 with `FAIL: live file not found`. Got exactly that (see output below). PASS (matches PR137 recorded Run 1).
2. T2 live-path measurement: `ls -la /home/jake/share/Flambeee/`. Expect exit 2 `No such file or directory`. Got exit 2. PASS.
3. T3 checker frozen: `git diff --stat -- scripts/verify-website-currency.sh` on main => empty. PASS.
4. T4 repo-mirror facts (read-only, main): `What's New` heading `v0.30.0`, latest tag `v0.30.0` (MATCH), 6 Play links (`games/2048, afterglow, cinder, minesweeper, simon, wordfire`), `GAME_ORDER` 6/6 including afterglow, `CACHE_VERSION 7` on main. Recorded. PASS.
5. T5 PR137 Run 1 claim match: PR137 body records exit 1 + same live-file FAIL + ls exit 2. Matches independent re-run. PASS.
6. T6 Run 2 not attempted. PASS (scope guard).

## Real output (main, 2026-10-17)
```
== Story 038: website currency + mirror byte-identity ==
live   : /home/jake/share/Flambeee/index.html
mirror : /home/jake/.hermes/flambeee/flambeee/website/index.html

FAIL: live file not found: /home/jake/share/Flambeee/index.html

RESULT: FAIL (1 check(s) failed)
EXIT_CODE:1
```
```
ls: cannot access '/home/jake/share/Flambeee/': No such file or directory
LS_EXIT:2
```

## Verdict
Run 1 reproduced exactly. AC-1 holds pre-merge. AC-2/AC-3 (post-tag Run 2, cmp+sha256) deferred to release wave by design.
