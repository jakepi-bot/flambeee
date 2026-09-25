# Test Plan: Story 046 - Website Currency Verification After the v0.22.0 Release Commit (Session 24, Two-Run Step)

**Story:** `docs/stories/046-website-currency-post-release-verification.md` (12 BDD scenarios)
**Code under test:** `scripts/verify-website-currency.sh` (unmodified since v0.19.0) and the deploy mirrors it checks.
**Baseline for the checker:** sha256 `bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92` at session entry.
**Recording target:** `/home/jake/.openclaw/workspace/flambeee-team/release-chain.md` (outside the repo, never committed), written **after** today's `session-plan.md`.
**Owner:** Scout runs both runs and the mirror comparison; Riven is the fix path; Vigil confirms truthful recording.

## What is being verified

The standing two-run release step, carried forward from Stories 041 and 043. Run 1 happens before release work on the entering state. Run 2 happens after the Wave 4 website What's New update for v0.22.0 and its live sync, and its heading must name **v0.22.0**. A release is not complete until run 2 is recorded and green. Run 1 alone never satisfies the step.

New this session: Story 044 changes `src/cinder.html`, so the Cinder deploy mirror `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` must also be compared, with the `cmp` exit code and the **sha256 of both files** recorded explicitly, at the ABSOLUTE path. The recorded values are the **post-merge** ones and must be equal.

## Method

`bash scripts/verify-website-currency.sh` is run from the repo root, exactly as documented, and never modified or wrapped. The command, the exit code and the full output are pasted. The Cinder mirror comparison is a plain `cmp` plus `sha256sum`, recorded as its own chain step; it is **not** a new script and this plan adds none.

## Scenario coverage

### S1 Run 1 before release, recorded (P3)
Run the checker at the start of release work, before any merge, tag, or website edit. Record the command, exit code, and auditable output in `release-chain.md`. A non-zero exit stops release work and opens the fix path.
**Expected:** PASS, exit 0.

### S2 Run 1 is green on the entering state (P3)
Assert PASS with exit 0, the What's New heading names the true latest `origin` tag (v0.21.0 at session entry, pre-release for v0.22.0), the live file and repo mirror are byte-identical (`cmp` exit 0), the summary has no em dashes and no heavy emoji, Releases and Blog are real `<a href>` anchors, and every relative Play-link target exists.
**Expected:** PASS.

### S3 Run 2 after the Wave 4 website update, recorded, heading names v0.22.0 (P3)
After the release commit and the What's New edit for v0.22.0 and the live sync, run the checker again. Record the same set of facts, with the heading naming **v0.22.0**.
**Expected:** PASS. This run belongs to the release wave; it is not executable at Wave 3 time and is recorded here as the required second half of the step.

### S4 Cinder deploy mirror compared and recorded with sha256 (P3)
After Story 044 is merged and the mirror is synced, compare `src/cinder.html` against `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Record the absolute path, the `cmp` exit code, and the sha256 of both files. Assert `cmp` exit 0 and identical sha256.
**Pre-merge baseline recorded at Wave 3:** `cmp` exit 0, both 60754 bytes, both sha256 `e48a1040083013f8e153cf8262074e20115d23245200b36502054f4e9febb56e`. These values **will change** when Story 044 lands; the recorded post-merge values must match each other.
**Expected:** PASS post-merge.

### S5 A stale game mirror fails the step (P3)
If the mirror was not synced after the Story 044 merge, assert non-zero `cmp` and differing sha256 are recorded, the mirror is re-synced, the comparison is re-run, the green result is recorded, and the failure itself stays in the chain.
**Expected:** not triggered if the mirror is synced. Recorded so the negative branch is covered.

### S6 Post-release drift is caught by the checker (P3)
If What's New is updated but the live file is not re-synced, or the heading names the wrong version, or new copy contains an em dash, assert a non-zero exit with a specific FAIL line naming the check, a small accuracy fix on base `main`, a re-sync, and a recorded green re-run.
**Expected:** PASS by catching nothing (no drift) or by catching drift and recording the fix.

### S7 A release is not complete without run 2 (P3)
Assert both website runs and the mirror comparison appear in the chain with exit codes and sha256 values, and the chain does not declare the release verified on run 1 alone.
**Expected:** PASS. Any chain entry that closes the release on run 1 is a blocking process defect.

### S8 The checker is not silently modified (P3)
Assert `scripts/verify-website-currency.sh` is byte-identical to its v0.19.0 state and no new verification script was added.
**Verification:** `sha256sum scripts/verify-website-currency.sh` must equal `bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92`.
**Expected:** PASS.

### S9 Truthful recording (P3)
Compare the recorded exit codes, outputs, and sha256 values against the real command output and real repository state. Assert nothing is green that was not green, and any failed run that was fixed shows both the failure and the green re-run.
**Expected:** PASS.

### S10 The absolute mirror path is used, not a relative path (P3)
Assert the chain entry names `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html` in full, and no relative `share/...` path appears anywhere in the record.
**Expected:** PASS. A relative path resolves to nothing from inside the repo and would silently produce a misreadable empty comparison.

### S11 A Story 045 website copy correction is covered by run 2 (P3)
If Story 045 corrected a reload-guard claim on the website What's New block, assert the corrected copy is present in the state run 2 verifies and the chain records that run 2 covered it.
**Expected:** PASS if Story 045 edited the website; otherwise recorded as "no website edit from Story 045".

### S12 The chain is written after the session plan (P3)
Compare `release-chain.md` and today's `session-plan.md` write times. Assert `release-chain.md` is newer.
**Expected:** PASS.

## Negative and boundary matrix

| Case | Condition | Expected |
|------|-----------|----------|
| Live file missing | `share/Flambeee/index.html` absent | FAIL exit 1, precondition line names the path |
| Repo mirror missing | `website/index.html` absent | FAIL exit 1 |
| Live and mirror differ by one byte | unsynced edit | FAIL, `cmp exit 1`, first differing line printed |
| Heading names the previous tag | stale What's New | FAIL naming the heading check |
| Heading names a tag that does not exist yet | pre-tag drift, seen Session 23 | FAIL exit 1; the exact drift class this step exists to catch |
| Em dash in the summary | tone violation | FAIL on the em-dash check |
| Heavy emoji in the summary | tone violation | FAIL on the emoji check |
| Releases URL as bare text | not clickable | FAIL on the anchor check |
| Play link target missing | `games/*.html` absent | FAIL naming the missing target |
| Cinder mirror stale after merge | `cmp` non-zero | mirror step FAILs, re-sync and re-record required |

## Verdict

**Test plan status: written 2026-09-25. Run 1 and the pre-merge mirror baseline were executed at Wave 3 time and are recorded in `/home/jake/.openclaw/workspace/flambeee-team/qa-results.md`, Session 24 section. Run 2 and the post-merge mirror values belong to the release wave and remain open until recorded.**

QA verifies and reports. The checker script is not modified and no new verification script is added.
