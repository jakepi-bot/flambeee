#!/usr/bin/env python3
"""Session 27 QA - Story 054 (Scout).

Website Currency and Deploy-Mirror Verification. Story 054 re-runs ONE existing
script twice and records ONE cmp/sha256 pair. This harness performs:

    Run 1   pre-release, heading expected v0.24.0
    Mirror  src/cinder.html vs the live deploy mirror at the ABSOLUTE path

Run 2 (post-release, heading v0.25.0) is NOT run here: it belongs to the
release job and only becomes meaningful after the v0.25.0 tag, the release
commit, the website What's New edit and the live sync.

The checker is NOT modified. Its blob is asserted against the shipped value
before anything else runs, so a tampered checker fails this harness instead of
silently passing it.

Usage:
    /home/jake/.openclaw/workspace/.venv/bin/python3 session27-story054-qa.py
Env:
    REPO  path to the flambeee repo
    REF   git ref holding the committed state under test (default main)

The mirror comparison reads `git show REF:src/cinder.html`, NOT the working
tree file. A dev's in-progress uncommitted edit is not the release state, and
comparing the mirror against a dirty worktree measures the dev's WIP rather
than the release. The worktree state is reported separately as information.
"""
import hashlib
import os
import re
import subprocess
import sys
import tempfile

REPO = os.environ.get("REPO", "/home/jake/.openclaw/workspace/flambeee")
REF = os.environ.get("REF", "main")
LIVE_INDEX = "/home/jake/.openclaw/workspace/share/Flambeee/index.html"
LIVE_GAME = "/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html"
REPO_CINDER = os.path.join(REPO, "src/cinder.html")
EXPECTED_BLOB = "9b1058b1a0401fe2025fd8cd9653297a51937842"

COUNT = {"pass": 0, "fail": 0}


def check(cond, name, detail=""):
    ok = bool(cond)
    COUNT["pass" if ok else "fail"] += 1
    line = ("PASS" if ok else "FAIL") + ": " + name
    if detail:
        line += "  | " + str(detail)
    print(line, flush=True)
    return ok


def group(name):
    print("\n--- %s ---" % name, flush=True)


def run(cmd):
    p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True,
                       text=True)
    return p.returncode, p.stdout + p.stderr


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=== Session 27 Story 054 QA (Scout) ===")
    print("repo: %s" % REPO)

    group("Scenario 8: checker unmodified (blob assertion)")
    rc, out = run("git rev-parse HEAD:scripts/verify-website-currency.sh")
    blob = out.strip()
    print("checker blob at HEAD: %s" % blob)
    print("expected blob       : %s" % EXPECTED_BLOB)
    check(blob == EXPECTED_BLOB,
          "scripts/verify-website-currency.sh blob is the shipped 9b1058b1...")
    rc, out = run("git diff --name-only main...HEAD -- scripts/")
    changed = [l for l in out.strip().splitlines() if l]
    print("scripts/ files changed vs main: %d %r" % (len(changed), changed))
    check(not changed, "no new or modified verification script added")

    group("Run 1: pre-release, heading expected v0.24.0")
    print("$ scripts/verify-website-currency.sh", flush=True)
    rc, out = run("scripts/verify-website-currency.sh")
    print(out, end="", flush=True)
    print("EXIT=%d" % rc)
    check(rc == 0, "Scenario 2: run 1 exits 0 on the entering state",
          "exit=%d" % rc)

    with open(LIVE_INDEX, encoding="utf-8") as fh:
        live = fh.read()
    m = re.search(r"<h3>(v[0-9][^<]*)</h3>", live)
    heading = m.group(1) if m else "<none>"
    rc, out = run("git ls-remote --tags origin")
    tags = [t.split("refs/tags/")[-1] for t in out.strip().splitlines()]
    tags = [t for t in tags if re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", t)]
    tags.sort(key=lambda s: [int(x) for x in s[1:].split(".")])
    latest = tags[-1] if tags else "<none>"
    print("origin latest tag: %s" % latest)
    print("live What's New heading: %s" % heading)
    check(heading.startswith("v0.24.0"),
          "Scenario 1: run 1 heading names v0.24.0", "heading=%s" % heading)

    group("Run 2: NOT RUN BY DESIGN (belongs to the release job)")
    print("Story 054 requirement 2: run 2 happens AFTER the v0.25.0 tag, the "
          "release commit, the website What's New edit and the live sync.")
    print("Recorded here as PENDING. Run 1 alone never satisfies Story 054 "
          "(Scenario 7).")

    group("Cinder deploy-mirror comparison at the ABSOLUTE path (ref=%s)" % REF)
    rc, out = run("git show %s:src/cinder.html" % REF)
    check(rc == 0 and out.strip() != "",
          "%s:src/cinder.html readable" % REF, "exit=%d" % rc)
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    tmp.write(out.encode("utf-8"))
    tmp.close()
    committed = tmp.name
    print("$ cmp <git show %s:src/cinder.html> %s" % (REF, LIVE_GAME))
    exists = os.path.isfile(LIVE_GAME)
    check(exists, "the mirror exists at the absolute path")
    if exists:
        with open(committed, "rb") as fh:
            a_bytes = fh.read()
        with open(LIVE_GAME, "rb") as fh:
            b_bytes = fh.read()
        same = a_bytes == b_bytes
        if not same:
            for i, (x, y) in enumerate(zip(a_bytes, b_bytes)):
                if x != y:
                    print("differ at byte %d" % (i + 1))
                    break
            else:
                print("differ at byte %d (length %d vs %d)"
                      % (min(len(a_bytes), len(b_bytes)) + 1,
                         len(a_bytes), len(b_bytes)))
        check(same, "Scenario 4: src/cinder.html and the live deploy mirror "
                    "are byte-identical")
        a, b = sha256(committed), sha256(LIVE_GAME)
        print("$ sha256sum <git show %s:src/cinder.html> %s" % (REF, LIVE_GAME))
        print("%s  %s:src/cinder.html" % (a, REF))
        print("%s  %s" % (b, LIVE_GAME))
        print("bytes: %d / %d" % (len(a_bytes), len(b_bytes)))
        check(a == b, "Scenario 4: both recorded sha256 values are equal")

        group("Informational: the WORKING TREE state (not the release state)")
        rc2, wt = run("git status --porcelain -- src/cinder.html")
        print("  git status --porcelain -- src/cinder.html: %r" % wt.strip())
        if wt.strip():
            print("  WARNING: src/cinder.html has uncommitted dev edits. The "
                  "mirror is NOT expected to match that; Story 054 req 3 runs "
                  "after Story 053 merges and the mirror is re-synced.")
            w = sha256(REPO_CINDER)
            print("  working-tree sha256: %s  (%d bytes)"
                  % (w, os.path.getsize(REPO_CINDER)))
            check(False,
                  "working tree is clean (informational; a dirty tree means "
                  "Story 053 has not merged yet)")
        else:
            print("  working tree is clean.")
            check(True, "working tree is clean")

    total = COUNT["pass"] + COUNT["fail"]
    print("\n=== %d checks, %d failed ===" % (total, COUNT["fail"]))
    print("RESULT: " + ("PASS" if COUNT["fail"] == 0 else "FAIL"))
    return 1 if COUNT["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())