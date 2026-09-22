# Story 043: Website Currency Verification Before and After the v0.21.0 Release (Session 23, P2)

**Status:** Ready for verification (Session 23, second half, 2026-09-22). Carries forward the Story 041 two-run release step, extended with a Cinder deploy-mirror check for this session.
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (brand surface accuracy; a standing release step, not a build).
**Assigned to:** **Scout** owns both runs and the recording in `flambeee-team/release-chain.md`. **Riven** owns the fix path if either run fails (Riven owns `share/Flambeee/index.html` and the repo mirror `website/index.html`). **Kai** peer-reviews only if a fix is needed. **Vigil** confirms the recorded results are truthful, including that no green was claimed that was not green.
**Tracked by:** Session 23 plan Priority 2. Extends `docs/stories/041-website-currency-post-release-verification.md` (which extends `docs/stories/038-website-currency-verification.md`, the checker shipped in v0.19.0).

## Summary

`scripts/verify-website-currency.sh` has been the team's standing website check since v0.19.0 (Story 038). Story 041 (Session 22) turned it into a **two-run release step**: run 1 before the release work, run 2 after the Wave 4 website What's New update and the live-file sync, with both runs recorded in the release chain. That worked in Session 22, but it worked because a human remembered to run the second pass twice; a continuation job that drops the step drops the verification with it.

This story carries the two-run step forward as a story, so it is scheduled work in Session 23 rather than an item in a process note. Two things are new:

1. **The step is re-specified for this session's release (v0.21.0).** Run 1 proves the entering state is current and in sync, before any merge, tag, or website edit. Run 2 runs after the Wave 4 What's New update and live sync, and is the run that proves the released version is named on the live site and that the live file and the repo mirror are still byte-identical. Recording both runs is what makes a release verified.
2. **The Cinder deploy mirror is now explicitly recorded.** Story 042 touches `src/cinder.html`, and the deploy mirror `share/Flambeee/games/cinder.html` is a **separate file outside the repo**. The currency checker covers `website/index.html`, not the game files. So this story requires the session to record, explicitly, the `cmp` result and the **sha256** of `src/cinder.html` against `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`, at the ABSOLUTE path, never as a relative `share/...` from inside the repo.

The checker script itself is not modified, and no new verification script is added. This story adds a second invocation, a recording requirement, and one `cmp`/`sha256` record for a file the checker does not cover.

## Business value

- The two-run discipline survives the split-cron schedule. In a two-cron session the requirements wave and the release wave run in different jobs; a step that lives only in a process note is one scheduling change away from being dropped. A story survives.
- Post-release website drift was the exact defect class that reached compliance review in Session 21. Two recorded runs make the same mistake visible in the chain within the session that caused it, with exit codes.
- The game mirror check closes a blind spot the website checker never had: `share/Flambeee/games/cinder.html` is not the file the checker looks at, and this session ships a change to the file it mirrors.
- Cheap and auditable. One extra invocation of an existing script and one `cmp`/`sha256` record, both written into the same chain file the team already keeps.

## User Story

As the Flambeee team shipping v0.21.0,
I want the website currency checker run before the release and again after the website What's New update, with both runs and the Cinder deploy-mirror comparison recorded in the release chain,
So that post-release drift and a stale game mirror are caught in the session that caused them, and no release is declared verified on a single green run.

## Requirements

### 1. Run 1: before release

- Run `scripts/verify-website-currency.sh` from the repo root at the start of the release work, before any merge, tag, or website edit.
- Record in `flambeee-team/release-chain.md`: the exact command, the exit code, and the checker's auditable output - origin latest tag, heading found, `cmp` exit code, both link hrefs, and the Play-link count.
- If it fails, the failure is a defect in the **entering** session state. It is fixed before release work continues: a small accuracy PR, base `main`, owned by Riven. The failed run is recorded, then the green re-run is recorded after it.

### 2. Run 2: after the Wave 4 website What's New update and live sync

- After the release commit and the website What's New edit for v0.21.0, run `scripts/verify-website-currency.sh` **again**, against the new state.
- Run 2 is the run that matters: it verifies the released version is named on the live site, that the live file and the repo mirror are byte-identical after the sync, and that no em dashes or heavy emoji entered the new copy.
- Record the same set of facts as run 1.
- **A release is not complete until run 2 is recorded and green.** Run 1 alone never satisfies this story.

### 3. Cinder deploy-mirror comparison, recorded explicitly

- Compare `src/cinder.html` (in the repo) against the deploy mirror at the **ABSOLUTE path** `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`.
- Record both: the `cmp` exit code and the **sha256** of each file.
- The absolute path is mandatory in the record. A relative `share/...` path from inside the repo resolves to nothing and is never used; the mirror lives outside the repository.
- The comparison is run after Story 042 is merged and the mirror is synced for this release, and it is recorded as its own chain step.
- If the two files differ, the mirror is re-synced and the comparison is re-run and re-recorded. A stale mirror fails the release step; it is not noted and passed.

### 4. Both runs recorded in the release chain

- Both website runs and the mirror comparison are written into `flambeee-team/release-chain.md` as their own steps, so the chain shows the pre-flight and the post-flight side by side with exit codes, matching the file's existing format (step heading, fenced command and captured output, PASS/FAIL, one-line interpretation).
- `release-chain.md` is written **after** today's `session-plan.md`, preserving the chain convention from Sessions 19-22.
- If run 2 or the mirror comparison fails, the recorded entry states the failure and the fix, and the green re-run is recorded after it. **A failed run is never omitted from the chain.**

### 5. No build, no new tooling

- This story writes **no** new script, no new check, and no website or game change of its own. It reuses `scripts/verify-website-currency.sh` exactly as shipped.
- The script itself is **not modified**. If the script is found to be wrong or incomplete, that is a separate story, a separate PR, and a separate record - never a silent edit inside this one.
- No new verification script may be added by this story. The Cinder mirror comparison is a `cmp`/`sha256` command recorded in the chain, not a new script.

### 6. Fix path, not a redesign

- If either website run fails, the fix makes the copy or the version true: a single-surface accuracy change plus a mirror re-sync. No redesign, no layout change, no new website feature.
- If the mirror comparison fails, the fix is a sync of the deploy mirror (and a re-check that `src/cinder.html` is the file that should have been deployed), owned by Riven as the deploy-surface owner, with Kai peer-reviewing only the game-file half.
- Any fix re-runs its check and records the green result.

### 7. Truthful recording

- Every recorded exit code and output line is the real output of the command that produced it.
- Nothing is reported green that was not green. A fix shows both the failure and the green re-run.
- If a run was skipped, that is recorded as skipped with the reason. A skipped run is never recorded as a pass.

## Out of scope

- Any change to `scripts/verify-website-currency.sh` itself.
- Any new verification script, wrapper, or harness.
- Any website redesign, layout change, or new What's New feature.
- Any game code change (Cinder, Wordfire, Minesweeper, Simon, 2048). Story 042 owns the Cinder change; this story only compares and records the result.
- Any change to the deploy pipeline, the Caddy sync, or the service worker cache version.
- Any change to the noon Bluesky posting flow.

## Acceptance Criteria (BDD)

### Scenario 1: Run 1 before release, recorded (P2, Scout)
- **Given** the release work for Session 23 has not started
- **When** Scout runs `scripts/verify-website-currency.sh` from the repo root
- **Then** the command, the exit code, and the auditable output are recorded in `flambeee-team/release-chain.md`, and a non-zero exit stops release work and opens the fix path

### Scenario 2: Run 1 is green on the entering state (P2, Scout)
- **Given** the site is current at session start (the Story 038 checks hold)
- **When** run 1 completes
- **Then** it reports PASS with exit 0, the What's New heading names the true latest `origin` tag, the live file and the repo mirror are byte-identical (`cmp` exit 0), the summary contains no em dashes and no heavy emoji, the Releases and Blog anchors are real `<a href>` links, and every relative Play-link target exists

### Scenario 3: Run 2 after the Wave 4 website update, recorded (P2, Scout)
- **Given** the release commit has landed and the website What's New has been updated for v0.21.0 and synced live
- **When** Scout runs `scripts/verify-website-currency.sh` again
- **Then** the command, the exit code, and the auditable output are recorded in `flambeee-team/release-chain.md` as the post-release run, with the heading naming v0.21.0

### Scenario 4: Cinder deploy mirror compared and recorded with sha256 (P2, Scout)
- **Given** Story 042 has been merged and `src/cinder.html` is the released game file
- **When** the session compares `src/cinder.html` against `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`
- **Then** the record shows the absolute path, the `cmp` exit code, and the sha256 of both files, and the comparison is green (`cmp` exit 0, identical sha256)

### Scenario 5: A stale game mirror fails the step (P2, Scout + Riven)
- **Given** the mirror was not synced after the Story 042 merge, so the two files differ
- **When** the comparison runs
- **Then** it fails with a non-zero `cmp` exit and differing sha256 values, the mirror is re-synced, the comparison is re-run, the green result is recorded, and the failure itself stays in the chain

### Scenario 6: Post-release drift is caught by the checker, not by compliance (P2, Scout + Vigil)
- **Given** a session updates What's New but the live file is not re-synced, or the heading names the wrong version, or the new copy contains an em dash
- **When** run 2 executes
- **Then** it fails with a non-zero exit and a specific FAIL line naming the check, Riven lands a small accuracy fix on base `main`, the mirror is re-synced, and the re-run goes green and is recorded

### Scenario 7: A release is not complete without run 2 (P2, Scout + Vigil)
- **Given** the release chain entry for Session 23
- **When** I read it
- **Then** both website runs and the mirror comparison appear with exit codes and sha256 values, and the chain does not declare the release verified on run 1 alone

### Scenario 8: The checker is not silently modified (P2, Kai + Vigil)
- **Given** this story's session
- **When** I inspect the repository
- **Then** `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state, and no new verification script was added by this story

### Scenario 9: Truthful recording (P2, Vigil)
- **Given** the two recorded runs and the mirror comparison in `release-chain.md`
- **When** Vigil compares them against the actual command output and the actual repository state
- **Then** the recorded exit codes, outputs, and sha256 values are truthful, nothing is reported green that was not green, and any failed run that was fixed shows both the failure and the green re-run

### Scenario 10: The absolute mirror path is used, not a relative path (P2, Scout + Vigil)
- **Given** the recorded mirror comparison
- **When** I read the chain entry
- **Then** it names `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` in full, and no relative `share/...` path appears anywhere in the record

## Technical notes (Quinn)

- **The checker:** `scripts/verify-website-currency.sh` (shipped v0.19.0, Story 038; carried forward by Story 041). It resolves the latest tag with `git ls-remote --tags origin` (never a hardcoded version), checks live-vs-mirror byte identity, the What's New heading, em dashes and heavy emoji in the summary, real clickable Releases and Blog anchors, and relative `games/*.html` Play links whose targets exist. Run it exactly as documented: `scripts/verify-website-currency.sh` from the repo root. Non-zero exit on any failure.
- **Reference run, verified for this story's specification.** Run at requirements time (2026-09-22) against the session's entering state: `RESULT: PASS (all checks green)`, exit 0. Reported `origin latest tag: v0.20.0`; heading found `v0.20.0: Cinder says welcome back`; live and mirror byte-identical (`cmp exit code: 0`), both 1320 lines; the two anchors are `https://github.com/jakepi-bot/flambeee/releases` and `https://github.com/jakepi-bot/flambeee/blob/main/BLOG.md`; `play links checked: 5`, all resolving under `/home/jake/.openclaw/workspace/share/Flambeee/games/`. This is the expected shape of run 1; run 2 differs in that the heading must name the **new** tag.
- **Paths the checker touches (do not change):** live `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE, outside the repo), repo mirror `website/index.html`, and the `games/` directory the Play links resolve against.
- **The game mirror (new in this story):** source `src/cinder.html`, mirror `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. At requirements time both read sha256 `dde7125b99bb2ac32660d453ed714933e1ab988f639b516b1a16110125763482` and `cmp` exits 0. Story 042 will change `src/cinder.html`, so **the sha256 will change at implementation time and the mirror must be re-synced after the merge**; the recorded values are the post-merge ones. The checker does not cover this file; that is why this story records the comparison directly.
- **The recording target:** `/home/jake/.openclaw/workspace/flambeee-team/release-chain.md` (outside the repo, never committed). Follow the existing chain format. The file must be written after today's `session-plan.md` (chain convention from Sessions 19-22).
- **Why run 2 exists (evidence):** Session 21 ran the checker pre-release only, passed, and then shipped a What's New edit without a re-run; the resulting drift (What's New still reading v0.18.1 while v0.19.0 was tagged) was found by Vigil's compliance review instead of by the checker. Session 22 executed both runs and both were green (recorded in `release-chain.md`). This story keeps that discipline scheduled in a two-cron session.
- **Ordering within the session:** run 1 belongs in the pre-release step, before merge/tag/website edit. Run 2 belongs immediately after the Wave 4 website What's New update and its live sync. The mirror comparison belongs immediately after the Story 042 merge and the mirror sync. All three are release-chain steps, not dev-wave work items.
- **No dependency on the dev wave outcome.** This story is independent of Story 042: it can be executed even if Story 042 lands nothing, in which case run 2 verifies the unchanged, correctly-synced state and the mirror comparison records the unchanged sha256.
- **Why the absolute path rule is in the story:** the deploy mirror is outside the repository. A relative `share/...` path from inside the repo resolves to a nonexistent path and would silently produce an empty or failed comparison that is easy to misread. The absolute path is the only correct form, and Scenario 10 enforces it.

## Visual Description (Quinn)

No visual change at all. This story adds no website surface, no page element, no copy, and no game-file change of its own. The website What's New block keeps its current rendering (flame "What's new" badge, bold version heading, muted summary, Releases and Blog links right-aligned, wrapping below the text on mobile); the only difference this session is the version it names, which Story 043 verifies twice rather than renders. The Cinder panel is unchanged by this story; its one changed line belongs to Story 042 and is described there.

## Open questions

1. **Recording granularity (recommended, confirm).** Recommendation: three chain steps - "website currency, pre-release", "website currency, post-release", and "Cinder deploy mirror, post-merge" - each with the command, exit code, and captured output, matching the file's existing style. Confirm if the parent prefers the mirror comparison folded into the post-release step as a sub-item.
2. **If the checker itself is wrong.** Recommendation: treat a real checker defect as a separate story and a separate PR, and record it as such. Do not fold a script change into this story. This keeps Scenario 8 (no silent modification) enforceable.
3. **Run-2 ordering relative to the written chain entry.** Recommendation: run 2 immediately after the website What's New update and live sync, before the release chain is declared complete. If the parent prefers to append it after the written entry, the same file takes it. No CEO input needed.
4. **Mirror comparison timing (recommendation).** Run the `cmp`/`sha256` comparison after the Story 042 merge and the mirror sync, before the release is declared complete, so a stale mirror cannot ride into the tag.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 2 and the Story 041 pattern it carries forward.
