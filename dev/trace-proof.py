#!/usr/bin/env python3
"""TRACE proof harness v2 (Story 172, Session 74).

Runs under:
    env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/trace-proof.py

Self-heal: at startup the harness re-execs itself under the team venv python
so the browser leg reaches PASS even when launched with the system python3
(which has no playwright). Guarded by FLAMBEee_TRACE_REEXEC, never loops.

Six legs (design-handoff Section 2.1, all normative):
  1. Exhaustive 49-cell mirror proof (primary): for each interior START cell,
     v2 EXIT via farthest-corner argmax, manhattan >= 6, EXIT != START, all 3
     skeleton cells disjoint from both. 49/49 required. Plus a full-triple
     sweep over first-D-per-cell derivations covering all 49 START cells.
  2. v1/v2 boundary: D=20784 derives the exact v1 triple, D=20785 derives the
     exact v2 triple, plus center day D=20901 giving (4,4) -> (1,1).
  3. Determinism 200/200: 200 seeded strokes forged twice, byte-identical.
  4. Reachability 200/200: D = 20785 + i, v2 triple, seeded synthetic stroke
     plus RING and CROSS fixtures, BFS START to EXIT within 80 moves.
  5. RED anchor: the distance assertion run against the 5d4a7a9 tree (old
     point-reflection fallback) must exit RED 2 naming the fallback.
     Full-run mode verifies the RED in-process (expected-RED check) and
     still exits 0 when every leg is green. --red-anchor (alias --leg red)
     runs the RED leg alone and exits 2.
  6. Browser leg: headless Chromium loads the ACTUAL page
     website/games/trace.html (never the mirror) and reads the derived
     triple by JS evaluation for today D and center day D=20901, asserting
     page triple equals the mirror v2 triple with distance >= 6.

Exit codes: 0 PASS, 1 FAIL, 2 RED (red-anchor mode), 3 SKIP (anchor commit
missing, or browser binary missing while mirror legs still gate).

File ownership: dev/trace-proof.py, entire file. No website bytes.
"""

import bisect
import json
import math
import os
import socket
import subprocess
import sys
import time
import urllib.request
from collections import deque
from pathlib import Path

# Self-heal re-exec: run the whole harness under the team venv python so
# the browser leg has playwright even when launched with system python3.
# Guarded by FLAMBEee_TRACE_REEXEC so it never loops; missing venv python
# or a failed re-exec falls through to the current behaviour.
_TEAM_VENV_PY = "/home/jake/.hermes/flambeee/.venv/bin/python"
if (not os.environ.get("FLAMBEee_TRACE_REEXEC")
        and Path(_TEAM_VENV_PY).is_file()):
    try:
        _reexec_env = os.environ.copy()
        _reexec_env.pop("PYTHONPATH", None)
        _reexec_env["FLAMBEee_TRACE_REEXEC"] = "1"
        os.execve(_TEAM_VENV_PY, [_TEAM_VENV_PY] + sys.argv,
                  _reexec_env)
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Tuning constants (design-handoff 2.3, all live here).
# ---------------------------------------------------------------------------
PROOF_CELLS = 49
DETERMINISM_RUNS = 200
REACHABILITY_RUNS = 200
V1_DAY = 20784
V2_DAY = 20785
ANCHOR_COMMIT = "5d4a7a9"
BROWSER_MIN_DAYS = 2

GRID = 9
FIELD_INTERNAL_PX = 324
CELL_PX = 36
RESAMPLE_STEP_PX = 2
MIN_STROKE_PX = 108
MIN_CELLS = 3
MOVE_LIMIT = 80
MANHATTAN_MIN = 6          # amended floor (contract Section 0)
V1_MANHATTAN_MIN = 8       # frozen v1 floor, D <= V1_DAY only
MAX_EXIT_DRAWS = 50
V2_CUTOFF_DAY = 20785      # v2 applies from D >= 20785
CORNERS = [(1, 1), (1, 7), (7, 1), (7, 7)]  # fixed order, first wins ties

CENTER_DAY = 20901         # first center-START v2 day (parent-verified)
CENTER_START = (4, 4)
CENTER_EXIT = (1, 1)

# Exact parent-verified triples (binding ground truth, 2026-11-27).
EXP_V1_20784 = ((6, 2), (3, 7), [(5, 5), (5, 6), (5, 7)])
EXP_V2_20785 = ((7, 6), (4, 1), [(4, 2), (4, 3), (4, 4)])

FIXED_START = (1, 1)
FIXED_EXIT = (7, 7)
FIXED_SKELETON = [(4, 3), (4, 4), (4, 5)]

GAME_REL = Path("website/games/trace.html")

CHECKS = []  # (name, passed: bool, detail: str)


def record(name, passed, detail=""):
    CHECKS.append((name, bool(passed), detail))
    return passed


def repo_root():
    # dev/trace-proof.py -> repo root is the parent of dev/.
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Normative PRNG (mulberry32, unsigned 32-bit wrap; matches the page).
# ---------------------------------------------------------------------------
def mulberry32(seed):
    state = seed & 0xFFFFFFFF

    def nxt():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
        t ^= t + ((t ^ (t >> 7)) * (t | 61) & 0xFFFFFFFF) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return nxt


# ---------------------------------------------------------------------------
# Day derivation mirrors (contract 1.1, normative v2 algorithm).
# ---------------------------------------------------------------------------
def _draw_interior(rng):
    return (1 + int(rng() * 7), 1 + int(rng() * 7))


def _draw_skeleton(rng, start, exit_cell):
    skr = 1 + int(rng() * 7)
    skc = 1 + int(rng() * 5)
    bar = [(skr, skc + i) for i in range(3)]
    guard = 0
    while (any(cell == start or cell == exit_cell for cell in bar)
           and guard < 16):
        skr = (skr % 7) + 1
        bar = [(skr, skc + i) for i in range(3)]
        guard += 1
    return bar


def farthest_corner(start):
    """First corner with maximal manhattan distance (fixed order)."""
    best = None
    best_d = -1
    for corner in CORNERS:
        d = abs(start[0] - corner[0]) + abs(start[1] - corner[1])
        if d > best_d:
            best_d = d
            best = corner
    return best


def max_cell_distance(start):
    """Max manhattan distance from start over the 49 interior cells."""
    return max(abs(start[0] - r) + abs(start[1] - c)
               for r in range(1, 8) for c in range(1, 8))


def derive_v1(day):
    """Frozen v1 derivation (byte-identical to 5d4a7a9 for D <= 20784)."""
    rng = mulberry32(day)
    start = _draw_interior(rng)
    exit_cell = _draw_interior(rng)
    draws = 1
    while (abs(start[0] - exit_cell[0]) + abs(start[1] - exit_cell[1])
           < V1_MANHATTAN_MIN and draws < MAX_EXIT_DRAWS):
        exit_cell = _draw_interior(rng)
        draws += 1
    if (abs(start[0] - exit_cell[0]) + abs(start[1] - exit_cell[1])
            < V1_MANHATTAN_MIN):
        fb = (8 - start[0], 8 - start[1])  # point-reflection fallback
        exit_cell = (1, 7) if fb == start else fb
    bar = _draw_skeleton(rng, start, exit_cell)
    return start, exit_cell, bar, draws


def derive_v2(day):
    """Normative v2 derivation (contract 1.1, byte-matches the v2 page).

    START uses the same two rng calls as v1. EXIT gets one initial draw
    exactly as v1; on the five center cells (maxCellDistance < 8) the
    50-draw loop is skipped (0 loop draws) and EXIT is the farthest
    corner directly, discarding the initial draw. Otherwise the loop runs
    at the floor-6 threshold with the corner as exhaustion fallback.
    The skeleton follows from the same stream (skR then skC, row guard).
    Returns (start, exit, bar, draws) with draws = total EXIT draws.
    """
    rng = mulberry32(day)
    start = _draw_interior(rng)
    exit_cell = _draw_interior(rng)  # initial draw, exactly as v1
    draws = 1
    if max_cell_distance(start) < V1_MANHATTAN_MIN:
        exit_cell = farthest_corner(start)  # precheck: loop skipped
    else:
        while (abs(start[0] - exit_cell[0]) + abs(start[1] - exit_cell[1])
               < MANHATTAN_MIN and draws < MAX_EXIT_DRAWS):
            exit_cell = _draw_interior(rng)
            draws += 1
        if (abs(start[0] - exit_cell[0]) + abs(start[1] - exit_cell[1])
                < MANHATTAN_MIN):
            exit_cell = farthest_corner(start)
    bar = _draw_skeleton(rng, start, exit_cell)
    return start, exit_cell, bar, draws


def derive(day):
    """Cutoff derivation: v1 for D <= 20784, v2 for D >= 20785."""
    if day <= V1_DAY:
        return derive_v1(day)
    return derive_v2(day)


def manh(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ---------------------------------------------------------------------------
# THE reference forge (unchanged from Session 73; steps 1-5 of the contract).
# ---------------------------------------------------------------------------
def forge_trace(strokes, start, exit_cell, skeleton):
    player_cells = set()
    ink_len_px = 0.0
    for pts in strokes:
        rs = resample_trace(pts, RESAMPLE_STEP_PX)
        for (x0, y0), (x1, y1) in zip(rs, rs[1:]):
            ink_len_px += math.hypot(x1 - x0, y1 - y0)
        for (x, y) in rs:
            col = int(math.floor(x / CELL_PX))
            row = int(math.floor(y / CELL_PX))
            col = min(GRID - 1, max(0, col))
            row = min(GRID - 1, max(0, row))
            player_cells.add((row, col))
    walls = set()
    for r in range(GRID):
        for c in range(GRID):
            if r == 0 or c == 0 or r == GRID - 1 or c == GRID - 1:
                walls.add((r, c))
    walls |= set(skeleton)
    walls |= player_cells
    walls.discard(start)
    walls.discard(exit_cell)
    floor = _floor_cells(walls)
    path = _bfs_path(floor, start, exit_cell)
    stitched = False
    if path is None:
        r0, c0 = start
        r1, c1 = exit_cell
        for c in range(min(c0, c1), max(c0, c1) + 1):
            walls.discard((r0, c))
        for r in range(min(r0, r1), max(r0, r1) + 1):
            walls.discard((r, c1))
        stitched = True
        floor = _floor_cells(walls)
        path = _bfs_path(floor, start, exit_cell)
    return {
        "walls": walls,
        "player_cells": player_cells,
        "ink_len_px": ink_len_px,
        "ink_cells": len(player_cells),
        "stitched": stitched,
        "reachable": path is not None,
        "moves": None if path is None else len(path) - 1,
        "path": path,
    }


def resample_trace(points, step=RESAMPLE_STEP_PX):
    pts = [(float(x), float(y)) for (x, y) in points]
    if len(pts) < 2:
        return list(pts)
    cum = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(x1 - x0, y1 - y0))
    total = cum[-1]
    if total <= 0.0:
        return [pts[0], pts[-1]]
    n = len(pts)
    out = []
    target = 0.0
    while target < total:
        k = bisect.bisect_right(cum, target, 0, n) - 1
        if k >= n - 1:
            k = n - 2
        span = cum[k + 1] - cum[k]
        t = 0.0 if span <= 0.0 else (target - cum[k]) / span
        out.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * t,
                    pts[k][1] + (pts[k + 1][1] - pts[k][1]) * t))
        target += step
    out.append(pts[-1])
    return out


def _floor_cells(walls):
    return {(r, c) for r in range(GRID) for c in range(GRID)
            if (r, c) not in walls}


def _bfs_path(floor, start, goal):
    if start == goal:
        return [start]
    if start not in floor or goal not in floor:
        return None
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        r, c = cur
        for nb in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if nb not in floor or nb in prev:
                continue
            prev[nb] = cur
            if nb == goal:
                path = [goal]
                while path[-1] != start:
                    path.append(prev[path[-1]])
                return list(reversed(path))
            q.append(nb)
    return None


# ---------------------------------------------------------------------------
# Synthetic strokes (seeded, fixed seeds, rerun-reproducible).
# ---------------------------------------------------------------------------
def synth_stroke(seed, n_points=40, step_min=10.0, step_max=30.0):
    rng = mulberry32(seed)
    x = rng() * FIELD_INTERNAL_PX
    y = rng() * FIELD_INTERNAL_PX
    pts = [(x, y)]
    for _ in range(n_points):
        ang = rng() * 2.0 * math.pi
        ln = step_min + rng() * (step_max - step_min)
        x = min(FIELD_INTERNAL_PX, max(0.0, x + math.cos(ang) * ln))
        y = min(FIELD_INTERNAL_PX, max(0.0, y + math.sin(ang) * ln))
        pts.append((x, y))
    return pts


def boundary_stroke(seed, n_points=30):
    """Adversarial: points within 0.5 px of a cell edge."""
    rng = mulberry32(seed)
    k = 1 + int(rng() * 7)
    edge = 36.0 * k
    y = rng() * 100.0
    pts = []
    for _ in range(n_points):
        x = edge + (rng() * 1.0 - 0.5)
        y = min(FIELD_INTERNAL_PX, max(0.0, y + 4.0 + rng() * 8.0))
        pts.append((x, y))
    return pts


def _cell_center(r, c):
    return (c * CELL_PX + CELL_PX / 2.0, r * CELL_PX + CELL_PX / 2.0)


RING_CELLS = [(2, 2), (2, 3), (2, 4), (3, 4), (4, 4), (4, 3), (4, 2), (3, 2)]
CROSS_CELLS = [(3, 4), (4, 4), (5, 4), (4, 4), (4, 3), (4, 4), (4, 5)]


def ring_points():
    return [_cell_center(r, c) for (r, c) in RING_CELLS
            ] + [_cell_center(*RING_CELLS[0])]


def cross_points():
    return [_cell_center(r, c) for (r, c) in CROSS_CELLS]


# ---------------------------------------------------------------------------
# Leg 1: exhaustive 49-cell mirror proof (primary).
# ---------------------------------------------------------------------------
def leg_exhaustive():
    # (a) Pure argmax sweep: every interior START cell maps to a corner
    # with distance >= 6 and EXIT != START.
    bad = []
    worst = 99
    below8 = []
    for r in range(1, 8):
        for c in range(1, 8):
            s = (r, c)
            e = farthest_corner(s)
            d = manh(s, e)
            worst = min(worst, d)
            if d < 8:
                below8.append(s)
            if d < MANHATTAN_MIN or e == s:
                bad.append((s, e, d))
    # (b) Full-triple sweep: first-D-per-cell derivations from V2_DAY on,
    # asserting the real triple path (loop or precheck plus skeleton).
    first_day = {}
    day = V2_DAY
    while len(first_day) < PROOF_CELLS and day < V2_DAY + 50000:
        s, _, _, _ = derive_v2(day)
        if s not in first_day:
            first_day[s] = day
        day += 1
    missing = [(r, c) for r in range(1, 8) for c in range(1, 8)
               if (r, c) not in first_day]
    triple_bad = []
    for s, dday in sorted(first_day.items()):
        s2, e, bar, _ = derive_v2(dday)
        assert s2 == s
        if manh(s, e) < MANHATTAN_MIN or e == s:
            triple_bad.append((dday, s, e))
        if any(cell == s or cell == e for cell in bar):
            triple_bad.append((dday, s, e, tuple(bar)))
    ok = (not bad) and (not missing) and (not triple_bad)
    ok = ok and worst >= MANHATTAN_MIN and len(first_day) == PROOF_CELLS
    detail = ("%d/49 cells >= 6 (pure argmax min %d; below-8 cells %s); "
              "full-triple sweep over %d first-days%s%s"
              % (PROOF_CELLS - len(bad), worst, sorted(below8),
                 len(first_day),
                 "" if not missing else "; MISSING %s" % (missing,),
                 "" if not triple_bad else "; BAD %s" % (triple_bad,)))
    return record("exhaustive-49", ok, detail)


# ---------------------------------------------------------------------------
# Leg 2: v1/v2 boundary pair plus the distinguishing center day.
# ---------------------------------------------------------------------------
def leg_boundary():
    s1, e1, b1, draws1 = derive(V1_DAY)
    s2, e2, b2, draws2 = derive(V2_DAY)
    sc, ec, bc, drawsc = derive_v2(CENTER_DAY)
    mcd_c = max_cell_distance(sc)
    ok1 = ((s1, e1, b1) == EXP_V1_20784
           and manh(s1, e1) == 8 and draws1 == 7)
    ok2 = ((s2, e2, b2) == EXP_V2_20785
           and manh(s2, e2) == 8 and draws2 == 1)
    # v1 and v2 must agree on the first v2 day (same START calls, loop
    # succeeds at once): catches a START call-count change.
    v1b = derive_v1(V2_DAY)
    ok2 = ok2 and (v1b[0], v1b[1], v1b[2]) == EXP_V2_20785
    okc = (sc == CENTER_START and ec == CENTER_EXIT
           and bc == [(7, 2), (7, 3), (7, 4)]
           and manh(sc, ec) == 6 and drawsc == 1 and mcd_c == 6
           and not any(cell == sc or cell == ec for cell in bc))
    ok = ok1 and ok2 and okc
    detail = ("D=20784 v1 START%s EXIT%s skel%s draws %d manhattan 8; "
              "D=20785 v2 START%s EXIT%s skel%s draws %d manhattan 8 "
              "D=20901 center START%s EXIT%s skel%s "
              "precheck loop skipped maxCellDistance 6 manhattan 6"
              % (s1, e1, b1, draws1, s2, e2, b2, draws2, sc, ec, bc))
    if not ok:
        detail += "  MISMATCH: want 20784 %s, 20785 %s, 20901 %s->%s" % (
            EXP_V1_20784, EXP_V2_20785, CENTER_START, CENTER_EXIT)
    return record("boundary", ok, detail)


# ---------------------------------------------------------------------------
# Leg 3: determinism 200/200 (secondary regression).
# ---------------------------------------------------------------------------
def leg_determinism():
    good = 0
    for i in range(DETERMINISM_RUNS):
        pts = boundary_stroke(i) if i >= 180 else synth_stroke(i)
        a = forge_trace([pts], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        b = forge_trace([pts], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        ja = json.dumps(sorted([list(c) for c in a["walls"]]))
        jb = json.dumps(sorted([list(c) for c in b["walls"]]))
        if ja == jb and a["reachable"]:
            good += 1
        else:
            return record("determinism", False,
                          "seed %d mismatch (boundary %s)" % (i, i >= 180))
    return record("determinism", good == DETERMINISM_RUNS,
                  "%d/200 determinism (seeds 0..179 walk, 180..199 "
                  "near-boundary tie-break)" % good)


# ---------------------------------------------------------------------------
# Leg 4: reachability 200/200 (secondary regression).
# ---------------------------------------------------------------------------
def leg_reachability():
    good = 0
    worst = 0
    stitched_n = 0
    for i in range(REACHABILITY_RUNS):
        day_index = V2_DAY + i
        start, exit_cell, bar, _ = derive(day_index)
        if manh(start, exit_cell) < MANHATTAN_MIN:
            return record("reachability", False,
                          "D %d manhattan %d below floor"
                          % (day_index, manh(start, exit_cell)))
        if any(cell == start or cell == exit_cell for cell in bar):
            return record("reachability", False,
                          "D %d skeleton overlaps START/EXIT" % day_index)
        res = forge_trace([synth_stroke(day_index), ring_points(),
                           cross_points()], start, exit_cell, bar)
        if not res["reachable"]:
            return record("reachability", False,
                          "D %d unreachable after stitch" % day_index)
        if res["moves"] is None or res["moves"] > MOVE_LIMIT:
            return record("reachability", False,
                          "D %d moves %s over MOVE_LIMIT 80"
                          % (day_index, res["moves"]))
        stitched_n += 1 if res["stitched"] else 0
        worst = max(worst, res["moves"])
        good += 1
    return record("reachability", good == REACHABILITY_RUNS,
                  "%d/200 reachability (D 20785..20984, worst %d moves, "
                  "L stitch fired on %d)" % (good, worst, stitched_n))


# ---------------------------------------------------------------------------
# Leg 5: RED anchor against 5d4a7a9 (old point-reflection fallback).
# ---------------------------------------------------------------------------
RED_MARKERS = ["8 - start", "{ r: 1, c: 7 }", "MANHATTAN_MIN: 8"]


def eval_red_anchor(root):
    """Returns (verdict, detail) with verdict in red/skip/fail.

    red: old semantics fail the floor as expected (harness is honest).
    skip: anchor commit object missing (never PASS by omission).
    fail: anchor present but markers absent, or git itself failed.
    """
    try:
        cp = subprocess.run(
            ["git", "cat-file", "-e",
             ANCHOR_COMMIT + "^{commit}"],
            cwd=str(root), stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=30)
    except Exception as exc:
        return ("fail", "git cat-file error: %s" % exc)
    if cp.returncode != 0:
        return ("skip",
                "anchor commit %s not present in this clone; "
                "RED leg cannot run, refusing to PASS by omission"
                % ANCHOR_COMMIT)
    try:
        cp = subprocess.run(
            ["git", "show",
             ANCHOR_COMMIT + ":website/games/trace.html"],
            cwd=str(root), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=30)
    except Exception as exc:
        return ("fail", "git show error: %s" % exc)
    if cp.returncode != 0:
        return ("fail", "git show %s:website/games/trace.html failed: %s"
                % (ANCHOR_COMMIT,
                   cp.stderr.decode("utf-8", "replace")[:200]))
    try:
        old_text = cp.stdout.decode("utf-8")
    except Exception as exc:
        return ("fail", "old page not UTF-8: %s" % exc)
    missing = [m for m in RED_MARKERS if m not in old_text]
    if missing:
        return ("fail", "anchor %s present but old-fallback markers "
                "absent: %s (tree changed?)" % (ANCHOR_COMMIT, missing))
    # Old semantics over all 49 cells: masked fallback exactly as coded,
    # plus the pure unmasked reflection count (the single self-map zero).
    masked_bad8 = 0
    masked_bad6 = 0
    pure_bad8 = 0
    pure_bad6 = 0
    for r in range(1, 8):
        for c in range(1, 8):
            s = (r, c)
            fb = (8 - s[0], 8 - s[1])
            pure_d = manh(s, fb)
            coded = (1, 7) if fb == s else fb
            coded_d = manh(s, coded)
            pure_bad8 += 1 if pure_d < 8 else 0
            pure_bad6 += 1 if pure_d < 6 else 0
            masked_bad8 += 1 if coded_d < 8 else 0
            masked_bad6 += 1 if coded_d < 6 else 0
    floor_holds = (masked_bad6 == 0)
    detail = ("anchor %s markers present %s; old point-reflection "
              "fallback: %d/49 below 8 as-coded (%d/49 unmasked), "
              "%d/49 below 6 as-coded with the {r:1,c:7} mask "
              "(%d/49 unmasked counting the self-map zero); "
              "floor >= 6 %s"
              % (ANCHOR_COMMIT, RED_MARKERS, masked_bad8, pure_bad8,
                 masked_bad6, pure_bad6,
                 "HOLDS??" if floor_holds else "VIOLATED"))
    if floor_holds:
        return ("fail", detail + " -- old code passes the floor, "
                "harness cannot RED it")
    return ("red", detail)


def leg_red_anchor_full(root):
    """Full-run form: expected-RED confirmed in-process; green stays 0."""
    verdict, detail = eval_red_anchor(root)
    if verdict == "red":
        return record("red-anchor", True,
                      "expected RED confirmed in-process: " + detail)
    if verdict == "skip":
        print("SKIP: RED anchor: %s" % detail)
        return None  # signals SKIP 3 to the caller
    return record("red-anchor", False, detail)


# ---------------------------------------------------------------------------
# Leg 6: browser leg (live page, never the mirror).
# ---------------------------------------------------------------------------
BROWSER_PORTS = tuple(range(8941, 8950))


def _pick_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        for port in BROWSER_PORTS:
            try:
                s.bind(("127.0.0.1", port))
                s.close()
                return port
            except OSError:
                continue
        try:
            s.close()
        except Exception:
            pass
        return None
    except Exception:
        return None


def _stop_child(srv):
    try:
        if srv is not None and srv.poll() is None:
            srv.terminate()
            try:
                srv.wait(timeout=5)
            except Exception:
                try:
                    srv.kill()
                except Exception:
                    pass
    except Exception:
        pass


def _port_cleanup(port):
    import shutil
    if shutil.which("fuser"):
        subprocess.run(["fuser", "-k", "%d/tcp" % port],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        # Port-scoped to the http.server this harness started; nothing else.
        subprocess.run(["pkill", "-f", "http[.]server %d" % port],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _today_day():
    return int(time.time() // 86400)


def browser_leg(root):
    """Returns (status, detail): status in pass/fail/skip."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return ("skip", "playwright import failed: %s" % exc)
    game = root / GAME_REL
    if not game.exists():
        return ("fail", "page file missing: %s" % GAME_REL)
    try:
        text = game.read_text()
    except Exception as exc:
        return ("fail", "cannot read page file %s: %s" % (GAME_REL, exc))
    if "deriveTriple" not in text:
        return ("fail", "page lacks deriveTriple; cannot read the triple")
    port = _pick_port()
    if port is None:
        return ("skip", "no free port in 8941-8949 for the local server")
    webdir = root / "website"
    origin = "http://127.0.0.1:%d" % port
    url = origin + "/games/trace.html"
    srv = None
    try:
        srv = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port),
             "--directory", str(webdir)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        return ("fail", "local server spawn failed (port %d): %s"
                % (port, exc))
    started = False
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(url, timeout=1)
            except Exception:
                if srv.poll() is not None:
                    return ("fail", "local server exited code %s (port %d "
                            "busy?)" % (srv.returncode, port))
                time.sleep(0.2)
                continue
            if srv.poll() is None:
                started = True
            break
        if not started:
            return ("fail", "local server did not start (port %d busy?)"
                    % port)
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch(headless=True)
            except Exception as exc:
                msg = str(exc)
                if ("executable" in msg.lower()
                        or "has not been downloaded" in msg.lower()):
                    return ("skip", "browser binary missing: %s" % msg[:200])
                return ("fail", "browser launch failed: %s" % msg[:200])
            try:
                page = browser.new_page()
                try:
                    page.goto(url, wait_until="load", timeout=15000)
                    page.wait_for_timeout(600)
                    days = sorted({_today_day(), CENTER_DAY})
                    notes = []
                    for day in days:
                        try:
                            raw = page.evaluate(
                                "JSON.stringify(deriveTriple(%d))" % day)
                        except Exception as exc:
                            return ("fail", "D %d: JS evaluation of "
                                    "deriveTriple failed: %s" % (day, exc))
                        try:
                            got = json.loads(raw)
                        except Exception as exc:
                            return ("fail", "D %d: page triple not JSON: %s"
                                    % (day, exc))
                        try:
                            ps = (got["start"]["r"], got["start"]["c"])
                            pe = (got["exit"]["r"], got["exit"]["c"])
                            pb = [(c["r"], c["c"]) for c in got["skel"]]
                        except Exception as exc:
                            return ("fail", "D %d: page triple shape bad: "
                                    "%s (%s)" % (day, exc, raw[:160]))
                        ms, me, mb, _ = derive(day)
                        if (ps, pe, pb) != (ms, me, mb):
                            return ("fail", "D %d: page triple "
                                    "START%s EXIT%s skel%s != mirror v2 "
                                    "START%s EXIT%s skel%s"
                                    % (day, ps, pe, pb, ms, me, mb))
                        d = manh(ps, pe)
                        if d < MANHATTAN_MIN:
                            return ("fail", "D %d: page triple distance "
                                    "%d below floor 6" % (day, d))
                        notes.append("D %d page==mirror START%s EXIT%s "
                                     "distance %d" % (day, ps, pe, d))
                finally:
                    try:
                        page.close()
                    except Exception:
                        pass
            finally:
                browser.close()
        detail = ("loaded %s; " % url) + "; ".join(notes)
        return ("pass", detail)
    finally:
        _stop_child(srv)
        _port_cleanup(port)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def _print_checks():
    for name, passed, detail in CHECKS:
        print("CHECK %s: %s (exit %d)%s"
              % (name, "PASS" if passed else "FAIL",
                 0 if passed else 1,
                 " " + detail if detail else ""))


def run_red_mode(root):
    print("TRACE proof harness v2 (Story 172) -- RED-anchor mode "
          "[python: %s]" % sys.executable)
    verdict, detail = eval_red_anchor(root)
    if verdict == "red":
        print("RED: old point-reflection fallback fails the floor "
              "as expected.")
        print("DETAIL: %s" % detail)
        print("RESULT: RED (exit 2)")
        return 2
    if verdict == "skip":
        print("SKIP: RED anchor: %s" % detail)
        print("RESULT: SKIP (exit 3)")
        return 3
    print("FAIL: RED anchor did not go RED: %s" % detail)
    print("RESULT: FAIL (exit 1)")
    return 1


def run_full(root):
    leg_exhaustive()
    leg_boundary()
    leg_determinism()
    leg_reachability()
    mirror_ok = all(passed for (_, passed, _) in CHECKS)
    if not mirror_ok:
        print("TRACE proof harness v2 (Story 172) [python: %s]"
              % sys.executable)
        print("")
        _print_checks()
        print("RESULT: FAIL (exit 1)")
        return 1
    red = leg_red_anchor_full(root)
    if red is None:
        _print_checks()
        print("RESULT: SKIP (exit 3)")
        return 3
    if not red:
        _print_checks()
        print("RESULT: FAIL (exit 1)")
        return 1
    status, detail = browser_leg(root)
    if status == "pass":
        record("browser", True, detail)
    elif status == "skip":
        print("SKIPPED: browser leg (reason: %s)" % detail)
        _print_checks()
        print("Today D=%d, center D=20901; page triple equals "
              "mirror not verified in this environment."
              % _today_day())
        print("RESULT: SKIP (exit 3)")
        return 3
    else:
        record("browser", False, detail)
        _print_checks()
        print("RESULT: FAIL (exit 1)")
        return 1
    print("TRACE proof harness v2 (Story 172) [python: %s]"
          % sys.executable)
    print("mirror: cutoff v1 D<=20784 / v2 D>=20785; argmax (1,1),(1,7),"
          "(7,1),(7,7) first wins; floor 6")
    print("")
    _print_checks()
    print("RESULT: PASS (exit 0)")
    return 0


def main():
    args = sys.argv[1:]
    if args in (["--red-anchor"], ["--leg", "red"]):
        return run_red_mode(repo_root())
    for arg in args:
        print("FAIL: unknown argument %r (want --red-anchor or "
              "--leg red)" % arg)
        print("RESULT: FAIL (exit 1)")
        return 1
    return run_full(repo_root())


if __name__ == "__main__":
    sys.exit(main())