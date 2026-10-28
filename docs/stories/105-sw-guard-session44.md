# Story 105: Service-worker guard in the currency checker (Session 44, P1b, Mechanism)

**Status:** Ready for development (Session 44, 2026-10-28).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1b (mechanism; the release-wave gate for the v0.37.0 cut. Runs alongside Story 103, same wave).
**Assigned to:** **Kai** (single owner; `scripts/` only).
**Tracked by:** Session 44 plan, Story 105. Follows Story 038 (checker), Story 100 (cache-staleness fix, shipped v0.36.1), Story 102 (HTTPS live leg, shipped v0.36.1).
**Depends on:** None. No code dependency on Story 103 or 104 except the ordering note below: this story asserts the CACHE rule, Story 103 exercises it.

## Summary

Extend `scripts/verify-website-currency.sh` with three service-worker assertions so the release gate lives in the script, not in a human's memory: the What's New heading names the newest tag, `CACHE_VERSION` changed since the last tag, and every app-card link target is present in `PRECACHE_URLS`. RED proof required on the pre-guard tree, green on the merged tree. `scripts/` only; no site edits.

## jakebot decision (advisory only, recorded)

Session 44 Wave 1 priorities per jakebot (session local-83c1f398af985ca091b172f0cd089e23eb336f49ed36e42a457088eab9b9f544, proceeded on its read): point 5, gate the release wave on the mechanism, not the prose. v0.36.1 fixed one cache bug, not the class: the bump rule existed and nothing raised it before release. A fourth app adds a shell asset, so this release needs CACHE 13 plus the new html in PRECACHE_URLS, and the checker must assert all three of heading == tag, CACHE_VERSION changed since the last tag, every app card target in PRECACHE_URLS. In the script, not in a human's memory.

**Citation:** `flambeee-team/session-plan.md`, Session 44 (2026-10-28), section "jakebot decisions (advisory only, recorded)".

## Why this story exists (one paragraph)

Story 100 proved the class: the CACHE bump rule existed since v0.33.0 and nothing enforced it before release, so v0.36.0 shipped a stale shell and v0.36.1 had to repair it. Story 103 adds another shell asset, which is exactly the shape that slips. This story puts the three assertions in the checker so the release wave reads an exit code instead of trusting prose.

## Requirements

### 1. The three assertions

The checker gains exactly three new checks, each with a pass/fail line in its output:

1. **Heading == tag.** The What's New heading names the newest tag resolved at run time (same resolution the checker already uses), or the check fails with both values printed.
2. **CACHE changed since last tag.** `CACHE_VERSION` in `website/sw.js` differs from the value at the newest tag (via `git show <tag>:website/sw.js`), or the check fails with both values printed. Rationale printed in the dev record: same version across a shell-asset change is the v0.36.0 defect shape.
3. **Every app-card target precached.** Each app-card link target on the Apps surface resolves to an entry in `PRECACHE_URLS`, or the check fails naming the missing target. At planning the three targets are `apps/index.html`, `apps/timer.html`, `apps/tally.html`; the checker reads them at run time, never hardcodes them.

Each assertion prints its measured values (heading, tag, CACHE now vs at tag, card targets vs precache entries) so a failure names the drift.

### 2. RED-then-green proof bar

- **RED:** the guarded checker run against the pre-guard tree (or against a fixture, or the v0.36.0/v0.36.1 pair) exits non-zero, proving the new assertions fire on the defect shape. The dev record pastes command, exit code, and the failing assertion line.
- **Green:** the same checker on the merged tree exits 0 with all three new lines passing. The dev record pastes command, exit code, and the three passing lines.
- Code with no RED run is not done.

### 3. Scope guard (scripts only)

In scope: `scripts/verify-website-currency.sh` plus any test fixture or harness file under `scripts/` the proof needs. Untouched: `website/` (no site edits, no sw.js edits, no card edits), `src/`, `games/`, the FPS probe, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`. Story 103 owns `website/sw.js`; this story never touches it, so no conflict by construction.

### 4. Ordering note

The dev wave lands Stories 103 and 105 in either order; neither blocks the other. The release wave runs the guarded checker post-merge as the cut gate: all three new assertions green is necessary but not sufficient for the v0.37.0 cut.

## BDD scenarios

**Scenario 1: Heading assertion fires.**
Given a tree where the What's New heading names an older version than the newest tag, when the guarded checker runs, then the heading check fails with both values printed and the exit code is non-zero.

**Scenario 2: CACHE assertion fires.**
Given a tree where `CACHE_VERSION` matches the value at the newest tag while shell surface changed (the v0.36.0/v0.36.1 pair is the reference fixture), when the guarded checker runs, then the CACHE check fails with both values printed and the exit code is non-zero.

**Scenario 3: Precache assertion fires.**
Given a tree where an app-card link target has no entry in `PRECACHE_URLS`, when the guarded checker runs, then the precache check fails naming the missing target and the exit code is non-zero.

**Scenario 4: Green on the merged tree.**
Given the merged tree, when the guarded checker runs, then all three new checks pass with measured values printed and the exit code is 0.

**Scenario 5: Scope guard.**
Given the story diff, when it is inspected, then every changed file sits under `scripts/`, and `website/`, `src/`, `games/`, and `dev/fps-probe/` show no diff.

## Acceptance Criteria

**AC-1.** Heading==tag assertion installed with both values printed on failure (Scenario 1).
**AC-2.** CACHE-changed-since-tag assertion installed with both values printed on failure (Scenario 2).
**AC-3.** App-card-targets-precached assertion installed naming the missing target on failure, targets read at run time not hardcoded (Scenario 3).
**AC-4.** RED run recorded with command, exit code, and failing assertion line (Scenarios 1-3, at least one RED shape proven; the v0.36.0/v0.36.1 pair is the suggested fixture).
**AC-5.** Green run recorded on the merged tree with command, exit code 0, and the three passing lines (Scenario 4).
**AC-6.** Diff limited to `scripts/`; no site edits (Scenario 5).
**AC-7.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

The three new assertion blocks quoted verbatim in the dev record; RED command plus exit code plus failing line; green command plus exit code 0 plus the three passing lines; `git diff --stat` showing `scripts/` only. Numbers, not adjectives.

## Non-Goals

- Any edit under `website/`, including `sw.js` (Story 103 owns it).
- Any change to the HTTPS live leg Story 102 installed (extend, do not rewrite).
- Deciding any version cut (release wave owns the cut decision and the tag).
- Touching `pending-post.txt` or any noon pipeline path.
