# Test Plan: 025 - Cinder Daily Quest System (v0.15.0)

**Story:** `docs/stories/025-cinder-daily-quest.md`
**Priority:** P0 (headline)
**QA analyst:** Scout
**Date:** 2026-09-06
**QA bar (Session 14):** Real browser taps/clicks required for all UI work. Mobile viewport render check mandatory, not merely claimed.

## Goal

Verify that Cinder assigns exactly one deterministic daily quest per UTC day, tracks progress from real combat/gold outcomes, pays the bonus once, persists completion state across reload, resets at UTC, degrades gracefully for existing saves and private mode, and is fully playable by real tap on mobile — all with zero regressions to the existing fights/day, Inn reset, and hub-modal stats.

## Test Environment

- **Deployed (live):** `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`
- **Repo copy (must be byte-identical):** `/home/jake/.openclaw/workspace/flambeee/src/cinder.html`
- **Tooling:** Playwright (Chromium) via `/home/jake/.openclaw/workspace/.venv/bin/python3`
- **Viewports:** Desktop 1280x800; Mobile 390x844, `has_touch: true`, `is_mobile: true`
- **Storage keys:** `flambeee-cinder-day` (day-state: dayIndex, fightsUsed, innHealsUsed, + new quest fields), `flambeee-cinder-save` (character: level/gold/wins/deaths — MUST NOT be reshaped)
- **Automation note:** `getDayIndex() = Math.floor(Date.now()/86400000)` anchors the UTC reset. For UTC-boundary tests, freeze the clock via Playwright `page.clock` or `addInitScript` overriding `Date.now` so the run is hermetic.

## BDD Scenario Verification

| # | Scenario | Method (REAL input) | Success Criterion |
| :--- | :--- | :--- | :--- |
| 1 | One deterministic daily quest | Load Cinder in a fresh profile; read the quest objective. Reload in a second profile; read objective. | Exactly one quest active; BOTH profiles see the identical objective for the same UTC day. |
| 2 | "Today's quest" entry in town hub | Base state = town hub. Real `page.tap()` on the "Today's quest" row AND keyboard path (press row number + Enter). | Row present with a live progress tail, selectable by both tap and keyboard. |
| 3 | Quest detail shows objective, progress, reward | Tap the quest row to open the detail view. | Panel shows objective text, current progress (e.g. 2/3), and the bonus reward (XP/gold). |
| 4 | Progress updates as I play | Fight monsters / earn gold / win boss fight per the objective; re-open the quest view. | Progress count increments from the REAL combat outcome; the hub progress tail updates live. |
| 5 | Quest completes and pays bonus once | Drive progress to the objective via real combat. | Quest marked complete; bonus XP/gold applied exactly once; UI shows collected indicator. |
| 6 | Completed stays complete, no re-pay | After completion, reload; then take more qualifying actions. | Still complete; no additional reward; progress counter does not move past completed state inconsistently. |
| 7 | No double-pay after reload | Close + reopen Cinder before UTC reset. | Completed quest stays complete, no claimable reward, XP/gold EXACTLY equals what was granted at completion. |
| 8 | UTC reset -> new quest, progress cleared | Freeze clock to next UTC day; reload. | Previous quest/progress/completion cleared; new day's deterministic quest assigned; progress = 0; fights/day + Inn also reset. |
| 9 | Existing save, no quest state | Seed a `flambeee-cinder-save` with NO quest fields (fresh/old format); load game. | Quest shows available today, 0 progress; character + day state load with no crash, no corrupt data. |
| 10 | Full flow on mobile by tap | Mobile viewport; real `page.tap()` from hub -> quest -> complete action -> claim. | Every step works by tap; progress + completion state update correctly. |
| 11 | Private mode safe | Block localStorage (incognito / `page.add_init_script` throwing on storage). | Quest assigns/tracks/completes in-session; no unhandled error; nothing persists between sessions. |

## Edge Cases & Boundary Conditions

- **Progress at exact threshold:** Bring progress to N-1, then take the qualifying action. Verify complete fires exactly at N, not N+1, and the reward is not granted twice (double-increment guard).
- **Counter overflow past objective:** After completion, force the progress counter past the objective value (e.g. earn gold beyond a gold-tally quest). Verify the displayed counter does not creep past the completed state / no inconsistent readout.
- **Quest type non-repetition:** For the rotation guarantee, simulate consecutive UTC days and assert the quest type does not repeat two days running (if required by CEO decision). Record the actual rotation ordering.
- **Boss-fight objective definition:** If the daily quest is a boss-fight objective, confirm the mapped monster tier is reachable at a fresh character's level (no impossible-for-day-one quest). Verify what counts as a "boss fight".
- **Reward balance sanity:** Record the actual bonus XP/gold amounts vs a single fight's reward. Flag to the CEO if the bonus is trivial (< ~0.5x a fight) or game-skipping (> ~3x a fight).
- **FFights/day interplay:** A completed quest + fights/day at cap in the same session. Verify quest claim still works when fights are exhausted (completion already achieved), and that completing the quest does not reset/alter `fightsUsed`.
- **Reload at every state:** Reload mid-quest (partial progress), at exactly the finishing action, and post-completion. State must be consistent at each point.
- **LocalStorage write failure mid-action:** If the quest save write throws (quota), verify the in-session flow still completes without an unhandled error (mirror the existing try/catch pattern).
- **Menu row numbering stability:** Existing rows 1-7 (Wilderness, Weapon, Armor, Bank, Inn, Trainer, Tavern) must be unchanged; verify row 8 ("Today's quest") appended, not renumbered.
- **Hub-modal stats regression:** The existing hub modal in `share/Flambeee/index.html` reads `flambeee-cinder-save`. After playing with the quest, open the site modal and verify level/gold/wins/deaths are unchanged in shape and correct in value.
- **Accessibility:** completion/progress conveyed by TEXT (e.g. "2/3", "COMPLETE"), not color alone; objective text readable at mobile size.

## Regression Checks

- `cmp` the deployed file vs the repo copy must exit 0 (byte-identical).
- Keyboard input (numbers + Enter) still works on all existing menu rows.
- Real `page.tap()` works on all existing menu rows (data-action delegated listener).
- No console errors / unhandled rejections on any of the above paths.

## Defect Reporting Format

Any failure recorded as: severity (Blocker / Major / Minor / Cosmetic), steps to reproduce, expected vs actual, environment (viewport, storage state), and attached console output. QA verifies and reports; QA does not fix.