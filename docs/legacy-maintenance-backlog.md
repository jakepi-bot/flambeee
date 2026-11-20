# Legacy maintenance backlog (cadence policy queue)

Home of the top legacy maintenance items flagged by the 2026-11-05 audits.
LEGACY-day sessions (Tue/Thu/Sat/Sun per `docs/cadence-policy.md`) pull from
the top of this list. Each item is tracked as a GitHub issue with the
`maintenance` label; the issue number is recorded next to the item when opened.

Health baseline (from `docs/legacy-games-apps-audit.md`): all 14 shipped
items are static, dependency-free, precached (`CACHE_VERSION = 20`), QA-green,
with zero open issues. Steady-state cost is ~0 hr/month. These items are
improvements and risk reduction, not fires.

## M-1: Archive the `src/` duplicate game copies and the wordpress mockup

- Evidence: legacy audit section "Dead weight vs keep". `src/*.html`
  (2048, afterglow, cinder, minesweeper, simon, wordfire copies) frozen since
  2026-10-18, superseded by `website/` as deploy root since Session 31.
  Nothing reads them. `wordpress/home-mockup.html` never deployed.
- Risk if skipped: a future editor fixes the wrong copy and ships a stale
  game (silent divergence, caught only by chance).
- Acceptance: `src/*.html` game copies and `wordpress/home-mockup.html` are
  deleted or moved to an `archive/` path with a one-line README each; `grep`
  proves no live file references the old paths; site precache and QA green.
- Cost: one session, fits a LEGACY day.

## M-2: Admit Echo Rounds and Typewreck to the Game-of-the-Week rotation or record why not

- Evidence: legacy audit cost-vs-value table. Echo Rounds (v0.40.0, 321
  lines, smallest game) and Typewreck (v0.44.0, 666 lines) are shipped,
  precached, and QA-green but excluded from `GAME_ORDER` rotation (rotation
  stays 6, roadmap-confirmed for both). Typewreck is 1 day old; re-evaluate
  after one month of issue signal per the audit.
- Risk if skipped: shipped games with no discovery path accumulate as
  unplayed surface (cadence audit signal 2: output without player signal).
- Acceptance: `GAME_ORDER` includes both games with rotation evidence, or a
  design note records why each stays out (with a revisit date).
- Cost: one session for the rotation change + QA; the decision note alone is
  half a session. Do not extend Echo Rounds (prototype, keyboard-only) as part
  of this item; promotion to full game is a separate NEW-GAME-day proposal.

## M-3: Privacy-preserving play counter on game pages

- Evidence: cadence audit verdict, "minimum next step if the cadence
  continues". Every played/shared/retained cell in the audit is unknown by
  construction: no analytics, counter, or event hook exists in any game page
  (only the service worker's same-origin cache fetch). Four of nine recent
  launches have no measurable outcome at all.
- Constraint: zero friction and privacy (culture.md, no PII). Counter must be
  on-device first: per-game plays/wins persisted in the existing
  `flambeee-*` localStorage key family and surfaced in the game detail view
  (Story 015 pattern), no network, no identity. Aggregation, if ever, is a
  separate opt-in proposal.
- Acceptance: each game page increments a local play count on real session
  start and the detail view renders it; QA proves counts increment, persist
  across reload, and stay empty-state friendly for visitors with no data; no
  network call added (grep proves it). The next cadence audit can read
  per-title engagement mechanics off-device during QA sessions.
- Cost: one LEGACY-day session per game batch; start with the two originals
  (Cinder, Afterglow) where retention matters most.

## M-4: Cinder edit QA bar (highest-churn file guard)

- Evidence: legacy audit. Cinder (`games/cinder.html`, 1754 lines, 78 KB) is
  the largest single file with the highest churn (23 commits, ~8 dedicated
  releases Sep to mid-Oct: day records, quest log, streaks, boss days,
  badge). Quiet since 2026-10-15, but regression risk on future edits is the
  highest in the tree (deepest state logic).
- Rule: any future Cinder edit re-runs the full harness family
  (`dev/` Cinder proofs plus quest-log/streak/boss-day checks) and records
  the run in the PR. No proof run, no merge.
- Acceptance: this rule is cited in the next Cinder-touching PR (or no
  Cinder PR lands, which also satisfies it).
- Cost: ~0 until Cinder is touched; the harness time is inside that session.

## Out of scope for this queue (recorded so they are not re-nominated)

- FPS gamepad gate (OPEN-BLOCKED-ON-HARDWARE, 16 sessions): blocked on Jake
  providing a pad on the named rig, not on session effort. Revisit only when
  hardware exists.
- Cinder offline resource accrual: decided against in Story 039; revisiting
  requires explicit CEO sign-off. Cinder cross-day streak history and
  welcome-back suppression likewise (Story 042 limitations).
- PR #206 Snapline: retired spine, open as reference only per design
  decision 001. Not legacy (never shipped); rework needs a new design that
  clears honest ballistic thresholds.
