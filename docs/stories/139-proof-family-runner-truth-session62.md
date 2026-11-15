# Story 139: Proof-family runner truth (Session 62, P0)

**Status:** Build-ready (Session 62, 2026-11-15).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P0 (only story this session, builds in the 01:55 dev wave).
**Assigned to:** **Kai** (backend/tooling, single owner, one PR). Riven peers the PR.
**Base commit:** `406aacc` (main, Session 61 merge of #247).
**Design contract:** `flambeee-team/design-handoff.md`, Section I (Rook; the contract wins on interpreter, exits, tally, baseline, and thresholds).
**Session plan:** `flambeee-team/session-plan.md`, Session 62 (2026-11-15), P0 item.
**Tracked by:** #248 (stub class, closes in the build PR body). Red rows owned by #249 and #250, filed 01:32 CST.

## Context (why this story exists)

The Cinder proof-family runner returns two verdicts for the same repo depending on the invoking interpreter. Measured 2026-11-15 on the same tree, no code change between runs: `python3 scripts/run-cinder-family.py` (system `/usr/bin/python3.13`) gives 11/19 PASS exit 1, while the project venv python gives 12/19 PASS exit 1. The delta is exactly two `playwright` importers (`docs/test-plans/session22-story040-qa.py`, `docs/test-plans/session27-story053-qa.py`); `playwright` is installed only under `/home/jake/.hermes/flambeee/.venv`. The runner uses a silent `sys.executable` for every child, so nobody invoking it knows which interpreter certified the result. This is the whole legend: every session since v0.47.0 carried "8 pre-existing content-drift failures" when the venv truth is 7 real failures, and one of the 8 was never content drift at all. It survived because it lived in session prose with no owner. This story replaces the legend with an instrument that names its interpreter, refuses loudly on a broken environment, and checks every run against a committed 19-row baseline where each red row carries its owning issue.

Tooling only. Zero website bytes. No `CACHE_VERSION` bump. No version cut by default.

## Files (one PR, Kai)

| File | Change | Owner |
|---|---|---|
| `scripts/run-cinder-family.py` | Explicit `--python` contract, pre-flight refusal, three-way tally with invariant, reconciled exits | Kai |
| `docs/test-plans/v0.6.0-smoke-test.js` | Stub class fix: all nine missing ids, both stub lists | Kai |
| `docs/test-plans/cinder-family-baseline.json` | New: 19 rows, expected status under the venv, category, owning issue | Kai |

Nothing else. No website byte, no `CACHE_VERSION` bump, no second story in the PR.

## Functional requirements

### Runner contract

- FR-1 (`--python` contract and default resolution). The child interpreter becomes an explicit `--python PATH` parameter. Resolution order: explicit flag, else `<repo>/.venv/bin/python`, else `<repo>/../.venv/bin/python`. Measured default on this host: `/home/jake/.hermes/flambeee/.venv/bin/python`. A nonexistent `--python` path is misuse (exit 3, `bad --python: <path>`), decided at parse time before anything executes. Never fall back to `sys.executable` silently.
- FR-2 (pre-flight refusal semantics). Before any member executes, the runner checks every name in `DECLARED_DEPS` (`playwright`) importable under the INVOKING interpreter (`sys.executable`) and under the effective child. If the invoking interpreter lacks a declared dep, the run is invalidated entirely: every discovered row prints `ENV-SKIP <rel>  reason=env-skip: <dep> missing under invoker <path>`, the tally shows `FAIL=0`, and the runner exits 2. This is refusal, not partial execution. `--python` cannot rescue a bad invoking interpreter. If only the child lacks the dep, same shape with `reason=env-skip: <dep> missing under child <path>`, exit 2. Wording default per I11 O1; take it and do not stop.
- FR-3 (three-way tally and invariant). Every row ends in exactly one of PASS (child exit 0), FAIL (child nonzero including child exit 3, `timeout`, spawn failure, `port`, `baseline-drift`), or ENV-SKIP (S6 refusal only; S8 never invents skips). The runner asserts in-process: `total == pass + fail + skip == FAMILY_SIZE == 19`. Trip means exit 2 with token `INVARIANT-BROKEN`, never 0, never silent.
- FR-4 (reconciled exit matrix). First match wins: `misuse ? 3 : fail_closed ? 2 : (F >= 1 ? 1 : (S >= 1 ? 2 : 0))`. 0 = CLEAN: full unfiltered run, 19/19 PASS, baseline MATCH; citable as release evidence. 1 = REAL FAIL: at least one FAIL row from any cause; FAIL dominates SKIP, so 1 FAIL plus 18 ENV-SKIPs is red, never indeterminate. 2 = NO VERDICT: environment or runner-level blockage, nothing proven (pre-flight refusal with F = 0 by construction, zero discovered, target missing, S5 baseline failure, mkdtemp failure, invariant trip, or post-execution skips with F = 0). 3 = MISUSE: unknown flag, missing value, `--port-base`/`--timeout` out of range, nonexistent `--python` path, `--repo` not a repo. Child exit 3 is row data (`reason=exit=3`), never a runner code. Timeouts stay FAIL. The old code-2 members keep code 2 under the widened NO-VERDICT meaning; nothing is renumbered.

### Baseline artifact

- FR-5 (baseline schema). `docs/test-plans/cinder-family-baseline.json`: top-level `{"family_size": 19, "generated": "<YYYY-MM-DD>", "rows": [...]}` with exactly 19 rows. Row fields: `script` (repo-relative path, unique), `expected` (`pass` or `fail`), `category` (one of `stub`, `stale-pin`, `deep-logic`, `env`), `issue` (integer, or null only when `expected` is `pass`), `note` (one line, measured symptom for red rows, risk class for green rows). `expected=fail` with null `issue` is `BASELINE-MALFORMED` and fails validation. Category assignment per I5: red cause wins, else first marker hit in order env, stale-pin, stub, deep-logic; `session22-story040-qa.py` imports playwright but is red on stale pins, so it is `stale-pin`.
- FR-6 (the 19 committed rows, EXPECTED under the venv). Red symptoms are the parent's measured figures of 2026-11-15.

| # | script | expected | category | issue |
|---|---|---|---|---|
| 1 | `archive/src-games/kai-story033-pure-read-proof.py` | fail | deep-logic | 249 |
| 2 | `archive/src-games/kai-story035-pure-read-proof.py` | pass | deep-logic | null |
| 3 | `archive/src-games/kai-story037-badge-proof.py` | pass | stub | null |
| 4 | `archive/src-games/kai-story040-pure-read-proof.py` | fail | deep-logic | 249 |
| 5 | `archive/src-games/kai-story042-streak-proof.py` | pass | stub | null |
| 6 | `archive/src-games/kai-story044-questlog-streak-proof.py` | fail | deep-logic | 249 |
| 7 | `archive/src-games/kai-story045-reload-guard-proof.py` | pass | stale-pin | null |
| 8 | `archive/src-games/kai-story047-questlog-readpath-proof.py` | fail | deep-logic | 249 |
| 9 | `archive/src-games/kai-story051-away-window-proof.py` | pass | stale-pin | null |
| 10 | `archive/src-games/kai-story053-record-normalize-proof.py` | pass | stale-pin | null |
| 11 | `archive/src-games/kai-story066-notice-proof.py` | pass | stale-pin | null |
| 12 | `docs/test-plans/session22-story040-qa.py` | fail | stale-pin | 250 |
| 13 | `docs/test-plans/session26-story050-qa.py` | pass | stale-pin | null |
| 14 | `docs/test-plans/session26-story051-qa.py` | pass | stale-pin | null |
| 15 | `docs/test-plans/session27-story053-qa.py` | pass | env | null |
| 16 | `docs/test-plans/session27-story054-qa.py` | fail | stale-pin | 250 |
| 17 | `docs/test-plans/session27-story055-qa.py` | fail | stale-pin | 250 |
| 18 | `scout-qa-session19-032.py` | pass | deep-logic | null |
| 19 | `scout-qa-session24.py` | pass | stub | null |

Row notes (one line each): row 1, exit 1, Preview path violates pure-read (write refs found). Row 4, exit 1, 3 of 40, S7 survived branch. Row 6, exit 1, node proof BLOCK. Row 8, exit 1, 2 of 25, S13 order. Row 12, exit 1, 3 of 164 under venv (playwright leg runs). Row 16, exit 1, 5 of 9, pins v0.24.0 heading/blob/mirror against live v0.50.0. Row 17, exit 1, 2 of 28, demands Story 053 in-flight while the record says shipped in v0.25.0. Row 15, passes under venv, imports playwright (venv-only), so interpreter environment is its risk class. Rows 3/5/19, pass under venv, verdict leans on an in-harness double (`getQuestState` stub, in-memory localStorage, thin shims). Rows 7/9/10/11/13/14, pass under venv, carry history pins but green today. Rows 2/18, pass under venv, prove live product semantics.
- FR-7 (baseline enforcement and falsification). On unfiltered enforced runs each row compares ACTUAL with EXPECTED. Match: silent. Mismatch: row becomes FAIL with `reason=baseline-drift(expected=<X> got=<Y>)`, exit follows FR-4 (a drifted baseline is red, exit 1). Enforcement is proven by AC-4's scratch-copy flip, not by the file existing. A baseline edit that flips EXPECTED to match a new red without a PR-body reason per AC-2 is whitewash the runner cannot detect; the control is process (every EXPECTED change needs a named row plus reason in the PR body), not code.
- FR-8 (discovery-vs-baseline separation, fail-closed). The baseline declares; it never discovers. Discovery stays the file rule (`scripts/run-cinder-family.py:113-134`, no hardcoded member list). A discovered script with no baseline row stops the run before any execution: exit 2, token `BASELINE-MISSING-ROW <rel>`, naming every offender. A baseline row whose script no longer exists is the same severity in the other direction: exit 2, token `BASELINE-ORPHAN-ROW <rel>`. Never an implicit pass, never silently dropped. `--no-baseline-check` bypasses S5 and the compare, prints `baseline: OFF (triage only, not evidence)`, and its output may not be cited as family evidence. Filtered runs (`--include`/`--exclude`) print `FILTERED-NO-BASELINE-CERTIFY` and may never be cited as full-family green.

### Smoke test and manifest anchor

- FR-9 (smoke-test stub class fix). `website/games/wordfire.html` and `archive/src-games/wordfire.html` call `getElementById` for 22 distinct ids; the stub in `docs/test-plans/v0.6.0-smoke-test.js` provides 13. All nine missing ids go into the stub id list in BOTH occurrences (the `els` list and the `els2` list): `stdBtn`, `hardBtn`, `distBars`, `distPanel`, `distSub`, `distTitle`, `overlayShareBtn`, `shareCopy`, `shareMsg`. `stdBtn` is only the first dereferenced at load (`wordfire.html:1082`); fixing it alone moves the crash to the next wiring line, so a single-site fix fails this requirement by construction. `v0.4.0-logic-check.js` and `v0.6.0-logic-check.js` are untouched (both exit 0 at 22/22 today).
- FR-10 (docstring anchor rule and regen fallback). Preferred: Kai edits the runner WITHOUT touching lines 1-28 (docstring, USAGE, filtered prose) and without moving the `def discover()` line; new contract text goes into code and into docstring lines appended BELOW line 28 only. Verification, all four required (Session 62 parent amendment I13): `sed -n '5p' scripts/run-cinder-family.py` prints byte-exactly `a file is in the family iff it ends in .py, it lives under archive/src-games/ or` (the "docs/test-plans/ or matches scout-qa-session*.py at the repo root, and its" sentence is line 6, not line 5); `env -u PYTHONPATH python3 dev/src-consumer-manifest.py` exits 0; `git diff --stat -- dev/` shows exactly 2 files and 2 changed lines, both the `base_commit` line; then `git checkout -- dev/src-consumer-manifest.json dev/src-consumer-manifest.md` and `git status --porcelain -- dev/` prints nothing. The generator rewrites `base_commit` from `050fcad...` to HEAD (`406aacc...`) by design, so the restore step is required, not optional: running the generator is an observation, not a commit. Any changed line other than `base_commit` is real drift: stop and escalate. Fallback, only if the contract cannot fit below line 28: regenerate both manifest artifacts in the same PR, with the diff limited to exactly three row classes (the line-5 row text change, the `discover()` synthetic row line-number move, `base_commit` advance), generator exit 0, second run byte-identical, every changed row explained in the PR body. Any other manifest row change fails the PR. `docs/roadmap.md` Story 127/131 prose stays frozen history either way.
- FR-11 (close #248). The build PR body closes #248 with measured before/after: the stub provided 13 of 22 ids (exit 1, `TypeError: Cannot read properties of null` at `stdBtn`), now provides all 22, `node docs/test-plans/v0.6.0-smoke-test.js` exit code pasted.

## BDD acceptance criteria

Threshold: 12 of 12 on the PR head. Each item states the plain-language scenario (Given/When/Then), then the exact command, its expected exit code, and its expected literal output token. Every Then is observable in a terminal, never a code-review judgement. T1-T6 carry the dev wave's acceptance tests verbatim in intent; each maps to its design scenario DA-T1 through DA-12.

- AC-1 (DA-T1, refusal, T1). Given system python3 (which lacks playwright) as the invoking interpreter, when the runner is invoked with no flags, then it refuses before executing anything: exit 2, output names `playwright`, every one of the 19 rows shows `ENV-SKIP`, and the tally shows `fail=0`.
  - Command: `env -u PYTHONPATH python3 scripts/run-cinder-family.py; echo "exit=$?"` exits 2, tokens `playwright`, `ENV-SKIP`, `fail=0`, 19 ENV-SKIP rows.
- AC-2 (DA-T2, honest run, T2). Given the venv python on the PR head, when the runner is invoked unfiltered, then it executes all 19 members: exit 1, all 19 names printed as PASS/FAIL/ENV-SKIP lines, the tally reconciles to 19 (`total` 19), `pass=` >= 12 (nothing regressed), and the `failed:` list names every red row. Every row whose status differs from the measured 12/7 split is explained by name in the PR body; hitting the floor by editing EXPECTED without a reason is whitewash and fails review.
  - Command: `env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python scripts/run-cinder-family.py; echo "exit=$?"` exits 1, tokens `total` reconciling to 19, `pass=` >= 12, `failed:` list, all 19 names present.
- AC-3 (DA-T3, determinism, T3). Given the venv python on the PR head, when two consecutive unfiltered runs have their verdict-plus-tally lines compared, then the spans are byte-identical.
  - Command: run AC-2 twice through `grep -E '^(PASS|FAIL|ENV-SKIP|family:|tally:|baseline:|failed:|  - )'` into two files; `sha256sum` of both spans equal.
- AC-4 (DA-T4, enforcement fires, T4). Given a scratch copy of the baseline (scratch dir only, never the repo) with one row's `expected` flipped, when the venv runner is pointed at it with `--baseline`, then it exits nonzero with `baseline-drift` naming the row. A passing run on the committed file alone proves nothing; the flip is the proof.
  - Command: `cp docs/test-plans/cinder-family-baseline.json <scratch>/bl-flip.json`, flip one row, `env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python scripts/run-cinder-family.py --baseline <scratch>/bl-flip.json; echo "exit=$?"` exits nonzero (1), token `baseline-drift` with the row named.
- AC-5 (DA-T5, smoke test direct, T5). Given the fixed smoke test on the PR head, when it runs directly, then its real exit code is pasted in the PR body (expected 0; a nonzero names the next missing id and fails the PR).
  - Command: `node docs/test-plans/v0.6.0-smoke-test.js; echo "exit=$?"`, exit code pasted verbatim.
- AC-6 (DA-T6, scope, T6). Given the PR branch against main, when the diff stat is read, then it shows exactly two code files plus the baseline and nothing else.
  - Command: `git diff --stat main...HEAD` (or `git diff --stat`), exactly `scripts/run-cinder-family.py`, `docs/test-plans/v0.6.0-smoke-test.js`, `docs/test-plans/cinder-family-baseline.json`. Any fourth file fails scope.
- AC-7 (DA-7, filtered honesty). Given the venv python with `--include kai-story033`, when the runner runs, then it prints `FILTERED` and `FILTERED-NO-BASELINE-CERTIFY`, and the output is rejected as T2 evidence on sight.
  - Command: venv python with `--include kai-story033` prints `FILTERED` and `FILTERED-NO-BASELINE-CERTIFY`.
- AC-8 (DA-8, bad knob). Given bad invocations, when each runs, then each exits 3 with usage and nothing executes: `--timeout 5`, nonexistent `--python /nope/python`, `--repo /tmp` (not a repo).
  - Commands: each exits 3, token `usage` or the named cause.
- AC-9 (DA-9, stale baseline, fail-closed). Given a scratch baseline copy minus one row, when the venv runner is pointed at it, then it exits 2 with `BASELINE-MISSING-ROW` naming the row and executes nothing.
  - Command: `--baseline` at the row-deleted scratch copy exits 2, token `BASELINE-MISSING-ROW` with the row named.
- AC-10 (DA-10, manifest untouched or explained). Given the PR head, when the four I8/I13 checks run in order, then the anchor holds, the generator exits 0, the only `dev/` diff is the `base_commit` line, and a restore leaves `dev/` clean. Or the three regen-fallback proofs hold (generator exit 0, second run byte-identical, every changed row explained).
  - Commands, in this order: `sed -n '5p' scripts/run-cinder-family.py` prints byte-exactly `a file is in the family iff it ends in .py, it lives under archive/src-games/ or`; `env -u PYTHONPATH python3 dev/src-consumer-manifest.py && echo GENERATOR-OK` exits 0; `git diff --stat -- dev/` shows exactly 2 files and 2 changed lines, both `base_commit`; `git checkout -- dev/src-consumer-manifest.json dev/src-consumer-manifest.md && test -z "$(git status --porcelain -- dev/)" && echo DEV-CLEAN` prints `DEV-CLEAN`. Any other changed line in step 3 is real drift: stop and escalate. (Or the regen-fallback equivalents.)
- AC-11 (DA-11, stub class, not single site). Given the fixed smoke test, when it runs and its stub lists are grepped, then it exits 0 AND `grep -c` of each of the nine ids (`stdBtn`, `hardBtn`, `distBars`, `distPanel`, `distSub`, `distTitle`, `overlayShareBtn`, `shareCopy`, `shareMsg`) in the stub is >= 1.
  - Command: `node docs/test-plans/v0.6.0-smoke-test.js` exits 0; each of the nine ids greps >= 1 in the stub lists.
- AC-12 (DA-12, zero website bytes). Given the PR working tree, when the website tree is checked, then it is clean.
  - Command: `test -z "$(git status --porcelain -- website/)" && echo WEBSITE-CLEAN` exits 0, first line `WEBSITE-CLEAN`.

Timebox (binding, from the ruling): if AC-4 is unreachable by 02:40, Kai ships FR-1 through FR-6 plus FR-9 with the baseline as documentation only (enforcement visibly off), says so plainly in the PR body, and enforcement moves to the next LEGACY window. A partial deliverable named as partial is fine; a green status that is not green is not.

## Definition of done

- AC-1 through AC-12 recorded pass in the build PR body with live pasted output, 12 of 12. T1-T6 outputs pasted verbatim: T1 exit 2 with `playwright` named and `fail=0`; T2 exit 1 with all 19 names, reconciled total 19, `pass=` >= 12, every delta from the 12/7 split explained by row name; T3 two sha256 spans equal; T4 nonzero exit with `baseline-drift` naming the flipped row; T5 real exit code pasted; T6 stat showing exactly the three files.
- The diff holds exactly three files: `scripts/run-cinder-family.py`, `docs/test-plans/v0.6.0-smoke-test.js`, `docs/test-plans/cinder-family-baseline.json`. No `website/` byte (AC-12 gates), no `CACHE_VERSION` touch, no version cut.
- Stop conditions (Kai stops and returns to this story): any S9 invariant trip (`total != 19` on an unfiltered run); any `website/` diff byte; any fourth file in the stat; any lowering of the >= 12 pass floor; any baseline row flipped without a stated row name plus reason in the PR body; any `expected=fail` row with null `issue`.
- Riven peers the PR. Rook design review runs against Section I after the PR opens; blocking findings gate the release wave. #248 closes in the build PR body with the measured before/after from FR-11.

## Out of scope

- The four deep-logic proofs (033, 040, 044, 047) stay red, owned by #249. No repair, no assertion relaxation. Each needs a ruling on whether the proof or the product is wrong; that is design-gate work, not an hour's work.
- The three stale-pin scripts (session22-040, session27-054, session27-055) stay red, owned by #250. No repair, no pin update. Next LEGACY window takes them against the repaired instrument.
- No version cut. Tooling-only session, so no user-visible change; the release wave decides and records the T1-T6 evidence either way (Session 59/61 precedent).
- #215 M-3 Cinder counter, #216 M-4 standing rule, #237/#238 manifest follow-ups, PRs #206, #208, #211, #212, #217. Untouched.
- `docs/roadmap.md` Story 127/131 prose, `FAMILY_REASON`, `BEFORE_SNIPPET`, `AFTER_SNIPPET`: frozen history, never edited.

## Open questions

None. The contract binds every open point.
