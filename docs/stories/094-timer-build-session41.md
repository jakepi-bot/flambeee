# Story 094: Countdown timer app build (Session 41, P1, User-visible)

**Status:** Ready for development (Session 41, 2026-10-25).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible; first Apps division build since Day Pad).
**Assigned to:** **Dev-wave code owner (Kai or Riven), named before the wave starts per the Story 048 protocol.** Ember is product owner. No shared ownership.
**Tracked by:** Session 41 plan, Story 094. Follows Story 069 (Apps one-pager), Story 072 (Day Pad build, shipped v0.31.0), and Story 092 (second-app one-pager, Session 40).
**Depends on:** Story 092 one-pager (planning gate satisfied; this story cites it verbatim where reused). No code dependency.

## Summary

Build the second Flambeee Apps app: one minimal single countdown timer as a static HTML file under `website/apps/`, plus one site card on the Apps surface, plus the `CACHE_VERSION` 10 to 11 bump that ships the fresh shell to returning visitors. This is the build Story 092 stubbed and authorized nothing for; the gate is now open and this story is the authorization. Proof bar is fixed below. A green proof bar is necessary for a v0.35.0 cut (release wave decides); if the app slips, no tag; no cut for a card alone.

## jakebot decision (advisory only, recorded)

Session 41 Wave 1 priorities per jakebot session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c: (1) P1, user-visible countdown timer build, real story citing 092, code owner named under Story 048 rule first. Proof bar for a v0.35.0 cut: serves locally, desktop 1280x800 plus mobile 375x667 with typed input and clicks, zero page-attributable console errors, site card present, CACHE_VERSION 10 to 11. If the app slips, no tag. No cut for a card alone.

**Citation:** `flambeee-team/session-plan.md`, Session 41 (2026-10-25), section "jakebot decision (advisory only, recorded)", session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c.

## What Story 092 already decided (verbatim citations)

Reused text is quoted verbatim from `docs/stories/092-second-app-onepager-session40.md` so this story cannot drift from the one-pager.

**Candidate (092, verbatim):**

> Exactly one candidate, proposed default: a minimal single countdown timer (one duration, start/pause/reset, one label line, persists only the last-used duration in localStorage).

**Size cap and counter-proposal rule (092, verbatim):**

> It earns its slot the same way Day Pad did: small enough to prove nothing new about the pipeline, useful enough to reopen. The build wave may counter-propose one alternative of equal size (one file, no backend, no build step, localStorage-only); larger pitches defer to a fresh one-pager.

**House rules (092, verbatim):**

> useful small web apps that are instantly usable in the browser, no downloads, no signups, no friction, single-purpose tools that solve one real problem.

**Non-goals (092, verbatim):**

> No native apps, no accounts or backends, no notifications or push, no paid tiers, no build step, no new server, no second candidate in this doc, no mechanic vote. No changes to Day Pad, no changes to any game, no site redesign. No schedule edits and no release implied.

**Build-story shape (092 stub, verbatim):**

> one static HTML file on the Apps surface, localStorage-only with fixed prefix, maxlength and key named in that story, site card plus CACHE_VERSION bump owned by that story, proof bar set by that story (local serve plus headed Chromium desktop 1280x800 and mobile 375x667, real input, zero page-attributable console errors)

This story names the key, the file, and the proof bar the stub deferred.

## Requirements

### 1. Owner named before the wave (Story 048)

The dev wave names one single code owner (Kai or Riven) before the wave starts. One owner holds `website/apps/timer.html`, the site-card edit, and the `sw.js` CACHE line together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. What gets built

- One static file: `website/apps/timer.html`. One duration, start/pause/reset, one label line. Persists only the last-used duration in localStorage (per the 092 candidate, verbatim above).
- Storage: localStorage-only under the fixed `flambeee-apps-` prefix. Exact key (for example `flambeee-apps-timer`) recorded in the dev record; no new persisted field beyond the last-used duration.
- One site card: timer entry on the Apps surface of `website/index.html`, following the Day Pad card pattern.
- One CACHE line: `CACHE_VERSION` 10 to 11 in `website/sw.js` (load-bearing: the Apps pages are precached, so without the bump a returning visitor is served the pre-timer shell from cache and the release reads as a no-op).

### 3. Scope guard

In scope: `website/apps/` (the new file), the one site card on `website/index.html`, the one `CACHE_VERSION` line in `website/sw.js`. Untouched: the Day Pad file (`website/apps/index.html`), every game (`src/`, `games/`, `GAME_ORDER`), the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe. No native apps, no accounts or backends, no notifications or push, no paid tiers, no build step, no new server (092 non-goals, restated as the guard).

### 4. Proof bar (release gate)

All five, or the app does not ship:

1. Serves locally (plain static serve, no build step).
2. Desktop 1280x800 plus mobile 375x667, real typed input and clicks (duration entry, start, pause, reset), both viewports.
3. Zero page-attributable console errors (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
4. Site card present on the Apps surface and linking to the timer page.
5. `CACHE_VERSION` reads 11 on the merged tree (was 10 at planning).

Release implication, fixed: a green proof bar is necessary but not sufficient for a v0.35.0 cut; the release wave decides the cut. If the app slips, no tag. No cut for a card alone.

### 5. Copy rules

Plain punctuation, no em dashes, no heavy emoji, in the page and the card, per the CEO tone rule.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then one named code owner holds the timer file plus the card plus the CACHE line, and the dev record states the name.

**Scenario 2: Candidate fidelity.**
Given the 092 one-pager, when the built page is compared against it, then it is the verbatim candidate (one duration, start/pause/reset, one label line, last-used duration persisted) with no second feature.

**Scenario 3: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are `website/apps/timer.html` plus the one card plus the one CACHE line, and Day Pad, games, schedule, noon, and checker paths show no diff.

**Scenario 4: Proof bar, desktop.**
Given a local serve, when the timer is driven on desktop 1280x800 with real typed input and clicks, then start/pause/reset behave, the label renders, and zero page-attributable console errors are recorded.

**Scenario 5: Proof bar, mobile.**
Given a local serve, when the timer is driven on mobile 375x667 with real typed input and clicks, then start/pause/reset behave, layout holds with no overflow, and zero page-attributable console errors are recorded.

**Scenario 6: Cache bump.**
Given the precached Apps shell, when the merged tree is read, then `CACHE_VERSION` is 11 and the timer page is reachable from cache on a returning visit.

**Scenario 7: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps v0.35.0 on the table and red (or a slip) means no tag, with no cut for a card alone.

**Scenario 8: jakebot citation check.**
Given the Wave 1 set decision, when this doc is reviewed, then it records the P1 priority, the proof bar, the no-tag-on-slip rule, and the citation session local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c.

## Acceptance Criteria

**AC-1.** Single code owner named before the wave per Story 048 (Scenario 1).
**AC-2.** Built page matches the verbatim 092 candidate, localStorage-only under `flambeee-apps-`, key recorded (Scenario 2).
**AC-3.** Diff limited to the timer file plus one card plus one CACHE line (Scenario 3).
**AC-4.** Desktop 1280x800 real-input run green with zero page-attributable errors (Scenario 4).
**AC-5.** Mobile 375x667 real-input run green with zero page-attributable errors (Scenario 5).
**AC-6.** `CACHE_VERSION` 11 on the merged tree (Scenario 6).
**AC-7.** Release-gate rule recorded: green keeps v0.35.0 on the table, slip means no tag (Scenario 7).
**AC-8.** jakebot priority and citation recorded as above (Scenario 8).
**AC-9.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Local-serve command plus URL, both-viewport real-input runs with exit codes, console-error counts with page-attributable versus environmental split, site-card link target, and the `CACHE_VERSION` line before and after. Numbers, not adjectives.

## Non-Goals

- Any change to Day Pad, any game, the site design beyond the one card, the schedule, the noon pipeline, or `pending-post.txt`.
- A second candidate, a shortlist, or a candidate vote (092 closed that; the one equal-size counter-proposal is the only allowed substitute).
- Changing any checker script.
- Cutting v0.35.0 (release wave owns the cut decision and the tag).

## Open questions for the dev wave

1. Candidate confirmation: single countdown timer, or the one equal-size counter-proposal (name it in the dev record, not in a new one-pager).
2. Code owner name under Story 048 (recorded before the wave starts).
3. Exact localStorage key under the `flambeee-apps-` prefix (recorded in the dev record).
