#!/usr/bin/env python3
"""Unit tests for the Ember inversion stage (scripts/ember_invert.py).

Uses the sample top-three hot-idea input in
scripts/ember_invert_sample.json. Stdlib unittest only, so the suite runs
with a bare `python3 scripts/test_ember_invert.py`.
"""

import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ember_invert
from ember_invert import (
    CONTRAST_MARKERS,
    INVERSION_AXES,
    INVERTED_CONCEPT_REQUIRED,
    invert_idea,
    invert_ideas,
    overlap_ratio,
    validate_concept,
)

SAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "ember_invert_sample.json")


def load_sample():
    with open(SAMPLE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def source_text_of(idea):
    return "%s %s %s %s" % (idea["title"], idea["core_mechanic"],
                            idea["why_hot"], idea["audience"])


class InversionTest(unittest.TestCase):
    def setUp(self):
        self.ideas = load_sample()

    # -- acceptance: sample top-three in, three opposed concepts out -----

    def test_sample_produces_three_valid_concepts(self):
        concepts = invert_ideas(self.ideas)
        self.assertEqual(len(concepts), 3)
        for concept in concepts:
            self.assertEqual(validate_concept(concept, self.ideas), [])

    def test_schema_fields_exact(self):
        for concept in invert_ideas(self.ideas):
            self.assertEqual(set(concept.keys()),
                             set(INVERTED_CONCEPT_REQUIRED))
            for field in INVERTED_CONCEPT_REQUIRED:
                self.assertIsInstance(concept[field], str)
                self.assertTrue(concept[field].strip(), field)

    def test_source_linkage_one_to_one(self):
        concepts = invert_ideas(self.ideas)
        self.assertEqual(
            sorted(c["source_idea_title"] for c in concepts),
            sorted(i["title"] for i in self.ideas))

    def test_axes_valid_and_distinct(self):
        concepts = invert_ideas(self.ideas)
        axes = [c["inversion_axis"] for c in concepts]
        for axis in axes:
            self.assertIn(axis, INVERSION_AXES)
        self.assertEqual(len(set(axes)), 3)

    def test_titles_distinct_and_opposed(self):
        concepts = invert_ideas(self.ideas)
        inverted = [c["inverted_title"] for c in concepts]
        sources = [i["title"] for i in self.ideas]
        self.assertEqual(len(set(t.lower() for t in inverted)), 3)
        for title in inverted:
            self.assertLessEqual(len(title.split()), 8)
            for source in sources:
                self.assertNotEqual(title.strip().lower(),
                                    source.strip().lower())

    def test_explicit_flip_statement(self):
        for concept in invert_ideas(self.ideas):
            lowered = concept["why_it_is_opposite"].lower()
            self.assertTrue(
                any(m in lowered for m in CONTRAST_MARKERS),
                concept["why_it_is_opposite"])

    def test_not_mere_rewording(self):
        for concept in invert_ideas(self.ideas):
            source = next(i for i in self.ideas
                          if i["title"] == concept["source_idea_title"])
            ratio = overlap_ratio(
                concept["inverted_title"] + " "
                + concept["concept_summary"],
                source_text_of(source))
            self.assertLess(ratio, ember_invert.MAX_OVERLAP_RATIO)

    def test_summaries_are_sketches_and_experiments_testable(self):
        for concept in invert_ideas(self.ideas):
            sentences = [s for s in re.split(r"[.!?]+",
                                                concept["concept_summary"])
                         if s.strip()]
            self.assertGreaterEqual(len(sentences), 2)
            experiment = concept["first_experiment"].lower()
            self.assertTrue(any(w in experiment
                                for w in ("test", "prototype", "trial",
                                          "measure", "try")),
                            concept["first_experiment"])

    # -- planner coverage: every axis flips on a fitting idea -------------

    def test_all_six_axes_validate(self):
        ideas_by_axis = {
            "mechanic": self.ideas[0],       # catch/grow loop
            "audience": self.ideas[1],        # competitive teens
            "session length": self.ideas[0],  # short daily tides
            "social mode": self.ideas[2],     # co-op dungeon
            "monetization": self.ideas[2],    # one-time purchase
            "theme": self.ideas[1],           # neon/grim
        }
        seen_titles = set()
        for axis, idea in ideas_by_axis.items():
            concept = invert_idea(idea, axis)
            self.assertEqual(concept["inversion_axis"], axis)
            self.assertEqual(validate_concept(concept, self.ideas), [],
                             axis)
            seen_titles.add(concept["inverted_title"])
        self.assertEqual(len(seen_titles), 6)

    def test_mechanic_flips_verb_direction(self):
        concept = invert_idea(self.ideas[0], "mechanic")
        self.assertIn("release", concept["concept_summary"].lower())

    def test_social_mode_removes_the_crowd(self):
        concept = invert_idea(self.ideas[2], "social mode")
        self.assertIn("lonely", concept["inverted_title"].lower())

    def test_monetization_flips_paid_to_free(self):
        concept = invert_idea(self.ideas[2], "monetization")
        self.assertIn("free", concept["inverted_title"].lower())

    def test_monetization_flips_free_to_paid(self):
        concept = invert_idea(self.ideas[0], "monetization")
        self.assertIn("flat-fee", concept["inverted_title"].lower())

    # -- determinism and input contracts -----------------------------------

    def test_deterministic(self):
        self.assertEqual(invert_ideas(self.ideas),
                         invert_ideas(copy.deepcopy(self.ideas)))

    def test_explicit_axes_respected(self):
        axes = ["theme", "mechanic", "audience"]
        concepts = invert_ideas(self.ideas, axes)
        self.assertEqual([c["inversion_axis"] for c in concepts], axes)
        for concept in concepts:
            self.assertEqual(validate_concept(concept, self.ideas), [])

    def test_rejects_wrong_idea_count(self):
        with self.assertRaises(ValueError):
            invert_ideas(self.ideas[:2])
        with self.assertRaises(ValueError):
            invert_ideas(self.ideas + self.ideas[:1])

    def test_rejects_duplicate_axes(self):
        with self.assertRaises(ValueError):
            invert_ideas(self.ideas, ["theme", "theme", "mechanic"])

    def test_rejects_unknown_axis(self):
        with self.assertRaises(ValueError):
            invert_idea(self.ideas[0], "platform")

    # -- validator rejects non-opposite and malformed concepts -------------

    def test_validator_rejects_rewording(self):
        idea = self.ideas[0]
        impostor = {
            "source_idea_title": idea["title"],
            "inverted_title": "Harbor Idle Too",
            "inversion_axis": "mechanic",
            "concept_summary": "Tap to catch fish and grow the harbor "
                               "with casual mobile players daily.",
            "why_it_is_opposite": "It is different because it is new.",
            "first_experiment": "Ship it and see what happens.",
        }
        problems = validate_concept(impostor, self.ideas)
        self.assertTrue(any("rewording" in p or "flip" in p
                            for p in problems), problems)

    def test_validator_rejects_bad_records(self):
        good = invert_idea(self.ideas[0], "theme")
        bad_axis = dict(good, inversion_axis="graphics")
        self.assertTrue(validate_concept(bad_axis, self.ideas))
        bad_source = dict(good, source_idea_title="No Such Game")
        self.assertTrue(any("source_idea_title" in p for p in
                            validate_concept(bad_source, self.ideas)))
        missing = dict(good)
        del missing["first_experiment"]
        self.assertTrue(any("first_experiment" in p for p in
                            validate_concept(missing, self.ideas)))
        extra = dict(good, notes="bonus")
        self.assertTrue(any("unexpected field" in p for p in
                            validate_concept(extra, self.ideas)))
        same_title = dict(good, source_idea_title=good["inverted_title"])
        self.assertTrue(validate_concept(same_title, self.ideas))

    # -- CLI end to end ------------------------------------------------------

    def test_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "concepts.json")
            proc = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "ember_invert.py"),
                 "--ideas", SAMPLE_PATH, "--out", out_path],
                capture_output=True, text=True, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(out_path, encoding="utf-8") as fh:
                concepts = json.load(fh)
            self.assertEqual(len(concepts), 3)
            for concept in concepts:
                self.assertEqual(validate_concept(concept, self.ideas), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
