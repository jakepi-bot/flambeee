# Story 072: Flambeee Apps first app (Session 33, P1, Dev)

**Status:** Ready for development (Session 33, 2026-10-17).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (dev; CEO override item 2, gate passed by Story 069).
**Assigned to:** **Riven** frontend owner. **Kai** consult on storage and prefix. **Scout** QA.
**Tracked by:** Session 33 plan, Story 072. Gate: Story 069 one-pager.
**Depends on:** Story 069 (division owner, scope, first-app default, boundary). Sibling to Story 071, not a child of it.

## Summary

Ship the first Flambeee Apps division app. Default: a minimal UTC-day countdown plus note pad (today's date in UTC, time to midnight UTC, one saveable line of text in localStorage). The dev wave may counter-propose exactly one equal-size alternative with a stated reuse test; larger pitches defer. This is the session ship per the Session 33 jakebot decision (session 20261017_011130_01bb1d): the FPS probe alone ships no playable thing, the Apps app is the ship.

## Source: Story 069

Story 069 (`docs/stories/069-apps-division-one-pager.md`) defines the division: parent owns planning, Ember steady-state product owner, scope is small useful web apps under house rules, out of scope is native, accounts/backends, push, paid, build steps, new servers. First-app default is the UTC-day countdown plus note pad above. Counter-proposal rule: one equal-size alternative allowed, larger pitches deferred. Reuse test: used daily or it does not ship. Size cap: no backend, no build. Division boundary: Apps does not rename, absorb, or re-theme the games; games work does not block on Apps.

## Requirements

### 1. Default first app

- One single-purpose page: today's date in UTC, live time remaining to midnight UTC, one saveable line of text in localStorage.
- Same house rules as the games: instantly usable in the browser, no downloads, no signups, no friction, single file, no dependencies, dark theme, plain punctuation, no em dashes, no heavy emoji.
- Includes new-surface overhead: new Apps directory, site card, stats-key prefix decision.

### 2. Counter-proposal rule

- Dev may counter-propose exactly one alternative of equal size with its reuse test stated.
- Larger pitches defer to a later session. No scope vote in this story.

### 3. Reuse test

- The app must be the kind of thing used daily, or it does not ship. The story records which reuse claim the shipped app makes.

### 4. Size cap and boundary

- No backend, no build step, no new server. localStorage only.
- Apps tree stays separate from Games. Games work does not block on Apps and Apps does not rename or re-theme the games (Story 069 boundary).

### 5. Stats prefix

- Fix the stats-key prefix before the first write. Story 069 recommends `flambeee-apps-*`; the dev wave confirms and records the chosen prefix.

### 6. CACHE_VERSION rule

- If a precached file is added (app page or asset in `PRECACHE_URLS`), bump `CACHE_VERSION` in `website/sw.js` on both sides, same as the games rule. If nothing precached is added, no bump.

## BDD scenarios

**Scenario 1: Default app shows the UTC day.**
Given the shipped app page, when it loads, then it shows today's date in UTC and the time remaining to midnight UTC, updating without reload.

**Scenario 2: One saveable line persists.**
Given the note pad line, when the user types one line and reloads, then the line is restored from localStorage; private mode and corrupt stored values degrade to the empty state with no exception.

**Scenario 3: Counter-proposal follows the rule.**
Given the dev wave prefers an alternative, when it is proposed, then it is exactly one alternative of equal size with a stated reuse test, or the default ships; anything larger defers.

**Scenario 4: Reuse test recorded.**
Given the shipped app, when this doc is reviewed, then it states the daily-reuse claim the app makes (used daily or it does not ship).

**Scenario 5: Size cap holds.**
Given the shipped diff, when inspected, then there is no backend, no build step, no new server, and no new dependency.

**Scenario 6: Division boundary holds.**
Given games work, when it plans, then no games story depends on Apps and no Apps change renames or re-themes the games; the Apps tree is separate from Games.

**Scenario 7: Prefix fixed before first write.**
Given the stats key, when the app first writes, then the `flambeee-apps-*` prefix (or the recorded confirmed alternative) is already decided and used.

**Scenario 8: Cache version correct.**
Given the service worker precache list, when a precached file was added, then `CACHE_VERSION` moved on both sides; when none was added, it did not.

## Acceptance Criteria

**AC-1.** Default app (or one equal-size counter-proposal with stated reuse test) ships as a single-purpose page (Scenarios 1, 2, 3).
**AC-2.** Reuse test recorded: used daily or it does not ship (Scenario 4).
**AC-3.** Size cap holds: no backend, no build, no new server (Scenario 5).
**AC-4.** Division boundary holds both ways (Scenario 6).
**AC-5.** Stats prefix fixed before first write (Scenario 7).
**AC-6.** CACHE_VERSION moved if and only if a precached file was added (Scenario 8).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Designing or building a second app.
- Accounts, backends, push, paid tiers, native wrappers.
- Site redesign or games changes.
- Staffing or schedule commitments.

## Open questions for dev wave

1. Default vs counter-proposal: accept the UTC countdown pad or name one equal-size alternative with its reuse test.
2. Stats-key prefix confirmation (`flambeee-apps-*` recommended; confirm before first write).
3. Site placement for the Apps card row (parent decides at build time).
