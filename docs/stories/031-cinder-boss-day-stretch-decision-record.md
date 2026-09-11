# Story 031 — Cinder Boss-Day Stretch: Decision Record (Session 18, P2, docs-only)

**Status:** Approved as a documentation decision record. This story is **docs-only** — it records the F1 boss-day decision. It does **NOT** authorize a balance change. No code/game change unless the CEO explicitly signs off.
**Author:** Quinn (Business Analyst) — documentation owner
**Priority:** P2
**Assigned to:** Docs-only — Quinn writes the record. No dev implementation this session. Kai/Riven/Scout not required (no code). Vigil verifies the record is accurate and truthful.
**Tracked by:** Session 18 plan, Priority 3. The Cinder F1 boss-day stretch was recorded in the roadmap/session notes and flagged to the CEO for confirmation. This session carries it as a documented decision, not a code change.

## Summary

Cinder's daily quest (v0.15.0, Story 025) includes a **boss-day quest** (F1): on a boss day, the quest stays a conscious **stretch goal** for low-level players. It rotates away the next day, pays the **largest bonus**, and there is **no balance change** — the behavior is intentionally unchanged vs. v0.15.0/v0.16.0. This decision was recorded in the roadmap but flagged to the CEO for explicit confirmation.

This story formally records that decision in the docs (roadmap decision record), so the team has a written, unambiguous statement of what the boss-day stretch is and why behavior is unchanged. It does not modify any behavior. No balance change will be made without explicit CEO sign-off.

## Business value

- Gives the team and future sessions a written, unambiguous record of the F1 boss-day decision (what it is, why behavior is unchanged).
- Removes ambiguity about whether boss-day quests for low-level players are a bug or an intended stretch: they are intentional.
- Low risk: docs-only, no code, no balance change.

## User Story

As a Flambeee team member / future session,
I want the Cinder boss-day (F1) stretch decision recorded explicitly in the roadmap/docs,
So that there is a single written source of truth stating the boss-day quest is an intended stretch (rotates away next day, largest bonus) with behavior intentionally unchanged.

## Requirements

1. **Record the decision.** Add/confirm an explicit decision record in the docs stating: boss-day quests are a conscious stretch goal for low-level players; the quest rotates away the next day; it pays the largest bonus; behavior is intentionally unchanged vs. v0.15.0/v0.16.0 (no balance change).
2. **No code/balance change.** This story must not modify any game behavior or balance. Any balance change requires explicit CEO sign-off in a future session.
3. **Accurate and truthful.** The record must match the shipped behavior and the roadmap's v0.15.0/v0.16.0 entries (Vigil verifies accuracy).
4. **Traceable.** The record links back to the roadmap entry and this story number so future sessions can find it.

### Out of scope

- Any code change, gameplay change, or balance change to Cinder or any game.
- Any implementation of a different boss-day behavior.
- Any new feature or quest content.

## Acceptance Criteria (BDD)

### Scenario 1: Decision is recorded (P2, docs-only; Quinn + Vigil)
- **Given** I read the Cinder boss-day (F1) decision record
- **When** I check the docs
- **Then** it explicitly states the boss-day quest is a conscious stretch goal for low-level players, rotates away the next day, pays the largest bonus, and that behavior is intentionally unchanged vs. v0.15.0/v0.16.0

### Scenario 2: No behavior change (P2, verified by Scout/Vigil on current code)
- **Given** the decision record is added
- **When** I compare Cinder's quest behavior on the shipped v0.16.0 code
- **Then** no boss-day/boss-quest behavior or balance changed as a result of this story (docs-only)

### Scenario 3: Record is accurate and truthful (P2, Vigil)
- **Given** the decision record
- **When** Vigil (compliance) reviews it against the roadmap and shipped behavior
- **Then** it is accurate, truthful, and matches the v0.15.0/v0.16.0 entries (culture.md)

### Scenario 4: Record is traceable (P2, Quinn)
- **Given** the record
- **When** I try to locate it from the roadmap and this story
- **Then** it is reachable via a clear link/reference from the roadmap entry and references Story 031

## Wireframe / visual description

None. This is a documentation/decision-record change only; no visual or UI output.

## Open questions / ambiguities (need CEO input)

1. **Explicit CEO sign-off on the stretch (required):** this story records the F1 boss-day decision docs-only. If the CEO wants any **behavior/balance change** to boss-day quests (rather than keeping them a stretch), that requires explicit sign-off and is out of scope for this story — open a follow-up before any code change.
2. **Where the record lives (confirm):** default is an entry in `docs/roadmap.md` (the decisions/notes section) plus this story. CEO confirm if a separate decision-record doc is preferred.
3. **Low-level-player definition (clarify, if ever needed):** the record need not define a numeric low-level threshold now (behavior is unchanged). Only define one if a future balance change is authorized.
