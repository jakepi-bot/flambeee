# Story 112: Dice invalid-input validation message (Session 48, P1, user-visible polish)

**Status:** Ready for development (Session 48, 2026-11-01).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible polish; v0.41.0 vehicle per jakebot, gated on green).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the app file plus the CACHE bump together). Ember is product owner. No shared ownership.
**Tracked by:** Session 48 plan, Story 112. Follows Story 069 (Apps one-pager), Story 092 (second-app one-pager), Story 094 (timer build, shipped v0.35.0), Story 098 (timer validation polish shipped v0.36.0, the pattern this story copies), Story 103 (Dice, shipped v0.37.0).
**Depends on:** The shipped Dice at `website/apps/dice.html` and the Story 098 timer pattern at `website/apps/timer.html`. No code dependency on Story 113 except the no-conflict note below: Story 113 (Kai) touches `scripts/` only and never `website/sw.js`, so there is no sw.js conflict by construction.

## Summary

Give the Dice app the input-validation pass the timer got in Story 098. Today three bad sides inputs plus one non-integer input reach the roll silently: empty sides, below-min (1), above-max (101), and decimal (7.5, which `parseInt` quietly truncates to 7 with no note and no field correction). After this story, every invalid or non-integer sides value surfaces a plain status note and corrects the field to the applied value, exactly the Story 098 shape. Valid input behaves exactly as today. One file plus the CACHE bump. v0.41.0 candidate; the release wave decides the cut.

## jakebot decision (advisory only, recorded)

Session 48 Wave 1 priorities per jakebot (session local-4fe265507574af9c9c587f97844a2ee0c668f23aa8a978b0f47bc54e5213a46f, proceeded on its read): point D, polish/corrective on the weakest measured app, cut v0.41.0. Dice measured weakest in the Wave 1 headless-Chromium probe (empty, 1, and 7.5 all roll with no note; timer and Convert both surface a plain note). Scope guard: exactly one existing app file, one named visitor-visible polish item, no new app file/card/key, no redesign. CACHE 16 to 17 rides with it (every app file precached).

**Citation:** `flambeee-team/session-plan.md`, Session 48 (2026-11-01), sections "jakebot decision (advisory only, recorded)" and "Wave 1 measurement".

## Baseline measured at Session 48 planning (2026-11-01 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.40.0 (matches tag v0.40.0) |
| Latest tag / release | v0.40.0 Echo Rounds (2026-10-31 07:57 UTC) |
| Open issues / open PRs | 0 / 0 |
| `GAME_ORDER` rotation list | 6/6 |
| App cards | 6 (`apps/index.html`, `apps/timer.html`, `apps/tally.html`, `apps/dice.html`, `apps/coin.html`, `apps/convert.html`) |
| `sw.js` `CACHE_VERSION`, repo mirror | 16 (measured at planning; run must read the line, not assume it) |
| App files in PRECACHE_URLS | all six app files present, including `./apps/dice.html` |
| Dice invalid input (probe, headless Chromium, real input) | empty rolls d2 no note; sides=1 rolls d2 no note; sides=7.5 coerces to d7 no note |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the app file (`website/apps/dice.html`) and the `CACHE_VERSION` bump line together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. The polish item (exactly one)

Invalid or non-integer sides input on `website/apps/dice.html` surfaces a plain status note in `#diceStatus` and corrects `#sidesInput` to the applied value, following the Story 098 timer shape:

- Note text: `Enter 2 to 100 sides. Using N.` where N is the applied sides value.
- Field correction: the sides field is set to the applied value at the same time the note surfaces.
- Applied values: empty corrects to 2; below-min (1) corrects to 2; above-max (101) corrects to 100; decimal (7.5) corrects to 7 (truncation toward the applied integer, field shows `7`, label reads `d7 rolled r`).
- Valid path unchanged: an in-range integer (for example 6 or 20) rolls with no note, the field is left untouched, and the readout keeps the `d{n} rolled {r}` shape.
- Persistence unchanged: still only `{sides, last}` under the fixed key `flambeee-apps-dice`. No new persisted field, no new key, stored shape unchanged.

### 3. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (16 to 17) in `website/sw.js`. Nothing else in `sw.js`.
- The precache entry `'./apps/dice.html'` is already present in `PRECACHE_URLS` and stays byte-identical: no new entry, no removed entry, no reordered entry. The dev record states the entry line verbatim plus the version readout before and after.
- Per the v0.33.0 comment rule, a change to an already-precached file needs the bump, so the bump ships with this story.

### 4. Scope guard

In scope: `website/apps/dice.html` (the validation item only) plus the one `CACHE_VERSION` bump line in `website/sw.js`. Untouched: every other app file (Day Pad, timer, Tally, coin, convert), every game (`src/`, `games/`, `GAME_ORDER`), the site card surface (no card change), the precache entries, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe.

### 5. Proof bar (release gate)

All six, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. RED on the current tree, then GREEN: the same five-case input script (empty, 1, 101, 7.5, valid) exits 1 on the pre-change tree (the decimal case fails at minimum: no note, field uncorrected; every case recorded with measured values, none assumed) and exits 0 on the merged tree with 5/5 passing.
3. Desktop 1280x800 with real typed input and clicks: each case shows its note (or no note for valid), the field reads the applied value, layout holds with overflow 0.
4. Mobile 375x667 with real typed input and clicks: same 5/5, layout holds with overflow 0.
5. Zero page-attributable console errors on both viewports (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
6. `CACHE_VERSION` reads 17 on the merged tree; the dice precache line is present and byte-identical to base.

Release implication, fixed: green keeps a v0.41.0 cut on the table, slip means no tag. The release wave decides the cut.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the app file plus the CACHE bump as single owner, and the dev record states the name.

**Scenario 2: Empty sides.**
Given the Dice page, when the sides field is cleared and Roll is clicked, then the status line reads `Enter 2 to 100 sides. Using 2.`, the field reads `2`, and the roll is a d2 roll.

**Scenario 3: Below-min sides.**
Given the Dice page, when `1` is typed into the sides field and Roll is clicked, then the status line reads `Enter 2 to 100 sides. Using 2.`, the field reads `2`, and the roll is a d2 roll.

**Scenario 4: Above-max sides.**
Given the Dice page, when `101` is typed into the sides field and Roll is clicked, then the status line reads `Enter 2 to 100 sides. Using 100.`, the field reads `100`, and the roll is a d100 roll.

**Scenario 5: Decimal sides.**
Given the Dice page, when `7.5` is typed into the sides field and Roll is clicked, then the status line reads `Enter 2 to 100 sides. Using 7.`, the field reads `7`, and the label reads `d7 rolled r`. (RED anchor: on the current tree this case shows no note and leaves the field at `7.5`.)

**Scenario 6: Valid sides unchanged.**
Given the Dice page, when a valid integer such as `20` is typed and Roll is clicked, then no validation note surfaces, the field still reads `20`, and the label reads `d20 rolled r`.

**Scenario 7: Persistence unchanged.**
Given the fixed key `flambeee-apps-dice`, when invalid input is corrected and the page reloads, then only `{sides, last}` persists with the applied sides value, and no new field or key exists in storage.

**Scenario 8: CACHE ownership.**
Given the repo `website/sw.js`, when the merged diff is inspected, then the version line reads 16 to 17 and the `'./apps/dice.html'` precache line is byte-identical to base, with no other precache line changed.

**Scenario 9: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one app file plus the CACHE bump line, and every other app, game, schedule, noon, checker, and FPS path shows no diff.

**Scenario 10: Proof bar, desktop.**
Given a local serve, when the five cases are driven on desktop 1280x800 with real typed input and clicks, then 5/5 pass, layout holds with overflow 0, and zero page-attributable console errors are recorded.

**Scenario 11: Proof bar, mobile.**
Given a local serve, when the five cases are driven on mobile 375x667 with real typed input and clicks, then 5/5 pass, layout holds with overflow 0, and zero page-attributable console errors are recorded.

**Scenario 12: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a v0.41.0 cut on the table and red (or a slip) means no tag.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Empty sides surfaces the note and corrects the field to 2 (Scenario 2).
**AC-3.** Sides of 1 surfaces the note and corrects the field to 2 (Scenario 3).
**AC-4.** Sides of 101 surfaces the note and corrects the field to 100 (Scenario 4).
**AC-5.** Sides of 7.5 surfaces the note and corrects the field to 7 (Scenario 5).
**AC-6.** Valid integer input rolls with no note and the field untouched (Scenario 6).
**AC-7.** Persistence is `{sides, last}` under `flambeee-apps-dice` only; no new field or key (Scenario 7).
**AC-8.** `CACHE_VERSION` 16 to 17 with the dice precache line byte-identical (Scenario 8).
**AC-9.** Diff limited per the scope guard (Scenario 9).
**AC-10.** Desktop 1280x800 real-input run 5/5 with overflow 0 and zero page-attributable errors (Scenario 10).
**AC-11.** Mobile 375x667 real-input run 5/5 with overflow 0 and zero page-attributable errors (Scenario 11).
**AC-12.** RED on the current tree (exit 1, cases recorded) then GREEN on the merged tree (exit 0).
**AC-13.** Release-gate rule recorded: green keeps v0.41.0 on the table, slip means no tag (Scenario 12).
**AC-14.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Five-case script plus its RED run (exit 1 on the current tree, per-case measured values) and GREEN run (exit 0, 5/5); local-serve command plus URL; both-viewport real-input runs with exit codes; overflow readings both viewports; console-error counts with page-attributable versus environmental split; the note text verbatim; storage readout showing `{sides, last}` only under `flambeee-apps-dice`; the `CACHE_VERSION` readout before and after plus the unchanged dice precache line verbatim. Numbers, not adjectives.

## Non-Goals

- A second polish item, a redesign, a new app file, a new card, or a new precache entry.
- Any change to Day Pad, the timer, Tally, coin, convert, any game, the site design, the schedule, the noon pipeline, or `pending-post.txt`.
- Changing any checker script (Story 113 owns `scripts/`; this story never touches it).
- A new persisted field or key, or a write on any path except the existing save.
- Cutting a version (release wave owns the cut decision and the tag).
