# Test Plan: Story 093 Website Currency Session 40 (Run 1 only)

Source: `docs/stories/093-website-currency-session40.md`. P3 standing
verification, no new code, checker frozen. Base `7c1f2b9`. Run 1 executed
by Riven (no branch, no PR); QA independently re-runs. Run 2 is N/A by
design (no release this session, no v0.35.0 cut).

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee` on `origin/main`
  (`7c1f2b9`).
- `git diff --stat -- scripts/verify-website-currency.sh` must be empty
  (checker frozen, AC-6). Verified by QA from disk.

## Cases

1. T1 Run 1 pre-merge (AC-1, Scenarios 1, 6).
   `bash scripts/verify-website-currency.sh; echo CHECKER_EXIT:$?`.
   Expect exit 1 with `FAIL: live file not found:
   /home/jake/share/Flambeee/index.html`. The live-path absence is the
   known environmental finding, not a repo defect.
2. T2 Run 2 N/A (AC-2, Scenario 2). No post-tag check, no sync, no tag
   resolution. PASS by scope guard; QA does not attempt it.
3. T3 Play links measured (AC-3, Scenario 3). 6 relative `games/*.html`
   links recorded with targets, every target existing under
   `website/games/`.
4. T4 GAME_ORDER plus Apps entry (AC-4, Scenario 4). `GAME_ORDER` read at
   run time (6/6 including afterglow expected) and `website/apps/index.html`
   present with N/280 count, `flambeee-apps-` prefix, maxlength 280,
   Saved-clear-on-input noted.
5. T5 CACHE_VERSION baseline (AC-5, Scenario 5). `website/sw.js` line 21
   reads `var CACHE_VERSION = 10;`, unchanged by this docs-plus-harness
   wave.
6. T6 Live-path measurement (AC-1, Scenario 6).
   `ls -la /home/jake/share/Flambeee/` measured at run time (expected
   `No such file or directory`, exit 2). Mirror status deferred to the
   serving host, not assumed green.
7. T7 Checker frozen (AC-6). `git diff --stat` on the checker path is
   empty.
8. T8 Copy rule (AC-7). Story file uses plain punctuation, no em dashes,
   no heavy emoji.

## Real output

Pasted by QA at run time into `flambeee-team/qa-results.md`: checker
command plus exit code plus output, `ls` measurement, CACHE_VERSION line,
GAME_ORDER line, Play-link list, heading-vs-tag comparison, checker
diff-stat.

## Verdict

Run-1 FAIL on the live-path absence matches Sessions 31-39 precedent:
environmental, not a repo defect. No PR for this story by design.
