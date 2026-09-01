# Story 021 - Cinder: Fix Menu Tap/Click Interaction (Issue #46)

**Status:** Ready for development (Session 14, v0.13.1)
**Author:** Quinn (Business Analyst)
**Priority:** HIGH (build first this session; mobile players cannot play Cinder at all)
**Assigned to:** Kai (backend/game logic). Peer review by Riven. QA by Scout (real browser taps, see test plan).
**Tracked by:** GitHub issue #46 "Cinder - menu" (BigFunger, 2026-08-30; public fix-promise reply 2026-08-30 19:00 UTC)

## Summary

Every menu row in Cinder is rendered with an inline `onclick="handleMenuClick(N)"` handler, but the entire game script is wrapped in an IIFE (`(function() {` at `src/cinder.html:61`, closes `init(); })();` at end of file). Inline attribute handlers resolve their function names at global scope, and `handleMenuClick` is never defined or exposed there. Result: every tap or click on any menu row throws `ReferenceError: handleMenuClick is not defined` and nothing happens.

Desktop players can fall back to typing the row number + Enter in the prompt input, so the game is playable there. Mobile players have no keyboard and cannot play Cinder at all. This shipped in v0.13.0 because QA smoke-tested via keyboard input only; a real tap would have caught it in one second.

The fix is small. The requirement is that every menu row actually works when tapped or clicked, everywhere in the game.

## Business value

- Cinder is unplayable on mobile, which is where a large share of web-game sessions happen. This is the difference between a shipped game and a shipped apology.
- Two community issues are open with public "we'll fix it" replies. Shipping this fix is a promise kept, and the fastest trust signal we have.
- Patch release v0.13.1 exists for exactly this. No new features, no storage changes, one scoping bug dead.

## Requirements

1. **Fix the scoping bug** so that `handleMenuClick` (or an equivalent delegation path) is reachable from the rendered menu rows. Two acceptable approaches; Kai picks one and documents the choice in the PR:
   - **Preferred: event delegation.** One click listener on the menu/display container that maps the tapped row to its action. Works for dynamically rendered rows, keeps the game's scope private, no globals added.
   - **Acceptable: explicit exposure.** `window.handleMenuClick = handleMenuClick;` at the end of the IIFE. Simple, but adds one global; if used, keep the name unchanged so existing markup works as-is.
2. **Every menu must work by tap/click** in every location: Town (7 rows: Wilderness, Weapon Shop, Armor Shop, Bank, Inn, Trainer, Tavern), Weapon Shop, Armor Shop, Bank (3 rows: Deposit All, Withdraw All, Leave), Inn, Trainer, Tavern, Wilderness, and Combat.
3. **Keyboard path unchanged.** Typing a row number + Enter in the prompt input must keep working exactly as today. This is a regression gate, not a nice-to-have.
4. **Mobile interaction baseline (v0.7.0 touch standards):** menu rows are full-width tappable targets, no 300ms tap delay, no double-tap zoom on rapid taps of different rows.
5. **Private mode safe:** the game must still play normally when localStorage is unavailable; the existing try/catch persistence guards stay; nothing persists, nothing crashes.
6. **No storage-format change.** Character data, day state, and saved characters must survive the fix untouched. The save key (`flambeee-cinder-save`) and its JSON shape stay exactly as they are.
7. **Deploy both copies, byte-identical:**
   - `flambeee/src/cinder.html` (in repo, via this PR)
   - `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` (deployed site copy, ABSOLUTE path; `share/` is outside the repo and must never be referenced as a relative path from inside it)
   - After the fix, `cmp` of the two files must report no differences. flambeee.com is broken the same way as the repo copy and must be fixed in the same change.
8. **No other changes.** No visual redesign, no new menu items, no copy edits, no other game files touched. This is a patch release.

## Acceptance Criteria (BDD)

### Scenario 1: Town menu rows work by tap (the reported failure)
- **Given** Cinder is loaded on a mobile viewport and I am at the Town menu
- **When** I tap the "1. Wilderness" row
- **Then** the Wilderness screen appears, exactly as if I had typed 1 and pressed Enter, and the browser console shows no ReferenceError

### Scenario 2: Every menu in every location is tappable
- **Given** Cinder is loaded and I can reach each menu (Town, Weapon Shop, Armor Shop, Bank, Inn, Trainer, Tavern, Wilderness, Combat)
- **When** I tap every row of every menu in each of those locations
- **Then** each tap performs that row's action (moves location, buys, deposits, withdraws, rests, trains, fights, or leaves) and no tap throws a console error

### Scenario 3: Desktop click works
- **Given** Cinder is loaded in a desktop browser at the Town menu
- **When** I click "4. Bank" with the mouse
- **Then** the Bank menu appears

### Scenario 4: Keyboard path regression
- **Given** Cinder is loaded at the Town menu
- **When** I type 2 and press Enter in the prompt input
- **Then** the Weapon Shop opens, same behavior as before the fix

### Scenario 5: Dynamic shop menus tappable
- **Given** I am at the Weapon Shop with enough gold to buy the next weapon
- **When** I tap the "Buy" row and then the "Leave" row
- **Then** the purchase completes and the shop menu closes; the dynamically rendered rows behave like every other row

### Scenario 6: Saves and day state survive
- **Given** I have a saved Cinder character with gold in the bank, day counter advanced, and a level above 1
- **When** I play by tapping, reload the page, and tap again
- **Then** my character data, bank gold, day state, and saved characters are exactly as before the fix, and the save key and JSON shape are unchanged

### Scenario 7: Private mode
- **Given** I open Cinder in a private/incognito window (localStorage unavailable)
- **When** I play through several menus using taps only
- **Then** the game plays normally, nothing persists across reload, and no error is thrown by the persistence try/catch

### Scenario 8: Mobile touch quality baseline
- **Given** a mobile viewport (v0.7.0 touch baseline)
- **When** I tap menu rows, including rapid taps on two different rows in succession
- **Then** rows are full-width tap targets, each tap registers once with no 300ms delay, and no double-tap zoom fires

### Scenario 9: Both copies byte-identical
- **Given** the fix is applied
- **When** the repo file `flambeee/src/cinder.html` is compared with `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`
- **Then** the two files are byte-identical (`cmp` reports no difference)

### Scenario 10: Real browser verification (the coverage gap that shipped #46)
- **Given** QA runs the test plan for this story
- **When** menus are exercised with real browser taps (`page.click()` / `page.tap()`), not keyboard input only
- **Then** every scenario above passes with real taps; keyboard-only testing is not accepted as proof for this story

## Technical notes (Quinn)

- **Root cause (verified in source, 2026-09-01):** IIFE opens at `src/cinder.html:61` (`(function() {`), all menu rows are template strings with inline `onclick="handleMenuClick(N)"` (e.g. lines 306-312 Town, 338/364 shops, 380-382 bank), and `handleMenuClick` is never assigned to `window`. Inline handlers look up `handleMenuClick` on global scope at event time: ReferenceError.
- **Fix choice is Kai's.** Event delegation is preferred (no new globals, one listener, robust to re-rendered rows). Window exposure is acceptable. Document the choice and why in the PR description.
- **Do not** rewrite the menu rendering or refactor the script structure beyond the fix. Minimal diff, patch release.
- **Deploy path:** the deployed site copy lives at `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Use the absolute path. `share/` is outside this repo.
- **Current deployed copy is byte-identical to repo copy** (verified via `cmp` 2026-09-01), so one fix, copied once, fixes both.
- **Test plan:** Scout owns `docs/test-plans/` for this story, including the real-tap Playwright suite that would have caught #46.

## Visual description

None. Zero visual change is a requirement (see Requirement 8). If anything looks different after the fix, it is a bug.

## Open questions

1. **Delegation vs window exposure.** Kai decides (Requirement 1). If window exposure is chosen, confirm no CSP or sandboxing concern exists for the deployed site; delegation avoids the question entirely.
2. **None other.** The failure mode, the fix options, and the deploy targets are all verified. If Kai finds a third option during implementation, raise it in the PR before choosing it.