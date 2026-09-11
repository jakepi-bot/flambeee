# Test Plan — Story 031 Cinder Boss-Day Stretch: Decision Record (P2, docs-only)

**Author:** Scout (QA) | **Date:** 2026-09-11 | **Source:** `docs/stories/031-cinder-boss-day-stretch-decision-record.md`
**Testable code:** **NO** — docs-only decision record. No code, no runtime tests. Verify record existence + accuracy + traceability via content checks.

## Scope

Verify the F1 boss-day decision is explicitly recorded (conscious stretch goal for low-level players; rotates away next day; pays largest bonus; behavior intentionally unchanged vs v0.15.0/v0.16.0); no behavior/balance change; record is traceable from roadmap and references Story 031.

## Test cases (mirror BDD scenarios 1–4)

| ID | BDD Scenario | Check | Expected |
|----|--------------|-------|----------|
| 031-T1 | S1 (decision recorded) | Search `docs/roadmap.md` for boss-day/F1 language | States all four facts: stretch goal, rotates next day, largest bonus, behavior unchanged |
| 031-T2 | S2 (no behavior change) | Confirm no game code touched by this story (docs-only; no feature PR) | No cinder.html / balance change attributable |
| 031-T3 | S3 (accurate & truthful) | Compare record to shipped v0.16.0 behavior + roadmap (BOSS_TIER=13, kind cycle, rewards 120xp/60gp) | Record matches roadmap and shipped behavior |
| 031-T4 | S4 (traceable) | `grep -rn "031" docs/roadmap.md` + story file | Roadmap entry links to / references **Story 031** |

## Test code / commands (ACTUAL)

- `grep -in "boss.day\|F1\|stretch\|large" docs/roadmap.md`
- `grep -rn "031" docs/roadmap.md` (traceability from roadmap → story)

## Result (filled at execution)

- **Status:** PARTIAL — decision facts present in roadmap.md (line 11); traceability to Story 031 NOT yet present in roadmap.
