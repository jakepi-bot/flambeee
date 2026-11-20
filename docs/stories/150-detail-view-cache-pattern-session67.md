# Story 150: Cache bump + pattern-doc detail-view section (Session 67, P1, #268)

**Status:** Ready for development (Session 67, 2026-11-20).
**Author:** Quinn, Business Analyst.
**Priority:** P1 (ships in the same Riven PR as P0 Stories 148/149; the cache line is load-bearing for #268 acceptance).
**Assigned to:** **Riven**, same PR.
**Base commit:** `8430f1d` (main, v0.53.0 released).
**Scope:** `website/sw.js` exactly one line (`CACHE_VERSION` 29 to 30) + `docs/play-counter-pattern.md` new detail-view section. No other website bytes.
**Design contract:** `flambeee-team/design-handoff.md`, Story 150 sections 1-7 plus pinned P1/P2/P3. Design-owned observable criteria live in contract section 6 and are NOT repeated here.

## Summary

One-line cache invalidation so visitors receive the shell with the new detail-view plays rows, plus the durable record of the detail-view rule (three shipped counters, read-only site rule, shared sanitize, empty state, modal-not-rotation note) so the next reader never re-derives these decisions. Without the bump, the old shell persists and the new rows silently do not appear (versioned-out state, not a bug).

## Baseline measured at Session 67 planning (Wave 1, 2026-11-20)

| Check | Value |
|---|---|
| `website/sw.js` `CACHE_VERSION` | 29 (line 21; re-read at build time, fix to exactly 30) |
| Pattern doc | `docs/play-counter-pattern.md`; no detail-view section today |
| Shipped counters | `flambeee-cinder-plays`, `flambeee-afterglow-plays`, `flambeee-typewreck-plays` (+ `flambeee-typewreck-best` `{score, seed}`) |

## Requirements

### 1. Cache bump (exactly one line)
- `CACHE_VERSION_new = CACHE_VERSION_old + 1 = 29 + 1 = 30` in `website/sw.js`. Exactly one changed line; no other `sw.js` bytes, no other website bytes outside `website/index.html`, the screenshot asset, and this doc section.
- Release wave reads the file back (expected 30). Bump of 31 is wrong; a missed bump (still 29) fails the tree.

### 2. Pattern-doc section (six required statements)
New section in `docs/play-counter-pattern.md` carrying:
1. The three plays keys: `flambeee-cinder-plays`, `flambeee-afterglow-plays`, `flambeee-typewreck-plays` (plus `flambeee-typewreck-best` `{score, seed}` for the Typewreck best row).
2. The read-only site rule: `website/index.html` never writes localStorage; corrupt values display as absent and are never repaired.
3. The shared sanitize rule (P2 verbatim, with cap 9007199254740991).
4. The empty-state rule (P1 verbatim, with exact copy `Play your first round to see your stats here`).
5. The modal-not-rotation note: Typewreck is a `GAMES` modal surface; `GAME_ORDER` stays 6 entries (Story 125 ruling stands).
6. Conflict rule: where the doc and a shipped game file disagree, the game file wins (established pattern-doc rule).

### 3. Boundaries (P3)
- No edits to `website/games/*.html`, `BLOG.md`, release notes, Bluesky staging. No network, aggregation, identity, new keys.
- If the docs amendment cannot land in the product PR, it may ride Quinn's docs PR (docs-only), but the cache line stays with the product PR. Never bump cache in a docs-only PR without product bytes.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 6 and are not repeated here.

1. Given the merged tree, when I read `website/sw.js`, then `CACHE_VERSION` is 30. (bump value)
2. Given `git diff main -- website/sw.js`, when I count changed lines, then exactly one line changed (`29` -> `30`). (one-line scope)
3. Given `docs/play-counter-pattern.md` on the branch, when I read the new section, then it names all three plays keys and the Typewreck best key with its `{score, seed}` shape. (doc keys)
4. Given the same section, when I read it, then it states the read-only rule (never writes localStorage; corrupt displays as absent, never repaired). (doc read-only)
5. Given the same section, when I read it, then it states the sanitize rule with the cap 9007199254740991 (integer 0..cap accepted, numeric strings accepted, everything else 0). (doc sanitize)
6. Given the same section, when I read it, then it states the empty-state rule with the exact copy `Play your first round to see your stats here` and the plays-alone-flips consequence. (doc empty-state)
7. Given the same section, when I read it, then it states the modal-not-rotation note (`GAMES` modal surface; `GAME_ORDER` 6 entries; Story 125 stands). (doc structural)
8. Given a visitor holding the stale shell (version 29), when the bumped shell (30) activates, then the new shell caches on next visit with no other cache-behavior change; a missed bump leaves the old shell with no rows (versioned-out, not a bug). (cache semantics)
9. Given issue #268 acceptance, when the release wave reads back the tree, then `CACHE_VERSION` is 30 and the diff holds no other `sw.js` bytes. (release read-back)

## Issue #268 / #215 linkage

The cache line is part of #268 acceptance (CACHE_VERSION bump). The doc section is the durable record Rook's contract requires; game-page conflicts resolve in favor of the shipped game file.

## Out of scope

Any `website/index.html` behavior beyond what Stories 148/149 specify, any game-file edit, any second cache change, version bumps elsewhere, release notes, blog, Bluesky, GOTW or `GAME_ORDER` changes.
