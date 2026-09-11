# Story 032 — Cinder Boss-Day Balance: Boss Fights Actually Appear (v0.17.1)

**Status:** Approved and implemented. CEO delegating team decision 2026-09-11 ("the team should handle and not need my input") authorizes the balance change that Story 031 explicitly gated on CEO sign-off. The delegation IS the sign-off, recorded here.
**Author:** Quinn (Business Analyst); implementation Riven/Kai; QA Scout.
**Priority:** P1 (player-facing defect: boss quest unreachable).
**Branch:** `feature/032-boss-day-balance` | **PR:** #69

## Summary

The boss-day quest (Story 025, boss1 template: defeat a boss, +120 XP / +60 gold) was **RNG-blocked**: `startCombat()` draws from a random pool capped at 2.5x the player's combined stats, and the fallback when nothing qualifies is a random monster from anywhere. On a boss day a low- or mid-level player could burn all 15 fights and never see a boss, so the quest literally could not advance. The F1 "stretch goal" framing (Story 031) papered over this.

## Change (single function, src/cinder.html `startCombat()`)

- On boss days (`getActiveQuest().kind === 'boss'`), the wilderness offers boss-tier monsters only (id >= BOSS_TIER). The quest becomes reachable; the fight itself is the difficulty.
- If no boss clears the 2.5x cap (very low level), offer the weakest boss (Shadow Knight, 63 combined stats) as a stretch fight. Run stays available, so the player is never trapped; death costs carried gold as usual.
- Non-boss days: selection logic is unchanged, byte-for-byte the old behavior (verified by the QA harness).

## Balance rationale

- Boss day remains the hardest day with the largest bonus (+120 XP / +60 gold vs +70/+35 slay, +50/+25 gold).
- Rotation, rewards, once-only payout, and progress rules are untouched.
- Low-level stretch is intentional (Story 031), now with the boss actually on the field.

## Acceptance Criteria (BDD)

### Scenario 1: Boss day offers bosses (P1, Scout)
- **Given** today's quest is a boss quest
- **When** the player enters combat
- **Then** every encountered monster is boss-tier (id >= 13)

### Scenario 2: Low-level stretch (P1, Scout)
- **Given** a very low-level player on a boss day
- **When** no boss clears the stat cap
- **Then** the weakest boss is offered as a stretch fight and Run remains available

### Scenario 3: Non-boss days unchanged (P1, Scout, regression)
- **Given** a normal slay/gold day
- **When** the player enters combat
- **Then** pool selection matches the pre-patch behavior exactly

### Scenario 4: No reward/rotation changes (P2, Vigil)
- **Given** the patch
- **When** reviewing quest templates, rotation, and payout
- **Then** rewards, rotation, once-only payout, and progress rules are unchanged

## Verification

- `node --check` on the extracted script: PASS.
- `scout-qa-session19-032.py` harness (committed in `flambeee-team/`): 6/6 PASS, including 200x15 simulated boss-day fight days (100% boss-only) and the pre-patch equivalence check for normal days.

## Out of scope

- Quest rewards, rotation schedule, gold-quest targets, XP curves, equipment.
- Boss monster stats.
- Anything outside Cinder.
