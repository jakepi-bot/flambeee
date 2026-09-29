# Story 052: Website Currency and Deploy-Mirror Verification, Two Runs for the v0.24.0 Release (Session 26, P3, Standing Verification)

**Status:** Ready for verification (Session 26, 2026-09-29). Standing release step, carried forward from Stories 041, 043, 046 and 049.
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P3 (brand surface accuracy; a standing release step, not a build).
**Assigned to:** **Scout** owns both runs, the Cinder deploy-mirror comparison, and the recording in `flambeee-team/release-chain.md`. **Riven** owns the fix path if either run fails (Riven owns `share/Flambeee/index.html` and the repo mirror `website/index.html`) and is the deploy-surface owner for the mirror re-sync. **Kai** peer-reviews only if a fix touches the game file. **Vigil** confirms the recorded results are truthful, including that no green was claimed that was not green.
**Tracked by:** Session 26 plan, Story 052. Extends `docs/stories/049-website-currency-verification-session25.md`, which extended `046`, which extended `043`, which extended `041`, and `038` (the checker shipped in v0.19.0).

## Summary

`scripts/verify-website-currency.sh` has been the team's standing website check since v0.19.0 (Story 038). Story 041 (Session 22) turned it into a **two-run release step**. Stories 043, 046 and 049 carried it forward. The step works only when the second run actually happens, and a two-cron session (this one) splits the requirements wave from the release wave, which is exactly when a second run gets dropped. So it is carried forward again as a scheduled story.

Two things are re-specified for this session's release (**target v0.24.0**; the latest tag at session start is v0.23.0):

1. **Both runs, recorded.** Run 1 before the release work, on the entering state, with the heading naming v0.23.0. Run 2 after the release commit and the website What's New update and live sync, with the heading naming the new tag (**expected v0.24.0**). Both recorded in `flambeee-team/release-chain.md` with the command, the exit code, and auditable output.
2. **The Cinder deploy-mirror comparison, recorded explicitly with `cmp` and sha256.** Story 050 changes `src/cinder.html`, and the deploy mirror `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` is a **separate file outside the repo** that the website checker does not cover. This session records the `cmp` result and the sha256 of both files explicitly, at the absolute path.

The checker script is not modified, and no new verification script is added. One extra invocation of an existing script, one `cmp`/sha256 record, and the recording discipline that makes a release verified rather than assumed.

## Business value

- The two-run discipline survives the split-cron schedule. In this session the requirements wave and the release wave run in different jobs; a step that lives only in a process note is one scheduling change away from being dropped. A story survives.
- Post-release website drift is the exact defect class that reached compliance review in Session 21, and the checker also caught a real pre-tag drift in Sessions 23 and 24. Two recorded runs make the same mistake visible in the chain within the session that caused it, with exit codes.
- The game-mirror check closes a blind spot the website checker never had: `share/Flambeee/games/cinder.html` is not the file the checker looks at, and this session ships a change to the file it mirrors.
- Cheap and auditable: one extra invocation of an existing script and one `cmp`/sha256 record, both written into the chain file the team already keeps.

## User Story

As the Flambeee team shipping v0.24.0,
I want the website currency checker run before the release and again after the website What's New update and live sync, with both runs and the Cinder deploy-mirror comparison recorded in the release chain,
So that post-release drift and a stale game mirror are caught in the session that caused them, and no release is declared verified on a single green run.

## Requirements

### 1. Run 1: before release

- Run `scripts/verify-website-currency.sh` from the repo root at the start of the release work, before any merge, tag, or website edit.
- Record in `flambeee-team/release-chain.md`: the exact command, the exit code, and the checker's auditable output - origin latest tag, heading found, `cmp` exit code, both link hrefs, and the Play-link count.
- If it fails, the failure is a defect in the **entering** session state. It is fixed before release work continues: a small accuracy PR, base `main`, owned by Riven. The failed run is recorded, then the green re-run is recorded after it. A failed run is never omitted.
- At session start the entering state is v0.23.0 (the heading names v0.23.0), so run 1 is expected green.

### 2. Run 2: after the release commit and the website What's New update and live sync

- After the release commit and the website What's New edit for v0.24.0, run `scripts/verify-website-currency.sh` **again**, against the new state.
- Run 2 is the run that matters: it verifies the released version is named on the live site, that the live file and the repo mirror are byte-identical after the sync, and that no em dashes or heavy emoji entered the new copy.
- Record the same set of facts as run 1, with the heading naming **v0.24.0**.
- **A release is not complete until run 2 is recorded and green.** Run 1 alone never satisfies this story.
- **The pre-tag drift case is a required failure, recorded not edited away.** If the live What's New heading names v0.24.0 **before** the v0.24.0 tag exists on `origin`, the checker MUST fail with exit 1, and that failure is recorded as a chain step. Do not edit the heading to make the checker pass. This exact real drift was caught in Sessions 24 and 25, and the failure is the value of the check.

### 3. Cinder deploy-mirror comparison, recorded explicitly with `cmp` and sha256

- Compare `src/cinder.html` (in the repo) against the deploy mirror at the **ABSOLUTE path** `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`.
- Record both: the **`cmp` exit code** and the **sha256 of each file**.
- The absolute path is mandatory in the record. A relative `share/...` path from inside the repo resolves to nothing and is never used; the mirror lives outside the repository.
- The comparison is run **after Story 050 (and any other `src/cinder.html` story) is merged and the mirror is synced** for this release, and it is recorded as its own chain step.
- Story 050 changes `src/cinder.html`, so the sha256 **will differ** from its value at session start. The recorded values are the **post-merge** ones on both files, and they must be equal (`cmp` exit 0).
- If Story 050 lands no code change (unlikely, but possible if the proof shows no defect), the comparison records the **unchanged** sha256 on both files, still equal, still at the absolute path, and the record says so.
- If the two files differ, the mirror is re-synced and the comparison is re-run and re-recorded. A stale mirror fails the release step; it is not noted and passed.

### 4. Both runs and the mirror comparison recorded in the release chain

- Both website runs and the mirror comparison are written into `flambeee-team/release-chain.md` as their own steps, so the chain shows the pre-flight and the post-flight side by side with exit codes, matching the file's existing format (step heading, fenced command and captured output, PASS/FAIL, one-line interpretation).
- `release-chain.md` is written **after** today's `session-plan.md`, preserving the chain convention from Sessions 19-25.
- If run 2 or the mirror comparison fails, the recorded entry states the failure and the fix, and the green re-run is recorded after it. **A failed run is never omitted from the chain.**

### 5. No build, no new tooling

- This story writes **no** new script, no new check, and no website or game change of its own. It reuses `scripts/verify-website-currency.sh` exactly as shipped.
- The script itself is **not modified**. If the script is found to be wrong or incomplete, that is a separate story, a separate PR, and a separate record, never a silent edit inside this one.
- No new verification script may be added by this story. The Cinder mirror comparison is a `cmp`/sha256 command recorded in the chain, not a new script.

### 6. Fix path, not a redesign

- If either website run fails, the fix makes the copy or the version true: a single-surface accuracy change plus a mirror re-sync. No redesign, no layout change, no new website feature.
- If the mirror comparison fails, the fix is a sync of the deploy mirror (plus a re-check that `src/cinder.html` is the file that should have been deployed), owned by Riven as the deploy-surface owner, with Kai peer-reviewing only the game-file half.
- Any fix re-runs its check and records the green result.
- A copy correction that also lands under Story 050 or Story 051 (a narrowed claim about the quest log or the welcome-back panel) is the same PR path, and it must be re-verified here by run 2.

### 7. Truthful recording

- Every recorded exit code and output line is the real output of the command that produced it.
- Nothing is reported green that was not green. A fix shows both the failure and the green re-run.
- If a run was skipped, that is recorded as skipped with the reason. A skipped run is never recorded as a pass.

## Out of scope

- Any change to `scripts/verify-website-currency.sh` itself.
- Any new verification script, wrapper, or harness.
- Any website redesign, layout change, or new What's New feature.
- Any game code change (Cinder, Wordfire, Minesweeper, Simon, 2048). Story 050 owns any Cinder change; this story only compares and records the result.
- Any change to the deploy pipeline, the Caddy sync, the service worker cache version, or the Caddy sync timing relative to the noon Bluesky post.
- Any change to the noon Bluesky posting flow.
- Any new game, leaderboard, multiplayer, or community-submitted game surfaced on the website.
- Any cron configuration, and any file under `jobs/`, `jobs-refactor-team/`, or `jakebot/`.

## Acceptance Criteria (BDD)

### Scenario 1: Run 1 before release, recorded (P3, Scout)
- **Given** the release work for Session 26 has not started
- **When** Scout runs `scripts/verify-website-currency.sh` from the repo root
- **Then** the command, the exit code, and the auditable output are recorded in `flambeee-team/release-chain.md`, and a non-zero exit stops release work and opens the fix path

### Scenario 2: Run 1 is green on the entering state (P3, Scout)
- **Given** the site is current at session start (the Story 038 checks hold; the heading names v0.23.0)
- **When** run 1 completes
- **Then** it reports PASS with exit 0, the What's New heading names the true latest `origin` tag, the live file and the repo mirror are byte-identical (`cmp` exit 0), the summary contains no em dashes and no heavy emoji, the Releases and Blog anchors are real `<a href>` links, and every relative Play-link target exists

### Scenario 3: Run 2 after the release and website update, recorded, heading names v0.24.0 (P3, Scout)
- **Given** the release commit has landed, the v0.24.0 tag exists on `origin`, and the website What's New has been updated for v0.24.0 and synced live
- **When** Scout runs `scripts/verify-website-currency.sh` again
- **Then** the command, the exit code, and the auditable output are recorded in `flambeee-team/release-chain.md` as the post-release run, with the heading naming v0.24.0

### Scenario 4: Cinder deploy mirror compared and recorded with `cmp` and sha256 (P3, Scout)
- **Given** Story 050 has been merged (or landed no change) and `src/cinder.html` is the released game file
- **When** the session compares `src/cinder.html` against `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`
- **Then** the record shows the absolute path, the `cmp` exit code, and the sha256 of both files, and the comparison is green (`cmp` exit 0, identical sha256), with the recorded values being the post-merge ones

### Scenario 5: A stale game mirror fails the step (P3, Scout + Riven)
- **Given** the mirror was not synced after the Story 050 merge, so the two files differ
- **When** the comparison runs
- **Then** it fails with a non-zero `cmp` exit and differing sha256 values, the mirror is re-synced, the comparison is re-run, the green result is recorded, and the failure itself stays in the chain

### Scenario 6: Post-release drift is caught by the checker, not by compliance (P3, Scout + Vigil)
- **Given** a session updates What's New but the live file is not re-synced, or the heading names the wrong version, or the new copy contains an em dash
- **When** run 2 executes
- **Then** it fails with a non-zero exit and a specific FAIL line naming the check, Riven lands a small accuracy fix on base `main`, the mirror is re-synced, and the re-run goes green and is recorded

### Scenario 7: A pre-tag heading drift fails with exit 1 and is recorded, not edited away (P3, Scout + Vigil)
- **Given** the live What's New heading names v0.24.0 while the v0.24.0 tag does not yet exist on `origin`
- **When** the checker runs
- **Then** it exits 1 with a FAIL line naming the heading-versus-tag mismatch, the failure is recorded as a chain step, and the heading is not edited to make the check pass

### Scenario 8: A release is not complete without run 2 (P3, Scout + Vigil)
- **Given** the release chain entry for Session 26
- **When** I read it
- **Then** both website runs and the mirror comparison appear with exit codes and sha256 values, and the chain does not declare the release verified on run 1 alone

### Scenario 9: The checker is not silently modified (P3, Kai + Vigil)
- **Given** this story's session
- **When** I inspect the repository
- **Then** `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state, and no new verification script was added by this story

### Scenario 10: Truthful recording (P3, Vigil)
- **Given** the two recorded runs and the mirror comparison in `release-chain.md`
- **When** Vigil compares them against the actual command output and the actual repository state
- **Then** the recorded exit codes, outputs, and sha256 values are truthful, nothing is reported green that was not green, and any failed run that was fixed shows both the failure and the green re-run

### Scenario 11: The absolute mirror path is used, not a relative path (P3, Scout + Vigil)
- **Given** the recorded mirror comparison
- **When** I read the chain entry
- **Then** it names `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` in full, and no relative `share/...` path appears anywhere in the record

### Scenario 12: A Story 050 or 051 change to public copy is covered by run 2 (P3, Scout + Riven)
- **Given** Story 050 (or a CEO-ruled Story 051 change) narrowed or changed a claim on the website What's New block after its proof
- **When** run 2 executes after the live sync
- **Then** the resulting copy is present in the verified state, and the chain records that the post-release run covered it

### Scenario 13: The chain is written after the session plan (P3, Scout)
- **Given** `flambeee-team/session-plan.md` for Session 26 and `flambeee-team/release-chain.md`
- **When** both are inspected
- **Then** the chain's Session 26 entry post-dates the session plan, preserving the chain convention from Sessions 19-25

## Proof / evidence required

1. **Run 1 record (Scout):** command, exit code, auditable output in `flambeee-team/release-chain.md`, heading naming v0.23.0.
2. **Run 2 record (Scout):** the same, after the v0.24.0 release and live sync, heading naming v0.24.0, and any pre-tag drift failure recorded with its exit 1.
3. **Mirror comparison record (Scout):** absolute path, `cmp` exit code, sha256 of both files, post-merge values equal.
4. **Checker-unmodified proof (Kai):** `scripts/verify-website-currency.sh` byte-identical to its v0.19.0 state (`git log` / blob hash), and no new script added.
5. **Truthfulness check (Vigil):** recorded values matched against actual command output and repository state.

## Open questions / ambiguities (need CEO input)

None for this story. It is a standing release step with no product decision. The release version target (v0.24.0) is set by the parent's release step, not by this story.
