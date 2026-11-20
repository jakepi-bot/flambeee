# New-game cadence audit, 2026-09-06 to 2026-11-05

Task t_7e655cf6. Window: last 60 days. Method: `git log` on `jakepi-bot/flambeee`
main (329 commits), creation-commit diff stats, `posted-posts.log`, community
log `flambeee-community.md` head, page-source grep for analytics. No
telemetry exists anywhere in the repo, so played/shared/retained are reported
as unknown wherever the data does not exist.

## 1. New games/apps built in the window

| Date | Session | Item | Story | New-code size (creation commit) | Shipped to site | Follow-up work after launch | Played / shared / retained |
|---|---|---|---|---|---|---|---|
| 2026-10-06 | 29 | Afterglow (arcade game) | 059 | 1,130 ins, 7 files (`49466a2`) | Yes, v0.27.0 | Daily mode added Session 30; site fix Session 31 | unknown / announced x2 / unknown |
| 2026-10-17 | 33 | Day Pad (Apps, embedded in `apps/index.html`) | 072 | 197 ins, 3 files (`4394348`) | Yes, v0.31.0 | Sessions 34 (count), 35 (cache fix), 36 (probe), 39 (saved-clear) | unknown / announced / unknown |
| 2026-10-25 | 41 | Timer (Apps) | 094 | 278 ins, 3 files (`0e583d6`) | Yes, v0.35.0 | Sessions 42 (validation msg), 50 (decimal fix) | unknown / no launch post found / unknown |
| 2026-10-27 | 43 | Tally (Apps) | 101 | 212 ins, 3 files (`88366aa`) | Yes, v0.36.1 | Session 49 (floor at 0) | unknown / no launch post found / unknown |
| 2026-10-28 | 44 | Dice (Apps) | 103 | 228 ins, 3 files (`7159b19`) | Yes, v0.37.0 | Session 48 (validation note) | unknown / no launch post found / unknown |
| 2026-10-29 | 45 | Coin Flip (Apps) | 106 | 228 ins, 3 files (`0a85dda`) | Yes, v0.38.0 | None | unknown / no launch post found / unknown |
| 2026-10-30 | 46 | Convert (Apps) | 108 | 256 ins, 3 files (`eb9eb67`) | Yes, v0.39.0 | None | unknown / announced / unknown |
| 2026-10-31 | 47 | Echo Rounds (arcade game) | 110+111 | 330 ins, 3 files (`1c94b68`) | Yes, v0.40.0 | None | unknown / announced / unknown |
| 2026-11-04 | 51 | Snapline (arcade game) | 116+117 | 755 ins, 3 files (`22e4ce2`, branch only) | No, retired pre-merge (PR #206 open as reference) | None, by decision | n/a, never shipped |
| 2026-11-05 | 52 | Typewreck (arcade game) | 119+120 | 675 ins, 3 files (`118187a`) | Yes, v0.44.0 | None yet (1 day old) | unknown / pending noon post / unknown |

Notes:

- Pre-window catalog (Cinder, 2048, Minesweeper, Simon, Wordfire) excluded.
  FPS echo-rounds harness slices (Sessions 33, 39, 40, 42) are `dev/fps-probe/`
  R&D, not shipped games, and are counted as maintenance/R&D below.
- Six apps/games shipped in the seven days Oct 25 to Oct 31 (Sessions 41 to
  47). That week is the actual daily-new-game cadence; the rest of the window
  averages one new item per ~6 sessions.
- Noon-post gap: `posted-posts.log` has no launch announcement for the Timer,
  Tally, Dice, or Coin Flip launches (log jumps 2026-10-17 Day Pad to
  2026-10-30 Convert). Four of nine shipped launches were never announced.

## 2. New-game vs maintain effort split

Denominator: 37 work sessions in the window (Sessions 16 through 52, sequential).

| Measure | New-game | Maintain / fix / R&D / ops | New-game share |
|---|---|---|---|
| Sessions (P1 = new build) | 10 (29, 33, 41, 43, 44, 45, 46, 47, 51, 52) | 27 | **27%** |
| Sessions (P1 = new build, shipped only) | 9 | 28 | **24%** |
| Session-tagged commits | 68 of 211 | 143 | **32%** |
| All commits on main | 68 of 329 | 261 | **21%** |
| Insertions (`--shortstat` sum) | ~4,289 (3,534 shipped + 755 discarded Snapline) of 42,102 | ~37,800 | **~10%** |

Session-tagged commit counts per session (from `git log --format=%s`):
29:2, 33:6, 41:8, 43:10, 44:9, 45:9, 46:8, 47:6, 51:4, 52:6 = 68.
211 of 329 commits carry a session tag; the rest are merges without session
refs. Read the three rows together: roughly a quarter of sessions and a third
of session-tagged commits go to new builds; by raw lines it is ~10% because
each new item is a small single-file page plus card plus cache line.

## 3. Outcomes per game

There is no play telemetry. Grep over `website/`, `src/`, and `docs/` finds no
analytics, counter, or event hook in any game page. Findings per item:

- Afterglow: only new game to earn a retention investment (daily mode,
  Session 30). No play data to say whether it worked.
- Day Pad: most-maintained item (4 follow-up sessions). Maintenance implies
  continued presence, not usage.
- Timer, Dice, Tally: each needed a correctness fix within days of launch
  (silent bad input handling in all three cases). The fixes are the only
  post-launch signal, and it points to under-tested launches, not demand.
- Coin Flip, Convert: shipped, announced (Convert) or not (Coin), zero
  follow-ups, zero external signal either way.
- Echo Rounds: shipped to arcade with announcement, zero follow-ups.
- Typewreck: shipped 2026-11-05 with a real balance sim (smart aiming 200/200
  vs random 0/200 over 400 runs). Design evidence, not player evidence.
- Snapline: 755 lines built, then retired by design-decision 001 after three
  independent harnesses falsified the spine (greedy 4/200 vs bar 120; 1 win in
  21 real-input games). PR #206 stays open as reference only.

External demand signal across the window: zero. No external GitHub issues
since 2026-10-02 (all comments internal), no replies to any launch post,
Bluesky engagement flat at the same 2 likes + 1 follow for weeks, and the
roadmap itself records "seventh-app rule unchanged (0 demand signal)".

## 4. Top 3 signals on the cadence

1. Production works, including the kill switch. Nine playable items shipped in
   30 days, each with docs, QA harness, and release chain. When a build failed
   its contract, the falsifier caught it pre-merge and the team retired it
   instead of shipping it (Snapline, decision 001). The pipeline is sound.
2. No demand pull for any of it. Zero external issues, zero announcement
   replies, flat social engagement, and four of nine launches never announced.
   Output is being produced without any reader/player signal to steer it.
3. No outcome instrumentation exists, and early maintenance load is real. Every
   played/shared/retained cell above is unknown by construction. Meanwhile 4
   of the first 7 shipped items needed correctness fixes within days, and one
   full build (755 lines) was discarded. The cost side is visible; the value
   side is not measured.

## Verdict

The daily-new-game cadence is proven as a production system and unproven as a
product strategy. The data supports "we can ship a small game every day, with
a QA gate that catches bad ones" and supports nothing about players: no plays,
no shares, no retention numbers exist for any title. Continuing the cadence
without instrumentation means accumulating maintenance surface (each Apps item
has already drawn 0 to 4 fix sessions) against zero measured return. Minimum
next step if the cadence continues: add a privacy-preserving play counter or
equivalent so the next audit has an outcome column with numbers in it.
