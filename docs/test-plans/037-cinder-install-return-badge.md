# Test Plan 037: Cinder Install-Aware Return Hook (App-Icon Badge)

**Author:** Scout (QA Analyst)
**Date:** 2026-09-18 (Session 21)
**Story:** `docs/stories/037-cinder-install-return-badge.md` (P1, 13 BDD scenarios)
**PR under test:** #80, branch `feature/037-cinder-install-badge` (tip `924ba4d`), base `main`
**Artifact under test:** `src/cinder.html` (branch copy)
**Test environment:** real Chromium via Playwright (`/home/jake/.openclaw/workspace/.venv/bin/python3`), branch worktree at `/tmp/qa-037`

---

## 1. Scope

The badge is a **pure mirror** of quest state. It reads `getQuestState()` (`{ progress, completed, rewarded }`) and calls `navigator.setAppBadge(1)` while today's UTC quest is pending, `navigator.clearAppBadge()` once it is `completed && rewarded`. No new save field, no localStorage write from the badge path, no notifications, no push, no permission prompt, no install nag, no new hub row.

Out of scope for this plan: OS-level badge rendering (the platform owns badge appearance and cannot be asserted in a headless browser beyond the API call).

## 2. Requirements-to-test map

| Req | Covered by |
|-----|-----------|
| 1 badge mirrors pending quest | S1, S2, S8, S9 |
| 2 feature detection, never throw | S3, S11, S6 |
| 3 no new persistence | S10, S9 |
| 4 update points (init, complete, rollover) | S1, S2, S9 |
| 5 no notifications/push/permission | S12, S4 |
| 6 mobile/menu-tap safe, no inline onclick | layout checks, DOM scan |
| 7 backwards compat + robustness | S5, S6, S7 |
| 8 no AI tells in new copy | S13 (no new copy) |

## 3. Hook points (independently re-derived)

| # | Location | Confirmed |
|---|----------|-----------|
| 1 | end of `init()`, immediately before `setInterval(renderStatus, 1000)` | line 1200 |
| 2 | end of `completeQuest()`, immediately after `saveCharacter(); saveDayState();` | line 331 |
| 3 | end of `checkDailyReset()`, after the reset/grace branch | line 530 |

`syncAppBadge` definition: 1 (line 280). Call sites: 3. Inline `onclick`: 0 attributes (the single textual match at line 1188 is inside a comment explaining why inline onclick is not used).

## 4. Test cases

### TC-037-01 (S1) Installed, incomplete quest -> badge 1
- **Given** a valid save and a day record for the current UTC day with the quest pending
- **When** Cinder loads
- **Then** every badge call is `setAppBadge(1)`, value is never 0 or higher, no console errors.
- **Note:** two calls fire on load, from hook 3 (`checkDailyReset`) then hook 1 (`init`). Both compute 1. This is the designed idempotent behaviour, not a defect.

### TC-037-02 (S2) Quest completed and rewarded -> badge cleared in the same path
- **Given** a day record one kill short of the target (`progress: 4` of 5)
- **When** the player taps Wilderness, then Attack until the kill completes the quest
- **Then** `clearAppBadge()` fires in the same completion path, `rewarded:true` is persisted, and the page is never reloaded.

### TC-037-03 (S3) No Badging API -> nothing throws, game unchanged
- **Given** `navigator.setAppBadge` and `navigator.clearAppBadge` are undefined
- **When** the game loads, plays, and completes the quest
- **Then** zero uncaught exceptions, zero console errors, quest completes normally.

### TC-037-04 (S4) Non-installed browser context
- **Given** an ordinary browser tab
- **When** the game loads and quest state changes
- **Then** no badge-related error, no install prompt/banner/modal in the rendered DOM, hub rows identical to pre-story.

### TC-037-05 (S5) Legacy save with no new fields
- **Given** a save with no badge-related fields
- **When** the game loads
- **Then** level, gold, XP, wins unchanged, quest state unchanged, badge 1.

### TC-037-06 (S6) Corrupt save values
- **Given** a day record with `quest` missing, `quest` a string, `quest` null, `completedQuests` not an array, or a non-numeric day index
- **When** the game loads
- **Then** clean load, no exception, badge resolves 0 or 1, nothing extra rewritten.

### TC-037-07 (S7) Private mode / storage unavailable
- **Given** localStorage helpers throwing and swallowing
- **When** the game loads and completes the quest
- **Then** in-memory play, badge path behaves the same, nothing throws. (Covered jointly with S3/S6: the badge path references no save helper.)

### TC-037-08 (S8) Completed but not rewarded
- **Given** `completed:true, rewarded:false`
- **When** the badge value is computed
- **Then** the badge is 1 (pending), clearing only on `completed && rewarded`.

### TC-037-09 (S9) UTC midnight rollover
- **Given** yesterday's record completed and rewarded
- **When** the daily reset creates the new day's quest
- **Then** the badge returns to 1, and the reset path writes no badge field.

### TC-037-10 (S10) Badge path never writes storage
- **Given** any state above
- **When** the badge is computed and applied
- **Then** `flambeee-cinder-save` and `flambeee-cinder-day` are byte-identical before/after, and a static scan of the badge path finds no forbidden write token.

### TC-037-11 (S11) Badge call rejects or throws
- **Given** a rejected Promise or a synchronous throw from the badge API
- **When** the badge is applied
- **Then** swallowed, no unhandled rejection, hub renders normally.

### TC-037-12 (S12) No notifications/push/permission
- **Given** the whole story code
- **When** scanned and exercised
- **Then** no `Notification`, no `pushManager`, no `requestPermission`, no `serviceWorker`, no permission prompt at load/play/completion.

### TC-037-13 (S13) Tone
- **Given** any new copy
- **When** reviewed
- **Then** no em dashes, no heavy emoji. Satisfied trivially: no new user-visible copy was added.

### TC-037-H1 Layout / mobile safety (edge)
- **When** rendered at 1280x800 and 375x667
- **Then** no horizontal overflow, no rendered inline `onclick` attribute.

## 5. Boundary conditions and edge cases

- Badge value boundaries: only 0 or 1, never higher, never negative. Asserted across S1/S2/S8/S9.
- Missing API on one method only: `canSet`/`canClear` are detected separately; if only `setAppBadge` exists but the quest is complete, the code falls through to the `setAppBadge(0)` branch. Verified in the node proof.
- Undefined `navigator` (non-browser sandbox): returns false, no throw.
- Corrupt day record + completed quest: still clears.
- Repeated calls with the same value: idempotent.
- Quest kind variants (slay / gold / boss): completion always funnels through `completeQuest()` -> hook 2, so the clear path is kind-independent.

## 6. Proof script re-execution (independent)

Kai's proof `src/kai-story037-badge-proof.py` was copied together with `src/cinder.html` into `/tmp/qa-proof-037` and run with `/home/jake/.openclaw/workspace/.venv/bin/python3`. Result: `ALL CHECKS PASS`, exit 0. The hook-point count (1 definition, 3 call sites) and the purity scan were re-derived by hand with `grep` and by reading the helper body.

## 7. Exit criteria

All 13 scenarios pass in the real browser plus proof, with no blocking defect.
