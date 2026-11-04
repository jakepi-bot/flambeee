#!/usr/bin/env python3
"""Ember hot-idea search: top-3 new web game ideas with seen-source exclusion.

Implements the interfaces defined in docs/ember-web-search-design.md
(sections 2 and 3) for task t_e2e2cd14.

Pipeline (agent drives, this module enforces):
  1. Agent runs DEFAULT_QUERIES via web_search, reads the results, and
     authors one candidate dict per promising result (prose judgment stays
     agent-side; see work-session-prompt.md Phase 1 step 4).
  2. select_top_ideas() drops every candidate whose canonical URL or domain
     is excluded by the seen-sources store, ranks the rest with a
     deterministic rubric, and returns exactly three HotGameIdea records.
  3. record_sources() appends the three used sources to the store so no
     later session reuses them.

Store: docs/ember-seen-sources.json, keyed by canonical URL.
Canonical form: lowercase scheme+host, strip default port, strip trailing
slash, drop tracking params (utm_*, fbclid, gclid, msclkid, mc_cid,
mc_eid, dsaid, wbraid, gbraid), drop fragment, sort remaining params.

Exclusion (two tiers):
  1. URL tier: an exact canonical URL in the store is never reused.
  2. Domain tier: a domain is excluded while
     current_session - first_seen_session <= reuse_cooldown_sessions
     for ANY record carrying that domain. Default cooldown is 4 sessions.

Stdlib only. No network access: search execution stays with the caller.
"""

import argparse
import copy
import datetime
import json
import re
import sys
import urllib.parse

# Queries aimed at recent/new web game concepts and trends. The caller runs
# these (or close variants) via web_search, then authors candidates from the
# results. Kept here so every session asks the same seed questions.
DEFAULT_QUERIES = [
    "new browser web game 2026",
    "hot indie web game trend 2026",
    "viral browser game mechanic 2026",
    "itch.io game jam winner browser 2026",
]

TRACKING_PARAMS = frozenset({
    "fbclid", "gclid", "msclkid", "dsaid", "wbraid", "gbraid",
    "mc_cid", "mc_eid",
})

HOT_IDEA_REQUIRED = (
    "title", "source_url", "source_domain", "why_hot",
    "core_mechanic", "audience", "monetization", "retrieved_at",
)

DEFAULT_COOLDOWN_SESSIONS = 4

# --- scoring rubric -------------------------------------------------------
# Deterministic, explainable, integer points. Max total is 10.
_RECENCY_PAT = re.compile(
    r"\b(2026|just launched|this month|this week|latest|debut|brand new)\b",
    re.I,
)
_EVIDENCE_NUM_PAT = re.compile(r"\d")
_EVIDENCE_WORD_PAT = re.compile(
    r"\b(million|thousand|billion|percent|%|viral|record|players|downloads|"
    r"copies sold|wishlists)\b",
    re.I,
)
_WEBFIT_TERMS = ("browser", "web game", "html5", "itch.io", "game jam",
                 "playable in browser", "webgl")
_NOVELTY_PAT = re.compile(
    r"\b(first|new genre|never before|innovative|reinvents|twist on)\b",
    re.I,
)


def canonicalize_url(url):
    """Return the canonical store key for a source URL."""
    parts = urllib.parse.urlsplit(url.strip())
    scheme = parts.scheme.lower() or "https"
    host = parts.hostname.lower() if parts.hostname else ""
    port = parts.port
    if port and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        host = "%s:%d" % (host, port)
    path = parts.path.rstrip("/") or ""
    params = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    kept = sorted(
        (k, v) for k, v in params
        if k.lower() not in TRACKING_PARAMS
        and not k.lower().startswith("utm_")
    )
    query = urllib.parse.urlencode(kept)
    return urllib.parse.urlunsplit((scheme, host, path, query, ""))


def domain_of(url):
    """Registrable-ish host: lowercase, no port, no leading www.

    Approximation (no PSL dependency): strips one leading 'www.' label.
    Documented so a future change to a real PSL lookup stays compatible.
    """
    host = (urllib.parse.urlsplit(url.strip()).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


_SESSION_PAT = re.compile(r"(?:session[-\s]?)?(\d+)\s*$", re.I)


def parse_session_number(value):
    """Accept 51, '51', 'session-51', 'session 51' -> 51. Raises ValueError."""
    if isinstance(value, int):
        if value < 0:
            raise ValueError("session number must be >= 0: %r" % (value,))
        return value
    m = _SESSION_PAT.search(str(value).strip())
    if not m:
        raise ValueError("unparseable session number: %r" % (value,))
    return int(m.group(1))


def load_store(path):
    """Load the seen-sources store. Missing file -> {} (first-run behavior)."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        raise ValueError("store must be a JSON object: %s" % path)
    return data


def save_store(path, store):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2, sort_keys=True)
        fh.write("\n")


def session_of_record(record):
    """Session number a store record was first seen in, or None."""
    try:
        return parse_session_number(record.get("session", ""))
    except (ValueError, TypeError):
        return None


def exclusion_reason(canonical_url, domain, store, current_session):
    """Return a reason string if excluded, else None. URL tier is permanent;
    domain tier lapses after reuse_cooldown_sessions sessions."""
    if canonical_url in store:
        return "url-seen"
    for record in store.values():
        if not isinstance(record, dict):
            continue
        if record.get("domain", "").lower() != domain:
            continue
        first = session_of_record(record)
        if first is None:
            return "domain-seen"  # unparseable session: fail closed
        cooldown = record.get(
            "reuse_cooldown_sessions", DEFAULT_COOLDOWN_SESSIONS)
        try:
            cooldown = int(cooldown)
        except (TypeError, ValueError):
            cooldown = DEFAULT_COOLDOWN_SESSIONS
        if current_session - first <= cooldown:
            return "domain-cooldown"
    return None


def score_candidate(candidate):
    """Score a candidate dict. Returns (total, features).

    Scored text is title + snippet. Deterministic: same input, same score.
    """
    text = "%s %s" % (candidate.get("title", ""),
                      candidate.get("snippet", ""))
    features = {}
    recency = 0
    if "2026" in text:
        recency += 2
    if _RECENCY_PAT.search(text):
        recency += 1
    features["recency"] = min(recency, 3)
    evidence = 0
    if _EVIDENCE_NUM_PAT.search(text):
        evidence += 2
    if _EVIDENCE_WORD_PAT.search(text):
        evidence += 1
    features["evidence"] = min(evidence, 3)
    lowered = text.lower()
    features["web_fit"] = min(
        sum(1 for term in _WEBFIT_TERMS if term in lowered), 3)
    features["novelty"] = 1 if _NOVELTY_PAT.search(text) else 0
    return sum(features.values()), features


def validate_idea(idea):
    """Validate a HotGameIdea record per the section-3 schema. Returns a
    list of problem strings; empty means valid."""
    problems = []
    for field in HOT_IDEA_REQUIRED:
        value = idea.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append("missing or empty: %s" % field)
    url = idea.get("source_url", "")
    if isinstance(url, str) and url:
        try:
            parts = urllib.parse.urlsplit(url)
            if parts.scheme not in ("http", "https") or not parts.hostname:
                problems.append("source_url is not an http(s) URI")
        except ValueError:
            problems.append("source_url is not a valid URI")
    stamp = idea.get("retrieved_at", "")
    if isinstance(stamp, str) and stamp:
        try:
            datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError:
            problems.append("retrieved_at is not RFC 3339")
    return problems


def make_idea(candidate, retrieved_at):
    """Build a HotGameIdea record from an agent-authored candidate."""
    url = canonicalize_url(candidate["url"])
    return {
        "title": candidate["idea_title"],
        "source_url": url,
        "source_domain": domain_of(url),
        "why_hot": candidate["why_hot"],
        "core_mechanic": candidate["core_mechanic"],
        "audience": candidate["audience"],
        "monetization": candidate["monetization"],
        "retrieved_at": retrieved_at,
    }


class TooFewIdeasError(Exception):
    pass


def select_top_ideas(candidates, store, current_session, retrieved_at,
                     limit=3):
    """Filter excluded, rank, return (ideas, excluded, scored).

    ideas: exactly `limit` validated HotGameIdea records, hottest first.
    excluded: [(candidate, reason)] for audit.
    scored: [(score, canonical_url, candidate)] full ranking, best first.
    Raises TooFewIdeasError when fewer than `limit` candidates survive.
    """
    current_session = parse_session_number(current_session)
    eligible = []
    excluded = []
    for candidate in candidates:
        url = canonicalize_url(candidate["url"])
        reason = exclusion_reason(url, domain_of(url), store,
                                  current_session)
        if reason is not None:
            excluded.append((candidate, reason))
            continue
        score, features = score_candidate(candidate)
        eligible.append((score, url, candidate, features))
    eligible.sort(key=lambda row: (-row[0], row[1]))
    if len(eligible) < limit:
        raise TooFewIdeasError(
            "only %d of %d candidates survive exclusion; "
            "broaden queries and retry" % (len(eligible), limit))
    ideas = []
    for score, url, candidate, _features in eligible[:limit]:
        idea = make_idea(candidate, retrieved_at)
        problems = validate_idea(idea)
        if problems:
            raise ValueError("invalid idea for %s: %s" % (url, problems))
        ideas.append(idea)
    scored = [(score, url, cand) for score, url, cand, _f in eligible]
    return ideas, excluded, scored


def record_sources(store, ideas, session_label, date_str=None,
                   cooldown=DEFAULT_COOLDOWN_SESSIONS):
    """Append the used sources to the store. Returns the updated store."""
    if date_str is None:
        date_str = datetime.datetime.now(
            datetime.timezone.utc).date().isoformat()
    store = copy.deepcopy(store)
    for idea in ideas:
        store[idea["source_url"]] = {
            "domain": idea["source_domain"],
            "first_seen": date_str,
            "session": session_label,
            "title_used": idea["why_hot"][:80],
            "sourced_idea": idea["title"],
            "reuse_cooldown_sessions": cooldown,
        }
    return store


def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z")


def run(candidates, store_path, current_session, session_label=None,
        date_str=None, limit=3, retrieved_at=None):
    """Full run: load store, select top ideas, record sources, save store."""
    store = load_store(store_path)
    retrieved_at = retrieved_at or utc_now_iso()
    ideas, excluded, scored = select_top_ideas(
        candidates, store, current_session, retrieved_at, limit)
    label = session_label or ("session-%d" % parse_session_number(
        current_session))
    save_store(store_path,
               record_sources(store, ideas, label, date_str))
    return ideas, excluded, scored


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Select top-3 hot web game ideas with source exclusion.")
    parser.add_argument("--candidates", required=True,
                        help="JSON file: list of candidate dicts")
    parser.add_argument("--store", required=True,
                        help="seen-sources store JSON path")
    parser.add_argument("--session", required=True,
                        help="current session number (e.g. 51, session-51)")
    parser.add_argument("--session-label", default=None)
    parser.add_argument("--date", default=None,
                        help="first_seen date ISO (default: today UTC)")
    parser.add_argument("--out", required=True,
                        help="output JSON file for the idea records")
    args = parser.parse_args(argv)
    with open(args.candidates, encoding="utf-8") as fh:
        candidates = json.load(fh)
    if isinstance(candidates, dict) and isinstance(
            candidates.get("candidates"), list):
        candidates = candidates["candidates"]
    if not isinstance(candidates, list):
        print("error: candidates file must hold a list", file=sys.stderr)
        return 2
    try:
        ideas, _excluded, _scored = run(
            candidates, args.store, args.session,
            session_label=args.session_label, date_str=args.date)
    except TooFewIdeasError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(ideas, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %d ideas to %s" % (len(ideas), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
