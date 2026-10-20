# Story 081: Day Pad mechanism probe, seeded restore plus evict isolation (Session 36, P1, Validation)

**Status:** Ready for development (Session 36, 2026-10-20).
**Author:** Quinn (Business Analyst), Wave 2 follow-up to Story 079.
**Priority:** P1 (validation; session ship).
**Assigned to:** **Riven** frontend owner (probe run plus evidence record). **Scout** witness and QA.
**Tracked by:** Session 36 plan, Story 081. Opened by the Story 079 pre-declared failure branch: 079 output was "probe failed, cause recorded" (same-profile premise unrecoverable; temp scoped profile dirs GC'd; no day-2-saved line survives on disk; UTC-midnight crossing unreachable in-session), so this new story carries the testable part of the claim. Closes nothing from Story 075 or 077; those stand as recorded.
**Depends on:** Story 077 (CACHE 8 to 9 fix merged as PR #144, day-2 reuse passed on source path and SW path). Story 079 (failure record with absence-check commands). No FPS dependency.

## Summary

Testable mechanism probe for the claim Story 079 could not reach. Same-profile day-2 to day-3 reuse is unrecoverable (079 cause recorded), so this story drops the same-profile requirement and tests the underlying mechanism directly in a fresh profile: a day-2-stamped line seeded under the production key restores at load with the N/280 count, the countdown renders the current UTC day, and the CACHE_VERSION 9 activate/evict cycle does not orphan the storage key. Evidence only, zero code change. If the seeded line fails to restore, or the key is orphaned after eviction, that is a real product defect and earns a fix story. If the probe passes, the mechanism holds and no fix story is opened.

## jakebot decision (advisory only, recorded)

Session 36 Wave 3 set A-variant, per session 20261020_015621_af95e4: Story 079 same-profile premise is unrecoverable (Session 35 temp scoped profile dirs garbage-collected; parent verified no surviving profile dir and no leveldb with the day-2 line), so 079 verdict is probe-failed-cause-recorded plus new story 081 with a testable claim. B (advancing the FPS playable slice before the gamepad gate has run) waits on the gate. A is not close.

## Mechanism under test (cited verbatim)

The service worker activate handler (`website/sw.js`): the v9 install evicts v8 via the activate handler (14 precached entries). localStorage is outside the Cache Storage API. Evicting a cache entry cannot delete a localStorage key unless app code writes it. The app restore path (`website/apps/index.html` `loadNote`): reads `flambeee-apps-daypad-note` at load, fills the input, renders N/280.

Claim to confirm: after seeding a day-2-stamped line under the production key in a fresh profile, Day Pad restores it at load with the N/280 count, the countdown renders the current UTC day (day-3, 2026-10-20), and after the CACHE 9 activate/evict the key still holds the seeded line.

## Rules carried into this story

**Evidence only, zero code change.** No diff to `website/`, `src/`, scripts, or docs beyond this story file plus the results records. A failed falsifying test earns a NEW fix story; no fix is folded into this diff.

**Fresh profile, stated seed.** The probe runs in a fresh Chromium profile dir under scratch. The seed line is written with `localStorage.setItem` under the production key and is stamped day-2 (2026-10-19) on its face, standing in for the day-2 save that 079 could not recover. Seed text, key, profile path, serve port, and browser build are recorded.

**Instrument first.** If the line does not restore, confirm origin, key, and profile match the seed step before calling it a product finding (Story 060 precedent).

**No new persisted field.** Storage key stays `flambeee-apps-daypad-note` (prefix `flambeee-apps-`), maxlength 280 unchanged. Per Story 039/042 precedent, any new persisted field needs a decision record plus sign-off, which is out of scope here.

**Verifiable without the share path.** Proof is local serve plus headless Chromium on this box (headed unavailable, no DISPLAY; headless exercises identical code paths, build string recorded). No step reads `/home/jake/share/Flambeee/`.

**Falsifying test on its face.** This probe passes only if every check below holds. If the seeded line fails to restore at load, or the storage key is orphaned (missing or altered) after the CACHE 9 activate/evict, the probe FAILS and the failure is recorded as a real product defect earning a fix story with a new number. A pass records the mechanism claim; a fail records cause plus the fix-story number.

## Requirements

### 1. Seed under the production key in a fresh profile

- Fresh Chromium profile dir under scratch (path recorded; the dir must not exist before the run).
- Serve the repo tree on 127.0.0.1 with a fresh port (Session 35 used 8477; pick another, record it).
- Seed line stamped day-2 on its face (contains `2026-10-19`), written via `localStorage.setItem('flambeee-apps-daypad-note', seed)` on the served origin. Record key plus value (localStorage readback before load).

### 2. Restore at load

- Reload Day Pad. The input holds the seeded line, the count label reads N/280 where N is the seed length, the UTC date reads the current day (day-3, 2026-10-20), and the countdown renders a live HH:MM:SS to midnight UTC. Record N/280 at load, UTC date text, and countdown text.

### 3. CACHE 9 activate/evict does not orphan storage

- Drive the v9 service worker install plus activate/evict on the served origin (register from the site root so the SW controls the origin, reload until the worker is active and older `flambeee-shell-v*` caches are evicted).
- Record `caches.keys()`, the localStorage key plus value before the evict and after the evict, and the CACHE_VERSION line from the served `website/sw.js`.
- Pass requires the key plus value byte-identical before and after, and the restored count still N/280 on the next SW-controlled load of Day Pad.

### 4. Prefix and size cap

- Storage key prefix stays `flambeee-apps-`, maxlength 280 stays enforced on the input (attribute read from disk). Persistence behavior unchanged (same key, same restore path).
- No backend, no build step, no new server, no new dependency. localStorage only.

### 5. Rig record

- Record local-serve port, browser build string, and observed N/280 count at load.

## BDD scenarios

**Scenario 1: Seeded line restores at load.**
Given a day-2-stamped line seeded under `flambeee-apps-daypad-note` in a fresh profile, when Day Pad loads, then the input holds the seeded line and the count label reads N/280 with N equal to the seed length.

**Scenario 2: Countdown renders the current UTC day.**
Given the seeded profile, when Day Pad loads on 2026-10-20, then the UTC date reads the current day and the countdown renders live time to midnight UTC.

**Scenario 3: Evict does not orphan storage.**
Given CACHE_VERSION 9 active after the install plus activate/evict, when storage is inspected before and after, then the `flambeee-apps-daypad-note` key holds the identical seeded value on both sides and no storage write came from the worker path.

**Scenario 4: Falsifying test stated.**
Given the probe runs, when the seeded line fails to restore at load or the key is missing or altered after the evict, then the probe FAILS, the failure is recorded as a real product defect, and a new fix-story number is opened. No fix is folded into this diff.

**Scenario 5: No new key.**
Given the app writes, when storage is inspected, then the `flambeee-apps-` prefix is used with no rename, maxlength 280 holds, and no new persisted field exists.

**Scenario 6: Rig recorded, no share-path read.**
Given the evidence run, when proof is recorded, then it cites serve port, browser build, and N/280 at load, uses only local serve plus headless Chromium on this box, and reads nothing from `/home/jake/share/Flambeee/`.

## Acceptance Criteria

**AC-1.** Probe run 2026-10-20 in a fresh profile (path recorded, dir new at run start) with the day-2-stamped seed written under the production key, key plus value recorded by localStorage readback (Scenario 1).
**AC-2.** Restore at load recorded: input value equals seed, count label N/280 with N equal to seed length, UTC date reads day-3, countdown renders live HH:MM:SS (Scenarios 1, 2).
**AC-3.** CACHE 9 activate/evict run on the served origin with `caches.keys()` plus key plus value recorded before and after; pass requires byte-identical value and N/280 still restoring on the next SW-controlled load (Scenario 3).
**AC-4.** Falsifying test honored as written: restore failure or post-evict orphan/mutation equals FAIL plus a real-defect record plus a new fix-story number, no fix in this diff (Scenario 4).
**AC-5.** Prefix stays `flambeee-apps-`, maxlength 280 read from disk, no new persisted field (Scenario 5).
**AC-6.** Serve port, browser build, and N/280 at load recorded; no share-path read (Scenario 6).
**AC-7.** Zero code change: `git diff --stat` on `website/`, `src/`, and `scripts/` is empty.
**AC-8.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Any code change, including a cache, count, or copy tweak.
- A second app or a second improvement in the same diff.
- Re-running Story 079 or re-opening the day-2 to day-3 same-profile window.
- Advancing the FPS playable slice before the gamepad gate has run.
- A gamepad run on this box. There is no pad here; see the note below.
- Writing to `/home/jake/share/Flambeee/` or assuming the deploy mirror state.

## Notes (not stories, carried by this file)

1. **Headed gamepad gate: OPEN-BLOCKED-ON-HARDWARE.** Pointer to the Story 074 runnable gate verbatim (rig jake-dev-desk, headed mode, pass criteria, Kai runs plus Scout witnesses, Session 35). Flip trigger: pad plus headed browsers available on the named rig. Carry-forward line: each subsequent session carries this note until it flips.
2. **079 window is closed.** Story 079 recorded probe-failed-cause-recorded plus this story number. This story does not re-open that window; it tests the mechanism with a stated seed instead.

## Open questions for dev wave

1. Fresh profile path, serve port, and browser build string for the evidence record.
2. Seed text (day-2-stamped) plus N for the N/280 count at load.
3. If the falsifying test trips: cause diagnosis (tester vs product mechanism) plus proposed fix-story number.
