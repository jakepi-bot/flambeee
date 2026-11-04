# Story 116: Snapline load-breaking ceiling shooter game (Session 51, P1, user-visible)

**Status:** Ready for development (Session 51, 2026-11-04).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (new game; v0.44.0 candidate, release wave decides the cut).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the game file in this story plus the Story 117 site surfaces in the same PR, so overlap is impossible by construction). No shared ownership.
**Tracked by:** Session 51 plan, Story 116. Design contract: `flambeee-team/design-handoff.md` (Rook, Session 51). Reskin gate passed, no fallback.
**Depends on:** No code dependency on any other story this session. Story 117 rides in the same PR by construction.

## Summary

Build Snapline, a load-breaking ceiling shooter, as a single file at `website/games/snapline.html` with no dependencies. The player aims from a bottom launcher and fires orbs upward into a ceiling-hung square lattice. Every fired orb sticks permanently and adds exactly one unit of load to the strand it joins. A strand detaches and scores when its orb count exceeds its anchor strength. The ceiling descends on a fixed shot clock. WIN by clearing the board. LOSE by letting any orb reach the line row or by running out of shots with orbs left. Every shot is both the threat (adds mass, advances the ceiling clock) and the cure (builds toward a snap).

Ship note (release wave uses verbatim): CEO asked for Snood; this is deliberately not Snood, it is a load-breaking shooter where every shot adds weight and strands snap when overloaded, because directive 6 forbids a reskin and only an explicit CEO override changes that.

Reskin gate (Story 068 test, passed at the doc gate): strip all art to identical gray circles with no colors and the remaining rule is load versus anchor strength on a hanging lattice. Puzzle Bobble, Bust-a-Move, and Snood clear by matching three or more of a color; color matching is absent here by construction. No named title has "add uniform mass until overloaded anchors snap" as its clearing predicate. Falsifying playtest question: with art stripped to gray orbs plus numeric strain readouts, do first-time players aim at the most-strained strand within their first ten shots; if a majority do anything else, the spine has failed and the fallback (Story 118) triggers.

First five minutes: title line plus aim hint, first shot inside ten seconds, first snap inside eight shots by aiming at the pre-strained column the seed guarantees, first failure no earlier than shot fifteen on default tuning.

## Baseline measured at Session 51 planning (2026-11-04 01:10 CST)

| Check | Value |
|---|---|
| Website What's New heading | v0.43.0 (matches tag v0.43.0) |
| `sw.js` `CACHE_VERSION`, repo mirror | 19 (run must read the line, not assume it) |
| Game files | 7 game files; `website/games/snapline.html` does not exist (RED anchor) |
| GAME_ORDER (`website/index.html`) | 6 entries, untouched by this story |
| jakebot advisory | P1 bubble-shooter-genre game with one original spine mechanic; coin/convert parity dead on measurement (no defect) |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the game file plus the Story 117 card, CACHE bump line, and precache entry together in one PR. No shared ownership with the jobs pipeline or any outside team.

### 2. Game file and states

Single file `website/games/snapline.html`, no dependencies, no build step. States TITLE, AIM, FLYING, RESOLVE, WIN, LOSE per Rook's contract. TITLE shows name, one-line rule, seed display, Start control, no running timer. AIM accepts aim and fire. FLYING holds one projectile; aim input pre-aims the next shot, fire ignored until resolve. RESOLVE runs the detach check, score and strain update, win/lose check, fixed length SNAP_PAUSE_MS, no input except restart. WIN shows score, shots used, seed, restart. LOSE shows reason string ("line" or "shots"), score, seed, restart.

### 3. Inputs and transitions

Pointer move over board sets aim angle in [AIM_MIN_DEG, AIM_MAX_DEG]. Click or tap fires if state is AIM. Arrow keys Left/Right adjust aim by AIM_KEY_STEP_DEG per press. Space fires if AIM. R key or restart control returns to TITLE seed reroll then AIM with a fresh board, allowed from any state. TITLE to AIM on Start. AIM to FLYING on fire (shotsFired increments by 1 at fire time). FLYING to RESOLVE on first contact (wall contact reflects, ceiling or orb contact sticks). RESOLVE to AIM if orbs remain and no lose condition; to WIN if zero orb cells remain; to LOSE if any orb cell is at or below LINE_ROW after the ceiling drop, or shotsLeft is 0 with orbs remaining. WIN or LOSE to AIM on restart with a new seed.

### 4. Rules and formulas (units per contract)

load(C) in orbs equals orb cells in ceiling-connected component C via 4-neighborhood flood fill from ceiling-touch cells. strength(C) in orbs equals the sum of STR(v) over the ceiling-touch cells of C, each dealt at generation in [STR_MIN, STR_MAX]. Snap predicate: C detaches when load(C) is strictly greater than strength(C). Unsupported cells with no 4-neighborhood path to the ceiling detach in the same RESOLVE (gravity), scoring identically. Score increases by detachedCount, one point per orb, no multipliers, no combos. shotsLeft equals SHOTS minus shotsFired. ceilingDrop in rows equals floor(shotsFired / DROP_EVERY), applied after each RESOLVE. Projectile moves at LAUNCH_PX_PER_S; wall reflection mirrors x exactly. Sticking rule: nearest empty cell to contact (ceiling contact: row 0 at that x snapped to column; orb contact: nearest empty 4-neighbor; ties break toward the ceiling), so every shot adds exactly one orb cell. strain(C) equals load(C) / strength(C); strain at or above STRAIN_WARN shows the warn state in text plus symbol, never color alone (Palette owns visuals). Board geometry: 8 cols x 40px equals 320px wide, fits the 375px mobile viewport with margin; 10 rows x 40px equals 400px plus launcher zone 120px.

### 5. Tuning constants (all live in the single file)

GRID_COLS 8 (6..10), GRID_ROWS 10 (8..12), CELL_PX 40 (32..48), LAUNCH_PX_PER_S 640 (400..960), AIM_MIN_DEG -75 (-85..-45), AIM_MAX_DEG 75 (45..85), AIM_KEY_STEP_DEG 2 (1..5), START_ROWS 3 (2..4), FILL_P 0.55 (0.35..0.75), STR_MIN 6 (4..8), STR_MAX 10 (8..14), SHOTS 40 (20..80), DROP_EVERY 8 (4..16), LINE_ROW 8 (7..9), SNAP_PAUSE_MS 350 (150..800), STRAIN_WARN 0.75 (0.5..0.9). Seed rule: seed equals floor(random * 2^31), displayed on TITLE and end screens; generation guarantees at least one column at or above STRAIN_WARN at start, topping up the weakest column if the roll misses.

### 6. Edge cases (contract)

Bridged components merge into one whose strength is the sum of both anchors. Simultaneous snaps in one RESOLVE both detach and score sums. Snap-disconnected neighbors fall in the same RESOLVE. Ceiling drop pushing an orb onto the line is LOSE (line). Last shot clearing the board is WIN, taking precedence over shots-exhausted LOSE. Firing into a full column climbs to the nearest empty cell; full down to the line is LOSE (line). Restart mid-flight discards the projectile and regenerates from a new seed. Best score persists under key `flambeee-snapline-best` as {score, seed} only; corrupt or missing value degrades to no best display. No other persisted state.

Plan B: if playtest shows players cannot find the first snap within ten shots, the only allowed retreat is numeric (raise FILL_P to 0.65, lower STR_MAX to 9). No colors, no combos, no second clearing rule. If the falsifying question fails, stop and take Story 118 rather than bolting on match-3.

### 7. Scope guard

In scope: `website/games/snapline.html` only. Untouched by this story: `website/index.html`, `website/sw.js`, every app file, every other game file, GAME_ORDER, the What's New heading (release wave owns it), the schedule, the noon pipeline, `pending-post.txt`, checker scripts, the FPS probe, jobs, jakebot, cron config, PRs 202/203/204.

### 8. Proof bar (release gate)

All six, or the game does not ship:

1. Serves locally (plain static serve, no build step).
2. RED on the current tree, then GREEN: `website/games/snapline.html` absent pre-change (RED by construction); post-change scenario script exits 0 with all cases passing.
3. Desktop 1280x800 with real input (pointer fire plus keyboard-only path): first snap within eight aimed shots at the warn-marked strand, layout holds with overflow 0.
4. Mobile 375x667 with real input: same, layout holds with overflow 0.
5. Zero page-attributable console errors on both viewports (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
6. Balance harness (dev owns it, pure logic extracted from the shipped file): seeds 1..200, greedy vs random, 400 runs; greedy clears at least 120/200, random clears at most 30/200, greedy median at or below 30 shots, zero seeds clear in fewer than 5 greedy shots, every seed starts within 3 loads of snapping. Fail branch: apply Plan B numerics once and re-run; still below means the spine is rejected.

Release implication, fixed: green keeps a v0.44.0 cut on the table, slip means no tag. The release wave decides the cut.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the game file plus the Story 117 site surfaces as single owner, and the dev record states the name.

**Scenario 2: First snap, the test that matters.**
Given a fresh run, when the player fires only at the pre-strained warn-marked strand, then that strand detaches with a score increase within eight shots. (RED anchor: the file does not exist on the current tree.)

**Scenario 3: Strain warn state.**
Given any run, when a component reaches strain at or above 0.75, then the board shows the warn state in text plus symbol before the next shot is fired.

**Scenario 4: Ceiling stick adds one.**
Given a fired orb heading at empty space, when it reaches the ceiling, then it sticks to the ceiling row and the strand load increases by exactly one.

**Scenario 5: WIN on clear.**
Given a board with zero orb cells after a RESOLVE, when the pause ends, then the WIN screen shows with score, shots used, and seed.

**Scenario 6: LOSE on line.**
Given an orb cell at or below the marked line row after a RESOLVE, when the pause ends, then the LOSE screen names the line reason.

**Scenario 7: LOSE on shots.**
Given zero shots left with orbs on the board after a RESOLVE, when the pause ends, then the LOSE screen names the shots reason.

**Scenario 8: Keyboard only.**
Given keyboard only, when the player aims with arrows and fires with Space, then orbs launch, stick, and score identically to pointer play.

**Scenario 9: Restart.**
Given any state including mid-flight, when R is pressed or the restart control is used, then the board regenerates from a new seed and play resumes at AIM.

**Scenario 10: Best score.**
Given the fixed key `flambeee-snapline-best`, when runs complete and the page reloads, then only {score, seed} persists, and a corrupt or missing value degrades to no best display.

**Scenario 11: Scope guard.**
Given the scope guard, when the diff is inspected, then the only new file is `website/games/snapline.html` and no site, app, script, or config path shows a diff from this story.

**Scenario 12: Proof bar, desktop.**
Given a local serve, when a full run completes on desktop 1280x800 with real input, then there is zero horizontal overflow and zero page-attributable console errors.

**Scenario 13: Proof bar, mobile.**
Given a local serve, when a full run completes on mobile 375x667 with real input, then there is zero horizontal overflow and zero page-attributable console errors.

**Scenario 14: Balance gap.**
Given the sim harness over seeds 1..200, when greedy and random policies run, then greedy clears at least 120, random clears at most 30, greedy median is at or below 30, and no seed is trivial or unreachable at start.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Fresh run snaps the warn-marked strand within eight aimed shots with a score increase (Scenario 2).
**AC-3.** Strain at or above 0.75 shows text plus symbol warn state before the next shot (Scenario 3).
**AC-4.** Ceiling contact sticks and adds exactly one load (Scenario 4).
**AC-5.** Empty board after RESOLVE shows WIN with score, shots used, seed (Scenario 5).
**AC-6.** Orb at or below the line shows LOSE naming the line reason (Scenario 6).
**AC-7.** Shots exhausted with orbs left shows LOSE naming the shots reason (Scenario 7).
**AC-8.** Keyboard-only play launches, sticks, and scores identically to pointer play (Scenario 8).
**AC-9.** Restart from any state rerolls the seed and resumes at AIM (Scenario 9).
**AC-10.** Persistence is {score, seed} under `flambeee-snapline-best` only with clean degrade (Scenario 10).
**AC-11.** Diff limited to the one new game file (Scenario 11).
**AC-12.** Desktop 1280x800 full run with overflow 0 and zero page-attributable errors (Scenario 12).
**AC-13.** Mobile 375x667 full run with overflow 0 and zero page-attributable errors (Scenario 13).
**AC-14.** Balance thresholds met or the Plan B branch taken per contract (Scenario 14).
**AC-15.** RED on the current tree (file absent) then GREEN on the merged tree (exit 0).
**AC-16.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Local-serve command plus URL; RED statement (file absent on base); GREEN scenario run exit 0 with per-case values (first snap shot count, score delta, WIN/LOSE screens, keyboard-only run); both-viewport overflow readings; console-error counts with page-attributable versus environmental split; seed display readouts; storage readout showing {score, seed} only under `flambeee-snapline-best`; balance harness run table (greedy clears, random clears, median, trivial count, reachability count). Numbers, not adjectives.

## Non-Goals

- Color matching, combos, multipliers, a second clearing rule, audio, menus, or a second mechanic.
- Site card, CACHE bump, precache entry, GAME_ORDER change, What's New edit (Story 117 and the release wave own those).
- A new persisted field or key beyond the best-score pair.
- Cutting a version (release wave owns the cut decision and the tag).
