# Test Plan: Story 039 - Cinder Away-Time Handling Decision Record (Session 22)

**Story:** `docs/stories/039-cinder-away-time-decision-record.md` (7 BDD scenarios)
**Type:** Documentation only. No code, no behaviour, no balance change. There is no runtime artifact to exercise, so this plan verifies the record itself and states that explicitly rather than implying a test that cannot exist.

## Scope

Story 039 is a Story 031-style decision record. The deliverable is the document. Testing it means checking that the decision is stated, the rationale is present and grounded, the claims about shipped mechanics are true, and the document is traceable. There is no executable code path introduced by this story.

## Checks

| # | Scenario | Check | How verified | Result |
|---|----------|-------|--------------|--------|
| 1 | Decision recorded explicitly | The record states no offline accrual for gold, XP, quests, boss fights; the fight economy is untouched; a welcome-back return summary replaces accrual | Read `docs/stories/039-cinder-away-time-decision-record.md` decision section | PASS |
| 2 | Rationale recorded | Genre trend check, byte-safety culture, CEO sign-off rule for balance changes, retention framing all present | Read the rationale section | PASS |
| 3 | No behaviour or balance change from this story | The Wave 2 commit contains only story docs; no `src/` or `website/` change | `git show 237c9b6 --stat` shows three story files only | PASS |
| 4 | Accurate against shipped mechanics | Claims about `completedQuests`, `computeQuestStreak`, `checkDailyReset` and the fight economy match the shipped v0.19.0 code | Read the cited functions in `src/cinder.html` at `77acd25` | PASS (see note) |
| 5 | Traceable | Reachable from the roadmap Future item and from Story 040 | Cross-references checked in both directions | PARTIAL (see note) |
| 6 | Prerequisite satisfied | The record exists before Story 040 shipped | Record is in main at `77acd25`; Story 040 PR #83 branches from it | PASS |
| 7 | No AI tells in the new documentation | No em dashes, no heavy emoji in the record | `grep` for U+2014/U+2013 and emoji ranges over the file | PASS |

## Note on check 4

The record claims that accrual "cannot be additive, it must mutate gold, XP, and quest state on return". That is verified directly against the shipped code: `completeQuest()` mutates `character.xp`, `character.gold` and `dayState.quest`, and `checkDailyReset()` replaces the day record wholesale. There is no shipped path that could pay a returning player without such a mutation, so the claim holds.

One nuance is recorded honestly rather than smoothed over: the record's retention framing is a product judgement, not a measurable claim, and it is presented as reasoning rather than as evidence. That is appropriate for a decision record.

## Note on check 5 (partial)

Story 040 -> Story 039 is present (`docs/stories/040-cinder-welcome-back-summary.md` names Story 039 as its authority in its status and tracked-by lines) and Story 039 -> Story 040 is present (Story 039 names Story 040 as the implementing story in several places).

The roadmap -> Story 039 direction is **not yet present**: `docs/roadmap.md` line 221 still carries the raw Future item "Cinder offline progress / catch-up on return" with no link to the 039 record. Per the requirements handoff section 8 item 4, the roadmap cross-reference is the **release step's job (parent)**, not part of Quinn's docs-only commit. So this is a deferred, owned item rather than a defect in the record, and it is flagged here so the release step does not miss it. Until the roadmap is updated, scenario 5 is PARTIAL, not PASS.

## What is NOT tested, and why

- No BDD scenario is executed as a runtime test, because the story introduces no runtime behaviour. Stating "no testable code" here is accurate rather than an omission.
- No balance or economy assertion is needed beyond check 3: the story's diff cannot change behaviour because it does not touch code.

## Verdict

Scenarios 1, 2, 3, 4, 6 and 7 verified by document and code inspection. Scenario 5 is PARTIAL pending the release-step roadmap cross-reference (owned by the parent, not a defect in the record). No blocking defects. GO.
