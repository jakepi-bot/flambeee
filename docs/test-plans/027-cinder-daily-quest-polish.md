# Test Plan — Story 027: Cinder Daily Quest Polish (v0.16.0)

**QA:** Scout | **Date:** 2026-09-08 | **Source:** `docs/stories/027-cinder-daily-quest-polish.md`
**QA bar:** Session 14 — real browser taps/clicks, not static inspection.

## Scope

Closes three non-blocking findings (F1/F2/F3) from Session 16 QA on the Cinder daily quest (v0.15.0, Story 025).

- **F2 (Riven):** completed quest tail reads `[Done]` (was `[COMPLETE]`); detail view keeps `COMPLETE - reward collected`; in-progress tail unchanged.
- **F1 (Kai + CEO):** boss-day reachability decision recorded (keep as stretch OR soften); no silent balance change.
- **F3 (Kai):** gold quest counts combat gold only, matching "from combat" text; confirmed intended.

## Test Environment

- Browser: Chromium via Playwright (`.venv/bin/python3`).
- Files under test: repo `src/cinder.html` and live `share/Flambeee/games/cinder.html`.
- Quest state lives in `flambeee-cinder-day` day-state object (`dayState.quest = { progress, completed, rewarded }`).

## BDD Scenario → Test Case Mapping

### Scenario 1: Completed quest tail shows `[Done]` (P0)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 027-1.1 | Completed tail reads `[Done]` | Load cinder.html; seed `dayState.quest = {progress:1, completed:true, rewarded:true}`; open town hub | Row 8 "Today's quest" tail reads `[Done]`, not `[COMPLETE]` |
| 027-1.2 | Detail view keeps `COMPLETE - reward collected` | Same completed state; open quest detail view | Detail shows `COMPLETE - reward collected` (gold class), unchanged |
| 027-1.3 | Boundary: completed but NOT rewarded | `{progress:1, completed:true, rewarded:false}` | Tail still `[Done]` (tail keys off `completed` only); detail shows `COMPLETE - reward collected` |
| 027-1.4 | Boundary: progress at target but completed flag false | `{progress:1, completed:false}` | Tail shows `1/1` (in-progress form), NOT `[Done]` — completed flag is the gate |

### Scenario 2: In-progress quest tail is unchanged (P0)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 027-2.1 | In-progress tail shows live progress | Seed `{progress:2, completed:false}` on a target-3 quest; open town hub | Tail reads `2/3`, unchanged |
| 027-2.2 | Boundary: zero progress | `{progress:0, completed:false}` | Tail reads `0/3` |
| 027-2.3 | Boundary: progress at target-1 | `{progress:2, completed:false}` on target-3 | Tail reads `2/3` (not `[Done]`) |

### Scenario 3: Boss-day decision recorded and implemented (P0)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 027-3.1 | Decision recorded in story | Read `docs/stories/027-cinder-daily-quest-polish.md` (PR #64) | F1 decision explicitly recorded (keep as stretch OR soften); no silent balance change |
| 027-3.2 | No balance numbers changed | Diff PR #64 against main | No change to reward XP/gold, BOSS_TIER, or monster table |
| 027-3.3 | Boss quest only advances on boss-tier kill | Code inspection of `applyQuestProgress` boss branch | Requires `monsterId >= BOSS_TIER (13)`; lower-tier kill counts 0 |

### Scenario 4: Gold quest counts combat gold only (P0)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 027-4.1 | Combat gold advances counter | Code inspection: `applyQuestProgress` called only from `winCombat` with combat gold | Combat gold feeds counter |
| 027-4.2 | Treasure gold does NOT advance counter | Code inspection: `triggerEvent` treasure case adds gold directly, never calls `applyQuestProgress` | Treasure gold excluded |
| 027-4.3 | Behavior matches text | Objective text reads "Earn N gold from combat" | Confirmed intended; no code change |

## Edge Cases / Boundary Conditions

- **Completed-but-unrewarded** state (tail vs detail divergence).
- **Progress-at-target-but-not-completed** (completed flag is the sole gate for `[Done]`).
- **Zero progress** and **target-1 progress** rendering.
- **Deployment sync:** repo `src/cinder.html` and live `share/Flambeee/games/cinder.html` must be byte-identical (`cmp`).
- **Private mode / localStorage throw:** quest flow must not throw unhandled (regression from Story 025).

## Negative Tests

- Missing/invalid quest state (e.g. `dayState.quest` undefined) → no unhandled error, graceful default.
- Quest detail with no active quest → no crash.
