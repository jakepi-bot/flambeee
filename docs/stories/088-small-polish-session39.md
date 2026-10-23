# Story 088: Day Pad stale save-confirmation clear (Session 39, P1, User-Visible Polish)

**Status:** Ready for development (Session 39, 2026-10-23).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible; session ship first per parent call).
**Assigned to:** **Riven** frontend owner. **Scout** QA.
**Tracked by:** Session 39 plan, Story 088. First user-visible change since v0.33.0.
**Depends on:** `website/apps/index.html` (Day Pad, Stories 072/075/077) plus `website/sw.js` CACHE rule. No FPS dependency. No gamepad dependency.

## Summary

Day Pad's save confirmation goes stale. After Save, `noteStatus` reads "Saved." and stays there while the player keeps typing, so the line on screen describes an edit that was never saved. One behavior change in one file: clear `noteStatus` on `input` so the confirmation only ever describes the last save. This plus the folded-in Day Pad note from session 36 is the v0.34.0 announcement the release wave decides on.

## jakebot decision (advisory only, recorded)

Session 39 Wave 1 priorities per session 20261023_011104_76722e: (b) FIRST small user-visible website or game polish, genuinely small (one page, one behavior, sw.js CACHE bump if a precached file changes), because four straight no-release sessions (35-38) left zero user-visible lines since v0.33.0. This story is that item.

**Citation:** `flambeee-team/session-plan.md`, Session 39 (2026-10-23), section "jakebot decision (advisory only, recorded)", session 20261023_011104_76722e.

## Concrete item grounded in current repo state

- **File changed:** `website/apps/index.html` only (lines 103-107 markup, lines 170-180 script, measured on origin/main at `379eedf`).
- **Defect:** `saveNote()` (lines 170-177) sets `status.textContent = 'Saved.'` on save, but the `input` listener (line 180) calls only `updateCount()`. After a save, further typing leaves "Saved." on screen next to unsaved text. A second save re-sets the identical string, so the polite live region does not re-announce either.
- **One behavior changed:** the `input` handler also clears `noteStatus` (sets it to empty) whenever the field value changes after a save. Nothing else changes: prefix `flambeee-apps-` unchanged, maxlength 280 unchanged, N/280 count behavior unchanged, countdown untouched, save path untouched.
- **Files explicitly not touched:** `src/`, `website/index.html`, `website/games/`, no other page.

## CACHE bump rule (load-bearing)

`website/apps/index.html` is in `PRECACHE_URLS` (`website/sw.js` line 38). Per the sw.js comment rule, which Story 077 settled as governing (any change to an already-precached file needs a CACHE bump; the Story 075 no-bump exception is superseded): this story bumps `CACHE_VERSION` 9 to 10 in `website/sw.js` (line 21) in the same diff. Without the bump, returning visitors keep serving the pre-088 Day Pad from cache and the fix reads as a no-op. No precache-list change (the entry already exists).

## Requirements

### 1. Behavior contract

- After Save, `noteStatus` reads "Saved." (unchanged).
- On the next `input` event in `#noteInput`, `noteStatus` is cleared to empty (new). The count still updates on the same event.
- Save after an edit sets "Saved." again, which re-announces because the text changed from empty (fixes the silent second save as a consequence, no extra code).
- Failed save ("Could not save in this browser.") follows the same rule: cleared on next input.

### 2. Verification (headed Chromium, local serve)

- Load the page, type a line, click Save: status reads "Saved.".
- Type one more character: status is empty, count updated.
- Click Save again: status reads "Saved." again.
- Reload: saved line restores with count correct (existing Story 075 behavior, regression check).
- Desktop 1280x800 and mobile 375x667, zero console errors.

### 3. Scope guard

One page, one behavior. No countdown change, no storage-shape change, no new persisted field, no prefix change, no second page. Diff is `website/apps/index.html` plus the one-line `website/sw.js` CACHE bump.

## BDD scenarios

**Scenario 1: Confirmation shows on save.**
Given a typed line, when Save is clicked, then `noteStatus` reads "Saved." and the count is unchanged.

**Scenario 2: Confirmation clears on next edit.**
Given "Saved." on screen, when one more character is typed, then `noteStatus` is empty and the N/280 count reflects the new length.

**Scenario 3: Re-save re-confirms.**
Given a cleared status after an edit, when Save is clicked again, then `noteStatus` reads "Saved." again (a text change, so the polite live region announces it).

**Scenario 4: Restore path intact.**
Given a saved line, when the page reloads, then the line restores with the correct count (Story 075 behavior, unchanged).

**Scenario 5: CACHE bump lands.**
Given `./apps/index.html` is precached, when this diff ships, then `CACHE_VERSION` is 10 and a returning visitor gets the fixed page after reload (no stale-shell serve).

**Scenario 6: v0.34.0 announcement line enabled.**
Given the fix merged, when the release wave writes the notes, then the line below is accurate with no further dev work.

## v0.34.0 announcement line (enabled by this story)

Day Pad: the save confirmation now clears while you type, so Saved means saved.

## Acceptance Criteria

**AC-1.** `website/apps/index.html` clears `noteStatus` on `input`; save sets it as before (Scenarios 1, 2, 3).
**AC-2.** Headed Chromium proof at both viewports with real typed input and clicks, zero console errors (Scenarios 1-4).
**AC-3.** `CACHE_VERSION` 9 to 10 in `website/sw.js`, precache list otherwise byte-identical (Scenario 5).
**AC-4.** Diff limited to the two files above; no storage-shape or prefix change (section 3).
**AC-5.** Copy uses plain punctuation, no em dashes, no heavy emoji.
**AC-6.** jakebot citation 20261023_011104_76722e recorded above.

## Non-Goals

- Any countdown, date, or restore-logic change.
- Any storage-shape, prefix, maxlength, or count-format change.
- Any second page, any game-file change, any checker change.
- Advancing the FPS slice or scheduling a gamepad run on this box.
- The release cut itself (release wave decides v0.34.0).

## Open questions for dev wave

1. Exact handler edit (one line in the `input` listener vs a named clear function; record the final line).
2. CACHE bump line recorded with before and after values.
3. Headed proof output pasted with viewport sizes and exit codes.
