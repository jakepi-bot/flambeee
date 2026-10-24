# Test Plan: Story 092 Second-App One-Pager (Session 40)

Source: `docs/stories/092-second-app-onepager-session40.md`. P2 planning.
Doc only, landed on main via PR #160 (commit `cbd3d9a`, 091/092/093 story
md only). No code owner, no QA harness. QA verifies read-only against the
file on base `7c1f2b9`.

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee` on `origin/main`
  (`7c1f2b9`).
- File under test: `docs/stories/092-second-app-onepager-session40.md`
  (108 lines).

## Cases

1. T1 Owner named (AC-1, Scenario 1). File names Ember (product owner) plus
   Quinn (planning carrier) and states the Story 048 code-owner rule for
   the later build story. Check lines 26, 44.
2. T2 Scope bounded (AC-2, Scenarios 2, 4). In-scope list plus explicit
   non-goals both present. Check lines 28, 32.
3. T3 Exactly one candidate (AC-3, Scenario 3). Names only the single
   countdown timer with size cap plus the one-equal-size
   counter-proposal rule. Check line 30. A second candidate fails the case.
4. T4 Build-story stub present (AC-4, Scenario 5). Stub gives the
   later-session shape with no early authorization. Check lines 36-38.
5. T5 Planning only (AC-5, Scenario 6). The 092 portion of the landing
   diff is this Markdown file alone: no code, no site card, no directory,
   no CACHE_VERSION touch, no schedule or release edit.
6. T6 jakebot citation (AC-6, Scenario 7). Records priority (b) SECOND
   plus session `local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4`.
   Check lines 16, 18.
7. T7 Copy rule (AC-7). Zero em/en dashes and zero emoji by grep over the
   file.

## Real output

Commands plus outputs pasted into `qa-results.md`: the PR #160 stat, the
per-AC line reads, and the dash/emoji grep with exit code.

## Verdict

7/7 ACs verified read-only by Riven in Session 40 dev wave; QA re-checks
each case from disk and records pass/fail. No PR exists for this story by
design (doc landed with the story batch).
