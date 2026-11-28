# Story 175: live-site smoke harness (Session 75, P0b)

**Status:** Ready for development (Session 75, 2026-11-28).
**Author:** Quinn, Business Analyst.
**Priority:** P0b (cut after 176; cut entire if 174 needs the wave).
**Assigned to:** **Riven**, sole code owner.
**Files touched:** new `dev/site-smoke.py` only. Zero website bytes.
**Depends on:** `flambeee-team/design-handoff.md` Section 2 (Session 75); served tree at `https://flambeee.com` plus repo `website/` as oracle; newest local tag via `git tag --sort=-v:refname`.

## Context

Yesterday's outage proved the public copy can go dark while the container looks healthy, and only a human reading a log noticed after about 24 hours.
The release wave needs one command that proves the deployed copy is the repo copy on all 19 pages with clean browser consoles before anything is announced.
This story builds that harness with static, desktop browser, and mobile legs plus a RED fixture that proves it can fail.

## Functional requirements

FR-1 (static leg). All 19 pages (1 hub `index.html`, 12 game files, `apps/index.html` plus 5 apps): HTTP 200 with content type containing `text/html`. Every `href="games/*.html"` and `href="apps/*.html"` in the served hub resolves 200. All 25 precache entries parsed at runtime from served `sw.js` resolve 200. Served `CACHE_VERSION` equals the repo value (37 today). Served `index.html` byte-identical to repo `website/index.html` via sha256. Served hub heading names the newest local tag.
FR-2 (desktop browser). Headless Chromium at 1280x800, one page at a time, `wait_until=load`: 0 console errors and 0 page errors per page, plus per-page anchors. Hub: non-empty `h1`. Each game: its per-game anchor from the table in design-handoff Section 2.1a and decision 012 (amended 2026-11-28 on the jakebot ruling), visible as defined there, AND a non-empty title; a game absent from the table FAILS. `apps/index.html`: non-empty `h1` AND (`input` OR `button`). Each app: `input` OR `button`. One miss fails the page.
FR-3 (mobile browser). Viewport 375x667 over the hub plus exactly 3 sampled games (`trace.html`, `2048.html`, `wordfire.html`, named constants, never random): 0 console errors, 0 page errors, and no horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`).
FR-4 (modes and cleanup). `--base` defaults to `https://flambeee.com`; `--local` serves `website/` on 127.0.0.1 with a free port from a fixed range; `--pages` subset filter prints subset counts and can never print bare PASS. Cleanup kills only the spawned PID, never `ps -C` or bare `pkill`; an exhausted range exits RED 2. Exactly 1 retry per page on navigation timeout only; errors and assertions never retry.
FR-5 (verdict). Print `PAGES x/19 STATIC ... BROWSER y/19 MOBILE z/4` with a `FAILING: <url, leg, reason>` line per miss; PASS only on full green. A partial run can never print PASS. Playwright absent means a loud `SKIPPED: browser leg (...)` line with STATIC still gating and exit 3. Exit discipline: 0 PASS, 1 FAIL, 2 RED, 3 SKIP.
FR-6 (counts are absolute). 19/19 pages, 25/25 precache, 0 errors per page; one miss fails the run. The 5-app-link assertion lives on the hub, which carries all six `apps/*.html` links; `website/apps/index.html` is Day Pad and carries no app-link assertion.

## Acceptance criteria (BDD, contract 2.7 verbatim)

1. Given the public base serving the current tree, when the harness runs full, then it exits 0 printing `PAGES 19/19`, `BROWSER 19/19`, `MOBILE 4/4`, and names CACHE_VERSION 37.
2. Given `--local`, when the harness runs, then it exits 0 against `http://127.0.0.1:<port>` and no foreign process is killed.
3. Given `--red-anchor` (fixture base missing one game file, loopback only), when the harness runs, then it exits 2 naming the missing file.
4. Given Playwright absent, when the harness runs, then STATIC still gates, stdout carries a loud SKIPPED line, and the exit is 3.
5. Given a page emitting one console error (injected fixture), when the harness runs, then that page FAILs, no retry forgives it, and the verdict is not PASS.
6. Given a navigation timeout on first attempt then success (stubbed), when the harness runs, then the page passes with exactly 1 retry recorded.
7. Given `--pages trace.html`, when the harness runs, then only that page is exercised and the verdict line names the subset.

## Out of scope

OUT OF SCOPE: zero website bytes (the release rejects any); no screenshots, no pixel comparison, anchors only; `wait_until` is `load`, never `networkidle`; no random mobile sample; no deploy hook (named follow-up only).

## Proof required in the dev record

PROOF: paste the full-run verdict line against the public base and against `--local` (pages, failing counts, exit code), plus the `--red-anchor` exit-2 line naming `games/simon.html` and the Playwright-absent SKIP line where applicable.

## Notes

Normative source is contract Section 2 (2.1 states and transitions, 2.2 formulas, 2.3 tuning, 2.4 edge cases, 2.5 failure modes, 2.6 Plan B, 2.7 BDD, 2.8 rationale) with reading choice 3 at the top (app-link assertion on the hub, not the apps index).
RED fixture is a scratch copy of `website/` minus `games/simon.html` served by the `--local` mechanics, STATIC leg only, deterministic, no external network.
Plan B: if Chromium cannot run, STATIC still gates and browser legs SKIP loudly with exit 3; slowness is fixed with longer `NAV_TIMEOUT_MS` within range, never with fewer pages.
