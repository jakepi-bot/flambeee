#!/usr/bin/env python3
"""Generated src consumer manifest builder (Story 131, Session 58).

Stages: SCAN (walk the fixed roots, record every src/ or kai-story hit with
repo-relative path and 1-based line number) -> CLASSIFY (exactly one kind per
row: runnable, historical, needs-a-decision) -> EMIT (consumers sorted by path
then line; byte-identical JSON plus Markdown on repeat runs).

Scan roots (fixed): repo-root *.py (covers scout-qa-session*.py), src/,
docs/test-plans/, dev/, README.md, docs/roadmap.md,
scripts/run-cinder-family.py. Scanned extensions under directories are
.py, .js and .md: the game HTML files under src/ are the referents, and their
internal self-referential comments are not consumer pointers, so .html is out
of scan by rule. The generator itself (dev/src-consumer-manifest.py) and its
two artifacts are excluded from the scan by rule: they are the observer, not
consumers, and their src/ strings are manifest vocabulary; scanning them
would make each run a function of the previous run's output. Two synthetic anchor rows are added by rule, never by hand:
the scripts/run-cinder-family.py discover() definition (the family-definition
change, no src/ literal in the code) and one file-level row for each of the
six #232 gate scripts that has no live-default row, so every one of the six
appears for a decision. counts partition distinct consumer paths by
highest-action kind (needs-a-decision, then runnable, then historical).

Row text is the matched line stripped, capped at 300 chars, with absolute
path prefixes redacted to [abs] and calendar dates to [date] so both artifacts
stay free of absolute paths and timestamps. Exit codes: 0 written, 1 a scan
root is missing or unreadable or the runnable floor (< 14 paths) is missed
(names the cause, writes nothing), 2 misuse.
"""

import json
import os
import re
import subprocess
import sys

GENERATED_BY = "dev/src-consumer-manifest.py"
MAX_TEXT = 300
RUNNABLE_FLOOR = 14

# Immutable git-show pins: tag blobs, sha pins, branch pins, named base refs.
HIST_RE = re.compile(
    r"v0\.\d+\.\d+:"
    r"|[0-9a-f]{7,40}:"
    r"|main:src"
    r"|origin/main:src"
    r"|feature/[\w.\-]+:src"
    r"|BASE_REF"
    r"|BASELINE_REF"
    r"|base_ref"
    r"|CONTROL_PIN"
    r"|V24\b"
    r"|BASE_REF-family"
    r"|tag blob"
    r"|git show v"
)

ABS_RE = re.compile(r"/home/\S*|/tmp/\S*")
DATE_RE = re.compile(r"\b20\d\d-\d\d(?:-\d\d)?\b")

# The six #232 gate-failure scripts. Each must appear as needs-a-decision.
GATE_SIX = (
    "docs/test-plans/session22-story040-qa.py",
    "docs/test-plans/session26-story050-qa.py",
    "docs/test-plans/session26-story051-qa.py",
    "docs/test-plans/session27-story053-qa.py",
    "docs/test-plans/session27-story054-qa.py",
    "docs/test-plans/session27-story055-qa.py",
)

# Anchor search strings for the file-level synthetic rows (first match wins).
GATE_ANCHOR = {
    "docs/test-plans/session22-story040-qa.py": ("QA_ART_DIR",),
    "docs/test-plans/session26-story050-qa.py": (
        "(default: website/games/cinder.html",
        "CINDER_PATH",
    ),
    "docs/test-plans/session27-story053-qa.py": (
        "(default: website/games/cinder.html",
        "CANDIDATE",
    ),
    "docs/test-plans/session27-story055-qa.py": (
        "RECORD  path",
        "RECORD",
    ),
}

GATE_SYNTHETIC_REASON = {
    "docs/test-plans/session22-story040-qa.py": (
        "Family member with no literal src/ pointer; exercises the Story 040 "
        "artifact through the QA_ART_DIR live default (website/games tree); "
        "archive step confirms no retarget is needed; owner: archive PR "
        "(Scout confirm)."
    ),
    "docs/test-plans/session26-story050-qa.py": (
        "Frozen-function extraction pins the v0.23.0 tag blob (historical "
        "rows) while CINDER_PATH defaults to the live website/games tree; "
        "archive step confirms the live default needs no retarget and "
        "accepts the tag pin; owner: archive PR (Scout confirm)."
    ),
    "docs/test-plans/session27-story053-qa.py": (
        "Real-browser harness pins the v0.24.0 tag blob (historical row) "
        "while CANDIDATE defaults to the live website/games tree; archive "
        "step confirms the live default needs no retarget and accepts the "
        "tag pin; owner: archive PR (Scout confirm)."
    ),
    "docs/test-plans/session27-story055-qa.py": (
        "Tag-blob-only harness by design: every src/ read resolves against "
        "the v0.24.0 tag blob (historical rows), never the working tree; "
        "archive step accepts the pin; owner: archive PR (Scout confirm)."
    ),
}

# Per-file reasons for live-default needs-a-decision rows in test-plan .py.
QA_PY_REASON = {
    "session26-story050-qa.py": (
        "Live QA harness (node sandbox plus Chromium); BASE_REF default "
        "v0.23.0 tag pin accepted, CINDER_PATH default is the live "
        "website/games tree; archive step confirms no src/ retarget is "
        "needed; owner: archive PR (Scout confirm)."
    ),
    "session26-story051-qa.py": (
        "Docstring cites the live proof src/kai-story051-away-window-proof.py; "
        "the proof moves with the archive and the runner retarget covers it; "
        "archive step updates the citation; owner: archive PR."
    ),
    "session27-story053-qa.py": (
        "Real-browser harness with CANDIDATE defaulting to the live "
        "website/games tree; archive step confirms no src/ retarget is "
        "needed; owner: archive PR (Scout confirm)."
    ),
    "session27-story054-qa.py": (
        "REF default main: git show REF:src/cinder.html plus cmp/sha256 "
        "against the live deploy mirror; archive step pins REF to the "
        "archive tag or accepts the mirror comparison as stale; owner: "
        "archive PR."
    ),
    "session27-story055-qa.py": (
        "Tag-blob-only harness by design; archive step accepts the v0.24.0 "
        "pin; owner: archive PR (Scout confirm)."
    ),
}

FAMILY_REASON = (
    "Family definition: discover() scans src/ plus docs/test-plans/ plus "
    "scout-qa-session*.py for the 19-member Cinder family, 11 of the 19 under "
    "src/; archiving src/ without the rewrite drops discovery 19 to 8 "
    "(19 - 11 = 8) with no error and no exit-code change (exit 0 either way), "
    "so M-4 (#216) would prove 11 fewer scripts; disposition: same-PR "
    "rewrite of src_dir to archive/src-games plus runner docstring line 5 "
    "src/ to archive/src-games/; owner: archive PR."
)

BEFORE_SNIPPET = (
    "# before (lines 115-117 at f029493):\n"
    'src_dir = os.path.join(repo, "src")\n'
    'plans_dir = os.path.join(repo, "docs", "test-plans")\n'
    "scan_dirs = [d for d in (src_dir, plans_dir) if os.path.isdir(d)]"
)
AFTER_SNIPPET = (
    "# after (archive step, same PR as the move):\n"
    'src_dir = os.path.join(repo, "archive", "src-games")\n'
    'plans_dir = os.path.join(repo, "docs", "test-plans")\n'
    "scan_dirs = [d for d in (src_dir, plans_dir) if os.path.isdir(d)]"
)


def fail_usage(msg):
    sys.stderr.write("usage: src-consumer-manifest.py [--repo DIR]\n")
    sys.stderr.write("error: %s\n" % msg)
    return 2


def parse_args(argv):
    opts = {"repo": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            sys.stdout.write(
                "usage: src-consumer-manifest.py [--repo DIR]\n"
                "Write dev/src-consumer-manifest.json and .md for the repo.\n"
            )
            sys.exit(0)
        elif a == "--repo":
            if i + 1 >= len(argv):
                return None, fail_usage("--repo needs a directory")
            opts["repo"] = argv[i + 1]
            i += 2
        else:
            return None, fail_usage("unknown flag: %s" % a)
    return opts, 0


def repo_root_of_script():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def sanitize(text):
    text = text.strip()
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT]
    text = ABS_RE.sub("[abs]", text)
    text = DATE_RE.sub("[date]", text)
    return text


def read_lines(repo, rel):
    full = os.path.join(repo, rel)
    with open(full, "rb") as fh:
        blob = fh.read()
    if b"\x00" in blob:
        return None
    return blob.decode("utf-8", errors="replace").splitlines()


def scan_roots(repo):
    required_dirs = ("src", "docs/test-plans", "dev")
    required_files = (
        "README.md",
        "docs/roadmap.md",
        "scripts/run-cinder-family.py",
    )
    if not os.path.isdir(repo):
        return None, "scan root missing: repo dir %s" % repo
    for rel in required_dirs:
        full = os.path.join(repo, rel)
        if not os.path.isdir(full):
            return None, "scan root missing: %s" % rel
        if not os.access(full, os.R_OK | os.X_OK):
            return None, "scan root unreadable: %s" % rel
    for rel in required_files:
        full = os.path.join(repo, rel)
        if not os.path.isfile(full):
            return None, "scan root missing: %s" % rel
        if not os.access(full, os.R_OK):
            return None, "scan root unreadable: %s" % rel
    return True, ""


def iter_scan_files(repo):
    excluded = {
        "dev/src-consumer-manifest.py",
        "dev/src-consumer-manifest.json",
        "dev/src-consumer-manifest.md",
    }
    files = []
    for name in sorted(os.listdir(repo)):
        if name.endswith(".py") and os.path.isfile(os.path.join(repo, name)):
            files.append(name)
    for root_rel in ("src", "docs/test-plans", "dev"):
        base = os.path.join(repo, root_rel)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for name in sorted(filenames):
                if name.endswith((".py", ".js", ".md")):
                    full = os.path.join(dirpath, name)
                    rel = os.path.relpath(full, repo).replace(os.sep, "/")
                    if rel not in excluded:
                        files.append(rel)
    for rel in ("README.md", "docs/roadmap.md", "scripts/run-cinder-family.py"):
        if rel not in files:
            files.append(rel)
    return files


def file_has_live_src_read(lines):
    for line in lines:
        if "readFileSync" in line and "src" in line:
            return True
        if "path.join" in line and '"src"' in line:
            return True
        if "extracts the real" in line and "src/" in line:
            return True
    return False


def historical_reason(pin):
    return (
        "Immutable git-show pin (%s); read-only base comparison with no "
        "working-tree execution; no archive-step edit needed." % pin
    )


def md_reason():
    return (
        "Prose record reference to src/; not executed, so the archive "
        "changes nothing it points at; no archive-step edit needed."
    )


def md_stale_reason():
    return (
        "Prose record with a stale absolute root, kept as history; accepted "
        "as stale, not executed; no archive-step edit needed."
    )


def classify(path, lineno, text, live_src_read):
    base = path.rsplit("/", 1)[-1]
    if path == "scripts/run-cinder-family.py" and lineno == 5:
        return (
            "needs-a-decision",
            "Docstring states the live src/ family rule executed today; "
            "refresh it alongside the discover() rewrite in the same PR; "
            "owner: archive PR.",
        )
    m = HIST_RE.search(text)
    if m:
        return "historical", historical_reason(m.group(0))
    if path == "README.md":
        return (
            "needs-a-decision",
            "Tree diagram names src/ (code, managed by Kai and Riven); "
            "archive step updates the diagram to the moved path; owner: "
            "archive PR.",
        )
    if path.endswith(".md"):
        if "[abs]" in text or "[date]" in text:
            return "historical", md_stale_reason()
        return "historical", md_reason()
    if path in ("dev/gen-words.py", "dev/capture-game-shots.py"):
        return (
            "needs-a-decision",
            "Live %s path executed today against src/; archive step retargets "
            "the path to the moved tree or moves the consumer with it; "
            "owner: archive PR."
            % ("write" if base == "gen-words.py" else "screenshot-subject"),
        )
    if path == "generate-hard-words.py":
        if "SRCJS" in text:
            return (
                "needs-a-decision",
                "Stale absolute SRCJS root is a pre-existing break (out of "
                "scope for this manifest); archive step retargets it or "
                "accepts it as stale; owner: archive PR.",
            )
        return (
            "needs-a-decision",
            "Docstring states the src/wordfire-words.js read behind the "
            "stale SRCJS root; archive step retargets the read with the "
            "SRCJS fix or accepts both rows as stale; owner: archive PR.",
        )
    if path.startswith("docs/test-plans/") and path.endswith(".py"):
        return "needs-a-decision", QA_PY_REASON.get(
            base,
            "Live QA harness with a working-tree default; archive step "
            "retargets any src/ read or accepts it as stale; owner: "
            "archive PR (Scout confirm).",
        )
    if path.startswith("docs/test-plans/") and path.endswith(".js"):
        if live_src_read:
            return (
                "runnable",
                "Executes against the live tree today, reading src/ bytes at "
                "run time; archive step retargets the relative src/ reads to "
                "the moved tree; owner: archive PR.",
            )
        return (
            "needs-a-decision",
            "Pure-JS mirror of src/ math with no live src/ read; archive "
            "step re-verifies the mirror against the moved file or accepts "
            "it as stale; owner: archive PR.",
        )
    if path.startswith("src/") and path.endswith(".py"):
        return (
            "runnable",
            "Proof script executed against the live tree today by the family "
            "runner; moves with the archive and the runner retarget covers "
            "it; owner: archive PR.",
        )
    if path == "scripts/run-cinder-family.py":
        return (
            "needs-a-decision",
            "Live family runner; src/ references here are covered by the "
            "discover() definition row; owner: archive PR.",
        )
    if path == "scout-qa-session24.py":
        return (
            "historical",
            historical_reason("v0.21.0:"),
        )
    return (
        "needs-a-decision",
        "Live working-tree reference; archive step retargets it or "
        "explicitly accepts it as stale; owner: archive PR.",
    )


def find_anchor(lines, keys):
    for key in keys:
        for idx, line in enumerate(lines):
            if key in line:
                return idx + 1, sanitize(line)
    return 1, sanitize(lines[0]) if lines else ""


def measure_family(repo):
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
            rel = os.path.relpath(path, repo).replace(os.sep, "/")
            found.append(rel)
    found = sorted(found)
    under = [p for p in found if p == "src" or p.startswith("src/")]
    return found, under


def md_escape(cell):
    return cell.replace("|", "\\|").replace("\n", " ")


def build_markdown(base_commit, counts, consumers):
    lines = []
    lines.append("# src consumer manifest (Story 131, Session 58)")
    lines.append("")
    lines.append("Generator: dev/src-consumer-manifest.py.")
    lines.append("Base commit: %s." % base_commit)
    lines.append(
        "Counts: runnable %d paths, historical %d paths, needs-a-decision "
        "%d paths; test-plan files %d; family %d total, %d under src/."
        % (
            counts["runnable"],
            counts["historical"],
            counts["needs_decision"],
            counts["test_plan_files"],
            counts["family_total"],
            counts["family_under_src"],
        )
    )
    lines.append("")
    lines.append("Scan roots: repo-root *.py, src/, docs/test-plans/, dev/, ")
    lines.append("README.md, docs/roadmap.md, scripts/run-cinder-family.py. ")
    lines.append("Scanned extensions under directories are .py, .js and .md; ")
    lines.append("the game HTML files under src/ are the referents, and ")
    lines.append("their internal self-referential comments are not consumer ")
    lines.append("pointers, so .html is out of scan by rule. The generator ")
    lines.append("itself and its two artifacts are excluded from the scan by ")
    lines.append("rule: they are the observer, not consumers, so each run is ")
    lines.append("a pure function of the rest of the tree. Row text is the ")
    lines.append("matched line stripped and capped at 300 chars, with ")
    lines.append("absolute path prefixes redacted to [abs] and calendar dates ")
    lines.append("to [date] so both artifacts stay leak-free. Counts ")
    lines.append("partition distinct consumer paths by highest-action kind ")
    lines.append("(needs-a-decision, then runnable, then historical). Two ")
    lines.append("synthetic anchor rows exist by rule, never by hand: the ")
    lines.append("discover() definition row below, and one file-level row ")
    lines.append("for each of the six #232 gate scripts that has no ")
    lines.append("live-default row, so all six appear for a decision.")
    lines.append("")
    lines.append("## Family-definition change (scripts/run-cinder-family.py)")
    lines.append("")
    lines.append("```")
    lines.append(BEFORE_SNIPPET)
    lines.append("```")
    lines.append("")
    lines.append("```")
    lines.append(AFTER_SNIPPET)
    lines.append("```")
    lines.append("")
    lines.append("plus the runner docstring line 5 updated from src/ to ")
    lines.append("archive/src-games/. Arithmetic: 19 members today, 11 of ")
    lines.append("the 19 under src/, 19 - 11 = 8, so removing src/ without ")
    lines.append("rewriting discover() silently shrinks discovery 19 to 8 ")
    lines.append("with no error and no exit-code change (exit 0 either way), ")
    lines.append("and M-4 (#216, the rule that cites the full-family run) ")
    lines.append("quietly starts proving 11 fewer scripts. Acceptance on the ")
    lines.append("archive step (not tonight): discovery prints 19 at base ")
    lines.append("and 19 at head, same set.")
    lines.append("")
    lines.append("## Consumers (%d rows)" % len(consumers))
    lines.append("")
    lines.append("| path | line | kind | reason | text |")
    lines.append("| --- | --- | --- | --- | --- |")
    for c in consumers:
        lines.append(
            "| %s | %d | %s | %s | %s |"
            % (
                md_escape(c["path"]),
                c["line"],
                c["kind"],
                md_escape(c["reason"]),
                md_escape(c["text"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def main(argv):
    opts, code = parse_args(argv)
    if opts is None:
        return code
    repo = os.path.abspath(opts["repo"]) if opts["repo"] else repo_root_of_script()
    if not os.path.isdir(repo) or not os.path.isdir(os.path.join(repo, ".git")):
        sys.stderr.write("error: --repo not a repo: %s\n" % (opts["repo"] or repo))
        return 2

    ok, msg = scan_roots(repo)
    if not ok:
        sys.stderr.write("error: %s\n" % msg)
        return 1

    try:
        base_commit = subprocess.run(
            ["git", "-C", repo, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
    except OSError as exc:
        sys.stderr.write("error: git rev-parse failed: %s\n" % exc)
        return 1
    if not re.fullmatch(r"[0-9a-f]{40}", base_commit or ""):
        sys.stderr.write("error: git rev-parse HEAD did not return full hex\n")
        return 1

    files = iter_scan_files(repo)
    contents = {}
    for rel in files:
        try:
            lines = read_lines(repo, rel)
        except OSError:
            sys.stderr.write("error: scan file unreadable: %s\n" % rel)
            return 1
        if lines is None:
            continue
        contents[rel] = lines

    consumers = []
    for rel in files:
        lines = contents.get(rel)
        if lines is None:
            continue
        live_src_read = file_has_live_src_read(lines) if rel.endswith(".js") else False
        for idx, line in enumerate(lines):
            if "src/" not in line and "kai-story" not in line:
                continue
            text = sanitize(line)
            kind, reason = classify(rel, idx + 1, text, live_src_read)
            consumers.append(
                {
                    "path": rel,
                    "line": idx + 1,
                    "text": text,
                    "kind": kind,
                    "reason": reason,
                    "has_src": "src/" in line,
                }
            )

    by_path_kind = {}
    for c in consumers:
        by_path_kind.setdefault(c["path"], set()).add(c["kind"])

    # Synthetic family-definition row at the discover() definition.
    runner_lines = contents.get("scripts/run-cinder-family.py", [])
    discover_line = 0
    for idx, line in enumerate(runner_lines):
        if line.startswith("def discover("):
            discover_line = idx + 1
            break
    if discover_line == 0:
        sys.stderr.write("error: discover() definition not found\n")
        return 1
    consumers.append(
        {
            "path": "scripts/run-cinder-family.py",
            "line": discover_line,
            "text": sanitize(runner_lines[discover_line - 1]),
            "kind": "needs-a-decision",
            "reason": FAMILY_REASON,
            "has_src": False,
        }
    )
    by_path_kind.setdefault("scripts/run-cinder-family.py", set()).add(
        "needs-a-decision"
    )

    # One file-level row per gate script lacking a live-default row.
    for rel in GATE_SIX:
        kinds = by_path_kind.get(rel, set())
        if "needs-a-decision" in kinds:
            continue
        lines = contents.get(rel, [])
        if not lines:
            sys.stderr.write("error: gate script unreadable: %s\n" % rel)
            return 1
        anchor_line, anchor_text = find_anchor(lines, GATE_ANCHOR.get(rel, (rel,)))
        consumers.append(
            {
                "path": rel,
                "line": anchor_line,
                "text": anchor_text,
                "kind": "needs-a-decision",
                "reason": GATE_SYNTHETIC_REASON[rel],
                "has_src": False,
            }
        )
        by_path_kind.setdefault(rel, set()).add("needs-a-decision")

    consumers.sort(key=lambda c: (c["path"], c["line"]))

    for c in consumers:
        del c["has_src"]

    def primary(path):
        kinds = by_path_kind[path]
        if "needs-a-decision" in kinds:
            return "needs-a-decision"
        if "runnable" in kinds:
            return "runnable"
        return "historical"

    paths = sorted(by_path_kind)
    runnable_paths = sorted(p for p in paths if primary(p) == "runnable")
    historical_paths = sorted(p for p in paths if primary(p) == "historical")
    needs_paths = sorted(p for p in paths if primary(p) == "needs-a-decision")

    if len(runnable_paths) < RUNNABLE_FLOOR:
        sys.stderr.write(
            "error: runnable floor missed: %d paths, need %d\n"
            % (len(runnable_paths), RUNNABLE_FLOOR)
        )
        return 1

    test_plan_files = sorted(
        {
            c["path"]
            for c in consumers
            if c["path"].startswith("docs/test-plans/")
        }
    )
    # Count only files whose own lines mention src/ (kai-story-only rows do
    # not qualify, though no such file exists at HEAD).
    test_plan_files = [
        p
        for p in test_plan_files
        if any(
            True
            for c in consumers
            if c["path"] == p and "src/" in contents[p][c["line"] - 1]
        )
    ]

    family, family_under = measure_family(repo)

    counts = {
        "runnable": len(runnable_paths),
        "historical": len(historical_paths),
        "needs_decision": len(needs_paths),
        "test_plan_files": len(test_plan_files),
        "family_total": len(family),
        "family_under_src": len(family_under),
    }

    payload = {
        "base_commit": base_commit,
        "generated_by": GENERATED_BY,
        "counts": counts,
        "consumers": consumers,
    }
    json_text = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    md_text = build_markdown(base_commit, counts, consumers)

    for rel, text in (
        ("dev/src-consumer-manifest.json", json_text),
        ("dev/src-consumer-manifest.md", md_text),
    ):
        full = os.path.join(repo, rel)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
