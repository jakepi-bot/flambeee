# Test Plan: Story 041 - Website Currency Verification Before and After Release (Session 22)

**Story:** `docs/stories/041-website-currency-post-release-verification.md` (7 BDD scenarios)
**Type:** Process verification. The checker itself (`scripts/verify-website-currency.sh`) is NOT modified by this story and must stay byte-identical to the v0.19.0 shipped version.
**Run command:** `scripts/verify-website-currency.sh` from the repo root.

## What this story requires

A release step with **two runs** of the standing checker, both recorded in `flambeee-team/release-chain.md` with the command, exit code and auditable output:

- **Run 1, before release work:** proves the entering state is current and the live file matches the repo mirror.
- **Run 2, after the Wave 4 website What's New update and live sync:** proves the released version is named on the live site and the mirror is still byte-identical.

A release is not complete until run 2 is recorded and green.

## Checks

| # | Scenario | Check | How verified | Result |
|---|----------|-------|--------------|--------|
| 1 | Run 1 recorded | Command, exit code and full output recorded | Run 1 output captured below and in qa-results.md | PASS |
| 2 | Run 1 green on the entering state | Heading names the true latest tag, `cmp` exit 0, no em dashes/heavy emoji, real clickable anchors, all Play links relative and resolving | Run 1 output below | PASS |
| 3 | Run 2 recorded after the website update | Run 2 must execute after the What's New update to v0.20.0 and the live sync, then be recorded in `release-chain.md` | **PENDING. Cannot run before the release. Exact command below.** | PENDING |
| 4 | Post-release drift caught by the checker | If run 2 fails, the failure is recorded, fixed (small accuracy PR on the mirror plus live re-sync), and the green re-run recorded | Not triggered yet; depends on run 2 | PENDING |
| 5 | A release is not complete without run 2 | `release-chain.md` contains both runs before the session is declared complete | Run 2 not yet recorded | PENDING |
| 6 | Checker script unmodified; no new verification script | `git diff` of the script against the v0.19.0 shipped version is empty; no new checker added | Byte-identity check below | PASS |
| 7 | Recorded results are truthful | The pasted output is the real command output, not a summary | Run 1 output is verbatim; run 2 will be too | PASS for run 1, PENDING for run 2 |

## Run 1 output (verbatim, this session)

```
$ ./scripts/verify-website-currency.sh
== Story 038: website currency + mirror byte-identity ==
live   : /home/jake/.openclaw/workspace/share/Flambeee/index.html
mirror : /tmp/flambeee-wt-scout/website/index.html

cmp exit code: 0
PASS: live and repo mirror are byte-identical (cmp exit 0)
live lines:   1320
mirror lines: 1320

origin latest tag: v0.19.0
heading found: v0.19.0: Cinder puts a badge on your home screen
PASS: What's New heading names the true latest release tag (v0.19.0)

summary: If you installed Cinder to your home screen, its app icon now shows a small badge while today's quest is still waiting, and clears it the moment you finish and collect the reward. No notifications, no permission popups, no nag to install. The badge is a mirror of quest state you already had, so nothing about your save moves. Browsers without the feature play exactly as before.
PASS: summary contains no em dashes
PASS: summary contains no heavy emoji

Releases anchor: <a href="https://github.com/jakepi-bot/flambeee/releases" target="_blank" rel="noopener">Releases</a>
Blog anchor:     <a href="https://github.com/jakepi-bot/flambeee/blob/main/BLOG.md" target="_blank" rel="noopener">Blog</a>
PASS: Releases and Blog are real clickable <a href> anchors
PASS: no bare-text Releases URL

  ok: games/2048.html -> /home/jake/.openclaw/workspace/share/Flambeee/games/2048.html
  ok: games/cinder.html -> /home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html
  ok: games/minesweeper.html -> /home/jake/.openclaw/workspace/share/Flambeee/games/minesweeper.html
  ok: games/simon.html -> /home/jake/.openclaw/workspace/share/Flambeee/games/simon.html
  ok: games/wordfire.html -> /home/jake/.openclaw/workspace/share/Flambeee/games/wordfire.html
play links checked: 5
PASS: all Play links are relative games/*.html and their files exist

RESULT: PASS (all checks green)
EXIT=0
```

## Run 2 (PENDING, the parent must execute this)

Run 2 cannot happen before the release, so it is recorded here as PENDING rather than claimed green. The release is **not complete** until run 2 is recorded green.

Exact command the parent runs after the Wave 4 website What's New update and the live sync:

```
cd /home/jake/.openclaw/workspace/flambeee && ./scripts/verify-website-currency.sh; echo "RUN2_EXIT=$?"
```

Expected run-2 state: origin latest tag `v0.20.0`, heading `v0.20.0: Cinder says welcome back`, `cmp` exit 0 against the re-synced live file, no em dashes or heavy emoji in the new summary, both anchors still real `<a href>` links, 5 Play links resolving, exit 0. Record the command, exit code and full output in `flambeee-team/release-chain.md`.

## Checker script byte-identity check (scenario 6)

```
$ git show v0.19.0:scripts/verify-website-currency.sh | sha256sum
bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92  -
$ sha256sum scripts/verify-website-currency.sh
bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92  scripts/verify-website-currency.sh
$ git diff --name-status v0.19.0..HEAD -- scripts/
(empty)
```

Identical hashes and an empty diff mean the checker is the v0.19.0 script, unmodified, and no new verification script was added under `scripts/`.

## Verdict

Scenario 6 green. Scenarios 1, 2 and the run-1 half of 7 green with run 1 captured verbatim above. Scenarios 3, 4, 5 and the run-2 half of 7 are **PENDING run 2** and are not claimed as passed. No blocking defect in the entering state; run 1 is clean.
