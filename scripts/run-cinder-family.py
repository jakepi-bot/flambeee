#!/usr/bin/env python3
"""Run the Cinder proof family against the live tree (Story 127, Session 55).

Discovers the family per the design-contract rule (no hardcoded member list):
a file is in the family iff it ends in .py, it lives under archive/src-games/ or
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


USAGE = ("usage: run-cinder-family.py [--repo DIR] [--target FILE] [--port-base N] "
         "[--timeout S] [--include SUB] [--exclude SUB] [--python PATH] [--baseline PATH] [--no-baseline-check]")


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
    src_dir = os.path.join(repo, "archive", "src-games")
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


# Session 62 (Story 139) instrument contract. This block documents the
# interpreter truth, pre-flight refusal, three-way tally, and baseline
# enforcement added below the anchor line; the docstring above (lines 1-28)
# and the `def discover()` line number are frozen by the design contract.
SESSION62_CONTRACT = (
    "interpreter: explicit --python PATH, else <repo>/.venv/bin/python, "
    "else <repo>/../.venv/bin/python; never sys.executable by default; "
    "nonexistent --python is misuse (exit 3). "
    "pre-flight: every DECLARED_DEPS name must import under the invoking "
    "interpreter and under the effective child, else full ENV-SKIP refusal "
    "(exit 2, fail=0, nothing executed). "
    "tally: total == pass + fail + skip == FAMILY_SIZE == 19, else "
    "INVARIANT-BROKEN (exit 2). exits first-match-wins: "
    "misuse ? 3 : fail_closed ? 2 : (F >= 1 ? 1 : (S >= 1 ? 2 : 0)). "
    "baseline: default docs/test-plans/cinder-family-baseline.json; "
    "S5 shape failures exit 2 before any execution; drift marks the row "
    "FAIL with reason=baseline-drift(expected=<X> got=<Y>)."
)

FAMILY_SIZE = 19                # S9 tripwire: the family has exactly 19 members
DECLARED_DEPS = ("playwright",)  # S6 pre-flight deps (stdlib probe only)
BASELINE_REL = os.path.join("docs", "test-plans", "cinder-family-baseline.json")
BASELINE_CATEGORIES = ("stub", "stale-pin", "deep-logic", "env")


def extract_session62_flags(argv):
    """Split Session 62 flags out of argv; the rest goes to parse_argv."""
    python_opt = None
    baseline_opt = None
    no_baseline_check = False
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--no-baseline-check":
            no_baseline_check = True
            i += 1
        elif a in ("--python", "--baseline"):
            if i + 1 >= len(argv):
                return None, fail_usage("flag %s needs a value" % a)
            v = argv[i + 1]
            if a == "--python":
                if not os.path.exists(v):
                    return None, fail_usage("bad --python: %s" % v)
                python_opt = v
            else:
                if not os.path.exists(v):
                    return None, fail_usage("bad --baseline: %s" % v)
                baseline_opt = v
            i += 2
        else:
            rest.append(a)
            i += 1
    return ({"python": python_opt, "baseline": baseline_opt,
             "no_baseline_check": no_baseline_check, "rest": rest}, 0)


def resolve_child_python(repo, explicit):
    """Effective child interpreter: flag, else repo .venv, else sibling .venv."""
    if explicit:
        return os.path.abspath(explicit)
    first = os.path.join(repo, ".venv", "bin", "python")
    if os.path.exists(first):
        return first
    return os.path.join(os.path.dirname(os.path.abspath(repo)),
                        ".venv", "bin", "python")


def dep_importable(python_bin, dep):
    """Stdlib-only probe: can <python_bin> import <dep>? Missing binary is False."""
    try:
        r = subprocess.run([python_bin, "-c", "import %s" % dep],
                           capture_output=True, timeout=60)
        return r.returncode == 0
    except Exception:
        return False


def load_baseline_file(path):
    """Load and schema-check the baseline. Returns (data, None) or (None, token)."""
    import json
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as e:
        return None, "BASELINE-MALFORMED (%s: %s)" % (path, e)
    if not isinstance(data, dict):
        return None, "BASELINE-MALFORMED (top level is not an object)"
    if data.get("family_size") != FAMILY_SIZE:
        return None, "BASELINE-MALFORMED (family_size != %d)" % FAMILY_SIZE
    if not isinstance(data.get("generated"), str) or not data.get("generated"):
        return None, "BASELINE-MALFORMED (bad generated date)"
    rows = data.get("rows")
    if not isinstance(rows, list):
        return None, "BASELINE-MALFORMED (rows is not a list)"
    seen = set()
    for r in rows:
        if not isinstance(r, dict):
            return None, "BASELINE-MALFORMED (row is not an object)"
        script = r.get("script")
        expected = r.get("expected")
        category = r.get("category")
        issue = r.get("issue")
        note = r.get("note")
        if not isinstance(script, str) or not script:
            return None, "BASELINE-MALFORMED (bad script value)"
        if script in seen:
            return None, "BASELINE-MALFORMED (duplicate script: %s)" % script
        seen.add(script)
        if expected not in ("pass", "fail"):
            return None, "BASELINE-MALFORMED (bad expected for %s)" % script
        if category not in BASELINE_CATEGORIES:
            return None, "BASELINE-MALFORMED (bad category for %s)" % script
        if expected == "fail":
            if not isinstance(issue, int) or isinstance(issue, bool):
                return None, "BASELINE-MALFORMED (fail row with null/bad issue: %s)" % script
        elif issue is not None:
            return None, "BASELINE-MALFORMED (pass row with non-null issue: %s)" % script
        if not isinstance(note, str) or not note or "\n" in note:
            return None, "BASELINE-MALFORMED (bad note for %s)" % script
    return data, None


def baseline_cross_check(baseline, rels):
    """Fail-closed discovery-vs-baseline identity. Returns a list of tokens.

    missing = discovered rels minus baseline scripts; orphan = baseline
    scripts minus discovered rels. MISSING prints first when both are set.
    Count mismatch is exclusively this stage's work (Story 152).
    """
    want = {}
    for r in baseline["rows"]:
        want[r["script"]] = r["expected"]
    errs = []
    missing = sorted(set(rels) - set(want))
    if missing:
        errs.append("BASELINE-MISSING-ROW %s" % " ".join(missing))
    orphan = sorted(set(want) - set(rels))
    if orphan:
        errs.append("BASELINE-ORPHAN-ROW %s" % " ".join(orphan))
    return errs


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
    s62, rc = extract_session62_flags(argv)
    if s62 is None:
        return rc
    opts, rc = parse_argv(s62["rest"])
    if opts is None:
        return rc
    repo = os.path.abspath(opts["repo"]) if opts["repo"] else repo_root_of_runner()
    if not os.path.exists(os.path.join(repo, ".git")):
        print("run-cinder-family: --repo is not a repo: %s" % repo)
        print(USAGE)
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

    child_python = resolve_child_python(repo, s62["python"])
    invoker_python = sys.executable

    digest = sha256_of(target)
    print("run-cinder-family")
    print("repo    : %s" % repo)
    print("target  : %s" % target)
    print("sha256  : %s" % digest)
    print("invoker : %s" % invoker_python)
    print("python  : %s" % child_python)
    if filtered:
        print("FILTERED RUN (include=%r exclude=%r): not the full family; "
              "never cite as full-family green"
              % (opts["include"], opts["exclude"]))
        print("FILTERED-NO-BASELINE-CERTIFY")
    print("discovery: %d script(s)" % len(family))
    for p in family:
        print("  - %s" % os.path.relpath(p, repo))
    if not family:
        print("run-cinder-family: zero scripts discovered")
        return 2

    rels = [os.path.relpath(p, repo) for p in family]

    # S5 baseline shape: fail-closed, before any execution.
    baseline = None
    baseline_line = None
    enforce = (not filtered) and (not s62["no_baseline_check"])
    if filtered:
        baseline_line = "baseline: STALE FILTERED-NO-BASELINE-CERTIFY"
    elif s62["no_baseline_check"]:
        baseline_line = "baseline: OFF (triage only, not evidence)"
    else:
        bpath = s62["baseline"] or os.path.join(repo, BASELINE_REL)
        baseline, berr = load_baseline_file(bpath)
        if berr is not None:
            print("run-cinder-family: %s" % berr)
            return 2
        xerrs = baseline_cross_check(baseline, rels)
        for xerr in xerrs:
            print("run-cinder-family: %s" % xerr)
        if xerrs:
            return 2

    # S6 pre-flight: every declared dep importable under invoker and child.
    # Refusal prints every discovered row ENV-SKIP, fail=0, exit 2, nothing executes.
    team_venv_python = os.path.join(os.path.dirname(os.path.abspath(repo)),
                                    ".venv", "bin", "python")
    for dep in DECLARED_DEPS:
        if not dep_importable(invoker_python, dep):
            for rel in rels:
                print("ENV-SKIP %s  reason=env-skip: %s missing under invoker %s"
                      % (rel, dep, invoker_python))
            print("family: 0/%d scripts passed" % FAMILY_SIZE)
            print("tally: pass=0 fail=0 skip=%d total=%d (assert %d==%d)"
                  % (len(rels), len(rels), len(rels), FAMILY_SIZE))
            print("baseline: STALE pre-flight-refusal (no comparison performed)")
            print("remediation: invoke run-cinder-family.py with %s "
                  "(the playwright-bearing interpreter)" % team_venv_python)
            return 2
        if not dep_importable(child_python, dep):
            for rel in rels:
                print("ENV-SKIP %s  reason=env-skip: %s missing under child %s"
                      % (rel, dep, child_python))
            print("family: 0/%d scripts passed" % FAMILY_SIZE)
            print("tally: pass=0 fail=0 skip=%d total=%d (assert %d==%d)"
                  % (len(rels), len(rels), len(rels), FAMILY_SIZE))
            print("baseline: STALE pre-flight-refusal (no comparison performed)")
            print("remediation: rerun with --python %s" % team_venv_python)
            return 2

    try:
        qa_art_dir, qa_notes = build_qa_art_dir(repo, target)
    except Exception as e:
        print("run-cinder-family: qa setup failed: %s" % e)
        return 2
    for n in qa_notes:
        print("qa setup: %s" % n)

    passed = 0
    failed = []
    actual = {}
    for i, script in enumerate(family):
        port = opts["port_base"] + i * PORT_STRIDE
        if not port_free(port):
            port += 1000
            if not port_free(port):
                print("FAIL %s  reason=port (base and retry in use)"
                      % os.path.relpath(script, repo))
                failed.append((script, "port"))
                actual[os.path.relpath(script, repo)] = "fail"
                continue
        env = dict(os.environ)
        env["REPO"] = repo
        env["QA_ART_DIR"] = qa_art_dir
        env["QA_PORT"] = str(port)
        env["PORT"] = str(port)
        for key in FAMILY_ENV_KEYS:
            env[key] = target
        code, out = run_one(child_python, script, target, env, opts["timeout"])
        rel = os.path.relpath(script, repo)
        if code == 0:
            passed += 1
            print("PASS %s" % rel)
            actual[rel] = "pass"
        else:
            reason = ("exit=%s" % code) if isinstance(code, int) else code
            print("FAIL %s  reason=%s" % (rel, reason))
            lines = [ln for ln in out.splitlines() if ln.strip()][:FAIL_LINES]
            for ln in lines:
                print("    | %s" % ln[:300])
            failed.append((script, reason))
            actual[rel] = "fail"

    # S9 tally: drift compare, then the in-process invariant, then the verdict.
    drifted = []
    if enforce and baseline is not None:
        exp = dict((r["script"], r["expected"]) for r in baseline["rows"])
        drifted = sorted(rel for rel in rels if actual.get(rel) != exp.get(rel))
        if drifted:
            drift_map = {}
            for rel in drifted:
                drift_map[rel] = ("baseline-drift(expected=%s got=%s)"
                                  % (exp[rel], actual.get(rel)))
                print("FAIL %s  reason=%s" % (rel, drift_map[rel]))
            rebuilt = []
            seen_fail = set()
            for script, reason in failed:
                rel = os.path.relpath(script, repo)
                seen_fail.add(rel)
                rebuilt.append((script, drift_map.get(rel, reason)))
            for rel in drifted:
                if rel not in seen_fail:
                    sp = [p for p in family if os.path.relpath(p, repo) == rel][0]
                    rebuilt.append((sp, drift_map[rel]))
            failed = sorted(rebuilt, key=lambda t: os.path.relpath(t[0], repo))
    nfail = len(failed)
    npass = passed - sum(1 for rel in drifted if actual.get(rel) == "pass")
    nskip = 0
    total = len(family)
    if npass + nfail + nskip != total or ((not filtered) and total != FAMILY_SIZE):
        print("run-cinder-family: INVARIANT-BROKEN "
              "(pass=%d fail=%d skip=%d total=%d family=%d)"
              % (npass, nfail, nskip, total, FAMILY_SIZE))
        return 2

    if filtered:
        print("family (filtered): %d/%d scripts passed" % (npass, total))
    else:
        print("family: %d/%d scripts passed" % (npass, total))
    print("tally: pass=%d fail=%d skip=%d total=%d (assert %d==%d)"
          % (npass, nfail, nskip, total, total, FAMILY_SIZE))
    if baseline_line is not None:
        print(baseline_line)
    elif drifted:
        print("baseline: MISMATCH %d row(s)" % len(drifted))
    else:
        print("baseline: MATCH")
    if failed:
        print("failed:")
        for script, reason in failed:
            print("  - %s (%s)" % (os.path.relpath(script, repo), reason))
    if nfail >= 1:
        return 1
    if nskip >= 1:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
