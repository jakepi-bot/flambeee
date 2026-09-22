# Test Plan: Story 043 - Website Currency Verification Before and After the v0.21.0 Release (Session 23)

**Story:** `docs/stories/043-website-currency-post-release-verification.md` (10 BDD scenarios)
**Checker under test:** `scripts/verify-website-currency.sh` (shipped v0.19.0, Story 038). Read only. Not modified. No new verification script added by this story.
**Live site:** `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE, outside the repo)
**Repo mirror:** `/home/jake/.openclaw/workspace/flambeee/website/index.html`
**Cinder deploy mirror:** `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` (ABSOLUTE, outside the repo)
**Cinder source:** `/home/jake/.openclaw/workspace/flambeee/src/cinder.html`
**Recording target:** `/home/jake/.openclaw/workspace/flambeee-team/release-chain.md` (outside the repo, never committed)
**Owner:** Scout owns both runs and the recording. Riven owns the fix path. Vigil confirms the record is truthful.

## What this story requires

Two invocations of an existing script plus one `cmp`/`sha256` record, all written into the release chain as their own steps:

1. **Run 1, pre-release.** Proves the entering state is current and in sync, before any merge, tag, or website edit.
2. **Run 2, post-release.** After the Wave 4 What's New update for v0.21.0 and its live sync. This is the run that proves the released version is named live and that the live file and repo mirror are still byte-identical.
3. **Cinder deploy-mirror comparison.** `cmp` and `sha256` of `src/cinder.html` against the ABSOLUTE mirror path, after the Story 042 merge and mirror sync.

**A release is not complete until run 2 is recorded and green, and the mirror comparison is green. Run 1 alone never satisfies the step.**

## Checks

1. Run 1 executes the checker from the repo root with no arguments, and the command, exit code, and auditable output are recorded.
2. Run 1 reports PASS with exit 0: heading names the true latest `origin` tag, live vs mirror byte-identical (`cmp` exit 0), summary has no em dashes and no heavy emoji, Releases and Blog are real `<a href>` anchors, no bare-text Releases URL, and every relative Play-link target exists.
3. Run 2 executes the same command after the What's New update and live sync, recorded with the same facts, heading naming v0.21.0.
4. The Cinder deploy mirror is compared with the ABSOLUTE path, and the `cmp` exit code plus the sha256 of both files are recorded.
5. A stale game mirror fails the step: non-zero `cmp`, differing sha256, mirror re-synced, comparison re-run, green result recorded, and the failure itself stays in the chain.
6. Post-release website drift is caught by the checker (non-zero exit and a specific FAIL line naming the check), fixed by a small accuracy PR on base `main`, re-synced, and the green re-run recorded.
7. The chain declares nothing verified on run 1 alone.
8. `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state, and no new verification script was added.
9. Every recorded exit code, output line, and sha256 value is the real output of the command that produced it. Nothing green that was not green.
10. The recorded mirror comparison names the absolute path in full, and no relative `share/...` path appears anywhere in the record.

## Exact commands (run 2 and the mirror comparison)

Run 2 is prepared now and executed after the release work. Run 2 as written here, from the repo root:

```
cd /home/jake/.openclaw/workspace/flambeee
bash scripts/verify-website-currency.sh
echo "RUN2_EXIT=$?"
```

Cinder deploy-mirror comparison, absolute paths, from anywhere:

```
cmp /home/jake/.openclaw/workspace/flambeee/src/cinder.html \
    /home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html
echo "CMP_EXIT=$?"
sha256sum /home/jake/.openclaw/workspace/flambeee/src/cinder.html \
          /home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html
```

Never a relative `share/...` from inside the repo: the mirror lives outside the repository and a relative path resolves to nothing.

## Record format (per chain step)

Each step goes into `flambeee-team/release-chain.md` in the file's existing style: a step heading, the fenced command and captured output verbatim, a PASS/FAIL line, and a one-line interpretation. Suggested headings, matching open question 1's recommendation:

- `### Website currency, pre-release (run 1)`
- `### Website currency, post-release (run 2)`
- `### Cinder deploy mirror, post-merge (cmp + sha256)`

Each step records: the exact command, the exit code, `origin latest tag`, `heading found`, `cmp exit code`, both link hrefs, the Play-link count, and (for the mirror step) the absolute path, `cmp` exit code, and both sha256 values.

## What is NOT tested, and why

- The checker script's own correctness is not re-verified beyond byte-identity. Story 043 forbids modifying it; a real checker defect is a separate story and a separate PR.
- The relative-`share/...` path is not tested as a working command, because it is the documented wrong form. Scenario 10 checks that no such path appears in the record.
- Story 042's game behaviour is tested in `042-cinder-welcomeback-streak-and-once-per-gap.md`. This plan only compares and records the Cinder file.

## Verdict

Recorded in `flambeee-team/qa-results.md`, Session 23 section: run 1 result with exit code, the mirror comparison state, and an explicit statement that run 2 is pending until the post-release step is executed. Run 2 is never claimed green before it is run.
