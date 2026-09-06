# Story 025 — Cinder Daily Quest System (Session 16, v0.15.0)

**Status:** Ready for development (Session 16, v0.15.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** P0 (headline feature of v0.15.0)
**Assigned to:** Kai (backend logic: quest seed, state, progress validation, reward, reset). Riven (frontend/UI/mobile: "Today's quest" town-hub menu entry, progress display, reward flow). Peer review across the aisle. QA by Scout (real browser taps/clicks on the full quest flow per the Session 14 QA bar).
**Tracked by:** Session 16 plan Priority 1. Retention play on Cinder, the newest, community-engaged game (issues #41/#45/#46). No open issue; mirrors Wordfire's proven UTC-daily retention hook.

## Summary

Cinder has a daily action cap (15 fights/day, UTC reset) but no reason to care about the character from one day to the next. This story adds a **single deterministic daily quest** per UTC day: a rotating objective (e.g. "defeat 3 monsters", "earn 150 gold", or a boss-fight objective) that gives repeated players a concrete reason to log in each day. Progress is tracked in the Cinder save; completing it pays bonus XP/gold; the reward and completed state persist until the UTC reset (aligned with the existing fights/day + Inn reset). The town hub gains a "Today's quest" menu entry showing progress, fully playable on mobile.

The seed is deterministic by UTC day so every player sees the same quest that day (the Wordfire daily habit, applied to Cinder). There is exactly one quest per day, no rerolls, no skip, no account.

## Business value

- Deepens the retention loop on the game the community is actively playing and reporting on. A player who had no daily reason to reopen Cinder now has one: finish today's quest, collect the bonus, come back tomorrow for a new one.
- Mirrors Wordfire's single best-proven mechanic (one UTC-daily objective everyone shares), so behavior is already understood and validated by the market's daily-puzzle habit signal.
- Session plan's explicit headline priority; the strongest pull signal in the repo.

## User Story

As a returning Cinder player,
I want to see one daily quest each UTC day, track my progress toward it, and collect a bonus reward when I finish it before the daily reset,
So that I have a concrete reason to come back to Cinder every day.

## Requirements

1. **One deterministic quest per UTC day.** Exactly one quest is active per UTC day, seeded deterministically from the UTC date so all players see the same objective on the same day. Quest types rotate; a given type must not repeat for the same player on consecutive days (see open question 1 for the rotation guarantee).
2. **Quest progress tracked in the Cinder save.** Progress toward the active quest persists in localStorage and survives reload. Field lives alongside the existing day-state so it resets cleanly at UTC.
3. **Time-limited to the UTC day.** Progress, reward eligibility, and completed state all reset at UTC midnight, aligned with the existing fights/day count and Inn heal reset. A new quest becomes available on the new UTC day.
4. **Quest completes exactly once per day.** The first time the player meets the objective, the bonus reward is applied and the quest is marked complete. A completed quest stays complete (and the reward is NOT re-granted) until the reset, even if the player's progress counter later drops or the game reloads.
5. **Bonus reward on completion.** Completing the quest pays a bonus XP and/or gold (a flat amount, not counted back into the quest's own progress). Exact numbers are Kai's call, flagged for CEO balance check if needed.
6. **New "Today's quest" town-hub menu entry.** The town hub shows the active quest, current progress (e.g. "Monsters slain 2/3" or a gold tally), and completion state. Selecting it shows the quest objective, a live progress readout, and the reward to be claimed.
7. **Mobile tap flow.** The entire quest flow works with real taps: open from the hub menu, read objective, see progress update after each qualifying action, and collect the reward. No keyboard required. Per the Session 14 QA bar, taps must actually be exercised in QA, not just keyboard.
8. **Existing-save grace.** Players with an existing `flambeee-cinder-save` and no quest state get a graceful default: the quest shows as available today with 0 progress. No crash, no corrupt data, no data migration beyond the default.
9. **No new game, no service-worker changes, no redesign.** Scope is confined to Cinder's quest system and the hub menu entry.

### Out of scope

- Any quest beyond the single daily one (no weekly/monthly/streak quests this session).
- Leaderboards, guess-count stats, multiplayer, community games (all deferred by session plan).
- Changes to the fights/day cap, Inn, or character balance unrelated to the quest reward.

## Acceptance Criteria (BDD)

### Scenario 1: One deterministic daily quest is assigned (P0, Kai)
- **Given** I open Cinder on a given UTC day
- **When** the game loads my character
- **Then** exactly one quest is active for that UTC day, and any other player opening Cinder that same UTC day sees the same objective

### Scenario 2: New "Today's quest" entry in the town hub (P0, Riven)
- **Given** I have an active character and am in the town hub
- **When** I view the town menu
- **Then** it includes a "Today's quest" entry with a live progress readout (e.g. current objective and how far along I am), selectable by keyboard and by tap

### Scenario 3: Quest detail shows objective, progress, and reward (P0, Riven/Kai)
- **Given** I select "Today's quest" from the town hub
- **When** the quest view opens
- **Then** it shows the objective text, my current progress toward it, and the bonus reward I will receive on completion

### Scenario 4: Progress updates as I play (P0, Kai/Riven)
- **Given** I have an active incomplete quest
- **When** I take an action that counts toward the objective (e.g. defeat a monster, earn gold, win a boss fight)
- **Then** the quest progress increments accordingly and the "Today's quest" entry reflects the updated count

### Scenario 5: Quest completes and pays the bonus once (P0, Kai)
- **Given** I have an active quest and my progress reaches the objective
- **When** the qualifying action completes
- **Then** the quest is marked complete, the bonus XP/gold is applied exactly once, and the UI shows the quest as complete with a collected indicator

### Scenario 6: Completed quest stays complete and does not re-pay (P0, Kai)
- **Given** I have completed today's quest
- **When** I reload the game or take further actions that would have counted toward the objective
- **Then** the quest remains marked complete, no additional reward is granted, and my progress counter does not move past the completed state inconsistently

### Scenario 7: Reward collected after reload is not double-paid (P0, Kai)
- **Given** my quest was completed and the reward applied
- **When** I close and reopen Cinder before the UTC reset
- **Then** I still see the completed quest with no claimable reward, and my character's XP/gold equals exactly what was granted at completion (no double payment)

### Scenario 8: UTC reset brings a new quest and clears progress (P0, Kai/Riven)
- **Given** the UTC date has changed since my last play and my previous quest was completed (or not)
- **When** I open Cinder in the new UTC day
- **Then** the previous quest and its progress/completion state reset, the new UTC day's deterministic quest is assigned, and progress starts at 0 (aligned with the fights/day and Inn reset)

### Scenario 9: Existing save with no quest state is graceful (P0, Kai)
- **Given** I have an existing `flambeee-cinder-save` with no quest state (e.g. from before this feature)
- **When** I open Cinder and view the quest
- **Then** the quest shows as available today with 0 progress, my character and day state load correctly with no crash and no corrupt data

### Scenario 10: Full quest flow works on mobile by tap (P1, Riven)
- **Given** I am on a mobile/touch viewport with an active character
- **When** I tap "Today's quest" in the town hub, complete a qualifying action, and try to claim the reward
- **Then** every step works via real taps (the Session 14 QA bar: taps actually exercised, not just keyboard), with progress and completion state updating correctly

### Scenario 11: Private mode stays safe (P1, Kai)
- **Given** localStorage is unavailable (private mode)
- **When** I open Cinder and play toward the quest
- **Then** the quest still assigns, tracks, and completes in-session; it just does not persist between sessions, and no action throws an unhandled error

## Technical notes (Quinn)

- **Primary file:** `share/Flambeee/games/cinder.html` (deployed, same-origin with the website so localStorage works). **Repo copy:** `flambeee/src/cinder.html` receives the same file (CEO directive: games go in both places).
- **Deterministic seed:** derive the quest choice from the UTC day index (`Math.floor(Date.now() / 86400000)`, already used for the daily reset) plus a deterministic function over the available quest templates, so the same UTC day always yields the same quest. Kai owns the seed function; document it in the PR. The existing `getDayIndex()` already anchors all daily logic.
- **Quest state location:** add quest fields to the existing day-state object key `flambeee-cinder-day` (which already holds `dayIndex`, `fightsUsed`, `innHealsUsed`). Fields: active quest id (implied by dayIndex), progress count, completed flag, reward-claimed flag. Because this object is already reset at UTC (see `checkDailyReset()`), the quest resets for free with the fights/day + Inn. Do NOT break the existing hub modal stats read of `flambeee-cinder-save` in `share/Flambeee/index.html`.
- **Progress hooks (verified in current code):** gold earned and wins are tracked via `character.gold`/`character.wins`; a monster defeat (win) runs through `winCombat()` which increments `wins++` and `fightsUsed++`. Quest progress for "defeat 3 monsters" / "earn 150 gold" / "boss fight" should be validated from the actual combat outcomes at the point these counters change, not from a separate guess, so the quest is always consistent with real play. A boss-fight objective maps to defeating a capped/high-tier monster; exact definition is Kai's call, documented.
- **Reward bonus:** a flat bonus XP and/or gold granted once at completion, not wired back into the quest's progress counter. Numbers should be modest (a visible but not game-skipping reward). Flag to CEO if a specific value matters for balance.
- **Private mode:** all localStorage access already wrapped in try/catch (existing pattern); quest reads/writes must follow the same guard.
- **UI (Riven):** a new town-hub menu row "Today's quest" (see visual description) with a quest detail view. Reuse the existing menu-row/event-delegation pattern from v0.13.1 (data-action rows + single listener on the display container) so mobile taps work identically to the rest of Cinder. Progress readout must update live as qualifying actions complete. Touch targets full-width and tappable per the v0.7.0 baseline (no tap delay, no double-tap zoom).
- **Accessibility:** objective text is readable; completion/progress is conveyed by text (e.g. "2/3"), not by color alone.
- **No PII, no network calls, no accounts.** Everything stays in the browser.

## Visual Description (Quinn)

Cinder keeps its BBS terminal presentation. The additions are:

- **Town hub menu** gains a "Today's quest" row, matching the existing rows (numbered, full-width tappable on mobile), e.g.:
  ```
  1. Wilderness
  2. Weapon Shop
  ...
  7. Tavern
  8. Today's quest  [Monsters slain 2/3]
  ```
  The progress tail sits right-aligned in the row, in the muted/gold color, updating live.
- **Quest detail view** (opening the row) shows a boxed panel:
  ```
  ============ TODAY'S QUEST ============
  Objective: Defeat 3 monsters
  Progress:  2 / 3
  Reward:    +40 XP, +25 gold
  ----------------------------------------
  [ Status: In progress ]
  ```
  When complete, `[ Status: In progress ]` becomes `[ Status: COMPLETE - reward collected ]` in the gold/positive color, and no further claim action is offered.
- ANSI-inspired colors on the existing near-black background, monospaced font stack; colors are decoration, text carries the meaning.
- Mobile: same panel, full-width tappable menu rows, no keyboard needed.

## Open questions

1. **Rotation guarantee.** The seed is deterministic by UTC day, but if the counter merely cycles template order, the same quest type could land on consecutive days for a player. Session plan says quests rotate; recommend a seed that also staggers the type so no player sees the same type two days running. Confirm the guarantee the CEO wants (no-repeat vs simple deterministic rotation).
2. **Reward numbers.** Bonus XP/gold amounts are not specified. Recommendation: a flat bonus that feels meaningful (roughly one extra fight's worth of XP/gold) without trivializing progression. Confirm a number or delegate to Kai.
3. **Boss-fight objective definition.** "A boss-fight objective" needs a concrete definition (which monster tier counts, whether it must be level-gated). Kai to define from the monster table and document; flag if the CEO has a specific intent.
4. **Where the "Today's quest" row sits in the menu.** Recommend appending as row 8 (keep the other seven numbered rows stable so existing muscle memory and v0.13.1 flow are unchanged). Confirm if renumbering is acceptable.