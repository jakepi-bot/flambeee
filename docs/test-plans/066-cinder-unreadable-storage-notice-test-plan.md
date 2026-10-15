# Test Plan — Story 066: Cinder unreadable-storage visible notice (Session 31, P1)

**Story:** `docs/stories/066-cinder-unreadable-storage-notice.md`
**Handoff:** `flambeee-team/requirements-handoff.md` (Session 31)
**Dev results:** `flambeee-team/dev-results.md` — no Kai/Riven Session 31 sections exist at QA time (file still Session 30 content). Plans derived from story + handoff only.
**QA:** Scout, 2026-10-15. **Target:** v0.29.0. No em dashes, plain punctuation.

## Scope

Story 066 implements the Story 058 ruling (ACCEPT Option 2): when Cinder storage is
unreadable on either record (character via `loadSave()`, day via `loadDayState()`),
show a visible non-blocking one-line notice and let the player play for the session.
Pure presentation. No new persisted field, no economy change. Story 058 is the decision
record and is not edited.

**Code under test:** `src/cinder.html`, `init()` at line ~1624, storage helpers
`loadSave()` (~935), `loadDayState()` (~950). Entering behavior: both catch and return
`null`, which routes silently to a new game (Option 1 behavior). Expected post-066:
same catch points also fire a one-line non-blocking notice.

## Environment

- Chromium via playwright-core, executable
  `/home/jake/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome`
- Target: local file `src/cinder.html` served over file:// (same-origin simple case;
  file:// localStorage is available in Chromium unless blocked).
- Viewports: desktop 1280x800, mobile 375x667.
- Unreadable-storage config: `context.addInitScript` that redefines
  `window.localStorage` / `window.sessionStorage` getters to throw `SecurityError`
  (simulates blocked storage / private mode). Fires before app scripts run.

## Cases

| ID | Type | Config | Expectation (post-066) | Story AC |
|----|------|--------|------------------------|----------|
| 066-P1 | positive | readable store, desktop 1280x800 | loads, no notice, town or creation screen, no console errors | AC-2, AC-3 |
| 066-P2 | positive | readable store, mobile 375x667 | loads, no notice, no horizontal overflow | AC-3, AC-5 |
| 066-N1 | negative | localStorage throws on read, desktop | one-line non-blocking notice visible, session playable (input accepted) | AC-1, AC-2, AC-7 |
| 066-N2 | negative | localStorage throws on read, mobile 375x667 | notice visible, no horizontal overflow, input not blocked | AC-1, AC-2, AC-5, AC-7 |
| 066-N3 | negative | localStorage throws on write only | notice or graceful play, no uncaught exception | AC-1, AC-2 |
| 066-N4 | negative | notice path writes nothing | stored keys byte-identical before/after notice path | AC-6 |
| 066-C1 | copy | notice text read | states unreadable as fact, offers no restore, plain punctuation, Vigil sign-off | AC-4 |

## Pre-066 baseline (what QA can observe now)

With no 066 implementation on `main` (4d42f9f), N1/N2 are expected to show the
entering silent-new-game path (no notice) or an uncaught error. That absence is the
run-1 finding the Kai harness would formalize once a PR exists.

## Results

| ID | Result | Evidence |
|----|--------|----------|
| 066-P1 | TBD by run | see qa-results.md |
| 066-P2 | TBD by run | see qa-results.md |
| 066-N1 | TBD by run | see qa-results.md |
| 066-N2 | TBD by run | see qa-results.md |
| 066-N3 | TBD by run | see qa-results.md |
| 066-N4 | TBD by run | see qa-results.md |
| 066-C1 | NOT RUNNABLE | no notice exists on main; needs Riven PR + Vigil review |

## Kai harness gate

No Kai PR exists (0 open PRs, no 066 branch on origin). Harness not runnable.
Re-run gate: when a `*066*` branch/PR appears, run the harness run 1 (pre-066 absence)
and run 2 (merged candidate exit 0) and paste output here.
