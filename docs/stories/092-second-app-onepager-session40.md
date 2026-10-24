# Story 092: Second Flambeee Apps app one-pager (Session 40, P2, Planning)

**Status:** Ready for review (Session 40, 2026-10-24). **Planning doc. No code.**
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (planning; second Apps division step, gate to a later build story).
**Assigned to:** **Quinn-carried doc** (Riven may support wording). No dev code owner, no QA owner. Doc only.
**Tracked by:** Session 40 plan, Story 092. Follows Story 069 (Apps one-pager) and Story 072 (first app Day Pad, shipped v0.31.0, polished v0.34.0).
**Depends on:** None. Sibling to Story 091, not a child of it. No code dependency.

## Summary

Define the second Flambeee Apps app before any dev wave touches it. Day Pad proved the division pipeline (plan, build, QA, release, site card); this one-pager names the division owner, repeats the scope boundary, proposes exactly one second-app candidate, states non-goals, and stubs the build story a later session will execute. Doc only: no code, no site card, no new directory, no schedule edit, no release change.

## jakebot decision (advisory only, recorded)

Session 40 Wave 1 priorities per jakebot session local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4: (b) SECOND, second Apps app one-pager only. One-pager plus build story stub, no code started that cannot be verified in-session.

**Citation:** `flambeee-team/session-plan.md`, Session 40 (2026-10-24), section "jakebot decision (advisory only, recorded)", session local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4.

## Division state (why a second app, why now)

Story 069 gated the division on a one-pager; Story 072 named Day Pad as the first app. Day Pad shipped in v0.31.0 (UTC date plus live countdown plus one saveable line, maxlength 280, prefix `flambeee-apps-`), gained its N/280 count in v0.32.0, and its Saved-clear-on-input polish in v0.34.0. The pipeline is proven end to end. A second app is the next division step per the Session 40 plan, and it enters through the same gate: one-pager first, build story later, no code this session.

## The one-pager

**Owner.** Flambeee Apps day-to-day product ownership sits with Ember; technical ownership assigns per story under the Story 048 protocol before any build wave starts. This doc is Quinn-carried planning only and names no code owner. No shared ownership with the jobs pipeline or any outside team.

**Scope.** Same house rules as Story 069, restated so this page stands alone: useful small web apps that are instantly usable in the browser, no downloads, no signups, no friction, single-purpose tools that solve one real problem. Apps live under the Flambeee brand and site, ship under the same SDLC (branch, PR, peer review, QA, compliance), and follow the same copy rules (plain punctuation, no em dashes, no heavy emoji). In scope: one static HTML file under the Apps surface, localStorage-only persistence with a fixed key prefix, reuse-shaped utilities a visitor opens more than once.

**Second-app candidate.** Exactly one candidate, proposed default: a minimal single countdown timer (one duration, start/pause/reset, one label line, persists only the last-used duration in localStorage). It earns its slot the same way Day Pad did: small enough to prove nothing new about the pipeline, useful enough to reopen. The build wave may counter-propose one alternative of equal size (one file, no backend, no build step, localStorage-only); larger pitches defer to a fresh one-pager.

**Non-goals.** No native apps, no accounts or backends, no notifications or push, no paid tiers, no build step, no new server, no second candidate in this doc, no mechanic vote. No changes to Day Pad, no changes to any game, no site redesign. No schedule edits and no release implied.

**Division boundary.** Flambeee Games stays as is: six shipped games plus Day Pad under Apps, small web games continue, directive 6 governs game originality. Apps work does not rename, absorb, or re-theme the games, and games work does not block on Apps.

## Build-story stub (for a later session, not this one)

Title placeholder: second Apps app build (candidate: single countdown timer). Owner: to be named under the Story 048 protocol before that dev wave starts. Shape, pre-declared: one static HTML file on the Apps surface, localStorage-only with fixed prefix, maxlength and key named in that story, site card plus CACHE_VERSION bump owned by that story, proof bar set by that story (local serve plus headed Chromium desktop 1280x800 and mobile 375x667, real input, zero page-attributable console errors). The stub authorizes nothing; the later session writes the real story, cites this one-pager, and may take the one equal-size counter-proposal instead.

## Requirements

### 1. Owner named

- Division product owner (Ember) plus planning carrier (Quinn) stated, with the code-owner rule (Story 048, named before the build wave) recorded.
- No unowned surface: the stub states its owner is named later, not now.

### 2. Scope bounded

- In-scope list and explicit non-goals list both stated in the doc, so a future pitch is accepted or rejected without debate.

### 3. Second-app candidate fixed

- Exactly one candidate named with its reuse test (reopened weekly or it does not ship) and its size cap (one file, no backend, no build).
- Counter-proposal rule stated: one equal-size alternative allowed, larger pitches deferred to a fresh one-pager.

### 4. Build-story stub present

- Stub names the later story shape (file surface, storage rule, proof bar, owner rule) without authorizing any build now.

### 5. Planning only

- No code, no site card, no new directory, no CACHE_VERSION touch, no release change, no schedule edit this session.

## BDD scenarios (one-pager completeness checks)

**Scenario 1: Owner check.**
Given the CEO requires an Apps division, when this doc is read, then it names the product owner and the planning carrier, states the code-owner rule for the later build story, and leaves no shared or unowned surface.

**Scenario 2: Scope check.**
Given a future second-app pitch, when checked against this doc, then in-scope items (one static file, localStorage-only, same SDLC and copy rules) pass and non-goal items (native, accounts, push, paid, build steps, new servers) are rejected without debate.

**Scenario 3: Candidate check.**
Given the division needs a second app, when this doc is read, then it names exactly one candidate (single countdown timer) with its reuse test and size cap, and states the one-equal-size counter-proposal rule.

**Scenario 4: Non-goals check.**
Given scope pressure, when this doc is reviewed, then Day Pad, the six games, the site design, the schedule, and any release are all explicitly untouched.

**Scenario 5: Stub check.**
Given a later session plans the build, when it reads the stub, then it finds the story shape (surface, storage rule, proof bar, owner rule) and the citation back to this one-pager, with no build authorized early.

**Scenario 6: Doc-only check.**
Given this story's diff, when it is inspected, then it contains only this Markdown file, with no code, no site card, no directory, no CACHE_VERSION touch, and no schedule or release edit.

**Scenario 7: jakebot citation check.**
Given the Wave 1-2 set decision, when this doc is reviewed, then it records the priority ((b) SECOND, one-pager plus stub, no code) and the citation session local-f5f07529d486a052abbccb1b354841a31c3b0c82a236126d42aa84edf088fbe4.

## Acceptance Criteria

**AC-1.** Owner named with product owner, planning carrier, and code-owner rule (Scenario 1).
**AC-2.** Scope bounded with in-scope list and explicit non-goals (Scenarios 2, 4).
**AC-3.** Exactly one second-app candidate with reuse test, size cap, and counter-proposal rule (Scenario 3).
**AC-4.** Build-story stub present with later-session shape and no early authorization (Scenario 5).
**AC-5.** Planning only: this Markdown file alone, nothing else (Scenario 6).
**AC-6.** jakebot priority and citation recorded as above (Scenario 7).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Any code, prototype, site card, directory, or CACHE_VERSION touch.
- A second candidate, a shortlist, or a candidate vote.
- Any change to Day Pad, any game, the site design, the schedule, or any release.
- Naming the build-story code owner now (that happens before the build wave, per Story 048).

## Open questions for a later session

1. Candidate confirmation: single countdown timer, or the one equal-size counter-proposal (name it then, not now).
2. Build-story code owner under Story 048 (named before that dev wave).
3. Reuse test detail for the chosen candidate (what "reopened" means in numbers).
