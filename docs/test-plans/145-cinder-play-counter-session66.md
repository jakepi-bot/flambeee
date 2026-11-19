# Test plan: Story 145 Cinder play counter (Session 66)

Owner: Scout. Status: written 2026-11-19, before Riven's branch exists.
Base: `0626fab`. Cinder sha256 at base:
`b41740744ac418bd73a242873eb8cfd9922969ebba1124d899b35eefc4ebaee8`.
`CACHE_VERSION` reads 28 at `website/sw.js:21` on base; 29 expected on head.
Branch under test: `feat/session66-cinder-play-counter` (Riven, sole code owner).

## Harness contract (applies to every scenario below)

- Serve from a detached worktree, never the main working tree:
  `git fetch origin feat/session66-cinder-play-counter`
  `git worktree add --detach /home/jake/.hermes/profiles/flambeee/cache/scratch/scout-session66 origin/feat/session66-cinder-play-counter`
  Serve the worktree's `website/` dir:
  `env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python -m http.server 8971`
  (from the worktree `website/` dir; port-scoped; stop only with
  `pkill -f "http.server 8971"` or `fuser -k 8971/tcp`).
- Playwright with the venv python (`/home/jake/.hermes/flambeee/.venv/bin/python`),
  chromium preferred, fallback to any installed browser. Fresh browser context
  per scenario. Viewport 1280x800 unless a scenario says 375x667.
- REAL input on the happy path: type the name into `#promptInput` and press
  Enter; select menu rows by clicking `.menu-row[data-action="N"]` or typing the
  number + Enter. No synthetic state injection for scenarios S01-S07, S12.
- Seeded storage (S06, S09-S11) uses `context.add_init_script()` with an
  INVOKED IIFE, e.g. `(function(){ localStorage.setItem('flambeee-cinder-plays','41'); })();`,
  and the script asserts the seed took hold (reads the value back) before
  trusting the result.
- Blocked storage (S08) uses `add_init_script` to redefine
  `localStorage.getItem`/`setItem` to throw, then asserts the override took
  hold (a probe write MUST throw) before trusting the absent key or absent error.
- Collect console messages + page errors on every scenario; filter favicon and
  network noise; list anything attributable to the page.
- Overflow check where stated:
  `document.documentElement.scrollWidth <= window.innerWidth`.
- Screenshots of key states go to the scratch dir when useful.
- RED anchors (S14) run against base `0626fab` extracted to the scratch dir.

## Town flow used by scenarios

Fresh profile lands on character creation (`showCharacterCreation`).
Type name `Scout` + Enter -> `createCharacter('Scout')` -> town square.
Town row `1` = Wilderness (`enterWilderness()`); row `2` = Weapon Shop.
Encounter resolves ~800ms after entry (`setTimeout(encounter, 800)`); wait for
the plays line text change or a fixed 2s before asserting.
Wilderness menu row `1` = Continue Exploring (re-entry, new counted entry);
row `2` = Return to Town.

## Scenarios

### S01 — fresh profile shows 0 (AC-1)
Given a fresh browser context with empty storage,
when `website/games/cinder.html` loads,
then the persistent shell beside `#statusLine` (outside `#display`) shows
exactly `Plays on this browser: 0` with no interaction.
Assert: element exists, text exact, `localStorage` untouched by the load itself.

### S02 — first wilderness entry reads 1 (AC-2)
Given S01 state with character `Scout` created (town square, count 0),
when the player enters the wilderness once (row 1, real click/Enter) and the
encounter deals,
then the shell reads exactly `Plays on this browser: 1`.
Assert: `localStorage['flambeee-cinder-plays'] === '1'`. Zero page-attributable
console errors.

### S03 — second entry reads 2 (AC-3)
Given S02 at 1 (back in town via wilderness row 2 or town return),
when the player enters the wilderness again and the encounter deals,
then the shell reads exactly `Plays on this browser: 2`.

### S04 — neutral renders do not change the count (AC-4)
Given a counted total of 2,
when each of these renders in turn: town menu re-render, weapon shop visit
then leave, character creation render on a second profile path is N/A
(use `createCharacter` on a fresh context at count 0 and assert still 0),
then the line does not change after any of them.
Welcome-back render: seed a stale day record (yesterday's UTC `dayIndex`) with
a stored count of 2, load, assert the welcome-back panel shows and the line
still reads 2.
Assert every step; any increment here is a defect.

### S05 — reload and tab restore do not change the count (AC-5)
Given a counted total of 2,
when the page reloads (3 cycles, asserting `Plays on this browser: 2` after
each) and when a second tab restores/loads the same origin without entering,
then the line still reads 2 every time.
Assert `localStorage` still `2` after all cycles.

### S06 — daily cap 15/15 blocks with no increment (AC-6)
Given seeded storage: count `5` plus a day record with `fightsUsed: 15`
(seeded via invoked-IIFE `addInitScript`; assert both seeds took hold),
when the player selects Wilderness (row 1),
then the out-of-fights log (`You are out of fights for today...`) appears,
the town menu returns, and the line still reads
`Plays on this browser: 5`. Repeat the selection twice more; count stays 5.

### S07 — treasure re-entry counts again (AC-7, known consequence)
Given a counted entry that deals a non-combat treasure event
(repeat entries until `Found ... gold!` appears in the log; cap attempts at 10
and record the attempt count),
when the player returns to the wilderness menu and enters again
(Continue Exploring) and the encounter deals,
then the count increments again (N -> N+1 on the re-entry).
This is the stated consequence, not a defect; the PR body must state it.

### S08 — blocked storage counts in memory, silent (AC-8)
Given `addInitScript` that redefines `localStorage.getItem`/`setItem` to throw,
and a probe write that MUST throw (assert the block took hold),
when the player creates a character and enters the wilderness twice,
then the line reads 1 then 2 in memory, no error note appears
(`#storageNotice` counter path adds none; the Story 066 save/day notice path
is not triggered by the counter), and zero page-attributable console errors.
Assert no `flambeee-cinder-plays` key is readable.

### S09 — corrupt values sanitize to 0 then 1 (AC-9a)
Matrix, one fresh context per value, seed via invoked IIFE, assert seed held:
`"abc"`, `-5`, `3.5`, `null` (literal JSON null).
When the page loads, the line shows `Plays on this browser: 0` (never garbage);
when the player creates a character and enters the wilderness once,
the line shows 1 and storage holds `1`.

### S10 — numeric string "41" accepted (AC-9b)
Given seeded `"41"`,
when the page loads, the line shows `Plays on this browser: 41`;
when the player enters the wilderness once, the line shows 42.

### S11 — large persisted value increments (AC-10)
Given seeded `999999999` (assert seed held),
when the page loads, the line shows `Plays on this browser: 999999999`;
when the player enters the wilderness once, the line shows `1000000000`.

### S12 — viewports, zero horizontal overflow (AC-11)
Given the shell with a counted total (e.g. 2),
when rendered at desktop 1280x800 and mobile 375x667,
then the plays line is fully visible with zero horizontal overflow on both:
`document.documentElement.scrollWidth <= window.innerWidth` at each width.
Do a full happy-path entry at 375x667 too (create + 1 entry) and re-check.

### S13 — cache version + no-network on the merged tree (AC-12, AC-13)
Given the PR head worktree,
when `website/sw.js` is read, `CACHE_VERSION` is 29 (line 21) and
`./games/cinder.html` remains in `PRECACHE_URLS` (no entry added/removed);
when the diff against base is grepped:
`git diff 0626fab...HEAD -- website/ | grep -Ei 'fetch\(|XMLHttpRequest|sendBeacon|WebSocket|https?://'`,
then zero hits. Paste the exact commands and their output in qa-results.md.

### S14 — RED anchors on base 0626fab (AC-14)
Given `git show 0626fab:website/games/cinder.html` extracted to the scratch dir,
when the file is grepped and the extracted page loads in a fresh context,
then `flambeee-cinder-plays` is absent from file and DOM and
`Plays on this browser` is absent from file and DOM.
A GREEN here means testing the wrong build; stop and re-verify the worktree.

## Story 146 gate (head run, Scout evidence)

From a clean checkout of the PR branch (the detached worktree), full
unfiltered, exact command:

```
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python scripts/run-cinder-family.py --port-base 8972
```

Required: `family: 19/19 scripts passed`, tally
`pass=19 fail=0 skip=0 total=19` with the `19==19` assert, `baseline: MATCH`,
exit 0, no `--include`/`--exclude`. Save full output to
`flambeee-team/runs/2026-11-19/cinder-family-head-scout.log`; base log for
comparison is `flambeee-team/runs/2026-11-19/cinder-family-base.log`
(19/19, MATCH, exit 0). Any new head failure against base is NO-GO.

## Verdict mapping

GO only if: S01-S14 all pass on the head worktree, family head run is
19/19 MATCH exit 0 unfiltered, diff matches the ownership map (five insertions
in `website/games/cinder.html`, `sw.js` line 21 only, `docs/play-counter-pattern.md`
append only), hook sits after the failed-start gate and before
`setTimeout(encounter, 800)`, one key only, line outside `#display`, exact copy,
no network APIs, cache 29, PR body cites M-4/#216 with both family runs.
Any miss is named in qa-results.md with severity and reproduction steps;
any new head family failure against base is an automatic NO-GO.
Checks not run are listed explicitly as not run, never claimed.
