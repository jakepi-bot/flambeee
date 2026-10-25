# Test Plan: Story 094 Countdown Timer Build (Session 41, P1)

Source: `docs/stories/094-timer-build-session41.md` (Quinn, Wave 2).
PR under test: https://github.com/jakepi-bot/flambeee/pull/165
(head `feat/session41-094-timer`, base `main` at `e67895f`).
QA: Scout. Written 2026-10-25 (Session 41 Wave 3).

Scope: user-visible build. Verify only; QA fixes nothing. Diff must be
`website/apps/timer.html` (new) plus one site card in `website/index.html`
plus one `CACHE_VERSION` line in `website/sw.js`.

## Setup

- PR head in isolated worktree
  `/home/jake/.hermes/profiles/flambeee/cache/scratch/wt-pr165`
  (head `0e583d6`); shared checkout stays on `main`.
- Serve: `python3 -m http.server <port> --directory website` from the
  PR worktree. No build step.
- Drive with Playwright + system Chromium, headless (no X server on this
  box; same Chromium binary, real typed input and real clicks).
  Record the headless substitution in results.
- Base `e67895f` used for noise reproduction and CACHE 10 read.

## Cases (story BDD 1-8 / AC-1..AC-9)

1. T1 Owner check (AC-1, Scenario 1). Dev record names one code owner
   holding all three paths. PASS if `flambeee-team/dev-results.md`
   (Kai section) names Kai sole owner and Riven makes zero edits to
   those paths.
2. T2 Candidate fidelity (AC-2, Scenario 2). Page has one duration
   input, Start/Pause toggle, Reset, MM:SS display, one label line,
   localStorage-only under `flambeee-apps-` with key recorded
   (`flambeee-apps-timer`). No second feature. PASS on element presence
   plus key read.
3. T3 Scope guard (AC-3, Scenario 3). `gh pr diff 165` file list is
   exactly `website/apps/timer.html`, `website/index.html`,
   `website/sw.js`. Day Pad, games, schedule, noon, checkers,
   `pending-post.txt` show no diff. PASS on file list plus stat
   (+271 new, +6 card, +1/-1 CACHE).
4. T4 Desktop proof (AC-4, Scenario 4). Serve, viewport 1280x800, type
   minutes + label, click Start (display counts), Pause (display stable
   across reads), Reset (back to duration, label shown). Record console
   errors split page-attributable vs environmental; reproduce any noise
   on base. PASS on behave + zero page-attributable errors.
5. T5 Mobile proof (AC-5, Scenario 5). Same steps at 375x667. Layout
   holds, no horizontal overflow. PASS on behave + zero
   page-attributable errors.
6. T6 Cache bump (AC-6, Scenario 6). `website/sw.js` line 21 reads
   `var CACHE_VERSION = 11;` on the PR head and `= 10;` on main.
   Timer page reachable from the served tree. PASS on both reads.
7. T7 Release gate (AC-7, Scenario 7). Story records green-keeps-v0.35.0
   on the table / slip-means-no-tag / no-cut-for-card-alone. PASS on
   story text presence (lines 12, 65-73).
8. T8 jakebot citation (AC-8, Scenario 8). Story records P1, proof bar,
   no-tag-on-slip, session
   `local-a073b43383b772fe9e2d4d3cacc737b9d8fd29efca87b93dd0ca6f03df951a6c`.
   PASS on citation text (lines 14-18).
9. T9 Copy rule (AC-9). Zero em dashes (U+2014/U+2013) and no heavy
   emoji in `website/apps/timer.html` plus the card lines. PASS on
   grep exit 1 (no matches) plus eyeball read.
10. T10 Persistence (acceptance support). Reload restores minutes from
    key `flambeee-apps-timer`. PASS on value round-trip.
11. T11 Card link (proof bar item 4). Card href `apps/timer.html`
    present on the Apps surface and resolves HTTP 200 from the serve.
    PASS on grep + fetch status.

## Real output (pasted into qa-results.md)

Serve command + URL, both-viewport runs with exit codes, typed values,
display reads, console-error counts with page-attributable vs
environmental split + base reproduction, card href + fetch status,
CACHE lines before/after, diff file list + stat, localStorage key
round-trip, dash/emoji grep outputs.

## Verdict

GO only if T1-T11 all pass and noon tail (082 matrix 12/12 + mirror
checker exit 0) is green. Any non-zero tail result is a blocking defect.
