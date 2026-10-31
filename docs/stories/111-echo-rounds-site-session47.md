# Story 111: Echo-rounds site integration plus proof (Session 47, P2)

**Status:** Ready for development (Session 47, 2026-10-31).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (site integration plus proof; rides with Story 110, same PR by construction).
**Assigned to:** **Riven** (single code owner per the Story 048 protocol, named before the wave starts; holds Story 110's game file plus this story's site surfaces together). Ember is product owner. No shared ownership.
**Tracked by:** Session 47 plan, Story 111. Follows Story 108 (Convert app plus card plus CACHE 14 to 15 plus precache, shipped v0.39.0) for the site-integration pattern.
**Depends on:** Story 110 (the game file must exist in the same PR; card target, precache entry, and proof all resolve against it). No code dependency outside that pair.

## Summary

Integrate the Story 110 echo-rounds game into the site and prove the pair: exactly one site card on `website/index.html` following the existing game-card pattern, CACHE_VERSION 15 to 16 plus exactly one new `sw.js` precache entry for the game file, What's New naming v0.40.0 after the cut, and a checker run with both viewports driven by real input. No controller claim anywhere. Same PR as Story 110 by construction; the split into two stories is for review clarity, not for separate ownership or separate merges.

## jakebot decision (advisory only, recorded)

Session 47 Wave 1 priorities per jakebot (session local-da8e342680b22b5cd118201b381c7b29a9ce153ecdd243158e69c9656442c0df, proceeded on its read): point 2, site integration plus proof (card target resolving, checker run, heading v0.40.0 post-release, both viewports with real input, zero page-attributable console errors). Scope guard adds: no controller claim anywhere, and the gamepad gate stays OPEN-BLOCKED-ON-HARDWARE, unmentioned in the release post.

**Citation:** `flambeee-team/session-plan.md`, Session 47 (2026-10-31), section "jakebot decision (advisory only, recorded)".

## Baseline measured at Session 47 planning (2026-10-31 01:10 CDT, paths re-verified Wave 2)

| Check | Value |
|---|---|
| Website What's New heading | v0.39.0 (matches tag v0.39.0) |
| `sw.js` `CACHE_VERSION`, repo mirror | 15 (run must read the line, not assume it) |
| Precache tail (`website/sw.js` PRECACHE_URLS) | `./apps/convert.html` last; 6 game files plus wordfire-words.js plus 6 app files present |
| Game cards on `website/index.html` | 6 (wordfire, minesweeper, simon, 2048, cinder, afterglow) |
| GAME_ORDER (`website/index.html`) | 6 entries (`cinder`, `wordfire`, `minesweeper`, `simon`, `2048`, `afterglow`) |

## Requirements

### 1. Owner named before the wave (Story 048)

Riven is the single code owner, holding Story 110's game file plus this story's card, CACHE bump line, and precache entry together in one PR, so overlap is impossible by construction. Ember holds product ownership; this story is Quinn-carried planning. No shared ownership with the jobs pipeline or any outside team.

### 2. Site card (exactly one)

- Exactly one new game card on `website/index.html` following the existing game-card pattern (name, one-line desc, Play link to the Story 110 file).
- Card target resolving: the link target exists in the same PR and loads over local serve.
- GAME_ORDER: leave the 6-entry rotation untouched unless the dev record states a one-line reason; the card is discoverable with or without rotation membership. No other index section is redesigned.

### 3. CACHE ownership (this story owns the bump)

- **This story owns:** the `CACHE_VERSION` bump line (15 to 16) and exactly one new precache entry (one line for the Story 110 game file), appended after the convert line.
- Per the v0.33.0 comment rule, any change to shell surface needs the bump, and the new game file plus the edited index are shell assets, so the bump ships with this story.
- The dev record states the entry line verbatim plus the version readout before and after.

### 4. What's New names v0.40.0

- After the cut, the What's New heading names v0.40.0 with a one-line echo-rounds entry. The heading edit is the release wave's post-tag step; this story requires it as acceptance, verified by checker Check 6 (heading names the newest origin tag).
- The entry names only what visitors notice (the new game). No cache talk, no controller talk in the entry.

### 5. Checker run

- Run 1 pre-merge: `scripts/verify-website-currency.sh` executed against the PR tree, exit code plus per-check lines recorded in the dev record. Checks 6/7/8 expectations: Check 8 (card target in precache) PASS pre-merge; Check 6 and Check 7 resolve post-tag and are the release wave's Run 2.
- Run 2 post-tag at v0.40.0 is the release wave's job (standing leg, no story). Quinn notes the one-liner, nobody re-proves it.

### 6. Scope guard

In scope: the at-most-one site card on `website/index.html`, the one `CACHE_VERSION` bump line, the at-most-one `sw.js` precache entry line, the release-wave heading line. Untouched, no diff: every existing game file, every app file, `GAME_ORDER` beyond the section 2 note, the schedule, the noon pipeline, `flambeee-team/state/pending-post.txt`, the checker scripts themselves (`scripts/` frozen, run not edited), the FPS probe (`dev/fps-probe/`), jobs, jakebot, cron config. The game file itself belongs to Story 110; this story adds no second copy of it.

### 7. Proof bar (release gate)

All five, or the pair does not ship:

1. Serves locally (plain static serve, no build step).
2. Desktop 1280x800 plus mobile 375x667, site and game driven with real keydown and click events, both viewports.
3. Zero page-attributable console errors (pre-existing environmental noise such as a favicon 404 reproduces on base and is recorded, not counted).
4. Layout holds with overflow 0 on both viewports, index and game page.
5. Card present and resolving, `CACHE_VERSION` reads 16 on the merged tree, new precache line present in `PRECACHE_URLS`.

Release implication, fixed: green keeps a v0.40.0 cut on the table, slip means no tag. The release wave decides the cut. No cut for a card alone.

### 8. No controller claim anywhere

No gamepad, controller, or pointer-lock claim in the card, the What's New entry, the dev record, or the release post. The gamepad gate stays OPEN-BLOCKED-ON-HARDWARE and goes unmentioned in the release post.

## BDD scenarios

**Scenario 1: Owner check.**
Given the Story 048 rule, when the dev wave starts, then Riven holds Story 110's game file plus this story's card, CACHE bump, and precache entry as single owner in one PR, and the dev record states the name.

**Scenario 2: Card resolves.**
Given a local serve, when the new site card link is followed, then the Story 110 game page loads.

**Scenario 3: CACHE ownership.**
Given the repo `website/sw.js`, when the merged diff is inspected, then the version line reads 15 to 16 and exactly one new precache line for the game file is appended after the convert line, and no other precache line changed.

**Scenario 4: Scope guard.**
Given the scope guard, when the diff is inspected, then changed site files are at most the one card plus the CACHE bump plus the one precache entry line (plus Story 110's one game file in the same PR), and existing games, apps, schedule, noon, checker, and probe paths show no diff.

**Scenario 5: Proof bar, desktop.**
Given a local serve, when the site and game are driven on desktop 1280x800 with real keydown and click events, then the card resolves, the game plays, layout holds, and zero page-attributable console errors are recorded.

**Scenario 6: Proof bar, mobile.**
Given a local serve, when the site and game are driven on mobile 375x667 with real keydown and click events, then layout holds with no overflow and zero page-attributable console errors are recorded.

**Scenario 7: Checker and heading.**
Given the merged tree plus the release cut, when the checker runs post-tag, then Check 6 (heading names newest tag, v0.40.0), Check 7 (CACHE changed since predecessor), and Check 8 (card target in precache) all PASS.

**Scenario 8: Release gate.**
Given the proof bar result, when the release wave decides, then green keeps a v0.40.0 cut on the table and red (or a slip) means no tag, with no cut for a card alone.

## Acceptance Criteria

**AC-1.** Single code owner Riven named before the wave per Story 048, holding Stories 110 and 111 together (Scenario 1).
**AC-2.** Exactly one new site card following the game-card pattern, target resolving over local serve (Scenario 2).
**AC-3.** CACHE ownership held: version line 15 to 16 plus exactly one new precache entry line after the convert line, no other precache line changed (Scenario 3).
**AC-4.** Diff limited per the scope guard (Scenario 4).
**AC-5.** Desktop 1280x800 real-input run green with zero page-attributable errors (Scenario 5).
**AC-6.** Mobile 375x667 real-input run green with zero page-attributable errors, overflow 0 (Scenario 6).
**AC-7.** Checker Run 1 recorded pre-merge with Check 8 PASS; Run 2 post-tag owned by the release wave with Checks 6/7/8 PASS (Scenario 7).
**AC-8.** What's New names v0.40.0 with a one-line game entry post-cut; entry names only what visitors notice (Scenario 7).
**AC-9.** No gamepad, controller, or pointer-lock claim in card, entry, dev record, or release post; gate stays OPEN-BLOCKED-ON-HARDWARE, unmentioned in the post (Scenario 8 scope).
**AC-10.** `CACHE_VERSION` reads 16 on the merged tree with the game precache line present.
**AC-11.** Release-gate rule recorded: green keeps a cut on the table, slip means no tag; no cut for a card alone (Scenario 8).
**AC-12.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Required Proof

Card link target plus local-serve load check; the new precache entry line verbatim plus the `CACHE_VERSION` readout before and after; checker Run 1 exit code plus per-check lines; both-viewport real-input runs with exit codes; overflow readings; console-error counts with page-attributable versus environmental split. Numbers, not adjectives.

## Non-Goals

- Any second card, any index redesign, any GAME_ORDER change beyond the section 2 note.
- Any game logic change (Story 110 owns the game file).
- Changing any checker script (run, do not edit).
- Any gamepad, controller, or pointer-lock implementation or claim.
- Any change to apps, schedule, noon, pending-post.txt, probe, jobs, jakebot, or cron config.
- Cutting a version (release wave owns the cut decision, the tag, the heading edit, and Run 2).
