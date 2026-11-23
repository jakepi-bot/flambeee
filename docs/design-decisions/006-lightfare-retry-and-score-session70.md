# 006 - LIGHTFARE retry and score edges, Session 70 (2026-11-23)

Date: 2026-11-23. Session: 70. Status: accepted. Story: 155. Design contract: flambeee-team/design-handoff.md (Session 70).

## Context

The Session 70 plan fixes the economy (budget 15, prices 1/2/4/8, move limit 80, score is light remaining) but leaves three calls open: what a LOSE retry preserves, whether inputs work during the 1.0 s reveal, and what a zero-look solve scores against the plan's parenthetical (0-14).

## Decision

1. LOSE retry resets the current level only (moves 0, light 15) and keeps banked scores from cleared levels. It never counts a play. Rationale: the run was counted at its start; retry is WIN-advance-shaped, matching the Empty Hands precedent.
2. All movement and look inputs are ignored during the 1.0 s reveal (frozen reveal). Rationale: move count then counts blind moves only, which keeps the harness trials and the par table testable.
3. Score is light remaining, range 0..15. The plan's 0-14 holds for every run using at least one look (all designed play). A zero-look solve banks 15; legal mastery edge, no cap added. Rationale: adding a min() cap would be an unplanned rule; the display question goes to Quinn.
4. Touch pad (4-dir + LOOK) is the normative, gated touch path; swipe is ungated enhancement. Rationale: the plan lists "swipe or pad", and parity needs exactly one testable path.

## What would change the decision

Playtest evidence that frozen reveal feels broken (inputs visibly swallowed) reopens call 2; release telemetry showing zero-look farming reopens call 3. Decided by Rook with Scout/Quinn evidence, next NEW-GAME session at the earliest.
