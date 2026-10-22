#!/usr/bin/env bash
# Noon pre-start launcher (Story 085, Session 38).
#
# Scheduled entry for the noon post. Resolves the python interpreter,
# traps every pre-start failure loudly, and only then starts the poster.
# In-poster failures stay owned by the Story 082 path inside the poster.
#
# Interpreter resolution rule (exact, recorded):
#   1. If FLAMBEEE_INTERPRETER is set and non-empty, it names the
#      interpreter. A value with no slash is looked up with
#      `command -v`; a value with a slash is used as an explicit path.
#   2. Otherwise the default is the venv interpreter
#      /home/jake/.hermes/flambeee/.venv/bin/python (explicit path).
#   There is no silent fallback: a missing default is trapped, not hidden.
#
# Poster path: FLAMBEEE_POSTER override, else the live poster
#   /home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py.
# Alert log: FLAMBEEE_ALERT_LOG override (scratch path in tests), else the
#   same Story 082 artifact
#   /home/jake/.hermes/flambeee/flambeee-team/state/noon-failure-alert.log.
#
# Pre-start trap: interpreter missing (exit 127), interpreter not
# executable (exit 126), poster file missing (exit 1). Each appends one
# line to the alert log in the poster format:
#   <ISO-timestamp> mode=launcher-<cause> exit=<code> <detail>
# Happy path: exec into the poster, so the launcher exits with the poster
# exit code unchanged and writes no alert line of its own.
#
# Scheduler install (Jake's one line, agents never touch the schedule):
#   /home/jake/.hermes/flambeee/flambeee/scripts/run-noon-post.sh
set -u

DEFAULT_INTERPRETER="/home/jake/.hermes/flambeee/.venv/bin/python"
DEFAULT_POSTER="/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py"
DEFAULT_ALERT="/home/jake/.hermes/flambeee/flambeee-team/state/noon-failure-alert.log"

INTERPRETER="${FLAMBEEE_INTERPRETER:-$DEFAULT_INTERPRETER}"
POSTER="${FLAMBEEE_POSTER:-$DEFAULT_POSTER}"
ALERT_LOG="${FLAMBEEE_ALERT_LOG:-$DEFAULT_ALERT}"

now_iso() {
  date --iso-8601=seconds
}

trap_fail() {
  # $1 cause token, $2 exit code, $3 detail
  local cause="$1" code="$2" detail="$3"
  local ts
  ts="$(now_iso)"
  mkdir -p "$(dirname "$ALERT_LOG")" 2>/dev/null || true
  printf '%s mode=launcher-%s exit=%s %s\n' "$ts" "$cause" "$code" "$detail" >> "$ALERT_LOG" 2>/dev/null || true
  echo "ERROR [launcher-$cause]: $detail (exit=$code)" >&2
  exit "$code"
}

# Resolve a bare name via command -v; explicit paths pass through.
RESOLVED="$INTERPRETER"
if [[ "$INTERPRETER" != *"/"* ]]; then
  RESOLVED="$(command -v "$INTERPRETER" 2>/dev/null || true)"
  if [ -z "$RESOLVED" ]; then
    trap_fail "no-interpreter" 127 "interpreter '$INTERPRETER' not found on PATH; poster not started"
  fi
fi

if [ ! -e "$RESOLVED" ]; then
  trap_fail "no-interpreter" 127 "interpreter '$RESOLVED' missing; poster not started"
fi
if [ ! -x "$RESOLVED" ] || [ -d "$RESOLVED" ]; then
  trap_fail "not-executable" 126 "interpreter '$RESOLVED' not executable; poster not started"
fi
if [ ! -f "$POSTER" ]; then
  trap_fail "no-poster" 1 "poster file '$POSTER' missing; nothing started"
fi

exec "$RESOLVED" "$POSTER" "$@"
