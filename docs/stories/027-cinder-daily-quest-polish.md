# Story 027 — Cinder Daily Quest Polish (Session 17, v0.16.0)

**Status:** Ready for development (Session 17, v0.16.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** P0 (headline of v0.16.0)
**Assigned to:** Kai (backend: boss-day reachability decision/state, gold-quest counting confirmation). Riven (frontend: `[Done]` cosmetic tail fix, any UI touch). Peer review across the aisle. QA by Scout (real browser taps per the Session 14 QA bar).
**Tracked by:** Session 17 plan Priority 1. Closes the three non-blocking findings (F1/F2/F3) carried from Session 16 QA on the newest, community-engaged feature (Cinder daily quest, shipped v0.15.0).

## Summary

The Cinder daily quest shipped in v0.15.0 (Story 025) and passed QA with 28/28 browser + 12/12 logic checks. Session 16 QA carried three non-blocking findings. This story closes them so the newest retention feature is tight:

- **F2 (cosmetic, trivial):** the town-hub quest tail shows `[COMPLETE]` when done, but the spec example was `[Done]`. Align the completed tail text to the spec.
- **F1 (balance, CEO-flagged):** on a `boss` quest day, a brand-new low-level player cannot complete the daily quest that UTC day, because boss-tier monsters (id >= 13) only spawn once the player is roughly level 6-7. This is a conscious stretch-goal framing (the boss day rotates away the next day and pays the largest bonus), but it needs an explicit CEO decision: keep as a stretch, or soften (e.g. lower the boss tier threshold, or add a low-level fallback objective). Do NOT silently change balance.
- **F3 (note):** the `gold` quest counts combat gold only; treasure-event gold is excluded. The displayed objective text says "Earn N gold **from combat**", so behavior matches the text. Confirm this is intended; if total gold earned was the intent, treasure gold should feed the counter.

## Business value

- Keeps the newest, community-engaged feature (Cinder daily quest) polished and consistent with its spec.
- Resolves a real player-facing balance question (boss-day reachability) with an explicit, documented decision rather than leaving it implicit.
- Cheap, safe, low-risk work that tightens the retention loop without adding scope.

## User Story

As a returning Cinder player,
I want the daily quest display to match its spec exactly and the boss-day objective to be a fair, deliberate challenge,
So that the daily-quest loop feels finished and consistent, and no player is silently locked out of a day's quest.

## Requirements

1. **F2 — Completed quest tail matches the spec.** When today's quest is complete, the town-hub "Today's quest" row tail reads `[Done]` (per the Story 025 spec example), not `[COMPLETE]`. The quest detail view's completion status text (`COMPLETE - reward collected`) is unchanged and stays as-is.
2. **F1 — Boss-day reachability is a conscious decision.** The CEO decides whether a `boss` quest day stays a stretch goal for low-level players (rotates away next day, pays the largest bonus) or is softened so a brand-new player can complete it that day. The decision is recorded in this story and implemented accordingly. No silent balance change.
3. **F3 — Gold-quest counting is confirmed.** Confirm the `gold` quest counts combat gold only (matching its "from combat" text) and that treasure-event gold is intentionally excluded. If total gold earned was the intent, update the counter and text together.

### Out of scope

- Any new quest type, streak, weekly/monthly quest, or leaderboard.
- Changes to the fights/day cap, Inn, or character balance unrelated to the boss-day decision.
- Any new game, service-worker change, or redesign.

## Acceptance Criteria (BDD)

### Scenario 1: Completed quest tail shows `[Done]` (P0, Riven)
- **Given** I have completed today's Cinder quest
- **When** I view the town hub menu
- **Then** the "Today's quest" row tail reads `[Done]` (matching the Story 025 spec), and the quest detail view still shows `COMPLETE - reward collected`

### Scenario 2: In-progress quest tail is unchanged (P0, Riven)
- **Given** I have an active, incomplete Cinder quest
- **When** I view the town hub menu
- **Then** the "Today's quest" row tail shows my live progress (e.g. `2/3`), unchanged by this story

### Scenario 3: Boss-day decision is recorded and implemented (P0, Kai + CEO)
- **Given** the CEO has decided the boss-day reachability policy (keep as stretch OR soften)
- **When** the decision is recorded in this story and implemented
- **Then** a brand-new low-level player's experience on a boss day matches the decided policy, and the change is documented (no silent balance change)

### Scenario 4: Gold quest counts combat gold only, matching its text (P0, Kai)
- **Given** I have an active `gold` quest ("Earn N gold from combat")
- **When** I earn gold from combat and from a treasure event
- **Then** only the combat gold advances the quest counter, matching the displayed objective text; the behavior is confirmed as intended (or the counter and text are updated together if total-gold was the intent)

## Open questions / ambiguities (need CEO input)

1. **F1 decision (required):** Keep the boss-day quest as a conscious stretch goal for low-level players (rotates away next day, largest bonus), or soften it (e.g. lower the boss tier threshold, or add a low-level fallback objective)? This is the only balance change in this story and must be an explicit CEO call.
2. **F3 confirmation (required):** Is "combat gold only" the intended behavior for the `gold` quest, or should treasure-event gold also count? The current text says "from combat", so behavior matches text; confirm intent.

## Decisions (recorded by Kai, backend, 2026-09-08)

### F1 — Boss-day reachability: KEEP as a conscious stretch goal (no balance change)

No CEO decision to soften the boss-day quest was given. Per the story's explicit rule ("Do NOT silently change balance"), the boss-day quest is **kept as a conscious stretch goal** for low-level players. Current behavior is unchanged:

- A `boss` quest only advances on a boss-tier monster kill (`monsterId >= BOSS_TIER`, where `BOSS_TIER = 13`; the boss-tier monsters are Shadow Knight id 13, Ancient Wyrm id 14, Void Horror id 15).
- The boss day rotates away the next UTC day (the kind cycle `['slay','gold','boss']` with `kindIndexForDay` guarantees no consecutive-day repeat and cycles through all three kinds).
- The boss quest pays the largest bonus of the three kinds (`rewardXp: 120, rewardGold: 60`).

**No balance numbers were changed.** This is a conscious, documented stretch-goal framing, not a silent balance change. If the CEO later decides to soften it (lower the boss tier threshold or add a low-level fallback objective), that is a separate, explicit decision and change.

### F3 — Gold quest counts combat gold only: CONFIRMED as intended (no code change)

Verified in `src/cinder.html`:

- `applyQuestProgress()` is called **only** from `winCombat()` (line ~786), passing `gold = currentMonster.gold` (combat gold).
- The treasure-event handler (`triggerEvent()`, `case 'treasure'`) adds gold directly to `character.gold` and calls `saveCharacter()`; it does **not** call `applyQuestProgress()`. Treasure-event gold therefore never feeds the quest counter.
- The `gold` quest objective text is "Earn N gold **from combat**" (templates `gold100`/`gold150`).

Behavior matches the displayed text. **Confirmed as intended. No code change needed.** If total-gold (combat + treasure) were ever the intent, the counter and the objective text would need to be updated together; that is not the case here.

### Verification notes (Kai, backend)

- Boss quests only spawn/advance on boss-tier monsters: `applyQuestProgress` boss branch requires `monsterId >= BOSS_TIER` (13+). Confirmed against monster table (ids 13-15 are the boss tier).
- Quest kind cycle works as documented: `KIND_CYCLE = ['slay','gold','boss']` with `kindIndexForDay(dayIdx) = (floor(dayIdx/3) + dayIdx%3) % 3`, which provably never assigns the same kind on consecutive days and cycles through all three kinds. Within a kind, `dayIndexHash` (FNV-1a) deterministically picks the specific template, so every player sees the same quest on a given UTC day.
