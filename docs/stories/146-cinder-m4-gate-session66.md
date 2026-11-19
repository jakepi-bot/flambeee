# Story 146: M-4 Cinder gate record (Session 66, P0b, zero code)

**Status:** Ready for execution (Session 66, 2026-11-19).
**Author:** Quinn, Business Analyst.
**Priority:** P0b. Backlog item M-4 (issue #216). Zero code.
**Assigned to:** **Scout**, QA owner of the evidence. No code owner; Riven's Story 145 PR carries the diff, Scout owns the gate record.
**Base commit:** `f26554e` (main, v0.52.0 released).
**Design contract:** `flambeee-team/design-handoff.md`, Story 146 sections 1 through 8. Design-owned observable criteria live in section 6 of that contract; the functional criteria below test the same gate from the requirements side.
**Jakebot ruling (binding):** session `local-1293548acc91245a8d713b75f92c88fb0183b0b03cf97518f9bb443473f4045f`. Hard-out: no merge without the full family run recorded in the PR.

## Summary

The M-4 rule (#216) requires that any Cinder-touching PR records the full Cinder proof family on base and on head before merge. The base run is already green and logged; Scout owns citing both runs in the Story 145 PR body and refusing the merge on any new head failure against base. This story ships no code and no docs bytes of its own; its output is the evidence record inside the Story 145 PR.

## Baseline measured at Session 66 planning (Wave 1, 2026-11-19)

| Check | Value |
|---|---|
| Base commit | `f26554e` (main, v0.52.0 released) |
| Base family | 19/19 PASS, tally pass=19 fail=0 skip=0 total=19 (assert 19==19), baseline MATCH, exit 0 |
| Base log | `flambeee-team/runs/2026-11-19/cinder-family-base.log` |
| Runner | `scripts/run-cinder-family.py`, stdlib only, serial, one failure never hides the rest |
| Family size rule | 19 members by discovery (files under `archive/src-games/` or `docs/test-plans/` or `scout-qa-session*.py` at root whose bytes match "cinder", case-insensitive) |

## Requirements

### 1. Two runs cited

The Story 145 PR body must paste both runs: the base family run (already captured green on `f26554e`) and the head family run on the PR branch (must also be 19/19, baseline MATCH, exit 0). One run alone never satisfies the gate.

### 2. Exact family-run commands and thresholds

Base (already run in Wave 1):

```
env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python scripts/run-cinder-family.py --port-base 8950
```

Thresholds per run: `family: 19/19 scripts passed`, tally `pass=19 fail=0 skip=0 total=19` with the `19==19` assert, `baseline: MATCH`, exit 0. Same venv interpreter and same port discipline on both runs. Exit 1 means at least one failure, exit 2 means runner-level error (zero discovered or target missing), exit 3 means misuse. Only exit 0 counts.

### 3. Unfiltered runs only

The gate run carries no `--include` and no `--exclude` flag. A filtered rerun is labeled FILTERED and never satisfies #216, even at 19/19.

### 4. Decide rule

Head 19/19 PASS with baseline MATCH and exit 0 authorizes merge. Any new head failure against base refuses the merge; fix forward in the counter diff only (never by editing a family script, the runner discovery rule, or the baseline file), then re-run the full unfiltered family. Base is green, so the pre-existing-failure branch is not live this session.

## Acceptance criteria (BDD, functional)

1. Given the Story 145 PR body, when it is read, then it cites the M-4 rule and issue #216.
2. Given the PR body evidence section, when it is read, then it pastes the base run (19/19 PASS, baseline MATCH, exit 0, HEAD `f26554e`) with interpreter and flags named.
3. Given the PR body evidence section, when it is read, then it pastes the head run on the PR branch (19/19 PASS, baseline MATCH, exit 0, unfiltered) with interpreter and flags named.
4. Given the head run command, when it is inspected, then it carries no `--include` and no `--exclude` flag.
5. Given any new head failure against base, when the gate is evaluated, then the PR does not merge.

## Out of scope

Any product-code or docs change (those belong to Stories 145 and 147), any edit to family scripts or the runner to reach green, any filtered rerun presented as the gate, any merge on a single run. Scout writes no website bytes under this story.

## Definition of done

Both runs pasted in the PR body with matching interpreter and port discipline, head run 19/19 PASS with baseline MATCH and exit 0, no filter flags, no new failures against base. #216 stays open until the merge it gates lands.
