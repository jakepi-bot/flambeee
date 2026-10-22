#!/usr/bin/env bash
# Byte-identity checker: vendored poster mirror vs live file (Story 086).
#
# Compares the repo mirror against the live poster with `cmp` plus equal
# sha256 on both sides, and compares the mirror against the recorded pin.
# Exit 0 only on full agreement (mirror == live == pin).
#
# Paths (overrides exist for scratch drift tests only):
#   FLAMBEEE_MIRROR  default: this repo's scripts/flambeee-post-noon.mirror.py
#   FLAMBEEE_LIVE    default: /home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py
#   FLAMBEEE_PIN     default: scripts/flambeee-post-noon.mirror.py.sha256
#
# The live file is read only, never written, moved, or edited. On mismatch
# this script reports which side differs and exits non-zero; it fixes
# nothing. Any sync is a recorded human decision, not a quiet fix.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRROR="${FLAMBEEE_MIRROR:-$HERE/flambeee-post-noon.mirror.py}"
LIVE="${FLAMBEEE_LIVE:-/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py}"
PIN_FILE="${FLAMBEEE_PIN:-$HERE/flambeee-post-noon.mirror.py.sha256}"

fail=0

[ -f "$MIRROR" ] || { echo "MISSING mirror: $MIRROR"; fail=1; }
[ -f "$LIVE" ] || { echo "MISSING live file: $LIVE"; fail=1; }
[ -f "$PIN_FILE" ] || { echo "MISSING pin file: $PIN_FILE"; fail=1; }
if [ "$fail" -ne 0 ]; then exit 2; fi

MIRROR_SHA="$(sha256sum "$MIRROR" | cut -d' ' -f1)"
LIVE_SHA="$(sha256sum "$LIVE" | cut -d' ' -f1)"
PIN="$(tr -d ' \t\n' < "$PIN_FILE")"

echo "mirror: $MIRROR"
echo "mirror sha256: $MIRROR_SHA"
echo "live:   $LIVE"
echo "live sha256:   $LIVE_SHA"
echo "pin:    $PIN"

if cmp -s "$MIRROR" "$LIVE"; then
  echo "cmp: mirror and live file are byte-identical"
else
  echo "DRIFT: mirror and live file differ (cmp non-zero); neither side edited"
  fail=1
fi

if [ "$MIRROR_SHA" = "$LIVE_SHA" ]; then
  echo "sha256: mirror == live"
else
  echo "DRIFT: mirror sha256 != live sha256"
  fail=1
fi

if [ "$MIRROR_SHA" = "$PIN" ]; then
  echo "pin: mirror == pin"
else
  echo "DRIFT: mirror sha256 != recorded pin"
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "VERIFY OK: mirror == live == pin"
  exit 0
else
  echo "VERIFY FAILED: see DRIFT lines above; report only, no writes made"
  exit 1
fi
