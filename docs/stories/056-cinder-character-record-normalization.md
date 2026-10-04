# Story 056: Cinder Character-Record Load Normalization (Session 28, P1, Corrective)

**Status:** Ready for development (Session 28, 2026-10-04).
**Author:** Parent (written directly by the parent overseer; see "Author note" below).
**Priority:** P1 (corrective; closes the character-record half of the load-path family).
**Assigned to:** **Kai** owns the pure normalization helper and extends the proof script. **Riven** owns the call-site line in `init()` if the fix lands there. The parent names the exact line before either dev starts, per the Story 048 protocol.
**Tracked by:** Session 28 plan, Story 056. Mirror of Story 053 (shipped v0.25.0) on the character-record side.

**Author note:** Quinn was spawned for this story with the full Wave 2 brief and returned
`status: ok` having written no files. Its final message was "Writing the stories now," which is
a progress statement, not a completion report. Verification on disk found no story files, no
branch, no PR, and `requirements-handoff.md` still dated 2026-10-02. The parent wrote this story
per the fallback in the session plan. Quinn's one substantive claim, that its probes covered the
real extracted functions, was re-measured rather than trusted, and checking it is what surfaced
defects G2, G3, H1 and H2. So the run was worth 4 of 7 defects and 0 of 3 story files.

## Summary

Story 053 shipped in v0.25.0 and normalized the **day record** once, on load, in memory:

```js
dayState = normalizeDayRecord(loadDayState());   // src/cinder.html:1518
```

It did this because the read surfaces had each grown their own private guard, and the record
itself was never checked once. That reasoning applies verbatim to the character record, and the
character record has no equivalent.

`loadSave()` (`src/cinder.html:827-834`) is the whole of the load path:

```js
function loadSave() {
  try {
    const data = localStorage.getItem(SAVE_KEY);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    return null;
  }
}
```

It returns the raw `JSON.parse` product. No shape check, no field normalization. `init()` assigns
it straight to `character` at `src/cinder.html:1517`, and from there every stat helper, every
affordability gate and the equipment lookup reads it.

The documented character shape, from `createCharacter()` (`src/cinder.html:1600-1615`), is:

```
{ name, level, xp, hp, maxHp, attack, defense, gold, bank, weapon, armor, wins, losses, deaths }
```

Fourteen fields, none of them checked on load.

### Why this is worth a session

Seven defects were reproduced by executing the real functions, not by reading them. Six are
fixed here. All six are **silent**: none throws, none logs, none surface in the UI. A player
whose save is damaged by any of these gets a game that looks like it is working.

| ID | Seed | Measured on v0.25.0 | Player-visible effect |
|---|---|---|---|
| A | `gold: "abc"` | `character.gold >= 10` -> `false` | Shop, inn and bank refuse forever. No error shown. |
| C | `level: null` | `attack=0 defense=0 maxHp=0` | Hero permanently has zero stats. Nothing reports it. |
| G2 | `weapon: "2"` | `attack=6`, same as bare | Gear bonus silently vanishes. |
| G3 | `armor: "2"` | `defense=3`, same as bare | Same on the armor side. |
| H1 | `hp: -50` | `hp=-50` | Hit-point bar below zero. |
| H2 | `hp: 1e9, maxHp: 26` | `hp=1000000000` vs max 26 | Bar 38 million times its own maximum. |

Seventh defect (E, unreadable storage destroys progress) is **out of scope here** and routed to
Story 058. It is a product decision wearing a bug's clothes.

### The trap in G2/G3, recorded so nobody "fixes" the wrong thing

A string `weapon` id is the same class of input as a string `level`, and string `level` was
**tested and found harmless**. Two hypotheses died on the way to this story, both measured
against the real functions:

- `level: "3"` is safe. `character.level++` coerces, `LEVELS[level-1]` resolves, stats come out
  right.
- `level: "9"` is safe. This was the real test of the level-cap comparison, and `'9' >= 10`
  coerces to `true`, so `canLevelUp()` agrees with the numeric case.

The reason `weapon: "2"` **is** a defect while `level: "3"` is not, is the strict `===` in
`getTotalAttack()` (`src/cinder.html:886`):

```js
const weapon = WEAPONS.find(w => w.id === character.weapon)?.atk || 0;
```

Equality against a table row does not coerce. `<` and `++` coerce; `===` against `id` does not.
So "string fields are probably fine here too" was the wrong inference, and only execution
settled it. The general rule for this record: **anything compared by strict equality against a
table row or a constant must be a number.** Anything only used in arithmetic will coerce on its
own and needs no rule.

A third hypothesis also died: `level: 99` is already safe, clamped by the loop bound in
`getBaseStats()`. A fourth, G1 "numeric equipment ids add their bonus", looked like a defect and
was not: the harness had hardcoded `defense === 11` when the real level-3 base is 6/3, so gear
yields 15/10. The harness now measures the gear **delta** against a measured baseline.

## Requirements

### 1. Normalize once on load, in memory

Add one pure helper `normalizeCharacterRecord(raw)` next to `normalizeDayRecord()`. Call it
**once**, at the `init()` call site:

```js
character = normalizeCharacterRecord(loadSave());   // replaces src/cinder.html:1517
```

Single call site, mirroring `:1518`. Not inside `loadSave()`, not at each read surface. The
point of the fix is that the record is repaired in one place, so a reviewer can audit one place.
If it is spread across readers, it is the piecemeal arrangement Story 053 just removed.

`loadSave()` itself is **not** changed. It stays the raw reader it is today. Its job is to hand
back what is in storage, or `null`.

### 2. Field rules (documented shape)

The record carries fourteen fields. Rules for each group:

- **`level`, `xp`, `gold`, `bank`**: finite integers. A non-number, `NaN`, infinite, negative or
  fractional value normalizes to `0`. **Exception: `level` floors to a minimum of 1**, not 0, so
  defect C cannot recur. `Math.floor` a positive fractional `level` to at least 1. This is what
  makes `getBaseStats()` return nonzero stats.
- **`hp`**: clamped to `[0, maxHp]`, where `maxHp` is the normalized `maxHp`. This closes H1
  (negative) and H2 (past its own maximum). Order matters: normalize `maxHp` first, then clamp
  `hp` against the result.
- **`maxHp`**: a finite integer, floored at 0. If `maxHp` is 0 after normalization while `hp` is
  positive, `hp` clamps to 0. Do not invent a fallback maximum; the stat helpers already derive
  the real maximum from `getBaseStats(level)`.
- **`weapon`, `armor`**: finite integers, floored at 0, defaulting to 0. This closes G2 and G3.
  The strict `===` in `WEAPONS.find()` and `ARMOR.find()` is the reason. A string id normalizes
  to a number and the bonus is found again.
- **`wins`, `losses`, `deaths`**: finite integers, floored at 0. Defensive; not currently a
  reproduced defect, but they are counters and belong to the same group.
- **`name`**: a string, trimmed, cut to 20 characters, matching `createCharacter()`'s
  `name.substring(0, 20)`. A non-string, `null`, `undefined` or missing value becomes `''`. A
  record written by the game always has a string name, so this is a no-op for every legitimate
  record. It matters because the name is interpolated into the status line and the log.
- **`attack`, `defense`**: **pass through unchanged, and do not normalize them.** These two
  stored fields are vestigial. `getTotalAttack()` and `getTotalDefense()` (`src/cinder.html:884`,
  `:890`) compute the real values from `getBaseStats(level)` plus the equipment bonus; they never
  read the stored fields. Normalizing dead fields is inventing a contract the code does not have.
  Flag them to the parent if that reading is wrong, but do not silently add rules.

Do not invent fields. Do not add fields. A record written by this session must have exactly the
fourteen fields `createCharacter()` writes.

### 2b. What the normalizer must not do

- Must not **write**. No `localStorage.setItem` on the load path. Zero writes when loading.
- Must not **migrate** or persist the normalized shape back. The stored record keeps its shape
  until the next ordinary `saveCharacter()`.
- Must not **add or remove fields**. Same fourteen keys in, same fourteen keys out.
- Must not **throw**. Given any input, including `null`, a number, a string, an array, or an
  object with wrong types everywhere, it returns either a well-formed record or `null`. It never
  throws and never returns a partially built record.
- Must not **change behavior for a well-formed record.** A save written by v0.25.0 must load to
  the same numbers, the same name and the same equipment after this story.

### 3. `null` and non-object input

`normalizeCharacterRecord` follows `normalizeDayRecord`'s precedent: a non-object, `null`, or
array input returns `null`. `init()` already handles `!character` by calling
`showCharacterCreation()` (`src/cinder.html:1535`), so this is an existing, working path and
needs no new handling.

Note the interaction with Story 058: `null` here routes to a new game, which is precisely the
behavior decision deferred there. Do **not** add a message, a notice or a retry. That is Story
058's scope and it needs CEO sign-off.

### 4. Frozen functions (binding)

Byte-identical to v0.25.0. Any change needs a separate story.

- `getBaseStats()` (`src/cinder.html:874`)
- `getMaxHp()` (`:896`)
- `getTotalAttack()` (`:884`)
- `getTotalDefense()` (`:890`)
- `getXpForLevel()` (`:900`)
- `canLevelUp()` (`:905`)
- `levelUp()` (`:910`)
- `createCharacter()` (`:1600`)
- `normalizeDayRecord()` (`:515`) and every day-record path
- `loadDayState()` (`:842`), `saveCharacter()` (`:836`)

The equipment tables `WEAPONS` (`:89`) and `ARMOR` (`:100`) are frozen. The fix is on the record
side; the tables are correct as written.

## Acceptance Criteria (Given/When/Then)

**AC-1, the control.** Given a well-formed save written by v0.25.0, when `init()` loads it, then
every field is identical to the stored value: name, level, xp, hp, maxHp, gold, bank, weapon,
armor, wins, losses, deaths.

**AC-2, zero writes.** Given any save, when the record is loaded, then `localStorage.setItem` is
called **zero** times on the load path.

**AC-3, no new fields.** Given a save, when it is normalized, then the resulting record has
exactly the fourteen keys `createCharacter()` writes, with no additions and no removals.

**AC-4, defect A (gold).** Given a save with `gold: "abc"`, when it is normalized, then `gold` is
the finite integer `0`, and `character.gold >= 10` evaluates to `false` **without throwing**. The
player can still earn gold and buy things afterwards.

**AC-5, defect C (null level).** Given a save with `level: null`, when it is normalized, then
`level` is `1`, and `getTotalAttack()`, `getTotalDefense()` and `getMaxHp()` all return values
**greater than zero**.

**AC-6, defects G2/G3 (equipment ids).** Given a save with `weapon: "2"` and `armor: "2"`, when
it is normalized, then both are the integer `2`, and `getTotalAttack()` and `getTotalDefense()`
each exceed their bare (equipment-free) baselines by the equipment's bonus.

**AC-7, defect H1 (negative hp).** Given a save with `hp: -50`, when it is normalized, then `hp` is
in `[0, maxHp]`, specifically `0`.

**AC-8, defect H2 (hp past max).** Given a save with `hp: 1e9` and `maxHp: 26`, when it is
normalized, then `hp` is `26`, not `1e9`.

**AC-9, no throw on garbage.** Given each of: `null`, `42`, `"a string"`, `[]`,
`{}`, and an object whose every field is the wrong type, when the normalizer runs, then it
returns either `null` or a well-formed record, and never throws.

**AC-10, name.** Given `name: 42`, `name: null`, and a 50-character name, when normalized, then
`name` is a trimmed string of at most 20 characters.

**AC-11, fractional and negative counters.** Given `xp: 12.7`, `gold: -5`, `wins: 3.2`, when
normalized, then each is a non-negative integer (`12`, `0`, `3` respectively).

**AC-12, missing record.** Given no save in storage, when `init()` runs, then `loadSave()`
returns `null`, the normalizer returns `null`, and the existing `showCharacterCreation()` path
runs unchanged.

**AC-13, dead fields.** Given a save with `attack: "junk"` and `defense: null`, when normalized,
then both pass through unchanged, because `getTotalAttack()` and `getTotalDefense()` do not read
them. *(If the parent rules that these fields are live, this AC is replaced before dev starts.)*

**AC-14, single call site.** Given a grep of `src/cinder.html`, when `normalizeCharacterRecord`
is searched for, then there is exactly **one** call site, at `init()`, and zero call sites inside
`loadSave()` or inside any read surface.

## Required Proof

**Extend the existing harness. Do not write a parallel script.**

`flambeee-team/runs/session28-loadsave-repro.py` already extracts the real functions out of
`src/cinder.html` and executes them. It currently reports `DEFECTS REPRODUCED: 7 (A, C, E, G2, G3,
H1, H2)`, exit 1. Story 056 adds `normalizeCharacterRecord` to the extraction set, points
`character` at the normalized record, and asserts the same invariants.

The proof obligation is unchanged and is exactly the Wave 1/2 obligation:

| Run | Target | Expected |
|---|---|---|
| 1 | tagged **v0.25.0** | **exit 1**, defects A, C, G2, G3, H1, H2 present |
| 2 | **merged candidate** on main | **exit 0**, all invariants hold |

Both runs are mandatory. Run 1 is what makes run 2 mean anything: a script that passes on both
targets has proven nothing. Quote the numeric output, not adjectives.

### Harness traps already paid for on 2026-10-04

Five defects in the proof harness itself initially printed as product behaviour. Whoever picks
this up should not re-learn them:

1. **The silent-defect counter.** The first version asserted only on "did it throw", printed three
   reproduced defects directly above `DEFECTS REPRODUCED: 0`, and exited **0**. Defects A, C, G2
   and G3 all exit 0 because they are silent. **Assert on invariants, not on exceptions.** A green
   exit from a proof script is a claim about the script, not about the product.
2. **`localStorage` shadowing.** Node 26 exposes a native read-only `localStorage`; a plain
   assignment is silently ignored. Rewrite references to a shim.
3. **Missing `SAVE_KEY`.** Without it the `try`/`catch` swallows a `ReferenceError` and returns
   `null`, which reads exactly like "no save present."
4. **Missing `character` binding.** The stat helpers read a module-level `character`. Undeclared,
   the first stat call dies with `ReferenceError`. Hit twice, in two harnesses.
5. **Unrestored storage reader.** After the DEFECT-E case swaps the reader for a thrower, every
   later `load()` returns `null` and the following cases die on `null.level`. Restore it, with a
   comment saying why.

**If the harness reports a defect nobody predicted, suspect the harness before the product.**
Every one of those five would have reached the CEO as a product bug.

## Non-Goals (out of scope for this story)

- **Defect E, unreadable storage.** Whether an unreadable store should silently start a new game,
  warn the player, or refuse is a product decision. **Story 058**, and it needs CEO sign-off.
- The level cap of 10 (`canLevelUp()` and `levelUp()` both test `>= 10`).
- The daily reset, the quest record, and stored history. Story 053 owns the day side.
- Cinder offline accrual and the welcome-back suppression across a later UTC day. Both are on the
  roadmap's Future list, both need CEO sign-off, and Story 055 already recorded them as open.
- A save-version field or any migration mechanism. The record has no version and this story does
  not add one.
- Cleaning up the vestigial stored `attack` and `defense` fields. Noted in AC-13, not acted on.

## Open questions (need the parent's ruling before dev starts)

1. **`maxHp` normalization.** AC-2 says clamp `hp` to `[0, maxHp]`. If `maxHp` itself normalizes to
   `0` while `hp` is positive, `hp` becomes 0. Alternative: leave `hp` alone when `maxHp` is 0,
   since the real maximum comes from `getBaseStats(level)`. **Parent's call.** Default unless
   overruled: clamp as written.
2. **Are stored `attack`/`defense` live?** This story reads them as vestigial and passes them
   through (AC-13). If they are read anywhere, that is a defect class of its own and needs its own
   story.