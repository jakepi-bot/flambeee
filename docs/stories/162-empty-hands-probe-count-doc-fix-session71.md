# Story 162: EMPTY HANDS probe-count doc correction (Session 71, P2)

**Status:** Ready for development (Session 71, 2026-11-24).
**Author:** Quinn, Business Analyst.
**Priority:** P2 (one-line-class doc fix; docs rider in the 159/160 PR; sequence first).
**Assigned to:** **Riven**, sole owner. File: `docs/stories/153-empty-hands-play-counter-session69.md` only. Zero code change.
**Base commit:** `582171b` (main, v0.57.0).
**Scope:** Issue #281: correct the two probe-count sentences (base 18 to 19, result `18 members become 19` to `19 members become 20`). No code change.
**Design contract:** `flambeee-team/design-handoff.md`, Section 4 (Story 162, subsections 4.1 through 4.6). Design-owned observable criteria live in contract subsection 4.5 and are mapped here one for one.
**Non-blocking rule:** rides in the 159/160 PR as a docs rider; sequence first per the session plan. If Quinn's story wording collides with this correction, Quinn owns the wording and Riven applies it with this section's numbers (19/20) winning on the counts.

## Summary

Issue #281 is one line done twice: the Story 153 file says the EMPTY HANDS probe `window.__empty` at `empty-hands.html:488` has 18 members on base and that adding the `plays` getter makes `18 members become 19`. The measured base is 19 members, and adding the single `plays` getter makes 20. Riven corrects exactly two sentences: line 30 becomes ``Probe on base | `window.__empty` (line 488), 19 members, no plays getter |`` and line 96 becomes ``Add `plays: function () { return playsMem; }` to `window.__empty` (read-only; 19 members become 20). No other probe change. `reset()` keeps its current behavior and never counts.`` Both `18` numerals become `19`, and `become 19` becomes `become 20`. No other line in the file changes, no game file is touched, no cache version moves.

## Baseline measured at Session 71 planning (Wave 1, 2026-11-24)

| Check | Value |
|---|---|
| Base commit | `582171b` (main, v0.57.0) |
| Target file | `docs/stories/153-empty-hands-play-counter-session69.md` |
| Line 30 today | ``Probe on base | `window.__empty` (line 488), 18 members, no plays getter |`` |
| Line 96 today | ``Add `plays: function () { return playsMem; }` to `window.__empty` (read-only; 18 members become 19). No other probe change. `reset()` keeps its current behavior and never counts.`` |
| Measured base probe membership | 19 (`members_base [count, integer] = 19`) |
| Result probe membership | 20 (`members_result [count, integer] = 20`) |
| Delta | `members_result - members_base = 1 [member: the plays getter]` |

## Functional requirements

FR-1 (contract 4.2, sentence 1). Line 30 reads byte for byte: ``Probe on base | `window.__empty` (line 488), 19 members, no plays getter |``. The `window.__empty` line-488 reference stays intact.

FR-2 (contract 4.2, sentence 2). Line 96 reads byte for byte: ``Add `plays: function () { return playsMem; }` to `window.__empty` (read-only; 19 members become 20). No other probe change. `reset()` keeps its current behavior and never counts.`` The `plays` getter snippet and the `reset()` sentence stay intact.

FR-3 (contract 4.4, change discipline). Only the two specified sentences change. Any third `18` found elsewhere in the file is left alone and flagged in the PR. Temptation to touch the probe code is forbidden: the diff for this story must show the story file and nothing else. If the file moved or the lines shifted, apply the same two sentence corrections at their new line numbers and record the numbers in the PR. If Quinn's story wording collides with this correction, Quinn owns the wording and Riven applies it with the 19/20 numbers winning.

## Acceptance criteria (BDD, observable in the doc)

Design-owned observable criteria are in contract subsection 4.5; AC-1 through AC-3 map them directly.

1. Given the merged file, when the reviewer reads the probe table row, then it says `19 members, no plays getter` with the `window.__empty` line-488 reference intact. (design 4.5.1; FR-1)
2. Given the merged file, when the reviewer reads section 4, then it says `19 members become 20` with the `plays` getter snippet and the `reset()` sentence intact. (design 4.5.2; FR-2)
3. Given `git diff main --stat` for this story, when the reviewer inspects it, then exactly one file changed (`docs/stories/153-empty-hands-play-counter-session69.md`), two lines changed, zero code files, zero cache bump. (design 4.5.3; FR-3)

## Out of scope

No new mechanic, no new storage key, no other game file, no `GAME_ORDER` change, no `website/index.html` change (there is no new game card today), no backlog issues beyond #281/#285/#287, no FPS/app work. No code change of any kind: no game file, no harness file, no `sw.js` cache bump, no probe-code touch. No other sentence in the Story 153 file changes.

## Non-blocking rule

Rides in the 159/160 PR as a docs rider; sequence first per the session plan (do it first, get it out of the way). Never blocks or holds the code stories.

## Defects/risks

- Wording collision with Quinn's story text: Quinn owns story text; Riven applies Quinn's wording with the 19/20 numbers winning on the counts.
- Extra `18` occurrences elsewhere in the file: only the two specified sentences change; any third `18` is left alone and flagged in the PR.
- Verification plan (1 pass after the edit): 2 grep reads (line 30 region shows `19 members, no plays getter`; line 96 region shows `19 members become 20`), 1 diffstat (`--stat` shows 1 file, 2-line shape), 1 collision check (no other `18 members` string remains in the file). Pass threshold: 4/4 checks exact; any code-file byte in the diff is FAIL.
