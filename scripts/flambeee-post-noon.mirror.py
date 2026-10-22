#!/usr/bin/env python3
"""Flambeee social post publisher — noon release announcement.

Run by cron AFTER the 11am Caddy sync so flambeee.com serves the new
build before the announcement goes out. Posts only what the session
staged, verifies the post URI, then clears the staging file.

Staging: the Flambeee work session (release wave) writes the announcement
text to flambeee-team/state/pending-post.txt instead of posting live.
This script is the ONLY poster for release announcements.

Exit 0 = posted+verified (or nothing pending). Non-zero = failure.

Failure policy (Stories 082/083, Session 37): EVERY failure mode exits
non-zero AND appends a line to the alert artifact at
flambeee-team/state/noon-failure-alert.log (ISO timestamp, mode, exit
code) AND appends a fuller entry to the durable run log at
flambeee-team/state/noon-job.log. The success path is unchanged:
post plus verify plus archive to posted-posts.log plus clear pending,
exit 0, no alert line.

Version guard (Story 083): the staged text names its release version
(first vMAJOR.MINOR.PATCH token in the text). The guard resolves the
newest origin tag at run time via `git ls-remote --tags origin` (never
hardcoded) and refuses a buffer older than the newest tag: no post,
pending kept, non-zero exit routed through the loud-failure path.

Test overrides (env, all optional; never used by the scheduled run):
  FLAMBEEE_PENDING    pending-post.txt path
  FLAMBEEE_VENV       venv python path (missing-interpreter simulation)
  FLAMBEEE_BSKY       flambeee-bsky.py helper path
  FLAMBEEE_ENV_PATH   creds .env path (missing-creds simulation)
  FLAMBEEE_REPO       repo dir for tag resolution
  FLAMBEEE_NEWEST_TAG pin newest tag (e.g. v0.33.0), skips ls-remote
  FLAMBEEE_ALERT_LOG  alert artifact path
  FLAMBEEE_RUN_LOG    durable run-log path
  FLAMBEEE_DRY_RUN=1  guard-ALLOW stops before pre-flight and the real
                      post (guard decision only), exit 0
"""
import datetime as DT
import os
import re
import subprocess
import sys
from pathlib import Path

# Bluesky hard limit: 300 GRAPHEMES for post text. Enforced here so an
# over-long staged announcement fails loudly at staging time instead of
# being rejected by the API as "grapheme too big" (400) — which the old
# client mislabeled "network_error" and which cost the 2026-09-22 noon run.
BSKY_MAX_GRAPHEMES = 300

# Version-token parse rule (Story 083, exact rule): the buffer version is
# the FIRST regex match of vMAJOR.MINOR.PATCH in the staged text. The
# newest tag is parsed with the same rule. Tuple-compare decides stale.
VERSION_RE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")

WORKSPACE = Path.home() / ".hermes" / "flambeee"


def _env_path(name: str, default: Path) -> Path:
    override = os.environ.get(name)
    return Path(override) if override else default


PENDING = _env_path("FLAMBEEE_PENDING", WORKSPACE / "flambeee-team" / "state" / "pending-post.txt")
BSKY = _env_path("FLAMBEEE_BSKY", WORKSPACE / "scripts" / "flambeee-bsky.py")
VENV = _env_path("FLAMBEEE_VENV", WORKSPACE / ".venv" / "bin" / "python")
ENV_PATH = _env_path("FLAMBEEE_ENV_PATH", Path.home() / ".config" / "flambeee" / ".env")
REPO = _env_path("FLAMBEEE_REPO", WORKSPACE / "flambeee")
ALERT_LOG = _env_path(
    "FLAMBEEE_ALERT_LOG", WORKSPACE / "flambeee-team" / "state" / "noon-failure-alert.log"
)
RUN_LOG = _env_path(
    "FLAMBEEE_RUN_LOG", WORKSPACE / "flambeee-team" / "state" / "noon-job.log"
)
ARCHIVE = WORKSPACE / "flambeee-team" / "state" / "posted-posts.log"


def _now_iso() -> str:
    return DT.datetime.now().astimezone().isoformat()


def _append(path: Path, line: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(line + "\n")
    except Exception as exc:
        print(f"WARNING: could not write {path}: {exc}")


def fail_loud(mode: str, detail: str, code: int = 1) -> int:
    """Single shared failure exit (Story 082): non-zero plus durable
    run-log entry plus alert-artifact line. All modes route here."""
    ts = _now_iso()
    clean = " ".join(detail.split())
    print(f"ERROR [{mode}]: {clean} (exit={code})")
    _append(RUN_LOG, f"{ts} result=failure mode={mode} exit={code} {clean}")
    _append(ALERT_LOG, f"{ts} mode={mode} exit={code} {clean}")
    return code


def _parse_version(text: str):
    m = VERSION_RE.search(text)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _version_str(version) -> str:
    return f"v{version[0]}.{version[1]}.{version[2]}"


def resolve_newest_tag():
    """Resolve newest origin tag at run time. Returns ((major, minor,
    patch), tag_string) or (None, error_detail)."""
    pinned = os.environ.get("FLAMBEEE_NEWEST_TAG")
    if pinned:
        v = _parse_version(pinned)
        if v is None:
            return None, f"FLAMBEEE_NEWEST_TAG {pinned!r} names no version"
        return v, _version_str(v)
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO), "ls-remote", "--tags", "origin"],
            capture_output=True, text=True, timeout=60,
            env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
        )
    except Exception as exc:
        return None, f"git ls-remote failed: {exc}"
    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()
        tail = err[-1] if err else f"exit={proc.returncode}"
        return None, f"git ls-remote exit={proc.returncode}: {tail}"
    best = None
    for line in (proc.stdout or "").splitlines():
        ref = line.split()[-1] if line.split() else ""
        if not ref.startswith("refs/tags/") or ref.endswith("^{}"):
            continue
        v = _parse_version(ref.split("refs/tags/", 1)[1])
        if v is not None and (best is None or v > best):
            best = v
    if best is None:
        return None, "no version tags found on origin"
    return best, _version_str(best)


def main() -> int:
    if not PENDING.exists():
        print("No pending post — nothing to do.")
        _append(RUN_LOG, f"{_now_iso()} result=nothing-pending mode=none exit=0 no pending file")
        return 0

    text = PENDING.read_text().strip()
    if not text:
        return fail_loud("empty-buffer", "pending file empty; no post sent, pending kept")

    # Length guard: count GRAPHEMES, not codepoints — Bluesky measures
    # graphemes, so an emoji counts as one but len() would count several.
    try:
        import grapheme  # type: ignore
        n = grapheme.length(text)
    except Exception:
        n = len(text)
    if n > BSKY_MAX_GRAPHEMES:
        return fail_loud(
            "over-length",
            f"staged post is {n} graphemes; Bluesky maximum is "
            f"{BSKY_MAX_GRAPHEMES} (post NOT sent, pending kept)",
        )

    # Version guard (Story 083): refuse a buffer older than newest tag.
    newest, newest_err = resolve_newest_tag()
    if newest is None:
        return fail_loud("tag-resolution-failed", f"{newest_err}; post NOT sent, pending kept")
    buf_version = _parse_version(text)
    newest_str = _version_str(newest)
    if buf_version is not None and buf_version < newest:
        return fail_loud(
            "stale-buffer",
            f"buffer {_version_str(buf_version)} older than newest tag {newest_str}; "
            "post NOT sent, pending kept",
        )
    guard_note = _version_str(buf_version) if buf_version is not None else "unversioned"
    print(f"guard: buffer {guard_note} vs newest tag {newest_str}: ALLOW")

    if os.environ.get("FLAMBEEE_DRY_RUN") == "1":
        print("DRY RUN: guard allowed; real post skipped, pending kept.")
        _append(
            RUN_LOG,
            f"{_now_iso()} result=dry-run-allow mode=none exit=0 "
            f"buffer={guard_note} newest={newest_str}",
        )
        return 0

    # Pre-flight checks (Story 082): every known failure mode fails loud
    # here instead of dying silently mid-run.
    if not VENV.exists():
        return fail_loud(
            "missing-interpreter",
            f"venv interpreter absent at {VENV} (Oct 19 exit-127 mode); post NOT sent",
        )
    if not BSKY.exists():
        return fail_loud(
            "missing-helper", f"poster helper absent at {BSKY}; post NOT sent"
        )
    if not ENV_PATH.exists():
        return fail_loud(
            "missing-creds",
            f"credentials file absent at {ENV_PATH} (Oct 18-20 mode); post NOT sent",
        )

    print("=== STAGED POST ===")
    print(text)
    print("===================")

    # Post via the verified helper (clickable link facets automatic).
    # PYTHONPATH is stripped: this host points it at a Hermes python3.14
    # site-packages tree, which shadows the venv's own packages and makes a
    # working venv look broken (pydantic_core._pydantic_core is a 3.14 binary
    # and can never load under the venv's 3.13). See flambeee-bsky.py.
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    try:
        proc = subprocess.run(
            [str(VENV), str(BSKY), "post", text],
            capture_output=True, text=True, timeout=120, env=env,
        )
    except FileNotFoundError as exc:
        return fail_loud("missing-interpreter", f"post spawn failed: {exc}; post NOT sent")
    except subprocess.TimeoutExpired:
        return fail_loud("post-timeout", "helper timed out after 120s; post NOT sent")
    except Exception as exc:
        return fail_loud("post-failed", f"helper spawn failed: {exc}; post NOT sent")
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out[-2000:])

    # Verify the post actually exists by finding the URI in output.
    if "at://" not in out and "app.bsky.feed.post" not in out:
        return fail_loud(
            "api-rejection",
            f"no post URI in helper output exit={proc.returncode}; "
            "no success entry written, pending kept",
        )

    # Success — keep a copy of the announcement for the record, clear pending.
    with ARCHIVE.open("a") as f:
        f.write(f"--- {DT.datetime.now().isoformat()} ---\n{text}\n")
    PENDING.unlink(missing_ok=True)
    _append(RUN_LOG, f"{_now_iso()} result=posted mode=none exit=0 buffer={guard_note}")
    print("Posted and verified; pending post cleared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
