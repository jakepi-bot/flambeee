# Test Plan: Story 019 — Cinder Content Seed

## Objective
Verify the variety, balance, and tone of the seeded game content.

## Test Scenarios

### 1. Monster Roster
- **Test:** Count unique monsters.
- **Expected:** $\ge 15$ distinct monsters.
- **Test:** Difficulty gradient.
- **Expected:** L1 can beat easiest monster; L10 challenged by hardest.

### 2. Event Pool
- **Test:** Count unique events.
- **Expected:** $\ge 20$ events.
- **Test:** Type variety.
- **Expected:** Treasure, Heal, Strange, and Gag events all present.

### 3. Gear Ladders
- **Test:** Weapon chain.
- **Expected:** 8 tiers, each strictly better ATK and more expensive than previous.
- **Test:** Armor chain.
- **Expected:** 8 tiers, each strictly better DEF and more expensive than previous.

### 4. Leveling Curve
- **Test:** XP thresholds.
- **Expected:** 10 levels, increasing thresholds.
- **Test:** Stat gains.
- **Expected:** Consistent gains per level.

### 5. Tone & Compliance
- **Test:** Text review.
- **Expected:** No em dashes (—), no heavy emoji, no PII, no copyrighted LORD content.
- **Test:** Tavern rumors.
- **Expected:** Variety of humorous rumors on repeated visits.
