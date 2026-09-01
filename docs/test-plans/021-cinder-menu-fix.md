# Test Plan: 021 - Cinder Menu Tap/Click Fix

## Goal
Verify that all menu interactions in Cinder work via tap/click on all devices (mobile/desktop) without console errors, while ensuring zero regressions in keyboard input, visual appearance, and storage format.

## Test Environment
- **Worktree:** `/home/jake/.openclaw/workspace/flambeee-kai` (fixed copy)
- **Baseline:** `/home/jake/.openclaw/workspace/flambeee/src/cinder.html` (broken copy)
- **Tooling:** Playwright (Chromium), Python 3.12
- **Viewports:** Desktop (1280x800), Mobile (390x844, has_touch: true)

## BDD Scenario Verification

| Scenario | Description | Method | Success Criterion |
| :--- | :--- | :--- | :--- |
| 1 | Town menu rows work by tap | `page.tap()` on row 1 | Wilderness screen appears; no `ReferenceError` |
| 2 | Every menu in every location tappable | `page.click()` all rows | Action performs; no console errors |
| 3 | Desktop click works | `page.click()` on Bank | Bank menu appears |
| 4 | Keyboard path regression | Type '2' + Enter | Weapon Shop opens |
| 5 | Dynamic shop menus tappable | `page.click()` Buy/Leave | Purchase completes / menu closes |
| 6 | Saves and day state survive | Play -> Reload -> Play | Gold/Level/Bank state identical |
| 7 | Private mode safe | Incognito / Block Storage | Game plays; no crash; nothing persists |
| 8 | Mobile touch baseline | Rapid taps / Multi-row | No double-tap zoom; full-width targets |
| 9 | Both copies byte-identical | `cmp` (repo vs share) | Exit code 0 |
| 10 | Real browser verification | `page.tap()` / `page.click()` | All above pass via browser events |

## Edge Cases & Boundary Conditions
- **Delegation Depth:** Click exactly on the `<span>` inside the `.menu-row` to ensure `e.target.closest()` works.
- **Affordability Flip:** Buy a weapon until gold is insufficient; verify the "Buy" row dynamically changes to "Leave" (or similar) and remains tappable.
- **Combat Routing (The Second Fix):** 
    - Enter combat -> Tap "Attack" until win -> Verify Wilderness menu returns.
    - Enter combat -> Tap "Run" -> Verify escape logic.
    - Verify keyboard '1' (Attack) and '2' (Run) in combat work.
- **Max Level:** Reach Level 10 -> Trainer "Level Up" row should be disabled or route to "Max Level" message.
- **Zero Fights:** Use all 15 fights -> Verify Wilderness entry is blocked.

## Visual Regression
- Capture bounding box of a standard menu row (e.g., Bank) on broken vs fixed build. Delta must be < 0.5px.
