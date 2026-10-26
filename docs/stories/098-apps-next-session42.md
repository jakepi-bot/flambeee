# Story 098: Third Flambeee Apps app or timer follow-up polish (Session 42, P2, User-visible candidate)

**Status:** Ready for development (Session 42, 2026-10-26).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (user-visible candidate; next Apps division step after the v0.35.0 timer).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the app file plus the card plus the CACHE line together). Ember is product owner. No shared ownership.
**Tracked by:** Session 42 plan, Story 098. Follows Story 069 (Apps one-pager), Story 072 (Day Pad, shipped v0.31.0), Story 092 (second-app one-pager, Session 40), Story 094 (timer build, shipped v0.35.0).
**Depends on:** Story 092 one-pager gate (satisfied) and the shipped timer at `website/apps/timer.html`. No code dependency on the FPS stories.

## Summary

Ship exactly one Apps division item this session: either the third-app pick (one new single-purpose app under the equal-size counter-proposal rule) or one timer follow-up polish item. One implementable story, one file surface, one proof bar. The dev wave picks exactly one of the two tracks before the wave starts and records the pick; the other track waits for a later session. If the picked track slips, no tag follows it down; the release wave decides any cut.

## jakebot decision (advisory only, recorded)

Session 42 Wave 1 priorities per jakebot (session local-ed66cc3b157bcdcdbd66f8c796fc4, proceeded on its read): P2 is the next Apps division item, third-app pick or timer follow-up polish, doc-light, one implementable story.

**Citation:** `flambeee-team/session-plan.md`, Session 42 (2026-10-26), section "Priorities (in order)".

## What Story 092 already decided (verbatim citations)

Reused text is quoted verbatim from `docs/stories/092-second-app-onepager-session40.md` so this story cannot drift from the one-pager.

**Size cap and counter-proposal rule (092, verbatim):**

> It earns its slot the same way Day Pad did: small enough to prove nothing new about the pipeline, useful enough to reopen. The build wave may counter-propose one alternative of equal size (one file, no backend, no build step, localStorage-only); larger pitches defer to a fresh one-pager.

**House rules (092, verbatim):**

> useful small web apps that are instantly usable in the browser, no downloads, no signups, no friction, single-purpose tools that solve one real problem.

**Non-goals (092, verbatim):**

> No native apps, no accounts or backends, no notifications or push, no paid tiers, no build step, no new server, no second candidate in this doc, no mechanic vote. No changes to Day Pad, no changes to any game, no site redesign. No schedule edits and no release implied.

## Flambeee Apps house rules (restated so this story stands alone)

Single file under `website/apps/`. No native apps, no accounts or backends, no notifications or push, no paid tiers, no build steps, no new server. localStorage-only persistence under the fixed `flambeee-apps-` prefix. Plain punctuation, no em dashes, no heavy emoji, in page and card, per the CEO tone rule.

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the app file, the site-card edit, and the `sw.js` CACHE line together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. Exactly one track, picked before the wave

- **Track A, third-app pick:** one new single-purpose app as one static file under `website/apps/` (for example a minimal stopwatch, a plain counter, or one equal-size alternative named in the dev record). One duration-style input surface at most, one label line at most, persists only its own last-used state under a new `flambeee-apps-` key recorded in the dev record. Plus one site card on the Apps surface following the Day Pad and timer card pattern, plus the one `CACHE_VERSION` line (11 to 12) in `website/sw.js`.
- **Track B, timer follow-up polish:** exactly one polish item on the shipped timer (`website/apps/timer.html`), named in the dev record before the wave (for example one input-validation message, one preset-duration row, or one audible end-of-countdown toggle; dev names the one). No second item, no redesign. CACHE line only if a precached file changes (per the v0.33.0 comment rule: any change to an already-precached file needs a CACHE bump).
- The dev record states the picked track and names the deferred track. Both tracks in one session is out of scope.

### 3. Scope guard

In scope: `website/apps/` (the one new or polished file), the at-most-one site card on `website/index.html` (Track A only; Track B touches no card unless the polish adds visitor-visible surface, recorded), the at-most-one `CACHE_VERSION` line in `website/sw.js`. Untouched: Day Pad (`website/apps/index.html`) except under Track B if the polish is shared-surface (recorded), every game (`src/`, `games/`, `GAME_ORDER`), the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe. House rules above restated as the guard.

### 4. Proof bar (release gate)

All five, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. Desktop 1280x800 plus mobile 375x667, real typed input and clicks, both viewports.
3. Zero page-attributable console errors (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
4. Site card present on the Apps surface and linking to the app page (Track A; Track B: existing timer card still correct).
5. `CACHE_VERSION` reads 12 on the merged tree if a precached file changed (was 11 at planning), else reads 11 with the no-bump reason recorded.

Release implication, fixed: a green proof bar is necessary but not sufficient for any version cut; the release wave decides the cut. If the item slips, no tag. No cut for a card alone.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the app file plus the card plus the CACHE line as single owner, and the dev record states the name.

**Scenario 2: One track picked.**
Given the two tracks, when the dev wave starts, then the dev record names exactly one picked track with its item, names the deferred track, and no work lands on the deferred track.

**Scenario 3: Candidate fidelity (Track A).**
Given the 092 one-pager, when the built page is compared against it, then it is one single-purpose app (one file, no backend, no build step, localStorage-only under `flambeee-apps-`) with no second feature.

**Scenario 4: Polish singularity (Track B).**
Given the shipped timer, when the polished page is compared against the v0.35.0 timer, then exactly the one named polish item changed and nothing else did.

**Scenario 5: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one app file plus at most one card plus at most one CACHE line, and games, schedule, noon, and checker paths show no diff.

**Scenario 6: Proof bar, desktop.**
Given a local serve, when the app is driven on desktop 1280x800 with real typed input and clicks, then it behaves, the label renders, layout holds, and zero page-attributable console errors are recorded.

**Scenario 7: Proof bar, mobile.**
Given a local serve, when the app is driven on mobile 375x667 with real typed input and clicks, then it behaves, layout holds with no overflow, and zero page-attributable console errors are recorded.

**Scenario 8: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a cut on the table and red (or a slip) means no tag, with no cut for a card alone.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Exactly one track picked and recorded, the other deferred (Scenario 2).
**AC-3.** Track A: built page matches the equal-size rule, localStorage-only under `flambeee-apps-`, key recorded (Scenario 3). Track B: exactly the one named polish item, nothing else (Scenario 4).
**AC-4.** Diff limited per the scope guard (Scenario 5).
**AC-5.** Desktop 1280x800 real-input run green with zero page-attributable errors (Scenario 6).
**AC-6.** Mobile 375x667 real-input run green with zero page-attributable errors (Scenario 7).
**AC-7.** `CACHE_VERSION` 12 if a precached file changed, else 11 with the reason recorded.
**AC-8.** Release-gate rule recorded: green keeps a cut on the table, slip means no tag (Scenario 8).
**AC-9.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Track pick plus deferred track named; local-serve command plus URL; both-viewport real-input runs with exit codes; console-error counts with page-attributable versus environmental split; site-card link target (Track A); the `CACHE_VERSION` line before and after with the bump-or-no-bump reason. Numbers, not adjectives.

## Non-Goals

- Both tracks in one session.
- A second candidate, a shortlist, or a candidate vote (092 closed that; the one equal-size alternative is the only allowed substitute under Track A).
- Any change to any game, the site design beyond the at-most-one card, the schedule, the noon pipeline, or `pending-post.txt`.
- Changing any checker script.
- Cutting a version (release wave owns the cut decision and the tag).

## Open questions for the dev wave

1. Track pick: third-app pick (name the app) or timer polish (name the one item).
2. Exact localStorage key under the `flambeee-apps-` prefix (recorded in the dev record).
3. CACHE bump or no-bump with the reason tied to the precache rule.
