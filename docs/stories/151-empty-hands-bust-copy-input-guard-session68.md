# Story 151: EMPTY HANDS tells the truth at BUST and ignores modifier keys (Session 68, P0, #265)

**Status:** Ready for development (Session 68, 2026-11-21).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (user-visible; release gate for v0.55.0). Issue #265.
**Assigned to:** **Riven**, sole code owner (Story 048 protocol). One PR shared with the cache line only.
**Base commit:** `afbf411` (main, v0.54.0 released).
**Scope:** `website/games/empty-hands.html` (BUST title mapping in `showEnd()`, modifier-key guard in the keydown listener, dead `turn` removal, one deal-reset comment) plus exactly one line in `website/sw.js` (`CACHE_VERSION` 30 to 31). No other website bytes.
**Design contract:** `flambeee-team/design-handoff.md`, Story 151 sections 1-7 plus structural pins. Design-owned observable criteria live in contract section 6 and are mapped here; the functional AC below test the same behavior from the requirements side.

## Summary

The EMPTY HANDS end screen says `OUT OF COINS` for every BUST, even when the purse still holds coins but neither end is affordable. And pressing Ctrl+A during play fires a left-end gift (and can trip the browser select-all path). Fix both: the BUST title becomes a pure function of the purse at render time (`OUT OF COINS` only when the purse is 0, `PURSE SHORT` otherwise), and any gameplay key press carrying Ctrl, Cmd, or Alt is ignored before the game or the browser-default handling is touched. Same PR also removes the dead `turn` variable, adds one setup-vs-spend comment, and bumps the service-worker cache so returning visitors get the fixed file.

## Baseline measured at Session 68 planning (Wave 1, 2026-11-21)

| Check | Value |
|---|---|
| Base commit | `afbf411` |
| `showEnd()` BUST title | `elEndTitle.textContent = 'OUT OF COINS'` for every BUST (`website/games/empty-hands.html:351`) |
| BUST entry predicate in `give()` | neither end affordable, or purse <= 0 with coins left (`empty-hands.html:403`) |
| Keydown handler | tests `k === 'a' \|\| k === 'A'` with no `ctrlKey`/`metaKey`/`altKey` guard (`empty-hands.html:476`) |
| Dead `turn` variable | declaration at line 253, reset `turn = 1` in `startBoard()`, increment `turn += 1` in `give()`; zero read sites |
| Deal-reset assignment | `purse = purse0` in `startBoard()` |
| Tuning | `CONFIG` at `empty-hands.html:133-145`, `GIFT_ANIM_MS`/`SHRINK_ANIM_MS` 120/120; all frozen |
| `website/sw.js` `CACHE_VERSION` | 30 (line 21; bump to exactly 31) |
| `./games/empty-hands.html` precache | present (`sw.js:47`), so the game edit needs the bump |
| `GAME_ORDER` | byte-identical; no new storage key |

## Requirements

### 1. State-accurate BUST title (single source of truth)

- The title mapping lives in `showEnd()` as one expression, the only place the title is decided. No second copy of the BUST entry predicate anywhere.
- Exact rule (purse in coins, integer): `title = (kind == 'WIN') ? 'ROW CLEAR' : (purse == 0 ? 'OUT OF COINS' : 'PURSE SHORT')`.
- Binding table:

| kind passed to showEnd() | purse at render | elEndTitle (exact) | elEndLines | elAgain |
|---|---|---|---|---|
| WIN | any | `ROW CLEAR` | unchanged (`Board clear. Purse remainder N.`) | unchanged (`Next row (Enter)`) |
| BUST | 0 | `OUT OF COINS` | unchanged (`Run over. Score S, best B.`) | unchanged (`New run (Enter)`) |
| BUST | greater than 0 | `PURSE SHORT` | unchanged | unchanged |

- Purse is never negative by construction (`give()` only subtracts affordable costs), so the two BUST rows cover every reachable BUST.
- Plan B (only if the one-expression form cannot cover an unreachable purse state cleanly): `purse <= 0 ? 'OUT OF COINS' : 'PURSE SHORT'` for the BUST branch. Never a third title, never touch the entry predicate, never touch endLines copy.

### 2. Modifier-key guard on every gameplay key

- The guard is the first statement of the keydown listener, before any key dispatch and before any `preventDefault`.
- Exact rule: `guard = e.ctrlKey OR e.metaKey OR e.altKey`, evaluated first. Guard true means zero game mutation AND zero `preventDefault`: no `give()`, no `click()`, no advance. The browser keeps the shortcut.
- Covers every key the handler knows (a/A/d/D/arrows/Enter/space), not only A. Binding precedence:

| ctrlKey / metaKey / altKey | key | state | effect |
|---|---|---|---|
| any true | any handled key | any | return immediately; browser shortcut proceeds natively |
| all false | a / A / ArrowLeft | RUN | `give('L')`, with `preventDefault` (byte-identical to today) |
| all false | d / D / ArrowRight | RUN | `give('R')`, with `preventDefault` (byte-identical to today) |
| all false | Enter / space | TITLE / WIN / BUST | existing advance path with `preventDefault` (byte-identical) |
| all false | any handled key | non-playing state | no-op (unchanged) |
| all false | unhandled key | any | ignored (unchanged) |

- Shift is intentionally NOT a guard key: Shift+A plays exactly as A does today. CapsLock needs no rule: it only changes letter case, which the existing branches already cover.
- The guard reads the event and never latches: a stuck modifier (key-up lost while tab hidden) only affects presses carrying it; the next clean press plays normally.

### 3. Zero-behavior-change hygiene (same file, same PR)

- Delete the dead `turn` variable: declaration (line 253), reset `turn = 1` in `startBoard()`, increment `turn += 1` in `give()`. Zero read sites anywhere in the file; removal changes no behavior.
- Add one comment at the deal-reset assignment `purse = purse0` in `startBoard()` stating it is board setup, not a spend: the only purse mutation point stays `purse -= cost` in `give()`. Suggested literal: `/* deal reset, not a spend: the only purse mutation is give(). */`. Riven may reword as long as placement (that assignment) and content (setup vs spend) hold.

### 4. Cache bump (exactly one line, same PR)

- `CACHE_VERSION` 30 to 31 in `website/sw.js`, exactly one line. A missed bump (still 30) leaves returning visitors on the old title; 32 or any second `sw.js` change is wrong.

### 5. Boundaries

- No change to scoring, ladder, purse, slack, or any tuning constant. `GAME_ORDER` byte-identical. No new storage key. No animation change (`GIFT_ANIM_MS` 120 + `SHRINK_ANIM_MS` 120 unchanged).
- Exact copy strings only: `OUT OF COINS`, `PURSE SHORT`, `ROW CLEAR`. Plain punctuation, no em dash, no emoji.
- Out-of-scope items stay out (see Out of scope below).

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 6; AC-1 through AC-4 map them directly, the rest pin the functional behavior. Each is verifiable by a test.

1. Given level 1 dealt from run seed 3000 with worst-end play (purse starts 23, spends 22, purse remainder 1, neither end affordable), when the board busts, then the end title reads `PURSE SHORT`. (design: BUST with coins in purse)
2. Given level 1 dealt from run seed 3021 with cheapest-end play (purse starts 25, spends exactly 25, coins remain), when the board busts, then the end title reads `OUT OF COINS`. (design: BUST with empty purse)
3. Given a RUN board with an affordable left end, when I press Ctrl+A (likewise Cmd+A, Alt+A, and each of ctrl/meta/alt with D, arrows, Enter, and Space), then purse, row, and score are unchanged and no gift animation or message fires. (design: modifier guard; 18 no-op presses)
4. Given a RUN board with affordable ends, when I press A, D, ArrowLeft, ArrowRight without modifiers, then the corresponding end is gifted exactly as today, and Enter and Space still start, advance, and restart. (design: plain-key parity)
5. Given a BUST reached by tapping an unaffordable end, when the end screen renders, then the title follows the same (kind, purse) table; the entry path does not matter, only kind and purse at render.
6. Given `showEnd` called with WIN, when the end screen renders, then the title reads `ROW CLEAR` regardless of purse (the purse test applies only to non-WIN).
7. Given Ctrl+Enter or Alt+Space on an end screen, when I press it, then the game does not advance; plain Enter/Space still advances.
8. Given the merged tree, when I grep `website/games/empty-hands.html` for `turn`, then there are no matches (declaration, reset, and increment all removed, no dangling reference).
9. Given the merged tree, when I read the `purse = purse0` assignment in `startBoard()`, then it carries a comment stating it is setup, not a spend, and `give()` remains the only purse mutation point (`purse -= cost`).
10. Given `git diff main -- website/games/empty-hands.html`, when I inspect the title hunk, then the BUST title is decided by one expression in `showEnd()` and the BUST entry predicate in `give()` is byte-identical to base.
11. Given the merged tree, when I read `website/sw.js`, then `CACHE_VERSION` is 31 and `git diff main -- website/sw.js` shows exactly one changed line (30 to 31).
12. Given `git diff main --stat`, when I list changed website files, then only `website/games/empty-hands.html` and `website/sw.js` changed (zero other website bytes; `GAME_ORDER` byte-identical; no new storage key).
13. Given the full existing EMPTY HANDS harness on the branch, when it runs on both viewports, then it is green with zero page-attributable console errors.
14. Given a stuck-modifier state (modifier key-up lost while tab hidden), when I make the next clean press without modifiers, then it plays normally (guard never latches).

## Evidence the dev must paste (in the PR)

- Seed probes: L1 deal rows and spends for R=3000 (`[7,7,4,9,1,8,5,1]`, optimal 20, purse0 23, worst-end line spends 22, remainder 1, `endTitle === 'PURSE SHORT'`) and R=3021 (`[8,8,8,5,2,6,2,9]`, optimal 22, purse0 25, cheapest-end line spends exactly 25, `endTitle === 'OUT OF COINS'`), 2/2 exact strings.
- Modifier matrix result: {ctrl, meta, alt} x {a, d, ArrowLeft, ArrowRight, Enter, space} = 18/18 no-op presses with zero mutation of purse/row/score/state; parity set (plain a/d/arrows/Enter/space) replayed move-for-move identical to base.
- `sw.js` diff: exactly one line, 30 to 31.
- `grep -n turn website/games/empty-hands.html`: no matches.
- Existing harness green on both viewports, zero page-attributable console errors.

## Definition of done

- AC-1 through AC-14 all hold on the branch; titles 2/2 exact, modifier no-ops 18/18, parity move-for-move.
- PR contains only `website/games/empty-hands.html` and the one `website/sw.js` line; diff confirms zero other website bytes.
- Scout QA GO and Rook design review NO BLOCKING FINDINGS.
- Release wave reads back `CACHE_VERSION` 31 in the final tree.
- v0.55.0 may be cut on this story only if the BUST copy and the Ctrl+A guard both ship (session-plan release gate).

## Issue #265 linkage

This story carries the two user-visible #265 items: BUST says `OUT OF COINS` while the purse still holds coins, and Ctrl+A is unguarded so `A` fires the left end. Both gate v0.55.0 ("the only thing in the list a player can see").

## Out of scope

- `accepts()` invalid-level guard (#265 item 6; test surface only).
- L4+ human findability re-check (#265 item 2; needs release telemetry).
- Heuristic static scan and mirror-vs-page coverage (#265 items 9/10).
- #259.1 detail mislabel, #237/#238 manifest work, #206 Snapline, #217 cadence policy, any tuning change, any `GAME_ORDER` change, any new storage key, `BLOG.md`, release notes, Bluesky staging.
