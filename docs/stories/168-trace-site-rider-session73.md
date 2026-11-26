# Story 168: TRACE site rider (Session 73, P0c)

**Status:** Ready for development (Session 73, 2026-11-26).
**Author:** Quinn, Business Analyst.
**Priority:** P0c (a twelfth game nobody can find is not shipped; same PR as Story 166 in v0.60.0).
**Assigned to:** **Riven**, sole code owner, same PR as Story 166. Files: `website/index.html` (one card plus header copy) and `website/sw.js` (one version line plus one precache line). Zero behavior change to existing games.
**Base commit:** `d5e8b63` (main, v0.59.0).
**Scope:** Twelfth game card after LIGHTFARE, header copy "Eleven games, one arcade" to "Twelve games, one arcade", CACHE_VERSION 35 to 36, precache 24 to 25 entries.
**Design contract:** `flambeee-team/design-handoff.md`, Section 3 (Story 168). Acceptance criteria map the contract one for one.
**Non-blocking rule:** this story is never cut. The cache bump plus the served-copy check in the release wave is what defeats the usual liar artifact.

## Summary

The home page needs to know the twelfth game exists. This story adds one card for TRACE right after LIGHTFARE with a plain text glyph, a short verb-led description, and a Play link, updates the header count from eleven to twelve, and bumps the service-worker cache version so returning visitors actually receive the new file. Nothing about any existing game changes.

## Story

As a visitor, I see a TRACE card after LIGHTFARE on the home page so I can open the twelfth game.

## Acceptance criteria (BDD, observable in product)

1. Given the home page, when it loads, then a TRACE card appears after LIGHTFARE with plain ASCII glyph "~", verb-led description "Draw the walls. Walk them.", and a Play link to games/trace.html. (contract Section 3, item 1)
2. Given the home page header, when it renders, then it reads "Twelve games, one arcade". (contract Section 3, item 1)
3. Given website/sw.js, when inspected, then CACHE_VERSION is 36 on exactly one changed line and the precache list holds 25 entries including ./games/trace.html on exactly one added line. (contract Section 3, item 2)
4. Given GAME_ORDER, when compared to main, then it is byte-identical, with no modal entry and no rotation slot for TRACE. (contract Section 3, item 3)
5. Given any existing game card, when clicked, then it behaves exactly as at `d5e8b63` (zero behavior change to existing games).

## Out of scope (NOT DOING)

No behavior change to any existing game. No touch to any other game file. No modal entry, no rotation slot, no GAME_ORDER change. No new precache entry beyond the single ./games/trace.html line. No copy change beyond the card and the header count.

## Dependencies

Depends on: Story 166 (same PR; the card links the file this story's sibling creates). Rider discipline: the CACHE_VERSION 35 to 36 bump rides this PR.

## Notes

Normative source is contract Section 3 (one card, three one-line edits, zero behavior change to existing games).
