# Test Plan 038: Website Latest-Release Currency and Mirror Byte-Identity Verification

**Author:** Scout (QA Analyst)
**Date:** 2026-09-18 (Session 21)
**Story:** `docs/stories/038-website-currency-verification.md` (P2, 6 BDD scenarios)
**PR under test:** #79, branch `feature/038-website-currency-check` (tip `fe73150`), base `main`
**Artifact under test:** `scripts/verify-website-currency.sh` (branch copy), plus the live/mirror page pair
**Test environment:** bash checker run from branch worktree `/tmp/qa-038`; live site `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE), repo mirror `website/index.html`

---

## 1. Scope

A standing verification, not a build. It proves, every session, that the live home page's What's New box names the true latest release, describes only what that release shipped, and that the live file is byte-identical to the repo mirror. No redesign, no game code, no layout change.

## 2. Requirements-to-test map

| Req | Covered by |
|-----|-----------|
| 1 latest-version truth from `git ls-remote --tags origin` | S1 |
| 2 accurate summary, nothing invented, CEO tone | S2 |
| 3 live and mirror byte-identical (`cmp`) | S3 |
| 4 Releases and Blog are real clickable anchors | S4 |
| 5 failed check records a defect + small accuracy PR | S5 |
| 6 no regressions from a fix (re-sync, links, no layout change) | S6 |

## 3. Test cases

### TC-038-01 (S1) Heading names the true latest release
- **Given** the latest tag on `origin` is resolved live via `git ls-remote --tags origin`, sorted by version
- **When** the What's New heading is read
- **Then** it names exactly `v0.18.1`, no unreleased or newer version appears as shipped.
- **Boundary:** the local tag list must NOT be trusted (local tags can lag; the story notes the local list stopped at v0.9.0 in an earlier session).

### TC-038-02 (S2) Summary describes only what v0.18.1 shipped
- **Given** the v0.18.1 ship notes (Story 035: Quest Log, recent completed quests, current streak, read-only, no new mechanics, no balance/reward changes, history starts at ship)
- **When** the What's New summary is read and compared line by line with `BLOG.md` v0.18.1
- **Then** it says only what v0.18.1 shipped, with no invented or upcoming feature, and contains no em dashes or heavy emoji.

### TC-038-03 (S3) Live and mirror are byte-identical
- **When** `cmp /home/jake/.openclaw/workspace/share/Flambeee/index.html /home/jake/.openclaw/workspace/flambeee/website/index.html` runs
- **Then** exit 0, both 1320 lines.

### TC-038-04 (S4) Releases and Blog links are real and clickable
- **When** the What's New anchors are inspected
- **Then** both are real `<a href>` links with `target="_blank" rel="noopener"`, with no bare-text URL.

### TC-038-05 (S5) Failed accuracy check flags a defect
- **Given** a future stale heading, an invented summary, or a mirror mismatch
- **When** the checker runs
- **Then** it exits non-zero (real defect signal) and records a defect with reproduction steps, with the fix landing as a small accuracy PR on `main`.

### TC-038-06 (S6) No regressions from a fix
- **Given** an accuracy fix was applied
- **Then** live and mirror are re-synced (`cmp` passes), links still work, and no content beyond the corrected What's New text changed.

## 4. Boundary conditions and edge cases

- Version resolution: the checker parses `${latest}` in the heading rather than hardcoding v0.18.1, so it stays valid after v0.19.0 with no edits.
- Local vs origin tags: the check must use `git ls-remote --tags origin`; a stale local tag must not produce a false PASS.
- Play-link existence: all 5 `games/*.html` targets must exist under the live `games/` dir; a removed game file must fail the check.
- Tone guards: em-dash and heavy-emoji scans run on the summary itself.
- Exit code is the failure signal: any single failed check must exit non-zero.

## 5. Independent execution

The checker was run from the branch worktree `/tmp/qa-038` with `bash scripts/verify-website-currency.sh`, exit 0. The Scenario 2 semantic comparison was performed independently by extracting the `<h3>`/`<p>` block and comparing it against the v0.18.1 section of `BLOG.md`.

## 6. Exit criteria

All 6 scenarios pass with the checker exiting 0, and the summary semantically matches the v0.18.1 ship notes.
