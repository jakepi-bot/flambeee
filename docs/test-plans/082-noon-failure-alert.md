# Test Plan: Story 082 Noon-Failure Alert (Session 37)

Source: `docs/stories/082-noon-failure-alert.md`. P1 mechanism. Prod change is
IN PLACE at `/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py`
(outside git, reviewed via pasted diff plus hashes). Repo PR under test:
PR #150 (base `00b5441`, one file `scripts/test-noon-failure-alert.sh`,
lines 1-125). QA re-ran the committed regression script from disk against
the REAL poster path plus one independent negative test of its own.

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee`, branch
  `qa/session37-082-083-084-test-plans` from `origin/main` (`00b5441`).
- Poster sha256 on disk: `38736cb448d4dc139e7a8f3bd0affa3a5839cba6336b1026296e0bcaf1b25f17`
  (matches Kai's claimed after-hash). Backup
  `flambeee-post-noon.py.bak-2026-10-21` present next to poster.
- `crontab -l` before and after: `no crontab for jake` (no schedule change).
- Quarantine sha256 before/after all QA runs:
  `656a917a8bbc46477dfc61b58f8ccdb356542da63a1d7c149fd1d063b13e2c59`
  (138 bytes, mtime 2026-10-19, untouched).
- `posted-posts.log` sha256 before/after: `c1c358beb75c1a6a7a8a4bc7e4be7334f39af92051434c821931a4dc80b803c9`
  (no new success entry).
- Real-path `flambeee-team/state/noon-job.log` holds exactly one line (see T8).
  Real-path `flambeee-team/state/noon-failure-alert.log` does not exist: all
  simulated failures ran with scratch alert logs via `FLAMBEEE_ALERT_LOG`
  override, and the only real-path run was nothing-pending (exit 0, no alert
  expected). Recorded as observation O1, not a defect.

## Cases

1. T1 Missing interpreter. Given the venv interpreter absent (Oct 19 mode),
   when the poster runs with `FLAMBEEE_VENV` pointed at an absent path, then
   exit is 1 and the alert line records `mode=missing-interpreter exit=1`.
   Covered by regression script case 1. PASS.
2. T2 Missing creds. Given the creds file absent (Oct 18-20 mode, HOME
   redirected to an empty fakehome), when the poster runs, then exit is 1
   with `mode=missing-creds exit=1`. Covered by regression script case 2.
   PASS.
3. T3 API rejection. Given the helper exits 1 with no post URI, when the
   poster runs, then exit is 1, no success entry is written, and the alert
   line records `mode=api-rejection exit=1`. Covered by regression script
   case 6. PASS.
4. T4 Empty buffer. Given an empty staged buffer, when the poster runs, then
   no post is sent, the pending file is kept, exit is 1 with
   `mode=empty-buffer exit=1`. Covered by regression script case 3 plus
   pending-kept check. PASS.
5. T5 Over-length buffer. Given a 301-grapheme staged buffer, when the poster
   runs, then exit is 1 with `mode=over-length exit=1`, pending kept.
   Covered by regression script case 4. PASS.
6. T6 Success path unchanged. Given no pending file, when the poster runs at
   the real path, then exit is 0 with no alert line. Covered by regression
   script case 8 and by Kai's real-wrapper run (exit 0,
   `No pending post — nothing to do.`). PASS.
7. T7 Next session can check. Given the documented alert format
   `{ISO-8601 with offset} mode={mode} exit={code} {detail}`, when the next
   session reads the alert log, then each failure carries timestamp, mode,
   and exit code without re-running the job. Format confirmed on scratch
   alert lines (see T9 output). PASS.
8. T8 Real-path durable log line matches the documented format. The single
   `noon-job.log` line reads
   `2026-10-21T02:04:25.227041-05:00 result=nothing-pending mode=none exit=0 no pending file`,
   which matches the documented run-log choice (`result=` entries for
   nothing-pending). Not undocumented residue. PASS.
9. T9 Independent QA negative test (stale scratch buffer, LIVE tag
   resolution, no pin). Command:
   `env -u PYTHONPATH FLAMBEEE_PENDING=<scratch>/pending.txt
   FLAMBEEE_ALERT_LOG=<scratch>/alert.log FLAMBEEE_RUN_LOG=<scratch>/run.log
   python3 /home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py`
   with `<scratch>/pending.txt` a copy of the quarantined v0.32.0 text.
   Exit 1. Stdout:
   `ERROR [stale-buffer]: buffer v0.32.0 older than newest tag v0.33.0; post NOT sent, pending kept (exit=1)`.
   Alert line:
   `2026-10-21T02:08:46.869418-05:00 mode=stale-buffer exit=1 buffer v0.32.0 older than newest tag v0.33.0; post NOT sent, pending kept`.
   Pending copy sha256 unchanged
   (`656a917a...`). PASS: REFUSE non-zero, pending kept, loud signals fired.

## Real output (regression script from PR #150 branch, real poster path, 2026-10-21)

```
--- 082: missing interpreter (FLAMBEEE_VENV override, in-poster equivalent) ---
PASS: missing-interpreter (exit=1)
--- 082: missing creds (HOME redirect to empty fakehome) ---
PASS: missing-creds (exit=1)
--- 082: empty buffer ---
PASS: empty-buffer (exit=1)
PASS: empty buffer pending kept
--- 082: over-length buffer (301 chars) ---
PASS: over-length (exit=1)
--- 083: stale buffer REFUSE (quarantine v0.32.0 text copy vs v0.33.0) ---
PASS: stale-buffer-refuse (exit=1)
PASS: stale buffer pending kept
--- 082: API rejection (fake helper exits 1, no URI; dummy creds so pre-flight passes) ---
PASS: api-rejection (exit=1)
--- 083: current buffer ALLOW (dry-run, no real post) ---
PASS: current-buffer-allow-dryrun (exit=0)
--- 082 scenario 5: nothing pending exits 0 silently ---
PASS: nothing-pending (exit=0)
--- live-path integrity ---
PASS: quarantine file untouched
PASS: posted-posts.log untouched
=== 12 passed, 0 failed ===
SCRIPT_EXIT=0
```

## Verdict

9/9 QA cases pass; regression script 12/12 pass, exit 0. AC-1 through AC-6
hold: all cited modes fail loudly with all three signals, success path
unchanged, alert format readable by the next session, no real post sent.
Observation O1 (real-path alert file never written, scratch logs only) is
expected pre-noon behavior, not a defect.
