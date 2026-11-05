# Story 119: Typewreck paste-to-fortress demolition game (Session 52, P1, user-visible)

**Status:** Ready for development (Session 52, 2026-11-05).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (new game; version cut decided by the release wave).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds the game file in this story plus the Story 120 site surfaces in the same PR, so overlap is impossible by construction). No shared ownership.
**Tracked by:** Session 52 plan, Story 119. Design contract: `flambeee-team/design-handoff.md` (Rook, Session 52). Reskin gate passed, no fallback.
**Depends on:** No code dependency on any other story this session. Story 120 rides in the same PR by construction.

## Summary

Build Typewreck, a paste-to-fortress demolition game, as a single file at `website/games/typewreck.html` with no dependencies. The player pastes any text (a URL, a sentence, anything) or deals a random wall, and the text becomes an 8-row fortress where each character sets one block's hit points by a public rarity rule. The player aims a bottom cannon and fires piercing shots: each shot spends a fixed damage budget traveling in a straight line, destroying what it can, stopping when the budget is spent or the ray exits. WIN by clearing every block. LOSE by running out of shots with blocks left. Score is blocks destroyed plus a bonus per unused shot on a win. Same text always deals the same wall, so pasting a URL and beating a posted score is the share loop. The page never fetches anything: the pasted string is level material only, hashed locally, and the page works offline after load.

Ship note (release wave uses verbatim): Paste anything and wreck it: Typewreck turns pasted text into a fortress where spaces and vowels crumble and capitals plus punctuation are armor, cleared by piercing shots that spend a fixed damage budget traveling in a straight line.

Reskin gate (Story 068 test, passed at the doc gate): strip all art to identical gray squares with HP numerals and no letters, and the remaining rule is text-seeded armor plus traveling-budget penetration. Breakout and Arkanoid bounce the ball and reflect it; nothing bounces or reflects here, rays travel straight and stop when the budget is spent. Space Invaders has descending shooters that fire back; nothing fires back and nothing descends. Puzzle Bobble, Bust-a-Move, and Snood clear by matching three or more of a color; there is no color and no matching. Collapse and SameGame clear tapped same-color groups; there is no tapping and no color. Falsifying playtest question: with HP numerals visible, do first-time players preferentially fire through high-HP clusters rather than spraying at random within their first ten shots, and do the cluster-aimers clear medium walls inside the ammo budget while sprayers lose; if a majority sprays, or if aimed play clears no better than random fire in the sim, the spine has failed and the reserve triggers.

First five minutes: paste or random deal inside seconds, first shot inside ten seconds of Start, first destroyed block within three aimed shots at a dense lane, first win inside five minutes on a medium wall, first loss (spraying a hard wall) teaches aiming through clusters.

## Baseline measured at Session 52 planning (2026-11-05 01:10 CST)

| Check | Value |
|---|---|
| Newest tag | v0.43.0 |
| Website What's New heading | v0.43.0 (matches tag v0.43.0) |
| `sw.js` `CACHE_VERSION`, repo mirror | 19 (run must read the line, not assume it) |
| Game files | 7 game files; `website/games/typewreck.html` does not exist (RED anchor) |
| GAME_ORDER (`website/index.html`) | 6 entries (`cinder`, `wordfire`, `minesweeper`, `simon`, `2048`, `afterglow`), untouched by this story |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding the game file plus the Story 120 card, CACHE bump line, and precache entry together in one PR. No shared ownership with the jobs pipeline or any outside team.

### 2. Game file and states

Single file `website/games/typewreck.html`, no dependencies, no build step. States SETUP, AIM, FLYING, RESOLVE, WIN, LOSE per Rook's contract. SETUP shows the paste box (empty, placeholder names URLs as an example), Random Wall button, wall toughness preview (total HP plus shot budget, updates on paste or deal), Start control, best-score line, no running timer. AIM shows the live wall, loaded cannon, aim indicator at the current angle, HUD with shots left, blocks left, score; accepts aim and fire. FLYING holds one visible projectile; aim input pre-aims the next shot, fire ignored until resolve. RESOLVE applies damage per cell in path order, updates score, shots, and toughness, runs the win/lose check, fixed length HIT_PAUSE_MS, no input except restart. WIN shows score with bonus line, shots used, seed or text hash, restart control. LOSE shows reason string ("shots"), score, blocks left, seed or text hash, restart control.

### 3. Inputs and transitions

Paste accepts typed or pasted text, 1 to 500 chars. Empty paste shows a note and does not start. Over 500 chars truncates to 500 with a note. Random Wall button (SETUP only) deals from seed = floor(random * 2^31), displayed. Start (SETUP only) moves SETUP to AIM with the dealt wall (shotsFired = 0, score = 0). Pointer move over board sets aim angle in [AIM_MIN_DEG, AIM_MAX_DEG]. Click or tap fires if state is AIM. Arrow keys Left/Right adjust aim by AIM_KEY_STEP_DEG per press. Space fires if AIM. AIM to FLYING on fire (shotsFired increments by 1 at fire time). FLYING to RESOLVE when the ray exits the board region or has no board cells left in path. RESOLVE to AIM if blocks remain and shotsLeft is above 0; to WIN if zero blocks remain; to LOSE if shotsLeft is 0 with blocks remaining. WIN or LOSE to AIM on restart (same wall, shots and score reset, mid-flight projectile discarded). WIN or LOSE to SETUP on the change-wall control (pasted text kept in the box for editing). R key or restart control replays the current wall from any state; paste walls replay identically, random walls replay the same seed.

### 4. Rules and formulas (units per contract)

hpForChar(ch) in HP: space or lowercase vowel (a, e, i, o, u) gives 1; other lowercase letter or digit gives 2; uppercase, punctuation, symbol, or any other code point gives 3. Player rule shown in SETUP: "Soft: space and vowels. Medium: other small letters and digits. Armor: capitals, punctuation, everything exotic." Wall cell k: index i (0 to 79, row-major) takes character text[i mod len(text)] for paste walls, or a seeded roll (u below 0.45 gives 1, below 0.85 gives 2, else 3) for random walls. totalHP = sum of cell HP over all 80 cells; paste corpus range 80 to 240, typical English about 130 to 160; shown as the toughness preview. Shot damage: ray cells in path order, each occupied cell absorbs min(cellHP, penLeft); penLeft starts at PEN and decreases; the shot ends when penLeft is 0 or the ray exits. Destroyed cells (HP 0) no longer block penetration within the same shot. shotsLeft = SHOTS minus shotsFired. blocksLeft = cells with HP above 0. score = destroyedBlocks (1 per block) plus, on WIN only, WIN_BONUS_PER_SHOT times shotsLeft. Seed display: random walls show the decimal seed; paste walls show the FNV-1a hash of the exact pasted text in hex. Same text plus same constants always deals the same wall. Aim angle in degrees from vertical, positive right. Projectile p(t) = p0 + v * t with |v| = LAUNCH_PX_PER_S, straight line, no reflection; shots that exit the sides or top deal only what they hit, and clean misses are legal and wasted. Board geometry: 10 cols x 32px = 320px wide (fits the 375px mobile viewport with margin); 8 rows x 32px = 256px plus launcher zone 120px; cannon at bottom center, 60px above the board bottom edge. Damage budget check: SHOTS * PEN = 336 HP total vs hardest measured wall 240 HP and typical 130 to 160 HP; every deal is clearable in-budget at 72 percent damage efficiency or better.

### 5. Tuning constants (all live in the single file)

GRID_COLS 10 (8..12), GRID_ROWS 8 (6..10), CELL_PX 32 (28..40), LAUNCHER_PX 120 (80..160), PEN 12 (8..16), SHOTS 28 (20..40), AIM_MIN_DEG -70 (-85..-45), AIM_MAX_DEG 70 (45..85), AIM_KEY_STEP_DEG 2 (1..5), LAUNCH_PX_PER_S 700 (400..960), HIT_PAUSE_MS 250 (150..600), PASTE_MAX 500 (100..2000), WIN_BONUS_PER_SHOT 2 (0..5). Exact HP mapping and seed rule per section 4.

### 6. Edge cases (contract)

Empty paste: note "Paste some text or deal a random wall." No state change, no wall dealt. Over-length paste: truncate to PASTE_MAX with note "Using the first 500 characters." Hash covers the truncated text. Single-char paste ("a"): repeats to fill 80 cells (80 HP wall). Legal, easy, shareable as a joke seed. All-armor paste: 240 HP wall, hardest legal deal, still inside the 336 budget. Ray through a fully cleared lane: deals 0, shot wasted; legal, the core aiming punishment. Last shot clearing the board: WIN takes precedence over shots-exhausted LOSE. Restart mid-flight: projectile discarded, shots and score reset, same wall. Change-wall from end screens: returns to SETUP, pasted text kept. Storage: best score persists under key `flambeee-typewreck-best` as {score, seed} only; corrupt or missing value degrades to no best display; no other persisted state; pasted text is never persisted. No network: zero requests after load (no fetch of pasted URLs, no analytics, no fonts); pasting a URL is string input, identical offline.

Plan B: if the sim fails the gap bar (greedy below 140 or greedy-minus-random below 100), the single allowed retreat is numeric, applied once: raise PEN to 14 and SHOTS to 32 (budget 448 HP), then re-run. No bouncing, no splash damage, no second clearing rule, no block HP change. If the spine still fails, stop and take the named reserve (inversion 2 give-back game) rather than bolting on color match or combos.

### 7. Scope guard

In scope: `website/games/typewreck.html` only. Untouched by this story: `website/index.html`, `website/sw.js`, every app file, every other game file, GAME_ORDER, the What's New heading (release wave owns it), the schedule, the noon pipeline, `pending-post.txt`, checker scripts, jobs, jakebot, cron config, PRs #206/#208.

### 8. Proof bar (release gate)

All six, or the game does not ship:

1. Serves locally (plain static serve, no build step).
2. RED on the current tree, then GREEN: `website/games/typewreck.html` absent pre-change (RED by construction); post-change scenario script exits 0 with all cases passing.
3. Desktop 1280x800 with real input (pointer fire plus keyboard-only path): first destroyed block within three aimed shots at a dense lane on a fresh medium wall, layout holds with overflow 0.
4. Mobile 375x667 with real input: same, layout holds with overflow 0.
5. Zero page-attributable console errors on both viewports (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
6. Balance harness (dev owns it, pure logic extracted from the shipped file): seeds 1..200, greedy vs random, 400 runs; greedy clears at least 140/200, random clears at most 40/200, greedy-minus-random at least 100, greedy median at or below 24 shots, zero seeds clear in fewer than 6 greedy shots, SHOTS * PEN covers totalHP on 200/200. Fail branch: apply Plan B numerics once and re-run; still below means the spine is rejected and the reserve triggers.

Release implication, fixed: green keeps a version cut on the table, slip means no tag. The release wave decides the cut.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds the game file plus the Story 120 site surfaces as single owner, and the dev record states the name.

**Scenario 2: Offline URL paste, the test that matters.**
Given the game page loaded and the network disabled, when a URL string is pasted and Start is pressed, then the full fortress wall appears and plays identically to online. (RED anchor: the file does not exist on the current tree.)

**Scenario 3: Deterministic deal.**
Given the same text pasted twice, when both walls are dealt, then block HP is identical cell for cell.

**Scenario 4: Dense-lane aiming pays.**
Given a fresh medium wall, when the player fires only through the densest lanes, then the first block is destroyed within three shots.

**Scenario 5: Toughness preview.**
Given a dealt wall, when the preview is read, then it names total HP and the shot budget before the first shot is fired.

**Scenario 6: WIN on clear.**
Given a board with zero blocks after a RESOLVE, when the pause ends, then the WIN screen shows with score, bonus line, shots used, and seed or hash.

**Scenario 7: LOSE on shots.**
Given zero shots left with blocks on the board after a RESOLVE, when the pause ends, then the LOSE screen names the shots reason with blocks left.

**Scenario 8: Empty paste.**
Given an empty paste box, when Start is pressed, then a plain note names the problem and no wall is dealt.

**Scenario 9: Keyboard only.**
Given keyboard only, when the player aims with arrows and fires with Space, then shots launch, pierce, and score identically to pointer play.

**Scenario 10: Best score.**
Given a finished run and a reload, when the best line is read, then only score plus seed persisted under `flambeee-typewreck-best`, and a corrupt value degrades to no best display.

**Scenario 11: Scope guard.**
Given the scope guard, when the diff is inspected, then the only new file is `website/games/typewreck.html` and no site, app, script, or config path shows a diff from this story.

**Scenario 12: Proof bar, desktop.**
Given a local serve, when a full run completes on desktop 1280x800 with real input, then there is zero horizontal overflow and zero page-attributable console errors.

**Scenario 13: Proof bar, mobile.**
Given a local serve, when a full run completes on mobile 375x667 with real input, then there is zero horizontal overflow and zero page-attributable console errors.

**Scenario 14: Balance gap.**
Given the sim harness over seeds 1..200, when greedy and random policies run, then greedy clears at least 140, random clears at most 40, the gap is at least 100, greedy median is at or below 24, no seed is trivial, and every seed fits the ammo budget.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** Pasted URL with network disabled deals and plays a full wall identically to online (Scenario 2).
**AC-3.** Same text deals identical walls cell for cell (Scenario 3).
**AC-4.** Dense-lane aiming destroys the first block within three shots on a fresh medium wall (Scenario 4).
**AC-5.** Toughness preview names total HP and shot budget before the first shot (Scenario 5).
**AC-6.** Empty board after RESOLVE shows WIN with score, bonus line, shots used, seed or hash (Scenario 6).
**AC-7.** Shots exhausted with blocks left shows LOSE naming the shots reason with blocks left (Scenario 7).
**AC-8.** Empty paste shows a plain note and deals no wall (Scenario 8).
**AC-9.** Keyboard-only play launches, pierces, and scores identically to pointer play (Scenario 9).
**AC-10.** Persistence is {score, seed} under `flambeee-typewreck-best` only with clean degrade (Scenario 10).
**AC-11.** Diff limited to the one new game file (Scenario 11).
**AC-12.** Desktop 1280x800 full run with overflow 0 and zero page-attributable errors (Scenario 12).
**AC-13.** Mobile 375x667 full run with overflow 0 and zero page-attributable errors (Scenario 13).
**AC-14.** Balance thresholds met or the Plan B branch taken per contract (Scenario 14).
**AC-15.** RED on the current tree (file absent) then GREEN on the merged tree (exit 0).
**AC-16.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Local-serve command plus URL; RED statement (file absent on base); GREEN scenario run exit 0 with per-case values (offline paste run, determinism check, first-destroy shot count, preview readout, WIN/LOSE screens, keyboard-only run); both-viewport overflow readings; console-error counts with page-attributable versus environmental split; seed and hash display readouts; storage readout showing {score, seed} only under `flambeee-typewreck-best`; balance harness run table (greedy clears, random clears, gap, median, trivial count, budget coverage). Numbers, not adjectives.

## Non-Goals

- Live URL fetching, cross-origin fetch, analytics, web fonts, audio, menus, a second mechanic, bouncing, splash damage, color match, or combos.
- Site card, CACHE bump, precache entry, GAME_ORDER change, What's New edit (Story 120 and the release wave own those).
- A new persisted field or key beyond the best-score pair; pasted text is never persisted.
- Cutting a version (release wave owns the cut decision and the tag).
