#!/usr/bin/env bash
# Regression test: noon-job failure alert (082) + pending-post version guard (083).
# Usage: scripts/test-noon-failure-alert.sh [TARGET_POSTER]
# Default target is the prod poster /home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py.
# Every case runs the REAL poster file with scratch copies / env overrides /
# HOME redirect only. Never touches the live pending-post.txt, the quarantine
# file, posted-posts.log, or any schedule. Sends no real post (positive
# control runs in FLAMBEEE_DRY_RUN=1; refusal cases never reach the post step).
set -u

TARGET="${1:-/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py}"
PASS=0
FAIL=0

SCRATCH="$(mktemp -d)"
ALERT="$SCRATCH/alert.log"
RUNLOG="$SCRATCH/run.log"
FAKEHOME="$SCRATCH/fakehome"
mkdir -p "$FAKEHOME"
QUARANTINE="/home/jake/.hermes/flambeee/flambeee-team/state/pending-post.quarantine-2026-10-20-v0.32.0.txt"
POSTED="/home/jake/.hermes/flambeee/flambeee-team/state/posted-posts.log"
QUAR_BEFORE="$(sha256sum "$QUARANTINE" | cut -d' ' -f1)"
POSTED_BEFORE="$(sha256sum "$POSTED" | cut -d' ' -f1)"

V033="Day Pad counts your characters now, live N/280 on your daily line. v0.33.0 https://flambeee.com"

run_poster() {
  # Runs the target poster against scratch pending; echoes output, returns poster exit.
  # Honors EXTRA_ENV (extra VAR=val assignments) and PENDING_OVERRIDE.
  env -u PYTHONPATH \
    FLAMBEEE_PENDING="${PENDING_OVERRIDE:-$SCRATCH/pending.txt}" \
    FLAMBEEE_ALERT_LOG="$ALERT" \
    FLAMBEEE_RUN_LOG="$RUNLOG" \
    FLAMBEEE_NEWEST_TAG="v0.33.0" \
    ${EXTRA_ENV:-} \
    python3 "$TARGET" 2>&1
}

check() {
  # $1 desc, $2 expected exit, $3 expected alert-mode substring (empty = expect NO new alert line)
  local desc="$1" want_exit="$2" want_mode="$3"
  local before_lines after_lines out exit_code
  before_lines="$(wc -l < "$ALERT" 2>/dev/null || echo 0)"
  out="$(eval "$4")"
  exit_code=$?
  after_lines="$(wc -l < "$ALERT" 2>/dev/null || echo 0)"
  if [ "$exit_code" -ne "$want_exit" ]; then
    echo "FAIL: $desc: exit=$exit_code, want $want_exit"; echo "$out" | tail -3; FAIL=$((FAIL+1)); return
  fi
  if [ -z "$want_mode" ]; then
    if [ "$after_lines" -ne "$before_lines" ]; then
      echo "FAIL: $desc: alert line written but none expected"; FAIL=$((FAIL+1)); return
    fi
  else
    if [ "$after_lines" -le "$before_lines" ]; then
      echo "FAIL: $desc: no alert line appended"; FAIL=$((FAIL+1)); return
    fi
    if ! tail -n +"$((before_lines+1))" "$ALERT" | grep -q "mode=$want_mode" ; then
      echo "FAIL: $desc: alert line lacks mode=$want_mode"; tail -2 "$ALERT"; FAIL=$((FAIL+1)); return
    fi
    if ! tail -n +"$((before_lines+1))" "$ALERT" | grep -q "exit=$want_exit"; then
      echo "FAIL: $desc: alert line lacks exit=$want_exit"; FAIL=$((FAIL+1)); return
    fi
  fi
  echo "PASS: $desc (exit=$exit_code)"; PASS=$((PASS+1))
}

: > "$ALERT"
: > "$RUNLOG"

echo "--- 082: missing interpreter (FLAMBEEE_VENV override, in-poster equivalent) ---"
printf '%s' "$V033" > "$SCRATCH/pending.txt"
EXTRA_ENV="FLAMBEEE_VENV=$SCRATCH/no-such-venv-python" \
  check "missing-interpreter" 1 "missing-interpreter" 'run_poster'

echo "--- 082: missing creds (HOME redirect to empty fakehome) ---"
printf '%s' "$V033" > "$SCRATCH/pending.txt"
EXTRA_ENV="HOME=$FAKEHOME FLAMBEEE_VENV=/home/jake/.hermes/flambeee/.venv/bin/python FLAMBEEE_BSKY=/home/jake/.hermes/flambeee/scripts/flambeee-bsky.py" \
  check "missing-creds" 1 "missing-creds" 'run_poster'

echo "--- 082: empty buffer ---"
printf '' > "$SCRATCH/pending.txt"
EXTRA_ENV="" \
  check "empty-buffer" 1 "empty-buffer" 'run_poster'
if [ -f "$SCRATCH/pending.txt" ]; then echo "PASS: empty buffer pending kept"; PASS=$((PASS+1)); else echo "FAIL: empty buffer pending not kept"; FAIL=$((FAIL+1)); fi

echo "--- 082: over-length buffer (301 chars) ---"
python3 -c "import sys; sys.stdout.write('x'*301)" > "$SCRATCH/pending.txt"
EXTRA_ENV="" \
  check "over-length" 1 "over-length" 'run_poster'

echo "--- 083: stale buffer REFUSE (quarantine v0.32.0 text copy vs v0.33.0) ---"
cp "$QUARANTINE" "$SCRATCH/pending.txt"
EXTRA_ENV="" \
  check "stale-buffer-refuse" 1 "stale-buffer" 'run_poster'
if grep -q "v0.32.0" "$SCRATCH/pending.txt"; then echo "PASS: stale buffer pending kept"; PASS=$((PASS+1)); else echo "FAIL: stale buffer pending not kept"; FAIL=$((FAIL+1)); fi

echo "--- 082: API rejection (fake helper exits 1, no URI; dummy creds so pre-flight passes) ---"
mkdir -p "$FAKEHOME/.config/flambeee"
printf 'BSKY_HANDLE=x\nBSKY_PASSWORD=y\n' > "$FAKEHOME/.config/flambeee/.env"
printf '#!/usr/bin/env bash\necho "simulated helper failure"; exit 1\n' > "$SCRATCH/fake-bsky.sh"
chmod +x "$SCRATCH/fake-bsky.sh"
printf '%s' "$V033" > "$SCRATCH/pending.txt"
EXTRA_ENV="HOME=$FAKEHOME FLAMBEEE_VENV=/home/jake/.hermes/flambeee/.venv/bin/python FLAMBEEE_BSKY=$SCRATCH/fake-bsky.sh" \
  check "api-rejection" 1 "api-rejection" 'run_poster'

echo "--- 083: current buffer ALLOW (dry-run, no real post) ---"
printf '%s' "$V033" > "$SCRATCH/pending.txt"
EXTRA_ENV="FLAMBEEE_DRY_RUN=1" \
  check "current-buffer-allow-dryrun" 0 "" 'run_poster'

echo "--- 082 scenario 5: nothing pending exits 0 silently ---"
PENDING_OVERRIDE="$SCRATCH/does-not-exist" EXTRA_ENV="" \
  check "nothing-pending" 0 "" 'run_poster'
unset PENDING_OVERRIDE

echo "--- live-path integrity ---"
QUAR_AFTER="$(sha256sum "$QUARANTINE" | cut -d' ' -f1)"
POSTED_AFTER="$(sha256sum "$POSTED" | cut -d' ' -f1)"
if [ "$QUAR_BEFORE" = "$QUAR_AFTER" ]; then echo "PASS: quarantine file untouched"; PASS=$((PASS+1)); else echo "FAIL: quarantine file changed"; FAIL=$((FAIL+1)); fi
if [ "$POSTED_BEFORE" = "$POSTED_AFTER" ]; then echo "PASS: posted-posts.log untouched"; PASS=$((PASS+1)); else echo "FAIL: posted-posts.log changed"; FAIL=$((FAIL+1)); fi

echo "=== $PASS passed, $FAIL failed ==="
rm -rf "$SCRATCH"
[ "$FAIL" -eq 0 ]
