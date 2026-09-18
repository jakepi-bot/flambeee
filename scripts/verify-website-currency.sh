#!/usr/bin/env bash
# Story 038: Website latest-release currency and mirror byte-identity verification.
#
# Standing check. Proves the Flambeee home page is current and that the live
# file and the repo mirror are byte-identical. Prints one PASS/FAIL line per
# check, plus auditable detail (origin latest tag, heading text, cmp exit code,
# link hrefs). Exits non-zero on any failure.
#
# Usage:
#   scripts/verify-website-currency.sh
#
# Paths: share/ is OUTSIDE the repo, so the live file is addressed by its
# ABSOLUTE path.

set -u
set -o pipefail

LIVE="/home/jake/.openclaw/workspace/share/Flambeee/index.html"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIRROR="${REPO_ROOT}/website/index.html"
GAMES_DIR="/home/jake/.openclaw/workspace/share/Flambeee/games"
RELEASES_URL="https://github.com/jakepi-bot/flambeee/releases"
BLOG_URL="https://github.com/jakepi-bot/flambeee/blob/main/BLOG.md"

fails=0
pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; fails=$((fails + 1)); }

echo "== Story 038: website currency + mirror byte-identity =="
echo "live   : ${LIVE}"
echo "mirror : ${MIRROR}"
echo

# --- Preconditions: both files exist ---
if [ ! -f "$LIVE" ]; then
  fail "live file not found: ${LIVE}"
  echo
  echo "RESULT: FAIL (${fails} check(s) failed)"
  exit 1
fi
if [ ! -f "$MIRROR" ]; then
  fail "repo mirror not found: ${MIRROR}"
  echo
  echo "RESULT: FAIL (${fails} check(s) failed)"
  exit 1
fi

# --- Check 1: live vs repo mirror, byte-identical ---
cmp -s "$LIVE" "$MIRROR"
cmp_rc=$?
echo "cmp exit code: ${cmp_rc}"
if [ "$cmp_rc" -eq 0 ]; then
  pass "live and repo mirror are byte-identical (cmp exit 0)"
else
  fail "live and repo mirror differ (cmp exit ${cmp_rc})"
  cmp "$LIVE" "$MIRROR" 2>&1 | head -3 | sed 's/^/      /'
fi
echo "live lines:   $(wc -l < "$LIVE")"
echo "mirror lines: $(wc -l < "$MIRROR")"
echo

# --- Check 2: What's New heading names the true latest release tag on origin ---
# Source of truth is origin, not the local tag list (local tags can lag).
latest_tag="$(git -C "$REPO_ROOT" ls-remote --tags origin 2>/dev/null \
  | sed 's/.*refs\/tags\///' \
  | grep -v '\^{}' \
  | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' \
  | sort -V \
  | tail -1)"
echo "origin latest tag: ${latest_tag:-<none found>}"
if [ -z "$latest_tag" ]; then
  fail "could not determine latest tag from git ls-remote --tags origin"
else
  heading="$(grep -o "<h3>${latest_tag}[^<]*</h3>" "$LIVE" | head -1 | sed 's/<[^>]*>//g')"
  echo "heading found: ${heading:-<none>}"
  if [ -n "$heading" ]; then
    pass "What's New heading names the true latest release tag (${latest_tag})"
  else
    # Report whatever version the heading does name, to make the drift auditable.
    other="$(grep -o '<h3>v[0-9][^<]*</h3>' "$LIVE" | head -1 | sed 's/<[^>]*>//g')"
    fail "What's New heading does not name origin latest ${latest_tag} (heading: ${other:-<none>})"
  fi
fi
echo

# --- Check 3: summary text has no em dashes and no heavy emoji ---
# Scope the scan to the What's New summary paragraph.
summary="$(grep -o '<p>The town now has a Quest Log[^<]*</p>' "$LIVE" | sed 's/<[^>]*>//g')"
if [ -z "$summary" ]; then
  summary="$(awk '/<section class="whats-new"/,/<\/section>/' "$LIVE" | grep -o '<p>[^<]*</p>' | head -1 | sed 's/<[^>]*>//g')"
fi
echo "summary: ${summary:-<none>}"
if [ -z "$summary" ]; then
  fail "could not locate the What's New summary paragraph"
else
  if printf '%s' "$summary" | grep -q $'\xe2\x80\x94'; then
    fail "summary contains an em dash"
  else
    pass "summary contains no em dashes"
  fi
  # Heavy emoji: anything outside the Basic Multilingual Plane surrogate span
  # used by emoji (U+1F300 and up), plus common symbol ranges.
  if printf '%s' "$summary" | grep -qP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}\x{FE0F}]'; then
    fail "summary contains heavy emoji"
  else
    pass "summary contains no heavy emoji"
  fi
fi
echo

# --- Check 4: Releases and Blog are real clickable <a href> anchors ---
releases_a="$(grep -o "<a href=\"${RELEASES_URL}\"[^>]*>Releases</a>" "$LIVE" | head -1)"
blog_a="$(grep -o "<a href=\"${BLOG_URL}\"[^>]*>Blog</a>" "$LIVE" | head -1)"
echo "Releases anchor: ${releases_a:-<none>}"
echo "Blog anchor:     ${blog_a:-<none>}"
if [ -n "$releases_a" ] && [ -n "$blog_a" ]; then
  pass "Releases and Blog are real clickable <a href> anchors"
else
  [ -n "$releases_a" ] || fail "Releases link missing or not a real <a href> to ${RELEASES_URL}"
  [ -n "$blog_a" ] || fail "Blog link missing or not a real <a href> to ${BLOG_URL}"
fi
# Bare-text URL guard: the URLs must not also appear as unlinked plain text.
if grep -qE ">[[:space:]]*${RELEASES_URL}[[:space:]]*<" "$LIVE"; then
  fail "Releases URL appears as bare text (not a clickable link)"
else
  pass "no bare-text Releases URL"
fi
echo

# --- Check 5: Play links point at relative games/*.html and those files exist ---
play_bad=0
play_count=0
while IFS= read -r href; do
  [ -n "$href" ] || continue
  play_count=$((play_count + 1))
  case "$href" in
    games/*.html) : ;;
    *) fail "Play link is not a relative games/*.html path: ${href}"; play_bad=$((play_bad + 1)); continue ;;
  esac
  if [ -f "${GAMES_DIR}/${href#games/}" ]; then
    echo "  ok: ${href} -> ${GAMES_DIR}/${href#games/}"
  else
    fail "Play target file missing: ${GAMES_DIR}/${href#games/}"
    play_bad=$((play_bad + 1))
  fi
done < <(grep -o 'class="play-btn" href="[^"]*"' "$LIVE" | sed 's/.*href="//; s/"$//' | sort -u)
echo "play links checked: ${play_count}"
if [ "$play_count" -eq 0 ]; then
  fail "no Play links found on the live page"
elif [ "$play_bad" -eq 0 ]; then
  pass "all Play links are relative games/*.html and their files exist"
fi
echo

# --- Result ---
if [ "$fails" -eq 0 ]; then
  echo "RESULT: PASS (all checks green)"
  exit 0
fi
echo "RESULT: FAIL (${fails} check(s) failed)"
exit 1
