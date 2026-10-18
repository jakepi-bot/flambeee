# Story 075: Small playable improvement (Session 34, P1, Dev)

**Status:** Ready for development (Session 34, 2026-10-18).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (dev; session ship; Principle 1 every session ships something playable).
**Assigned to:** **Riven** frontend owner (Apps surface). **Kai** consult on storage and prefix. **Scout** QA.
**Tracked by:** Session 34 plan, Story 075. Sibling to Story 074, not a child of it.
**Depends on:** Story 072 (Day Pad shipped, prefix `flambeee-apps-`, CACHE_VERSION 8). No FPS dependency.

## Summary

Ship one bounded improvement to the Day Pad app so Session 34 still ships something playable. Scope: add a visible character count (N/280) to the one saveable line, with maxlength enforced and line persistence unchanged. Verifiable without the share path by commit plus local serve plus headed check runnable on this box. Day Pad daily-reuse validation is folded in, not parked.

## jakebot decision (advisory only, recorded)

Session 34 Wave 1-2 set Option A per session 20261018_011238_406ef3: P1 FPS build-decision plus P1 small playable improvement plus P2 currency. The improvement is the ship; the FPS doc alone ships no playable thing.

**Citation:** `flambeee-team/session-plan.md`, Session 34 (2026-10-18), session 20261018_011238_406ef3.

## Rules carried into this story

**Verifiable without the share path.** Proof is commit plus local serve plus headed check, all runnable on this box. No step reads `/home/jake/share/Flambeee/`. If the share path is absent, the story still proves green.

**Size cap.** No backend, no build step, no new server, no new dependency. Single-file change to `website/apps/index.html` plus site text only if the count label needs it.

**Day Pad reuse validation folded in.** The reuse check ships inside this story (requirement 5 below), not parked. Carried twice from Sessions 32 and 33, closed here.

## Requirements

### 1. One bounded improvement

- Add a visible character count `N/280` next to the Day Pad saveable line, updating on input without reload.
- maxlength 280 already enforced stays enforced; persistence behavior unchanged (same key, same restore path).
- No second improvement, no redesign, no new app, no games change.

### 2. Verifiable without share path

- Prove by: (a) commit hash of the change, (b) local serve (`python3 -m http.server` from repo root or equivalent, no new dependency), (c) headed Chromium check on this box (real browser, not headless-only) showing count updates, reload restores line plus count, private mode and corrupt stored values degrade to empty state with no exception.
- Record commands, exit codes, and observed counts. No share-path read in the proof.

### 3. Size cap

- No backend, no build, no new server, no new dependency. localStorage only.
- Diff limited to `website/apps/index.html` and, if needed, one label line in `website/index.html`. No `src/` game file touched.

### 4. Division boundary

- Apps tree stays separate from Games. Games work does not block on Apps and this change does not rename, absorb, or re-theme any game.
- If the count label is shown on the site card, card text only, no game-card logic change.

### 5. Day Pad reuse validation folded in

- Folded in: Scout records a 3-day reuse probe (open Day Pad on three distinct UTC days on the local serve, confirm the saved line persists across the UTC midnight boundary and the countdown rolls to the new day).
- Reuse claim recorded in the dev results: Day Pad is the kind of thing opened daily to check the date plus countdown plus note. If the probe fails, it is a finding on this story, not a new story.

### 6. Prefix rule

- Storage key prefix stays `flambeee-apps-` (Story 072). No new prefix, no key rename. If a new key is unavoidable, confirm with Kai before first write and record it.

### 7. CACHE rule

- If a precached file is added to `PRECACHE_URLS`, bump `CACHE_VERSION` in `website/sw.js` (currently 8) by exactly 1 on the repo side. If no precached file is added (expected: edit in place to an already precached page), no bump. Record the decision either way.

## BDD scenarios

**Scenario 1: Count label shows and updates.**
Given the Day Pad page, when the user types in the saveable line, then a visible `N/280` count shows and updates on each input without reload.

**Scenario 2: Line persists with count.**
Given a typed line, when the page reloads, then the line is restored from localStorage and the count matches the restored length; private mode and corrupt stored values degrade to the empty state with no exception.

**Scenario 3: Verifiable without share path.**
Given the merged commit, when proof runs, then it uses only commit hash plus local serve plus headed Chromium check on this box, records commands and exit codes, and reads nothing from `/home/jake/share/Flambeee/`.

**Scenario 4: Size cap holds.**
Given the shipped diff, when inspected, then there is no backend, no build step, no new server, no new dependency, and no `src/` game file change.

**Scenario 5: Division boundary holds.**
Given games work, when it plans, then no games story depends on this change and no change here renames or re-themes the games; the Apps tree stays separate.

**Scenario 6: Prefix and cache rules hold.**
Given the storage key, when the app writes, then the `flambeee-apps-` prefix is used with no rename; given the precache list, when reviewed, then `CACHE_VERSION` moved if and only if a precached file was added.

**Scenario 7: Reuse validation folded in.**
Given Day Pad live on local serve, when opened on three distinct UTC days, then the saved line persists across the midnight boundary, the countdown rolls to the new day, and the reuse claim is recorded in dev results.

## Acceptance Criteria

**AC-1.** Visible `N/280` count ships on the Day Pad line, updating on input, persistence unchanged (Scenarios 1, 2).
**AC-2.** Proof by commit plus local serve plus headed check, no share-path read, commands and exit codes recorded (Scenario 3).
**AC-3.** Size cap holds: no backend, no build, no new server, no new dependency, no game file touched (Scenario 4).
**AC-4.** Division boundary holds both ways (Scenario 5).
**AC-5.** Prefix stays `flambeee-apps-`; CACHE_VERSION moved if and only if a precached file was added (Scenario 6).
**AC-6.** Day Pad 3-day reuse probe recorded with claim (Scenario 7).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- A second app or a second improvement in the same diff.
- Accounts, backends, push, paid tiers, native wrappers.
- Site redesign or games changes.
- A gamepad or FPS change under this story number.

## Open questions for dev wave

1. Count label placement (inline right of input vs below) without layout shift at 375px width.
2. Local-serve port and headed browser version to record in proof.
3. Reuse probe dates to use (three UTC days, recorded).
