# Story 069: Flambeee Apps division one-pager (Session 32, P1, Planning)

**Status:** Ready for review (Session 32, 2026-10-16). **Planning doc. No code.**
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (planning; CEO override item 2, gate to first dev wave).
**Assigned to:** **Parent-owned doc.** Ember consults on scope wording if needed. No code assignment.
**Tracked by:** Session 32 plan, Story 069. References `flambeee-team/CEO-DIRECTIVES.md` section 7, `docs/roadmap.md` Now section.
**Depends on:** None. Sibling to Story 068, not a child of it.

## Summary

Define Flambeee Apps as a second division alongside Flambeee Games before any dev wave touches it. This one-pager names the owner, the scope, and the first app, and states what Apps will not do. It is the gate the roadmap requires: no Apps dev wave without this page on main.

## Directive this story serves

Quoted from `CEO-DIRECTIVES.md` section 7 (CEO override 2026-10-15, convo 3mwvyou25ec2p, message 3mxvvvuomct2n):

> Let's also start branching out a bit, instead of just web games how about we make useful web apps? You can do both of these at the same time, maybe have the apps be a separate division within flambeee such as "Flambeee apps" vs "flambeee games"

Decision recorded in section 7, ACCEPTED: Flambeee Apps as a second division alongside Flambeee Games. Gate to the first dev wave is a one-pager (owner, scope, first app).

## The one-pager

**Owner.** Flambeee Apps is owned by the parent (CEO delegate for Session 32 planning) until the division ships its first app. Day-to-day product ownership sits with Ember once the division is staffed; technical ownership assigns per story under the Story 048 protocol. No shared ownership with the jobs pipeline or any outside team.

**Scope.** Useful small web apps under the same house rules as the games: instantly playable in the browser, no downloads, no signups, no friction, single-purpose tools that solve one real problem. Apps live under the Flambeee brand and site, ship under the same SDLC (branch, PR, peer review, QA, compliance), and follow the same copy rules (plain punctuation, no em dashes, no heavy emoji). Out of scope: native apps, accounts and backends, notifications and push, paid tiers, and anything that needs a build step or a server the team does not already run.

**First app.** A single-purpose daily utility that earns its slot by reuse, proposed default: a minimal UTC-day countdown and note pad (today's date in UTC, time to midnight UTC, one saveable line of text in localStorage). Small enough to prove the division's pipeline (plan, build, QA, release, site card) without inventing a backend. The dev wave may counter-propose one alternative of equal size; larger pitches defer.

**Division boundary.** Flambeee Games stays as is: six shipped games, small web games continue, directive 6 governs game originality. Flambeee Apps does not rename, absorb, or re-theme the games, and games work does not block on Apps.

## Requirements

### 1. Owner named

- One accountable owner named for the division at planning stage (parent, per above), plus the steady-state product owner (Ember).
- No unowned surface: every future Apps story names its dev owner under Story 048 before dev starts.

### 2. Scope bounded

- In-scope list (small useful web apps, house rules, same SDLC and copy rules) and explicit out-of-scope list (native, accounts/backends, push, paid, build steps, new servers) both stated in the doc.

### 3. First app fixed

- Exactly one first app named (default above) with its reuse test (used daily or it does not ship) and its size cap (no backend, no build).
- Counter-proposal rule stated: one equal-size alternative allowed, larger pitches deferred.

### 4. Planning only

- No code, no site card, no new directory, no release change this half.

## BDD scenarios

**Scenario 1: Owner named.**
Given the CEO requires an Apps division, when this doc is read, then it names the planning owner and the steady-state product owner with no shared or unowned surface.

**Scenario 2: Scope bounded.**
Given future Apps pitches, when checked against this doc, then in-scope items (small useful web apps under house rules and SDLC) pass and out-of-scope items (native, accounts, push, paid, build steps, new servers) are rejected without debate.

**Scenario 3: First app fixed.**
Given the gate to the first dev wave, when the dev wave plans, then it builds the named first app (or one equal-size counter-proposal) and defers anything larger.

**Scenario 4: Games untouched.**
Given the division boundary, when games work plans, then no games story depends on Apps and no Apps story renames or re-themes the games.

**Scenario 5: No code.**
Given this story's diff, when inspected, then it contains only this Markdown file and changes no source, site, script, blog, or release file.

## Acceptance Criteria

**AC-1.** Owner named for planning and steady state (Scenario 1).
**AC-2.** Scope stated with in-scope and out-of-scope lists (Scenario 2).
**AC-3.** First app named with reuse test and size cap (Scenario 3).
**AC-4.** Division boundary protects games work both ways (Scenario 4).
**AC-5.** Planning only, no code or site change (Scenario 5).
**AC-6.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Designing the first app beyond the one-paragraph default above.
- Any Apps code, site card, asset, or directory.
- Staffing, hiring, or schedule commitments.
- Any change to games, site, or release process.

## Open questions for dev wave

1. First-app default vs counter-proposal: accept the UTC countdown pad or name one equal-size alternative with its reuse test.
2. Site placement for the future Apps card row (parent decides at build time, not here).
3. Whether Apps needs its own stats-key prefix convention (recommend `flambeee-apps-*`; dev wave confirms).
