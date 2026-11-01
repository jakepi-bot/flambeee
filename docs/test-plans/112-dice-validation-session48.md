# Test Plan: Story 112 Dice Invalid-Input Validation (Session 48)

**Story:** `docs/stories/112-dice-validation-session48.md` (P1, v0.41.0 vehicle, gated on green).
**Owner:** Riven (single owner: `website/apps/dice.html` + `CACHE_VERSION` line). **QA:** Scout. **PR:** #190, branch `riven/story-112-dice-validation`, base `e63dc9c`, head `5fcc0c2`.
**Artifact:** validation note on `website/apps/dice.html`, Story 098 timer shape, plus CACHE 16 to 17.

## Scope
In scope: `website/apps/dice.html` (the one validation item: parse/invalid-sides plus Roll correct-plus-note, change listener persist-only) and the one `CACHE_VERSION` bump line in `website/sw.js`. Out of scope: every other app file, every game, `src/`, `games/`, `GAME_ORDER`, site cards, precache entries, schedule, noon, `pending-post.txt`, checker scripts, FPS probe. Any diff there fails this plan.

## Checks (each maps to an AC / BDD scenario)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Riven named pre-wave (Sc 1) | Dev record + `gh pr view` | Riven holds app file + CACHE line, Ember product owner |
| 2 | AC-2 | Empty sides corrects to 2 with note (Sc 2) | Clear field, real Roll click | Status `Enter 2 to 100 sides. Using 2.`, field `2`, label `d2 rolled r` |
| 3 | AC-3 | Sides 1 corrects to 2 with note (Sc 3) | Type `1`, real Roll click | Status `Enter 2 to 100 sides. Using 2.`, field `2`, `d2` roll |
| 4 | AC-4 | Sides 101 corrects to 100 with note (Sc 4) | Type `101`, real Roll click | Status `Enter 2 to 100 sides. Using 100.`, field `100`, `d100` roll |
| 5 | AC-5 | Sides 7.5 corrects to 7 with note (Sc 5) | Type `7.5`, real Roll click | Status `Enter 2 to 100 sides. Using 7.`, field `7`, label `d7 rolled r` |
| 6 | AC-6 | Valid integer (20) rolls clean (Sc 6) | Type `20`, real Roll click | No note, field untouched `20`, label `d20 rolled r` |
| 7 | AC-7 | Persistence `{sides,last}` under `flambeee-apps-dice` only (Sc 7) | Read localStorage after runs + reload | Keys exactly `sides,last`; no new field or key |
| 8 | AC-8 | CACHE 16 to 17, dice precache line byte-identical (Sc 8) | `git diff` vs base + read `website/sw.js` | Version line 16 to 17, `  './apps/dice.html',` unchanged, no other precache change |
| 9 | AC-9 | Diff limited to app file + bump line (Sc 9) | `git diff --stat` vs `e63dc9c` | Exactly 2 files: `website/apps/dice.html` + `website/sw.js` (1 line) |
| 10 | AC-10 | Desktop 1280x800 real-input 5/5, overflow 0, zero page errors (Sc 10) | Static serve + headless Chromium, typed input + clicks | Exit 0, 5/5, overflow 0, page-attributable errors 0 |
| 11 | AC-11 | Mobile 375x667 real-input 5/5, overflow 0, zero page errors (Sc 11) | Same driver at 375x667 | Exit 0, 5/5, overflow 0, page-attributable errors 0 |
| 12 | AC-12 | RED exit 1 on base then GREEN exit 0 on merged tree | Same five-case script on base `e63dc9c` then PR head | RED 1/5 exit 1 (decimal anchor fails); GREEN 5/5 exit 0 |
| 13 | AC-13 | Release-gate rule recorded (Sc 12) | Dev record + qa-results | Green keeps v0.41.0 on table, slip means no tag |
| 14 | AC-14 | Copy tone | grep new lines for em dash / heavy emoji | 0 em dashes, no heavy emoji |
| 15 | Neg | Blur-change does not wipe the Roll note | Type invalid, blur, click Roll, read status | Note still present after Roll click |
| 16 | Edge | Boundary 2 and 100 roll clean | Type `2`, type `100`, Roll each | No note, fields untouched |

## Result (Scout independent re-run, 2026-11-01)
Driver: `s48qa` probe (playwright-core + system chromium `/usr/bin/chromium`), own static serves, real `pressSequentially` typed input plus real Roll clicks on both viewports. Pass/fail counts and full output in `flambeee-team/qa-results.md`.
