# Test Plan: Story 113 Checker Live Leg to Post-Deploy-Only (Session 48)

**Story:** `docs/stories/113-checker-postdeploy-session48.md` (P2, mechanism, rides along, justifies no cut).
**Owner:** Kai (single owner: `scripts/` only). **QA:** Scout. **PR:** #191, branch `kai/story-113-checker-postdeploy`, base `e63dc9c`, head `70f9e13`.
**Artifact:** Check 1 mode split in `scripts/verify-website-currency.sh`; Checks 2 through 8 byte-identical.

## Scope
In scope: `scripts/verify-website-currency.sh` (the Check 1 mode change only). Out of scope: `website/` (all of it, including `sw.js`), `src/`, `apps/`, `games/`, schedule, noon, `pending-post.txt`, every Story 112 surface, FPS probe. Any diff there fails this plan.

## Checks (each maps to an AC / BDD scenario)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Kai named pre-wave, opt-in mechanism recorded (Sc 1) | Dev record + script header | Kai holds `scripts/` only; opt-in is `FLAMBEEE_POST_DEPLOY=1` |
| 2 | AC-2 | RED recorded: unmodified checker exits 1 on drifted served copy (Sc 2) | Base-tree script vs drifted fixture (`FLAMBEEE_LIVE_URL` at scratch server) | Exit 1, Check 1 FAIL MISMATCH, both sha256 recorded |
| 3 | AC-3 | Default pre-merge run exits 0 with NOTE only (Sc 3) | Modified script, default mode, drifted + identical fixtures and live | Exit 0, one `NOTE:` line with both sha256, never PASS, never FAIL on Check 1 |
| 4 | AC-4 | Post-deploy mode enforces Check 1 exactly as before (Sc 4) | `FLAMBEEE_POST_DEPLOY=1` on both fixtures | Byte compare, PASS on match, FAIL plus non-zero exit on mismatch |
| 5 | AC-5 | Falsifying control exits 1 on differing bytes (Sc 5) | Post-deploy mode vs drifted fixture | Exit 1, Check 1 FAIL named |
| 6 | AC-6 | Positive control exits 0 on identical bytes (Sc 6) | Post-deploy mode vs identical fixture | Exit 0, Check 1 PASS MATCH |
| 7 | AC-7 | Freeze: zero lines outside `scripts/`, Checks 2-8 unchanged (Sc 7) | `git diff --stat` + per-check output diff old vs new | `scripts/` only; Checks 2-8 lines identical apart from Check 1 |
| 8 | AC-8 | No cut claimed (release implication) | Dev record + story | v0.41.0 decision stays with Story 112 green + release wave |
| 9 | AC-9 | Script copy tone | grep diff for em dash / heavy emoji | 0 em dashes, no heavy emoji |
| 10 | Neg | Unreachable live copy in default mode is NOTE, not FAIL | Point `FLAMBEEE_LIVE_URL` at a closed port, default mode | NOTE line, exit decided by Checks 2-8 (not forced FAIL) |
| 11 | Edge | Default reachable fetch keeps the HTTP 200 precondition line | Default mode vs fixture server | `live HTTP status: 200` printed, verdict NOTE rather than PASS |

## Result (Scout independent re-run, 2026-11-01)
No browser leg (checker story by design). Own fixture servers (identical + drifted `index.html` copies), own runs of the base and modified scripts in default and post-deploy modes. Commands, exit codes, NOTE/FAIL/PASS lines, and the freeze diff in `flambeee-team/qa-results.md`.
