# Test plan 153-154: EMPTY HANDS play counter + proof gate (Session 69)

Scope: Story 153 (Riven, P0, `website/games/empty-hands.html` + `website/sw.js:21`
+ `docs/play-counter-pattern.md` §9) and Story 154 (Kai, P1b,
`dev/empty-hands-proof.py` gate8 only). Base `24f89c2`. Verified on the
integrated tree (153 + 154 merge) in a detached scratch worktree.

## Commands

```sh
cd /home/jake/.hermes/flambeee/flambeee && git fetch origin
git worktree add --detach /home/jake/.hermes/profiles/flambeee/cache/scratch/s69-qa origin/feat/session69-153-empty-hands-play-counter
# in worktree:
git merge --no-ff origin/feat/session69-154-proof-counter-gate -m 'QA integration: 153+154'
# scope audit
git diff --stat 24f89c2...origin/feat/session69-153-empty-hands-play-counter   # exactly 3 files
git diff --stat 24f89c2...origin/feat/session69-154-proof-counter-gate        # exactly 1 file
git diff 24f89c2...origin/feat/session69-153-empty-hands-play-counter -- website/index.html  # empty
# shipped harness (full, both viewports)
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/empty-hands-proof.py
# narrowing
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/empty-hands-proof.py --sim-only        # SKIPPED, exit 3
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/empty-hands-proof.py --viewport=bogus  # FAIL, exit 1
# independent QA (own script, own server :8943, real Chromium, fresh profile/case)
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python /home/jake/.hermes/profiles/flambeee/cache/scratch/s69-qa-scout.py
```

Thresholds: full harness exit 0, every CHECK PASS, zero page-attributable
console errors both viewports; narrowing exits 3/1 as above; independent
script 100% QA-PASS.

## Story 153 cases (each at 1280x800 and 375x667 unless noted)

1. Fresh boot: HUD parent line exactly `Plays on this browser: 0`,
   `__empty.plays()===0`, TITLE visible, zero console/page errors, no
   horizontal overflow (`scrollWidth <= innerWidth`).
2. Start click: line `1`, probe 1, `localStorage` JSON number `1`, state RUN
   on the identical seed/board dealt at boot.
3. Reload mid-run: line unchanged, lands TITLE, no increment.
4. WIN via solver play, `Next row (Enter)`: plays unchanged, RUN level 2.
5. BUST via worst-end play, `New run (Enter)`: exactly +1, fresh seed,
   level-1 RUN. Repeat restart via Enter key: exactly +1.
6. #276: BUST title `OUT OF COINS` when purse 0, `PURSE SHORT` when coins
   remain but neither end affordable (reached via simulated-then-real play).
7. Blocked storage (`Storage.prototype` get/set throw): Start works, line
   shows in-memory 1, no user error, no page error.
8. Double-click Start: exactly +1. Enter auto-repeat on TITLE: exactly +1.
9. `__empty.reset()`: TITLE, no increment.
10. Corrupt seeds (`abc`, `-1`, `1.5`, `null`, `1e999`,
    `99999999999999999999`, `{bad json`): boot 0, silent. Numeric `"3"`:
    boots 3, Start goes 4. Cap `9007199254740991`: Start stays at cap.
    Quota write-fail: in-memory increment, silent. Cleared storage: restarts 0.
11. Static: one `bumpPlays()` call site inside `enterRun()`; Start and BUST
    restart both route through it; `give`/`endBoardWin`/`endRunBust`/`render`/
    `newRun`/`advance`/`showEnd`/`startBoard` clean; HUD element inside `.hud`
    outside `#panel`; no end-panel plays line; `sw.js` one-line 31→32;
    pattern-doc §9 carries counting unit, boot-deal nuance, display rule,
    key/cap/helpers, WIN-advance non-count; probe delta exactly +`plays()`;
    GAME_ORDER byte-identical; only keys `...-best` + `...-plays`.

## Story 154 cases

1. Full run integrated tree: gate8 PASS both viewports, exit 0.
2. Mutation: new harness vs pre-153 file: gate8 FAIL both viewports
   (`no #plays line on fresh boot`), gates 1-7 PASS, exit 1.
3. `--sim-only`: SKIPPED browser leg, exit 3. `--viewport=bogus`: FAIL exit 1.
   Game file absent: RED exit 2. FAIL dominates SKIP.
4. Static: `dev/empty-hands-proof.py` only; gates 1-7, baseline, manifest
   behavior-identical; `gate8` present; zero website bytes.
