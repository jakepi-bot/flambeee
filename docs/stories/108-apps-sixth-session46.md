# Story 108: Sixth Flambeee Apps app, Track A (Session 46, P1, User-visible candidate)

**Status:** Ready for development (Session 46, 2026-10-30).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible candidate; v0.39.0 vehicle per jakebot, gated on green).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the app file plus the site card plus the CACHE bump plus its own precache entry together). Ember is product owner. No shared ownership.
**Tracked by:** Session 46 plan, Story 108. Follows Story 069 (Apps one-pager), Story 072 (Day Pad, shipped v0.31.0), Story 092 (second-app one-pager, Session 40), Story 094 (timer build, shipped v0.35.0), Story 098 (Track B timer polish shipped v0.36.0), Story 101 (Tally, shipped v0.36.1), Story 103 (Dice, shipped v0.37.0), Story 106 (Coin Flip, shipped v0.38.0).
**Depends on:** Story 092 one-pager gate (satisfied) and the shipped Coin Flip at `website/apps/coin.html`. No code dependency on Story 109 (docs-only decision record, no diff).

## Summary

Ship the sixth Apps app on the Track A pipeline Coin Flip proved: exactly one new single-purpose static app under `website/apps/`, plus one site card, plus CACHE_VERSION 14 to 15 plus its own single `sw.js` precache entry. Single owner holds all four surfaces together, so no P1 split this session and no conflict by construction. v0.39.0 candidate; the release wave decides the cut. This is the last free one per jakebot: a seventh app needs a demand reason, not a cadence reason.

## jakebot decision (advisory only, recorded)

Session 46 Wave 1 priorities per jakebot (session local-2ffe00df485cab745a80f806f53302872f3f936738fdb6dd20264b0c99fe09bf, proceeded on its read): point 1, sixth app becomes P1 as the v0.39.0 vehicle with one condition, the pick must name a real use case, not the smallest thing that fits the template. Suggested strongest sixth: unit converter (pairs with timer/dice as daily utility, one file, one input). Choice is the dev's per the 092 equal-size rule. This is the last free one.

**Citation:** `flambeee-team/session-plan.md`, Session 46 (2026-10-30), section "jakebot decisions (advisory only, recorded)".

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

## Baseline measured at Session 46 planning (2026-10-30 01:10 CDT)

| Check | Value |
|---|---|
| Website What's New heading | v0.38.0 (matches tag v0.38.0) |
| Latest tag / release | v0.38.0 Coin Flip joins the Apps shelf (2026-10-29 07:58 UTC) |
| Open issues / open PRs | 0 / 0 |
| App cards | 5 (`apps/index.html`, `apps/timer.html`, `apps/tally.html`, `apps/dice.html`, `apps/coin.html`) |
| `sw.js` `CACHE_VERSION`, repo mirror | 14 (measured at planning; run must read the line, not assume it) |
| App files in PRECACHE_URLS | all five app files present |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the app file, the site-card edit, the `CACHE_VERSION` bump line, and its own `sw.js` precache entry together, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team. No P1 split this session: Story 109 (Kai) is docs-only and touches no `website/` path, so there is no sw.js conflict by construction.

### 2. Track A pick (exactly one app, value gate applies)

- One new single-purpose app as one static file under `website/apps/` (suggested default: plain unit converter, one input with unit select and converted output; or one equal-size alternative named in the dev record under the 092 counter-proposal rule above). Timer, Tally, Dice, and Coin Flip patterns are the size reference.
- Value gate: the dev record names the real use case the pick serves (who uses it, for what, in one line). Template-filler means no cut. Five apps in five sessions with 0 open issues means the shelf has no demand signal; "it fits the pipeline" is not a reason.
- One input surface at most, one label line at most, persists only its own last-used state under a new `flambeee-apps-` key recorded in the dev record.
- Plus one site card on `website/index.html` following the Day Pad, timer, Tally, Dice, and Coin Flip card pattern.
- The dev record names the picked app and its localStorage key before the wave. No second app, no shortlist, no vote.
- Fallback if no sixth pick clears the value gate: Track B polish on the weakest of the five existing apps (user-visible, one file, does not grow the shelf). The fallback is recorded in the dev record, not silently substituted.

### 3. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (14 to 15) and its own single precache entry (one line for the new app file), appended after the coin line.
- Per the v0.33.0 comment rule, any change to shell surface needs the bump, and the new app file is a shell asset, so the bump ships with this story.
- The dev record states the entry line verbatim plus the version readout before and after.

### 4. Scope guard

In scope: the one new file under `website/apps/`, the at-most-one site card on `website/index.html`, the one `CACHE_VERSION` bump line, the at-most-one `sw.js` precache entry line owned by this story. Untouched, no diff: Day Pad (`website/apps/index.html`), the timer (`website/apps/timer.html`), Tally (`website/apps/tally.html`), Dice (`website/apps/dice.html`), Coin Flip (`website/apps/coin.html`), every game (`src/`, `games/`, `GAME_ORDER`), the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts (`scripts/`), the FPS probe (`dev/fps-probe/`).

### 5. Proof bar (release gate)

All five, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. Desktop 1280x800 plus mobile 375x667, real typed input and clicks, both viewports.
3. Zero page-attributable console errors (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
4. Site card present on the Apps surface and linking to the new app page.
5. `CACHE_VERSION` reads 15 on the merged tree; the new app's precache line is present in `PRECACHE_URLS`.

Release implication, fixed: green keeps a cut on the table, slip means no tag. The release wave decides the cut. No user-visible delta means no cut. No cut for a card alone.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the app file plus the card plus the CACHE bump plus its own precache entry as single owner, and the dev record states the name.

**Scenario 2: Equal-size pick with a real use case.**
Given the 092 one-pager, when the built page is compared against it, then it is one single-purpose app (one file, no backend, no build step, localStorage-only under `flambeee-apps-`) with no second feature, and the dev record names its real use case in one line.

**Scenario 3: CACHE ownership.**
Given the repo `website/sw.js`, when the merged diff is inspected, then the version line reads 14 to 15 and exactly one new precache line for the new app file is appended after the coin line, and no other precache line changed.

**Scenario 4: Scope guard.**
Given the scope guard, when the diff is inspected, then changed files are at most the one app file plus at most one card plus the CACHE bump plus at most one precache entry line, and Day Pad, timer, Tally, Dice, Coin Flip, games, schedule, noon, checker, and probe paths show no diff.

**Scenario 5: Proof bar, desktop.**
Given a local serve, when the app is driven on desktop 1280x800 with real typed input and clicks, then it behaves, the label renders, layout holds, and zero page-attributable console errors are recorded.

**Scenario 6: Proof bar, mobile.**
Given a local serve, when the app is driven on mobile 375x667 with real typed input and clicks, then it behaves, layout holds with no overflow, and zero page-attributable console errors are recorded.

**Scenario 7: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a cut on the table and red (or a slip) means no tag, with no cut for a card alone and no cut when there is no user-visible delta.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Built page matches the equal-size rule, localStorage-only under `flambeee-apps-`, key recorded; no second feature (Scenario 2).
**AC-3.** Value gate met: dev record names the real use case in one line; template-filler means no cut (Scenario 2).
**AC-4.** CACHE ownership held: version line 14 to 15 plus exactly one new precache entry line, no other precache line changed (Scenario 3).
**AC-5.** Diff limited per the scope guard; Day Pad, timer, Tally, Dice, Coin Flip, games, schedule, noon, checker, and probe paths show no diff (Scenario 4).
**AC-6.** Desktop 1280x800 real-input run green with zero page-attributable errors (Scenario 5).
**AC-7.** Mobile 375x667 real-input run green with zero page-attributable errors (Scenario 6).
**AC-8.** `CACHE_VERSION` reads 15 on the merged tree with the new app's precache line present.
**AC-9.** Release-gate rule recorded: green keeps a cut on the table, slip means no tag (Scenario 7).
**AC-10.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

App name plus localStorage key plus one-line real use case; local-serve command plus URL; both-viewport real-input runs with exit codes; console-error counts with page-attributable versus environmental split; site-card link target; the new precache entry line verbatim plus the `CACHE_VERSION` readout before and after. Numbers, not adjectives.

## Non-Goals

- A second candidate, a shortlist, or a candidate vote (092 closed that; the one equal-size alternative is the only allowed substitute).
- Any change to Day Pad, the timer, Tally, Dice, Coin Flip, any game, the site design beyond the at-most-one card, the schedule, the noon pipeline, or `pending-post.txt`.
- Changing any checker script.
- Cutting a version (release wave owns the cut decision and the tag).
