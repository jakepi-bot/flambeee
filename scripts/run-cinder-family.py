#!/usr/bin/env python3
"""Run the Cinder proof family against the live tree (Story 127, Session 55).

Discovers the family per the design-contract rule (no hardcoded member list):
a file is in the family iff it ends in .py, it lives under src/ or
docs/test-plans/ or matches scout-qa-session*.py at the repo root, and its
bytes contain a case-insensitive match for "cinder".

Each discovered script runs serially with the target file passed as argv[1]
plus the family env overrides (CINDER_SRC, CINDER_PATH, CANDIDATE, QA_ART_DIR,
REPO, QA_PORT, PORT), a per-script timeout, and an allocated port. One failure
never hides the rest: every script still runs.

Exit codes (contract 2.3):
  0 = all discovered scripts passed.
  1 = at least one script failed, timed out, or was unrunnable.
  2 = runner-level error (zero scripts discovered, target file missing).
  3 = misuse (unknown flag, --repo is not a repo, bad knob value).

Usage:
  python3 scripts/run-cinder-family.py [--repo DIR] [--target FILE]
      [--port-base N] [--timeout S] [--include SUB] [--exclude SUB]

Filtered reruns (--include/--exclude) are labeled FILTERED and never reported
as the full-family run; the M-4 record cites an unfiltered run.

Stdlib only.
"""
import hashlib
import os
import socket
import subprocess
import sys
import tempfile

TIMEOUT = 300          # per-script timeout, seconds (contract table: 120..900)
PORT_BASE = 8765       # base of the per-script port range (contract: 1024..60000)
PORT_STRIDE = 1        # script i gets PORT_BASE + i
FAIL_LINES = 30        # captured output lines per failure (contract: 10..100)
CONTROL_PIN = "77acd25:src/cinder.html"  # S5c byte-safety control, per the
# session22 docstring ("The main-build artifact (77acd25) is used as a
# byte-safety control"). Materialized to a runtime temp dir, never the tree.

FAMILY_ENV_KEYS = ("CINDER_SRC", "CINDER_PATH", "CANDIDATE")


USAGE = ("usage: run-cinder-family.py [--repo DIR] [--target FILE] "
         "[--port-base N] [--timeout S] [--include SUB] [--exclude SUB]")


def fail_usage(msg):
    print("run-cinder-family: %s" % msg)
    print(USAGE)
    return 3


def parse_argv(argv):
    opts = {
        "repo": None,
        "target": None,
        "port_base": PORT_BASE,
        "timeout": TIMEOUT,
        "include": [],
        "exclude": [],
    }
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__.strip())
            print(USAGE)
            return None, 0
        if a in ("--repo", "--target", "--port-base", "--timeout",
                 "--include", "--exclude"):
            if i + 1 >= len(argv):
                return None, fail_usage("flag %s needs a value" % a)
            v = argv[i + 1]
            if a == "--port-base":
                try:
                    v = int(v)
                except ValueError:
                    return None, fail_usage("--port-base must be an integer")
                if not 1024 <= v <= 60000:
                    return None, fail_usage("--port-base out of range 1024..60000")
                opts["port_base"] = v
            elif a == "--timeout":
                try:
                    v = int(v)
                except ValueError:
                    return None, fail_usage("--timeout must be an integer")
                if not 120 <= v <= 900:
                    return None, fail_usage("--timeout out of range 120..900")
                opts["timeout"] = v
            elif a == "--include":
                opts["include"].append(v)
            elif a == "--exclude":
                opts["exclude"].append(v)
            elif a == "--repo":
                opts["repo"] = v
            else:
                opts["target"] = v
            i += 2
        else:
            return None, fail_usage("unknown flag: %s" % a)
    return opts, 0


def repo_root_of_runner():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def discover(repo):
    found = []
    src_dir = os.path.join(repo, "src")
    plans_dir = os.path.join(repo, "docs", "test-plans")
    scan_dirs = [d for d in (src_dir, plans_dir) if os.path.isdir(d)]
    candidates = []
    for d in scan_dirs:
        for name in sorted(os.listdir(d)):
            if name.endswith(".py"):
                candidates.append(os.path.join(d, name))
    for name in sorted(os.listdir(repo)):
        if name.startswith("scout-qa-session") and name.endswith(".py"):
            candidates.append(os.path.join(repo, name))
    for path in candidates:
        try:
            with open(path, "rb") as fh:
                blob = fh.read()
        except OSError:
            continue
        if b"cinder" in blob.lower():
            found.append(path)
    return sorted(found)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def port_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def build_qa_art_dir(repo, target):
    """Runtime serve dir for session22: symlink to the target plus the pinned
    pre-040 control artifact (edge case 4: dead-worktree dependency rewritten
    to a temp dir created at run time). Returns (dir, notes)."""
    notes = []
    tmp = tempfile.mkdtemp(prefix="cinder-family-qa-")
    link = os.path.join(tmp, "cinder.html")
    try:
        os.symlink(os.path.abspath(target), link)
    except OSError as e:
        notes.append("symlink unavailable (%s); copied instead" % e)
        with open(os.path.abspath(target), "rb") as fh:
            body = fh.read()
        with open(link, "wb") as fh:
            fh.write(body)
    try:
        r = subprocess.run(["git", "-C", repo, "show", CONTROL_PIN],
                           capture_output=True, timeout=30)
        if r.returncode == 0 and r.stdout:
            with open(os.path.join(tmp, "cinder-main.html"), "wb") as fh:
                fh.write(r.stdout)
            notes.append("control cinder-main.html materialized from %s" % CONTROL_PIN)
        else:
            notes.append("control pin unreadable; S5c will report missing control")
    except Exception as e:
        notes.append("control materialization failed (%s)" % e)
    return tmp, notes


def run_one(python, script, target, env, timeout):
    try:
        r = subprocess.run([python, script, target],
                           capture_output=True, text=True, timeout=timeout,
                           cwd=env["REPO"], env=env)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        err = (e.stderr or "") if isinstance(e.stderr, str) else ""
        return "timeout", out + err
    except Exception as e:
        return "spawn", "runner could not start %s: %s" % (script, e)


def main(argv):
    opts, rc = parse_argv(argv)
    if opts is None:
        return rc
    repo = os.path.abspath(opts["repo"]) if opts["repo"] else repo_root_of_runner()
    if not os.path.exists(os.path.join(repo, ".git")):
        print("run-cinder-family: --repo is not a repo: %s" % repo)
        return 3
    target = opts["target"] or os.path.join(repo, "website", "games", "cinder.html")
    target = os.path.abspath(target)
    if not os.path.isfile(target):
        print("run-cinder-family: target file missing: %s" % target)
        return 2

    family = discover(repo)
    if opts["include"]:
        family = [p for p in family
                  if any(s in os.path.relpath(p, repo) for s in opts["include"])]
    if opts["exclude"]:
        family = [p for p in family
                  if not any(s in os.path.relpath(p, repo) for s in opts["exclude"])]
    filtered = bool(opts["include"] or opts["exclude"])

    digest = sha256_of(target)
    print("run-cinder-family")
    print("repo    : %s" % repo)
    print("target  : %s" % target)
    print("sha256  : %s" % digest)
    if filtered:
        print("FILTERED RUN (include=%r exclude=%r): not the full family; "
              "never cite as full-family green"
              % (opts["include"], opts["exclude"]))
    print("discovery: %d script(s)" % len(family))
    for p in family:
        print("  - %s" % os.path.relpath(p, repo))
    if not family:
        print("run-cinder-family: zero scripts discovered")
        return 2

    qa_art_dir, qa_notes = build_qa_art_dir(repo, target)
    for n in qa_notes:
        print("qa setup: %s" % n)

    python = sys.executable
    passed = 0
    failed = []
    for i, script in enumerate(family):
        port = opts["port_base"] + i * PORT_STRIDE
        if not port_free(port):
            port += 1000
            if not port_free(port):
                print("FAIL %s  reason=port (base and retry in use)"
                      % os.path.relpath(script, repo))
                failed.append((script, "port"))
                continue
        env = dict(os.environ)
        env["REPO"] = repo
        env["QA_ART_DIR"] = qa_art_dir
        env["QA_PORT"] = str(port)
        env["PORT"] = str(port)
        for key in FAMILY_ENV_KEYS:
            env[key] = target
        code, out = run_one(python, script, target, env, opts["timeout"])
        rel = os.path.relpath(script, repo)
        if code == 0:
            passed += 1
            print("PASS %s" % rel)
        else:
            reason = ("exit=%s" % code) if isinstance(code, int) else code
            print("FAIL %s  reason=%s" % (rel, reason))
            lines = [ln for ln in out.splitlines() if ln.strip()][:FAIL_LINES]
            for ln in lines:
                print("    | %s" % ln[:300])
            failed.append((script, reason))

    total = len(family)
    if filtered:
        print("family (filtered): %d/%d scripts passed" % (passed, total))
    else:
        print("family: %d/%d scripts passed" % (passed, total))
    if failed:
        print("failed:")
        for script, reason in failed:
            print("  - %s (%s)" % (os.path.relpath(script, repo), reason))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
