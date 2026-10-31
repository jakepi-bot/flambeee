# Test Plan: Story 111 Echo-Rounds Site Integration (Session 47)

**Story:** `docs/stories/111-echo-rounds-site-session47.md` (P2, rides with 110, same PR by construction).
**Owner:** Riven. **QA:** Scout. **PR:** #187, branch `riven/story-110-111-echo-rounds`, base `27d6d43`.
**Surfaces:** one card in `website/index.html`, CACHE 15 to 16, one precache line.

## Scope
In scope: at most one site card, the one `CACHE_VERSION` bump line, at most
one `sw.js` precache entry line, release-wave heading line. Out of scope:
game logic (Story 110 owns it), checker scripts (run, do not edit), apps,
schedule, noon, pending-post.txt, probe, jobs, cron. Any diff there fails.

## Checks (each maps to an AC / BDD scenario)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Single owner Riven holds 110+111 in one PR (Sc 1) | `gh pr view` + dev record | Owner named, one PR for both stories |
| 2 | AC-2 | Exactly one new card, game-card pattern, target resolves (Sc 2) | Read index diff; GET target over local serve; click card | 1 card block, `games/echo-rounds.html` 200 + title |
| 3 | AC-3 | CACHE 15 to 16, exactly one new precache line after convert line, no other precache change (Sc 3) | `git diff` on `website/sw.js` | 1 version line, 1 added entry verbatim |
| 4 | AC-4 | Scope guard (Sc 4) | `git diff --name-only` vs base | At most card + bump + entry (+ 110 game file) |
| 5 | AC-5 | Desktop 1280x800 real-input green, zero page errors (Sc 5) | Serve + Chromium, card click + game drive | Card resolves, game plays, 0 page errors |
| 6 | AC-6 | Mobile 375x667 real-input green, overflow 0 index + game (Sc 6) | Same at 375x667 | 0 overflow both pages, 0 page errors |
| 7 | AC-7 | Checker Run 1 pre-merge recorded with Check 8 PASS; Run 2 post-tag owned by release wave (Sc 7) | Run `scripts/verify-website-currency.sh` on PR tree | Exit code + per-check lines recorded; only Check 1 fail (live-vs-mirror, environmental) |
| 8 | AC-8 | What's New names v0.40.0 post-cut, one-line entry, no cache/controller talk (Sc 7) | Post-tag check (release wave) | Heading + entry present; pre-merge heading stays v0.39.0 |
| 9 | AC-9 | No gamepad/controller/pointer-lock claim in card, entry, dev record, release post | grep all four surfaces | 0 claims; gate stays OPEN-BLOCKED-ON-HARDWARE |
| 10 | AC-10 | CACHE reads 16 on merged tree, game precache line present | grep merged tree | `var CACHE_VERSION = 16`, `'./games/echo-rounds.html'` in PRECACHE_URLS |
| 11 | AC-11 | Gate rule: green keeps cut on table, slip means no tag, no cut for card alone (Sc 8) | Dev record + qa-results | Rule recorded |
| 12 | AC-12 | Copy tone | grep for em dash / heavy emoji | 0 em dashes, no heavy emoji |
| 13 | Neg | GAME_ORDER untouched (card-only accepted) | `git diff` GAME_ORDER lines | 6-entry rotation unchanged unless one-line reason stated |
| 14 | Edge | Served-vs-mirror mismatch is the new card line only (environmental until live sync) | Checker output + cmp detail | Mismatch at card lines; target file exists in tree |

## Result (Scout independent re-run, 2026-10-31)
Driver: own script, own static serve, playwright-core with cached Chromium,
real keydown plus real clicks on both viewports; checker run unmodified from
the PR worktree. Pass/fail counts and full output in
`flambeee-team/qa-results.md`.
