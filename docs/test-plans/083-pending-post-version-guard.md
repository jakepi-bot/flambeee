# Test Plan: Story 083 Pending-Post Version Guard (Session 37)

Source: `docs/stories/083-pending-post-version-guard.md`. P1 mechanism.
Prod change is IN PLACE at
`/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py` (outside git).
Regression coverage rides PR #150 (`scripts/test-noon-failure-alert.sh`,
lines 1-125, base `00b5441`). QA verified the guard against the live
v0.33.0 tag with its own independent runs.

## Setup

- Workdir `/home/jake/.hermes/flambeee/flambeee`, branch
  `qa/session37-082-083-084-test-plans` from `origin/main` (`00b5441`).
- Quarantine file
  `flambeee-team/state/pending-post.quarantine-2026-10-20-v0.32.0.txt`
  sha256 `656a917a8bbc46477dfc61b58f8ccdb356542da63a1d7c149fd1d063b13e2c59`
  before and after all QA runs (byte-identical, mtime 2026-10-19).
- Live newest tag resolved at QA run time via `git ls-remote --tags origin`:
  v0.33.0 (never hardcoded in the guard path; poster source confirms
  `resolve_newest_tag()` uses `git -C <repo> ls-remote --tags origin` with
  `FLAMBEEE_NEWEST_TAG` honored only as a test pin).
- No live `pending-post.txt` created; no real post sent.

## Cases

1. T1 Stale buffer refused. Given a staged buffer naming v0.32.0 (scratch
   copy of the quarantined text) and newest tag v0.33.0 resolved live, when
   the real poster runs, then no post is sent, the pending file is kept, and
   exit is 1. QA independent run (no tag pin): exit 1, stdout
   `ERROR [stale-buffer]: buffer v0.32.0 older than newest tag v0.33.0; post NOT sent, pending kept (exit=1)`,
   scratch pending copy sha256 unchanged. PASS. Regression script case
   (pinned v0.33.0): `PASS: stale-buffer-refuse (exit=1)` plus
   `PASS: stale buffer pending kept`. PASS.
2. T2 Refusal is loud. Given the stale-buffer refusal, when the poster exits,
   then the durable run-log entry plus the Story 082 alert-artifact line
   record the stale version, the newest tag, and the exit code. QA run
   alert line:
   `2026-10-21T02:08:46.869418-05:00 mode=stale-buffer exit=1 buffer v0.32.0 older than newest tag v0.33.0; post NOT sent, pending kept`.
   Run-log line:
   `2026-10-21T02:08:46.869418-05:00 result=failure mode=stale-buffer exit=1 buffer v0.32.0 older than newest tag v0.33.0; post NOT sent, pending kept`.
   Single shared `fail_loud()`, always exit 1, mode string distinguishes;
   stale refusal routes through the 082 loud path (poster source confirms).
   PASS.
3. T3 Current buffer allowed. Given a scratch buffer naming the resolved
   newest tag (v0.33.0), when the guard evaluates in dry-run, then it allows
   the normal post path with exit 0 and no alert line. Regression script:
   `PASS: current-buffer-allow-dryrun (exit=0)`. QA also notes Kai's live-tag
   dry-run ALLOW (`guard: buffer v0.33.0 vs newest tag v0.33.0: ALLOW`,
   exit 0). No real post sent in either run. PASS.
4. T4 Tag resolution is live. Given the guard code path, when it runs, then
   it resolves the newest tag via `git ls-remote --tags origin` at run time
   with no version literal in the guard path. Poster source: `VERSION_RE =
   re.compile(r"v(\\d+)\\.(\\d+)\\.(\\d+)")` parses both buffer text and
   tags; int-tuple compare; a future v0.34.0 tag is picked up with no code
   change. QA's unpinned negative run resolved v0.33.0 live, proving the
   path. PASS.
5. T5 Parse rule exactness. Buffer version is the FIRST regex match of
   `v(\\d+)\\.(\\d+)\\.(\\d+)` in the staged text; unversioned text passes
   the guard (nothing to judge stale). Documented in poster docstring and
   dev record; matches observed behavior on the v0.32.0 quarantine copy
   (first token `v0.32.0`) and the v0.33.0 scratch buffer. PASS.
6. T6 Quarantine untouched. Quarantine sha256 identical before and after
   every QA and regression run (all runs used scratch copies, never the
   live pending path); `posted-posts.log` sha256 identical, no new success
   entry. PASS.

## Verdict

6/6 QA cases pass. AC-1 through AC-5 hold: live tag resolution, negative
control REFUSE with loud signals, positive control ALLOW with no real post,
quarantine byte-identical. No blocking defects.
