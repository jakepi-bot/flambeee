# Story 086: Hardened-poster mirror under git (Session 38, P2, Mechanism)

**Status:** Ready for development (Session 38, 2026-10-22).
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P2 (mechanism; vendored mirror plus pin).
**Assigned to:** **Kai** backend owner (mirror plus pin plus checker). **Scout** witness and QA.
**Tracked by:** Session 38 plan, Story 086. Follows Stories 082 and 083 plus the Session 37 roadmap Current State entry.
**Depends on:** Live hardened poster outside git (path below). Story 085 is independent; either may land first. No FPS dependency. No gamepad dependency.

## Summary

Get the hardened poster under git as a vendored mirror copy with a recorded sha256 pin plus a checker that verifies byte-identity against the live file. The running code today lives outside version control, so "merged" does not mean "shipped" for the 082 and 083 fixes until the pin verifies. Zero user-visible change. The live layout is untouched; the backup is kept.

## jakebot decision (advisory only, recorded)

Session 38 Wave 1 priorities per session 20261022_011059_0b55b4: P2 poster mirror plus byte-identity pin, with the "merged does not mean shipped" caveat standing until the pin verifies. No release implied.

**Citation:** `flambeee-team/session-plan.md`, Session 38 (2026-10-22), section "jakebot decision (advisory only, recorded)", session 20261022_011059_0b55b4.

## Live file cited verbatim

- Live hardened poster: `/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py`
- sha256 at Session 38 planning: `38736cb448d4dc139e7a8f3bd0affa3a5839cba6336b1026296e0bcaf1b25f17`
- Backup kept: `flambeee-post-noon.py.bak-2026-10-21` (rollback exercised Session 37, kept in place)

## Requirements

### 1. Vendored-mirror-plus-pin rule

Copy the live hardened poster byte-for-byte into the repo as a vendored mirror (proposed path `scripts/flambeee-post-noon.mirror.py`; dev records the final path if it differs). Record the sha256 pin in two places: in the dev record and in a sidecar pin file next to the mirror (proposed `scripts/flambeee-post-noon.mirror.py.sha256`). The mirror is a verbatim vendored copy, not a rewrite: no logic edits in the mirror diff. Any drift between mirror and live file is reported, never silently resolved.

### 2. Byte-identity checker contract (against the live file)

New checker script in the repo (proposed `scripts/verify-poster-mirror.sh`) that verifies byte-identity of the vendored mirror against the live file at the absolute path above. Contract:

- Compares mirror bytes against `/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py` with `cmp` plus equal sha256 on both sides, and compares the mirror against the recorded pin.
- Prints both sha256 values, the pin value, and exit code. Exit 0 only when mirror equals live file and both equal the pin.
- Reads the live file only; never writes to it, never moves it, never edits it.
- Takes no action on mismatch beyond a non-zero exit and a readable report (which side differs is stated, not fixed).

### 3. Live-layout-untouched constraint

The live poster stays where it is. The backup `flambeee-post-noon.py.bak-2026-10-21` stays where it is. Dev runs no post, sends no real post, edits no schedule, creates no live buffer, and leaves the quarantine file and posted-posts.log untouched. Proof is the checker output plus `ls -l` of the live dir before and after, not adjectives.

### 4. "Merged does not mean shipped" caveat

The caveat stands until the pin verifies: the running code is whatever bytes sit on that disk. When the checker exits 0 with mirror sha256 equal to live sha256 equal to the pin `38736cb448d4dc139e7a8f3bd0affa3a5839cba6336b1026296e0bcaf1b25f17`, the Session 38 entry may record the mirror as verified. If the live file has changed since planning, dev records the new live sha256, does not overwrite the mirror to match without a recorded decision, and the story does not claim verification.

### 5. No FPS advancement

No FPS or playable-slice change in this diff. No gamepad run on this box.

## BDD scenarios

**Scenario 1: Mirror is byte-identical to live.**
Given the live poster at the absolute path with the cited sha256, when the vendored mirror is compared, then `cmp` exits 0 and both sha256 values equal the pin.

**Scenario 2: Checker verifies the pin.**
Given the mirror plus sidecar pin in the repo, when the checker runs, then it prints mirror sha256, live sha256, and pin value, and exits 0 on full agreement.

**Scenario 3: Checker reports drift loudly.**
Given a mirror that differs by even one byte from the live file, when the checker runs, then it exits non-zero and states which side differs without editing either side.

**Scenario 4: Live layout untouched.**
Given the live dir listing before the story, when the story lands, then the live poster and the backup remain in place with unchanged bytes, no post has been sent, and no schedule has been edited.

## Acceptance Criteria

**AC-1.** Vendored mirror in the repo is byte-identical to the live file with `cmp` exit 0 and equal sha256 recorded (Scenario 1).
**AC-2.** sha256 pin `38736cb448d4dc139e7a8f3bd0affa3a5839cba6336b1026296e0bcaf1b25f17` recorded in the dev record plus the sidecar pin file (Scenarios 1, 2).
**AC-3.** Byte-identity checker in the repo verifies mirror against the live absolute path, printing both sha256 values plus pin plus exit code; drift case exits non-zero with no writes (Scenarios 2, 3).
**AC-4.** Live layout untouched: live poster and backup in place, `ls -l` before and after recorded, no post sent, no schedule edit, quarantine and posted-posts.log untouched (Scenario 4).
**AC-5.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- Changing poster logic (mirror is verbatim; behavior changes are separate stories).
- Syncing the mirror back to live or live to mirror on mismatch (report only; any sync is a recorded decision, not a quiet fix).
- Restoring creds, changing post copy, or touching the success archive format.
- Any website, game-file, or release change.
- Advancing the FPS playable slice before the gamepad gate has run.
- A gamepad run on this box. There is no pad here; see the note below.

## Notes (not stories)

1. **Headed gamepad gate: DEFERRED-UNTIL-PAD-EXISTS on rig jake-dev-desk.** Runnable gate verbatim lives in Story 074 in this dir. Returns only when a pad exists. Per Session 38 plan this line is not carried forward session to session.

## Open questions for dev wave

1. Final mirror path and pin sidecar path (record both if they differ from the proposal).
2. Checker output sample with real sha256 values plus exit code, and `ls -l` of the live dir before and after.
3. If the live sha256 has moved since planning, the new value plus the recorded decision (no silent overwrite).
