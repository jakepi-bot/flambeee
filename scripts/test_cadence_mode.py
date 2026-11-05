#!/usr/bin/env python3
"""Unit tests for the session cadence script (scripts/cadence_mode.py).

Stdlib unittest only, so the suite runs with a bare
`python3 scripts/test_cadence_mode.py` from the repo root.
"""

import datetime
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cadence_mode import describe, next_new_game_day, session_mode

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "cadence_mode.py")

# Week of 2026-11-02 (Monday) through 2026-11-08 (Sunday).
MON = datetime.date(2026, 11, 2)
TUE = datetime.date(2026, 11, 3)
WED = datetime.date(2026, 11, 4)
THU = datetime.date(2026, 11, 5)
FRI = datetime.date(2026, 11, 6)
SAT = datetime.date(2026, 11, 7)
SUN = datetime.date(2026, 11, 8)


class TestSessionMode(unittest.TestCase):
    def test_new_game_days(self):
        for day in (MON, WED, FRI):
            self.assertEqual(session_mode(day), "NEW-GAME", day.isoformat())

    def test_legacy_days(self):
        for day in (TUE, THU, SAT, SUN):
            self.assertEqual(session_mode(day), "LEGACY", day.isoformat())

    def test_full_week_split_is_3_new_4_legacy(self):
        modes = [session_mode(MON + datetime.timedelta(days=n))
                 for n in range(7)]
        self.assertEqual(modes.count("NEW-GAME"), 3)
        self.assertEqual(modes.count("LEGACY"), 4)


class TestNextNewGameDay(unittest.TestCase):
    def test_new_game_day_returns_itself(self):
        for day in (MON, WED, FRI):
            self.assertEqual(next_new_game_day(day), day)

    def test_legacy_day_returns_next_new_game_day(self):
        self.assertEqual(next_new_game_day(TUE), WED)
        self.assertEqual(next_new_game_day(THU), FRI)
        self.assertEqual(next_new_game_day(SAT), MON + datetime.timedelta(7))
        self.assertEqual(next_new_game_day(SUN), MON + datetime.timedelta(7))

    def test_describe_lines_agree(self):
        mode, reason, nxt = describe(THU)
        self.assertEqual(mode, "LEGACY")
        self.assertIn("Thursday", reason)
        self.assertEqual(nxt, FRI)


class TestCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, SCRIPT] + list(args),
            capture_output=True,
            text=True,
        )

    def test_cli_legacy_thursday(self):
        proc = self.run_cli("--date", "2026-11-05")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("mode: LEGACY", proc.stdout)
        self.assertIn("next_new_game_day: 2026-11-06", proc.stdout)

    def test_cli_new_game_wednesday(self):
        proc = self.run_cli("--date", "2026-11-04")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("mode: NEW-GAME", proc.stdout)

    def test_cli_defaults_to_today(self):
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        today = datetime.date.today().isoformat()
        self.assertIn("date: %s" % today, proc.stdout)

    def test_cli_bad_date_exits_2(self):
        proc = self.run_cli("--date", "not-a-date")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
