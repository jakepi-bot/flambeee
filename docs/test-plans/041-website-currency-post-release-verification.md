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
| 1 | Run 1 recorded | Command, exit code and full output recorded in release-chain.md | See release-chain.md, Story 041 run 1 | PASS |
| 2 | Run 1 green on the entering state | Heading names the true latest tag, `cmp` exit 0, no em dashes/heavy emoji, real clickable anchors, all Play links relative and resolving | Run 1 output | PASS |
| 3 | Run 2 recorded after the website update | Run 2 executed after the What's New update to v0.20.0 and the live sync, recorded in the same file | See release-chain.md, Story 041 run 2 | PASS |
| 4 | Post-release drift caught by the checker | If run 2 fails, the failure is recorded, fixed (small accuracy PR on the mirror + live re-sync), and the green re-run recorded | Not triggered; run 2 was green on the first attempt | N/A, see note |
| 5 | A release is not complete without run 2 | release-chain.md contains both runs before the session is declared complete | Both runs present | PASS |
| 6 | Checker script unmodified; no new verification script | `git diff` of the script against the v0.19.0 shipped version is empty; no new checker added | See the byte-identity check below | PASS |
| 7 | Recorded results are truthful | The pasted output is the real command output, not a summary | Output captured verbatim from the command | PASS (Vigil confirms) |

## Note on scenario 4

Scenario 4 describes the failure path, which is conditional: it only applies if run 2 catches drift. Run 2 was green on the first attempt this session, so the fix-and-re-run path was not exercised. That is recorded as N/A rather than as a pass, because claiming to have tested a path that did not run would be false.

The gap this story closes is real and from the immediately preceding session: in Session 21 the checker ran pre-release only and passed, the What's New edit happened afterwards with no re-run, and the resulting drift was caught by Vigil's compliance review instead of by the checker. This session runs the checker after the update as a required step.

## Checker script byte-identity check

```
$ git log --oneline -1 -- scripts/verify-website-currency.sh
8bea7ca Merge pull request #79 ... (v0.19.0)
$ git diff 8bea7ca HEAD -- scripts/verify-website-currency.sh
(empty)
```

No diff means the checker is the v0.19.0 script, unmodified, and no second checker was added under `scripts/`.

## Verdict

Scenario 6 verified green; scenarios 1, 2, 3, 5, 7 verified green by the recorded runs; scenario 4 is N/A because the failure path was not triggered. No blocking defects. GO.
