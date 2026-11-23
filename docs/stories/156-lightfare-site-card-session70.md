# Story 156: LIGHTFARE site card and cache activation (Session 70, P0b)

**Status:** Ready for development (Session 70, 2026-11-23).
**Author:** Quinn, Business Analyst.
**Priority:** P0b (user-visible site rider; same PR as Story 155, release gate for v0.57.0).
**Assigned to:** **Riven**, sole code owner, same PR as Story 155.
**Base commit:** `23674a2` (main, v0.56.0 released).
**Scope:** `website/index.html` (one LIGHTFARE card after EMPTY HANDS, header count copy `Ten games` to `Eleven games`, no other change) plus `website/sw.js` (`CACHE_VERSION` 32 to 33, exactly one line, plus exactly one precache line for `./games/lightfare.html`). No game file in this story (that is Story 155).
**Design contract:** `flambeee-team/design-handoff.md`, Story 156 sections 1 through 6. Design-owned observable criteria live in contract section 5 and are mapped here one for one.

## Summary

Story 155 adds the LIGHTFARE game file; without this story nobody can find it and returning visitors keep the old cached shell. This story adds one static card after the EMPTY HANDS card (glyph per current card convention, verb-led description, Play link `games/lightfare.html`), updates the header count copy, and activates the new shell with the one-line cache bump plus one precache entry. `GAME_ORDER` stays byte-identical: LIGHTFARE is Play-link discoverable like Typewreck, with no modal entry and no GOTW rotation slot (Story 125 ruling stands, decision 002).

## Functional requirements

FR-1 (contract section 1). The home page gains exactly one static LIGHTFARE card placed after the EMPTY HANDS card: glyph (Palette-neutral placeholder per current card convention), verb-led description, Play link `games/lightfare.html`. The card link must GET 200 over local serve before merge.

FR-2 (contract section 1-2). Header count copy at `website/index.html` line ~674 changes from `Ten games, one arcade` to `Eleven games, one arcade`. Card count goes 10 to 11.

FR-3 (contract section 1-2). `CACHE_VERSION` 32 to 33 in `website/sw.js`, exactly one line, same PR. Exactly one precache line appended after the empty-hands entry (`./games/lightfare.html`); precache entries go 23 to 24. This one bump (shared with Story 155) activates both the new game file and the new card for returning visitors.

FR-4 (contract section 1). `GAME_ORDER` byte-identical to base. No GAMES modal entry for LIGHTFARE, no rotation slot, no redesign of the home page, no other index change.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in contract section 5; AC-1 through AC-3 map them directly. AC-4 onward pin the structural requirements.

1. Given the home page, when it renders, then a LIGHTFARE card appears after EMPTY HANDS with a working Play link to `games/lightfare.html`. (design 5.1; FR-1)
2. Given the home page header, when read, then it says `Eleven games, one arcade`. (design 5.2; FR-2)
3. Given a returning visitor on the old worker, when the new worker activates, then the LIGHTFARE card appears with no stale-mix state. (design 5.3; FR-3)
4. Given the card Play link, when fetched over local serve, then it returns GET 200 for `games/lightfare.html`. (FR-1)
5. Given `git diff main -- website/sw.js`, when inspected, then `CACHE_VERSION` changes 32 to 33 on exactly one line and exactly one precache line is added after the empty-hands entry (23 to 24 entries). (FR-3)
6. Given `git diff main -- website/index.html`, when inspected, then the only hunks are the one new card, the count-copy line, and nothing else; `GAME_ORDER` is byte-identical. (FR-2; FR-4)
7. Given any conflict between this story and the shipped game file at merge, when reviewed, then the game file governs per the standing conflict rule. (pattern-doc conflict rule)

## Edge cases

- Card link 404: must GET 200 over local serve before merge; fix the href, not the checker. (contract section 4)
- Stale cached index served: old copy/count until the 33 activation lands; versioned-out, not a bug; the same-PR bump is the fix path. (contract section 4)
- `GAME_ORDER` accidentally touched: FAIL the story; rotation changes need a NEW-GAME-day proposal; revert the hunk. (contract section 4)

## Out of scope

The game file itself (Story 155), the proof harness (Story 157), the pattern-doc section (Story 158), any modal or detail view, any `GAME_ORDER` change, any other `website/` bytes, any tuning or mechanic decision.

## Traceability

Every contract clause is covered: section 1 states/inputs/transitions map to FR-1 through FR-4 (AC-1 through AC-4, AC-6); section 2 formulas map to FR-2 and FR-3 (AC-2, AC-5); section 3 tuning table maps to FR-2 through FR-4 (AC-5, AC-6); section 4 edge cases map to the Edge cases list above; section 5 design criteria map to AC-1 through AC-3; section 6 measurement rationale maps to AC-4 through AC-6 (card GET 200, copy exact, bump one line, precache +1, `GAME_ORDER` byte-identical, all or FAIL).

## Evidence the dev must paste (in the PR)

- Card screenshot or DOM: LIGHTFARE card after EMPTY HANDS, Play link GET 200.
- Header copy reads `Eleven games, one arcade`.
- `sw.js` diff: exactly one version line (32 to 33) plus exactly one precache line.
- `GAME_ORDER` byte-identical to base.

## Definition of done

- AC-1 through AC-7 all hold on the branch.
- PR contains only the Story 155 game file, this card plus count copy, the one `sw.js` bump plus one precache line, and the Story 158 doc section.
- Scout QA GO and Rook design review NO BLOCKING FINDINGS.
