# Test Plan: Story 084 Website Currency Session 37 (Run 1 only)

Source: `docs/stories/084-website-currency-session37.md`. P2 standing
verification, no new code, checker frozen. Base `00b5441`. Run 1 executed by
Riven (no branch, no PR) and independently re-run by QA. Run 2 explicitly
out of scope (not attempted; needs the tag plus the serving host).

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee` on `origin/main`
  (`00b5441`).
- `git diff --stat -- scripts/verify-website-currency.sh` => empty (checker
  frozen, AC-7). Verified by QA from disk.

## Cases

1. T1 Run 1 pre-merge. `bash scripts/verify-website-currency.sh; echo
   CHECKER_EXIT:$?`. Expect exit 1 with `FAIL: live file not found`.
   Got exactly Riven's recorded output (see below). PASS (matches dev
   record verbatim).
2. T2 Live-path measurement. `ls -la /home/jake/share/Flambeee/` => `No such
   file or directory`, exit 2. `/home/jake/share/` itself exists (no
   Flambeee entry). Mirror status deferred to the serving host, not phrased
   as a pass. PASS.
3. T3 Heading vs tag. `website/index.html` line 742
   `<h3>v0.33.0: Day Pad cache fix, returning visitors get the count</h3>`
   vs origin newest tag v0.33.0 (resolved live via `git ls-remote --tags
   origin`): MATCH. PASS.
4. T4 Play links measured. 6 unique relative targets
   (`games/2048.html, games/afterglow.html, games/cinder.html,
   games/minesweeper.html, games/simon.html, games/wordfire.html`); every
   target exists under `website/games/`. PASS.
5. T5 GAME_ORDER plus Apps entry. `GAME_ORDER` at `website/index.html:1127`
   is `['cinder', 'wordfire', 'minesweeper', 'simon', '2048', 'afterglow']`,
   6/6 including afterglow. `website/apps/index.html` present with count
   label `0/280`, `var PREFIX = 'flambeee-apps-';` (line 121),
   `maxlength="280"` (line 103). PASS.
6. T6 CACHE_VERSION baseline. `website/sw.js` line 21
   `var CACHE_VERSION = 9;` (baseline 9, unchanged by this docs-only wave).
   Run-2 agreement from both sides deferred. PASS.
7. T7 Run 2 not attempted. PASS (scope guard).

## Real output (QA re-run, main `00b5441`, 2026-10-21)

```
== Story 038: website currency + mirror byte-identity ==
live   : /home/jake/share/Flambeee/index.html
mirror : /home/jake/.hermes/flambeee/flambeee/website/index.html

FAIL: live file not found: /home/jake/share/Flambeee/index.html

RESULT: FAIL (1 check(s) failed)
CHECKER_EXIT=1
```

```
ls: cannot access '/home/jake/share/Flambeee/': No such file or directory
LS_EXIT=2
```

## Verdict

7/7 QA cases pass. Run-1 FAIL is the known environmental live-path absence
(same as Sessions 31-36), not a repo defect. AC-1, AC-4, AC-5, AC-6, AC-7
hold pre-merge. AC-2/AC-3 (post-tag Run 2, cmp plus sha256) deferred to the
release wave by design.
