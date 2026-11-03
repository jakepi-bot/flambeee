# Story 115: Timer decimal-minutes note plus field correction plus paused-resume note guard (Session 50, P1, user-visible polish)

**Status:** Ready for development (Session 50, 2026-11-03).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible polish; v0.43.0 candidate per jakebot, gated on green).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the app file plus the CACHE bump together). Ember is product owner. No shared ownership.
**Tracked by:** Session 50 plan, Story 115. Follows Story 098 (timer validation pattern, shipped v0.36.0), Story 112 (dice validation, shipped v0.41.0, the pattern this story copies), Story 114 (tally floor, shipped v0.42.0).
**Depends on:** The shipped Timer at `website/apps/timer.html` and the Story 112 dice shape at `website/apps/dice.html` (`invalidSides` at dice.html:157). No code dependency on any other story this session: single story, no shared file by construction.

## Summary

Give the Timer app the decimal-minutes pass the dice got in Story 112. Today a decimal minutes input reaches Start silently: typing 7.5 and pressing Start leaves the field at 7.5 with no note while the clock runs 7 minutes, so the field and the clock disagree. After this story, non-integer minutes surfaces the plain note `Enter 1 to 999 minutes. Using 7.` and corrects the field to the applied integer, so clock and field agree, plus the paused-resume path stops lying: a bad value typed into the field while paused no longer applies a note for a duration the timer never adopts. Valid input behaves exactly as today. One file plus the CACHE bump. v0.43.0 candidate; the release wave decides the cut.

## jakebot decision (advisory only, recorded)

Session 50 Wave 1 priorities per jakebot (session local-f4720a1b82376a75caa21b629cd6578f613ede4fc0c8aec229d0099995c938cd, proceeded on its read): point D, timer decimal polish, not close. Seventh-app option dead on the seventh-app rule (0 demand signal). FPS step hardware-blocked with the keyboard slice shipped. Second original mechanic premature (Echo Rounds 3 days old, zero reception data). No-cut fails because D is real, cheap, and already measured. Scope, same story not a new one: (1) timer `invalidMinutes` non-integer check mirroring dice `invalidSides` (dice.html:157, Number plus Math.trunc), same note shape; (2) `start()` note-lie guard: only apply and note when remainingMs <= 0, since on paused resume the note says "Using N" while the timer resumes leftover time. Cut: **v0.43.0 candidate stays on the table; the release wave decides.** Precedent Sessions 40-49: each shipped a named story, each cut. Gate rule fixed: green keeps a cut on the table, slip means no tag.

**Citation:** `flambeee-team/session-plan.md`, Session 50 (2026-11-03), sections "jakebot decision (advisory only, recorded)" and "Wave 1 measurement".

## Baseline measured at Session 50 planning (2026-11-03 01:10 CST)

| Check | Value |
|---|---|
| Website What's New heading | v0.42.0 (matches tag v0.42.0) |
| Latest tag / release | v0.42.0 Tally stops counting below zero (2026-11-02 08:58 UTC) |
| Open issues / open PRs | 0 / 0 |
| `sw.js` `CACHE_VERSION`, repo mirror | 18 (measured at planning; run must read the line, not assume it) |
| App files in PRECACHE_URLS | all six app files present, including `./apps/timer.html` |
| Timer decimal path (probe, headless Chromium, real input) | type 7.5, press Start: field stays `7.5`, status `''`, readout `07:00`. RED, 2 cases failed |
| Timer control path (same probe) | type 0, Start: status `Enter 1 to 999 minutes. Using 1.`, field `1`. Story 098 intact |
| Code read | `invalidMinutes` (timer.html:193) uses parseInt, so 7.5 reads valid; `parseMinutes` truncates to 7 for the clock but the field-correction branch never runs |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the app file (`website/apps/timer.html`) and the `CACHE_VERSION` bump line together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. The polish item: non-integer minutes note plus field correction

Non-integer minutes input on `website/apps/timer.html` surfaces a plain status note and corrects the minutes field to the applied integer, mirroring dice `invalidSides` (dice.html:157, Number plus Math.trunc), same note shape as Story 098:

- Non-integer check: `invalidMinutes` treats any non-integer numeric input (for example 7.5) as invalid, using Number plus Math.trunc the way `invalidSides` does. `parseMinutes` already truncates toward the applied integer, so the clock keeps running the truncated value.
- Note text: `Enter 1 to 999 minutes. Using 7.` where 7 is the applied integer for the measured 7.5 case.
- Field correction: the minutes field is set to the applied integer at the same time the note surfaces, so the field and the clock agree.
- Valid path unchanged: an in-range integer (for example 5) starts with no note and the field left untouched.
- Out-of-range paths unchanged per Story 098: 0, empty, and 1000 still note and correct exactly as today.
- Persistence schema unchanged: still only the last-used duration under the fixed key `flambeee-apps-timer`. No new persisted field, no new key, stored shape unchanged.

### 3. The polish item: paused-resume note guard in `start()`

`start()` only applies the field value and only notes when remainingMs <= 0:

- On a fresh start (remainingMs <= 0), behavior is the decimal path above: apply, note, correct.
- On a paused resume (remainingMs > 0), the timer resumes the leftover time and applies no field value and surfaces no "Using N" note for the field contents, so the note can never claim a duration the timer did not adopt.
- Reset path keeps its existing note behavior; this guard touches `start()` only.

### 4. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (18 to 19) in `website/sw.js`. Nothing else in `sw.js`.
- The precache entry `'./apps/timer.html'` is already present in `PRECACHE_URLS` and stays byte-identical: no new entry, no removed entry, no reordered entry. The dev record states the entry line verbatim plus the version readout before and after.
- Per the v0.33.0 comment rule, a change to an already-precached file needs the bump, so the bump ships with this story.

### 5. Scope guard

In scope: `website/apps/timer.html` (the decimal item plus the `start()` guard only) plus the one `CACHE_VERSION` bump line in `website/sw.js`. Untouched: every other app file (Day Pad, Tally, dice, coin, convert), every game (`src/`, `games/`, `GAME_ORDER`), the site card surface (no card change), the precache entries, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe.

### 6. Proof bar (release gate)

All six, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. RED on the current tree, then GREEN: the same decimal script (7.5 typed plus Start, integer-valid, 0/empty/1000 per 098, pause-resume no-lie) exits 1 on the pre-change tree (the decimal 7.5 case fails at minimum: field stays 7.5 with status empty; every case recorded with measured values, none assumed) and exits 0 on the merged tree with all cases passing.
3. Desktop 1280x800 with real typed input and clicks: each case shows its note (or no note for valid paths), the field reads the applied value, layout holds with overflow 0.
4. Mobile 375x667 with real typed input and clicks: same cases, layout holds with overflow 0.
5. Zero page-attributable console errors on both viewports (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
6. `CACHE_VERSION` reads 19 on the merged tree; the timer precache line is present and byte-identical to base.

Release implication, fixed: green keeps a v0.43.0 cut on the table, slip means no tag. The release wave decides the cut.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the app file plus the CACHE bump as single owner, and the dev record states the name.

**Scenario 2: Decimal 7.5, the test that matters.**
Given the Timer page, when `7.5` is typed into the minutes field and Start is pressed, then the status line reads `Enter 1 to 999 minutes. Using 7.`, the field reads `7`, and the readout starts at `07:00`. (RED anchor: on the current tree the field stays `7.5` with status empty while the readout shows `07:00`.)

**Scenario 3: Integer-valid unchanged.**
Given the Timer page, when `5` is typed into the minutes field and Start is pressed, then no validation note surfaces, the field still reads `5`, and the readout starts at `05:00`.

**Scenario 4: 0 still notes per 098.**
Given the Timer page, when `0` is typed into the minutes field and Start is pressed, then the status line reads `Enter 1 to 999 minutes. Using 1.` and the field reads `1`.

**Scenario 5: Empty still notes per 098.**
Given the Timer page, when the minutes field is cleared and Start is pressed, then the status line reads `Enter 1 to 999 minutes. Using 1.` and the field reads `1`.

**Scenario 6: 1000 still notes per 098.**
Given the Timer page, when `1000` is typed into the minutes field and Start is pressed, then the status line reads `Enter 1 to 999 minutes. Using 999.` and the field reads `999`.

**Scenario 7: Pause-resume no-lie.**
Given a running timer started at 5 minutes that is then paused with leftover time, when a bad value is typed into the minutes field and Start is pressed to resume, then the timer resumes the leftover time, no `Using N` note surfaces for the field contents, and the field value is not applied to the running countdown.

**Scenario 8: Persistence unchanged.**
Given the fixed key `flambeee-apps-timer`, when the decimal, valid, and resume paths run and the page reloads, then only the last-used duration persists with the applied value, and no new field or key exists in storage.

**Scenario 9: CACHE ownership.**
Given the repo `website/sw.js`, when the merged diff is inspected, then the version line reads 18 to 19 and the `'./apps/timer.html'` precache line is byte-identical to base, with no other precache line changed.

**Scenario 10: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one app file plus the CACHE bump line, and every other app, game, schedule, noon, checker, and FPS path shows no diff.

**Scenario 11: Proof bar, desktop.**
Given a local serve, when the decimal cases are driven on desktop 1280x800 with real typed input and clicks, then all cases pass, layout holds with overflow 0, and zero page-attributable console errors are recorded.

**Scenario 12: Proof bar, mobile.**
Given a local serve, when the decimal cases are driven on mobile 375x667 with real typed input and clicks, then all cases pass, layout holds with overflow 0, and zero page-attributable console errors are recorded.

**Scenario 13: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a v0.43.0 cut on the table and red (or a slip) means no tag.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Decimal 7.5 surfaces the note, corrects the field to 7, clock runs 7:00 (Scenario 2).
**AC-3.** Integer-valid input starts silent with the field untouched (Scenario 3).
**AC-4.** 0 surfaces the note and corrects to 1 per 098 (Scenario 4).
**AC-5.** Empty surfaces the note and corrects to 1 per 098 (Scenario 5).
**AC-6.** 1000 surfaces the note and corrects to 999 per 098 (Scenario 6).
**AC-7.** Paused resume with bad input in the field applies nothing and notes nothing (Scenario 7).
**AC-8.** Persistence is the last-used duration under `flambeee-apps-timer` only; no new field or key (Scenario 8).
**AC-9.** `CACHE_VERSION` 18 to 19 with the timer precache line byte-identical (Scenario 9).
**AC-10.** Diff limited per the scope guard (Scenario 10).
**AC-11.** Desktop 1280x800 real-input run all passing with overflow 0 and zero page-attributable errors (Scenario 11).
**AC-12.** Mobile 375x667 real-input run all passing with overflow 0 and zero page-attributable errors (Scenario 12).
**AC-13.** RED on the current tree (exit 1, cases recorded) then GREEN on the merged tree (exit 0).
**AC-14.** Release-gate rule recorded: green keeps v0.43.0 on the table, slip means no tag (Scenario 13).
**AC-15.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Decimal script plus its RED run (exit 1 on the current tree, per-case measured values) and GREEN run (exit 0, all passing); local-serve command plus URL; both-viewport real-input runs with exit codes; overflow readings both viewports; console-error counts with page-attributable versus environmental split; the note text verbatim; storage readout showing the duration only under `flambeee-apps-timer`; the `CACHE_VERSION` readout before and after plus the unchanged timer precache line verbatim. Numbers, not adjectives.

## Non-Goals

- A second polish item, a redesign, a new app file, a new card, or a new precache entry.
- Any change to Day Pad, Tally, dice, coin, convert, any game, the site design, the schedule, the noon pipeline, or `pending-post.txt`.
- Changing any checker script (this story never touches `scripts/`).
- A new persisted field or key, or a write on any path except the existing save.
- Cutting a version (release wave owns the cut decision and the tag).
