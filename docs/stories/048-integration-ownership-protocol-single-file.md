# Story 048: Integration Ownership Protocol for Single-File Stories (Session 25, P2, Docs-Only)

**Status:** Ready for development (Session 25, 2026-09-27). **Docs-only. No code change.** One short spec in `docs/`.
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P2 (process: the single-file collision is now a standing property, and each instance costs the parent a manual reconcile and risks a defect that QA has to catch).
**Assigned to:** **Riven** (write the spec - Riven owns the frontend call sites this protocol assigns), with **Kai** (review - Kai owns the backend helpers and the proof pattern the protocol names). Parent-authored is acceptable if the dev wave prefers it. **Vigil** confirms the spec is truthful about the sessions it cites and contains no team mixing.
**Tracked by:** Session 25 plan Priority 2. Grounded in the real integration history: Story 042 (Session 23, PR #92) and Story 044 (Session 24, PR #96), both of which put two devs on `src/cinder.html` and both of which required a parent-side reconcile of two correct-but-conflicting halves. Grounded in the Session 24 QA defects D1 (out-of-scope reference) and D2 (forbidden post-reset fallback), and in the worktree rule that Sessions 22-24 carried forward.

## Summary

Almost every recent story has touched exactly one file, `src/cinder.html`, because Cinder is a single-file game. That makes `src/cinder.html` the highest-risk file in the repo: two developers working one story is normal here, and the merge is where their halves meet.

The cost is now measurable and recurring:

- **Session 23 (Story 042, PR #92):** Kai and Riven each independently solved both problems with their own helpers. Both were correct. Merging both would have shipped two implementations of each fix. The parent reconciled by hand, keeping Kai's `computeAwayWindow()` streak source and gate and dropping Riven's two now-redundant helpers.
- **Session 24 (Story 044, PR #96):** both halves touched the same call-site line. The parent reconciled again, keeping Kai's helper and the `questLogAnchor` call form, dropping Riven's out-of-scope `rawDayState` form, and dropping a post-reset fallback in the helper.
- **Session 24 QA (D1/D2):** the reconcile left two blocking defects for Scout to catch: an out-of-scope binding (D1) and a forbidden fallback to the post-reset record (D2).

In both sessions the two halves were individually correct and the defect was in how they met. The parent's manual reconcile is the improvised control, and it fails under load. This story replaces it with a written, binding, repo-resident rule so the collision is prevented at the source rather than repaired at merge time.

**This story changes no code.** It adds one short spec under `docs/` and nothing else. It is not a feature, not a tool, and not a refactor.

## Business value

- Removes the parent-side reconcile step, which has been needed in two consecutive sessions and is the step most exposed to human error at the end of a long session.
- Kills the specific defect class Scout caught in Session 24 (D1 out-of-scope reference, D2 forbidden fallback) by assigning each line an owner before dev starts, so no line is written twice and no half can reference another half's scope.
- Makes the worktree rule, currently carried as prose in each story, a permanent repo artifact the dev wave reads from `main`.
- Costs one page and one review. No maintenance burden, no build step, no new tooling.

## User Story

As the Flambeee team shipping stories that touch a single shared file,
I want a written, binding rule that assigns one owner per helper and per call-site line before development starts and requires each developer to declare the exact line range it owns,
So that two correct halves can no longer collide at merge time, the parent no longer has to reconcile by hand, and the defects that reconcile produced stop recurring.

## Requirements

### 1. One short spec in `docs/`

- The deliverable is **one new file** under `docs/`, for example `docs/integration-ownership-protocol.md`. The exact filename is Riven's choice; it must be short, descriptive, and unambiguous.
- The file is **one page**. If it grows past roughly one screen of prose, it is too long; cut it to the rule and the checklist.
- No new directory is required unless `docs/` conventions suggest one. Follow the existing `docs/` layout.

### 2. Scope: stories that touch `src/cinder.html`

- The protocol applies to **any story that changes `src/cinder.html`** (and, stated once, to any story that puts two or more developers on one file).
- It must state the rule in plain language a non-technical stakeholder can read, then give the checklist a developer follows.
- It must not attempt to cover multi-file stories, build systems, or anything outside the single-file case. Small and exact beats general.

### 3. One owner per helper and per call-site line, declared before dev starts

- The spec must require, for any single-file story, that **exactly one owner is named per helper and per call-site line before development starts**, in the Wave 3 brief or the story's dev-assignment section.
- It must define the two halves in the terms this repo already uses: a **helper** (a pure function, for example `computeQuestLogStreak()`) and a **call-site line** (the line inside a render or handler that calls the helper, for example `renderQuestLog()`'s list expression).
- It must state plainly that a helper and its call site are **different ownership units**, so one developer can own the helper while the other owns the call site, and neither may write the other's.

### 4. Exact line-range declaration in every PR body

- The spec must require that **each developer states the exact line range it owns in its PR body** for the file it touched.
- "Exact" means line numbers against the branch's base commit, not a description. A reviewer must be able to check the claim against the diff mechanically.
- The spec must state what happens when the owned ranges **overlap**: the PR is not mergeable until the ranges are re-cut so each line has one owner, and the re-cut is recorded in the PR body.
- The spec must state the rule for an **unowned line**: any changed line with no named owner in any PR body is a review failure, not a merge-time discovery.

### 5. The required pre-merge check

- The spec must name **one required pre-merge check** and who runs it. Recommendation (Riven/Kai to confirm): the second developer, or the parent acting as integrator, performs a line-ownership check against the PR bodies before merge, and QA (Scout) runs the out-of-scope-reference and forbidden-fallback scan against the **merged** candidate, not the two branches.
- The check must be concrete enough to be performed without judgement: read each PR body's declared line ranges, confirm they do not overlap, confirm every changed line has an owner, and run the scan on the merged result.
- It must state that **Scout reads the merged candidate**, per the Session 24 lesson: D1 and D2 were invisible on the individual branches and only appeared once the halves met.

### 6. Worktrees are part of the rule

- The spec must require **separate git worktrees** for each developer on a single-file story (`git worktree add` under a temp dir outside the main tree), as Sessions 22-24 carried forward in prose.
- It must state briefly **why**: two branches off one file let each half be developed and proven in isolation, and the worktree keeps the main tree clean for the parent's integration step.

### 7. No code change, no tooling, no enforcement automation

- The spec is **documentation only**. It adds no script, no hook, no CI job, no linter rule, and no build step.
- It must not require a tool the team does not already use. The check is a human reading declared line ranges, done deliberately and recorded in the PR body.
- It must not modify `src/cinder.html` or any other source file. Scenario 6 makes this testable.

### 8. Truthfulness and no team mixing

- Every session, PR, and defect the spec cites must be **real**: Story 042 / PR #92 (Session 23), Story 044 / PR #96 (Session 24), and the Session 24 QA defects D1 (out-of-scope reference) and D2 (forbidden fallback). Cite them accurately or cite none.
- The spec is a Flambeee artifact. It must contain **no reference to the jobs pipeline, `jobs/`, `jobs-refactor-team/`, or `jakebot/`**, and no shared procedure from those teams.

## Out of scope

- Any change to `src/cinder.html` or any other source file.
- Any new script, hook, CI job, linter rule, or build step.
- Any enforcement automation. The rule is written and checked by people.
- Any change to the SDLC beyond this one protocol: no branch-naming change, no PR-template change beyond what the spec describes, no review-policy change.
- Any new feature, game, or product surface.
- Any website change. The site is current and on-brand.
- Any change to `scripts/verify-website-currency.sh`. Story 049 owns the checker runs.
- Any cron configuration, and any file under `jobs/`, `jobs-refactor-team/`, or `jakebot/`.

## Acceptance Criteria (BDD)

### Scenario 1: The spec exists in `docs/` and is one page (P2, Riven)
- **Given** the repository at the story's branch
- **When** I look under `docs/`
- **Then** there is exactly one new protocol file for this story, it fits roughly one screen of prose, and it states the rule before it states any rationale

### Scenario 2: The protocol names its scope, which is the single-file story (P2, Riven)
- **Given** the protocol file
- **When** I read its scope
- **Then** it applies to any story that changes `src/cinder.html` or puts two or more developers on one file, and it says so plainly enough for a non-technical stakeholder to understand

### Scenario 3: One owner per helper and per call-site line, named before dev starts (P2, Riven + Kai)
- **Given** the protocol file
- **When** I read its ownership rule
- **Then** it requires exactly one owner per helper and per call-site line to be named before development starts, and it distinguishes a helper from its call site as separate ownership units

### Scenario 4: Every PR body declares an exact line range (P2, Riven)
- **Given** the protocol file
- **When** I read its PR requirement
- **Then** it requires each developer to state the exact line range it owns, in line numbers against the base commit, in its PR body

### Scenario 5: Overlap and unowned lines are handled, not discovered at merge (P2, Riven + Kai)
- **Given** the protocol file
- **When** I read its conflict rules
- **Then** it states that an overlapping range makes the PR not mergeable until the ranges are re-cut and recorded, and that a changed line with no named owner is a review failure rather than a merge-time surprise

### Scenario 6: The spec adds no code and no tooling (P2, Kai + Vigil)
- **Given** this story's diff
- **When** I inspect it
- **Then** it contains only a new Markdown file under `docs/`, `src/cinder.html` and every other source file are byte-identical to their pre-story state, and no script, hook, CI job, linter rule, or build step was added

### Scenario 7: The required pre-merge check is named and concrete (P2, Riven + Kai)
- **Given** the protocol file
- **When** I read its check
- **Then** it names one required pre-merge check and who runs it, and the check is performable without judgement: read the declared line ranges, confirm no overlap, confirm every changed line has an owner, and run the out-of-scope-reference and forbidden-fallback scan on the merged candidate

### Scenario 8: The separate-worktree rule is written in the repo (P2, Riven + Kai)
- **Given** the protocol file
- **When** I read the worktree rule
- **Then** it requires separate git worktrees per developer on a single-file story and states briefly why, so the rule no longer depends on prose carried story to story

### Scenario 9: Scout reads the merged candidate, as the rule requires (P2, Kai + Scout)
- **Given** the protocol file
- **When** I read the check
- **Then** it states that QA runs its scan against the merged candidate, not the individual branches, and it cites the Session 24 D1/D2 defects as the reason

### Scenario 10: The citations are true (P2, Vigil)
- **Given** every session, PR, and defect the protocol cites
- **When** Vigil checks them against the repository and the session records
- **Then** each cited session, PR number, and defect is real and described accurately, or it is not cited

### Scenario 11: No team mixing (P2, Vigil)
- **Given** the protocol file
- **When** Vigil reads it
- **Then** it contains no reference to the jobs pipeline, `jobs/`, `jobs-refactor-team/`, or `jakebot/`, and no shared procedure from those teams

### Scenario 12: It reads as a human document, in the CEO's tone (P2, Vigil)
- **Given** the protocol file
- **When** it is reviewed
- **Then** it uses plain punctuation, no em dashes, and at most a single emoji where one genuinely fits, and reads like a person wrote it, not a template

### Scenario 13: The parent's reconcile step is removed by the rule, not by luck (P2, Kai + Riven)
- **Given** the rule as written
- **When** the next single-file story follows it, naming one owner per helper and per call-site line before dev starts
- **Then** no two developers write the same line, the PR bodies show non-overlapping owned ranges with full coverage, and the parent has no reconcile to perform

### Scenario 14: The story itself is small (P2, Riven)
- **Given** this story's diff and its PR
- **When** the work is reviewed
- **Then** the PR contains one new docs file and no functional change, and it is merged like any other small docs PR, with peer review

## Technical notes (Quinn)

Verified against the repository at `main` = `38ea83b` (Merge PR #98, release v0.22.0).

- **The recurring facts the spec records, with sources:**
  - Story 042 / PR #92 (Session 23): Kai (PR #91) and Riven (PR #89) independently produced their own helpers for the same two problems. Both correct. Reconciled by keeping Kai's `computeAwayWindow()` streak source and `shouldShowWelcomeBack()` gate and dropping Riven's two redundant helpers.
  - Story 044 / PR #96 (Session 24): both halves touched the same call-site line. Reconciled by keeping Kai's `computeQuestLogStreak()` helper and the `questLogAnchor` call form, dropping Riven's out-of-scope `rawDayState` form, and dropping a post-reset fallback in the helper.
  - Session 24 QA defects: D1 (out-of-scope binding) and D2 (post-reset fallback), both found by Scout against the merged candidate and fixed before merge.
- **The ownership units, defined for the spec:** a **helper** is a pure function (in this file, `computeQuestLogStreak()`, `computeQuestStreak()`, `computeAwayWindow()`, `shouldShowWelcomeBack()` are examples already proven extractable). A **call-site line** is the line inside a render function or handler that calls a helper or reads state (for example `renderQuestLog()`'s `computeQuestLogStreak(dayState, questLogAnchor)` call and its `completed.slice(-5).reverse()` list expression). These are the two units the rule assigns.
- **The D1/D2 scan, made concrete:** "out-of-scope reference" means a variable used outside the scope that owns it (the Session 24 D1 class); "forbidden fallback" means a read path falling back to the post-reset record when the loaded record is unavailable (the Session 24 D2 class). The spec should name both in one line each so the check is mechanical.
- **Existing docs layout:** `docs/` already holds `roadmap.md`, `stories/`, and other product docs. The protocol file sits alongside them. No build step reads `docs/`.
- **Recording target:** the protocol file only. No entry in `flambeee-team/release-chain.md` is needed; this story is not a release step. The parent records the story's completion in the session summary.
- **Peer review:** Riven writes, Kai reviews (the direction the session plan names). Vigil reviews for truthfulness and team separation, per Scenarios 10, 11, and 12.

## Visual Description (Quinn)

No user-visible surface. The deliverable is a Markdown document under `docs/`. Its reader is a developer opening a PR on `src/cinder.html`.

The document should read, in order, as:

```
# Integration Ownership Protocol for Single-File Stories

1. When this applies       -> any story that changes src/cinder.html
2. The ownership rule      -> one owner per helper and per call-site line, named BEFORE dev starts
3. What you put in the PR  -> the exact line range you own, in line numbers against the base commit
4. If ranges overlap       -> not mergeable until re-cut and recorded
5. If a line has no owner  -> a review failure, not a merge-time surprise
6. The pre-merge check     -> who runs it and exactly what they read
7. Worktrees               -> one per developer, and why
8. Why this exists         -> Story 042 / PR #92 and Story 044 / PR #96, and the D1/D2 defects
```

Each numbered item is a short paragraph or a short list. No diagrams are required; a single small ownership table (helper | owner | call site | owner) is welcome if it makes the rule concrete. Palette is not required for this story; there is no brand surface.

## Open questions

1. **Exact filename (Riven, minor).** Recommendation: `docs/integration-ownership-protocol.md`, matching the descriptive-kebab style of the existing story filenames. Not a CEO question.
2. **Whether the parent or a developer runs the pre-merge ownership check (Riven/Kai).** Recommendation: the non-owning developer of the two, with the parent as fallback when one developer is solo on the file. Not a CEO question.
3. **Whether a PR-template change is wanted (parent).** Recommendation: no separate template change. The rule in the spec is enough for now; if the team later wants the line-range field enforced by the template, that is a separate small story. Not a CEO question.
4. **Whether this protocol should also cover the deploy mirror (Riven).** Recommendation: no. The mirror is a copy, not a source, and Story 049 records its comparison. Keep the protocol to `src/cinder.html` in the repo.

No other ambiguities. This story is grounded entirely in `flambeee-team/session-plan.md` Priority 2 and the integration history it names; nothing beyond that was invented.
