# Story 149: Typewreck detail view with plays and best score (Session 67, P0, #268)

**Status:** Ready for development (Session 67, 2026-11-20).
**Author:** Quinn, Business Analyst.
**Priority:** P0. Issue #268, milestone M-3 batch; gates #215 close.
**Assigned to:** **Riven**, same PR as Stories 148 and 150 (Story 048 sole-owner protocol).
**Base commit:** `8430f1d` (main, v0.53.0 released).
**Scope:** `website/index.html` (`GAMES.typewreck` entry + card-to-modal mapping) and one new asset `website/assets/game-typewreck.png`. No `website/games/typewreck.html` edit.
**Design contract:** `flambeee-team/design-handoff.md`, Story 149 sections 1-8 plus pinned P1/P2/P3. Design-owned observable criteria live in contract section 7 and are NOT repeated here.

## Summary

Typewreck has no detail view today: its card is a plain Play link with no `GAMES` entry and no modal hook. Add `GAMES.typewreck` (name, desc, rules, `playLink: 'games/typewreck.html'`, real screenshot asset) and the card click mapping `games/typewreck.html` -> `typewreck`, so the card opens the detail modal like the other six games. The modal shows read-only `Plays` from `flambeee-typewreck-plays` and `Best score` from `flambeee-typewreck-best` (`{score, seed}`), under P1/P2. `GAME_ORDER` stays byte-identical at 6 entries: Typewreck is a modal surface only, not a GOTW rotation member (Story 125 ruling stands).

## Baseline measured at Session 67 planning (Wave 1, 2026-11-20)

| Check | Value |
|---|---|
| `GAMES` entries | 6; no `typewreck` entry, no modal hook |
| Typewreck card | plain Play link to `games/typewreck.html` |
| `GAME_ORDER` | `['cinder', 'wordfire', 'minesweeper', 'simon', '2048', 'afterglow']`, 6 entries |
| Keys on disk | `flambeee-typewreck-plays` (typewreck.html:133), `flambeee-typewreck-best` (:132, `{score, seed}`) |
| Screenshot asset | absent (no `website/assets/game-typewreck.png` today) |
| Rules source | shipped card desc + typewreck.html header comment lines 8-13 (no invented mechanics) |
| `GAME_ORDER` constraint | Story 125: byte-identical, Typewreck out of rotation until 2026-12-07 |

## Requirements

### 1. GAMES.typewreck entry
- `name`: Typewreck; `desc` verbatim from the shipped card: `Paste anything to raise a fortress wall, then wreck it with piercing shots.`
- `playLink: 'games/typewreck.html'`; modal Play button href equals `games/typewreck.html` (hard requirement: the button lands on the game).
- `screenshot: 'assets/game-typewreck.png'` with alt text describing the board; capture is deterministic Playwright at 1280x800 via `?seed=` + `?text=` + `?start=1`, neutral public-domain text (e.g. a pangram), no personal data.
- `rules` array, exactly these 6 lines, each traceable to the header comment or shipped setup/keys copy:
  1. `Paste text to raise a fortress wall; each character sets one block's HP`
  2. `Fire piercing shots from the bottom cannon in a straight line`
  3. `Each shot spends 12 damage traveling through blocks`
  4. `You get 28 shots per wall`
  5. `Clear every block to win; run out of shots and the wall stands`
  6. `Replay the same wall or paste new text for a new one`
- No other mechanics claimed. Damage falloff, combos, crits, anything not in the file must not appear.

### 2. Card-to-modal mapping
- Add mapping `games/typewreck.html` -> `typewreck`, same pattern as the six existing mappings. Card remains a `.game-card` with a Play link.
- Card click (or keyboard-activated Play-link click, Enter fires click) opens `openModal('typewreck')` instead of navigating. Middle-click / open-in-new-tab still navigates to `games/typewreck.html` by browser default (acceptable, same as the other six cards).
- Existing focus trap, Escape close, and focus return keep working for the new mapping. Tab order unchanged.

### 3. Stats reads (P1/P2)
- Per modal open, read-only: `localStorage.getItem('flambeee-typewreck-plays')` sanitized by the shared P2 helper (Story 148), plus `localStorage.getItem('flambeee-typewreck-best')` parsed as `{score, seed}`.
- Best is valid only when the parsed object has numeric `score` and `seed` present (mirror the game page's `loadBest` validity check), else absent. Seed is not displayed; modal shows the score only.
- Gate: EMPTY iff plays is 0/absent AND best is absent/null; existing empty copy unchanged. DATA iff plays > 0 OR (best valid AND best.score > 0). A best of exactly 0 with no plays is EMPTY.
- DATA row order: Plays first, Best score second. Labels exactly `Plays` and `Best score`.
- Plays > 0 with no best renders Plays row only. Valid best with no plays renders Best score row only (player who set a best before the plays counter shipped). Corrupt plays sanitizes to 0 per P2 while a valid best still surfaces. Corrupt best (`"junk"`, `{"score":"high"}`, missing seed) is absent; with plays also 0/absent the modal is EMPTY. Storage throwing treats both as absent; modal still opens.

### 4. Screenshot Plan B (graceful no-image modal)
- If a clean frame is impossible: ship the modal with the img hidden and no `src` pointing at a missing file (no 404, no broken glyph). Title, desc, rules, stats, and Play button intact; zero console errors from the modal.
- The asset then becomes a Palette-owned follow-up; #268 stays shippable on the imageless modal per the session-plan risk note. The PR states which path shipped (Plan A with asset, or Plan B imageless).
- Never ship a wrong-game or broken `<img>`.

### 5. Boundaries (P3 + structural)
- `GAME_ORDER` byte-identical: `['cinder', 'wordfire', 'minesweeper', 'simon', '2048', 'afterglow']`. Typewreck never appears as Game of the Week on any UTC date.
- No edits to `website/games/typewreck.html` or any other game file. No network, no aggregation, no identity, no new localStorage keys. Site never writes localStorage.

## Acceptance criteria (BDD, functional)

Design-owned observable criteria are in the design contract section 7 and are not repeated here.

1. Given the home page with the Typewreck card visible, when I click the Typewreck card Play link (or activate it by keyboard), then a detail modal opens with title `Typewreck`, the modal Play button href is `games/typewreck.html`, and the page has not navigated away. (mapping)
2. Given localStorage holds `flambeee-typewreck-plays` = 5 and `flambeee-typewreck-best` = `{"score": 120, "seed": "abc123"}`, when I open the Typewreck detail view, then I see a row labeled `Plays` with value `5` and a row labeled `Best score` with value `120`, in that order, and no empty message. (both rows)
3. Given a browser with no `flambeee-typewreck` keys, when I open the Typewreck detail view, then I see `Play your first round to see your stats here` with no `NaN`, no `undefined`, no exception. (P1 fresh)
4. Given plays = 5 with no best key, when I open the Typewreck detail view, then I see the Plays row only and no empty message. (plays-only)
5. Given a valid best (`{"score": 120, "seed": "abc123"}`) with no plays key, when I open the Typewreck detail view, then I see the Best score row only and no empty message. (best-only, pre-counter player)
6. Given best `{"score": 0}` (or seed present, score 0) with no plays, when I open the Typewreck detail view, then I see the empty message. (zero-best is EMPTY)
7. Given corrupt best values (`"junk"`, `{"score":"high"}`, `{"score": 50}` with missing seed) with no plays, when I open the Typewreck detail view, then I see the empty message and no error. (best validity check)
8. Given corrupt plays (`"not-json{{{"`, `-3`, `2.5`, over-cap integer) alongside a valid best, when I open the Typewreck detail view, then plays sanitizes to absent/0 per P2 while the Best score row still surfaces. (P2 plays-corrupt, best survives)
9. Given numeric-string plays (`"7"`), when I open the Typewreck detail view, then the Plays row reads `7`. (P2 numeric-string)
10. Given any UTC date, when the Game of the Week strip renders, then it names one of cinder, wordfire, minesweeper, simon, 2048, afterglow, and Typewreck never appears as Game of the Week; `git diff` shows `GAME_ORDER` byte-identical. (Story 125 structural)
11. Given the asset `website/assets/game-typewreck.png` exists (Plan A), when I open the Typewreck detail view, then I see a Typewreck board screenshot (fortress grid, cannon, HUD), the capture is 1280x800 deterministic (`?seed=` + `?text=` + `?start=1`, neutral text, no personal data), and the image alt text describes the board. Exactly one screenshot path ships and the PR states which.
12. Given the asset is absent (Plan B), when I open the Typewreck detail view, then no image box or broken-image icon appears, no 404 is raised, and the title, rules, stats block, and working Play button are all present. (graceful no-image)
13. Given keyboard-only use, when I open the Typewreck modal with Enter, trap Tab inside it, close with Escape, then focus returns to the invoking element. (a11y parity with existing six cards)
14. Given the stored best value before and after the modal open, when the modal renders a corrupt best or corrupt plays, then both stored values are byte-identical afterwards (read-only; site never writes localStorage).
15. Given issue #268 acceptance, when Scout runs a real browser on desktop and mobile, then the Typewreck modal renders the specified states with exact labels (`Plays`, `Best score`) and exact empty copy, with zero modal-attributable console errors.

## Issue #268 / #215 linkage

With Story 148, this story completes #268 acceptance for all three games (plays from existing keys, friendly empty state, game-page sanitize parity, real-browser QA, cache bump via Story 150). #215 closes only when this lands.

## Out of scope

Cinder/Afterglow rows (Story 148), cache bump + pattern-doc amendment (Story 150), `GAME_ORDER` change (forbidden), GOTW rotation membership (Typewreck stays out until 2026-12-07), any `website/games/*.html` edit, new storage keys, network/aggregation/identity.
