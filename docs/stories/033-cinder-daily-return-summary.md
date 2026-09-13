# Story 033 — Cinder Daily-Return Summary: Come Back Tomorrow (Session 19, P1)

**Status:** Ready for development (Session 19, 2026-09-13).
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (retention: deepen the Cinder daily-return loop, no new product scope).
**Assigned to:** Riven (frontend: `renderQuest()` detail-view addition, mobile tap polish). Peer review: Kai reviews Riven's change. QA by Scout (real browser render of the quest detail view on desktop + mobile viewport, per the Session 14 QA bar).
**Tracked by:** Session 19 plan Priority 1 (small verifiable Cinder daily-habit improvement). Grounded in Story 025 (daily quest) and its `determineQuestForDay(dayIdx)` pure-day-seed design.

## Summary

Cinder already gives the player one deterministic quest per UTC day (Story 025) with a progress detail view (`renderQuest()`). Today's quest is reachable and finishable, but the player never sees that the loop keeps going: once today's quest is done, the surface goes quiet until after midnight. This story makes the daily-return loop visible by adding a **"come back tomorrow" daily-return summary** to the quest detail view. On the same screen that confirms today's quest was completed, the player sees a preview of tomorrow's quest (same kind-and-label framing, deterministic, no spoiler of exact reward) and a clear call to return after midnight.

It is a **single-file change inside `src/cinder.html`**: an addition to the existing `renderQuest()` detail view only. No new mechanics, no balance change, no boss-day rebalance, no new save fields, no new products. The daily cadence is the retention surface being deepened.

## Business value

- The daily-return loop (the core retention thesis across the site) becomes legible inside the game: a player who finishes today sees exactly why to come back tomorrow, with the next objective already named.
- Zero new product scope and near-zero regression surface: one deterministic read (tomorrow's quest) plus one rendered line, no new persistence, no server.
- Complements the website's Game of the Week (Story 026) and Play Today (Story 028) surfaces, which work at weekly and one-tap cadences; this works at the deeper in-game daily cadence.

## User Story

As a Cinder player who just completed today's quest,
I want to see a preview of tomorrow's quest and a reason to come back after the daily reset,
So that I return to the game daily instead of only when I happen to think of it.

## Requirements

1. **Completed-state daily-return summary.** In the quest detail view (`renderQuest()`), when today's quest is completed (`[Status: COMPLETE - reward collected]`), add a block below the status line that names tomorrow's quest objective and shows a "come back tomorrow" call to return after the UTC midnight reset.
2. **Tomorrow preview is deterministic and non-mutating.** Compute tomorrow's quest from the exact same selection logic the live loop uses for today, shifted by one day: `determineQuestForDay(getDayIndex() + 1)` (or equivalent read-only derivation). This must be a pure read, with no state writes, no save changes, and no effect on progress, rewards, or rotation. Show the objective/label; do not reveal the exact reward figure up front (keep the reveal for when the day actually arrives, to preserve the daily hook).
3. **In-progress state unchanged.** While today's quest is incomplete, the detail view renders exactly as today. The daily-return summary block appears only in the completed state.
4. **Mobile-first.** The new block flows within the existing `boxed-menu` layout, no horizontal overflow, tappable/readable on a narrow viewport, consistent with v0.7.0 touch baseline.
5. **No balance or mechanics change.** Rewards, rotation, payout-once, boss-day selection, and XP/gold curves are untouched. This story adds display text only. Boss-day balance is out of scope absent explicit CEO sign-off.
6. **Tone and no AI tells.** Any new copy uses plain punctuation, no em dashes, no heavy emoji, on-brand with the Cinder voice.

### Out of scope

- Any rebalance of quest rewards, rotation, boss-day selection, or XP/gold.
- Any new product, new save fields, new quest templates, or new mechanics.
- Leaderboards, multiplayer, community-submitted games (all roadmap-gated).
- Changes to the website, Wordfire, or any other game.

## Acceptance Criteria (BDD)

### Scenario 1: Completed quest shows tomorrow's preview (P1, Riven)
- **Given** today's quest is completed and rewarded
- **When** I open the quest detail view
- **Then** a daily-return summary block is shown naming tomorrow's quest objective (deterministically derived from the day after today) with a "come back tomorrow" call to action

### Scenario 2: Preview is a pure read (P1, Kai + Scout)
- **Given** I open the quest detail view with today's quest completed
- **When** the tomorrow preview is computed and rendered
- **Then** no save data is written (dayState, character, and quest state are byte-identical before and after), and progress/reward/rotation values are unchanged

### Scenario 3: Deterministic tomorrow quest (P1, Riven + Scout)
- **Given** a specific UTC day index D
- **When** I open the completed quest detail view on day D and again on any reload/visitor on day D
- **Then** the preview always names the same tomorrow quest, matching `determineQuestForDay(D + 1)`, and every player sees the same preview that day

### Scenario 4: In-progress view is unchanged (P1, Riven, regression)
- **Given** today's quest is incomplete
- **When** I open the quest detail view
- **Then** it renders exactly as before the story, with no daily-return summary block

### Scenario 5: Mobile renders without layout break (P1, Riven)
- **Given** I view the completed quest detail view on a mobile/touch viewport
- **When** the daily-return summary block is present
- **Then** the layout has no horizontal overflow, the block is fully visible and readable, and the Back to Town row still works via tap (per the Session 14 tap bar)

### Scenario 6: Tone and no-AI-tells (P2, Vigil)
- **Given** the new copy
- **When** any external-facing text from this story is reviewed
- **Then** it contains no em dashes, no heavy emoji, and matches the plain-punctuation, dry-humor Cinder voice

## Technical notes (Quinn)

- **Single file:** `src/cinder.html`, `renderQuest()` only. Riven owns the presentation and the mobile tap polish. A repo mirror of the game also exists (`share/Flambeee/games/cinder.html` and the live absolute path); if a mirror copy is present it gets the same change and is kept in sync (verify with `cmp`) per the standing deploy practice used for the website.
- **Tomorrow derivation:** `determineQuestForDay` is already a pure function of the day index (verified in code: FNV-1a hash + kind rotation, no state). Tomorrow = same function at `getDayIndex() + 1`. Confirm `getDayIndex()` itself is read-only and advances only via the existing UTC reset, so the preview never nudges the day.
- **Completed-state gate:** the summary block renders only when `q.completed` is true (and `q.rewarded`, matching the existing reward-collected status text). Do not show it for incomplete quests.
- **QA bar (Session 14):** real browser render of the completed quest detail view is mandatory on desktop and a narrow mobile viewport, with the Back to Town row actually tapped. Persistence no-op is proven by comparing save state before and after opening the view.
- **Accessibility:** summary text readable at the existing quest-detail font size, sufficient contrast, no on-brand change that harms readability.

## Visual Description (Quinn)

An extra block inside the existing quest detail box, below the `[ Status: COMPLETE - reward collected ]` line and above the divider before Back to Town. It reads as the payoff for finishing the day, styled with the muted text color and the flame accent reserved for the reward line:

```
=== TODAY'S QUEST ===
Objective: Defeat a boss (Shadow Knight or stronger)
Progress:  1 / 1
Reward:    +120 XP, +60 gold
[ Status: COMPLETE - reward collected ]
-
Tomorrow: Earn 100 gold from combat
Come back after midnight to start it.
[ 1. Back to Town ]
```

On mobile the block stacks full-width inside the existing `boxed-menu`, no horizontal scroll, tap target for Back to Town unchanged.

## Open questions

1. **Preview detail depth.** Preview names tomorrow's objective (as shown) but hides the exact reward figure. Confirm the CEO prefers the objective preview to keep the daily hook, or a more minimal "a new quest awaits tomorrow" without naming it. Recommend naming the objective: it is deterministic, already visible to the player on the next day, and does not reduce the reward reveal. Ember + CEO to confirm.
2. **Whether a preview at all.** An alternative is a plainer "come back after midnight for a new quest" line with no tomorrow detail. The objective preview carries slightly more curiosity risk if a player reads an upcoming boss day as pressure. Recommend the objective-preview version for the stronger return nudge.
