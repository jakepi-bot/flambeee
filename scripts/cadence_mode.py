#!/usr/bin/env python3
"""Session cadence mode: new-game day or legacy-maintenance day.

Implements the rule in docs/cadence-policy.md (Option B, jakebot advisory
2026-11-05): Monday/Wednesday/Friday sessions may build new games or apps;
Tuesday/Thursday/Saturday/Sunday sessions work the legacy maintenance
backlog (docs/legacy-maintenance-backlog.md) only. A broken game or site
jumps the queue on any day.

Stdlib only. Deterministic: the same date always yields the same mode, so
Wave 1 planning cannot drift with the agent's mood. Run from the repo root:

    python3 scripts/cadence_mode.py [--date YYYY-MM-DD]

Exit 0 with `mode: NEW-GAME|LEGACY` plus reason and next-new-game-day lines.
Exit 2 on an unparsable --date.
"""

import argparse
import datetime
import sys

# Monday=0 ... Sunday=6. New-game days are Mon/Wed/Fri per the policy.
NEW_GAME_WEEKDAYS = (0, 2, 4)

WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def session_mode(day):
    """Return 'NEW-GAME' or 'LEGACY' for a datetime.date."""
    return "NEW-GAME" if day.weekday() in NEW_GAME_WEEKDAYS else "LEGACY"


def next_new_game_day(day):
    """Return the next date (on or after `day`) that is a new-game day."""
    probe = day
    for _ in range(7):
        if probe.weekday() in NEW_GAME_WEEKDAYS:
            return probe
        probe += datetime.timedelta(days=1)
    raise AssertionError("no new-game day within a week")


def describe(day):
    mode = session_mode(day)
    name = WEEKDAY_NAMES[day.weekday()]
    if mode == "NEW-GAME":
        reason = (
            "%s is a new-game day (new-game days: Mon/Wed/Fri). "
            "New builds allowed; backlog work still allowed." % name
        )
    else:
        reason = (
            "%s is a legacy-maintenance day (new-game days: Mon/Wed/Fri). "
            "Work docs/legacy-maintenance-backlog.md only; "
            "anything broken jumps the queue." % name
        )
    return mode, reason, next_new_game_day(day)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date",
        default=None,
        help="Session date as YYYY-MM-DD (default: today, local time).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.date is None:
        day = datetime.date.today()
    else:
        try:
            day = datetime.date.fromisoformat(args.date)
        except ValueError:
            print("error: --date must be YYYY-MM-DD, got %r" % args.date,
                  file=sys.stderr)
            return 2
    mode, reason, nxt = describe(day)
    print("mode: %s" % mode)
    print("date: %s (%s)" % (day.isoformat(), WEEKDAY_NAMES[day.weekday()]))
    print("reason: %s" % reason)
    print("next_new_game_day: %s" % nxt.isoformat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
