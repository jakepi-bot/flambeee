# Story 101: Third Flambeee Apps app, Track A (Session 43, P2, User-visible candidate)

**Status:** Ready for development (Session 43, 2026-10-27).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (user-visible candidate; next Apps division step after the v0.36.0 timer polish).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the app file plus the site card plus its own CACHE entry together). Ember is product owner. No shared ownership.
**Tracked by:** Session 43 plan, Story 101. Follows Story 069 (Apps one-pager), Story 072 (Day Pad, shipped v0.31.0), Story 092 (second-app one-pager, Session 40), Story 094 (timer build, shipped v0.35.0), Story 098 (Track B timer polish shipped v0.36.0; Track A deferred here).
**Depends on:** Story 092 one-pager gate (satisfied) and the shipped timer at `website/apps/timer.html`. No code dependency on the FPS stories or on Story 100.

## Summary

Ship the Track A third-app pick deferred from Story 098: exactly one new single-purpose static app under `website/apps/`, plus one site card, plus its own single `sw.js` precache entry. Track B is closed this session (timer polish shipped v0.36.0). One implementable story, one file surface, one proof bar. If the pick slips, no tag follows it down; the release wave decides any cut.

## jakebot decision (advisory only, recorded)

Session 43 Wave 1 priorities per jakebot (session local-73eab48a611ea40ed30626c7f362c9b89726a8066f4c59c571213edeade85142, proceeded on its read): P2 confirmed as the third-app pick, Track A deferred from Story 098, Riven single owner per Story 048.

**Citation:** `flambeee-team/session-plan.md`, Session 43 (2026-10-27), section "jakebot decisions (advisory only, recorded)".

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

Riven is the single code owner, holding the app file, the site-card edit, and its own `sw.js` CACHE entry together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. Track A pick (exactly one app)

- One new single-purpose app as one static file under `website/apps/` (for example a minimal stopwatch, a plain counter, or one equal-size alternative named in the dev record under the 092 counter-proposal rule above).
- One input surface at most, one label line at most, persists only its own last-used state under a new `flambeee-apps-` key recorded in the dev record.
- Plus one site card on the Apps surface following the Day Pad and timer card pattern.
- The dev record names the picked app and its localStorage key before the wave. No second app, no shortlist, no vote. Track B (timer polish) is closed; no work lands on the timer file.

### 3. CACHE-line boundary with Story 100 (drawn explicitly so both sw.js edits land without conflict)

- **Story 100 (P1, Kai) owns:** the `CACHE_VERSION` bump line (11 to 12) and the `'./apps/timer.html'` precache entry. It lands first.
- **This story (P2, Riven) owns:** only its own single precache entry (one line for the new app file), appended after P1's timer line, rebased onto P1's change. P2 touches no version line and no other precache line.
- If the new app file is precached, the entry above is required (per the v0.33.0 comment rule: any change to shell surface needs the bump, and P1's bump already covers it). The dev record states the entry line verbatim.
- Ordering rule: the dev wave lands P1 first, P2 rebases onto it; if P1 slips, P2 still lands its app file plus card, and its precache entry rides the next version bump with the reason recorded.

### 4. Scope guard

In scope: the one new file under `website/apps/`, the at-most-one site card on `website/index.html`, the at-most-one `sw.js` precache entry line owned by this story. Untouched: Day Pad (`website/apps/index.html`), the timer (`website/apps/timer.html`), every game (`src/`, `games/`, `GAME_ORDER`), the `CACHE_VERSION` line (Story 100 owns it), the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe.

### 5. Proof bar (release gate)

All five, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. Desktop 1280x800 plus mobile 375x667, real typed input and clicks, both viewports.
3. Zero page-attributable console errors (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
4. Site card present on the Apps surface and linking to the new app page.
5. `CACHE_VERSION` reads 12 on the merged tree (P1's bump, verified not assumed); the new app's precache line is present in `PRECACHE_URLS`.

Release implication, fixed: a green proof bar is necessary but not sufficient for any version cut; the release wave decides the cut. If the item slips, no tag. No cut for a card alone.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the app file plus the card plus its own CACHE entry as single owner, and the dev record states the name.

**Scenario 2: Equal-size pick.**
Given the 092 one-pager, when the built page is compared against it, then it is one single-purpose app (one file, no backend, no build step, localStorage-only under `flambeee-apps-`) with no second feature.

**Scenario 3: CACHE boundary.**
Given Stories 100 and 101, when both sw.js edits land, then P1 owns the version line plus the timer entry, P2 owns only its own single entry appended after the timer line, and no other precache line changed.

**Scenario 4: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one app file plus at most one card plus at most one CACHE entry line, and games, schedule, noon, checker, and timer paths show no diff.

**Scenario 5: Proof bar, desktop.**
Given a local serve, when the app is driven on desktop 1280x800 with real typed input and clicks, then it behaves, the label renders, layout holds, and zero page-attributable console errors are recorded.

**Scenario 6: Proof bar, mobile.**
Given a local serve, when the app is driven on mobile 375x667 with real typed input and clicks, then it behaves, layout holds with no overflow, and zero page-attributable console errors are recorded.

**Scenario 7: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a cut on the table and red (or a slip) means no tag, with no cut for a card alone.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Built page matches the equal-size rule, localStorage-only under `flambeee-apps-`, key recorded; no second feature (Scenario 2).
**AC-3.** CACHE boundary held: P2 diff on sw.js is at most its own single entry line, version line untouched (Scenario 3).
**AC-4.** Diff limited per the scope guard; timer, Day Pad, games, schedule, noon, and checker paths show no diff (Scenario 4).
**AC-5.** Desktop 1280x800 real-input run green with zero page-attributable errors (Scenario 5).
**AC-6.** Mobile 375x667 real-input run green with zero page-attributable errors (Scenario 6).
**AC-7.** `CACHE_VERSION` reads 12 on the merged tree with the new app's precache line present.
**AC-8.** Release-gate rule recorded: green keeps a cut on the table, slip means no tag (Scenario 7).
**AC-9.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

App name plus localStorage key; local-serve command plus URL; both-viewport real-input runs with exit codes; console-error counts with page-attributable versus environmental split; site-card link target; the new precache entry line verbatim plus the `CACHE_VERSION` readout. Numbers, not adjectives.

## Non-Goals

- A second candidate, a shortlist, or a candidate vote (092 closed that; the one equal-size alternative is the only allowed substitute).
- Any change to Day Pad, the timer, any game, the site design beyond the at-most-one card, the `CACHE_VERSION` line, the schedule, the noon pipeline, or `pending-post.txt`.
- Changing any checker script.
- Cutting a version (release wave owns the cut decision and the tag).
