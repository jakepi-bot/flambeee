# Story 079: Day Pad day-3 reuse final claim (Session 36, P1, Validation)

**Status:** Ready for development (Session 36, 2026-10-20).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (validation; session ship; Principle 1 every session ships something playable).
**Assigned to:** **Riven** frontend owner (Apps surface evidence run). **Scout** witness and QA.
**Tracked by:** Session 36 plan, Story 079. Closes the 3-day reuse window opened by Story 075 (day-1, 2026-10-18) and continued by Story 077 (day-2, 2026-10-19). Sibling to Story 074, not a child of it.
**Depends on:** Story 075 (N/280 count, day-1 reuse evidence), Story 077 (CACHE 8 to 9 fix merged as PR #144, day-2 reuse passed on source path and SW path). No FPS dependency.

## Summary

Final leg of the Day Pad 3-day reuse probe. Day 3 is 2026-10-20 (this session). Evidence only, zero code change. Thing under test: the CACHE 8-to-9 activate/evict cycle did not orphan the localStorage line. The v9 install evicts every older flambeee-shell-v* cache on activate; cache eviction must not touch localStorage. A failure gets diagnosed against the right mechanism (cache vs storage), not folded into a fix.

## jakebot decision (advisory only, recorded)

Session 36 Wave 1 set A-variant, per session 20261020_011043_f6c103: P1 Day Pad day-3 reuse final validation plus P2 currency, gate as note. B (advancing the FPS playable slice before the gamepad gate has run) waits on the gate. A is not close. What would change it: a pad arriving on the rig today, which has not happened.

**Citation:** `flambeee-team/session-plan.md`, Session 36 (2026-10-20), section "jakebot decision (advisory only, recorded)", session 20261020_011043_f6c103.

## Mechanism under test (cited verbatim)

The service worker activate handler (`website/sw.js`): the v9 install evicts v8 via the activate handler (14 precached entries). localStorage is outside the Cache Storage API. Evicting a cache entry cannot delete a localStorage key unless app code writes it.

Claim to confirm: after the 8-to-9 evict, the day-2 saved line is still present under the same key, the count restores, and the countdown rolls to the new day.

## Rules carried into this story

**Evidence only, zero code change.** No diff to `website/`, `src/`, scripts, or docs beyond the evidence record. If reuse fails, output is "probe failed, cause recorded" plus a new story. Do not fold a fix into this diff.

**Same browser profile as day-2.** Day-2 and day-3 must run in the same profile or the probe is measuring the tester. Same profile, same origin, key prefix still `flambeee-apps-` before calling a missing line an app defect.

**Instrument first.** Check the instrument before believing the reading (Story 060 precedent). If the line is absent, confirm the profile, origin, and key prefix match day-2 before recording a product finding.

**No new persisted field.** Storage key prefix stays `flambeee-apps-`, maxlength 280 unchanged. Per Story 039/042 precedent, any new persisted field needs a decision record plus sign-off, which is out of scope here.

**Verifiable without the share path.** Proof is local serve plus headed Chromium on this box. No step reads `/home/jake/share/Flambeee/` (077 AC-5 carries).

**Record the rig.** Serve port, browser build, and observed N/280 at load are recorded in the evidence, not assumed.

## Requirements

### 1. Day-3 reuse probe

- Day-1 reuse evidence is 2026-10-18 (Story 075). Day-2 reuse evidence is 2026-10-19 (Story 077, source path and SW path both passed).
- Day 3 is 2026-10-20 (this session).
- Open Day Pad in the same browser profile as day-2, confirm the day-2 saved line persists across the UTC midnight boundary, the N/280 count restores at load, and the countdown rolls to the new day.

### 2. Cache-vs-storage diagnosis

- Record the active CACHE_VERSION (expected 9) and the localStorage key plus value before and after load.
- If the line is present, the claim holds: eviction did not orphan storage.
- If the line is absent, diagnose against the right mechanism: profile/origin/prefix mismatch (tester) vs cache evict touching storage (product). Record which one with evidence.

### 3. Pre-declared failure branch

- Pass: record the final claim, close the 3-day window.
- Fail: output is "probe failed, cause recorded" plus a new story number for the follow-up. Do not re-run on day 4 to complete a broken window.

### 4. Prefix and size cap

- Storage key prefix stays `flambeee-apps-` (Story 072). maxlength 280 stays enforced. Persistence behavior unchanged (same key, same restore path).
- No backend, no build step, no new server, no new dependency. localStorage only.

### 5. Rig record

- Record local-serve port, headed browser build string, and observed N/280 count at load.

## BDD scenarios

**Scenario 1: Day-3 reuse passes.**
Given the day-2 saved line from 2026-10-19 in the same browser profile, when Day Pad opens on 2026-10-20, then the saved line persists, the N/280 count restores at load, the countdown rolls to the new day, and the final reuse claim is recorded.

**Scenario 2: Evict did not orphan storage.**
Given CACHE_VERSION 9 active after the 8-to-9 evict, when storage is inspected, then the `flambeee-apps-` key still holds the day-2 line and no storage write came from the worker path.

**Scenario 3: Failure branch pre-declared.**
Given the probe runs, when reuse fails, then the output is "probe failed, cause recorded" plus a new story number, with no fix folded into this diff and no day-4 re-run to complete the window.

**Scenario 4: Instrument first.**
Given a missing line, when the finding is triaged, then profile, origin, and key prefix are confirmed against day-2 before the absence is called an app defect.

**Scenario 5: No new key.**
Given the app writes, when storage is inspected, then the `flambeee-apps-` prefix is used with no rename, maxlength 280 holds, and no new persisted field exists.

**Scenario 6: Rig recorded, no share-path read.**
Given the evidence run, when proof is recorded, then it cites serve port, browser build, and N/280 at load, uses only local serve plus headed Chromium on this box, and reads nothing from `/home/jake/share/Flambeee/`.

## Acceptance Criteria

**AC-1.** Day-3 reuse probe run 2026-10-20 in the same browser profile as day-2, result recorded either way (Scenario 1).
**AC-2.** CACHE 8-to-9 evict-vs-localStorage claim confirmed or refuted with key plus value evidence (Scenario 2).
**AC-3.** Failure branch honored as written: fail output is cause plus new story, no fix in this diff, no day-4 re-run (Scenario 3).
**AC-4.** Instrument-first check recorded before any product finding on a missing line (Scenario 4).
**AC-5.** Prefix stays `flambeee-apps-`, maxlength 280, no new persisted field (Scenario 5).
**AC-6.** Serve port, browser build, and N/280 at load recorded; no share-path read (Scenario 6).
**AC-7.** Zero code change: `git diff --stat` on `website/`, `src/`, and `scripts/` is empty.
**AC-8.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Any code change, including a cache, count, or copy tweak.
- A second app or a second improvement in the same diff.
- Advancing the FPS playable slice before the gamepad gate has run.
- A gamepad run on this box. There is no pad here; see the note below.
- Re-running on day 4 to complete a broken window.

## Notes (not stories, carried by this file)

1. **Headed gamepad gate: OPEN-BLOCKED-ON-HARDWARE.** Pointer to the Story 074 runnable gate verbatim (rig jake-dev-desk, headed mode, pass criteria, Kai runs plus Scout witnesses, Session 35). Flip trigger: pad plus headed browsers available on the named rig. Carry-forward line: each subsequent session carries this note until it flips.
2. **3-day window closes here.** Pass records the final claim; fail records cause plus a new story. Either way the window is closed.

## Open questions for dev wave

1. Same-profile confirmation vs day-2 (profile name or path, origin, key prefix observed).
2. Local-serve port and headed browser build string for the evidence record.
3. If fail: cause diagnosis (tester vs product mechanism) and proposed new story number.
