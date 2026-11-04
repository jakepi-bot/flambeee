# Story 117: Snapline site integration plus proof (Session 51, P2)

**Status:** Ready for development (Session 51, 2026-11-04).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (site integration plus proof; rides with Story 116, same PR by construction).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds Story 116's game file plus this story's site surfaces together). Ember is product owner. No shared ownership.
**Tracked by:** Session 51 plan, Story 117. Follows Story 111 (Echo Rounds site integration, shipped v0.40.0) for the site-integration pattern. Design contract: `flambeee-team/design-handoff.md` (Rook, Session 51).
**Depends on:** Story 116 (the game file must exist in the same PR; card target, precache entry, and proof all resolve against it). No code dependency outside that pair.

## Summary

Integrate the Story 116 Snapline game into the site and prove the pair: exactly one site card on `website/index.html` following the existing game-card pattern (icon glyph, name Snapline, one-line desc naming load-breaking, Play link to `games/snapline.html`), CACHE_VERSION 19 to 20 plus exactly one new `sw.js` precache entry (`  './games/snapline.html'`, appended after the echo-rounds line), GAME_ORDER stays six entries (Story 111 precedent: card only, no rotation change, no modal entry), What's New naming left to the release wave. Same PR as Story 116 by construction; the split into two stories is for review clarity, not for separate ownership or separate merges.

## Baseline measured at Session 51 planning (2026-11-04 01:10 CST, paths re-verified Wave 2)

| Check | Value |
|---|---|
| Website What's New heading | v0.43.0 (matches tag v0.43.0) |
| `sw.js` `CACHE_VERSION`, repo mirror | 19 (run must read the line, not assume it) |
| Precache tail (`website/sw.js` PRECACHE_URLS) | `./games/echo-rounds.html` last; 7 game files plus wordfire-words.js plus 6 app files present |
| Game cards on `website/index.html` | 7 (wordfire, minesweeper, simon, 2048, cinder, afterglow, echo-rounds) |
| GAME_ORDER (`website/index.html`) | 6 entries (`cinder`, `wordfire`, `minesweeper`, `simon`, `2048`, `afterglow`) |
| Card target | `games/snapline.html` absent on base (RED anchor, resolves in the same PR) |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding Story 116's game file plus this story's card, CACHE bump line, and precache entry together in one PR, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. Site card (exactly one)

- Exactly one new game card on `website/index.html` following the existing game-card pattern: icon glyph block (card without screenshot follows the Echo Rounds precedent, no image asset), name Snapline, one-line desc naming load-breaking, Play link to `games/snapline.html`.
- Card target resolving: the link target exists in the same PR and returns 200 over local serve.
- GAME_ORDER: stays exactly the six existing entries in order (Story 111 precedent: card only, no rotation change, no modal entry). The new game is reachable by card and direct link only, the same shelf position Echo Rounds holds.
- No other index section is redesigned.

### 3. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (19 to 20) and exactly one new precache entry (one line for the Story 116 game file), appended after the echo-rounds line: `  './games/snapline.html'`.
- Per the v0.33.0 comment rule, the new game file plus the edited index are shell assets, so the bump ships with this story. Never bump CACHE without the precache entry in the same diff.
- The dev record states the entry line verbatim plus the version readout before and after.
- Exact-match invariants after the change: GAME_ORDER length 6, precache entries containing `games/` 8, CACHE_VERSION 20.

### 4. What's New (release wave owns it)

The What's New heading and section line are the release wave's post-tag step and are not touched by this story. The entry names only what visitors notice (the new game). No cache talk in the entry.

### 5. Checker run

- Run 1 pre-merge: `scripts/verify-website-currency.sh` executed against the PR tree, exit code plus per-check lines recorded in the dev record. Expectation: Check 8 (card target in precache) PASS pre-merge; Check 6 and Check 7 resolve post-tag and are the release wave's Run 2.
- Run 2 post-tag is the release wave's job (standing leg, no story). Quinn notes the one-liner, nobody re-proves it.
- Verification plan: checker Run 1 pre-merge records the entering state (heading v0.43.0, CACHE 19 baseline, Play targets resolving). Pass thresholds: card GET 200, precache count 8 game entries, GAME_ORDER 6 of 6, overflow 0 both viewports, zero console errors.

### 6. Scope guard

In scope: the one site card on `website/index.html`, the one `CACHE_VERSION` bump line, the one `sw.js` precache entry line. Untouched, no diff: every existing game file, every app file, GAME_ORDER membership and order, the What's New block, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts themselves (`scripts/` frozen, run not edited), the FPS probe (`dev/fps-probe/`), jobs, jakebot, cron config, PRs 202/203/204. The game file itself belongs to Story 116; this story adds no second copy of it.

Plan B: if the card plus cache change cannot land cleanly in the single PR, land the game file first and carry the card to the next session rather than hand-editing the manifest.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds Story 116's game file plus this story's card, CACHE bump, and precache entry as single owner, and the dev record states the name.

**Scenario 2: Card resolves.**
Given local serve, when the Play link target is requested, then it returns 200 for `games/snapline.html`.

**Scenario 3: GAME_ORDER untouched.**
Given the hub page, when GAME_ORDER is read, then it holds exactly the six existing entries in order (`cinder`, `wordfire`, `minesweeper`, `simon`, `2048`, `afterglow`).

**Scenario 4: Cache manifest.**
Given the service worker file, when read, then CACHE_VERSION is 20 and the precache list contains the exact snapline line once, appended after the echo-rounds line.

**Scenario 5: Card visible both viewports.**
Given desktop 1280x800 and mobile 375x667, when the hub loads, then the Snapline card is visible, there is zero horizontal overflow, and there are zero page-attributable console errors.

**Scenario 6: Checker Run 1.**
Given the PR tree, when `scripts/verify-website-currency.sh` runs pre-merge, then Check 8 passes (card target in precache) and the exit code plus per-check lines are recorded in the dev record.

**Scenario 7: Scope guard.**
Given the scope guard, when the diff for this story is inspected, then changed lines are at most the one card block, the one CACHE line, and the one precache line, and every other site, app, game, schedule, noon, checker, and FPS path shows no diff.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048 (Scenario 1).
**AC-2.** One Snapline card on the hub with glyph, load-breaking desc, and Play link to `games/snapline.html` (Scenario 2).
**AC-3.** Card target returns 200 over local serve (Scenario 2).
**AC-4.** GAME_ORDER holds exactly the six existing entries in order (Scenario 3).
**AC-5.** CACHE_VERSION reads 19 to 20 with the exact snapline precache line once, after the echo-rounds line (Scenario 4).
**AC-6.** Precache entries containing `games/` total 8 (Scenario 4).
**AC-7.** Snapline card visible both viewports with overflow 0 and zero page-attributable errors (Scenario 5).
**AC-8.** Checker Run 1 recorded with Check 8 PASS; Run 2 is the release wave's job (Scenario 6).
**AC-9.** Diff limited per the scope guard (Scenario 7).
**AC-10.** What's New untouched by this story (release wave owns it).
**AC-11.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Local-serve command plus URL; card target GET 200 readout; GAME_ORDER readout showing 6 of 6 in order; `CACHE_VERSION` readout before and after plus the new precache line verbatim; precache game-entry count; both-viewport hub runs with overflow readings and console-error counts (page-attributable versus environmental split); checker Run 1 exit code plus per-check lines. Numbers, not adjectives.

## Non-Goals

- A second card, a second precache entry, a GAME_ORDER rotation change, a modal entry, or a What's New edit.
- Any change to the game file beyond Story 116, any app file, any checker script, the schedule, the noon pipeline, or `pending-post.txt`.
- A stats key wiring beyond the card link (game-local best display is the game's own concern).
- Cutting a version (release wave owns the cut decision and the tag).
