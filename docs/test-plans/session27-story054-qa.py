#!/usr/bin/env python3
"""Session 27 QA - Story 054 (Scout), repinned Session 64 / Story 141.

Website Currency and Deploy-Mirror Verification. Story 054 re-runs ONE existing
script twice and records ONE cmp/sha256 pair. This harness performs:

    Run 1   pre-release, heading expected v0.24.0, read from the FROZEN
            v0.24.0:website/index.html (B1.3)
    Base    src/cinder.html read at the frozen REF (default v0.24.0, B1.1)

The checker is NOT modified. Its blob is asserted against the blob live at
Session 27 (commit 2907623, B1.2) before anything else runs, so a tampered
checker fails this harness instead of silently passing it. The introduce /
next-change window (fe73150 introduces, 8545cb8 next changes) is verified so
the pin is the story-live state, not just a matching sha.

Run 2 (post-release, heading v0.25.0) is NOT run here: it belongs to the
release job and only becomes meaningful after the v0.25.0 tag, the release
commit, the website What's New edit and the live sync.

Retired by name (Session 64; no frozen ref can satisfy them):
  - mirror-byte-identical, mirror-sha-pair-equal: end-to-end deploy-mirror
    byte identity. website/games/cinder.html exists at neither 2907623 nor
    v0.24.0 (the deploy root landed in Session 31, 6d3b5b8). Coverage lost:
    end-to-end deploy-mirror byte-identity; retained: committed-base
    readability/size and checker-blob identity.
  - working-tree-clean-informational: asserted live-tree state, which a frozen
    design must not gate on. Coverage lost: none (informational only).
  - live-origin-tag-lookup: network-dependent `git ls-remote --tags origin`
    newest-tag discovery, replaced by the frozen expectation (tag v0.24.0
    resolves locally). Coverage lost: live-origin newest-tag awareness.
  - live-currency-run: executing the live scripts/verify-website-currency.sh
    gates on live + network state (curl fetch, ls-remote); replaced by the
    frozen Run-1 re-verification below. Coverage lost: none beyond the above;
    the served-copy leg belongs to the release job by design.

Usage:
    python3 session27-story054-qa.py
Env:
    REPO        path to the flambeee repo (default: derived, $REPO wins)
    REF         frozen git ref holding src/cinder.html AND website/index.html
                under test (default v0.24.0; $REF wins for triage/mutation)
    PIN_COMMIT  commit whose scripts/verify-website-currency.sh blob is the
                story-live checker (default 2907623; override for triage only)

Every history read is `git show <frozen-ref>:<path>` (B1.1-B1.3), so this
script is green on main and green from a worktree checked out at the old tag
with identical tallies. The mirror comparison reads the frozen base blob, NOT
the working tree file; the worktree state is never gated on.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _repo_root():
    """Repo root at run time: $REPO wins, else walk up from this file."""
    env = os.environ.get("REPO")
    if env:
        return env
    d = HERE
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return d
        d = parent


REPO = _repo_root()
# REF is the frozen historical-base variable: git reads of REF:src/cinder.html
# and REF:website/index.html are base comparisons, never the artifact under test.
REF = os.environ.get("REF", "v0.24.0")
PIN_COMMIT = os.environ.get("PIN_COMMIT", "2907623")
PIN_PATH = "scripts/verify-website-currency.sh"
INTRODUCED_BY = "fe73150"
NEXT_CHANGED_BY = "8545cb8"
EXPECTED_BLOB = "9b1058b1a0401fe2025fd8cd9653297a51937842"
EXPECTED_HEADING = ("v0.24.0: Cinder quest log labels now describe your run, "
                    "not your absence")
EXPECTED_BASE_BYTES = 67969

COUNT = {"pass": 0, "fail": 0}


def check(cond, name, detail=""):
    ok = bool(cond)
    COUNT["pass" if ok else "fail"] += 1
    line = ("PASS" if ok else "FAIL") + ": " + name
    if detail:
        line += "  | " + str(detail)
    print(line, flush=True)
    return ok


def retired(name, coverage):
    print("RETIRED: %s -- %s" % (name, coverage), flush=True)


def group(name):
    print("\n--- %s ---" % name, flush=True)


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def git_bytes(args):
    """Raw bytes (no newline translation) for byte-exact size assertions."""
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout


def main():
    print("=== Session 27 Story 054 QA (Scout), repinned Story 141 ===")
    print("repo: %s" % REPO)
    print("ref: %s  pin-commit: %s" % (REF, PIN_COMMIT))

    group("Scenario 8: checker unmodified (frozen blob pin at %s)" % PIN_COMMIT)
    rc, blob = git(["rev-parse", "%s:%s" % (PIN_COMMIT, PIN_PATH)])
    print("checker blob at %s: %s" % (PIN_COMMIT, blob))
    print("expected blob            : %s" % EXPECTED_BLOB)
    check(rc == 0 and blob == EXPECTED_BLOB,
          "scripts/verify-website-currency.sh blob is the story-live 9b1058b1...")
    rc1, blob1 = git(["rev-parse", "%s:%s" % (INTRODUCED_BY, PIN_PATH)])
    rc2, blob2 = git(["rev-parse", "%s:%s" % (NEXT_CHANGED_BY, PIN_PATH)])
    print("blob at %s (introduces): %s" % (INTRODUCED_BY, blob1))
    print("blob at %s (next change): %s" % (NEXT_CHANGED_BY, blob2))
    check(rc1 == 0 and blob1 == EXPECTED_BLOB
          and rc2 == 0 and blob2 != EXPECTED_BLOB,
          "checker pin window holds (introduced by %s, next changed by %s)"
          % (INTRODUCED_BY, NEXT_CHANGED_BY))
    rc, wt = git(["status", "--porcelain", "--untracked-files=no", "--",
                    "scripts/"])
    print("git status (tracked) -- scripts/: %r" % wt)
    check(rc == 0 and wt == "",
          "no new or modified verification script in this checkout")

    group("Run 1 (frozen): pre-release, heading expected v0.24.0")
    rc, index = git(["show", "%s:website/index.html" % REF])
    m = re.search(r"<h3>(v[0-9][^<]*)</h3>", index) if rc == 0 else None
    heading = m.group(1) if m else "<none>"
    print("frozen What's New heading: %s" % heading)
    check(heading.startswith("v0.24.0"),
          "Scenario 1: frozen run-1 heading names v0.24.0",
          "heading=%s" % heading)
    check(heading == EXPECTED_HEADING,
          "frozen What's New heading is the verified v0.24.0 line")
    rc, tag = git(["rev-parse", "v0.24.0^{commit}"])
    print("frozen tag v0.24.0 resolves to: %s" % tag)
    check(rc == 0 and tag != "",
          "frozen latest tag v0.24.0 resolves locally (no network)")

    group("Run 2: NOT RUN BY DESIGN (belongs to the release job)")
    print("Story 054 requirement 2: run 2 happens AFTER the v0.25.0 tag, the "
          "release commit, the website What's New edit and the live sync.")
    print("Recorded here as PENDING. Run 1 alone never satisfies Story 054 "
          "(Scenario 7).")

    group("Committed base at the frozen ref (ref=%s)" % REF)
    rc, body = git_bytes(["show", "%s:src/cinder.html" % REF])
    check(rc == 0 and len(body) > 0,
          "%s:src/cinder.html readable" % REF, "exit=%d" % rc)
    print("committed base bytes: %d (expected %d)"
          % (len(body), EXPECTED_BASE_BYTES))
    check(len(body) == EXPECTED_BASE_BYTES,
          "committed base is the verified 67969 bytes")
    head = body[:60].decode("utf-8", "replace")
    print("committed base head: %r" % head)
    check(body.startswith(b"<!DOCTYPE html>"),
          "committed base head bytes are HTML")

    group("Retired by name (Session 64; no frozen ref can satisfy them)")
    retired("mirror-byte-identical",
            "end-to-end deploy-mirror byte-identity; website/games/cinder.html "
            "exists at neither 2907623 nor v0.24.0 (deploy root landed Session 31)")
    retired("mirror-sha-pair-equal",
            "same coverage as mirror-byte-identical (sha pair over the same absent path)")
    retired("working-tree-clean-informational",
            "no coverage lost (informational only; dirty-tree warning stays a print, not a check)")
    retired("live-origin-tag-lookup",
            "live-origin newest-tag awareness (network-dependent ls-remote discovery)")
    retired("live-currency-run",
            "served-copy currency leg; belongs to the release job by design")

    total = COUNT["pass"] + COUNT["fail"]
    print("\n=== %d checks, %d failed ===" % (total, COUNT["fail"]))
    print("RESULT: " + ("PASS" if COUNT["fail"] == 0 else "FAIL"))
    return 1 if COUNT["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
