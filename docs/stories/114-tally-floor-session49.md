# Story 114: Tally floor at 0 with status note (Session 49, P1, user-visible polish)

**Status:** Ready for development (Session 49, 2026-11-02).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible polish; v0.42.0 candidate per jakebot, gated on green).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the app file plus the CACHE bump together). Ember is product owner. No shared ownership.
**Tracked by:** Session 49 plan, Story 114. Follows Story 098 (timer validation pattern), Story 101 (Tally build, shipped v0.36.1), Story 112 (dice validation, shipped v0.41.0, the pattern this story copies).
**Depends on:** The shipped Tally at `website/apps/tally.html` and the Story 098/112 status-note pattern at `website/apps/timer.html` and `website/apps/dice.html`. No code dependency on any other story this session: single story, no shared file by construction.

## Summary

Give the Tally app the floor-at-0 pass the timer and dice got for invalid input. Today the minus path has no floor and the load path has no clamp: three real minus clicks from 0 reach -3 with no note, and a seeded -3 survives reload. After this story, minus at 0 keeps 0 and surfaces a plain status note, a seeded negative state clamps to 0 on load, and the note clears on the next successful plus. Plus, reset, label, and valid paths behave exactly as today. One file plus the CACHE bump. v0.42.0 candidate; the release wave decides the cut.

## jakebot decision (advisory only, recorded)

Session 49 Wave 1 priorities per jakebot (session local-fee1a3ef1dca6fccab42040f668381fd701c9645fd8b33fe09bfb2b140369150c1b12efcbcc, proceeded on its read): point D, polish/corrective on the weakest measured app, cut v0.42.0 candidate. Tally measured weakest in the Wave 1 headless-Chromium probe (three minus clicks from 0 reach -3, no status element exists, seeded -3 persists). Flooring is correct: the copy says "one running count", a count of things is not signed, a negative is a wrong state, not a valued use. Scope guard: exactly one existing app file, one named visitor-visible polish item, no new app file/card/key, no redesign. CACHE 17 to 18 rides with it (tally.html is precached, line byte-identical).

**Citation:** `flambeee-team/session-plan.md`, Session 49 (2026-11-02), sections "jakebot decision (advisory only, recorded)" and "Wave 1 measurement".

## Baseline measured at Session 49 planning (2026-11-02 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.41.0 (matches tag v0.41.0) |
| Latest tag / release | v0.41.0 Dice learns to say what it is doing (2026-11-01 09:58 UTC) |
| Open issues / open PRs | 0 / 0 |
| `GAME_ORDER` rotation list | 6/6 |
| App files | 6 (`apps/index.html`, `apps/timer.html`, `apps/tally.html`, `apps/dice.html`, `apps/coin.html`, `apps/convert.html`) |
| Game files | 7 |
| `sw.js` `CACHE_VERSION`, repo mirror | 17 (measured at planning; run must read the line, not assume it) |
| App files in PRECACHE_URLS | all six app files present, including `./apps/tally.html` |
| Tally minus path (probe, headless Chromium, real clicks) | initial 0, three minus clicks reach -1, -2, -3, no status note (no status element exists), negative persists to `flambeee-apps-tally` |
| Tally plus/reset path (same probe) | two plus clicks from -3 reach -1; reset reaches 0 with storage `{"label":"","count":0}` |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the app file (`website/apps/tally.html`) and the `CACHE_VERSION` bump line together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. The polish item (exactly one)

Minus on `website/apps/tally.html` floors at 0 with a plain status note, following the Story 098/112 shape:

- Status element: add one status element to tally.html (the only app without one; coin/convert/dice/timer/index all have a status line with aria-live). Suggested id `tallyStatus`, `aria-live="polite"`, placed in the Setup card next to the buttons, styled like the sibling `#diceStatus` line. Exact markup is the fixer's call; the scenarios below pin behavior, not markup.
- Note text: `Count is at 0. Nothing to remove.`
- Minus at 0: count stays 0, storage stays `{label, count: 0}`, the note surfaces.
- Seeded negative reload: `load()` clamps any finite negative (the measured case is a seeded -3) to 0 on reload. This is the test that matters; it fails today because `load()` at line 167 accepts any finite number.
- Click-path clamp: `minusBtn` never decrements below 0.
- Note clears: the note clears on the next successful plus click (and on reset). Valid paths show no note.
- Plus path unchanged: plus from 0 reaches 1 with no note.
- Reset path unchanged: reset reaches 0 (note cleared).
- Label path unchanged: label input still renders and persists as today.
- Persistence unchanged: still only `{label, count}` under the fixed key `flambeee-apps-tally`. No new persisted field, no new key, stored shape unchanged.

### 3. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (17 to 18) in `website/sw.js`. Nothing else in `sw.js`.
- The precache entry `'./apps/tally.html'` is already present in `PRECACHE_URLS` and stays byte-identical: no new entry, no removed entry, no reordered entry. The dev record states the entry line verbatim plus the version readout before and after.
- Per the v0.33.0 comment rule, a change to an already-precached file needs the bump, so the bump ships with this story.

### 4. Scope guard

In scope: `website/apps/tally.html` (the floor item only) plus the one `CACHE_VERSION` bump line in `website/sw.js`. Untouched: every other app file (Day Pad, timer, dice, coin, convert), every game (`src/`, `games/`, `GAME_ORDER`), the site card surface (no card change), the precache entries, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe.

### 5. Proof bar (release gate)

All six, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. RED on the current tree, then GREEN: the same floor script (minus-at-0, seeded -3 reload, plus-minus-plus, reset, note-clears-on-plus) exits 1 on the pre-change tree (the seeded -3 reload fails at minimum: count stays -3 with no clamp; every case recorded with measured values, none assumed) and exits 0 on the merged tree with all cases passing. The fixer must reproduce RED before touching the file (jakebot caveat: it read source, did not re-run the probe).
3. Desktop 1280x800 with real clicks: each case shows its note (or no note for valid paths), the count reads the expected value, layout holds with overflow 0.
4. Mobile 375x667 with real clicks: same cases, layout holds with overflow 0.
5. Zero page-attributable console errors on both viewports (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
6. `CACHE_VERSION` reads 18 on the merged tree; the tally precache line is present and byte-identical to base.

Release implication, fixed: green keeps a v0.42.0 cut on the table, slip means no tag. The release wave decides the cut.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the app file plus the CACHE bump as single owner, and the dev record states the name.

**Scenario 2: Minus at 0.**
Given the Tally page at count 0 with no note, when minus is clicked, then the count still reads 0, the status line reads `Count is at 0. Nothing to remove.`, and storage still reads `{label, count: 0}`.

**Scenario 3: Seeded -3 reload clamp.**
Given storage seeded to a negative count (the measured case is -3 under `flambeee-apps-tally`), when the page reloads, then the count reads 0 (not -3). (RED anchor: on the current tree the count stays -3 because `load()` accepts any finite number.)

**Scenario 4: Plus minus plus.**
Given the Tally page at count 0, when plus, minus, plus are clicked in order, then the count reads 1 and no note surfaces on the valid steps.

**Scenario 5: Reset.**
Given the Tally page at count 2, when reset is clicked, then the count reads 0 and no note surfaces.

**Scenario 6: Note clears on next plus.**
Given the Tally page showing the floor note after a minus at 0, when plus is clicked, then the count reads 1 and the status line is empty.

**Scenario 7: Persistence unchanged.**
Given the fixed key `flambeee-apps-tally`, when the floor, plus, and reset paths run and the page reloads, then only `{label, count}` persists with the applied count value, and no new field or key exists in storage.

**Scenario 8: CACHE ownership.**
Given the repo `website/sw.js`, when the merged diff is inspected, then the version line reads 17 to 18 and the `'./apps/tally.html'` precache line is byte-identical to base, with no other precache line changed.

**Scenario 9: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one app file plus the CACHE bump line, and every other app, game, schedule, noon, checker, and FPS path shows no diff.

**Scenario 10: Proof bar, desktop.**
Given a local serve, when the floor cases are driven on desktop 1280x800 with real clicks, then all cases pass, layout holds with overflow 0, and zero page-attributable console errors are recorded.

**Scenario 11: Proof bar, mobile.**
Given a local serve, when the floor cases are driven on mobile 375x667 with real clicks, then all cases pass, layout holds with overflow 0, and zero page-attributable console errors are recorded.

**Scenario 12: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a v0.42.0 cut on the table and red (or a slip) means no tag.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Minus at 0 keeps 0 and surfaces the note, storage unchanged (Scenario 2).
**AC-3.** Seeded -3 reload clamps to 0 (Scenario 3).
**AC-4.** Plus minus plus reaches 1 with no note on valid steps (Scenario 4).
**AC-5.** Reset reaches 0 with no note (Scenario 5).
**AC-6.** Floor note clears on the next successful plus (Scenario 6).
**AC-7.** Persistence is `{label, count}` under `flambeee-apps-tally` only; no new field or key (Scenario 7).
**AC-8.** `CACHE_VERSION` 17 to 18 with the tally precache line byte-identical (Scenario 8).
**AC-9.** Diff limited per the scope guard (Scenario 9).
**AC-10.** Desktop 1280x800 real-click run all passing with overflow 0 and zero page-attributable errors (Scenario 10).
**AC-11.** Mobile 375x667 real-click run all passing with overflow 0 and zero page-attributable errors (Scenario 11).
**AC-12.** RED on the current tree (exit 1, cases recorded) then GREEN on the merged tree (exit 0).
**AC-13.** Release-gate rule recorded: green keeps v0.42.0 on the table, slip means no tag (Scenario 12).
**AC-14.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Floor script plus its RED run (exit 1 on the current tree, per-case measured values) and GREEN run (exit 0, all passing); local-serve command plus URL; both-viewport real-click runs with exit codes; overflow readings both viewports; console-error counts with page-attributable versus environmental split; the note text verbatim; storage readout showing `{label, count}` only under `flambeee-apps-tally`; the `CACHE_VERSION` readout before and after plus the unchanged tally precache line verbatim. Numbers, not adjectives.

## Non-Goals

- A second polish item, a redesign, a new app file, a new card, or a new precache entry.
- Any change to Day Pad, the timer, dice, coin, convert, any game, the site design, the schedule, the noon pipeline, or `pending-post.txt`.
- Changing any checker script (this story never touches `scripts/`).
- A new persisted field or key, or a write on any path except the existing save.
- Cutting a version (release wave owns the cut decision and the tag).
