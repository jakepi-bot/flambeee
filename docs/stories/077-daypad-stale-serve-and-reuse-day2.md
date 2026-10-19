# Story 077: Day Pad stale serve plus day-2 reuse plus cache fix (Session 35, P1, Dev)

**Status:** Ready for development (Session 35, 2026-10-19).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (dev; session ship; Principle 1 every session ships something playable).
**Assigned to:** **Riven** frontend owner (Apps surface plus service worker line). **Scout** QA and witness.
**Tracked by:** Session 35 plan, Story 077. Sibling to Story 074, not a child of it.
**Depends on:** Story 072 (Day Pad shipped, prefix `flambeee-apps-`, CACHE_VERSION 8), Story 075 (N/280 count, merged as e266eb9). No FPS dependency.

## Summary

Fix one measured defect class in the Day Pad ship path and validate day-2 reuse while doing it. Story 075 edited the already-precached `website/apps/index.html` with no CACHE bump, under a cache-first worker. Returning visitors holding a v8 cache are served the pre-075 Day Pad with no N/280 count. This story reproduces that stale serve locally, runs day-2 reuse against both the source path and the SW path, then fixes in one line. If reuse finds a defect, the fix IS the improvement and no elective work is added.

## jakebot decision (advisory only, recorded)

Session 35 Wave 1-2 set A-variant, evidence-first, per session 20261019_011109_2495b4: P1 Day Pad day-2 reuse validation folded into a small bounded playable improvement plus P2 currency, gate as note. B waits on the gate. Day-2 validation picks the improvement; no unevidenced tweak is pre-picked.

**Citation:** `flambeee-team/session-plan.md`, Session 35 (2026-10-19), section "jakebot decision (advisory only, recorded)", session 20261019_011109_2495b4.

## The contradiction (cited verbatim)

The service worker comment rule (`website/sw.js`, lines 9-11):

> Cache versioning: bump CACHE_VERSION below whenever any shell asset changes. The new version installs, then deletes every older flambeee-shell-v* cache on activate. No stale asset mixing.

Story 075 rule 7 (`docs/stories/075-small-playable-improvement.md`, lines 60-62):

> If a precached file is added to `PRECACHE_URLS`, bump `CACHE_VERSION` in `website/sw.js` (currently 8) by exactly 1 on the repo side. If no precached file is added (expected: edit in place to an already precached page), no bump. Record the decision either way.

These two rules disagree on the exact case that shipped. Story 075 edited the already-precached `website/apps/index.html` (commit e266eb9) with no `sw.js` change (`sw.js` last touched in 4394348, Story 072). Under rule 7 that was correct procedure. Under the sw.js comment rule it was a missed bump. The fetch handler is cache-first (`website/sw.js:87-88`):

> function cacheFirst(request) { return caches.match(request).then(function (cached) {

with `if (cached) return cached;` on the next line, so a cached v8 shell wins over the network and the returning visitor sees the pre-075 Day Pad with no N/280 count.

Precedent: v0.25.0 (`docs/roadmap.md`, Story 057 entry) bumped CACHE_VERSION 3 to 4 for a content change to an already-precached file, recorded as load-bearing because without it "a returning visitor is served the pre-056 shell from cache and the release reads as a no-op". Story 075 shipped the same failure class under the wrong rule.

## Rules carried into this story

**Fixed P1 order.** Reproduce first, then reuse on both paths, then fix. No step is skipped and no step is reordered: (1) reproduce the stale serve locally, (2) run day-2 reuse against both the source path and the SW path, (3) land the one-line fix. If reuse finds a defect, the fix IS the improvement and the elective improvement drops.

**Verifiable without the share path.** Proof is commit plus local serve plus headed Chromium, all runnable on this box. No step reads `/home/jake/share/Flambeee/`. Day Pad uses no Pointer Lock, so this box can run the full proof.

**No new persisted field.** Storage key prefix stays `flambeee-apps-`, maxlength 280 unchanged. A changed key orphans day-1 data the reuse test depends on. Per Story 039/042 precedent, any new persisted field needs a decision record plus sign-off, which is out of scope here.

**Single owner, single file, boundary named first.** If both `website/sw.js` and `website/apps/index.html` are touched, the ownership boundary is named before dev starts per Story 048. Expected shape is one line in one file.

**Apps/Games division boundary.** Keep the Apps/Games division boundary. Do not pull game code in to satisfy "playable". No `src/` game file is touched.

## Requirements

### 1. Reproduce the stale serve

- Serve the repo locally, install the v8 worker in headed Chromium, then apply the 075 tree and reload with the v8 cache held.
- Expected: the served Day Pad is the pre-075 page with no N/280 count, proving a returning visitor never sees the release.
- Record commands, exit codes, and the observed count label (absent vs present).

### 2. Day-2 reuse on both paths

- Day-1 reuse evidence is 2026-10-18 (Story 075). Day 2 is 2026-10-19 (this session).
- Open Day Pad on local serve via the source path (direct page URL, no worker) and via the SW path (worker-controlled reload), confirm the day-1 saved line persists across the UTC midnight boundary and the countdown rolls to the new day, on both paths.
- The two paths differ and that is the point: source path proves the app, SW path proves the ship. If either path fails, it is a finding on this story, not a new story.

### 3. One-line fix

- Either bump CACHE_VERSION 8 to 9 in `website/sw.js`, or write a one-line correction of the sw.js comment rule. One line either way.
- The fix must resolve the contradiction at rule level, not just bump past it: after the fix, the comment rule and the story rule agree on the in-place-edit case. Record which option was taken and why.

### 4. Prefix and size cap

- Storage key prefix stays `flambeee-apps-` (Story 072). maxlength 280 stays enforced. Persistence behavior unchanged (same key, same restore path).
- No backend, no build step, no new server, no new dependency. localStorage only.

### 5. Division boundary

- Apps tree stays separate from Games. No games story depends on this change and no change here renames, absorbs, or re-themes any game.

## BDD scenarios

**Scenario 1: Stale serve reproduced.**
Given a headed Chromium holding the v8 cache, when the 075 tree is served and the worker-controlled page reloads, then the Day Pad shows the pre-075 page with no N/280 count, and the commands plus observed label are recorded.

**Scenario 2: Day-2 reuse on the source path.**
Given the day-1 saved line from 2026-10-18, when Day Pad opens on 2026-10-19 via the direct page URL, then the saved line persists, the countdown rolls to the new day, and the result is recorded.

**Scenario 3: Day-2 reuse on the SW path.**
Given the same day-1 saved line, when Day Pad opens on 2026-10-19 via the worker-controlled reload, then the saved line persists, the countdown rolls to the new day, and the result is recorded against the post-fix cache version.

**Scenario 4: One-line fix lands.**
Given the reproduced stale serve, when the fix merges, then exactly one line changed (CACHE 8 to 9, or the comment correction), the comment rule and the story rule agree on the in-place-edit case, and a worker-controlled reload serves the N/280 count.

**Scenario 5: No new key.**
Given the app writes, when storage is inspected, then the `flambeee-apps-` prefix is used with no rename and maxlength 280 holds.

**Scenario 6: Verifiable without share path.**
Given the merged commit, when proof runs, then it uses only commit hash plus local serve plus headed Chromium on this box, records commands and exit codes, and reads nothing from `/home/jake/share/Flambeee/`.

**Scenario 7: Division boundary holds.**
Given games work, when it plans, then no games story depends on this change and no change here touches `src/`.

## Acceptance Criteria

**AC-1.** Stale serve reproduced locally with commands and observed label recorded (Scenario 1).
**AC-2.** Day-2 reuse passes on both the source path and the SW path with the 2026-10-19 date recorded (Scenarios 2, 3).
**AC-3.** One-line fix merged; comment rule and story rule agree on the in-place-edit case; worker-controlled reload serves the count (Scenario 4).
**AC-4.** Prefix stays `flambeee-apps-`, maxlength 280, no new persisted field (Scenario 5).
**AC-5.** Proof by commit plus local serve plus headed check, no share-path read (Scenario 6).
**AC-6.** Division boundary holds both ways, no `src/` touch (Scenario 7).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- A second app or a second improvement in the same diff.
- Advancing the FPS playable slice before the gamepad gate has run.
- A pre-picked elective tweak. If reuse is clean, the fix is the ship.
- Any change to small web games, the site index, or the release process.
- A gamepad run on this box. There is no pad here; see the note below.

## Notes (not stories, carried by this file)

1. **Headed gamepad gate: OPEN-BLOCKED-ON-HARDWARE.** Pointer to the Story 074 runnable gate verbatim (rig jake-dev-desk, headed mode, pass criteria, Kai runs plus Scout witnesses, Session 35). Flip trigger: pad plus headed browsers available on the named rig. Carry-forward line: each subsequent session carries this note until it flips.
2. **Day-3 reuse trigger: 2026-10-20.** The 3-day probe closes on day 3; the session owning 2026-10-20 records the final reuse claim.
3. **Cache-rule contradiction at rule level.** The sw.js comment rule and Story 075 rule 7 disagree on in-place edits to precached files. This story resolves it for the Day Pad case; the standing currency checker and future stories must cite the resolved rule, not re-litigate it.

## Open questions for dev wave

1. Fix option taken (CACHE 8 to 9 vs comment correction) with reason.
2. Ownership boundary if both `sw.js` and `apps/index.html` are touched (name before dev per Story 048).
3. Local-serve port and headed browser version to record in proof.
