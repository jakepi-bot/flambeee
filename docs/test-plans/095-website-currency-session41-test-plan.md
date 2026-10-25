# Test Plan: Story 095 Website Currency Session 41 (Run-1 Evidence Review)

Source: `docs/stories/095-website-currency-session41.md` (Quinn, Wave 2).
P3 standing verification, checker frozen. Run 1 executed by Riven
(no branch, no PR); QA independently reviews the evidence and re-runs
read-only measurements. Run 2 is conditional on the release wave
(post-tag v0.35.0 with CACHE 11 if the tag lands, else N/A by design).

QA: Scout. Written 2026-10-25 (Session 41 Wave 3). Base `e67895f`.

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee` on `origin/main`
  (`e67895f`).
- `git diff --stat -- scripts/verify-website-currency.sh` must be empty
  (checker frozen, AC-6). Verified by QA from disk.
- Live path `/home/jake/share/Flambeee/` must be measured, never assumed.

## Cases

1. T1 Run 1 pre-merge (AC-1, Scenarios 1, 6).
   `bash scripts/verify-website-currency.sh; echo CHECKER_EXIT:$?`.
   Expect exit 1 with `FAIL: live file not found:
   /home/jake/share/Flambeee/index.html`. The live-path absence is the
   known environmental finding (13th session running), not a repo defect.
   QA re-runs and pastes real output.
2. T2 Run 2 fork (AC-2, Scenario 2). If no v0.35.0 tag exists at QA
   time, record "Run 2: N/A, no release" with no tag resolution and no
   sync. If the tag landed, verify heading v0.35.0 + CACHE 11 + MATCH.
   PASS on the correct fork branch.
3. T3 Play links measured (AC-3, Scenario 3). Count plus targets of
   relative `games/*.html` links at run time (6 expected:
   `games/wordfire, games/minesweeper, games/simon, games/2048,
   games/cinder, games/afterglow` per planning; record actual read),
   every target existing under `website/games/`.
4. T4 GAME_ORDER plus Apps entry (AC-4, Scenario 4). `GAME_ORDER` line
   read at run time (6/6 including afterglow expected) and
   `website/apps/index.html` present with N/280 count,
   `flambeee-apps-` prefix, maxlength 280, Saved-clear-on-input noted.
   Timer page + card noted as additive facts only if merged, not as
   currency requirements.
5. T5 CACHE_VERSION baseline (AC-5, Scenario 5). `website/sw.js` line 21
   reads `var CACHE_VERSION = 10;` on main. (11 belongs to the PR head
   / tag branch only.)
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
GAME_ORDER line, Play-link list with existence check, heading-vs-tag
comparison (heading line + `git tag` / `ls-remote` read), open
issues/PRs count, checker diff-stat, run-2 fork outcome.

## Verdict

Run-1 exit 1 solely from the live-path absence matches the Sessions
31-40 precedent: expected environmental, not a repo defect, and the
checker stays frozen. Any additional failure line is a genuine defect.
