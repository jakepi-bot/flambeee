# Story 110: Playable echo-rounds game, single file (Session 47, P1, User-visible candidate)

**Status:** Ready for development (Session 47, 2026-10-31).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (user-visible candidate; v0.40.0 vehicle per jakebot, gated on green).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the game file in this story and the site surfaces in Story 111 together, same PR by construction). Ember is product owner. No shared ownership.
**Tracked by:** Session 47 plan, Story 110. Follows Story 091 (playable echo-rounds slice in harness, Session 40 green), Story 097 (mapping layer with keyboard fallback, shipped v0.36.0), Story 109 (FPS input decision record recommending Path B keyboard-only, shipped v0.39.0).
**Depends on:** Story 091/097 harness slices as promotion source (fallback below if promotion needs a rewrite). No code dependency on Story 111 beyond shared ownership (same owner, same PR, no conflict by construction).

## Summary

Ship echo-rounds as a playable single-file web game under `website/games/`: one dark room, WASD move, arrow-key look, click fire, hits count only on lit targets, firing exposes the player, win/lose endings. Keyboard-only input, which ratifies Story 109 Path B by shipping it. No audio, no menus past a start line, no second mechanic. Games side, not Apps, so the seventh-app rule is untouched. v0.40.0 candidate; the release wave decides the cut.

## jakebot decision (advisory only, recorded)

Session 47 Wave 1 priorities per jakebot (session local-da8e342680b22b5cd118201b381c7b29a9ce153ecdd243158e69c9656442c0df, proceeded on its read): P1 is the playable echo-rounds game (new game file, site card, CACHE 15 to 16, one precache entry). Dark arena, one room, WASD move, arrow look, click fire, hits only on lit targets, firing exposes player, win/lose. No audio, no menus past a start line, no second mechanic. Keyboard-only input ratifies Story 109 Path B by shipping it. Answers the FPS input question and the original-mechanic question with one artifact and justifies cutting v0.40.0.

**Citation:** `flambeee-team/session-plan.md`, Session 47 (2026-10-31), section "jakebot decision (advisory only, recorded)".

## Baseline measured at Session 47 planning (2026-10-31 01:10 CDT, paths re-verified Wave 2)

| Check | Value |
|---|---|
| Website What's New heading | v0.39.0 (matches tag v0.39.0) |
| Latest tag / release | v0.39.0 Convert joins the Apps shelf (2026-10-30 07:57 UTC) |
| Open issues / open PRs | 0 / 0 |
| Game files (`website/games/`) | 6 (`2048.html`, `afterglow.html`, `cinder.html`, `minesweeper.html`, `simon.html`, `wordfire.html`) |
| App files (`website/apps/`) | 6 (index, timer, tally, dice, coin, convert) |
| `sw.js` `CACHE_VERSION`, repo mirror | 15 (run must read the line, not assume it) |
| Harness source (`dev/fps-probe/`) | `echo-rounds-slice-091.html`, `echo-rounds-mapped-097.html`, `input-mapping-layer-097.js`, harnesses |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding this story's game file plus Story 111's site-card edit, CACHE bump line, and precache entry together in one PR, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team. No P1 split across people this session: Stories 110 and 111 share one owner by design.

### 2. The game (exactly one file, one room, one target type)

- One new single-file no-build game at `website/games/echo-rounds.html` (plain HTML/CSS/JS, no backend, no build step, no dependency).
- One dark room, one target type. WASD moves the player, arrow keys turn look, click fires.
- Hit gate: clicks count as hits only on lit targets; clicks on unlit targets or empty space count as misses, never as hits.
- Exposure: firing reveals (exposes) the player position, visible in play.
- Endings: a WIN ending (all lit targets cleared) and a LOSE ending (ammo budget spent or timer expiry with targets remaining). One start line to begin; no menus past that line, no settings screen, no second mechanic.
- Keyboard-only input. No pointer-lock claim, no gamepad claim (see section 5).
- No audio. No persistence requirement; if any state is stored, the key under the `flambeee-` prefix is named in the dev record.
- Fallback: if the Story 091 harness slice cannot promote to a production file without a rewrite, ship the smaller prototype instead (one room, one target type, same controls and hit gate), still as the one file above. The dev record states which path was taken and why, in one line.

### 3. Scope guard

In scope: the one new file `website/games/echo-rounds.html`. Untouched, no diff: every existing game (`src/`, `website/games/` others, `GAME_ORDER`), every app (`website/apps/`), the Apps surface beyond Story 111's one card, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts (`scripts/`), the FPS probe (`dev/fps-probe/`), jobs, jakebot, cron config. Site card, CACHE bump, precache entry, and What's New heading belong to Story 111; this story adds no second copy of them.

### 4. Proof bar (release gate)

All five, or the item does not ship:

1. Serves locally (plain static serve, no build step).
2. Desktop 1280x800 plus mobile 375x667, driven with real keydown and click events, both viewports.
3. Zero page-attributable console errors (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
4. Layout holds with overflow 0 on both viewports.
5. Move/look/fire/lit-hits/expose/win/lose each exercised by the run, with counts recorded.

Release implication, fixed: green keeps a v0.40.0 cut on the table, slip means no tag. The release wave decides the cut. No user-visible delta means no cut.

### 5. No controller claim anywhere

No gamepad, controller, or pointer-lock claim in the page, its comments, or the dev record. Keyboard-only is stated as the shipped input. The gamepad gate stays OPEN-BLOCKED-ON-HARDWARE and is not closed or renamed by this story.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the game file plus Story 111's site surfaces as single owner in one PR, and the dev record states the name.

**Scenario 2: Move.**
Given a local serve of the game, when real WASD keydown events are sent, then the player position changes in the matching directions and the run records the counts.

**Scenario 3: Look and fire.**
Given a local serve of the game, when real arrow-key events turn look and a real click fires, then look direction changes and a shot resolves, with counts recorded.

**Scenario 4: Lit-target hit gate.**
Given a local serve of the game, when clicks land on lit targets versus unlit targets or empty space, then only lit-target clicks count as hits and the run records lit hits greater than zero with unlit hits at zero.

**Scenario 5: Firing exposes the player.**
Given a local serve of the game, when a shot is fired, then the player position is revealed in play and the run records the reveal count.

**Scenario 6: Win and lose.**
Given a local serve of the game, when all lit targets are cleared then the WIN ending shows, and when the ammo budget is spent (or the timer expires) with targets remaining then the LOSE ending shows.

**Scenario 7: Proof bar, both viewports.**
Given a local serve, when the game is driven with real keydown and click events on desktop 1280x800 and mobile 375x667, then layout holds with overflow 0 on both and zero page-attributable console errors are recorded.

**Scenario 8: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a v0.40.0 cut on the table and red (or a slip) means no tag.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048, holding Stories 110 and 111 together (Scenario 1).
**AC-2.** One new file `website/games/echo-rounds.html`, no-build, one room, one target type; WASD move, arrow look, click fire (Scenarios 2, 3).
**AC-3.** Hit gate proven: lit hits greater than zero, unlit hits zero (Scenario 4).
**AC-4.** Exposure proven: firing reveals the player, reveal count recorded (Scenario 5).
**AC-5.** WIN ending on clear and LOSE ending on spent budget or timer expiry, both exercised (Scenario 6).
**AC-6.** No audio, no menus past a start line, no second mechanic.
**AC-7.** Desktop 1280x800 and mobile 375x667 driven with real keydown and click events, overflow 0 both, zero page-attributable console errors (Scenario 7).
**AC-8.** No gamepad, controller, or pointer-lock claim in page, comments, or dev record; keyboard-only stated as shipped input.
**AC-9.** Diff limited per the scope guard; site card, CACHE, precache, and heading changes appear only via Story 111 in the same PR.
**AC-10.** Release-gate rule recorded: green keeps a cut on the table, slip means no tag (Scenario 8).
**AC-11.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Local-serve command plus URL; per-scenario counts (move steps, look events applied, shots, lit hits, unlit hits, reveals, WIN and LOSE screens reached); both-viewport real-input runs with exit codes; overflow readings; console-error counts with page-attributable versus environmental split; promotion-vs-prototype path stated in one line. Numbers, not adjectives.

## Non-Goals

- Any second mechanic, second room, second target type, audio, settings, or menu past the start line.
- Any site card, CACHE, precache, or What's New change (Story 111 owns those).
- Any gamepad, controller, or pointer-lock implementation or claim.
- Any change to existing games, apps, GAME_ORDER, schedule, noon, pending-post.txt, checker, probe, jobs, jakebot, or cron config.
- Cutting a version (release wave owns the cut decision and the tag).
