# Story 019 — Cinder: Content Seed (Monsters, Events, Shops, Writing)

**Status:** Ready for development (Session 13, v0.13.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** HIGH (required for v0.13.0 — build after Story 018's systems exist)
**Assigned to:** Kai (data structures, balance numbers) + Riven (writing, tone, presentation of text). Peer review: Kai reviews Riven, Riven reviews Kai. QA by Scout.

## Summary

Story 018 defines Cinder's systems: town, combat, leveling, shops, bank, inn, daily reset. This story defines **what fills those systems**: the monster roster, the random event pool, the weapon/armor upgrade ladders, the level/XP curve, and all the writing. The session plan explicitly scopes this: ~15 monsters, ~20 random events, 10 levels, weapon/armor upgrade ladder, humorous BBS door game tone, all original content.

This is a content story, not a systems story. The data structures and balance numbers are Kai's; the writing and tone are Riven's (with Ember's voice guidance). Both must land in the same single file.

## Business value

- A text RPG lives or dies on its writing and its variety. 15 monsters and 20 events give enough variety for the first weeks of daily play without bloating the file.
- Humor is the differentiator: the BBS door game tone (playful, irreverent, PG-13) is what makes Cinder feel like a door game rather than a spreadsheet.
- Original content keeps us clear of LORD's copyright while honoring the genre (mechanics are not copyrightable; names, characters, and locations are).

## User Story

As a player,
I want a world full of funny monsters, strange events, and a clear ladder of gear to buy,
So that every trip to the Wilderness feels different and I always know what to save up for.

## Requirements

1. **~15 monsters**, each with: name, HP, attack, defense, XP reward, gold reward, and 1-2 lines of humorous flavor text. All original names (no LORD characters). Difficulty spread from "newbie-safe" to "dangerous at level 10".
2. **~20 random events** in the Wilderness, covering: treasure (gold/items), healing, strange events (flavor with small mechanical effects), and at least one "nothing happened" gag. All original writing.
3. **Weapon upgrade ladder:** a chain of weapons from starter to endgame (e.g. 6-8 weapons), each with name, attack bonus, and price. Buying the next weapon requires the previous one (or the shop only offers what you can afford/qualify for).
4. **Armor upgrade ladder:** same structure for armor (defense bonus, price).
5. **10 levels with an XP curve:** XP thresholds per level, and per-level stat gains (HP, attack, defense). Level 10 is the cap.
6. **Shop inventories** derived from the ladders: the Weapon Shop and Armor Shop show the player's current gear, the next upgrade, its price, and whether they can afford it.
7. **Tavern rumors:** a pool of humorous flavor lines (can reuse/rotate event writing, but should feel like town gossip, not wilderness events).
8. **All content original** — no copyrighted names, characters, or locations. BBS door game style is a genre and fine to replicate; specific LORD content is not.
9. **Tone:** playful, irreverent, PG-13. No PII, nothing malicious, nothing political. Dry humor in the CEO's voice (no em-dash flourishes, no heavy emoji — the game text should read like a person wrote it).

## Acceptance Criteria (BDD)

### Scenario 1: Monster roster is seeded
- **Given** the game data is loaded
- **When** I inspect the monster roster
- **Then** it contains at least 15 distinct monsters, each with a name, HP, attack, defense, XP reward, gold reward, and flavor text, and no two monsters share a name

### Scenario 2: Monster difficulty spread
- **Given** the monster roster
- **When** I compare monsters
- **Then** there is a clear difficulty spread: at least one monster a level-1 character can beat, and at least one that is dangerous even at level 10

### Scenario 3: Random event pool is seeded
- **Given** the game data is loaded
- **When** I inspect the event pool
- **Then** it contains at least 20 distinct events covering treasure, healing, strange events, and at least one "nothing happened" gag

### Scenario 4: Weapon ladder is a chain
- **Given** the weapon ladder
- **When** I look at any weapon after the first
- **Then** it is strictly better (higher attack bonus) and strictly more expensive than the previous weapon in the chain

### Scenario 5: Armor ladder is a chain
- **Given** the armor ladder
- **When** I look at any armor after the first
- **Then** it is strictly better (higher defense bonus) and strictly more expensive than the previous armor in the chain

### Scenario 6: Level curve reaches 10
- **Given** the XP curve
- **When** I inspect the level thresholds
- **Then** there are exactly 10 levels, each threshold is higher than the last, and level 10 is the maximum

### Scenario 7: Shop shows current gear and next upgrade
- **Given** I visit the Weapon Shop (or Armor Shop)
- **When** the shop screen renders
- **Then** it shows my current weapon/armor, the next upgrade with its price, and whether I can afford it

### Scenario 8: Tavern has rumors
- **Given** I visit the Tavern
- **When** I listen to the patrons
- **Then** I see humorous flavor text drawn from a rumor pool, and repeated visits can show different rumors

### Scenario 9: No copyrighted content
- **Given** the full game content (monsters, events, shops, rumors, locations)
- **When** I review it
- **Then** no name, character, or location is copied from LORD or any other copyrighted work (original names only)

### Scenario 10: Tone check
- **Given** the full game text
- **When** I read it
- **Then** it is playful and irreverent but PG-13, contains no PII, nothing malicious, and no em-dash or emoji flourishes (plain punctuation, dry humor)

## Technical notes (Quinn)

- **Data lives in the single file** (`share/Flambeee/games/cinder.html` + repo copy `flambeee/src/cinder.html`), as plain JS arrays/objects. No external data files, no fetch.
- **Suggested shapes (Kai's call, documented in code):**
  - `MONSTERS = [{ id, name, hp, atk, def, xp, gold, flavor }]` — 15 entries
  - `EVENTS = [{ id, type: 'treasure'|'heal'|'strange'|'gag', text, effect }]` — 20 entries
  - `WEAPONS = [{ id, name, atk, price }]` — 6-8 entries, index = tier
  - `ARMOR = [{ id, name, def, price }]` — 6-8 entries, index = tier
  - `LEVELS = [{ level, xpNeeded, hpGain, atkGain, defGain }]` — 10 entries
  - `RUMORS = [string]` — a pool of tavern lines
- **Encounter weighting:** monsters should be the common case, events rarer (e.g. ~70/30 or similar). Kai's call; Scout verifies variety over a session of play.
- **Monster scaling:** a monster's stats should be roughly beatable at the level its XP reward targets. Scout will verify the first monster is winnable at level 1 with starting gear and that the top monster is a real threat at level 10.
- **Writing ownership:** Riven writes all flavor/rumor/event text. Ember's voice guidance applies (CEO tone: direct, dry humor, no AI tells). Kai owns numbers and data structure. Both review each other's half.
- **Balance target (from Story 018):** level 10 reachable in roughly 2-3 weeks of daily play at 15 fights/day. XP curve and monster XP rewards should land near that; exact numbers are Kai's call, Scout verifies the shape.
- **No copyrighted content:** names must be original. Genre mechanics (turn-based combat, town menus, daily limits) are fine. If a monster name is even close to a LORD name, rename it.

## Visual Description (Quinn)

No new visuals beyond Story 018's terminal UI. Content appears as text within the existing screens:

- **Monster encounters:** a monster name line with flavor text, e.g. `A Mud Gremlin blocks your path! "You smell like wet socks," it says.` followed by the combat prompt.
- **Events:** a short paragraph of terminal text with the outcome line, e.g. `You find a pouch of 12 gold in a hollow stump.` (gold in yellow), `A strange hermit heals you for 8 HP.` (healing in green).
- **Shops:** a simple list, e.g.:
  ```
  ============ WEAPON SHOP ============
  Current: Rusty Dagger (ATK +2)
  Next:    Iron Sword (ATK +5) — 60 gold
  You have 45 gold. You cannot afford this.
  -------------------------------------
   1. Buy Iron Sword   2. Leave
  ```
- **Tavern:** a rotating rumor line in cyan, e.g. `The barkeep swears the Wilderness gets weirder after midnight. He also swears he once wrestled a bear.`

## Open questions

1. **Exact monster/event content.** The session plan says ~15 monsters and ~20 events. Exact names, stats, and text are the devs' creative call within the constraints (original, PG-13, humorous). Ember reviews tone; Vigil reviews compliance.
2. **Encounter weighting.** Not specified. Recommendation: monsters ~70%, events ~30%, with treasure/heal/strange/gag split inside the event pool. Kai's call.
3. **Weapon/armor ladder length.** Not specified. Recommendation: 6-8 tiers each so there is a purchase roughly every 1-2 levels. Kai's call.
4. **Starting gear.** Not specified. Recommendation: a "Rusty Dagger" (ATK +1) and "Cloth Tunic" (DEF +1) as free starting gear, so the ladders have a tier 0. Confirm with CEO if free starting gear is not desired.
5. **Gold economy.** Not specified. Monster gold rewards, shop prices, and Inn costs must be balanced so a player can afford the next weapon roughly when they reach the level where it matters. Kai sets numbers; Scout verifies the economy is not broken (no infinite loops, no unwinnable states).
