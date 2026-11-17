# Story 141: Cinder proof family close-out (Session 64, P0 floor plus P1 ceiling, tooling only)

**Status:** Build-ready (Session 64, 2026-11-17).
**Author:** Quinn (Business Analyst), Wave 1.
**Priority:** P0 for Group A, P1 for Group B (tooling only, no user-visible change).
**Assigned to:** **Kai** (SOLE code owner; one PR covering scripts and baseline only, zero `website/` bytes). Riven peers the PR. Scout runs QA.
**Base commit:** `5ce51a0` (main, Session 63 release v0.51.0; branch `docs/session64-141-cinder-proof-family` carries one planning commit on top).
**Design contract:** `flambeee-team/design-handoff.md`, Sections B through I (Rook; the contract wins on frozen refs, K1-K4 rulings, mutation protocol, reconciliation, frozen-history independence, and the product-bytes guard).
**Session plan:** `flambeee-team/session-plan.md`, Session 64 (2026-11-17), P0 item plus P1 ceiling plus P2 docs.
**Dependencies:** None. The dev wave branches from main after this half's docs PR merges.

## Context (why this story exists)

LEGACY day. The Cinder family has seven red rows in `docs/test-plans/cinder-family-baseline.json` (19 rows: 12 pass, 7 red, every red row attributed), and the repair closes them so every row either passes or carries a cited ruling. Group A repins the three stale-pin scripts (#250) to frozen history. Group B applies the four repairs implied by Rook rulings K1-K4 (#249, all four read "proof is stale"). One PR, zero paths under `website/`, no version cut (no-release on the Session 59/61/62 precedent).

## Files (one PR, Kai)

| File | Change | Owner |
|---|---|---|
| `docs/test-plans/session27-story054-qa.py` | Repin per B1: REF frozen to `v0.24.0` for the `src/cinder.html` and What's New reads, blob read frozen to `2907623:scripts/verify-website-currency.sh`, mirror and working-tree assertions retired by name | Kai |
| `docs/test-plans/session27-story055-qa.py` | Repin per B2: RECORD resolved through `git show v0.25.0:<record-path>` (env override still honored for triage, committed default is the frozen ref); Parts 1/2 unchanged | Kai |
| `docs/test-plans/session22-story040-qa.py` | Pin made real per B3: serve materialized `git show 28e5c49:src/cinder.html` bytes, keep the `77acd25` S5c control real, disposition the 3 failing checks per rule B3.3 (repin where a frozen ref satisfies, retire by name where a shipped contract contradicts) | Kai |
| `archive/src-games/kai-story033-pure-read-proof.py` | Repair per K1: narrow scan to the `renderQuestNextDayBlock` body plus the `renderQuest` call site, strip comments before token search | Kai |
| `archive/src-games/kai-story040-pure-read-proof.py` | Repair per K2: replace the S7 survived fixture with `rec(TODAY-4, [TODAY-4])`, assert shouldShow true plus survived true plus the explicit survived line end to end | Kai |
| `archive/src-games/kai-story044-questlog-streak-proof.py` | Repair per K3: add `computeRecentQuestEntries` (verbatim extract) to the sandbox list and the static-scan PATH_FNS | Kai |
| `archive/src-games/kai-story047-questlog-readpath-proof.py` | Repair per K4: compute S13 expectations with the two-arg anchor-relative form, expected first row `today: Objective 6` | Kai |
| `docs/test-plans/cinder-family-baseline.json` | Data file, in scope: each done script flips its row to `expected: pass` with the note updated (observed exit code plus tally), or a row is deleted only with the retirement name plus coverage loss recorded in the issue | Kai |

No other file. No path under `website/`. No version cut.

## BDD acceptance criteria, Group A (#250 stale pins, floor, P0)

Threshold: 3 of 3 on the PR head. Each Then names the observable command and the expected exit code under `env -u PYTHONPATH .venv/bin/python`.

- AC-A1 (054 repin). Given the repinned `docs/test-plans/session27-story054-qa.py` (REF frozen to `v0.24.0`, blob read frozen to `2907623`, assertions `mirror-byte-identical`, `mirror-sha-pair-equal`, `working-tree-clean-informational`, and `live-origin-tag-lookup` retired by name with coverage loss recorded), when run as `env -u PYTHONPATH .venv/bin/python docs/test-plans/session27-story054-qa.py`, then it exits 0 (9/9 with the retired names listed in output), and the baseline row for `docs/test-plans/session27-story054-qa.py` flips to `expected: pass` with the note updated to the observed run.
- AC-A2 (055 repin). Given the repinned `docs/test-plans/session27-story055-qa.py` (RECORD resolved through `git show v0.25.0:docs/stories/055-cinder-record-family-decision-record.md`, Parts 1/2 unchanged on frozen `v0.24.0:src/cinder.html`), when run as `env -u PYTHONPATH .venv/bin/python docs/test-plans/session27-story055-qa.py`, then it exits 0 (28/28), and the baseline row for `docs/test-plans/session27-story055-qa.py` flips to `expected: pass` with the note updated to the observed run.
- AC-A3 (040-qa pin made real). Given the repaired `docs/test-plans/session22-story040-qa.py` (serves materialized `28e5c49:src/cinder.html` bytes, `77acd25` S5c control kept real, the 3 failing checks each dispositioned per B3.3 with names pasted in the PR body), when run as `env -u PYTHONPATH .venv/bin/python docs/test-plans/session22-story040-qa.py`, then it exits 0 (164/164, or the documented retire-by-name disposition where a shipped contract contradicts), and the baseline row for `docs/test-plans/session22-story040-qa.py` flips to `expected: pass` with the note updated to the observed run.

## BDD acceptance criteria, Group B (#249 rulings, ceiling, P1)

Threshold: 4 of 4 on the PR head. Each Then names the script and the expected exit 0, plus the baseline row flip.

- AC-B1 (K1 repair, proof is stale). Given the repaired `archive/src-games/kai-story033-pure-read-proof.py` (scan narrowed to the preview body plus call site, comments stripped, 6 forbidden tokens still forbidden inside), when run under `env -u PYTHONPATH .venv/bin/python`, then it exits 0 printing `PURE-READ PROOF PASS` with zero retired assertions, and its baseline row flips to `expected: pass` with the note updated.
- AC-B2 (K2 repair, proof is stale). Given the repaired `archive/src-games/kai-story040-pure-read-proof.py` (S7 fixture `rec(TODAY-4, [TODAY-4])`, asserts shouldShow true plus survived true plus the explicit `Your streak survived.` line), when run under `env -u PYTHONPATH .venv/bin/python`, then it exits 0 printing `ALL CHECKS PASS (40 checks)`, and its baseline row flips to `expected: pass` with the note updated.
- AC-B3 (K3 repair, proof is stale). Given the repaired `archive/src-games/kai-story044-questlog-streak-proof.py` (`computeRecentQuestEntries` extracted verbatim into the sandbox and PATH_FNS), when run under `env -u PYTHONPATH .venv/bin/python` (node v22.23.3 for the extracted leg), then it exits 0 printing `ALL CHECKS PASS`, and its baseline row flips to `expected: pass` with the note updated.
- AC-B4 (K4 repair, proof is stale). Given the repaired `archive/src-games/kai-story047-questlog-readpath-proof.py` (S13 expectations computed with two-arg anchor-relative labels, first row `today: Objective 6`), when run under `env -u PYTHONPATH .venv/bin/python` (node v22.23.3 for the extracted leg), then it exits 0 printing `ALL CHECKS PASS`, and its baseline row flips to `expected: pass` with the note updated.

## Falsifying tests (acceptance criteria, not prose)

- FT-1 (mutation, design-handoff Section D). For every repinned script (054, 055, 040-qa) plus every K1-K4 repair: one mutation against the pinned content in a throwaway worktree exits nonzero (RED), and the un-mutated frozen control exits 0 (GREEN). Three pairs minimum for the repins. A repin that stays green under mutation is a relaxed assertion and the PR is rejected. Exit codes pasted in the PR body with the interpreter named.
- FT-2 (row-for-row reconciliation, Section E). The unfiltered venv run matches `docs/test-plans/cinder-family-baseline.json` row for row, and discovery prints 19 (`discovery: 19 script(s)`). Any other count is INVARIANT-BROKEN (exit 2), not evidence. Unexplained flips are drift, not done.
- FT-3 (frozen-history independence, Section F). Each repinned script run inside a worktree checked out at its old tag is GREEN there and GREEN on main with identical tallies (new script file against old data files; only data crosses the boundary).
- FT-4 (product-bytes guard, Section G). `git diff --stat` on the PR contains zero paths under `website/`. Verified by pasting the full stat output, not asserted.

## Scope guard

Allowed paths: scripts under `docs/test-plans/` and `archive/src-games/`, plus `docs/test-plans/cinder-family-baseline.json` only. Zero paths under `website/`. No version cut, no release artifacts, no BLOG, no Bluesky staging.

## Definition of done

- AC-A1 through AC-A3 plus AC-B1 through AC-B4 recorded pass in the build PR body with live pasted output, 7 of 7 (or Group A 3 of 3 with any Group B miss carried as red-with-cited-#249-ruling per the hard-out rule).
- Unfiltered family run under the venv: 19 discovered, per-row outcomes matching the updated baseline JSON row for row (`baseline: MATCH`), every remaining `fail` row carrying a cited #249 ruling.
- The diff holds only the eight files listed above (subset allowed when a row retires instead of flipping). No ninth file, no `website/` path.
- Stop conditions (Kai stops and returns to this story): any repin that stays green under mutation (relaxed assertion, reject); any `main:`-relative product read still defaulting to live (change the default to the frozen ref); any assertion relaxed to match live instead of repinned to frozen history or retired by name; any `website/` byte in `git status --porcelain` before push; any B3.3 failure that traces to a genuine product break (ruling becomes "product is wrong" for that check: file it, row stays red-with-ruling, no website edit today).
- Riven peers the PR. Rook design review runs against Sections B through I after the PR opens; blocking findings gate the release wave. Release wave records no-release on the Session 59/61/62 precedent.
- Successor named in the dev PR body for Thursday 2026-11-19 (LEGACY window): #215 Cinder play counter, harness family green under #216, per `docs/play-counter-pattern.md`.

## Out of scope

- No product fix today even under a "product is wrong" ruling (filed with the ruling cited, row stays red-with-ruling; that is still a declared baseline).
- No #215 play counter, no #216 QA bar change, no #217 cadence policy, no #259, no #254/#255 runner UX, no #237/#238 manifest work.
- No FPS, no new game, no website byte, no release, no What's New edit, no precache change.
- No visual redesign. Palette owns visual direction; this story carries no visual content.

## Open questions

None. Sections B through I bind every open point except B3.3, where Kai names the 3 failures in the PR body before choosing repin versus retire per the stated decision rule.

## References

- `flambeee-team/session-plan.md`, Session 64 (2026-11-17): P0 floor, P1 ceiling, P2 docs, jakebot advisory (option B), cut line, hard-out rule, four falsifying tests.
- `flambeee-team/design-handoff.md`, Sections B through I (Rook): ref/pin table with verified frozen refs, K1-K4 rulings with evidence and required repairs, mutation protocol, reconciliation contract, frozen-history independence, product-bytes guard, edge cases and Plan B, design acceptance criteria with measurement rationale.
- `docs/test-plans/cinder-family-baseline.json`: baseline under repair, family_size 19.
