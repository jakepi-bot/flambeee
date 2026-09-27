# Integration Ownership Protocol for Single-File Stories

A rule for any story that changes `src/cinder.html`, or that puts two or more developers on one file. It exists because two consecutive sessions shipped correct halves that collided at merge time, and both needed a hand reconcile.

## 1. When this applies

Any story that changes `src/cinder.html`. Cinder is a single-file game, so two developers on one story is normal here and the merge is where their halves meet. Any story that puts two or more developers on any one file follows the same rule.

## 2. The ownership rule

Name exactly one owner per helper and per call-site line **before development starts**, in the story's dev-assignment section or the Wave 3 brief.

A **helper** is a pure function, for example `computeQuestLogStreak()`. A **call-site line** is the line inside a render function or handler that calls a helper or reads state, for example `renderQuestLog()`'s list expression. They are **different ownership units**: one developer can own the helper while the other owns the call site, and neither may write the other's line.

| Unit | Example | Owner |
|---|---|---|
| Helper | `computeQuestLogStreak()` | named before dev starts |
| Call-site line | `renderQuestLog()` list expression | named before dev starts |

One helper, one owner. If two developers each write their own helper for the same problem, that is the duplicate-solution hazard this rule removes.

## 3. What you put in the PR

State the **exact line range you own** in your PR body: line numbers against your branch's base commit, not a description. A reviewer must be able to check the claim against the diff mechanically.

## 4. If ranges overlap

An overlapping range makes the PR **not mergeable** until the ranges are re-cut so each line has one owner, and the re-cut is recorded in the PR body.

## 5. If a line has no owner

Any changed line with no named owner in any PR body is a **review failure**, not a merge-time discovery.

## 6. The required pre-merge check

One required check, run before merge. The **non-owning developer** runs it (the parent is the fallback when one developer is solo on the file, or the integrator when the halves are combined). The check is performable without judgement:

1. Read each PR body's declared line ranges.
2. Confirm they do not overlap.
3. Confirm every changed line has an owner (full coverage).
4. Run the out-of-scope-reference and forbidden-fallback scan on the **merged** candidate, not the two branches.

The scan names two defect classes: an **out-of-scope reference** is a variable used outside the scope that owns it; a **forbidden fallback** is a read path that falls back to the post-reset record when the loaded record is unavailable.

QA reads the **merged candidate**. Story 044's two blocking defects, D1 (out-of-scope reference) and D2 (forbidden fallback), were invisible on the individual branches and only appeared once the halves met.

## 7. Worktrees

Each developer on a single-file story works in a **separate git worktree** (`git worktree add` under a temp dir outside the main tree). Two branches off one file let each half be developed and proven in isolation, and the worktree keeps the main tree clean for the integrator's step.

## 8. Why this exists

Story 042 (Session 23, PR #92): Kai (PR #91) and Riven (PR #89) each independently solved both problems with their own helpers. Both were correct; merging both would have shipped two implementations of each fix. The reconcile kept Kai's `computeAwayWindow()` streak source and `shouldShowWelcomeBack()` gate and dropped Riven's two redundant helpers.

Story 044 (Session 24, PR #96): both halves touched the same call-site line. The reconcile kept Kai's `computeQuestLogStreak()` helper and the `questLogAnchor` call form, dropped Riven's out-of-scope `rawDayState` form, and dropped a post-reset fallback in the helper. That reconcile then left two blocking defects (D1, D2) for QA to catch.

In both sessions the halves were individually correct and the defect was in how they met. Assigning each line an owner before dev starts, and requiring the declared ranges in the PR body, removes the hand reconcile and the defect class it produced.
