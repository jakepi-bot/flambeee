# Test Plan — Story 065: Website currency and deploy mirror verification, Session 30 (P2)

**Source:** `docs/stories/065-website-currency-session30.md` (Quinn, Wave 2).
**Target:** PR #124 (Riven, branch `riven/065-website-currency`, defects 1+3).
Defect 2 (What's New heading) and run 2 are release-wave steps, not this PR.

## 1. BDD scenario coverage

| # | Scenario (story) | Test | Method | Pass bar |
|---|---|---|---|---|
| 1 | Game count agrees | U1 heading/cards/About | Read PR #124 mirror: heading text, Play-link count, About stat row | `Six games, one arcade`, 6 Play links incl. `games/afterglow.html`, About row `6 / Games shipped` |
| 2 | What's New names the release | DEFERRED to release wave | Run 2 after tag v0.28.0; resolve latest tag via `git ls-remote --tags origin`, never hardcoded | Heading == true latest tag, accurate summary |
| 3 | Rotation covers Afterglow | U2 GAME_ORDER | Read `GAME_ORDER` on PR #124 mirror | All 6 games incl. `afterglow`, comment says six |
| 4 | Run 1 recorded | U3 checker run 1 | `bash scripts/verify-website-currency.sh` pre-merge, exact exit + output | Recorded honestly (exit 1, stale hardcoded live path; not a product defect, checker frozen) |
| 5 | Run 2 green | DEFERRED to release wave | Checker post-tag + live sync | exit 0, heading-vs-tag match |
| 6 | Mirrors byte-identical | U4 real-path equivalents (pre-release state) | `cmp` + sha256 pairs at absolute paths; `CACHE_VERSION` from both sw.js | Pre-release: index differs exactly at the two fixed lines (sync is release step); sw.js identical (`d9353e6b…`, v5 both sides); afterglow live vs candidate differs (sync is release step) |
| 7 | Checker frozen | U5 `git diff --stat` on `scripts/verify-website-currency.sh` | Empty output; `git status` clean on that path | Unmodified |

## 2. Edge and boundary cases

- E1 Live-vs-mirror `cmp` mismatch handling (the load-bearing rule): on a mismatch, check `git log`/`git status` on the mirror first and restore the stale side FROM the committed side; never hand-write into `/home/jake/share/Flambeee/`. Verified: mirror `website/index.html` clean, committed pre-fix text confirmed via `git show HEAD:...`.
- E2 PR #124 scope: exactly `website/index.html`, 5 insertions / 5 deletions, two hunks (heading line 674, `GAME_ORDER` line 1109 + comment). No `scripts/`, no game files.
- E3 `sw.js` unchanged on both sides with equal sha256: no `CACHE_VERSION` bump needed since the shell did not change (both sides still agree, recorded either way per story).
- E4 Checker run 1 FAIL is environmental (hardcoded `/home/jake/.openclaw/workspace/share/...` vs real `/home/jake/share/Flambeee/...`), reported not hidden, checker NOT fixed (frozen by story).
- E5 Defect 2 status: What's New still `v0.27.0` on the PR #124 tree (line 724) while live release is `v0.27.1`. Expected pre-release; fixed at run 2 by the release wave, not this PR.

## 3. Results (Session 30 QA re-run, real output)

- U1: heading `Six games, one arcade`; 6 unique Play links (`2048, afterglow, cinder, minesweeper, simon, wordfire`); About row `6 / Games shipped`. AC-1 holds.
- U2: `GAME_ORDER = ['cinder', 'wordfire', 'minesweeper', 'simon', '2048', 'afterglow']`. AC-3 holds.
- U3: exit 1, `FAIL: live file not found: /home/jake/.openclaw/workspace/share/Flambeee/index.html`. AC-4 recorded.
- U4: index sha live `2609efd7…` vs mirror `69994413…` (differ at line 674 + GAME_ORDER hunk only); sw.js `d9353e6b…` both sides, `CACHE_VERSION = 5` both sides; afterglow live `17dcbb15…` vs candidate `bb12a139…` (deploy sync pending release wave).
- U5: `git diff` on checker path empty. AC-7 holds.
- Full pasted outputs: `flambeee-team/qa-results.md` (Session 30).

## 4. Verdict

Defects 1+3 fixed per AC-1/AC-3; AC-4/AC-7 hold. AC-2/AC-5/AC-6(run 2 + sync) are
release-wave steps. No blocking defects in PR #124.
