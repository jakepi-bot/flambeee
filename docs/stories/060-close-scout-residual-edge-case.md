# Story 060: Close Scout's unreported residual edge case (Session 29, P2, Verification)

**Status:** Ready for development (Session 29, 2026-10-06).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (a carried, unknown-content item; closes before new artifacts are published).
**Assigned to:** **Kai** owns the re-derivation and the proof script. Independently verified by a
second worker per the ownership protocol. **No speculative code.**
**Tracked by:** Session 29 plan, Story 060. Carried from the Session 28 session note.

## Summary

Session 28's Scout run ended on the sentence "found a residual edge case" and never reported it.
The note records the item verbatim:

> **Scout's unreported residual edge case.** Scout's run ended on "found a residual edge case" and
> never reported it. Cannot establish whether it is one of the three documented non-blocking notes
> or a fourth finding. A note nobody wrote down remains unmeasured. **Session 29 should close this
> before new artifacts are published.**

This story closes it by measurement against the **shipped v0.26.0** `src/cinder.html`. It is a
verification story: it either reproduces a fourth finding with evidence, or states with evidence
that the residual was one of the three documented non-blocking notes. **A no-defect answer is a
valid, complete result.**

## The three documented non-blocking notes (from v0.26.0, Story 056)

Quoted from `roadmap.md` v0.26.0 and Story 056, so the comparison is against the recorded notes and
not a re-derivation:

1. **`hp: 0` at the inn.** Under the clamp-to-0 ruling, `hp: 0` renders "You are dead. Reviving..."
   at the inn; it self-heals on the next visit. It is a consequence of a parent ruling made before
   dev started, not new behavior.
2. **Normalizer asymmetry.** `normalizeCharacterRecord({})` returns a level-1 hero, where
   `normalizeDayRecord({})` returns `null`. Recorded as an asymmetry; real saves always carry
   `name` and `level`.
3. **Proof location.** `flambeee-team/` is gitignored, so the proof lives in the PR body plus
   untracked files rather than in a committed script. A logistics note, not a product behavior.

## Requirements

### 1. Re-run the Session 28 seeds against shipped v0.26.0

Re-run, by executing the real functions from **v0.26.0** `src/cinder.html` (not v0.25.0, not a
re-implementation):

- The Session 28 character-record seeds from `flambeee-team/runs/session28-loadsave-repro.py`:
  the A, C, G2, G3, H1, H2 cases and the E (unreadable storage) case.
- The three documented non-blocking notes above, exercised directly.
- The storage and boundary cases: `null`, `42`, `"a string"`, `[]`, `{}`, an all-wrong-type object,
  a 50-character name, `xp: 12.7`, `gold: -5`, `wins: 3.2`, `level: null`, `level: 99`,
  `weapon: "2"`, `armor: "2"`, `hp: -50`, `hp: 1e9` / `maxHp: 26`, `maxHp: 0` with positive `hp`.

### 2. Reproduce a fourth finding, or rule it out with evidence

- **If a fourth finding reproduces and it is a real defect:** route it to a story number with a
  minimal reproduction (seed in, observed out, expected out). Do not fix it in this story.
- **If nothing reproduces beyond the three documented notes:** state that with evidence, and the
  item is closed. Show the sweep and the pass counts.

### 3. No speculative code

No code change ships under this story. If a fourth finding is real, the fix is a separate story.
The deliverable is a measurement and a written answer.

### 4. Record the answer where the item lives

- `flambeee-team/dev-results.md`: the re-derivation, the seeds run, the outcome, the evidence.
- This story file: the outcome, so the item stops being carried.

## Acceptance Criteria (Given/When/Then)

**AC-1.** Given shipped v0.26.0 `src/cinder.html`, when the Session 28 seeds and the storage and
boundary cases are executed, then each case prints a measured result, not a re-implementation.

**AC-2.** Given the three documented non-blocking notes, when each is exercised, then it either
reproduces as recorded or is shown not to.

**AC-3.** Given the full sweep, when it completes, then the outcome is exactly one of: "a fourth
finding reproduced, routed to story N with a reproduction" or "the residual was one of the three
documented notes, no fourth finding, item closed." No third, vague outcome.

**AC-4.** Given the change set, when `git diff --stat` is read, then the only changed files are
this story file and `dev-results.md`. No `src/` or `website/` change.

**AC-5.** Given the proof script, when run against v0.26.0, then its exit code and the pass/fail
counts are recorded. If it is a genuine sweep it should exit 0 on v0.26.0 (all previously fixed
defects stay fixed); if it reproduces a fourth defect it exits non-zero and names it.

## Required Proof

A re-runnable sweep (extend `flambeee-team/runs/session28-loadsave-repro.py` if it fits, otherwise
a new script under `flambeee-team/runs/`) that executes the real v0.26.0 functions and prints the
outcome for every seed. Quote the numbers: cases run, cases passed, cases reproduced. The answer
sentence in `dev-results.md` must be backed by that output.

**Suspect the instrument before believing the result.** A sweep that reports "nothing happened"
might be a broken harness. Assert on invariants, not on throws; the Session 28 traps (native
`localStorage`, missing `SAVE_KEY`, missing `character` binding, unrestored storage reader) still
apply and are recorded in Story 056.

## Non-Goals

- Fixing anything. A reproduced fourth finding gets its own story.
- Re-opening the seven Session 28 defects. They are fixed and 056's proof covers them.
- Story 058 (unreadable storage). Blocked on a CEO ruling.
- Any change to Cinder's shipped behaviour.

## Open questions

1. **Where the answer is recorded.** Recommended: `dev-results.md` plus the outcome line in this
   file. If the parent prefers a single location, `dev-results.md` is the one.

---

## OUTCOME — CLOSED by measurement (2026-10-06, Session 29)

**Result: NO FOURTH FINDING.** Scout's unnamed residual edge case is closed.

Measured against shipped **v0.26.0** `src/cinder.html` by executing the real extracted functions
(`dev/afterglow-060-residual.py`, run in Node). Not read, not inferred.

- **All Session 28 seeds A, C, G2/G3, H1/H2 are fixed on v0.26.0.** `gold: 'abc'` becomes the
  finite integer `0` (so the gates compare numerically and the player can earn their way out);
  `level: null` yields atk 2 / def 1 / hp 10; string equipment ids find their bonus (atk 15 vs 6,
  def 10 vs 3); `hp: -50` clamps to 0 and `hp: 1e9 / maxHp 26` clamps to 26.
- **The three documented non-blocking notes all reproduce as recorded**, and none is a fourth
  defect: N1 `maxHp: 'junk'` clamps hp to 0 (the clamp-ruling consequence, hp 0 reads as death at
  the inn), N2 `normalizeCharacterRecord({})` returns a level-1 hero where `normalizeDayRecord({})`
  returns null (the recorded asymmetry), N3 `flambeee-team/` is gitignored (logistics, not
  behaviour).
- **Storage and boundary sweep: no throws.** `null` / `42` / `'a string'` / `[]` all normalize to
  null; `{}` returns a record (N2). 50-char name, `xp: 12.7`, `gold: -5`, `wins: 3.2`, `level: 99`,
  `maxHp: 0` with positive hp, and an all-wrong-types object all normalize without throwing.
- **Defect E (unreadable storage) is unchanged and still ownered to Story 058.** Out of scope here.

**A harness bug was found and corrected during this run, and it is worth recording because it is
this project's recurring failure mode.** The first pass asserted `gold >= 10` for seed A and
reported a spurious FOURTH FINDING. Story 056 AC-4 is explicit that `gold: 'abc'` must normalize to
`0` and that `gold >= 10` is then **false correctly**; the defect was the type being a string, not
the value being zero. The assertion tested affordability, which is not the invariant. Corrected to
assert a finite number, and the finding disappeared. A green (or red) exit is a claim about the
script: check the harness before believing the product.

No code changed under Story 060.
