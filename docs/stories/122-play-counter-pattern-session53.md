# Story 122: Play counter pattern doc (Session 53, P1b, docs only)

**Status:** Ready for development (Session 53, 2026-11-06).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1b (docs only; the copy-paste pattern for the remaining 7 games and the apps).
**Assigned to:** **Kai** (docs owner; zero code, zero cache impact). Ember is product owner. No shared ownership.
**Tracked by:** Session 53 plan, Story 122. Design contract: `flambeee-team/design-handoff.md` (Rook, Session 53, sections 10 and Story 122 block).
**Depends on:** Story 121 as built. Any conflict between this pattern doc and Story 121 as built resolves in favor of Story 121. No code dependency.

## Summary

Write down the counter pattern once so later LEGACY sessions do not re-derive it. After this story, `docs/play-counter-pattern.md` holds the exact snippet family, the counting rule, the copy rule, the per-game checklist, and the unhappy-path summary, consistent with the Story 121 Typewreck build by content (same key family, same counting rule). Zero code, zero cache impact.

## jakebot decision (advisory only, recorded)

Same advisory as Story 121 (session local-0e08fb1d409009efbdac0ea5aa30943fcbe38fedc6b860bfe93c1db62c3d44dc): counter pattern on Typewreck only, plus the shared snippet, in the 55-minute window. This story is the shared snippet half. Not the full 8-game batch.

**Citation:** `flambeee-team/session-plan.md`, Session 53 (2026-11-06), sections "Decision (jakebot advisory...)" and "Priorities (in order)".

## Baseline measured at Session 53 planning (2026-11-06 01:10-01:20 CST)

| Check | Value |
|---|---|
| Pattern doc on base | `docs/play-counter-pattern.md` absent (RED anchor) |
| Shipped counter | none; Story 121 builds the first one this session |
| Remaining surface | 7 games plus the apps, all without a counter |

## Requirements

### 1. Owner named before the wave (Story 048)

Kai is the docs owner. This story touches exactly one docs file and no code, so overlap is impossible by construction. No shared ownership with the jobs pipeline or any outside team.

### 2. The pattern doc exists with six elements

`docs/play-counter-pattern.md` must contain all six, contradicting nothing in Story 121 as built:

1. Key family: `flambeee-<slug>-plays` (Typewreck: `flambeee-typewreck-plays`). Per-game copies change only the middle slug.
2. Load/increment/render trio: read with try/catch plus sanitize, write with try/catch, render the plays line on boot and after each increment, mirroring the existing best-score trio.
3. Counting rule verbatim from design-handoff section 2: one play equals one run start that deals and enters play; restart and replay count; page load, failed start, reload, tab restore, WIN/LOSE, and return-to-setup do not.
4. Copy rule verbatim from design-handoff section 5: `Plays on this browser: N`, always rendered including 0 on a first visit. The words "on this browser" are mandatory.
5. Per-game checklist: key suffix (middle slug), display element id and placement, run-start hook name (the function that resets score and enters play, never a click handler or page-load path), CACHE_VERSION bump in the same PR whenever a precached game file changes, no-network grep (no fetch, XMLHttpRequest, sendBeacon, WebSocket, or new external URL).
6. Unhappy-path summary from design-handoff section 6: blocked storage stays silent and keeps counting in memory for the session; corrupt, negative, or non-numeric stored values reset to 0 and never render garbage; quota failure drops the write silently; two tabs are last-write-wins and may lose at most one count (documented as acceptable).

What must change per game: the key suffix (middle slug), the display element id and its placement on that game's setup surface, and the run-start hook name. What must NOT change: the counting rule, the copy, the always-render-zero empty state, and the silent-storage-failure discipline.

### 3. Consistency rule

Anything in the doc that contradicts Story 121 as built is a defect against Story 122, resolved in favor of the built Story 121 rule.

### 4. Scope guard

In scope: `docs/play-counter-pattern.md` only. Untouched: every game file, every app file, `website/sw.js`, GAME_ORDER, the hub surface, the What's New block, the schedule, the noon pipeline, `pending-post.txt`, checker scripts, jobs, jakebot, cron config, PRs #206/#208/#211/#212/#217. Zero code, zero cache impact: this story never bumps CACHE_VERSION and never adds a precache entry.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the docs wave starts, then Kai holds the pattern doc as owner with zero code, and the dev record states the name.

**Scenario 2: Doc exists.**
Given the repo, when `docs/play-counter-pattern.md` is read, then the file exists and is non-empty. (RED anchor: absent on base.)

**Scenario 3: Key family.**
Given the pattern doc, when read, then it names the key family `flambeee-<slug>-plays` with the Typewreck instance.

**Scenario 4: Trio.**
Given the pattern doc, when read, then it holds the load/increment/render trio with try/catch plus sanitize discipline.

**Scenario 5: Counting rule.**
Given the pattern doc, when read, then it states the counting rule verbatim: one play per run start; restart and replay count; load, failed start, reload, restore, WIN/LOSE, and return-to-setup do not.

**Scenario 6: Copy rule.**
Given the pattern doc, when read, then it states the copy rule verbatim: `Plays on this browser: N`, always rendered including 0, with "on this browser" mandatory.

**Scenario 7: Per-game checklist.**
Given the pattern doc, when read, then it holds the per-game checklist: key suffix, display element, run-start hook, CACHE_VERSION bump in the same PR, no-network grep.

**Scenario 8: Unhappy paths.**
Given the pattern doc, when read, then it summarizes the unhappy paths: silent blocked storage with in-memory counting, corrupt or negative resets to 0, quota drop is silent, two tabs are last-write-wins.

**Scenario 9: Consistency.**
Given Story 121 as built, when the pattern doc is compared against it, then nothing contradicts it, and any conflict resolves in favor of Story 121.

**Scenario 10: Scope guard.**
Given the scope guard, when the diff is inspected, then the only changed file is `docs/play-counter-pattern.md`, with no game, app, site, or config path showing a diff.

## Acceptance Criteria

**AC-1.** Docs owner Kai named before the wave per Story 048 (Scenario 1).
**AC-2.** `docs/play-counter-pattern.md` exists and is non-empty (Scenario 2).
**AC-3.** Doc contains the key family (Scenario 3).
**AC-4.** Doc contains the load/increment/render trio (Scenario 4).
**AC-5.** Doc contains the counting rule verbatim (Scenario 5).
**AC-6.** Doc contains the copy rule verbatim (Scenario 6).
**AC-7.** Doc contains the per-game checklist (Scenario 7).
**AC-8.** Doc contains the unhappy-path summary (Scenario 8).
**AC-9.** Doc contradicts nothing in Story 121 as built; conflicts resolve for Story 121 (Scenario 9).
**AC-10.** Diff limited to the one docs file; zero code, zero cache impact (Scenario 10).
**AC-11.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

The pattern doc path plus a six-element checklist readout quoting each element's location in the file; a consistency statement against Story 121 as built; the diff file list showing only `docs/play-counter-pattern.md`. Numbers, not adjectives.

## Non-Goals

- Any code change, any game instrumentation, any CACHE bump, any precache entry.
- The other 7 games, M-2 registry or modal work, win or share counters, analytics, network calls, aggregation, visuals.
- Cutting a version (release wave owns the cut decision and the tag).
