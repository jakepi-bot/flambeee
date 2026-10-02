# Story 054: Website Currency and Deploy-Mirror Verification, Two Runs for the v0.25.0 Release (Session 27, P2, Standing Verification)

**Status:** Ready for verification (Session 27, 2026-10-02). Standing release step, carried forward from Stories 041, 043, 046, 049 and 052.
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (brand surface accuracy; a standing release step, not a build).
**Assigned to:** **Scout** owns both runs, the Cinder deploy-mirror comparison, and the recording in `flambeee-team/release-chain.md`. **Riven** owns the fix path if either run fails (Riven owns `share/Flambeee/index.html` and the repo mirror) and is the deploy-surface owner for the mirror re-sync. **Kai** peer-reviews only if a fix touches the game file. **Vigil** confirms the recorded results are truthful, including that no green was claimed that was not green.
**Tracked by:** Session 27 plan, Story 054. Extends `docs/stories/052-website-currency-verification-session26.md`, which extended `049`, which extended `046`, which extended `043`, which extended `041`, and `038` (the checker shipped in v0.19.0).

## Summary

`scripts/verify-website-currency.sh` has been the team's standing website check since v0.19.0
(Story 038). Story 041 (Session 22) turned it into a **two-run release step**. Stories 043, 046, 049
and 052 carried it forward. The step works only when the second run actually happens, and a
two-cron session splits the requirements wave from the release wave, which is exactly when a second
run gets dropped. So it is carried forward again as a scheduled story.

Two things are re-specified for this session's release (**target v0.25.0**; the latest tag at
session start is v0.24.0):

1. **Both runs, recorded.** Run 1 before the release work, on the entering state, with the heading
   naming v0.24.0. Run 2 after the release commit, the website What's New update and the live sync,
   with the heading naming the new tag (**expected v0.25.0**). Both recorded in
   `flambeee-team/release-chain.md` with the command, the exit code, and auditable output.
2. **The Cinder deploy-mirror comparison, recorded explicitly with `cmp` and sha256.** Story 053
   changes `src/cinder.html`, and the deploy mirror
   `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` is a **separate file outside
   the repo** that the website checker does not cover. This session records the `cmp` result and the
   sha256 of both files explicitly, at the absolute path.

The checker script is not modified, and no new verification script is added. One extra invocation of
an existing script, one `cmp`/sha256 record, and the recording discipline that makes a release
verified rather than assumed.

## Business value

- The two-run discipline survives the split-cron schedule. In this session the requirements wave and
  the release wave run in different jobs; a step that lives only in a process note is one scheduling
  change away from being dropped. A story survives.
- Post-release website drift is the exact defect class that reached compliance review in Session 21,
  and the checker caught a real pre-tag drift in Sessions 23, 24 and 26. Two recorded runs make the
  same mistake visible in the chain within the session that caused it, with exit codes.
- The game-mirror check closes a blind spot the website checker never had:
  `share/Flambeee/games/cinder.html` is not the file the checker looks at, and this session ships a
  change to the file it mirrors.
- Cheap and auditable: one extra invocation of an existing script and one `cmp`/sha256 record, both
  written into the chain file the team already keeps.

## User Story

As the Flambeee team shipping v0.25.0,
I want the website currency checker run before the release and again after the website What's New
update and live sync, with both runs and the Cinder deploy-mirror comparison recorded in the
release chain,
So that post-release drift and a stale game mirror are caught in the session that caused them, and
no release is declared verified on a single green run.

## Requirements

### 1. Run 1: before release

- Run `scripts/verify-website-currency.sh` from the repo root at the start of the release work,
  before any merge, tag, or website edit.
- Record in `flambeee-team/release-chain.md`: the exact command, the exit code, and the checker's
  auditable output - origin latest tag, heading found, `cmp` exit code, both link hrefs, and the
  Play-link count.
- If it fails, the failure is a defect in the **entering** session state. It is fixed before release
  work continues: a small accuracy PR, base `main`, owned by Riven. The failed run is recorded, then
  the green re-run is recorded after it. A failed run is never omitted.
- At session start the entering state is v0.24.0 (the heading names v0.24.0), so run 1 is expected
  green.

### 2. Run 2: after the release commit and the website What's New update and live sync

- After the release commit and the website What's New edit for v0.25.0, run
  `scripts/verify-website-currency.sh` **again**, against the new state.
- Run 2 is the run that matters: it verifies the released version is named on the live site, that
  the live file and the repo mirror are byte-identical after the sync, and that no em dashes or
  heavy emoji entered the new copy.
- Record the same set of facts as run 1, with the heading naming **v0.25.0**.
- **A release is not complete until run 2 is recorded and green.** Run 1 alone never satisfies this
  story.
- **The pre-tag drift case is a required failure, recorded not edited away.** If the live What's New
  heading names v0.25.0 **before** the v0.25.0 tag exists on `origin`, the checker MUST fail with
  exit 1, and that failure is recorded as a chain step. Do not edit the heading to make the checker
  pass. This exact real drift was caught in Sessions 24, 25 and 26, and the failure is the value of
  the check.

### 3. Cinder deploy-mirror comparison, recorded explicitly with `cmp` and sha256

- Compare `src/cinder.html` (in the repo) against the deploy mirror at the **ABSOLUTE path**
  `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`.
- Record both: the **`cmp` exit code** and the **sha256 of each file**.
- The absolute path is mandatory in the record. A relative `share/...` path from inside the repo
  resolves to nothing and is never used; the mirror lives outside the repository.
- The comparison is run **after Story 053 (and any other `src/cinder.html` story) is merged and the
  mirror is synced** for this release, and it is recorded as its own chain step.
- Story 053 changes `src/cinder.html`, so the sha256 **will differ** from its value at session start.
  The recorded values are the **post-merge** ones on both files, and they must be equal (`cmp`
  exit 0).
- If Story 053 lands no code change (possible if the proof shows no defect), the comparison records
  the **unchanged** sha256 on both files, still equal, still at the absolute path, and the record
  says so.
- If the two files differ, the mirror is re-synced and the comparison is re-run and re-recorded. A
  stale mirror fails the release step; it is not noted and passed.

### 4. Both runs and the mirror comparison recorded in the release chain

- All three records (run 1, run 2, mirror comparison) are written into
  `flambeee-team/release-chain.md`, each as its own step with its command and result.
- A claim of green that the recorded output does not support is a compliance violation (Vigil).

## Acceptance Criteria (Given/When/Then)

**Scenario 1: run 1 recorded before release**
- Given the session has entered with the latest tag at v0.24.0,
- When the release work is about to start,
- Then run 1 is executed and its command, exit code and output are recorded, with the heading naming
  v0.24.0.

**Scenario 2: run 1 green on the entering state**
- Given the entering state is current (website mirror and deployed copy in sync at v0.24.0),
- When run 1 executes,
- Then it exits 0.

**Scenario 3: run 2 recorded after the release**
- Given the v0.25.0 tag exists, the release commit is on `main`, the website What's New names
  v0.25.0, and the live file has been synced,
- When run 2 executes,
- Then it exits 0 and the record shows the heading naming v0.25.0.

**Scenario 4: Cinder deploy-mirror comparison recorded**
- Given Story 053 is merged and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`
  has been re-synced,
- When the comparison runs,
- Then `cmp` exits 0 and the sha256 of both files is recorded, equal, at the absolute path.

**Scenario 5: a stale mirror fails the step**
- Given the deploy mirror differs from `src/cinder.html`,
- When the comparison runs,
- Then it fails, the mirror is re-synced, and the comparison is re-run and re-recorded as a green
  step after the recorded failure.

**Scenario 6: a pre-tag heading drift fails with exit 1**
- Given the live What's New heading names v0.25.0 but no v0.25.0 tag exists on `origin`,
- When the checker executes,
- Then it exits 1 and the failure is recorded as a chain step, not edited away.

**Scenario 7: release not complete without run 2**
- Given run 1 is green and run 2 has not been recorded,
- When the release chain is claimed complete,
- Then that claim is false; the chain is incomplete.

**Scenario 8: checker unmodified**
- Given the merged change,
- When `scripts/verify-website-currency.sh` is compared to its v0.24.0 form,
- Then it is unmodified and no new verification script was added.

## Required Proof

- The three records in `flambeee-team/release-chain.md`, each with the exact command, exit code and
  auditable output.
- The `cmp` and sha256 values for the Cinder mirror, at the absolute path.
- Vigil confirms the recorded output supports every green claim.

## Non-Goals (out of scope for this story)

- No modification to `scripts/verify-website-currency.sh`.
- No new verification script.
- No website redesign. No new page. No brand asset change.
- No touching `jobs/`, `jobs-refactor-team/`, `jakebot/`, or any cron configuration.
