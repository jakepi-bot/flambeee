# Story 037: Cinder Install-Aware Return Hook (App-Icon Badge) (Session 21, P1)

**Status:** Ready for development (Session 21, first half, 2026-09-18).
**Author:** Quinn (Business Analyst), with Ember (Product).
**Priority:** P1 (retention: make the daily-return loop visible before the player opens the tab).
**Assigned to:** **ONE dev owns `src/cinder.html`** - recommended **Kai** (guarded logic, feature-detection, pure-mirror proof, backwards-compat proof). If a change is needed in `share/Flambeee/` (hub-side PWA surface), that is a **separate file and a separate PR**, owned by **Riven**. Palette reviews any new user-visible copy and brand consistency.
**Tracked by:** Session 21 plan Priority 1 (Cinder install-aware return hook). Grounded in Story 023 (PWA install), Story 024 (service worker), Story 025 (daily quest), Story 033 (daily-return preview), Story 035 (quest log + streak), and the v0.13.1 event delegation pattern.

## Summary

Cinder gives one deterministic quest per UTC day (Story 025). Story 033 tells a player who finished today to come back after midnight. Story 035 added a Quest Log showing recent quests and the current streak. All of that is only visible **after** the player has already opened the tab or the installed app.

This story closes that gap for **installed** players. Once Cinder is installed as a PWA, the home-screen app icon can carry a small badge. When today's quest is not yet complete, the badge reads **1**. The moment the quest is completed and rewarded, the badge clears to **0**. Nothing else increments it this session.

This is not a new mechanic. The badge is a pure mirror of the quest state that already exists: it is derived from data the game already has, it writes nothing new to the save, and it never prompts, notifies, or subscribes the player to anything. If the browser has no Badging API, the game behaves exactly as it does today.

## Business value

- The daily-return loop becomes visible at the exact moment it can still be acted on: the home screen, before the app is opened.
- Rides the confirmed browser-game retention lever (daily-return loops) without new product scope, new economy, or new balance.
- Near-zero regression surface: the only new code path is a guarded, best-effort badge write that fails silently everywhere the API is missing.
- Complements Story 033 (come back tomorrow) and Story 035 (what you already did) instead of duplicating either.

## User Story

As a Cinder player who installed the game to my home screen,
I want my app icon to show that today's quest is still waiting,
So that I get a small nudge to come back and keep my streak alive, and the badge disappears once I have finished.

## Requirements

### 1. Badge mirrors pending daily quest

The badge value is derived from existing quest state only:

- Today's quest **not completed** -> badge **1**.
- Today's quest **completed and rewarded** -> badge **0** (cleared), including on the very next render after the reward is paid.
- No other daily action contributes to the count this session. The value is always 0 or 1, never higher.

The value is recomputed from the same state the hub already reads (`dayState.quest.completed` / `rewarded` via `getQuestState()`). No new source of truth is introduced.

### 2. Feature detection, never throw

`navigator.setAppBadge` and `navigator.clearAppBadge` are **optional** APIs. The badge path must:

- Feature-detect both before use (`typeof navigator.setAppBadge === 'function'`, same for clear).
- Never throw when either is absent (Firefox, older Chromium, most non-Chromium browsers, iOS Safari).
- Swallow any rejection or synchronous error from the call itself (the API returns a Promise and can reject).

If the API is missing, the rest of the game is unaffected: same hub, same quest, same save.

### 3. No new persistence, no save-shape change

- **Never write localStorage from the badge path.** No `saveCharacter()`, no `saveDayState()`, no direct `localStorage.setItem`.
- **Never touch the save shape.** No new field on `flambeee-cinder-save` or on the day record. This includes the additive day record from Story 035: no `badgeShown`, no `lastBadgeValue`, nothing.
- The badge is a **pure mirror**, computed and applied on render. If the game loses the value (reload, fresh install), the next render recomputes it from quest state and reapplies it.

### 4. Update points

The badge must be applied:

- On game load / init, after the quest state is ensured (so a returning player with today's quest still open sees 1 immediately).
- Immediately when the quest is completed and rewarded (so the badge clears to 0 in the same moment the reward is paid, no reload needed).
- On the UTC midnight rollover path, when the daily reset creates a fresh uncompleted quest for the new day (so the badge goes back to 1 for the new day's pending quest).

Applying the badge is idempotent: calling it repeatedly with the same value is harmless.

### 5. No notifications, no push, no permission prompts

- No `Notification.requestPermission()`, ever.
- No push subscription, no service worker message channel, no scheduled/background badge writes.
- No install prompt, banner, modal, tooltip, or nag anywhere. The hub already has an install control (Story 023); this story adds no visible promotion of installation.
- No new UI element in the town hub, the quest view, or the Quest Log. The badge lives on the app icon, not in the page.

### 6. Mobile / menu-tap safe, no inline onclick

The badge path does not add any menu row. If any developer-visible message is added (see requirement 8), it must not break the existing layout. All interactive markup continues to use the v0.13.1 `data-action` event delegation pattern. No inline `onclick` handlers anywhere.

### 7. Backwards compatibility and robustness

- A legacy save with no new fields loads clean: level, gold, XP, wins unchanged.
- A corrupt save or day record (missing `quest`, non-array history, string where an object is expected) still loads clean and the badge is simply 0 or 1 from whatever valid state exists.
- Private mode / storage unavailable: the game runs from in-memory state; the badge path still works if the API exists, and never throws if it does not.
- A legacy save that has a completed quest for today still clears the badge correctly.

### 8. No AI tells in any new copy

Any user-visible string introduced (for example an optional one-line console-free log entry, if the dev chooses to reuse the log for status) uses plain punctuation, no em dashes, no heavy emoji, in the dry Cinder voice. Preferred: no new visible copy at all.

## Out of scope

- Any notification, push messaging, permission prompt, or background sync.
- Any install nag or promotion of installation.
- Any new badge count source (Wordfire daily, Game of the Week, events, streaks). Only today's quest, only 0 or 1.
- Any balance, reward, rotation, payout, or quest-mechanic change.
- Any change to the save shape or any new persisted field.
- Any hub redesign or new town-hub row.
- Offline progress / catch-up on return (deferred, needs a decision record first).

## Acceptance Criteria (BDD)

### Scenario 1: Installed player with an incomplete quest sees a badge of 1 (P1, Kai + Riven)
- **Given** a player is in an installed PWA context on a browser that supports `navigator.setAppBadge`
- **And** today's quest is not completed
- **When** Cinder loads and the hub renders
- **Then** `navigator.setAppBadge(1)` is called once with the value 1, and the app icon shows a badge of 1

### Scenario 2: Badge clears to 0 on completion and reward (P1, Kai + Scout)
- **Given** an installed player with a badge of 1 and today's quest in progress
- **When** the last required fight (or gold, or boss kill) completes the quest and the reward is paid
- **Then** `navigator.clearAppBadge()` is called (or `setAppBadge(0)`) in that same completion path, the icon badge disappears, and no reload is required

### Scenario 3: No Badging API support, nothing throws (P1, Kai + Scout)
- **Given** a browser where `navigator.setAppBadge` and `navigator.clearAppBadge` are undefined (Firefox or iOS Safari)
- **When** the game loads, the player plays, and the quest is completed
- **Then** no exception is raised anywhere in the load, play, or completion path, no console error appears, and the game plays exactly as it does today

### Scenario 4: Non-installed browser context (P1, Riven + Scout)
- **Given** the game is open as an ordinary browser tab and not installed
- **When** the game loads and the quest state changes
- **Then** no badge-related error is raised, no install prompt appears, no banner or modal suggesting installation is shown, and the hub renders identically to the pre-story version

### Scenario 5: Legacy save with no new fields (P1, Kai, regression)
- **Given** a legacy save written before this story (no badge-related fields anywhere) with a non-completed quest
- **When** the game loads
- **Then** the save loads without error, level, gold, XP, and wins are unchanged, the quest state is unchanged, and the badge value is 1

### Scenario 6: Corrupt save values (P1, Kai + Scout)
- **Given** a save or day record with corrupt values (missing `quest`, `quest` not an object, `completedQuests` not an array, non-numeric day index)
- **When** the game loads
- **Then** the game loads clean with no exception, the badge resolves to a valid value (0 or 1), and no data beyond the corrupt field is lost or rewritten by the badge path

### Scenario 7: Private mode / storage unavailable (P1, Kai)
- **Given** the browser is in private mode or storage is otherwise unavailable, so the existing localStorage helpers are throwing and swallowing
- **When** the game loads and the player completes the quest
- **Then** the game still runs from in-memory state, the badge path behaves the same as with storage, and nothing throws

### Scenario 8: Quest completed but reward not yet collected (P1, Kai + Scout)
- **Given** a state where today's quest is completed but the reward has not been paid (`completed: true`, `rewarded: false`)
- **When** the badge value is computed
- **Then** the badge is treated as pending (value 1), and it clears only on the completed **and** rewarded state, matching the payout-once gate

### Scenario 9: UTC midnight rollover (P1, Kai + Scout)
- **Given** an installed player who completed yesterday's quest (badge 0) and returns after the UTC midnight reset
- **When** the daily reset creates the new day's quest and the game re-renders
- **Then** the badge returns to 1 for the new day's uncompleted quest, and the reset path writes no badge-related field to the save

### Scenario 10: The badge path never writes storage (P1, Kai)
- **Given** any of the states above
- **When** the badge value is computed and applied
- **Then** `flambeee-cinder-save` and the day record are byte-identical before and after the badge call, and a static scan of the badge path finds no `saveCharacter`, `saveDayState`, `localStorage.setItem`, `ensureQuestState`, `completeQuest`, `applyQuestProgress`, or state-mutating `character.` / `dayState.` writes

### Scenario 11: Badge call rejects or hangs (P1, Kai)
- **Given** `navigator.setAppBadge` exists but returns a rejected Promise (or throws synchronously)
- **When** the badge is applied
- **Then** the rejection or error is swallowed, no unhandled rejection reaches the console, and the quest and hub render normally

### Scenario 12: No notifications, no push, no permission prompt (P1, Vigil + Scout)
- **Given** the whole story's code
- **When** it is scanned and exercised in a browser
- **Then** it contains no `Notification` permission request, no `pushManager`, no subscription code, and no permission prompt of any kind appears at any point in load, play, or completion

### Scenario 13: Tone and no-AI-tells (P2, Vigil)
- **Given** any new user-visible copy introduced by this story
- **When** it is reviewed
- **Then** it contains no em dashes, no heavy emoji, and matches the plain-punctuation, dry-humor Cinder voice

## Technical notes (Quinn)

- **Single game file:** `src/cinder.html` is the source of truth. The deploy mirror `share/Flambeee/games/cinder.html` (ABSOLUTE path, outside the repo) must end the session **byte-identical** to `src/cinder.html` (`cmp` PASS). Verified identical at the start of this session.
- **Existing state to read:** `getQuestState()` returns the live `dayState.quest` (`{ progress, completed, rewarded }`), backfilled by `ensureQuestState()`. `checkDailyReset()` creates the fresh day record on a new UTC day. `init()` calls `checkDailyReset()` then `ensureQuestState()` before rendering the town menu. `completeQuest()` is the single place where `completed` and `rewarded` flip, guarded by the payout-once gate. The badge path hooks these three points: init, `completeQuest()`, and the reset/rollover path.
- **Recommended shape:** one small helper, e.g. `syncAppBadge()` that (a) feature-detects, (b) computes the value from `getQuestState()`, (c) calls `setAppBadge(value)` or `clearAppBadge()` inside a try/catch with a `.catch(function () {})` on the returned Promise, (d) returns a boolean/no-op when the API is missing. Call it at the end of `init()`, at the end of `completeQuest()` (after the reward is paid), and after the daily reset branch. Keep it a pure reader: it must not call `saveCharacter` or `saveDayState`.
- **Proof expectation (Session 14 bar):** Kai provides a node-based proof script plus a static scan (same pattern as the Story 033/035 proofs) that extracts `syncAppBadge`'s value computation, asserts 1 for incomplete, 1 for completed-but-unrewarded, 0 for completed-and-rewarded, asserts a missing-API invocation path returns without throwing, and scans the badge path for forbidden writes. Expected exit code 0.
- **If a hub-side change is required** in `share/Flambeee/` (for example wiring badge clearing from the hub shell), that is a **different file** and lands as a **separate PR** owned by Riven. It must not be edited in the same working tree by the dev who owns `src/cinder.html` (Session 20 lesson).
- **Mirror sync:** if the hub file changes, `share/Flambeee/index.html` and `flambeee/website/index.html` must still `cmp` clean at the end of the session.
- **QA bar:** real browser render at desktop and a narrow mobile viewport (375x667) with the quest actually completed by taps, confirming the badge call fires (instrumented `navigator.setAppBadge` stub) and that a no-API environment raises no error.

## Visual Description (Quinn)

No in-page visual change. The only visible surface is the operating system's app-icon badge:

```
Home screen, installed Cinder icon, quest pending:
    [ Cinder icon ]
             (1)      <- small numeric badge, browser/OS default styling

Home screen, installed Cinder icon, quest completed and rewarded:
    [ Cinder icon ]   <- no badge
```

Rules for the visual:
- The badge is written by the OS/browser from `setAppBadge(1)`. Do not style, theme, or colour it; the platform owns badge appearance.
- No badge in a plain browser tab (not installed): the same code path applies to the document, but there is nothing visible, and nothing else renders.
- No new hub row, no banner, no tooltip, no notification dot, no install nag. The town hub renders byte-for-byte the same rows as before.

## Open questions

1. **Badge value on "completed but reward not yet collected".** Recommended: treat as pending (1), clearing only on completed **and** rewarded, matching the payout-once gate. This is a single-line decision; confirm.
2. **Should the badge show on the hub shell too?** If Cinder is opened from the hub and the hub is the installed surface, the badge may belong to the hub's document rather than Cinder's. Recommended: this story covers the Cinder document only; a hub-side badge is a separate file, separate PR, and only if it is needed. Confirm scope.
3. **Clearing on uninstall / browser restart.** Browsers generally clear an app badge when the app is closed or the badge is superseded. We rely on platform behaviour and do not attempt to force persistence across installs. Confirm that is acceptable.
