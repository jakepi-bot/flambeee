# Story 041: Website Currency Verification Before and After Release (Session 22, P2)

**Status:** Ready for verification (Session 22, second half, 2026-09-20). Extends Story 038.
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (brand surface accuracy; a standing process check, not a build).
**Assigned to:** **Scout** owns the two runs and records both results (Scout owns verification). **Riven** owns the fix path if either run fails (Riven owns `share/Flambeee/index.html` and the repo mirror `website/index.html`). **Kai** peer-reviews only if a fix is needed. **Vigil** confirms the recorded results are truthful. **Palette** co-owns the clickable-links check per the standing UX directive.
**Tracked by:** Session 22 plan Priority 3. Extends `docs/stories/038-website-currency-verification.md` (the checker itself, shipped in v0.19.0). Closes the Session 21 process gap recorded in `flambeee-team/SESSION-LOG.md`: "Process fix needed: run the currency checker AFTER the release commit as a required release step, since its absence is exactly how the website drift reached compliance."

## Summary

`scripts/verify-website-currency.sh` shipped in v0.19.0 (Story 038). It resolves the latest tag from `git ls-remote --tags origin` at run time and checks live-vs-mirror `cmp` byte-identity, the What's New heading, no em dashes or heavy emoji in the summary, real clickable Releases and Blog anchors, and relative `games/*.html` Play links whose targets exist. It exits non-zero on any failure.

The checker itself is not the problem. **When it runs is.** In Session 21 it ran before the release, passed, and the session then updated the website's What's New to v0.19.0 without re-running it. The website drift that Vigil caught (What's New still read v0.18.1 while v0.19.0 was tagged) was found by a human review instead of by the checker, even though the checker would have caught it. The pre-release pass was green; the post-release state was never verified.

This story makes the check a **two-run standing step** in the release chain:

1. **Run 1, before release** - prove the site is current and the mirror is in sync as the session begins, so any drift entering the session is caught before anyone builds on it.
2. **Run 2, after the Wave 4 website What's New update** - prove the site is *still* current and in sync after the release commit and the What's New edit, which is the only run that can catch post-release drift.

**Both runs are recorded in `flambeee-team/release-chain.md`**, with the command, the exit code, and the key auditable lines (origin latest tag, heading found, `cmp` exit code, link hrefs). A release is not considered verified until run 2 is recorded.

## Business value

- Closes the exact gap that let website drift reach compliance review in Session 21. The checker existed; the discipline did not.
- Converts a manual, human-caught defect class into an automated, recorded one. Vigil should never be the tool that finds stale website copy.
- Cheap: the checker already exists and runs in seconds. This story adds a second invocation and a recording requirement, not new tooling.
- Makes the release chain auditable end to end: every release shows a green pre-flight and a green post-flight, on disk, with exit codes.

## User Story

As the team,
I want the website currency checker run before release and again after the website What's New update, with both results recorded in the release chain,
So that post-release website drift is caught by the checker in the same session instead of by compliance review in the next one.

## Requirements

### 1. Run 1: before release

- Run `scripts/verify-website-currency.sh` at the start of the release work, before any merge, tag, or website edit.
- Record: the exact command, the exit code, and the checker's auditable output (origin latest tag, heading found, `cmp` exit code, the two link hrefs, Play-link count).
- If it fails, the failure is a defect in the **entering** session state and is fixed before release work continues (a small accuracy PR, base main, owned by Riven).

### 2. Run 2: after the Wave 4 website What's New update

- After the release commit and the website What's New edit (Wave 4), run `scripts/verify-website-currency.sh` **again**, against the new state.
- Run 2 is the run that matters: it verifies the released version is named on the live site, that the live file and the repo mirror are byte-identical after the sync, and that no em dashes or heavy emoji entered the new copy.
- Record the same set of facts as run 1.
- **A release is not complete until run 2 is recorded and green.**

### 3. Both results recorded in the release chain

- Both runs are written into `flambeee-team/release-chain.md` as their own step, so the chain shows the pre-flight and the post-flight side by side with exit codes.
- The same file (`release-chain.md`) is written after today's `session-plan.md`, preserving the existing chain convention.
- If run 2 fails, the recorded entry states the failure and the fix, and the re-run that goes green is recorded after it. A failed run is never omitted from the chain.

### 4. No build, no new tooling

- This story writes **no** new script, no new check, and no website change of its own. It reuses `scripts/verify-website-currency.sh` exactly as shipped in Story 038.
- The script itself is not modified by this story. If the script is found to be wrong or incomplete (a real defect in the checker), that is a separate fix, separate PR, and separate story, not a silent edit inside this one.

### 5. Fix path, not a redesign

- If either run fails, the fix makes the copy or the version true: a single-surface accuracy change plus a mirror re-sync. No redesign, no layout change, no new website feature.
- Any fix re-runs the checker and records the green result.

### Out of scope

- Any change to `scripts/verify-website-currency.sh` itself.
- Any website redesign, layout change, or new What's New feature.
- Any game code change (Cinder, Wordfire, Minesweeper, Simon, 2048).
- Any change to the deploy pipeline, the Caddy sync, or the service worker cache version.
- Any change to the noon Bluesky posting flow.

## Acceptance Criteria (BDD)

### Scenario 1: Run 1 before release, recorded (P2, Scout)
- **Given** the release work for this session has not started
- **When** Scout runs `scripts/verify-website-currency.sh`
- **Then** the command, the exit code, and the auditable output are recorded in `flambeee-team/release-chain.md`, and a non-zero exit stops release work and opens a fix path

### Scenario 2: Run 1 is green on the entering state (P2, Scout)
- **Given** the site is current at session start (Story 038's patterns hold)
- **When** run 1 completes
- **Then** it reports PASS with exit 0, the What's New heading names the true latest origin tag, the live file and the repo mirror are byte-identical (`cmp` exit 0), the summary has no em dashes or heavy emoji, the Releases and Blog anchors are real `<a href>` links, and every relative Play link target exists

### Scenario 3: Run 2 after the wave 4 website update, recorded (P2, Scout)
- **Given** the release commit has landed and the website What's New has been updated for this session's release
- **When** Scout runs `scripts/verify-website-currency.sh` again
- **Then** the command, the exit code, and the auditable output are recorded in `flambeee-team/release-chain.md` as the post-release run

### Scenario 4: Post-release drift is caught by the checker, not by compliance (P2, Scout + Vigil)
- **Given** a session updates What's New but the live file is not re-synced, or the heading names the wrong version, or the new copy contains an em dash
- **When** run 2 executes
- **Then** it fails with a non-zero exit and a specific FAIL line naming the check, Riven lands a small accuracy fix (base main), the mirror is re-synced, and the re-run goes green and is recorded

### Scenario 5: A release is not complete without run 2 (P2, Scout + Vigil)
- **Given** the release chain entry for this session
- **When** I read it
- **Then** both runs appear with exit codes, and the chain does not declare the release verified on run 1 alone

### Scenario 6: The checker is not silently modified (P2, Kai + Vigil)
- **Given** this story's commit
- **When** I inspect the diff
- **Then** `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state, and no new verification script was added by this story

### Scenario 7: Truthful recording (P2, Vigil)
- **Given** the two recorded runs in `release-chain.md`
- **When** Vigil compares them against the actual checker output and the actual repo state
- **Then** the recorded exit codes and outputs are truthful, nothing is reported green that was not green, and a failed run that was fixed shows both the failure and the green re-run

## Technical notes (Quinn)

- **The checker:** `scripts/verify-website-currency.sh` (shipped v0.19.0, Story 038). It resolves the latest tag with `git ls-remote --tags origin` (never a hardcoded version), so it survives new releases with no edit. Run it exactly as documented: `scripts/verify-website-currency.sh` from the repo root. Non-zero exit on any failure.
- **Paths it touches (do not change):** live `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE, outside the repo), repo mirror `website/index.html`, and the `games/` directory the Play links resolve against.
- **The recording target:** `/home/jake/.openclaw/workspace/flambeee-team/release-chain.md` (outside the repo, never committed). Follow the existing chain format: a step heading, a fenced block with the command and captured output, then PASS/FAIL and a one-line interpretation. The file must be written after today's `session-plan.md` (chain convention from Sessions 19-21).
- **Why run 2 exists (evidence):** Session 21 ran the checker pre-release only and passed. The What's New edit that shipped v0.19.0 to the site happened after that run, and the drift was caught during Vigil's compliance review, not by the checker. Recording both runs makes that failure mode visible in the chain. See the Session 21 entry in `flambeee-team/SESSION-LOG.md` (carried risk paragraph).
- **Ordering within the session:** run 1 belongs in the pre-release step (before merge/tag/website edit); run 2 belongs immediately after the Wave 4 website What's New update and its live sync. Both are release-chain steps, not dev-wave work items.
- **No dependency on the dev wave.** This story is independent of Stories 039 and 040; it can be executed even if the dev wave changes nothing on the website (run 2 then verifies the unchanged, correctly-synced state).

## Visual Description (Quinn)

No visual change at all. This story adds no website surface, no page element, and no copy. The website What's New block keeps its current rendering (flame "What's new" badge, bold version heading, muted summary, Releases and Blog links right-aligned, wrapping below the text on mobile). The story only verifies that block is true and in sync, twice, and records both results.

## Open questions

1. **Recording granularity (recommended, confirm).** Recommendation: one release-chain step per run ("Step N: website currency, pre-release" and "Step M: website currency, post-release"), each with the command, exit code, and captured output, matching the file's existing style. Confirm if a single consolidated step with both runs is preferred instead.
2. **If the checker itself is wrong.** Recommendation: treat a real checker defect as a separate story and a separate PR, and record it as such in the chain. Do not fold a script change into this story. This keeps Scenario 6 (no silent modification) enforceable.
3. **What counts as the "release commit" for run 2 timing.** Recommendation: run 2 immediately after the website What's New update and the live-file sync, before the release chain is declared complete. If the parent prefers run 2 after the written release chain entry, run 2 still records into the same file, appended. No CEO input needed; parent to confirm the ordering.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 3 and the Session 21 process note it closes.
