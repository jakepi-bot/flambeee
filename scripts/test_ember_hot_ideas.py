#!/usr/bin/env python3
"""Tests for ember_hot_ideas.py (task t_e2e2cd14).

Stdlib unittest only. Run:
  env -u PYTHONPATH python3 scripts/test_ember_hot_ideas.py
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ember_hot_ideas as ehi

CURRENT = 51


def cand(url, idea_title, title, snippet):
    return {
        "url": url,
        "idea_title": idea_title,
        "title": title,
        "snippet": snippet,
        "why_hot": "why %s" % idea_title,
        "core_mechanic": "loop for %s" % idea_title,
        "audience": "casual players",
        "monetization": "cosmetic shop",
    }


HI = cand(
    "https://fresh-a.dev/hook-harbor",
    "Harbor Idle",
    "New 2026 browser hit",
    "Just launched this month, a 2026 browser game jam winner with "
    "2 million players and a first-of-its-kind twist on fishing. "
    "Playable in browser via HTML5.",
)
OLD_DOMAIN = cand(
    "https://oldblog.net/fresh-2026-piece",
    "Idle Bloom",
    "2026 idle game boom",
    "A 2026 roundup of browser idle games with 500 thousand players "
    "trying the latest releases.",
)
MID = cand(
    "https://fresh-b.dev/cozy-acres",
    "Cozy Acres",
    "Cozy pixel farming sim",
    "A new cozy farming sim gaining players on itch.io, with "
    "thousands of downloads this week.",
)
LO = cand(
    "https://fresh-c.dev/maze-chaser",
    "Maze Chaser",
    "Retro maze chaser",
    "A small retro maze game made over a weekend.",
)
REUSED_URL = cand(
    "https://example.com/cozy-fishing-trend?utm_source=x#frag",
    "Stale Idea",
    "stale",
    "stale 2026 browser game jam viral hit with 9 million players first",
)
SAME_DOMAIN = cand(
    "https://example.com/other-trend",
    "Blocked Idea",
    "blocked",
    "blocked 2026 browser game jam viral hit with 9 million players first",
)


def seeded_store():
    return {
        "https://example.com/cozy-fishing-trend": {
            "domain": "example.com",
            "first_seen": "2026-11-03",
            "session": "session-50",
            "title_used": "rising cozy fishing sims",
            "sourced_idea": "harbor idle",
            "reuse_cooldown_sessions": 4,
        },
        "https://oldblog.net/pixel-trends": {
            "domain": "oldblog.net",
            "first_seen": "2026-10-01",
            "session": "session-44",
            "title_used": "pixel trend roundup",
            "sourced_idea": "pixel painter",
            "reuse_cooldown_sessions": 4,
        },
    }


class CanonicalizationTest(unittest.TestCase):
    def test_tracking_params_fragment_case_slash(self):
        self.assertEqual(
            ehi.canonicalize_url(
                "HTTPS://Example.COM/Path/?utm_source=x&fbclid=abc&b=2&a=1#frag"
            ),
            "https://example.com/Path?a=1&b=2",
        )

    def test_gclid_and_utm_prefix_dropped_others_kept(self):
        self.assertEqual(
            ehi.canonicalize_url(
                "https://example.com/g?utm_campaign=z&gclid=1&q=web+game"),
            "https://example.com/g?q=web+game",
        )

    def test_domain(self):
        self.assertEqual(ehi.domain_of("https://WWW.Example.COM:443/x"),
                         "example.com")
        self.assertEqual(ehi.domain_of("http://sub.example.com:8080/"),
                         "sub.example.com")

    def test_domain_strips_port(self):
        self.assertEqual(ehi.domain_of("http://example.com:8080/x"),
                         "example.com")


class SessionTest(unittest.TestCase):
    def test_parse_variants(self):
        self.assertEqual(ehi.parse_session_number(51), 51)
        self.assertEqual(ehi.parse_session_number("51"), 51)
        self.assertEqual(ehi.parse_session_number("session-51"), 51)
        self.assertEqual(ehi.parse_session_number("Session 51"), 51)

    def test_parse_invalid(self):
        with self.assertRaises(ValueError):
            ehi.parse_session_number("session-xyz")


class ExclusionTest(unittest.TestCase):
    def test_url_tier_is_permanent(self):
        store = seeded_store()
        url = "https://example.com/cozy-fishing-trend"
        self.assertEqual(ehi.exclusion_reason(url, "example.com", store, 51),
                         "url-seen")
        self.assertEqual(ehi.exclusion_reason(url, "example.com", store, 99),
                         "url-seen")

    def test_domain_cooldown_active(self):
        store = seeded_store()
        self.assertEqual(
            ehi.exclusion_reason("https://example.com/other",
                                 "example.com", store, CURRENT),
            "domain-cooldown")

    def test_domain_cooldown_lapses(self):
        store = seeded_store()
        # 55 - 50 = 5 > 4: domain eligible again with a fresh URL.
        self.assertIsNone(
            ehi.exclusion_reason("https://example.com/other",
                                 "example.com", store, 55))

    def test_old_domain_eligible_but_old_url_not(self):
        store = seeded_store()
        self.assertIsNone(
            ehi.exclusion_reason("https://oldblog.net/fresh-2026-piece",
                                 "oldblog.net", store, CURRENT))
        self.assertEqual(
            ehi.exclusion_reason("https://oldblog.net/pixel-trends",
                                 "oldblog.net", store, CURRENT),
            "url-seen")

    def test_unparseable_session_fails_closed(self):
        store = {"https://x.test/a": {"domain": "x.test",
                                      "session": "???",
                                      "reuse_cooldown_sessions": 4}}
        self.assertEqual(ehi.exclusion_reason("https://x.test/b", "x.test",
                                              store, CURRENT),
                         "domain-seen")

    def test_empty_history_excludes_nothing(self):
        for cand_ in (HI, MID, LO):
            url = ehi.canonicalize_url(cand_["url"])
            self.assertIsNone(ehi.exclusion_reason(url, ehi.domain_of(url),
                                                  {}, CURRENT))

    def test_missing_store_file_is_empty(self):
        self.assertEqual(ehi.load_store("/nonexistent/store.json"), {})


class RankingTest(unittest.TestCase):
    def test_scores_separate(self):
        hi, _ = ehi.score_candidate(HI)
        old, _ = ehi.score_candidate(OLD_DOMAIN)
        mid, _ = ehi.score_candidate(MID)
        lo, _ = ehi.score_candidate(LO)
        self.assertTrue(hi > old > mid > lo,
                        (hi, old, mid, lo))

    def test_deterministic_tiebreak(self):
        a = cand("https://b.test/x", "B", "t", "plain words here")
        b = cand("https://a.test/x", "A", "t", "plain words here")
        _ideas, _ex, scored = ehi.select_top_ideas(
            [a, b,
             cand("https://c.test/x", "C", "t",
                  "2026 browser game jam viral 5 million first"),
             cand("https://d.test/x", "D", "t",
                  "2026 browser game jam viral 5 million first debut")],
            {}, CURRENT, "2026-11-04T00:00:00Z", limit=4)
        urls = [u for _s, u, _c in scored]
        self.assertEqual(urls, sorted(urls,
                                      key=lambda u: (-dict(
                                          (u2, s) for s, u2, _c in scored)[u],
                                          u)))


class SelectionTest(unittest.TestCase):
    def test_seeded_history_yields_exactly_three(self):
        ideas, excluded, _scored = ehi.select_top_ideas(
            [REUSED_URL, SAME_DOMAIN, HI, OLD_DOMAIN, MID, LO],
            seeded_store(), CURRENT, "2026-11-04T00:00:00Z")
        self.assertEqual(len(ideas), 3)
        self.assertEqual([i["title"] for i in ideas],
                         ["Harbor Idle", "Idle Bloom", "Cozy Acres"])
        reasons = dict((c["idea_title"], r) for c, r in excluded)
        self.assertEqual(reasons,
                         {"Stale Idea": "url-seen",
                          "Blocked Idea": "domain-cooldown"})
        seen_urls = set(seeded_store())
        for idea in ideas:
            self.assertNotIn(idea["source_url"], seen_urls)
            self.assertNotEqual(idea["source_domain"], "example.com")
            self.assertEqual(ehi.validate_idea(idea), [])

    def test_all_schema_fields_populated(self):
        ideas, _, _ = ehi.select_top_ideas(
            [HI, OLD_DOMAIN, MID, LO], {}, CURRENT, "2026-11-04T00:00:00Z")
        self.assertEqual(len(ideas), 3)
        for idea in ideas:
            self.assertEqual(set(idea), set(ehi.HOT_IDEA_REQUIRED))
            self.assertEqual(ehi.validate_idea(idea), [])

    def test_empty_history_still_returns_three(self):
        ideas, excluded, _ = ehi.select_top_ideas(
            [HI, OLD_DOMAIN, MID, LO], {}, CURRENT, "2026-11-04T00:00:00Z")
        self.assertEqual(len(ideas), 3)
        self.assertEqual(excluded, [])

    def test_too_few_raises(self):
        with self.assertRaises(ehi.TooFewIdeasError):
            ehi.select_top_ideas([REUSED_URL, SAME_DOMAIN], seeded_store(),
                                 CURRENT, "2026-11-04T00:00:00Z")

    def test_record_back_blocks_reuse(self):
        store = seeded_store()
        ideas, _, _ = ehi.select_top_ideas(
            [HI, OLD_DOMAIN, MID, LO], store, CURRENT, "2026-11-04T00:00:00Z")
        updated = ehi.record_sources(store, ideas, "session-51",
                                     date_str="2026-11-04")
        self.assertEqual(len(updated), len(store) + 3)
        for idea in ideas:
            rec = updated[idea["source_url"]]
            self.assertEqual(rec["domain"], idea["source_domain"])
            self.assertEqual(rec["session"], "session-51")
            self.assertEqual(rec["sourced_idea"], idea["title"])
            self.assertEqual(rec["reuse_cooldown_sessions"], 4)
        # Original store untouched; second run starves: only LO is fresh.
        self.assertEqual(len(store), 2)
        with self.assertRaises(ehi.TooFewIdeasError):
            ehi.select_top_ideas([HI, OLD_DOMAIN, MID, LO], updated,
                                 CURRENT, "2026-11-04T00:00:00Z")

    def test_validate_catches_problems(self):
        ideas, _, _ = ehi.select_top_ideas(
            [HI, OLD_DOMAIN, MID], {}, CURRENT, "2026-11-04T00:00:00Z")
        bad = dict(ideas[0])
        del bad["audience"]
        self.assertTrue(any("audience" in p
                            for p in ehi.validate_idea(bad)))
        bad = dict(ideas[0], source_url="not a url")
        self.assertTrue(any("source_url" in p
                            for p in ehi.validate_idea(bad)))
        bad = dict(ideas[0], retrieved_at="yesterday")
        self.assertTrue(any("retrieved_at" in p
                            for p in ehi.validate_idea(bad)))


class RunIntegrationTest(unittest.TestCase):
    def test_run_writes_ideas_and_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            store_path = os.path.join(tmp, "seen.json")
            out_path = os.path.join(tmp, "ideas.json")
            with open(store_path, "w", encoding="utf-8") as fh:
                json.dump(seeded_store(), fh)
            rc = ehi.main(["--candidates", self._write_cands(tmp),
                           "--store", store_path,
                           "--session", "session-51",
                           "--out", out_path])
            self.assertEqual(rc, 0)
            with open(out_path, encoding="utf-8") as fh:
                ideas = json.load(fh)
            self.assertEqual(len(ideas), 3)
            store = ehi.load_store(store_path)
            self.assertEqual(len(store), 2 + 3)

    def test_run_exits_nonzero_when_starved(self):
        with tempfile.TemporaryDirectory() as tmp:
            store_path = os.path.join(tmp, "seen.json")
            with open(store_path, "w", encoding="utf-8") as fh:
                json.dump(seeded_store(), fh)
            cands = os.path.join(tmp, "c.json")
            with open(cands, "w", encoding="utf-8") as fh:
                json.dump([REUSED_URL, SAME_DOMAIN], fh)
            rc = ehi.main(["--candidates", cands, "--store", store_path,
                           "--session", "51",
                           "--out", os.path.join(tmp, "o.json")])
            self.assertEqual(rc, 2)

    def test_run_accepts_candidates_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            store_path = os.path.join(tmp, "seen.json")
            with open(store_path, "w", encoding="utf-8") as fh:
                json.dump({}, fh)
            cands = os.path.join(tmp, "c.json")
            with open(cands, "w", encoding="utf-8") as fh:
                json.dump({"candidates": [HI, OLD_DOMAIN, MID]}, fh)
            out = os.path.join(tmp, "o.json")
            self.assertEqual(ehi.main(["--candidates", cands,
                                       "--store", store_path,
                                       "--session", "51",
                                       "--out", out]), 0)
            with open(out, encoding="utf-8") as fh:
                self.assertEqual(len(json.load(fh)), 3)

    def _write_cands(self, tmp):
        path = os.path.join(tmp, "cands.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([REUSED_URL, SAME_DOMAIN, HI, OLD_DOMAIN, MID, LO],
                      fh)
        return path


if __name__ == "__main__":
    unittest.main(verbosity=2)
