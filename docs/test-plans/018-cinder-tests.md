# Test Plan: Story 018 — Cinder Core Game Loop

## Objective
Verify the core mechanics, state management, and UI of the Cinder BBS-style text RPG.

## Test Scenarios

### 1. Character Creation & Initialization
- **Test:** Start game with no existing save.
- **Expected:** Prompt for name $\rightarrow$ create L1 character $\rightarrow$ land in Town hub.
- **Verification:** Check `localStorage` for `flambeee-cinder-save`.

### 2. Town Hub & Navigation
- **Test:** Verify visibility of all 6 locations and status line.
- **Expected:** Weapon Shop, Armor Shop, Bank, Inn, Trainer, Tavern visible. Status shows Name, Lvl, HP, Gold, Fights.
- **Test:** Navigate using number keys (1-6) and touch/click.
- **Expected:** Correct location loads.

### 3. Wilderness & Encounters
- **Test:** Enter Wilderness with fights > 0.
- **Expected:** Random encounter (Monster, Treasure, Heal, or Strange Event) triggers.
- **Test:** Enter Wilderness with fights = 0.
- **Expected:** Blocked with message $\rightarrow$ return to Town.

### 4. Combat Mechanics
- **Test:** Combat - Attack.
- **Expected:** Damage resolved (ATK - DEF + var), both HPs update, log updates.
- **Test:** Combat - Run.
- **Expected:** 50% success $\rightarrow$ return to Wilderness; 50% fail $\rightarrow$ monster free attack.
- **Test:** Combat Win.
- **Expected:** XP/Gold gained, Wins +1, Fights -1.

### 5. Death & Revival
- **Test:** Reach 0 HP in combat.
- **Expected:** Gold $\rightarrow$ 0, Fights $\rightarrow$ 0, Deaths +1, sent to Inn.
- **Test:** Revive at Inn.
- **Expected:** HP restored to full for free. Banked gold remains.

### 6. Progression & Services
- **Test:** Level up at Trainer.
- **Expected:** Stats increase per curve if XP threshold met. L10 is cap.
- **Test:** Weapon/Armor Shop purchases.
- **Expected:** Gold deducted, stats update, next upgrade shown.
- **Test:** Bank transactions.
- **Expected:** Deposit/Withdraw balance updates. No over-withdrawal.
- **Test:** Inn healing.
- **Expected:** Pay gold $\rightarrow$ full HP, heal allowance decremented.

### 7. System Constraints
- **Test:** Daily limit (15 fights).
- **Expected:** 16th fight blocked.
- **Test:** Daily reset (UTC midnight).
- **Expected:** Fights/Heals reset when date changes.
- **Test:** Persistence.
- **Expected:** Reload page $\rightarrow$ state preserved.
- **Test:** Private Mode.
- **Expected:** Game playable, no persistence.
