# Legacy games and apps maintenance audit

Date: 2026-11-05. Head: `9fcbe15` on `main` (v0.44.0, Session 52).
Scope: every shipped item under `website/games/` and `website/apps/`.
Method: file history (`git log --follow`), release records (`docs/roadmap.md`),
open/closed issues and PRs (`gh`), dependency scan (script/link grep),
deprecated-API scan, telemetry scan, service-worker precache list.
Live-site reachability could NOT be checked from this box: the served copy
(`~/share/Flambeee/`, Jake's Caddy sync target) is absent here, and the
currency checker's live leg is post-deploy-only since Story 113. Health below
is therefore inferred from precache membership + per-release QA verdicts +
issue tracker state, and that limitation is stated per row where it matters.

## Headline facts

- 14 shipped items: 8 games, 6 apps. All static single files, no build step.
- Zero external JS/CSS dependencies repo-wide. The only non-footer outbound
  references are footer links (github, bsky) and one local data file
  (`wordfire-words.js`). No CDN, no npm, no framework to rot.
- Zero deprecated-API hits. One `webkitAudioContext` occurrence is the
  standard `window.AudioContext || window.webkitAudioContext` fallback in
  `simon.html:432`, not a deprecated dependency.
- Zero telemetry: no analytics, no fetch/XHR/beacon in any game or app.
  The only `fetch` in the tree is the service worker's same-origin
  cache-first handler. Consequence: there is no usage data anywhere, so the
  value column below rates strategic signals (originality, daily hooks,
  rotation slots), not measured traffic. That is an assumption, stated here.
- Zero open issues (5 closed total, all pre-September or September-era) and
  zero open PRs against any shipped file. Open PRs are #206 Snapline
  (unmerged new game, not legacy) and #208 Ember prompts (tooling).
- Every shipped item is in the SW precache (`CACHE_VERSION = 20`, 21 URLs:
  shell + 8 games + words.js + 6 app pages). Nothing ships outside the cache.
- Per-change shared tax (not per-item cost): any edit to a precached file
  needs a `CACHE_VERSION` bump + What's New line + release cut, owned by the
  release wave. This is the only recurring mechanism cost and it is flat.

## Per-item table

Sizes are current `website/` bytes; LOC is `wc -l`. Ship = first release
carrying the item (roadmap + first-commit date). Churn = commit count on the
`website/` path. Last touch = newest commit touching the file.

| Item | File | Shipped | Size | Deployed/hosted | Health | Open bugs / crash logs | Deps / deprecated APIs | Last touch / churn | Recurring cost | Value | Cost vs value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Minesweeper | `games/minesweeper.html` | v0.1.0, 2026-07-28 | 786 lines, 21 KB | Static file, precached, flambeee.com via Caddy sync | QA-green at ship; untouched since 2026-10-15 deploy-root migration | None (0 open repo-wide) | None; vanilla DOM + localStorage (`flambeee-stats-minesweeper`) | 2026-10-15 (migration) / 7 commits | ~0 hr/mo baseline; episodic fix historically one single-file story (~0.5-1 hr one time) | Medium: classic, Game-of-the-Week rotation slot | Keep. Cost ~0, value steady. |
| Simon | `games/simon.html` | 2026-07-31 | 605 lines, 15 KB | Static file, precached, flambeee.com via Caddy sync | QA-green at ship; untouched since 2026-10-15 | None | WebAudio via standard fallback (`AudioContext \|\| webkitAudioContext`); localStorage (`flambeee-simon-best`, `-difficulty`, `-stats-simon`) | 2026-10-15 / 5 commits | ~0 hr/mo baseline | Medium: classic, GOTW rotation slot | Keep. Cost ~0, value steady. |
| 2048 | `games/2048.html` | v0.3.0, 2026-08-04 | 454 lines, 14 KB | Static file, precached, flambeee.com via Caddy sync | QA-green at ship; 1 closed mobile-scroll issue (#12, fixed Aug 7); untouched since 2026-10-15 | None | None; localStorage (`flambeee-2048-best`, `-size`, `flambeee-stats-2048`) | 2026-10-15 / 4 commits | ~0 hr/mo baseline | Medium: classic, GOTW rotation slot | Keep. Cost ~0, value steady. |
| Wordfire | `games/wordfire.html` + `games/wordfire-words.js` | v0.6.0, 2026-08-11 | 1093 lines + word list (8 lines, 58 KB asset), 34 KB + 58 KB | Static files, both precached, flambeee.com via Caddy sync | QA-green; 1 closed mobile issue (#26, fixed Aug 14); daily + hard + colorblind modes added since | None | None (local word list, no network); localStorage family (`flambeee-wordfire-*`, ~10 keys) | 2026-10-15 / 6 + 3 commits | ~0 hr/mo baseline; word list is static (no daily fetch to maintain) | High: daily word + hard mode + colorblind mode, Play-today slot, GOTW slot | Keep. Highest value-per-line among clones. |
| Cinder | `games/cinder.html` | v0.13.0, 2026-08-30 (Stories 018+019) | 1754 lines, 78 KB (largest single file) | Static file, precached, flambeee.com via Caddy sync | QA-green; 2 closed issues (#45, #46, Sep 1); 8 dedicated releases v0.15.0-v0.26.0 + v0.29.0 (Sep-Oct) then quiet since 2026-10-15 | None | None; localStorage (`flambeee-cinder-day`, `-save`) + quest/streak records | 2026-10-15 / 23 commits (highest churn) | ~0 hr/mo baseline now; historically the costliest item (~1 release/6 days across Sep to mid-Oct, each a defect/polish story at ~1-2 hrs one time). Regression risk on future edits is the highest in the tree (deepest state logic: day records, quest log, streaks, boss days, badge) | High: flagship original (BBS text RPG, CEO-directive-6 compliant), daily quest, Play-today slot, GOTW slot | Keep. Past cost was real but is sunk and quiet; future edits deserve the most QA of any file. |
| Afterglow | `games/afterglow.html` | v0.27.0, 2026-10-06 (daily mode v0.28.0, 2026-10-11) | 657 lines, 24 KB | Static file, precached, flambeee.com via Caddy sync | QA-green (39/39 Playwright at ship + daily-mode harness); pure-logic `AFTERGLOW-PURE` block has dedicated proof harnesses (`dev/afterglow-*.py`); untouched since 2026-10-15 | None | None; localStorage (`flambeee-afterglow-stats`, `-daily-stats`) | 2026-10-15 / 3 commits | ~0 hr/mo baseline; cheapest original to verify (pure block + harnesses exist) | High: original mechanic (disjoint see/move windows), daily UTC-seeded mode, GOTW slot | Keep. Best originality-to-cost ratio. |
| Echo Rounds | `games/echo-rounds.html` | v0.40.0, 2026-10-31 (Stories 110+111) | 321 lines, 12 KB (smallest game) | Static file, precached, flambeee.com via Caddy sync | QA-green (11/11 + 12/12 at ship). Shipped explicitly as a prototype ("shipped, not a promotion"); keyboard-only; no audio, no persistence | None | None; no storage keys | 2026-10-31 / 1 commit | ~0 hr/mo (1 commit ever) | Low-medium: playable but thin; NOT in `GAME_ORDER` rotation (rotation stays 6, roadmap-confirmed); FPS-probe lineage continues under `dev/fps-probe/`, not in this file | Keep for now, do not extend. If the FPS web build lands, this file is superseded; if FPS goes native, revisit whether a keyboard-only prototype earns its card. |
| Typewreck | `games/typewreck.html` | v0.44.0, 2026-11-05 (Stories 119+120) | 666 lines, 24 KB | Static file, precached, flambeee.com via Caddy sync | QA-green (42/42 desktop + 7/7 mobile + 12/12 balance at ship, 1 day ago) | None | None; localStorage (`flambeee-typewreck-best`) | 2026-11-05 / 1 commit | ~0 hr/mo (too new to have a cost history) | Unrated yet: original (paste-to-fortress), but NOT in `GAME_ORDER` rotation and 1 day old | Keep, re-evaluate after one month of issue signal (or silence). |
| Day Pad | `apps/index.html` | v0.31.0, 2026-10-17 (Story 072) | 185 lines, 6 KB (smallest item) | Static file, precached, flambeee.com via Caddy sync | Most-validated app: day-1/2/3 reuse probes (Stories 075/077/079/081), stale-serve cache fix v0.33.0, save-clear v0.34.0; all green | None | None; localStorage (`flambeee-apps-daypad-note`, prefix `flambeee-apps-`) | 2026-10-23 (Story 088) / 3 commits | ~0 hr/mo baseline | Medium-high: first app, proven multi-day retention mechanic | Keep. Validation cost already paid. |
| Timer | `apps/timer.html` | v0.35.0, 2026-10-25 (Story 094) | 312 lines, 10 KB | Static file, precached, flambeee.com via Caddy sync | QA-green; 3 follow-up polish stories (098 validation msg, 100 cache fix, 115 decimal/paused guards), all green | None | None; localStorage (`flambeee-apps-timer`) | 2026-11-03 (Story 115) / 3 commits | ~0 hr/mo baseline; most-polished app (3 post-ship stories, each ~0.5 hr one time) | Medium: utility, deepest-validated input handling of the six apps | Keep. Polish cost paid, now quiet. |
| Tally | `apps/tally.html` | v0.36.1, 2026-10-27 (Story 101) | 219 lines, 7 KB | Static file, precached, flambeee.com via Caddy sync | QA-green; floor-at-0 fix v0.42.0 (Story 114) | None | None; localStorage (`flambeee-apps-tally`) | 2026-11-02 (Story 114) / 2 commits | ~0 hr/mo baseline | Low-medium: simplest utility; roadmap notes "weakest measured app" at Story 114 time, since fixed | Keep. Trivial size, zero ongoing cost. |
| Dice | `apps/dice.html` | v0.37.0, 2026-10-28 (Story 103) | 224 lines, 7 KB | Static file, precached, flambeee.com via Caddy sync | QA-green; validation-note polish v0.41.0 (Story 112) | None | None; localStorage (`flambeee-apps-dice`) | 2026-11-01 (Story 112) / 3 commits | ~0 hr/mo baseline | Low-medium: utility shelf-filler | Keep. Trivial size, zero ongoing cost. |
| Coin Flip | `apps/coin.html` | v0.38.0, 2026-10-29 (Story 106) | 219 lines, 6 KB | Static file, precached, flambeee.com via Caddy sync | QA-green, no post-ship fixes needed | None | None; localStorage (`flambeee-apps-coin`) | 2026-10-29 / 3 commits | ~0 hr/mo | Low-medium: utility shelf-filler, cleanest ship (no follow-ups) | Keep. |
| Convert | `apps/convert.html` | v0.39.0, 2026-10-30 (Story 108) | 247 lines, 8 KB | Static file, precached, flambeee.com via Caddy sync | QA-green, no post-ship fixes needed | None | None; conversion table is inline (11 pairs, no network) | 2026-10-30 / 1 commit | ~0 hr/mo | Low-medium: utility shelf-filler, cleanest ship | Keep. |

## Dead weight vs keep

No shipped item is dead weight: all 14 are precached, QA-green, dependency-free,
and cost ~0 at steady state. The actual dead weight is all unshipped:

- `src/*.html` (2048, afterglow, cinder, minesweeper, simon, wordfire copies,
  frozen 2026-10-18): superseded by `website/` as deploy root since Session 31
  (v0.30.0-era migration; last global sync 2026-10-15). Nothing reads them.
  Recommend: delete or archive in one cleanup story. Risk of keeping: future
  editors fix the wrong copy.
- `wordpress/home-mockup.html`: pre-ship design artifact, never deployed.
  Recommend: archive or delete.
- `dev/` proof scripts, `dev/fps-probe/`, `scripts/verify-website-currency.sh`:
  tooling, not product. Keep.
- In-flight, not legacy: PR #206 Snapline (Stories 116+117, unmerged new game).
  Out of scope for this audit; flagged only so it is not mistaken for shipped.

## Cost rollup and recommendation

- Steady-state legacy cost across all 14 items: ~0 hr/mo, bounded above by
  ~5-10% of one daily session in weeks where a polish story lands (evidence:
  the last 3 weeks shipped 4 legacy-polish stories: 112 dice, 114 tally,
  115 timer, plus cache-fix 100; each fit inside its session alongside new work).
- The only item with significant historical cost is Cinder (23 commits, ~8
  dedicated releases). That cost is sunk and the file is quiet since Oct 15.
- The binding constraint on new-game cadence is not legacy maintenance (there
  is almost none) but the per-release shared tax (CACHE bump, What's New,
  release cut, noon post) plus QA capacity per new file. Slowing new games
  does not reduce legacy cost meaningfully, because legacy cost is already ~0.
  Recommendation: keep all 14 shipped items; delete/archive `src/` duplicates
  and the wordpress mockup; admit Echo Rounds and Typewreck to the
  Game-of-the-Week rotation or record why they stay out; re-run this audit
  only when an item gets its first open bug or its first dependency.
