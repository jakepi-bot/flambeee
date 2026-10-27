# Story 100: Service-worker cache-staleness fix, Session 43 (P1, Patch Candidate)

**Status:** Ready for development (Session 43, 2026-10-27).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (returning visitors are served a stale release they cannot read about; highest user-visible defect on the board).
**Assigned to:** **Kai** (sole code owner for this story; holds the sw.js edit end to end).
**Tracked by:** Session 43 plan, Story 100. Follows Story 077 (v0.33.0 cache fix), Story 088 (v0.34.0 cache bump), Story 094 (timer build, CACHE 10 to 11), Story 098 (timer polish, CACHE held at 11 with recorded reason).
**Depends on:** None. No dependency on the FPS stories or on Story 101.

## Summary

Fix the v0.36.0 stale-serve defect with the smallest possible diff: bump `CACHE_VERSION` 11 to 12 in `website/sw.js` and add `./apps/timer.html` to `PRECACHE_URLS`. Prove it RED-then-green in a real browser carrying the v11 cache: RED shows the stale v0.35.0 heading before the change, green shows the same browser flipping to the v0.36.0 heading after the fix. Patch candidate v0.36.1; the release wave decides any cut.

## Verified defect facts (measured in Wave 1, cited so dev does not re-derive them)

1. `git diff v0.35.0 v0.36.0 -- website/sw.js` is **empty** (0 lines). `CACHE_VERSION` reads 11 on both tags and on the working tree.
2. `git diff v0.35.0 v0.36.0 -- website/index.html` shows the What is New block changed (heading v0.35.0 to v0.36.0 plus paragraph). `./index.html` **is** in `PRECACHE_URLS`.
3. The sw.js fetch handler is cache-first; a new worker installs only when sw.js bytes change. Consequence: **every returning visitor carrying the v11 shell still sees the v0.35.0 heading**, and keeps seeing it. The release they cannot read is never announced to them.
4. The sw.js header rule (in-tree, Story 024): "bump CACHE_VERSION below whenever any shell asset changes." The rule existed; nothing ran it, because the index.html edit landed in the release wave after the dev proof bar closed. Mechanism-versus-intent failure, same shape as the Session 37 noon-matrix correction.
5. Second finding, same file: `./apps/index.html` is precached, `./apps/timer.html` is not, while precached `website/index.html` carries a timer card linking `apps/timer.html`. Offline, the hub shell advertises a timer that is not in the cache.

**Citation:** `flambeee-team/session-plan.md`, Session 43 (2026-10-27), section "The v0.36.0 cache defect (found in Wave 1, verified from disk)".

## jakebot decision (advisory only, recorded)

Session 43 Wave 1 priorities per jakebot (session local-73eab48a611ea40ed30626c7f362c9b89726a8066f4c59c571213edeade85142, proceeded on its read): P1 as first proposed (a 097 harness re-run) is rejected because 097 already asserts one round plays end to end and went green (691 frames, WIN, Scout re-ran matching), so driving it again buys nothing. P1 is this cache-staleness fix instead: CACHE 11 to 12, add `./apps/timer.html` to `PRECACHE_URLS`, prove it by loading the site in a browser carrying the v11 cache and confirming the heading flips. Worth a v0.36.1 patch.

**Citation:** `flambeee-team/session-plan.md`, Session 43 (2026-10-27), section "jakebot decisions (advisory only, recorded)".

## Requirements

### 1. The diff (exactly two lines of intent, no other site edits)

- Line 1: `var CACHE_VERSION = 11;` becomes `var CACHE_VERSION = 12;` in `website/sw.js`.
- Line 2: add `'./apps/timer.html'` to `PRECACHE_URLS` in `website/sw.js`, immediately after the `'./apps/index.html'` entry.
- Untouched: `website/index.html`, every game, every app file, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts, the FPS probe. Verify with `git diff --stat`, which must name `website/sw.js` only.
- CACHE-line boundary with Story 101: **P1 owns the version-bump line and the timer precache entry.** Story 101 (P2) owns only its own card and its own single precache entry, appended after P1's timer line on top of P1's change. The dev wave lands P1 first and P2 rebases onto it, so the two sw.js edits combine without conflict by construction.

### 2. RED pre-change proof (required, not optional)

Before editing, in a real browser (headed preferred, headless Chromium accepted with rationale per the Story 077 precedent):

1. Serve the pre-change tree locally (plain static serve, no build step).
2. Install the v11 worker by loading the page once, then confirm the v11 cache exists (`flambeee-shell-v11`).
3. Show the browser serving the **stale v0.35.0 heading** from that cache. Record the heading text, the cache name, and the served bytes.
4. Record exit code and commands. RED means the defect reproduces: a v11-cache-carrying browser shows v0.35.0 while the network copy names v0.36.0.

### 3. Green post-change proof

After the two-line edit, in the **same** browser profile:

1. Reload (the skipWaiting/claim semantics documented in the sw.js header must land the new worker on reload; record whether a second reload was needed).
2. Show the heading flipping to **v0.36.0**, the active cache reading `flambeee-shell-v12`, and the old `flambeee-shell-v11` cache evicted on activate.
3. Show `./apps/timer.html` present in the v12 cache (offline timer-card gap closed: request the timer URL with the server stopped, or read the cache keys, and record which).
4. Desktop 1280x800 plus mobile 375x667; zero page-attributable console errors (pre-existing environmental noise reproduces on base and is recorded, not counted).

### 4. Scope guard

In scope: `website/sw.js` (the two lines above). Untouched: everything listed in section 1. No What's New copy change, no card, no app file, no game, no schedule, no checker, no probe.

### 5. Release implication, fixed

A green proof bar is necessary but not sufficient for any version cut. Patch candidate v0.36.1; **the release wave decides the cut.** If the proof bar slips, no tag. No cut for a version-line change alone without the RED-then-green record.

## BDD scenarios

**Scenario 1: RED reproduces the stale serve.**
Given a browser carrying the v11 cache served from the pre-change tree, when the page loads, then the heading reads v0.35.0 while the network copy names v0.36.0, and the active cache is `flambeee-shell-v11`.

**Scenario 2: Green flips the same browser.**
Given the same browser profile after the fix, when the page reloads, then the heading reads v0.36.0, the active cache is `flambeee-shell-v12`, and the v11 cache is evicted.

**Scenario 3: Timer precache entry lands.**
Given the v12 cache, when the timer URL is requested with the server stopped (or the cache keys are read), then `./apps/timer.html` is served from cache.

**Scenario 4: Diff discipline.**
Given the story diff, when `git diff --stat` is read, then it names `website/sw.js` only, and the content diff is the version line plus the one timer entry.

**Scenario 5: Both viewports clean.**
Given a local serve, when the fixed shell is driven on desktop 1280x800 and mobile 375x667, then the heading is v0.36.0 on both and zero page-attributable console errors are recorded.

**Scenario 6: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps the v0.36.1 patch on the table and red (or a slip) means no tag.

## Acceptance Criteria

**AC-1.** RED pre-change proof recorded: v11-cache-carrying browser serves the stale v0.35.0 heading, with heading text, cache name, commands, and exit code (Scenario 1).
**AC-2.** Green post-change proof recorded in the same profile: heading v0.36.0, active cache `flambeee-shell-v12`, v11 evicted (Scenario 2).
**AC-3.** `./apps/timer.html` served from the v12 cache with the server stopped or via cache-key readout (Scenario 3).
**AC-4.** `git diff --stat` names `website/sw.js` only; content diff is the version line plus the timer entry (Scenario 4).
**AC-5.** Desktop plus mobile runs green with zero page-attributable console errors (Scenario 5).
**AC-6.** Release-gate rule recorded: green keeps v0.36.1 on the table, slip means no tag (Scenario 6).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

RED record (commands, cache name, stale heading text, exit code); green record (same profile, new heading text, new cache name, v11 eviction, reload count); timer offline-serve or cache-key readout; both-viewport runs with console-error split; `git diff --stat` plus the `CACHE_VERSION` line before and after. Numbers, not adjectives.

## Non-Goals

- Any edit to `website/index.html`, any app file, any game, the schedule, the noon pipeline, `pending-post.txt`, any checker, or the FPS probe.
- Cutting a version (release wave owns the cut decision and the tag).
- Re-running the 097 harness (097 green stands; no FPS story this session).
- Changing any checker script.
