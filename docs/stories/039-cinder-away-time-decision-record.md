# Story 039 - Cinder Away-Time Handling: Decision Record (Session 22, P1, docs-only)

**Status:** Approved as a documentation decision record. This story is **docs-only** - it records the delegated decision on what happens when a player is away from Cinder for one or more days. It does **NOT** authorize a balance change. No code/game change follows from this story except the pure-presentation return summary authorized as Story 040.
**Author:** Quinn (Business Analyst) - documentation owner. Decision delegated by the CEO; recorded here as the team's written source of truth.
**Priority:** P1 (it is the prerequisite Session 21 explicitly required before any away-time code).
**Assigned to:** Docs-only - Quinn writes the record. No dev implementation in this story. Kai and Riven are not assigned work here; their work lives in Story 040, which implements this record. Scout and Vigil verify the record is accurate and truthful.
**Tracked by:** Session 22 plan, Priority 1. Supersedes and closes the `docs/roadmap.md` Future item "Cinder offline progress / catch-up on return", which the roadmap carried as "highest-value future story; touches the fight economy and balance, so it needs a Story 031-style decision record before any code."

## Summary

Cinder gives one deterministic quest per UTC day (Story 025), a daily-return preview (Story 033), a quest log and streak (Story 035), and an app-icon badge for installed players (Story 037). The one genre-standard piece still missing is what the game does with the time a player was **away**.

Two options were on the table:

1. **Offline resource accrual** - gold, XP, quest progress, or boss fights accumulate while the player is gone and are paid out on return (a catch-up economy).
2. **A return summary** - nothing accumulates; Cinder simply tells the returning player where they stand.

**The decision is option 2.** No offline resource accrual, and no change to the fight economy. On return after a missed day, Cinder shows a one-time welcome-back summary: days away, quests missed, streak status (kept or broken), and a pointer to today's quest. This is **pure presentation** - it reads existing state and writes no new game state, pays nothing, and changes no number.

Story 040 implements this record. No away-time code may be written before this record exists; that prerequisite is now satisfied by this document.

## Business value

- Removes the ambiguity that has blocked away-time work since Session 21: the roadmap's top Future item now has a decided answer instead of an open question.
- Protects the fight economy and the balance surface. Nothing about rewards, rotation, payout, or progression changes, so no balance review or CEO sign-off is consumed by this session.
- Keeps the retention lever intact. The daily-return loop is the retention engine; a return summary strengthens it by making the game acknowledge the absence, without handing out progress the player did not earn.
- Near-zero regression risk: the implementable half (Story 040) is additive, backwards-compatible, and read-only.

## User Story

As a Flambeee team member and future session,
I want the away-time decision recorded explicitly in the docs,
So that there is a single written source of truth stating that Cinder pays no offline resources and instead shows a welcome-back return summary, and no future session reopens an economy question that has already been decided.

## Decision record

### D1 - No offline resource accrual (DECIDED: no)

While a player is away from Cinder:

- **Gold does not accrue.** No bank interest, no passive income, no catch-up payout.
- **XP does not accrue.** No rested-experience mechanic, no offline training.
- **Quest progress does not accrue.** A missed day's quest is missed; it is not completed retroactively, and its bonus is not paid later.
- **Boss fights do not accrue.** A boss day that passes while the player is away stays in the past. The player fights bosses only while present.
- **Daily fights do not bank.** The 15-fights-per-day allowance resets at UTC midnight (existing behavior); unused fights from a missed day do not carry forward or stack.

### D2 - The fight economy is untouched (DECIDED: unchanged)

This record authorizes **no** change to rewards, quest rotation, the payout-once gate, monster pools, level curve, boss-day behavior, or any other balance surface. Any balance change requires explicit CEO sign-off in a future session, exactly as with the Story 031 boss-day record. The Session 21 deferral note on boss-day balance remains in force.

### D3 - Cinder shows a welcome-back return summary instead (DECIDED: yes)

When a player returns after at least one **fully missed** day, Cinder shows a one-time return summary. It is pure presentation:

- **Days away** - how many UTC days have passed since the player last played.
- **Quests missed** - how many daily quests passed uncompleted during the absence.
- **Streak status** - whether the streak is kept or broken (it is broken by a gap; the summary states which).
- **Pointer to today's quest** - the player is directed straight at today's objective.

The summary pays nothing, writes no new state, creates no new save field, and changes no number in the game. Story 040 specifies it as BDD acceptance criteria.

### D4 - Rationale (why this decision, not the other one)

1. **2026 genre trend check - the two halves are not the same kind of work.** Browser idle/incremental roundups in September 2026 consistently treat *save continuity* (progress is never lost; the player's state survives absence) and *offline progress* as related but distinct. Save continuity is genuinely table stakes for browser idle games; Cinder already meets it (localStorage saves, byte-stable across sessions, legacy and corrupt saves load clean). Offline **accrual** is a design choice that belongs to a game with an idle loop. Cinder is a turn-based, single-file RPG with a fixed daily fight budget; it has no idle loop, so bolting on accrual would be inventing a second economy rather than meeting an expectation.
2. **Byte-safety culture.** The team's standing rules make byte-identity and additive-only change the default for shipped game files. Offline accrual cannot be additive: it necessarily mutates gold, XP, quest state, and timestamps on return, which is exactly the class of change the byte-safety discipline exists to slow down. A read-only return summary is additive and provable to write nothing.
3. **No balance change without CEO sign-off.** Accrual is a balance change by definition - it changes the rate at which players acquire gold and XP. The team does not make balance changes without explicit CEO sign-off (Story 031 precedent), and no sign-off exists for an away-time economy.
4. **Retention framing - the daily-return loop is the retention engine.** PMF grounding for this product is retention over shipping: the daily quest, the near-midnight preview (Story 033), the quest log and streak (Story 035), and the app-icon badge (Story 037) all exist to bring the player back on the day. Paying a returning player for the days they missed would weaken the reason to return on any particular day. A summary does the opposite: it names the cost of the gap (streak broken, quests missed) and immediately points at today's objective, which is the strongest available hook back into the loop.

### D5 - Precedent and follow-up behavior

- This follows the Story 031 pattern: a delegated product decision recorded in the docs, with explicitly no code and no balance change unless the CEO signs off.
- Reopening accrual requires CEO input. It is not a dev call, and it is not in any session's scope by default.
- Boss-day balance remains separately deferred and still requires CEO sign-off.
- Any future away-time work implements Story 040's summary only. Nothing in this record authorizes more.

## Requirements

1. **Record the decision.** This document states, unambiguously: no offline resource accrual (gold, XP, quests, boss fights); the fight economy untouched; a welcome-back return summary instead (pure presentation).
2. **No code/balance change.** This story ships documentation only. It must not modify `src/cinder.html`, `share/Flambeee/`, the website, or any balance value.
3. **Accurate and truthful.** The record must match the shipped behavior of `src/cinder.html` at v0.19.0 for all behavioral claims it makes about existing mechanics (UTC reset, 15 fights/day, payout-once, streak reset on gap, save persistence). Vigil verifies.
4. **Traceable.** The record links to the roadmap (whose Future item it closes) and to Story 040 (which implements it), so future sessions can find both halves.
5. **Retention rationale preserved.** The rationale in D4 is part of the record, not commentary; it is the reason a future session should not re-litigate the decision without new evidence.

### Out of scope

- Any offline accrual, catch-up payout, rested XP, bank interest, or banked-fight mechanic.
- Any change to gold, XP, rewards, quest rotation, boss-day behavior, the level curve, or the payout gate.
- Any implementation work. The implementable half is Story 040 (return summary).
- Any notification, push, email, or reminder about missed days.

## Acceptance Criteria (BDD)

### Scenario 1: The decision is recorded explicitly (P1, docs-only; Quinn + Vigil)
- **Given** I read the Cinder away-time decision record
- **When** I check `docs/stories/039-cinder-away-time-decision-record.md`
- **Then** it explicitly states that there is no offline resource accrual for gold, XP, quests, or boss fights, that the fight economy is untouched, and that Cinder shows a welcome-back return summary instead

### Scenario 2: The rationale is recorded, not just the outcome (P1, Quinn + Vigil)
- **Given** the decision record
- **When** I read the rationale section
- **Then** it names all four grounds: the 2026 genre trend check (save continuity and offline progress are distinct; Cinder has no idle loop), byte-safety culture, no balance change without CEO sign-off, and retention framing (the daily-return loop is the retention engine)

### Scenario 3: No behavior or balance change from this story (P1, verified by Scout/Vigil)
- **Given** the decision record is added
- **When** I compare Cinder's quest, combat, reward, and progression behavior before and after
- **Then** nothing changed: no gold, XP, reward, rotation, payout, boss-day, or save-shape difference (docs-only)

### Scenario 4: The record is accurate and truthful (P1, Vigil)
- **Given** the decision record's claims about existing mechanics
- **When** Vigil reviews them against the shipped v0.19.0 code
- **Then** every stated mechanic matches the code (UTC-day reset via `getDayIndex()`, 15 fights per day, payout-once gate, streak reset on gap, additive `completedQuests`, localStorage persistence) and no claim is invented

### Scenario 5: The record is traceable from both ends (P1, Quinn)
- **Given** the decision record
- **When** I navigate from the roadmap's Future section, or from Story 040
- **Then** I reach this record, and this record references Story 040 and the roadmap item it closes

### Scenario 6: The prerequisite is satisfied for Story 040 (P1, Quinn + Scout)
- **Given** Session 21's requirement that a Story 031-style decision record exist before any away-time code
- **When** Story 040 is written and later implemented
- **Then** this record exists first, and Story 040 cites it as its authority

### Scenario 7: No AI tells in the new copy (P2, Vigil)
- **Given** the new documentation text
- **When** it is reviewed
- **Then** it contains no em dashes and no heavy emoji, and keeps the direct, plain-punctuation team voice

## Technical notes (Quinn)

- **Docs-only change.** The only file this story writes is `docs/stories/039-cinder-away-time-decision-record.md`. The roadmap is updated by the release step (parent), not by this story's commit. No `src/` file, no `share/Flambeee/` file, no website file, no brand asset.
- **Behavioral claims verified against `src/cinder.html` (v0.19.0) at write time:**
  - `getDayIndex()` = `Math.floor(Date.now() / 86400000)`, a pure UTC day index; `checkDailyReset()` builds a fresh day record when `dayState.dayIndex !== today`, with `fightsUsed: 0`, `innHealsUsed: 0`, `quest: { progress: 0, completed: false, rewarded: false }`, `completedQuests: []`.
  - `MAX_FIGHTS_PER_DAY` = 15 (daily budget resets at UTC).
  - `computeQuestStreak(dayStateRef)` counts trailing consecutive completed day indexes, anchored on today when today is complete and on yesterday otherwise, so a gap resets it.
  - The payout-once gate is the `completed && rewarded` pair on `dayState.quest`; `completeQuest()` is the single place those flip.
  - `completedQuests` is additive and `Array.isArray`-guarded (Story 035); `ensureQuestState()` backfills `quest` and `completedQuests` for legacy saves.
  - `loadDayState()` / `saveDayState()` are the only `flambeee-cinder-day` readers/writers.
- **Implementation authority:** Story 039 authorizes exactly one implementation, Story 040 (read-only return summary). Anything that changes a stored value is out of scope and requires a new decision record plus CEO sign-off.
- **Ceiling for Story 040:** if a requirement there would require writing to `flambeee-cinder-save` or `flambeee-cinder-day`, or reading a new persisted field, it is outside this decision and must be escalated instead of implemented.

## Wireframe / visual description

None for this story. It is a documentation decision record with no UI output. The user-visible surface it authorizes is specified in Story 040 (the welcome-back return summary).

## Open questions / ambiguities (need CEO input)

1. **Reopening accrual.** This record closes the accrual question with "no". If the CEO wants offline accrual at any point, that reverses D1 and D2 and requires explicit sign-off, a new decision record, and a balance review. It is not a dev call and it is not in this session's scope.
2. **Where the decision is surfaced (confirm).** Default is this story doc plus a `docs/roadmap.md` cross-reference (matching Story 031's precedent of story doc plus roadmap entry). Confirm if a single consolidated decisions document is preferred instead.
3. **Missed-day wording for long absences.** Story 040 caps and phrases long absences ("it has been a while"); the record does not fix a numeric cap. No CEO input needed unless a specific wording is wanted.

No other ambiguities. This record is grounded entirely in `flambeee-team/session-plan.md` Priority 1 and the roadmap Future item it closes.
