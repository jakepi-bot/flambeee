# Test Plan: Story 104 FPS Keyboard Leg (Session 44) - DEFERRED, NO TESTABLE CODE

**Story:** `docs/stories/104-fps-keyboard-session44.md` (P2, bounded).
**Owner:** Kai. **Witness:** Scout.

## Status
Deferred. Dev record states: "Story 104: deferred, hours did not remain."
Per the story's own requirement 5 and Scenario 7, deferral is an accepted
outcome, recorded not failed, and carries to the next session plan.

## Why no testable code
No PR was opened for Story 104. No commits under `dev/fps-probe/` this
session. There is nothing to check out, serve, or drive, so no BDD scenario
(1-6) and no AC (AC-1 through AC-7, AC-9) can execute. AC-8 (deferral path)
is satisfied by the dev record line alone.

## What QA did
1. Confirmed no Story 104 PR exists (`gh pr list`: only #175 and #176 open).
2. Confirmed the dev record contains the exact deferral line from
   requirement 5.
3. Recorded no fail. No RED run is required for a deferred story.

## Next session
Re-plan from the story file as written: RED run first, then trusted key
events (WASD + click) plus arrow-key look through the 097 mapping layer at
1280x800 DPR 1x, 600+ frames with first-30 warmup excluded, p95 in
15.84-17.50ms, Scout independent re-run, harness-only diff.
