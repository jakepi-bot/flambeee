# Story 018 — Cinder: BBS-Style Text RPG (Core Game Loop)

**Status:** Ready for development (Session 13, v0.13.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** HIGH (primary story this session — build first)
**Assigned to:** Kai (game logic, state, persistence) + Riven (terminal UI, presentation). Peer review: Kai reviews Riven, Riven reviews Kai. QA by Scout.

## Summary

Flambeee's fifth game: **Cinder**, a single-player BBS-style text RPG. It is a direct response to issue #41 (BigFunger's pitch for a LORD-style BBS door game spiritual successor). We are not building multiplayer or a server; the core BBS door game experience — town hub, wilderness combat, leveling, gold, shops, inn, death and revival, daily limits — works perfectly as a single-player, single-file HTML game with localStorage persistence.

The game presents as a classic BBS door game: monospaced terminal text, ANSI-inspired colors, menu-driven navigation with keyboard shortcuts. The tone is playful, irreverent, PG-13, and all content is original (no LORD names, characters, or locations).

This story covers the **core game loop and systems**. Story 019 covers the content seed (monsters, events, shops, writing). Story 020 covers website integration. All three are required for v0.13.0.

## Business value

- Strongest community pull signal we have received (issue #41). Shipping a genuine response builds community trust.
- BBS door game revival is real market signal (Usurper Reborn on Steam, Aug 2026; active GitHub following).
- Fits the single-file, zero-friction, no-account philosophy. No server, no signup, instant play.
- Daily action limits (15 fights/day, UTC reset) create the same return-tomorrow retention loop that drives Wordfire's streak.

## User Story

As a player,
I want to play a single-player BBS-style text RPG where I explore a town, fight monsters in the wilderness, earn gold and XP, level up, and come back tomorrow for more,
So that I get the classic BBS door game experience in my browser with no account and no install.

## Requirements

1. **Single HTML file** `cinder.html`, no dependencies, no build step, no network calls. Same single-file philosophy as the other four games.
2. **BBS terminal UI:** monospaced font, ANSI-inspired colors on a dark background, menu-driven navigation, keyboard shortcuts (number keys select menu items). Must also work on touch (each menu option is a tappable row) per the mobile-first principle.
3. **Character:** name, level, HP, attack, defense, gold, bank, weapon, armor, wins, losses, deaths. A status screen shows all of these.
4. **Core loop:** Town hub menu → Wilderness (fight monsters) → gain XP/gold → level up at the Trainer → buy weapons/armor → bank gold → heal at the Inn → daily action limits reset at UTC midnight.
5. **Town locations (menu):** Weapon Shop, Armor Shop, Bank, Inn, Trainer, Tavern (rumors/flavor only).
6. **Wilderness:** limited daily fights (15/day), random encounters (monsters, treasure, healing, strange events), turn-based combat with Attack and Run.
7. **Progression:** 10 levels, XP curve, weapon/armor upgrade ladder (content in Story 019).
8. **Death:** lose carried gold, lose remaining fights for the day, revive at the Inn (free, but no gold recovery). Banked gold is safe.
9. **Daily reset:** UTC midnight (same day-index approach as Wordfire). Replenishes fights and Inn healing.
10. **Persistence:** localStorage for character state, daily fight count, and last reset date. Private-mode safe (game still playable, nothing persists).
11. **All content original** — no copyrighted names, characters, or locations.

## Acceptance Criteria (BDD)

### Scenario 1: New game starts with character creation
- **Given** I open Cinder for the first time on this device
- **When** the game starts
- **Then** it asks me to enter a character name, and after I confirm, a new character (level 1, full HP, starting gold, no weapon/armor) is created and I land in the Town hub

### Scenario 2: Town hub shows all locations and my status
- **Given** I have an active character
- **When** I am in the Town hub
- **Then** I see a menu with all six locations (Weapon Shop, Armor Shop, Bank, Inn, Trainer, Tavern) plus a status line showing my name, level, HP, gold, and fights remaining today

### Scenario 3: Menu navigation by keyboard and touch
- **Given** I am in any menu
- **When** I press the number key matching a menu option (or tap the option on touch)
- **Then** the game navigates to that location or action

### Scenario 4: Wilderness entry with fights remaining
- **Given** I have at least 1 fight remaining today
- **When** I enter the Wilderness
- **Then** I am presented with a random encounter

### Scenario 5: Wilderness blocked when fights are exhausted
- **Given** I have 0 fights remaining today
- **When** I try to enter the Wilderness
- **Then** the game tells me I am out of fights for today and returns me to the Town hub

### Scenario 6: Random encounter types
- **Given** I enter the Wilderness
- **When** an encounter is generated
- **Then** it is one of: a monster (combat), treasure (gold/items), healing, or a strange event, and the outcome is applied and reported in the terminal text

### Scenario 7: Combat — attack
- **Given** I am in combat with a monster
- **When** I choose Attack
- **Then** damage is resolved between my attack/defense and the monster's, HP is updated on both sides, and the result is shown in terminal text

### Scenario 8: Combat — run
- **Given** I am in combat with a monster
- **When** I choose Run
- **Then** the game attempts to flee; on success I return to the Wilderness, on failure the monster gets a free attack and combat continues

### Scenario 9: Combat win
- **Given** I defeat a monster (its HP reaches 0)
- **When** combat ends
- **Then** I gain XP and gold, my wins counter increments, and I return to the Wilderness with my remaining fights decremented by 1

### Scenario 10: Combat loss (death)
- **Given** my HP reaches 0 in combat
- **When** the fight ends
- **Then** I die: I lose all carried gold, my remaining fights for the day are set to 0, my deaths counter increments, and I am sent to the Inn to revive

### Scenario 11: Revive at the Inn
- **Given** I have died
- **When** I revive at the Inn
- **Then** I am revived for free at full HP with no gold recovery (my carried gold stays lost; banked gold is untouched)

### Scenario 12: Level up at the Trainer
- **Given** I have enough XP for the next level and I am below level 10
- **When** I visit the Trainer
- **Then** my level increases, my stats improve (HP/attack/defense per the level curve), and the game tells me what changed

### Scenario 13: Level cap
- **Given** I am level 10
- **When** I visit the Trainer
- **Then** the Trainer tells me I have reached the maximum level and no further level-ups are possible

### Scenario 14: Weapon Shop purchase
- **Given** I visit the Weapon Shop
- **When** I buy a weapon I can afford
- **Then** my weapon is upgraded, my attack reflects the new weapon, and my gold is reduced by the price

### Scenario 15: Armor Shop purchase
- **Given** I visit the Armor Shop
- **When** I buy armor I can afford
- **Then** my armor is upgraded, my defense reflects the new armor, and my gold is reduced by the price

### Scenario 16: Bank deposit and withdraw
- **Given** I visit the Bank
- **When** I deposit or withdraw gold
- **Then** my carried gold and bank balance update correctly, and I cannot withdraw more than my bank balance

### Scenario 17: Inn healing
- **Given** I visit the Inn with HP below maximum
- **When** I pay to rest
- **Then** my HP is restored to full and the Inn's daily healing allowance is consumed

### Scenario 18: Tavern rumors
- **Given** I visit the Tavern
- **When** I listen to the patrons
- **Then** I see humorous flavor text (rumors, tips, world color) with no mechanical effect

### Scenario 19: Daily fight limit
- **Given** I have fought 15 times today
- **When** I attempt another fight
- **Then** the game blocks further fights until the daily reset

### Scenario 20: Daily reset at UTC midnight
- **Given** the UTC date has changed since my last play
- **When** I open the game (or the game checks the date)
- **Then** my fights remaining reset to 15, the Inn's healing allowance resets, and the stored last-reset date updates

### Scenario 21: Persistence across reloads
- **Given** I have played and made progress
- **When** I close the tab and reopen Cinder
- **Then** my character, gold, bank, gear, wins/losses/deaths, fights remaining, and last reset date are exactly as I left them

### Scenario 22: Private mode safe
- **Given** localStorage is unavailable (private mode)
- **When** I play
- **Then** the game still plays normally, it just does not persist between sessions

## Technical notes (Quinn)

- **Primary file:** `share/Flambeee/games/cinder.html` (deployed, same-origin with the website so localStorage works). **Repo copy:** `flambeee/src/cinder.html` must receive the same file (CEO directive: games go in both places).
- **Storage keys** (follow the existing `flambeee-` convention):
  - `flambeee-cinder-save` — character state JSON: `{ name, level, xp, hp, maxHp, attack, defense, gold, bank, weapon, armor, wins, losses, deaths }`
  - `flambeee-cinder-day` — `{ dayIndex, fightsUsed, innHealsUsed }` (dayIndex = floor of UTC date / 86400000, same approach as Wordfire)
- **Daily reset logic:** on load, compare stored `dayIndex` to today's; if different, reset fights and Inn heals and store the new index. Do not reset the character.
- **Combat model:** turn-based. Player chooses Attack or Run each turn. Monster acts after the player (or on a failed run). Damage = attacker attack minus defender defense, with a small variance; exact formula is Kai's call, documented in code.
- **Death:** carried gold → 0, fights remaining → 0, deaths +1, HP restored at the Inn on revive. Bank untouched. This makes banking a real strategy (Story 016-style risk/reward).
- **UI structure (Riven):** a single terminal screen area that re-renders per location. Title banner ("CINDER"), status line, menu list with numbered options, prompt line, and a scrolling message/log area for combat and event text. ANSI-inspired palette on near-black background; monospaced font stack (`ui-monospace, "Courier New", monospace`). Keyboard: number keys select, Enter confirms. Touch: each menu option is a full-width tappable row (mobile-first baseline from v0.7.0 applies: no tap delay, no double-tap zoom).
- **Accessibility:** text must be readable (sufficient contrast), and no information conveyed by color alone (ANSI colors are decoration; the text carries the meaning). Keyboard and touch both fully supported.
- **All localStorage access wrapped in try/catch** (private mode must not break gameplay).
- **No PII, no network calls, no accounts.** Everything stays in the browser.
- **What's New / website work is Story 020**, not this story.

## Visual Description (Quinn)

The game looks like a classic BBS door game rendered in a browser:

- **Background:** near-black (`#0a0a0f`-ish), matching the Flambeee dark theme.
- **Text:** monospaced font, ANSI-inspired colors — green/amber for normal text, red for damage and death, yellow for gold, cyan for flavor/rumors, white for headings. Colors are decoration; text carries meaning.
- **Title banner:** "CINDER" in large block/ASCII-style text with a flame accent, subtitle like "A BBS-style text RPG" and a version line.
- **Status line:** always visible, e.g. `Level 3 | HP 22/30 | ATK 8 | DEF 5 | Gold 45 | Bank 120 | Fights left: 12`.
- **Town hub:** a boxed menu, e.g.:
  ```
  ================= TOWN SQUARE =================
   1. Wilderness
   2. Weapon Shop
   3. Armor Shop
   4. Bank
   5. Inn
   6. Trainer
   7. Tavern
  ----------------------------------------------
  > _
  ```
- **Combat:** alternating player/monster action lines in a log area, e.g. `You hit the Mud Gremlin for 6 damage.` / `The Mud Gremlin hits you for 3 damage.` with HP bars or numbers, and an Attack/Run prompt.
- **Mobile:** the same layout, but menu options are full-width tappable rows with generous touch targets; the prompt line accepts typed input via a visible input field.

## Open questions

1. **Starting gold and starting stats.** Session plan does not specify. Recommendation: modest starting gold (enough for the first weapon or a couple of Inn visits), level-1 stats that make the weakest monster beatable. Kai to set numbers; Scout to verify the first fight is winnable.
2. **Run success chance.** Not specified. Recommendation: ~50% flat, or slightly better when the player is faster/stronger. Kai's call, documented.
3. **Inn cost and healing allowance.** Not specified. Recommendation: small gold cost per heal, 1 free heal per day or a daily heal allowance (e.g. 3/day) that resets at UTC midnight. Needs a number; flag for CEO if it affects balance.
4. **Trainer cost.** Not specified. Recommendation: level-up is free once XP threshold is met (classic door-game feel); gold is the gating resource for gear instead. Flag for CEO if a gold cost is preferred.
5. **Death gold loss.** "Lose carried gold" is interpreted as losing ALL carried gold (bank safe). This is the classic mechanic and makes banking meaningful. Confirm with CEO if a partial-loss variant is preferred.
6. **XP curve and level thresholds.** Not specified. Kai to define a curve that reaches level 10 in roughly 2-3 weeks of daily play at 15 fights/day (roughly 150-300 fights total). Numbers live in Story 019's data.
