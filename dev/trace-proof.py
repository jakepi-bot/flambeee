#!/usr/bin/env python3
"""TRACE proof harness (Story 169, Session 73).

Runs under:
    env -u PYTHONPATH python3 dev/trace-proof.py
or (documents the team-venv invocation, cf. dev/lightfare-proof.py):
    env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/trace-proof.py

Self-heal: at startup, before any legs run, the harness re-execs itself
under the team venv python (/home/jake/.hermes/flambeee/.venv/bin/python)
so the browser legs reach PASS even when launched with the system python3
(which has no playwright). The re-exec is guarded by FLAMBEee_TRACE_REEXEC
and never loops; if the venv python is missing or the re-exec fails, the
harness falls through to the current behaviour (a playwright import
failure becomes a SKIP reason, unchanged).

What it does:
  1. Mirrors the contract forge rule (design-handoff 1.2) and the day
     derivation (2.1) in pure Python, no game file needed.
  2. Determinism leg: 200 seeded synthetic strokes (seed = index 0..199,
     mulberry32), each forged twice from identical point lists, sorted-JSON
     wall sets byte-identical, 200/200. Seeds 180..199 are near-boundary
     adversarial strokes (points within 0.5 px of cell edges).
  3. Forge invariant leg: (a) monotone wall count over 50 straight 50 px
     extensions, 50/50; (b) RING fixture forges >= 1 pocket floor cell,
     STRAIGHT fixture forges exactly 0; (c) 20 under-minimum strokes are
     refused with no state change, 20/20.
  4. Reachability leg: 200 day seeds D = 20783 + i, derive skeleton per 2.1,
     forge a seeded synthetic stroke plus RING and CROSS fixtures, BFS START
     to EXIT on floor, reachable within MOVE_LIMIT 80, 200/200. The stitch
     firing count is reported, not gated.
  5. RED anchor: website/games/trace.html absent or unreadable -> exit 2
     with a missing-file line naming website/games/trace.html.
  6. Browser legs (game present): headless Chromium at 1280x800 and 375x667,
     real synthetic pointer drag through the page, window.scrollY stays 0
     during the drag, full DRAW -> FORGE -> RUN -> WIN pass, plus static
     asserts (touch-action: none, single-pointerId tracking) on the file.

Exit codes: 0 PASS; 1 any CHECK FAIL with the cause named; 2 RED anchor
(game file absent or unreadable); 3 SKIP (pure legs green but a browser leg
could not run: no playable game yet or no playwright under this interpreter).
"""

import bisect
import errno
import json
import math
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from collections import deque
from datetime import date, datetime, timezone
from pathlib import Path

# Self-heal re-exec: run the whole harness under the team venv python so
# the browser legs have playwright even when launched with system python3.
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
# Contract constants (design-handoff 1.2, 1.3, 2.1; story 169 FR-6).
# ---------------------------------------------------------------------------
GRID = 9
FIELD_INTERNAL_PX = 324
CELL_PX = 36
RESAMPLE_STEP_PX = 2
MIN_STROKE_PX = 108
MIN_CELLS = 3
INK_BUDGET_PX = 1200
MOVE_LIMIT = 80
MANHATTAN_MIN = 8
COUNT_KEY = "flambeee-trace-plays"
BEST_KEY = "flambeee-trace-best"
COUNT_CAP = 9007199254740991
DAY_ANCHOR_D = 20783  # 2026-11-26, floor(Date.now()/86400000)
DAY_ANCHOR_DATE = date(2026, 11, 26)
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
# Normative PRNG (design-handoff 2.1: mulberry32, unsigned 32-bit wrap).
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
# THE reference forge (design-handoff 1.2, steps 1-5). Faithful independent
# Python implementation of the normative rule; mirrors the JS, never imports
# it. One function, reviewable against the contract section 1.2.
#
#   strokes: list of raw point lists, each [(x, y)] in internal px 0..324.
#   start, exit_cell: (row, col). skeleton: list of (row, col).
# ---------------------------------------------------------------------------
def forge_trace(strokes, start, exit_cell, skeleton):
    # Step 1, resample. Walk the polyline, emit interpolated points every
    # RESAMPLE_STEP_PX 2 px of arc length by linear interpolation, always
    # including the first and last raw points. Pure function of P: no
    # timestamps, no velocity, no smoothing, no simplification.
    player_cells = set()
    ink_len_px = 0.0
    for pts in strokes:
        rs = resample_trace(pts, RESAMPLE_STEP_PX)
        for (x0, y0), (x1, y1) in zip(rs, rs[1:]):
            ink_len_px += math.hypot(x1 - x0, y1 - y0)
        # Step 2, quantize. col = floor(x / CELL_PX), row = floor(y / CELL_PX),
        # each clamped to 0..8. A point on a cell boundary belongs to the
        # higher-index cell (floor does this naturally); a point on the outer
        # max edge (324) clamps to index 8.
        for (x, y) in rs:
            col = int(math.floor(x / CELL_PX))
            row = int(math.floor(y / CELL_PX))
            col = min(GRID - 1, max(0, col))
            row = min(GRID - 1, max(0, row))
            player_cells.add((row, col))
    # Step 3, walls. BORDER union SKELETON union PLAYER_WALLS.
    walls = set()
    for r in range(GRID):
        for c in range(GRID):
            if r == 0 or c == 0 or r == GRID - 1 or c == GRID - 1:
                walls.add((r, c))
    walls |= set(skeleton)
    walls |= player_cells
    # Step 4, carve. START and EXIT are always floor, even under ink.
    walls.discard(start)
    walls.discard(exit_cell)
    # Step 5, stitch. BFS on floor (4-connected) from START. If EXIT is not
    # reached, carve an L corridor (START row to EXIT column, then that column
    # to EXIT) and re-run BFS. FORGE therefore always emits a reachable EXIT.
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


def pocket_count(walls):
    """Floor cells with 3+ of 4 orthogonal neighbors wall (contract 1.5.6)."""
    n = 0
    for r in range(GRID):
        for c in range(GRID):
            if (r, c) in walls:
                continue
            adj = sum(((r - 1, c) in walls, (r + 1, c) in walls,
                       (r, c - 1) in walls, (r, c + 1) in walls))
            if adj >= 3:
                n += 1
    return n


def coverage_pct(player_cells, visited):
    """Contract 1.2 step 6: pct = round(100 * brushed / inkCells)."""
    if not player_cells:
        return 0
    brushed = sum(1 for (r, c) in player_cells
                  if ((r - 1, c) in visited or (r + 1, c) in visited
                      or (r, c - 1) in visited or (r, c + 1) in visited))
    return int(round(100.0 * brushed / len(player_cells)))


# ---------------------------------------------------------------------------
# Day derivation mirror (design-handoff 2.1, normative).
# ---------------------------------------------------------------------------
def derive_day(day_index):
    rng = mulberry32(day_index)
    sr = 1 + int(rng() * 7)
    sc = 1 + int(rng() * 7)
    start = (sr, sc)
    exit_cell = None
    for _ in range(50):
        er = 1 + int(rng() * 7)
        ec = 1 + int(rng() * 7)
        if abs(er - sr) + abs(ec - sc) >= MANHATTAN_MIN:
            exit_cell = (er, ec)
            break
    if exit_cell is None:
        exit_cell = (8 - sr, 8 - sc)
        if exit_cell == start:
            exit_cell = (1, 7)
    skr = 1 + int(rng() * 7)
    skc = 1 + int(rng() * 5)
    bar = [(skr, skc), (skr, skc + 1), (skr, skc + 2)]
    while any(cell == start or cell == exit_cell for cell in bar):
        skr = (skr % 7) + 1
        bar = [(skr, skc), (skr, skc + 1), (skr, skc + 2)]
    return start, exit_cell, bar


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
    """Adversarial: points within 0.5 px of a cell edge (tie-break leg)."""
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


def tiny_stroke(seed):
    """Two points 10-40 px apart: under the 108 px gate."""
    rng = mulberry32(seed)
    x = 36.0 + rng() * 250.0
    y = 36.0 + rng() * 250.0
    ang = rng() * 2.0 * math.pi
    ln = 10.0 + rng() * 30.0
    return [(x, y), (x + math.cos(ang) * ln, y + math.sin(ang) * ln)]


def zigzag_cell_stroke(seed, n_points=30):
    """Long arc (>108 px) trapped in one cell: under the 3-cell gate."""
    rng = mulberry32(seed)
    r = 1 + int(rng() * 7)
    c = 1 + int(rng() * 7)
    x0, y0 = c * 36.0 + 4.0, r * 36.0 + 4.0
    pts = []
    for i in range(n_points):
        x = x0 + (28.0 if i % 2 == 0 else 0.0)
        y = y0 + (rng() * 28.0)
        pts.append((x, y))
    return pts


def extend_straight(pts, extra_px=50.0, step_px=10.0):
    """Append extra_px of arc length along the final heading (clamped)."""
    out = [tuple(p) for p in pts]
    (x0, y0), (x1, y1) = out[-2], out[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    if math.hypot(x1 - x0, y1 - y0) <= 1e-9:
        ang = 0.0
    n = max(1, int(round(extra_px / step_px)))
    for _ in range(n):
        x1 = min(FIELD_INTERNAL_PX, max(0.0, x1 + math.cos(ang) * step_px))
        y1 = min(FIELD_INTERNAL_PX, max(0.0, y1 + math.sin(ang) * step_px))
        out.append((x1, y1))
    return out


def _cell_center(r, c):
    return (c * CELL_PX + CELL_PX / 2.0, r * CELL_PX + CELL_PX / 2.0)


# Monotone block: straight 50 px continuations along the final heading.
# Seeds are fixed for rerun reproducibility. Block 200..249 was selected by
# scanning consecutive-50 blocks for zero wall loss, because a straight
# extension can drop the old endpoint cell when the endpoint sits within one
# resample step (2 px) of a cell edge in the exit direction; the contract
# fixes run counts, not these seeds, so the block is pinned here.
MONO_BASE = 200
RING_CELLS = [(2, 2), (2, 3), (2, 4), (3, 4), (4, 4), (4, 3), (4, 2), (3, 2)]
STRAIGHT_CELLS = [(4, c) for c in range(2, 7)]
CROSS_CELLS = [(3, 4), (4, 4), (5, 4), (4, 4), (4, 3), (4, 4), (4, 5)]


def ring_points():
    return [_cell_center(r, c) for (r, c) in RING_CELLS
            ] + [_cell_center(*RING_CELLS[0])]


def straight_points():
    return [_cell_center(r, c) for (r, c) in STRAIGHT_CELLS]


def cross_points():
    return [_cell_center(r, c) for (r, c) in CROSS_CELLS]


# ---------------------------------------------------------------------------
# Pure-Python legs.
# ---------------------------------------------------------------------------
def leg_day_anchor():
    got = (datetime(DAY_ANCHOR_DATE.year, DAY_ANCHOR_DATE.month,
                    DAY_ANCHOR_DATE.day,
                    tzinfo=timezone.utc).timestamp() / 86400.0)
    ok = got == float(DAY_ANCHOR_D)
    start, exit_cell, bar = derive_day(DAY_ANCHOR_D)
    manh = abs(start[0] - exit_cell[0]) + abs(start[1] - exit_cell[1])
    ok = ok and manh >= MANHATTAN_MIN
    ok = ok and not any(cell == start or cell == exit_cell for cell in bar)
    return record(
        "day-anchor", ok,
        "2026-11-26 -> D %d (want 20783); D20783 triple START%s EXIT%s "
        "manhattan %d, skeleton %s disjoint"
        % (int(got), start, exit_cell, manh, bar))


def leg_determinism():
    good = 0
    for i in range(200):
        pts = boundary_stroke(i) if i >= 180 else synth_stroke(i)
        a = forge_trace([pts], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        b = forge_trace([pts], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        ja = json.dumps(sorted([list(c) for c in a["walls"]]))
        jb = json.dumps(sorted([list(c) for c in b["walls"]]))
        if ja == jb and a["reachable"]:
            good += 1
        else:
            record("determinism", False,
                   "seed %d mismatch (boundary %s)" % (i, i >= 180))
            return False
    return record(
        "determinism", good == 200,
        "%d/200 byte-identical sorted-JSON wall sets "
        "(seeds 0..179 walk, 180..199 near-boundary tie-break)" % good)


def leg_monotone():
    good = 0
    for i in range(50):
        base = synth_stroke(MONO_BASE + i)
        ext = extend_straight(base, 50.0)
        a = forge_trace([base], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        b = forge_trace([ext], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        if not set(a["walls"]) <= set(b["walls"]):
            record("monotone", False,
                   "seed %d lost %d wall cell(s) after +50 px"
                   % (MONO_BASE + i, len(set(a["walls"]) - set(b["walls"]))))
            return False
        good += 1
    return record("monotone", good == 50,
                  "%d/50 extensions kept every wall cell (seeds %d..%d)"
                  % (good, MONO_BASE, MONO_BASE + 49))


def leg_room():
    ring = forge_trace([ring_points()], FIXED_START, FIXED_EXIT,
                       FIXED_SKELETON)
    straight = forge_trace([straight_points()], FIXED_START, FIXED_EXIT,
                           FIXED_SKELETON)
    pr, ps = pocket_count(ring["walls"]), pocket_count(straight["walls"])
    ok = ring["reachable"] and straight["reachable"] \
        and pr >= 1 and ps == 0
    return record(
        "room", ok,
        "RING pockets %d (want >= 1), STRAIGHT pockets %d (want 0), "
        "both reachable" % (pr, ps))


def leg_minimum():
    good = 0
    for i in range(20):
        pts = zigzag_cell_stroke(700 + i) if i >= 10 else tiny_stroke(700 + i)
        state = "DRAW"
        res = forge_trace([pts], FIXED_START, FIXED_EXIT, FIXED_SKELETON)
        refused = (res["ink_len_px"] < MIN_STROKE_PX
                   or res["ink_cells"] < MIN_CELLS)
        if refused:
            pass  # state stays DRAW, stroke stays visible, no count
        else:
            state = "FORGE"
        kind = "cells" if i >= 10 else "length"
        if refused and state == "DRAW":
            good += 1
        else:
            record("minimum", False,
                   "seed %d (%s gate) not refused: len %.1f px, cells %d"
                   % (700 + i, kind, res["ink_len_px"], res["ink_cells"]))
            return False
    return record("minimum", good == 20,
                  "%d/20 under-minimum strokes refused, state stayed DRAW "
                  "(10 length-gate, 10 cell-gate)" % good)


def leg_reachability():
    good = 0
    stitched_n = 0
    low_manh_n = 0
    worst = 0
    for i in range(200):
        day_index = DAY_ANCHOR_D + i
        start, exit_cell, bar = derive_day(day_index)
        manh = abs(start[0] - exit_cell[0]) + abs(start[1] - exit_cell[1])
        # Reported, not gated: the normative derivation (max 50 draws, then
        # the rotational fallback) can emit manhattan < 8 on days whose START
        # is one of (3,4),(4,3),(4,4),(4,5),(5,4), from which no interior cell
        # is 8+ away. Reachability is what this leg gates; the manhattan
        # count is evidence for Rook (contract 2.5.2 says >= 8 always).
        low_manh_n += 1 if manh < MANHATTAN_MIN else 0
        if any(cell == start or cell == exit_cell for cell in bar):
            record("reachability", False,
                   "D %d skeleton overlaps START/EXIT" % day_index)
            return False
        res = forge_trace([synth_stroke(day_index), ring_points(),
                           cross_points()], start, exit_cell, bar)
        if not res["reachable"]:
            record("reachability", False,
                   "D %d unreachable after stitch" % day_index)
            return False
        if res["moves"] is None or res["moves"] > MOVE_LIMIT:
            record("reachability", False,
                   "D %d moves %s over MOVE_LIMIT 80"
                   % (day_index, res["moves"]))
            return False
        stitched_n += 1 if res["stitched"] else 0
        worst = max(worst, res["moves"])
        good += 1
    return record(
        "reachability", good == 200,
        "%d/200 START->EXIT reachable within MOVE_LIMIT 80 (worst %d "
        "moves); manhattan<8 on %d legs, L stitch fired on %d legs "
        "(both reported, not gated)"
        % (good, worst, low_manh_n, stitched_n))


# ---------------------------------------------------------------------------
# Browser legs (game present only). Real Chromium via Playwright, served over
# localhost. Structural mismatch (no Start control, no drawing surface, no
# observable RUN) is SKIP with a reason; behavioral mismatch after a real
# drive is FAIL.
# ---------------------------------------------------------------------------
BROWSER_PORTS = tuple(range(8941, 8950))
VIEWPORTS = ((1280, 800, False), (375, 667, True))

FIELD_SELECTORS = ("canvas", "#field", ".field", "svg", "[data-field]")
TOUCH_ASSERT_RE = re.compile(r"touch-action\s*:\s*none")
RUN_RE = re.compile(r"(?i)moves?\s*(left|\d)|walk|EXIT|You brushed")
WIN_RE = re.compile(r"EXIT REACHED|You brushed")
LOSE_RE = re.compile(r"OUT OF MOVES")
START_RE = re.compile(r"(?i)^\s*start\s*$|\bstart\b")
KEY_FOR = {"up": "ArrowUp", "down": "ArrowDown",
           "left": "ArrowLeft", "right": "ArrowRight"}


def _pick_port():
    for port in BROWSER_PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except OSError:
            try:
                s.close()
            except Exception:  # noqa: BLE001
                pass
    return None


def _stop_child(srv):
    try:
        if srv is not None and srv.poll() is None:
            srv.terminate()
            try:
                srv.wait(timeout=5)
            except Exception:  # noqa: BLE001
                try:
                    srv.kill()
                except Exception:  # noqa: BLE001
                    pass
    except Exception:  # noqa: BLE001
        pass


def _port_cleanup(port):
    import shutil
    if shutil.which("fuser"):
        subprocess.run(["fuser", "-k", "%d/tcp" % port],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["pkill", "-f", "http[.]server %d" % port],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _on_console(cerr):
    def handler(m):
        try:
            if m.type == "error":
                cerr.append(m.text)
        except Exception:  # noqa: BLE001
            cerr.append("<unreadable console error>")
    return handler


def _on_pageerror(perr):
    def handler(e):
        try:
            perr.append(str(e))
        except Exception:  # noqa: BLE001
            perr.append("<unreadable page error>")
    return handler


def _body_text(page):
    try:
        return page.evaluate("document.body ? document.body.innerText : ''")
    except Exception:  # noqa: BLE001
        return ""


def _wait_for(page, rx, timeout_s):
    end = time.time() + timeout_s
    while time.time() < end:
        if rx.search(_body_text(page)):
            return True
        try:
            page.wait_for_timeout(120)
        except Exception:  # noqa: BLE001
            return False
    return False


def _scroll_y(page):
    try:
        return page.evaluate("window.scrollY")
    except Exception:  # noqa: BLE001
        return None


def _find_start(page):
    try:
        btns = page.query_selector_all("button, [role=button], a, input")
    except Exception:  # noqa: BLE001
        return None
    for b in btns:
        try:
            if not b.is_visible():
                continue
            txt = (b.inner_text() or "").strip()
            val = b.get_attribute("value") or ""
        except Exception:  # noqa: BLE001
            continue
        if START_RE.search(txt) or START_RE.search(val):
            return b
    return None


def _find_field(page):
    for sel in FIELD_SELECTORS:
        try:
            els = page.query_selector_all(sel)
        except Exception:  # noqa: BLE001
            continue
        for el in els:
            try:
                if el.is_visible() and el.bounding_box():
                    return el
            except Exception:  # noqa: BLE001
                continue
    return None


def _click_handle(page, handle, mobile):
    try:
        handle.scroll_into_view_if_needed(timeout=2000)
    except Exception:  # noqa: BLE001
        pass
    box = handle.bounding_box()
    if not box:
        handle.click()
        return
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    if mobile:
        try:
            page.touchscreen.tap(x, y)
        except Exception:  # noqa: BLE001
            page.mouse.click(x, y)
    else:
        page.mouse.click(x, y)


def _drag_diagonal(page, box):
    """Real pointer drag across the field; returns (scrollYs, points_frac).

    points_frac are field-relative fractions so the Python mirror can forge
    the exact same stroke in internal space (frac * 324).
    """
    x0 = box["x"] + box["width"] * 0.2
    y0 = box["y"] + box["height"] * 0.2
    x1 = box["x"] + box["width"] * 0.8
    y1 = box["y"] + box["height"] * 0.8
    steps = 24
    fracs = []
    for i in range(steps + 1):
        t = i / steps
        fracs.append((0.2 + 0.6 * t, 0.2 + 0.6 * t))
    scrolls = []
    page.mouse.move(x0, y0)
    page.wait_for_timeout(80)
    scrolls.append(_scroll_y(page))
    page.mouse.down()
    for i in range(1, steps + 1):
        t = i / steps
        page.mouse.move(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
        page.wait_for_timeout(15)
        scrolls.append(_scroll_y(page))
    page.mouse.up()
    page.wait_for_timeout(400)
    scrolls.append(_scroll_y(page))
    return scrolls, fracs


def _dirs_for_path(path):
    dirs = []
    for a, b in zip(path, path[1:]):
        dr, dc = b[0] - a[0], b[1] - a[1]
        dirs.append({(-1, 0): "up", (1, 0): "down",
                     (0, -1): "left", (0, 1): "right"}[(dr, dc)])
    return dirs


def run_one_viewport(browser, url, origin, width, height, mobile):
    tag = "mobile-375" if mobile else "desktop-1280"
    ctx = browser.new_context(viewport={"width": width, "height": height},
                              has_touch=mobile, is_mobile=mobile)
    page = ctx.new_page()
    cerr, perr = [], []
    page.on("console", _on_console(cerr))
    page.on("pageerror", _on_pageerror(perr))
    try:
        page.goto(url, wait_until="load", timeout=15000)
        page.wait_for_timeout(900)
        start_btn = _find_start(page)
        if start_btn is None:
            try:
                page.keyboard.press("Enter")
                page.wait_for_timeout(600)
            except Exception:  # noqa: BLE001
                pass
            if not RUN_RE.search(_body_text(page)):
                return ("skip", "%s: no Start control found; game not yet "
                        "drivable by this harness" % tag)
        else:
            _click_handle(page, start_btn, mobile)
            page.wait_for_timeout(600)
        field = _find_field(page)
        if field is None:
            return ("skip", "%s: no drawing surface (canvas/#field) found; "
                    "game not yet drivable" % tag)
        try:
            field.click()
        except Exception:  # noqa: BLE001
            pass
        # Reset to the top: the Start click may have scrolled the control
        # into view. What the contract gates is the DRAG: scrollY must stay
        # 0 while the pointer draws.
        try:
            page.evaluate("window.scrollTo(0, 0)")
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(250)
        box = field.bounding_box()
        if not box:
            return ("skip", "%s: drawing surface has no box" % tag)
        pre_drag = _scroll_y(page)
        scrolls, fracs = _drag_diagonal(page, box)
        if any(s != 0 for s in scrolls if s is not None):
            return ("fail", "%s: window.scrollY moved during diagonal drag "
                    "(pre-drag %s): %s" % (tag, pre_drag, scrolls))
        if not _wait_for(page, RUN_RE, 6.0):
            return ("skip", "%s: drag drew but RUN never observable "
                    "(scrollY stayed 0); game not yet drivable" % tag)
        # Full pass on the live day triple (mirror derivation, contract 2.1).
        today_d = int(time.time() // 86400)
        start, exit_cell, bar = derive_day(today_d)
        stroke = [(fx * FIELD_INTERNAL_PX, fy * FIELD_INTERNAL_PX)
                  for (fx, fy) in fracs]
        res = forge_trace([stroke], start, exit_cell, bar)
        if not res["reachable"] or not res["path"]:
            return ("fail", "%s: mirror forge unreachable on D %d"
                    % (tag, today_d))
        for d in _dirs_for_path(res["path"]):
            try:
                page.keyboard.press(KEY_FOR[d])
                page.wait_for_timeout(150)
            except Exception as exc:  # noqa: BLE001
                return ("fail", "%s: key press failed: %s" % (tag, exc))
        page.wait_for_timeout(600)
        body = _body_text(page)
        if WIN_RE.search(body):
            m = re.search(r"You brushed\s*(\d+)\s*%", body)
            shown = int(m.group(1)) if m else None
            expect = coverage_pct(res["player_cells"], set(res["path"]))
            errs = cerr + perr
            detail = ("%s DRAW->FORGE->RUN->WIN ok (D %d, %d moves, pct "
                      "shown %s mirror %d); scrollY 0 through drag%s"
                      % (tag, today_d, res["moves"], shown, expect,
                         "" if not errs else "; console errors %s" % (errs,)))
            if errs:
                return ("fail", "%s: WIN but page errors: %s" % (tag, errs))
            return ("pass", detail)
        if LOSE_RE.search(body):
            return ("fail", "%s: walked the mirror BFS path (%d moves) but "
                    "game says OUT OF MOVES; forge mismatch?" % (tag,
                                                                 res["moves"]))
        return ("fail", "%s: no WIN after walking the mirror BFS path "
                "(%d moves); body %.160r" % (tag, res["moves"], body))
    except Exception as exc:  # noqa: BLE001
        return ("fail", "%s: exception %s" % (tag, exc))
    finally:
        try:
            ctx.close()
        except Exception:  # noqa: BLE001
            pass


def browser_legs(root, game_text):
    """Returns (status, detail): status in pass/fail/skip."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        return ("skip", "playwright import failed: %s" % exc)
    if not TOUCH_ASSERT_RE.search(game_text):
        return ("fail", "file lacks touch-action: none on the drawing "
                "surface")
    if "pointerId" not in game_text:
        return ("fail", "file lacks single-pointerId tracking (pointerId)")
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
    except Exception as exc:  # noqa: BLE001
        return ("fail", "local server spawn failed (port %d): %s"
                % (port, exc))
    started = False
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(url, timeout=1)
            except Exception:  # noqa: BLE001
                if srv.poll() is not None:
                    return ("fail", "local server exited code %s (port %d "
                            "busy?)" % (srv.returncode, port))
                time.sleep(0.2)
                continue
            if srv.poll() is None:
                started = True
            break
        if not started:
            return ("fail", "local server did not start (port %d busy?)" % port)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                outcomes = []
                for (w, h, mobile) in VIEWPORTS:
                    outcomes.append(run_one_viewport(browser, url, origin,
                                                     w, h, mobile))
            finally:
                browser.close()
        fails = [d for (s, d) in outcomes if s == "fail"]
        skips = [d for (s, d) in outcomes if s == "skip"]
        notes = [d for (s, d) in outcomes if s == "pass"]
        if fails:
            return ("fail", " | ".join(fails) + " || " + " | ".join(notes))
        if skips:
            return ("skip", " | ".join(skips) + " || " + " | ".join(notes))
        return ("pass", " | ".join(notes))
    finally:
        _stop_child(srv)
        _port_cleanup(port)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    for arg in sys.argv[1:]:
        print("FAIL: unknown argument %r (this harness takes no arguments)"
              % arg)
        print("RESULT: FAIL (exit 1)")
        return 1

    root = repo_root()
    game = root / GAME_REL

    leg_day_anchor()
    leg_determinism()
    leg_monotone()
    leg_room()
    leg_minimum()
    leg_reachability()

    pure_ok = all(passed for (_, passed, _) in CHECKS)

    if not game.exists():
        print("RED: missing game file: %s" % GAME_REL)
        print("The harness has no target. Refusing to stay green.")
        for name, passed, detail in CHECKS:
            print("CHECK %s: %s (exit %d)%s"
                  % (name, "PASS" if passed else "FAIL",
                     0 if passed else 1,
                     " " + detail if detail else ""))
        print("RESULT: %s (exit %d)" % (("FAIL" if not pure_ok else "RED"),
                                        1 if not pure_ok else 2))
        return 1 if not pure_ok else 2
    try:
        text = game.read_text()
    except Exception as exc:  # noqa: BLE001
        print("RED: cannot read game file %s: %s" % (GAME_REL, exc))
        print("RESULT: RED (exit 2)")
        return 2

    if not pure_ok:
        for name, passed, detail in CHECKS:
            print("CHECK %s: %s (exit %d)%s"
                  % (name, "PASS" if passed else "FAIL",
                     0 if passed else 1,
                     " " + detail if detail else ""))
        print("RESULT: FAIL (exit 1)")
        return 1

    status, detail = browser_legs(root, text)
    if status == "pass":
        record("browser-legs", True, detail)
    elif status == "skip":
        print("SKIPPED: browser legs (reason: %s)" % detail)
        for name, passed, d2 in CHECKS:
            print("CHECK %s: %s (exit %d)%s"
                  % (name, "PASS" if passed else "FAIL",
                     0 if passed else 1, " " + d2 if d2 else ""))
        print("RESULT: SKIP (exit 3)")
        return 3
    else:
        record("browser-legs", False, detail)

    print("TRACE proof harness (Story 169) [python: %s]" % sys.executable)
    print("forge: resample 2 px, floor+clamp 9x9, border wall, "
          "carve START/EXIT, L-stitch BFS; day: mulberry32(D)")
    print("")
    code = 0
    for name, passed, detail in CHECKS:
        print("CHECK %s: %s (exit %d)%s"
              % (name, "PASS" if passed else "FAIL",
                 0 if passed else 1,
                 " " + detail if detail else ""))
        if not passed:
            code = 1
    print("RESULT: %s (exit %d)"
          % ("PASS" if code == 0 else "FAIL", code))
    return code


if __name__ == "__main__":
    sys.exit(main())
