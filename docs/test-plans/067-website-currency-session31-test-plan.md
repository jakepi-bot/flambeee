# Test Plan — Story 067: Website currency and deploy mirror verification, Session 31 (P2)

**Story:** `docs/stories/067-website-currency-session31.md`
**Handoff:** `flambeee-team/requirements-handoff.md` (Session 31)
**QA:** Scout, 2026-10-15. **Target:** v0.29.0. No em dashes, plain punctuation.
**Rule:** checker `scripts/verify-website-currency.sh` is frozen, never modified.

## Scope

Standing two-run check that the live site (`/home/jake/share/Flambeee/`), the repo
mirror (`website/` + `src/` game files), and the release tag agree. No new code.

**Known entering defect:** the frozen checker hardcodes the stale live path
`/home/jake/.openclaw/workspace/share/Flambeee/index.html`, so it exits 1 on the
precondition before checking anything. Real live path is `/home/jake/share/Flambeee/`.
QA runs the checker verbatim (evidence) plus real-path equivalents by hand.

## Cases

| ID | What | Command | Expectation |
|----|------|---------|-------------|
| 067-R1 | run 1, checker verbatim pre-merge | `bash scripts/verify-website-currency.sh; echo EXIT:$?` | exit 0 (expected FAIL on stale path; recorded honestly) |
| 067-M1 | index mirror byte-identity | `cmp /home/jake/share/Flambeee/index.html website/index.html` + sha256 pair | cmp exit 0, equal sha256 |
| 067-M2 | sw.js mirror + version | `cmp` + `CACHE_VERSION` line from both sw.js files | cmp exit 0, versions agree |
| 067-M3 | game-file mirrors | `cmp src/<g>.html` vs live `games/<g>.html` for all 6 | all 6 cmp exit 0 |
| 067-P1 | Play links | 6 `games/*.html` hrefs, all targets exist | 6/6 |
| 067-G1 | GAME_ORDER | rotation list covers all 6 incl. afterglow | 6/6 |
| 067-H1 | heading vs tag | What's New heading names latest tag | run 1: v0.28.0 vs v0.28.0 |
| 067-C1 | checker unmodified | `git diff --stat -- scripts/verify-website-currency.sh` empty | AC-6 |
| 067-R2 | run 2 post-tag | checker + full mirror set after v0.29.0 tag + sync | exit 0, deferred to release wave |

## Baseline at planning (2026-10-15 07:25 CDT)

Heading "Six games, one arcade", 6 cards, What's New v0.28.0, GAME_ORDER 6/6,
6 Play links, CACHE_VERSION 6 both sides, cmp exit 0 on index/sw.js/all 6 games,
latest tag v0.28.0, 0 open issues, 0 open PRs.

## Results

Filled in qa-results.md with actual pasted output. Run 2 (067-R2) is deferred:
no v0.29.0 tag exists and no Story 066 merge has happened, so run 2 belongs to the
release wave (Riven owner, Scout may execute).
