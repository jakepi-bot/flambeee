#!/usr/bin/env bash
# Story 102 (Session 43): Website latest-release currency and mirror byte-identity
# verification, with the live leg rewritten as HTTPS fetch-and-compare.
#
# Standing check. Proves the Flambeee home page is current and that the served
# copy and the repo mirror are byte-identical. Prints one PASS/FAIL line per
# check, plus auditable detail (origin latest tag, heading text, HTTP status,
# both sha256, cmp exit code, link hrefs). Exits non-zero on any failure.
#
# Story 102 rewrite: the absent local path /home/jake/share/Flambeee/ is retired
# as a check item (absent from the run box many sessions running). The live leg
# now fetches ${FLAMBEEE_LIVE_URL:-https://flambeee.com/} with curl and compares
# the served bytes against the repo mirror website/index.html. Game link targets
# resolve under the repo website/games/ dir and Apps link targets under the repo
# website/apps/ dir. On a served-vs-mirror mismatch, do not assume the served
# copy is stale: inspect git log and HEAD for website/index.html first, restore
# the stale side from the committed side, re-run, and record both sha256.
#
# Usage:
#   scripts/verify-website-currency.sh
#   FLAMBEEE_LIVE_URL=https://staging.example/ scripts/verify-website-currency.sh

set -u
set -o pipefail

LIVE_URL="${FLAMBEEE_LIVE_URL:-https://flambeee.com/}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIRROR="${REPO_ROOT}/website/index.html"
GAMES_DIR="${REPO_ROOT}/website/games"
APPS_DIR="${REPO_ROOT}/website/apps"
RELEASES_URL="https://github.com/jakepi-bot/flambeee/releases"
BLOG_URL="https://github.com/jakepi-bot/flambeee/blob/main/BLOG.md"

fails=0
pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; fails=$((fails + 1)); }

echo "== Story 102: website currency + mirror byte-identity =="
echo "live url : ${LIVE_URL}"
echo "mirror   : ${MIRROR}"
echo

# --- Preconditions: repo mirror exists; served copy fetched over HTTPS ---
if [ ! -f "$MIRROR" ]; then
  fail "repo mirror not found: ${MIRROR}"
  echo
  echo "RESULT: FAIL (${fails} check(s) failed)"
  exit 1
fi
SERVED="$(mktemp)"
trap 'rm -f "$SERVED"' EXIT
if ! http_status="$(curl -sS --max-time 25 -o "$SERVED" -w '%{http_code}' "$LIVE_URL")"; then
  fail "live fetch failed: curl could not retrieve ${LIVE_URL}"
  echo
  echo "RESULT: FAIL (${fails} check(s) failed)"
  exit 1
fi
echo "live HTTP status: ${http_status}"
if [ "$http_status" != "200" ]; then
  fail "live fetch returned HTTP ${http_status}, expected 200"
  echo
  echo "RESULT: FAIL (${fails} check(s) failed)"
  exit 1
fi
pass "live fetch returned HTTP 200"
echo

# --- Check 1: served copy vs repo mirror, byte-identical ---
served_sha="$(sha256sum "$SERVED" | awk '{print $1}')"
mirror_sha="$(sha256sum "$MIRROR" | awk '{print $1}')"
echo "served sha256: ${served_sha}"
echo "mirror sha256: ${mirror_sha}"
cmp -s "$SERVED" "$MIRROR"
cmp_rc=$?
echo "cmp exit code: ${cmp_rc}"
if [ "$cmp_rc" -eq 0 ]; then
  pass "served and repo mirror are byte-identical (MATCH, cmp exit 0)"
else
  fail "served and repo mirror differ (MISMATCH, cmp exit ${cmp_rc})"
  cmp "$SERVED" "$MIRROR" 2>&1 | head -3 | sed 's/^/      /'
fi
echo "served lines:   $(wc -l < "$SERVED")"
echo "mirror lines: $(wc -l < "$MIRROR")"
echo

# --- Check 2: What's New heading names the true latest release tag on origin ---
# Source of truth is origin, not the local tag list (local tags can lag).
# Story 107: resolve the predecessor tag (second-newest) alongside the newest
# from the same ls-remote source with the same vX.Y.Z filter and sort -V
# ordering. Check 7 compares against the predecessor; Check 6 keeps newest.
sorted_tags="$(git -C "$REPO_ROOT" ls-remote --tags origin 2>/dev/null \
  | sed 's/.*refs\/tags\///' \
  | grep -v '\^{}' \
  | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' \
  | sort -V)"
latest_tag="$(printf '%s\n' "$sorted_tags" | tail -1)"
predecessor_tag=""
if [ "$(printf '%s\n' "$sorted_tags" | wc -l)" -ge 2 ]; then
  predecessor_tag="$(printf '%s\n' "$sorted_tags" | tail -2 | head -1)"
fi
echo "origin latest tag: ${latest_tag:-<none found>}"
echo "origin predecessor tag: ${predecessor_tag:-<none found>}"
if [ -z "$latest_tag" ]; then
  fail "could not determine latest tag from git ls-remote --tags origin"
else
  heading="$(grep -o "<h3>${latest_tag}[^<]*</h3>" "$SERVED" | head -1 | sed 's/<[^>]*>//g')"
  echo "heading found: ${heading:-<none>}"
  if [ -n "$heading" ]; then
    pass "What's New heading names the true latest release tag (${latest_tag})"
  else
    # Report whatever version the heading does name, to make the drift auditable.
    other="$(grep -o '<h3>v[0-9][^<]*</h3>' "$SERVED" | head -1 | sed 's/<[^>]*>//g')"
    fail "What's New heading does not name origin latest ${latest_tag} (heading: ${other:-<none>})"
  fi
fi
echo

# --- Check 3: summary text has no em dashes and no heavy emoji ---
# Scope the scan to the What's New summary paragraph.
summary="$(grep -o '<p>The town now has a Quest Log[^<]*</p>' "$SERVED" | sed 's/<[^>]*>//g')"
if [ -z "$summary" ]; then
  summary="$(awk '/<section class="whats-new"/,/<\/section>/' "$SERVED" | grep -o '<p>[^<]*</p>' | head -1 | sed 's/<[^>]*>//g')"
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
releases_a="$(grep -o "<a href=\"${RELEASES_URL}\"[^>]*>Releases</a>" "$SERVED" | head -1)"
blog_a="$(grep -o "<a href=\"${BLOG_URL}\"[^>]*>Blog</a>" "$SERVED" | head -1)"
echo "Releases anchor: ${releases_a:-<none>}"
echo "Blog anchor:     ${blog_a:-<none>}"
if [ -n "$releases_a" ] && [ -n "$blog_a" ]; then
  pass "Releases and Blog are real clickable <a href> anchors"
else
  [ -n "$releases_a" ] || fail "Releases link missing or not a real <a href> to ${RELEASES_URL}"
  [ -n "$blog_a" ] || fail "Blog link missing or not a real <a href> to ${BLOG_URL}"
fi
# Bare-text URL guard: the URLs must not also appear as unlinked plain text.
if grep -qE ">[[:space:]]*${RELEASES_URL}[[:space:]]*<" "$SERVED"; then
  fail "Releases URL appears as bare text (not a clickable link)"
else
  pass "no bare-text Releases URL"
fi
echo

# --- Check 5: Play and Open links point at relative targets and those files exist ---
# Game cards link games/*.html (resolved under website/games/); Apps cards link
# apps/*.html (resolved under website/apps/). Both use the play-btn class.
play_bad=0
play_count=0
while IFS= read -r href; do
  [ -n "$href" ] || continue
  play_count=$((play_count + 1))
  case "$href" in
    games/*.html)
      target="${GAMES_DIR}/${href#games/}"
      ;;
    apps/*.html)
      target="${APPS_DIR}/${href#apps/}"
      ;;
    *)
      fail "card link is not a relative games/*.html or apps/*.html path: ${href}"
      play_bad=$((play_bad + 1))
      continue
      ;;
  esac
  if [ -f "$target" ]; then
    echo "  ok: ${href} -> ${target}"
  else
    fail "card link target file missing: ${target}"
    play_bad=$((play_bad + 1))
  fi
done < <(grep -o 'class="play-btn" href="[^"]*"' "$SERVED" | sed 's/.*href="//; s/"$//' | sort -u)
echo "card links checked: ${play_count}"
if [ "$play_count" -eq 0 ]; then
  fail "no card links found on the served page"
elif [ "$play_bad" -eq 0 ]; then
  pass "all card links are relative games/*.html or apps/*.html and their files exist"
fi
echo

# --- Check 6 (Story 105): repo What's New heading names the newest tag ---
# Same tag resolution as Check 2 (origin ls-remote at run time), but measured
# on the repo mirror file so a stale tree fails the gate even when the served
# copy is current. Both values print on failure.
story105_tag="${latest_tag:-}"
echo "Story 105 newest tag (runtime): ${story105_tag:-<none found>}"
if [ -z "$story105_tag" ]; then
  fail "Story 105 heading check: could not resolve newest tag (mirror heading unread)"
else
  story105_mirror_heading="$(grep -o '<h3>v[0-9][^<]*</h3>' "$MIRROR" | head -1 | sed 's/<[^>]*>//g')"
  echo "Story 105 mirror heading: ${story105_mirror_heading:-<none>}"
  story105_hit="$(grep -o "<h3>${story105_tag}[^<]*</h3>" "$MIRROR" | head -1 | sed 's/<[^>]*>//g')"
  if [ -n "$story105_hit" ]; then
    pass "Story 105 heading check: mirror heading names newest tag ${story105_tag} (heading: ${story105_hit})"
  else
    fail "Story 105 heading check: mirror heading does not name newest tag ${story105_tag} (heading: ${story105_mirror_heading:-<none>})"
  fi
fi
echo

# --- Check 7 (Story 105, Story 107 predecessor compare): CACHE_VERSION changed since the predecessor tag ---
# Story 107: compares against the second-newest origin tag, not the newest.
# Against the newest tag the check is a self-compare post-tag by construction
# (same bytes, same CACHE, guaranteed FAIL). Check 6 still targets newest.
# Both values print on failure, with the predecessor tag named.
story105_cache_now="$(grep -E '^var CACHE_VERSION = ' "${REPO_ROOT}/website/sw.js" 2>/dev/null | sed 's/[^0-9]//g')"
story105_cache_tag=""
story105_pred_tag="${predecessor_tag:-}"
if [ -n "$story105_pred_tag" ]; then
  story105_cache_tag="$(git -C "$REPO_ROOT" show "${story105_pred_tag}:website/sw.js" 2>/dev/null | grep -E '^var CACHE_VERSION = ' | sed 's/[^0-9]//g')"
fi
echo "Story 107 CACHE_VERSION now: ${story105_cache_now:-<none>}"
echo "Story 107 CACHE_VERSION at predecessor ${story105_pred_tag:-<no tag>}: ${story105_cache_tag:-<none>}"
if [ -z "$story105_cache_now" ] || [ -z "$story105_cache_tag" ]; then
  fail "Story 107 CACHE check: could not read CACHE_VERSION (now: ${story105_cache_now:-<none>}, at predecessor ${story105_pred_tag:-<no tag>}: ${story105_cache_tag:-<none>})"
elif [ "$story105_cache_now" != "$story105_cache_tag" ]; then
  pass "Story 107 CACHE check: CACHE_VERSION changed since predecessor ${story105_pred_tag} (now: ${story105_cache_now}, at tag: ${story105_cache_tag})"
else
  fail "Story 107 CACHE check: CACHE_VERSION unchanged since predecessor ${story105_pred_tag} (now: ${story105_cache_now} == at tag: ${story105_cache_tag})"
fi
echo

# --- Check 8 (Story 105): every app-card link target is in PRECACHE_URLS ---
# Both sides read at run time: card hrefs from the mirror HTML, entries from
# website/sw.js. Nothing hardcoded, so a new app passes as long as its card
# and its precache entry agree. The missing target is named on failure.
story105_precache_bad=0
story105_precache_count=0
while IFS= read -r story105_href; do
  [ -n "$story105_href" ] || continue
  story105_precache_count=$((story105_precache_count + 1))
  story105_entry="./${story105_href}"
  if grep -qF "'${story105_entry}'" "${REPO_ROOT}/website/sw.js"; then
    echo "  Story 105 precached: ${story105_href}"
  else
    fail "Story 105 precache check: app-card target missing from PRECACHE_URLS: ${story105_href}"
    story105_precache_bad=$((story105_precache_bad + 1))
  fi
done < <(grep -o 'class="play-btn" href="apps/[^"]*"' "$MIRROR" | sed 's/.*href="//; s/"$//' | sort -u)
echo "Story 105 app-card targets checked: ${story105_precache_count}"
if [ "$story105_precache_count" -eq 0 ]; then
  fail "Story 105 precache check: no app-card link targets found in mirror"
elif [ "$story105_precache_bad" -eq 0 ]; then
  pass "Story 105 precache check: all ${story105_precache_count} app-card targets present in PRECACHE_URLS"
fi
echo

# --- Result ---
if [ "$fails" -eq 0 ]; then
  echo "RESULT: PASS (all checks green)"
  exit 0
fi
echo "RESULT: FAIL (${fails} check(s) failed)"
exit 1
