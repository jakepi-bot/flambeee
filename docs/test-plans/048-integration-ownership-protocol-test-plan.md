# Test Plan: Story 048 - Integration Ownership Protocol for Single-File Stories (Session 25)

**Story:** `docs/stories/048-integration-ownership-protocol-single-file.md` (14 BDD scenarios)
**Code under test:** none. The deliverable is **one new Markdown file under `docs/`** (recommended `docs/integration-ownership-protocol.md`). Docs-only. No code change, no script, no hook, no CI job, no linter rule.
**Owner:** Riven writes, Kai reviews, Vigil confirms truthfulness and team separation. Scout verifies the spec text against the 14 scenarios.
**Method:** read the spec file and check each scenario's assertion against its text. The Scenario 6 test is a diff check: the spec PR must contain only a new `docs/*.md` file, with `src/cinder.html` and every other source file byte-identical to pre-story state.

## What is being verified

That the written spec carries the rule the last two sessions improvised: one owner per helper and per call-site line named before dev starts, exact owned line ranges in each PR body, overlap/unowned-line handling, one required pre-merge check (with the D1/D2 scan on the **merged** candidate), and separate worktrees. Also that its citations of Story 042 / PR #92, Story 044 / PR #96, and the Session 24 defects D1/D2 are real and accurate, and that it contains no team mixing.

## Scenario coverage

### S1 The spec exists in `docs/` and is one page (P2)
Assert exactly one new protocol file for this story under `docs/`, roughly one screen of prose, rule stated before rationale.
**Expected:** PASS.

### S2 The protocol names its scope: the single-file story (P2)
Assert it applies to any story changing `src/cinder.html` or putting two or more developers on one file, in plain language.
**Expected:** PASS.

### S3 One owner per helper and per call-site line, named before dev starts (P2)
Assert the ownership rule requires exactly one owner per helper and per call-site line, named before development starts, and distinguishes a helper from its call site as separate ownership units.
**Expected:** PASS.

### S4 Every PR body declares an exact line range (P2)
Assert it requires each developer to state the exact line range it owns, in line numbers against the base commit, in its PR body.
**Expected:** PASS.

### S5 Overlap and unowned lines handled, not discovered at merge (P2)
Assert an overlapping range makes the PR not mergeable until re-cut and recorded, and a changed line with no named owner is a review failure.
**Expected:** PASS.

### S6 The spec adds no code and no tooling (P2)
Inspect the diff: only a new Markdown file under `docs/`; `src/cinder.html` and every other source file byte-identical to pre-story state; no script, hook, CI job, linter rule, or build step added.
**Expected:** PASS.

### S7 The required pre-merge check is named and concrete (P2)
Assert one required pre-merge check and who runs it (recommended: the non-owning developer, parent fallback), performable without judgement: read declared ranges, confirm no overlap, confirm every changed line has an owner, run the D1/D2 scan on the merged candidate.
**Expected:** PASS.

### S8 The separate-worktree rule is written in the repo (P2)
Assert it requires separate git worktrees per developer on a single-file story and states briefly why.
**Expected:** PASS.

### S9 Scout reads the merged candidate, as the rule requires (P2)
Assert it states QA runs its scan against the merged candidate, not the individual branches, and cites the Session 24 D1/D2 defects as the reason.
**Expected:** PASS.

### S10 The citations are true (P2)
Verify each cited session, PR number, and defect against the repository and session records. Story 042 / PR #92 (Session 23), Story 044 / PR #96 (Session 24), D1 (out-of-scope reference), D2 (forbidden post-reset fallback).
**Expected:** PASS (accurate) or FAIL (inaccurate/unsupported citation).

### S11 No team mixing (P2)
Assert no reference to the jobs pipeline, `jobs/`, `jobs-refactor-team/`, or `jakebot/`, and no shared procedure from those teams.
**Expected:** PASS.

### S12 It reads as a human document, in the CEO's tone (P2)
Assert plain punctuation, no em dashes, at most a single emoji where one genuinely fits, reads like a person wrote it.
**Expected:** PASS.

### S13 The parent's reconcile step is removed by the rule, not by luck (P2)
Assert the rule as written would, if followed, produce non-overlapping owned ranges with full coverage and no reconcile (checked by reading the rule, not by running it on a future story).
**Expected:** PASS.

### S14 The story itself is small (P2)
Assert the PR contains one new docs file and no functional change, merged like any other small docs PR with peer review.
**Expected:** PASS.

## Negative and boundary matrix

| Case | Condition | Expected |
|------|-----------|----------|
| Two new docs files | duplicated deliverable | FAIL S1 (exactly one) |
| Spec cites a nonexistent PR | fabricated citation | FAIL S10 |
| Spec references `jobs/` or `jakebot/` | team mixing | FAIL S11 |
| Spec adds a script or hook | tooling | FAIL S6 |
| Spec omits the worktree rule | gap | FAIL S8 |
| Spec omits "merged candidate" wording | gap | FAIL S9 |
| Em dash / heavy emoji in spec | tone | FAIL S12 |
| Spec grows past one screen | over-length | FAIL S1 |
| Source file touched by the PR | code change | FAIL S6 |

## Verdict

**Test plan status: written 2026-09-27. Executed against Riven's spec PR text when the PR appears; results recorded in `/home/jake/.openclaw/workspace/flambeee-team/qa-results.md`.**

QA verifies and reports. This plan adds no script and modifies no source.
