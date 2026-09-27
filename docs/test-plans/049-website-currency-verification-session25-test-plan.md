# Test Plan: Story 049 - Website Currency Verification, Two Runs for the v0.23.0 Release (Session 25)

**Story:** `docs/stories/049-website-currency-verification-session25.md` (13 BDD scenarios)
**Code under test:** `scripts/verify-website-currency.sh` (unmodified since v0.19.0; sha256 `bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92` at session entry). Plus the Cinder deploy mirror compared by `cmp`/`sha256sum` (not a script).
**Recording target:** `/home/jake/.openclaw/workspace/flambeee-team/release-chain.md` (outside the repo, never committed), written **after** today's `session-plan.md`.
**Owner:** Scout runs both runs and the mirror comparison; Riven is the fix path; Vigil confirms truthful recording.
**Baseline at requirements time:** live `/home/jake/.openclaw/workspace/share/Flambeee/index.html` 43557 bytes, heading names v0.22.0; `src/cinder.html` 64445 bytes; mirror `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` 64445 bytes, byte-identical.

## What is being verified

The standing two-run release step: run 1 pre-release on the entering state (heading names the true latest `origin` tag, expected v0.22.0 pre-release for v0.23.0), run 2 post-release after the What's New update and live sync (heading must name **v0.23.0**). Plus the explicit Cinder deploy-mirror comparison with `cmp` exit code and the sha256 of both files, at the ABSOLUTE path. A release is not complete until run 2 is recorded and green. The checker is not modified and no new verification script is added.

## Method

`bash scripts/verify-website-currency.sh` is run from the repo root, exactly as documented, never modified or wrapped. The command, exit code, and full output are pasted. The mirror comparison is a plain `cmp` plus `sha256sum`, recorded as its own chain step; it is not a new script.

## Scenario coverage

### S1 Run 1 before release, recorded (P3) - EXECUTED
Run the checker at the start of release work, before any merge, tag, or website edit. Record the command, exit code, and auditable output. A non-zero exit stops release work and opens the fix path.
**Expected:** PASS, exit 0.

### S2 Run 1 is green on the entering state (P3) - EXECUTED
Assert PASS exit 0, heading names the true latest `origin` tag (v0.22.0, pre-release for v0.23.0), live file and repo mirror byte-identical (`cmp` exit 0), no em dashes / heavy emoji in the summary, Releases and Blog are real `<a href>` anchors, every relative Play-link target exists.
**Expected:** PASS.

### S3 Run 2 after the release and website update, heading names v0.23.0 (P3) - OPEN
After the release commit and the What's New edit for v0.23.0 and the live sync, run the checker again. Record the same facts, heading naming **v0.23.0**.
**Expected:** PASS. Belongs to the release wave; not executable at Wave 3 time.

### S4 Cinder deploy mirror compared and recorded with `cmp` and sha256 (P3) - BASELINE RECORDED
After Story 047 is merged (or landed no change) and the mirror is synced, compare `src/cinder.html` against `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Record the absolute path, `cmp` exit code, and sha256 of both files.
**Pre-merge baseline at Wave 3:** `cmp` exit 0, both 64445 bytes, both sha256 `0dd0c0104ccc6a361ed56e05d01f749ea1cc742295c3055bac954fa7bc88efa5`. These values **change** if Story 047 lands a code change; the recorded post-merge values must match each other.
**Expected:** PASS post-merge.

### S5 A stale game mirror fails the step (P3)
If the mirror was not synced after the Story 047 merge, assert non-zero `cmp` and differing sha256 are recorded, the mirror is re-synced, the comparison re-run, the green result recorded, and the failure itself stays in the chain.
**Expected:** not triggered if the mirror is synced; the branch is covered.

### S6 Post-release drift is caught by the checker (P3)
If What's New is updated but the live file is not re-synced, or the heading names the wrong version, or new copy contains an em dash, assert a non-zero exit with a specific FAIL line, a small accuracy fix on base `main`, a re-sync, and a recorded green re-run.
**Expected:** PASS by catching nothing, or by catching drift and recording the fix.

### S7 A release is not complete without run 2 (P3)
Assert both website runs and the mirror comparison appear in the chain with exit codes and sha256 values, and the chain does not declare the release verified on run 1 alone.
**Expected:** PASS. Any chain entry closing the release on run 1 is a blocking process defect.

### S8 The checker is not silently modified (P3)
Assert `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state and no new verification script was added.
**Verification:** `sha256sum scripts/verify-website-currency.sh` equals `bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92`.
**Expected:** PASS.

### S9 Truthful recording (P3)
Compare the recorded exit codes, outputs, and sha256 values against real command output and real repo state. Assert nothing is green that was not green; any fixed failure shows both failure and green re-run.
**Expected:** PASS.

### S10 The absolute mirror path is used, not a relative path (P3)
Assert the chain entry names `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` in full, and no relative `share/...` path appears in the record.
**Expected:** PASS.

### S11 A Story 047 narrowed website claim is covered by run 2 (P3)
If Story 047 narrowed or left a claim on the website What's New block after its proof, assert the resulting copy is present in the state run 2 verifies and the chain records that run 2 covered it.
**Expected:** PASS if Story 047 edited the website; otherwise recorded as "no website edit from Story 047".

### S12 The step is independent of the Story 047 outcome (P3)
Assert both runs and the mirror comparison execute either way, and the chain records the state truthfully in both cases (changed sha256 with re-synced mirror, or unchanged sha256 with mirror still byte-identical).
**Expected:** PASS.

### S13 The chain is written after the session plan (P3)
Compare `release-chain.md` and today's `session-plan.md` write times; assert `release-chain.md` is newer.
**Expected:** PASS.

## Negative and boundary matrix

| Case | Condition | Expected |
|------|-----------|----------|
| Live file missing | `share/Flambeee/index.html` absent | FAIL exit 1, precondition line names the path |
| Repo mirror missing | `website/index.html` absent | FAIL exit 1 |
| Live and mirror differ by one byte | unsynced edit | FAIL, `cmp exit 1`, first differing line printed |
| Heading names the previous tag | stale What's New | FAIL naming the heading check |
| Heading names a tag that does not exist yet | pre-tag drift (seen Session 23) | FAIL exit 1 |
| Em dash in the summary | tone violation | FAIL on the em-dash check |
| Heavy emoji in the summary | tone violation | FAIL on the emoji check |
| Releases URL as bare text | not clickable | FAIL on the anchor check |
| Play link target missing | `games/*.html` absent | FAIL naming the missing target |
| Cinder mirror stale after merge | `cmp` non-zero | mirror step FAILs, re-sync and re-record required |
| Relative `share/...` path in the record | path error | FAIL S10 |

## Verdict

**Test plan status: written 2026-09-27. Run 1 (pre-release) and the pre-merge mirror baseline were executed at Wave 3 time and are recorded in `/home/jake/.openclaw/workspace/flambeee-team/qa-results.md`, Session 25 section. Run 2 and the post-merge mirror values belong to the release wave and remain open until recorded.**

QA verifies and reports. The checker script is not modified and no new verification script is added.
