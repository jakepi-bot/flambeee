#!/usr/bin/env python3
"""LIGHTFARE proof harness and balance gate (Story 157, Session 70).

Runs under:
    env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/lightfare-proof.py

What it does:
  1. Locates the repo root from its own path and requires
     website/games/lightfare.html. Absent or unreadable -> RED anchor,
     exit 2 (the pre-155 tree has no target; never bless it green).
  2. Static legs: extract the 5 shipped layout strings, BFS each, require
     exactly [8, 10, 12, 14, 16]; mirror the cost math (prices 1/2/4/8,
     spends 1/3/7/15, budget 15, unaffordable 5th look refused) and
     require the verbatim refusal line plus price/budget evidence in the
     shipped file. Exact match or FAIL.
  3. 250 seeded wrong-turn trials (50 per level, seed = L*1000 + t,
     t 0..49, wrong-turn p 0.25 per junction): every level 50/50
     completes within 80 moves, per-level median looks <= par
     [1,1,2,2,3], no trial above 4 looks. Any breach is FAIL.
  4. Mutation control: swap in a one-wall-drifted layout and require a
     length check to go red. Green-on-drift is a harness FAIL.
  5. Browser legs in real Chromium at 1280x800 and 375x667, real input
     on fresh profiles, Story 152 narrowing (SKIPPED lines in argv
     order) and loud FALLBACK discipline.

Exit codes (Story 152): 0 PASS; 1 any CHECK FAIL with the cause named;
2 RED anchor (game file absent or unreadable); 3 SKIP-narrowed (every
executed check passed and at least one narrowing flag printed its
SKIPPED line). FAIL dominates SKIP; invalid flag values are FAILs.
"""

import json
import re
import statistics
import subprocess
import sys
import time
import urllib.request
from collections import deque
from pathlib import Path

# ---------------------------------------------------------------------------
# Contract constants (design-handoff Story 157 section 3; story FR-6).
# ---------------------------------------------------------------------------
EXPECTED_LENGTHS = [8, 10, 12, 14, 16]
PAR_LOOKS = [1, 1, 2, 2, 3]
TRIALS_PER_LEVEL = 50
WRONG_TURN_P = 0.25
MOVE_LIMIT = 80
LIGHT_BUDGET = 15
LOOK_PRICES = [1, 2, 4, 8]
REVEAL_MS = 1000
GAME_REL = Path("website/games/lightfare.html")
BROWSER_PORT = 8943  # new; no clash with 8932 or 8941
VIEWPORTS = (
    ("desktop", {"width": 1280, "height": 800}, False),
    ("mobile", {"width": 375, "height": 667}, True),
)

COUNT_KEY = "flambeee-lightfare-plays"
BEST_KEY = "flambeee-lightfare-best"
ONELINER = "Every look costs. Reach the exit with light to spare."
REFUSAL_LINE = "Not enough light."
LOSE_LINE = "Out of moves."
PLAYS_LINE_RE = re.compile(r"Plays on this browser:\s*(\d+)")
CLEAR_RE = re.compile(r"Level (\d+) clear\. Light kept: (\d+)\.")
WIN_RE = re.compile(r"Run complete\. Total light: (\d+)\.")
CORRUPT_SEEDS = ["abc", "{bad json", "1.5", "null", "-1", "NaN", "Infinity"]
BEST_CORRUPT_SEEDS = ["abc", "{bad json", "-1"]

CHECKS = []  # (name, passed: bool, detail: str)


def record(name, passed, detail=""):
    CHECKS.append((name, bool(passed), detail))
    return passed


def repo_root():
    # dev/lightfare-proof.py -> repo root is the parent of dev/.
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Layout extraction from the shipped file.
# Rows are recovered from each exact-7 '#' top-border anchor by collecting
# the next 42 grid characters (# . S E) while skipping separators (quotes,
# commas, whitespace, brackets, backslash-n escapes, comment punctuation).
# Every recovered 7x7 block must have full top/bottom walls, exactly one S
# and one E, so prose or comment '#' runs can never validate.
# ---------------------------------------------------------------------------
GRID_CHARS = "#.SE"
SEP_CHARS = frozenset("'\" \t\r\n,;[]{}()+=-/*.:\\n")


def _valid_maze(rows):
    if len(rows) != 7 or any(len(r) != 7 for r in rows):
        return False
    if rows[0] != "#" * 7 or rows[6] != "#" * 7:
        return False
    flat = "".join(rows)
    if any(ch not in GRID_CHARS for ch in flat):
        return False
    if flat.count("S") != 1 or flat.count("E") != 1:
        return False
    return True


def extract_layouts(text):
    """Return (list of 7x7 grid strings in file order, found_count)."""
    blocks = []
    for m in re.finditer(r"(?<!#)#{7}(?!#)", text):
        chars = []
        i = m.end()
        while i < len(text) and len(chars) < 42:
            ch = text[i]
            if ch in GRID_CHARS:
                chars.append(ch)
            elif ch in SEP_CHARS:
                pass
            else:
                break
            i += 1
        if len(chars) != 42:
            continue
        # Anchor supplies row 0 (top border); chars hold the 6 rows below.
        rows = [m.group(0)] + ["".join(chars[k * 7:(k + 1) * 7])
                               for k in range(6)]
        if not _valid_maze(rows):
            continue
        grid = "\n".join(rows)
        if grid in blocks:
            continue
        blocks.append(grid)
    return blocks, len(blocks)


def bfs_path(rows, start, end, is_wall):
    """Shortest path (list of cells) from start to end; None if unreachable."""
    q = deque([start])
    parent = {start: None}
    while q:
        cur = q.popleft()
        if cur == end:
            break
        r, c = cur
        for nb in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if not (0 <= nb[0] < len(rows) and 0 <= nb[1] < len(rows[nb[0]])):
                continue
            if nb in parent or is_wall(nb):
                continue
            parent[nb] = cur
            q.append(nb)
    if end not in parent:
        return None
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return list(reversed(path))


def _grid_parts(grid):
    rows = grid.split("\n")
    start = exit_ = None
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch == "S":
                start = (i, j)
            elif ch == "E":
                exit_ = (i, j)
    return rows, start, exit_


def bfs_length(grid):
    rows, start, exit_ = _grid_parts(grid)
    if start is None or exit_ is None:
        return None
    path = bfs_path(rows, start, exit_, lambda cell: rows[cell[0]][cell[1]] == "#")
    return None if path is None else len(path) - 1


# ---------------------------------------------------------------------------
# Static legs: BFS lengths, cost sequence, shipped evidence.
# ---------------------------------------------------------------------------
def static_length_check(layouts):
    """Exact-length check over the extracted layouts. Returns (ok, detail)."""
    got = [bfs_length(g) for g in layouts]
    ok = len(layouts) == 5 and got == EXPECTED_LENGTHS
    return ok, "BFS %s want %s (5/5 exact)" % (got, EXPECTED_LENGTHS)


def aggregate_length_check(layouts):
    """Same check, per-level detail (used for the mutation control)."""
    got = [bfs_length(g) for g in layouts]
    ok = len(layouts) == 5 and got == EXPECTED_LENGTHS
    detail = "; ".join(
        "L%d got %s want %s" % (i + 1, g, EXPECTED_LENGTHS[i])
        for i, g in enumerate(got)
    )
    return ok, detail


def cost_mirror():
    """Formula mirror: prices, spends, budget, affordability gate."""
    prices = [2 ** (k - 1) for k in range(1, 5)]
    spends = [2 ** n - 1 for n in range(1, 5)]
    budget = LIGHT_BUDGET
    allowed = []
    for n in range(5):
        light_left = budget - (2 ** n - 1)
        allowed.append(light_left >= 2 ** n)
    ok = (
        prices == [1, 2, 4, 8]
        and spends == [1, 3, 7, 15]
        and budget == 15
        and allowed == [True, True, True, True, False]
    )
    detail = (
        "prices %s; spends %s; budget %d; look gates n=0..4 %s; "
        "5th look refused (light 0 < 16)"
        % (prices, spends, budget, allowed)
    )
    return ok, detail


def shipped_cost_evidence(text):
    """Verbatim refusal plus price/budget evidence in the shipped file."""
    missing = []
    if REFUSAL_LINE not in text:
        missing.append("verbatim refusal %r" % REFUSAL_LINE)
    price_pat = (
        r"1\s*,\s*2\s*,\s*4\s*,\s*8"
        r"|2\s*\*\*\s*\("
        r"|Math\.pow\s*\(\s*2"
        r"|2\s*\*\*\s*\(?k\b"
    )
    if not re.search(price_pat, text):
        missing.append("look price sequence 1,2,4,8 (or 2**(k-1) formula)")
    budget_pat = (
        r"budget[^0-9\n]{0,24}\b15\b"
        r"|LIGHT[_ ]?BUDGET[^0-9]{0,20}15"
        r"|\b(?:const|let|var)\s+light\b[^0-9\n]{0,16}=\s*15\b"
        r"|\blight\b[^0-9\n]{0,16}=\s*15\b"
    )
    if not re.search(budget_pat, text, re.IGNORECASE):
        missing.append("budget-15 constant")
    return missing


# ---------------------------------------------------------------------------
# Seeded wrong-turn trials (FR-2).
#
# Agent: follows the BFS plan over its remembered snapshot (unknown cells
# assumed passable). At any junction (2+ legal neighbours) it takes a random
# legal wrong step with p = 0.25. It may look only when a cell its snapshot
# assumed passable turns out to be a wall in the halo; each look reveals the
# full board, after which it banks the true BFS remainder and walks it to the
# exit. Seeded PRNG (mulberry32), seed = L*1000 + t.
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


def _neighbours(cell):
    r, c = cell
    return ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))


def trial_agent(grid, seed):
    rows, start, exit_ = _grid_parts(grid)
    if start is None or exit_ is None:
        return {"completed": False, "moves": 0, "looks": 0}
    nr, nc = len(rows), len(rows[0])

    def true_wall(cell):
        return rows[cell[0]][cell[1]] == "#"

    rng = mulberry32(seed)
    known = {}       # cell -> "wall" | "pass" (observed truth)
    assumed = set()  # cells a computed plan treated as passable while unknown
    banked = None    # exact remainder path after a look
    pos = start
    moves = 0
    looks = 0
    light = LIGHT_BUDGET

    def observe():
        """Halo read at pos. Returns True on snapshot-vs-halo contradiction."""
        contr = False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                cell = (pos[0] + dr, pos[1] + dc)
                if not (0 <= cell[0] < nr and 0 <= cell[1] < nc):
                    continue
                obs = "wall" if true_wall(cell) else "pass"
                prev = known.get(cell)
                if prev is None:
                    known[cell] = obs
                    if obs == "wall" and cell in assumed:
                        contr = True
        return contr

    def plan():
        """Optimistic BFS over the remembered snapshot (unknown = passable)."""
        path = bfs_path(rows, pos, exit_, lambda c: known.get(c) == "wall")
        if path is None:
            return None
        for cell in path:
            if cell not in known:
                assumed.add(cell)
        return path

    observe()  # boot halo
    guard = 0
    while pos != exit_:
        guard += 1
        if guard > 5000 or moves >= MOVE_LIMIT:
            return {"completed": False, "moves": moves, "looks": looks}
        if banked is not None and pos in banked:
            path = banked[banked.index(pos):]
        else:
            banked = None
            path = plan()
            if path is None or len(path) < 2:
                return {"completed": False, "moves": moves, "looks": looks}
        nxt = path[1]
        if banked is None:
            legal = [nb for nb in _neighbours(pos)
                     if 0 <= nb[0] < nr and 0 <= nb[1] < nc and not true_wall(nb)]
            if len(legal) >= 2 and rng() < WRONG_TURN_P:
                wrongs = [c for c in legal if c != nxt]
                if wrongs:
                    nxt = wrongs[int(rng() * len(wrongs)) % len(wrongs)]
        if true_wall(nxt):
            # Neighbours are always halo-visible, so this is unreachable;
            # treat as a refused bump (no move charged) and re-observe.
            if not observe():
                return {"completed": False, "moves": moves, "looks": looks}
            continue
        pos = nxt
        moves += 1
        contr = observe()
        if contr and looks < len(LOOK_PRICES) and light >= LOOK_PRICES[looks]:
            light -= LOOK_PRICES[looks]
            looks += 1
            # Full-board look: the snapshot becomes exact truth.
            for r in range(nr):
                for c in range(nc):
                    known[(r, c)] = "wall" if true_wall((r, c)) else "pass"
            banked = plan()  # banked true BFS remainder from pos to E
    return {"completed": True, "moves": moves, "looks": looks}


def run_trials(layouts):
    per_level = []
    for idx, grid in enumerate(layouts):
        level = idx + 1
        done = 0
        looks_list = []
        max_moves = 0
        for t in range(TRIALS_PER_LEVEL):
            seed = level * 1000 + t
            res = trial_agent(grid, seed)
            if res["completed"] and res["moves"] <= MOVE_LIMIT:
                done += 1
            looks_list.append(res["looks"])
            max_moves = max(max_moves, res["moves"])
        per_level.append({
            "level": level,
            "par": PAR_LOOKS[idx],
            "done": done,
            "median": statistics.median(looks_list),
            "max_looks": max(looks_list),
            "max_moves": max_moves,
        })
    return per_level


# ---------------------------------------------------------------------------
# Mutation control (FR-5): one-wall-drifted layout must turn a length check
# red. A green-on-drift run is a harness FAIL, never a pass.
# ---------------------------------------------------------------------------
def mutation_control(layouts):
    for idx, grid in enumerate(layouts):
        expected = EXPECTED_LENGTHS[idx]
        rows, start, exit_ = _grid_parts(grid)
        nr, nc = len(rows), len(rows[0])
        cands = []
        for flip_to in ("#", "."):
            for r in range(1, nr - 1):
                for c in range(1, nc - 1):
                    if (r, c) in (start, exit_) or rows[r][c] == flip_to:
                        continue
                    flipped = [list(row) for row in rows]
                    flipped[r][c] = flip_to
                    drifted = "\n".join("".join(row) for row in flipped)
                    if bfs_length(drifted) != expected:
                        cands.append((r, c, rows[r][c], flip_to, drifted))
            if cands:
                break
        if not cands:
            continue
        r, c, was, now, drifted = cands[0]
        mutated = list(layouts)
        mutated[idx] = drifted
        ok, detail = aggregate_length_check(mutated)
        label = ("drift L%d cell (%d,%d) %s->%s" % (idx + 1, r, c, was, now))
        if ok:
            return False, ("%s: length check stayed green on the drifted "
                           "layout (tautological instrument)" % label)
        return True, ("%s -> length check red as required (%s)" % (label, detail))
    return False, ("no single-wall drift changed any BFS length across the "
                   "5 layouts; mutation control cannot prove the check red")


# ---------------------------------------------------------------------------
# Browser leg helpers.
# ---------------------------------------------------------------------------
PROBE_GLOBALS = ["__lightfare", "__lf", "__lightFare", "__LIGHTFARE",
                 "__lfGame", "__game"]
PROBE_METHODS = {
    "state": ["state"],
    "plays": ["plays", "playCount"],
    "best": ["best"],
    "level": ["level"],
    "moves": ["moves", "moveCount"],
    "light": ["light"],
    "bank": ["bank", "banked", "total", "score"],
}

KEY_FOR = {"up": "ArrowUp", "down": "ArrowDown",
           "left": "ArrowLeft", "right": "ArrowRight"}
DIR_GLYPHS = {
    "up": ("up", "arrowup", "w", "↑", "▲"),
    "down": ("down", "arrowdown", "s", "↓", "▼"),
    "left": ("left", "arrowleft", "a", "←", "◀"),
    "right": ("right", "arrowright", "d", "→", "▶"),
}

BLOCKED_STORAGE_SCRIPT = (
    "(function () {"
    " function denied() { throw new Error('blocked-storage'); }"
    " try {"
    "  Object.defineProperty(window, 'localStorage', {"
    "   configurable: true, writable: true,"
    "   value: { getItem: denied, setItem: denied, removeItem: denied,"
    "            clear: denied, key: denied,"
    "            get length() { throw new Error('blocked-storage'); } }"
    "  });"
    " } catch (e) {}"
    "})();"
)


def resolve_probe(page):
    """Locate a window global exposing state()/plays() style probes."""
    for gname in PROBE_GLOBALS:
        try:
            exists = page.evaluate(
                "typeof window[%s] === 'object' && window[%s] !== null"
                % (json.dumps(gname), json.dumps(gname)))
        except Exception:  # noqa: BLE001
            continue
        if not exists:
            continue
        methods = {}
        for key, names in PROBE_METHODS.items():
            for nm in names:
                try:
                    is_fn = page.evaluate(
                        "typeof window[%s][%s] === 'function'"
                        % (json.dumps(gname), json.dumps(nm)))
                except Exception:  # noqa: BLE001
                    is_fn = False
                if is_fn:
                    methods[key] = nm
                    break
        if "state" in methods and "plays" in methods:
            return {"global": gname, "methods": methods}
    return None


class Reader:
    """Page state reader: window probe first, rendered copy as fallback."""

    def __init__(self, page, origin):
        self.page = page
        self.origin = origin
        self.probe = resolve_probe(page)

    def invalidate(self):
        try:
            self.probe = resolve_probe(self.page)
        except Exception:  # noqa: BLE001
            self.probe = None

    def _body(self):
        try:
            return self.page.inner_text("body")
        except Exception:  # noqa: BLE001
            return ""

    def _probe(self, key):
        if not self.probe or key not in self.probe["methods"]:
            return None
        expr = "window[%s][%s]()" % (
            json.dumps(self.probe["global"]),
            json.dumps(self.probe["methods"][key]))
        try:
            return self.page.evaluate(expr)
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _num(pattern, text):
        m = re.search(pattern, text)
        return int(m.group(1)) if m else None

    def state(self):
        v = self._probe("state")
        if v is not None:
            return v
        txt = self._body()
        if ONELINER in txt:
            return "TITLE"
        if CLEAR_RE.search(txt):
            return "LEVELCLEAR"
        if LOSE_LINE in txt:
            return "LOSE"
        if WIN_RE.search(txt):
            return "WIN"
        if re.search(r"(?i)\bmoves?\b", txt):
            return "RUN"
        return None

    def plays_line(self):
        """Rendered 'Plays on this browser: N' line, whitespace-normalised."""
        txt = self._body()
        for line in txt.splitlines():
            if "Plays on this browser" in line:
                return " ".join(line.split())
        return None

    def plays(self):
        v = self._probe("plays")
        if v is not None:
            return v
        m = PLAYS_LINE_RE.search(self._body())
        return int(m.group(1)) if m else None

    def best(self):
        v = self._probe("best")
        if v is not None:
            return v
        return self._num(r"(?i)\bbest\b\D{0,6}(\d+)", self._body())

    def light(self):
        v = self._probe("light")
        if v is not None:
            return v
        return self._num(r"(?i)\blight\b\D{0,6}(\d+)", self._body())

    def moves(self):
        v = self._probe("moves")
        if v is not None:
            return v
        return self._num(r"(?i)\bmoves?\b\D{0,6}(\d+)", self._body())

    def level(self):
        v = self._probe("level")
        if v is not None:
            return v
        return self._num(r"(?i)\blevel\D{0,4}(\d+)", self._body())

    def bank(self):
        v = self._probe("bank")
        if v is not None:
            return v
        return self._num(r"(?i)\b(?:bank(?:ed)?|total|score)\D{0,6}(\d+)",
                         self._body())


def blur(page):
    try:
        page.evaluate(
            "(function () { if (document.activeElement"
            " && document.activeElement.blur) document.activeElement.blur(); })()")
    except Exception:  # noqa: BLE001
        pass


def wait_state(reader, want, timeout_s=3.0):
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            if reader.state() == want:
                return True
        except Exception:  # noqa: BLE001
            pass
        reader.page.wait_for_timeout(80)
    return False


def wait_num_change(reader, getter, before, timeout_s=2.0):
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            v = getter()
        except Exception:  # noqa: BLE001
            v = None
        if v is not None and v != before:
            return True
        reader.page.wait_for_timeout(60)
    return False


def find_button(page, pattern, index=0):
    try:
        btns = page.query_selector_all("button, [role=button]")
    except Exception:  # noqa: BLE001
        return None
    vis = [b for b in btns if b.is_visible()]
    if not vis:
        return None
    for b in vis:
        try:
            txt = (b.inner_text() or "").strip()
        except Exception:  # noqa: BLE001
            continue
        if re.search(pattern, txt, re.IGNORECASE):
            return b
    return vis[index] if len(vis) > index else None


def _norm_token(s):
    return re.sub(r"[\s_\-]+", "", (s or "").strip().lower())


def find_pad_button(page, direction):
    """On-screen pad control for a direction (text, aria-label, data attrs)."""
    want = set(DIR_GLYPHS[direction]) | {direction, "arrow" + direction,
                                         "move" + direction}
    try:
        btns = page.query_selector_all(
            "button, [role=button], [data-dir], [data-direction], [data-key]")
    except Exception:  # noqa: BLE001
        return None
    for b in btns:
        try:
            if not b.is_visible():
                continue
            attrs = [b.inner_text()]
            for a in ("aria-label", "title", "data-dir", "data-direction",
                      "data-key", "data-move"):
                v = b.get_attribute(a)
                if v:
                    attrs.append(v)
        except Exception:  # noqa: BLE001
            continue
        for a in attrs:
            tok = _norm_token(a)
            if tok in want:
                return b
            if a and a.strip() in want:
                return b
    return None


def find_look_button(page):
    try:
        btns = page.query_selector_all("button, [role=button]")
    except Exception:  # noqa: BLE001
        return None
    for b in btns:
        try:
            if not b.is_visible():
                continue
            txt = (b.inner_text() or "").strip()
            label = b.get_attribute("aria-label") or ""
        except Exception:  # noqa: BLE001
            continue
        if re.search(r"(?i)look", txt) or re.search(r"(?i)look", label):
            return b
    return None


def click_handle(page, handle, mobile):
    # Controls may sit below the mobile fold; tap coordinates are
    # viewport-relative, so bring the target on-screen before measuring.
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


def grid_directions(grid):
    """Direction names along the BFS path S -> E."""
    rows, start, exit_ = _grid_parts(grid)
    path = bfs_path(rows, start, exit_, lambda c: rows[c[0]][c[1]] == "#")
    if path is None:
        return None
    dirs = []
    for a, b in zip(path, path[1:]):
        dr, dc = b[0] - a[0], b[1] - a[1]
        dirs.append({(-1, 0): "up", (1, 0): "down",
                     (0, -1): "left", (0, 1): "right"}[(dr, dc)])
    return dirs


def first_legal_dir(grid):
    rows, start, _ = _grid_parts(grid)
    for nb, d in zip(_neighbours(start), ("up", "down", "left", "right")):
        if 0 <= nb[0] < len(rows) and 0 <= nb[1] < len(rows[nb[0]]) \
                and rows[nb[0]][nb[1]] != "#":
            return d
    return "down"


def move_step(reader, page, direction, tag, level, step_no, mobile):
    """Key-press-first move; degrades loudly to a pad click."""
    before = reader.moves()
    blur(page)
    page.keyboard.press(KEY_FOR[direction])
    if wait_num_change(reader, reader.moves, before):
        return True
    print("FALLBACK key->click at %s L%d move %d" % (tag, level, step_no),
          flush=True)
    btn = find_pad_button(page, direction)
    if btn is None:
        return False
    click_handle(page, btn, mobile)
    return wait_num_change(reader, reader.moves, before)


def drive_path(reader, page, grid, tag, level, mobile, failures):
    dirs = grid_directions(grid)
    if not dirs:
        failures.append("%s: no BFS path to drive on L%d" % (tag, level))
        return False
    for i, d in enumerate(dirs, start=1):
        if not move_step(reader, page, d, tag, level, i, mobile):
            failures.append("%s: L%d move %d (%s) did not register"
                            % (tag, level, i, d))
            return False
    return True


def drive_exhaust(reader, page, grid, tag, level, mobile, failures):
    """Walk the first BFS edge back and forth 80 times -> LOSE."""
    dirs = grid_directions(grid)
    if not dirs:
        failures.append("%s: no BFS path for the move-exhaust leg" % tag)
        return False
    fwd, bwd = dirs[0], {"up": "down", "down": "up",
                         "left": "right", "right": "left"}[dirs[0]]
    for i in range(MOVE_LIMIT):
        d = fwd if i % 2 == 0 else bwd
        if not move_step(reader, page, d, tag, level, i + 1, mobile):
            failures.append("%s: exhaust move %d (%s) did not register"
                            % (tag, i + 1, d))
            return False
    return True


def look_step(reader, page, tag, level, n, mobile):
    """Key-press-first look (Space); degrades loudly to a LOOK click."""
    before = reader.light()
    blur(page)
    page.keyboard.press("Space")
    if wait_num_change(reader, reader.light, before):
        page.wait_for_timeout(REVEAL_MS + 150)  # reveal freeze window
        return True
    print("FALLBACK key->click at %s L%d look %d" % (tag, level, n), flush=True)
    btn = find_look_button(page)
    if btn is None:
        return False
    click_handle(page, btn, mobile)
    if not wait_num_change(reader, reader.light, before):
        return False
    page.wait_for_timeout(REVEAL_MS + 150)
    return True


def _refusal_visible(page, timeout_s=1.5):
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            if REFUSAL_LINE in page.inner_text("body"):
                return True
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(60)
    return False


def look_refused(reader, page, tag, level, mobile):
    """5th look with 0 light: verbatim refusal, light stays 0."""
    blur(page)
    page.keyboard.press("Space")
    if _refusal_visible(page) and reader.light() == 0:
        return True
    print("FALLBACK key->click at %s L%d look 5" % (tag, level), flush=True)
    btn = find_look_button(page)
    if btn is not None:
        click_handle(page, btn, mobile)
    return _refusal_visible(page) and reader.light() == 0


def click_until_state(reader, page, pattern, mobile, want_state, tag,
                      step_label, timeout_s=3.0):
    """Click the named control (caller prints the FALLBACK degradation line)."""
    blur(page)
    btn = find_button(page, pattern, 0)
    if btn is None:
        return False
    click_handle(page, btn, mobile)
    return wait_state(reader, want_state, timeout_s)


def advance_level(reader, page, tag, mobile):
    """LEVELCLEAR->RUN (next level) via Enter, degrading to a click."""
    blur(page)
    page.keyboard.press("Enter")
    if wait_state(reader, "RUN", 3.0):
        return True
    print("FALLBACK key->click at %s advance" % tag, flush=True)
    return click_until_state(reader, page, r"(?i)next|continue|advance",
                             mobile, "RUN", tag, "advance")


def retry_level(reader, page, tag, mobile):
    """LOSE->RUN retry via Enter, degrading to a click."""
    blur(page)
    page.keyboard.press("Enter")
    if wait_state(reader, "RUN", 3.0):
        return True
    print("FALLBACK key->click at %s retry" % tag, flush=True)
    return click_until_state(reader, page, r"(?i)retry|try again|again",
                             mobile, "RUN", tag, "retry")


def press_start(reader, page, tag, mobile):
    blur(page)
    page.keyboard.press("Enter")
    if wait_state(reader, "RUN", 3.0):
        return True
    print("FALLBACK key->click at %s start" % tag, flush=True)
    return click_until_state(reader, page, r"(?i)\bstart\b|begin",
                             mobile, "RUN", tag, "start")


def attributable_errors(cerr, perr, origin):
    """Console/page errors that come from the served page itself."""
    out = []
    for e in perr:
        out.append("pageerror: %s" % e)
    for m in cerr:
        try:
            loc = (m.location or {}).get("url") or ""
        except Exception:  # noqa: BLE001
            loc = ""
        if loc.startswith("http") and not loc.startswith(origin):
            continue  # external resource, not page-attributable
        out.append("console: %s" % m.text)
    return out


# ---------------------------------------------------------------------------
# Browser legs (FR-3): both viewports, real input, fresh profiles, order:
# fresh 0/0 -> Start 1 -> reload keeps -> clear L1 advance +0 -> exhaust to
# LOSE, retry +0 same level light 15 bank kept -> 4 looks to 0 with refused
# 5th and completable level -> storage probe match, corrupt seeds to 0,
# blocked storage silent -> touch pad path on mobile -> zero page errors.
# ---------------------------------------------------------------------------
def run_viewport(browser, url, origin, tag, vp, mobile, layouts, notes):
    failures = []
    ctx = browser.new_context(viewport=vp, has_touch=mobile, is_mobile=mobile)
    page = ctx.new_page()
    cerr, perr = [], []
    page.on("console", lambda m: cerr.append(m) if m.type == "error" else None)
    page.on("pageerror", lambda e: perr.append(str(e)))

    def console_gate(label):
        errs = attributable_errors(cerr, perr, origin)
        if errs:
            failures.append("%s: %s page-attributable errors: %s"
                            % (tag, label, errs[:5]))
            return False
        notes.append("%s %s console errors 0" % (tag, label))
        return True

    try:
        # --- fresh profile: boot 0/0, one-liner, TITLE -------------------
        page.goto(url, wait_until="load", timeout=15000)
        page.wait_for_timeout(800)
        reader = Reader(page, origin)
        if reader.state() != "TITLE":
            failures.append("%s: first load state=%s want TITLE"
                            % (tag, reader.state()))
            return failures
        if ONELINER not in page.inner_text("body"):
            failures.append("%s: one-liner %r not visible on TITLE"
                            % (tag, ONELINER))
            return failures
        if reader.plays_line() != "Plays on this browser: 0":
            failures.append("%s: fresh plays line %r want 'Plays on this "
                            "browser: 0'" % (tag, reader.plays_line()))
            return failures
        if reader.plays() != 0 or reader.best() != 0:
            failures.append("%s: fresh plays/best %r/%r want 0/0"
                            % (tag, reader.plays(), reader.best()))
            return failures
        notes.append("%s fresh 0/0 with one-liner ok" % tag)

        # --- Start from TITLE -> plays exactly 1 ------------------------
        if not press_start(reader, page, tag, mobile):
            failures.append("%s: Start did not reach RUN" % tag)
            return failures
        if reader.plays() != 1 or reader.plays_line() != "Plays on this browser: 1":
            failures.append("%s: after Start line=%r plays=%r want 1"
                            % (tag, reader.plays_line(), reader.plays()))
            return failures
        if reader.level() not in (None, 1) or reader.light() != 15 \
                or reader.moves() != 0:
            failures.append("%s: after Start level=%r light=%r moves=%r "
                            "want level 1 light 15 moves 0"
                            % (tag, reader.level(), reader.light(),
                               reader.moves()))
            return failures
        notes.append("%s Start -> plays 1, light 15, moves 0 ok" % tag)

        # --- reload keeps plays 1 on TITLE ------------------------------
        page.reload(wait_until="load", timeout=15000)
        page.wait_for_timeout(800)
        reader.invalidate()
        if reader.state() != "TITLE" or reader.plays() != 1 \
                or reader.plays_line() != "Plays on this browser: 1":
            failures.append("%s: after reload state=%s line=%r plays=%r "
                            "want TITLE / 'Plays on this browser: 1'"
                            % (tag, reader.state(), reader.plays_line(),
                               reader.plays()))
            return failures
        notes.append("%s reload keeps plays 1 on TITLE ok" % tag)

        # --- Start again (counted -> 2), clear L1, advance +0 -----------
        if not press_start(reader, page, tag, mobile):
            failures.append("%s: second Start did not reach RUN" % tag)
            return failures
        if reader.plays() != 2:
            failures.append("%s: second Start from TITLE plays=%r want 2 "
                            "(each Start from TITLE counts once)" % (tag, reader.plays()))
            return failures
        if not drive_path(reader, page, layouts[0], tag, 1, mobile, failures):
            return failures
        if not wait_state(reader, "LEVELCLEAR", 5.0):
            failures.append("%s: L1 clear did not reach LEVELCLEAR (state=%s)"
                            % (tag, reader.state()))
            return failures
        m = CLEAR_RE.search(page.inner_text("body"))
        if not m or int(m.group(1)) != 1 or int(m.group(2)) != 15:
            failures.append("%s: L1 clear line %r want 'Level 1 clear. "
                            "Light kept: 15.'" % (tag, m.group(0) if m else None))
            return failures
        if reader.plays() != 2:
            failures.append("%s: L1 clear changed plays to %r (want 2)"
                            % (tag, reader.plays()))
            return failures
        notes.append("%s clear L1 zero-look banks 15, plays 2 ok" % tag)

        # --- advance to L2: no count, fresh light/moves -----------------
        if not advance_level(reader, page, tag, mobile):
            failures.append("%s: LEVELCLEAR advance did not reach RUN" % tag)
            return failures
        if reader.plays() != 2:
            failures.append("%s: LEVELCLEAR advance changed plays to %r "
                            "(want 2)" % (tag, reader.plays()))
            return failures
        if reader.light() != 15 or reader.moves() != 0:
            failures.append("%s: after advance light=%r moves=%r want 15/0"
                            % (tag, reader.light(), reader.moves()))
            return failures
        lvl_after_advance = reader.level()
        if lvl_after_advance is not None and lvl_after_advance != 2:
            failures.append("%s: after advance level=%r want 2"
                            % (tag, lvl_after_advance))
            return failures
        bank_before = reader.bank()
        notes.append("%s advance +0, light 15, moves 0 ok" % tag)

        # --- exhaust 80 moves -> LOSE, verbatim line, +0 ----------------
        if not drive_exhaust(reader, page, layouts[1], tag, 2, mobile, failures):
            return failures
        if not wait_state(reader, "LOSE", 5.0):
            failures.append("%s: 80 moves did not reach LOSE (state=%s)"
                            % (tag, reader.state()))
            return failures
        if LOSE_LINE not in page.inner_text("body"):
            failures.append("%s: LOSE line %r not visible" % (tag, LOSE_LINE))
            return failures
        if reader.plays() != 2:
            failures.append("%s: LOSE changed plays to %r (want 2)"
                            % (tag, reader.plays()))
            return failures
        notes.append("%s exhaust 80 moves -> LOSE 'Out of moves.', plays 2 ok"
                     % tag)

        # --- retry: same level, light 15, bank kept, plays +0 ------------
        if not retry_level(reader, page, tag, mobile):
            failures.append("%s: LOSE retry did not reach RUN" % tag)
            return failures
        if reader.plays() != 2:
            failures.append("%s: LOSE retry changed plays to %r (want 2)"
                            % (tag, reader.plays()))
            return failures
        if reader.light() != 15 or reader.moves() != 0:
            failures.append("%s: after retry light=%r moves=%r want 15/0"
                            % (tag, reader.light(), reader.moves()))
            return failures
        lvl_after_retry = reader.level()
        if lvl_after_retry is not None and lvl_after_retry != 2:
            failures.append("%s: retry loaded level=%r, want same level 2"
                            % (tag, lvl_after_retry))
            return failures
        bank_after = reader.bank()
        if bank_before is not None and bank_after is not None \
                and bank_before != bank_after:
            failures.append("%s: retry changed bank %r -> %r (bank kept)"
                            % (tag, bank_before, bank_after))
            return failures
        notes.append("%s retry: plays 2, light 15, bank kept%s ok" % (
            tag, "" if bank_before is not None else " (bank not text-readable)"))

        # --- 4 looks spend 15 -> 0 (14, 12, 8, 0) -----------------------
        for i, want in enumerate((14, 12, 8, 0), start=1):
            if not look_step(reader, page, tag, 2, i, mobile):
                failures.append("%s: look %d did not register" % (tag, i))
                return failures
            if reader.light() != want:
                failures.append("%s: after look %d light=%r want %r"
                                % (tag, i, reader.light(), want))
                return failures
        notes.append("%s 4 looks spend 15 -> 0 (14,12,8,0) ok" % tag)

        # --- 5th look refused with the verbatim line, light stays 0 -----
        if not look_refused(reader, page, tag, 2, mobile):
            failures.append("%s: 5th look not refused with %r (light=%r)"
                            % (tag, REFUSAL_LINE, reader.light()))
            return failures
        notes.append("%s 5th look refused with 'Not enough light.', light 0 ok"
                     % tag)

        # --- level still completable at light 0 -------------------------
        if not drive_path(reader, page, layouts[1], tag, 2, mobile, failures):
            return failures
        if not wait_state(reader, "LEVELCLEAR", 5.0):
            failures.append("%s: L2 not completable after refused 5th look "
                            "(state=%s)" % (tag, reader.state()))
            return failures
        m = CLEAR_RE.search(page.inner_text("body"))
        if not m or int(m.group(1)) != 2 or int(m.group(2)) != 0:
            failures.append("%s: L2 clear line %r want 'Level 2 clear. "
                            "Light kept: 0.'" % (tag, m.group(0) if m else None))
            return failures
        if reader.plays() != 2:
            failures.append("%s: L2 clear changed plays to %r (want 2)"
                            % (tag, reader.plays()))
            return failures
        notes.append("%s L2 completable at light 0 ('Level 2 clear. Light "
                     "kept: 0.'), plays 2 ok" % tag)

        # --- advance to L3 (no count), storage probe match --------------
        if not advance_level(reader, page, tag, mobile):
            failures.append("%s: L2 advance did not reach RUN" % tag)
            return failures
        if reader.plays() != 2:
            failures.append("%s: second advance changed plays to %r (want 2)"
                            % (tag, reader.plays()))
            return failures
        try:
            raw = page.evaluate(
                "localStorage.getItem(%s)" % json.dumps(COUNT_KEY))
        except Exception as exc:  # noqa: BLE001
            failures.append("%s: storage read threw: %s" % (tag, exc))
            return failures
        if raw is None:
            failures.append("%s: storage key %s absent after counted run"
                            % (tag, COUNT_KEY))
            return failures
        try:
            stored = json.loads(raw)
        except Exception:  # noqa: BLE001
            stored = "BADJSON:%r" % (raw,)
        if stored != reader.plays():
            failures.append("%s: matchAssertion storage %r != probe %r"
                            % (tag, stored, reader.plays()))
            return failures
        try:
            raw_best = page.evaluate(
                "localStorage.getItem(%s)" % json.dumps(BEST_KEY))
        except Exception:  # noqa: BLE001
            raw_best = None
        try:
            stored_best = json.loads(raw_best) if raw_best is not None else 0
        except Exception:  # noqa: BLE001
            stored_best = "BADJSON:%r" % (raw_best,)
        if stored_best != reader.best():
            failures.append("%s: matchAssertion best storage %r != probe %r"
                            % (tag, stored_best, reader.best()))
            return failures
        notes.append("%s storage match: plays %r == probe, best %r == probe ok"
                     % (tag, stored, stored_best))
        console_gate("counting flow")
        ctx.close()

        # --- corrupt seeds boot to 0 ------------------------------------
        ctx = browser.new_context(viewport=vp, has_touch=mobile,
                                  is_mobile=mobile)
        page = ctx.new_page()
        cerr, perr = [], []
        page.on("console",
                lambda m: cerr.append(m) if m.type == "error" else None)
        page.on("pageerror", lambda e: perr.append(str(e)))
        page.goto(url, wait_until="load", timeout=15000)
        page.wait_for_timeout(800)
        reader = Reader(page, origin)
        for seed in CORRUPT_SEEDS:
            page.evaluate("localStorage.setItem(%s, %s)"
                          % (json.dumps(COUNT_KEY), json.dumps(seed)))
            page.reload(wait_until="load", timeout=15000)
            page.wait_for_timeout(700)
            reader.invalidate()
            if reader.plays_line() != "Plays on this browser: 0" \
                    or reader.plays() != 0:
                failures.append("%s: corrupt seed %r booted line=%r plays=%r "
                                "want 0" % (tag, seed, reader.plays_line(),
                                            reader.plays()))
                return failures
        page.evaluate("localStorage.removeItem(%s)" % json.dumps(COUNT_KEY))
        page.reload(wait_until="load", timeout=15000)
        page.wait_for_timeout(700)
        reader.invalidate()
        if reader.plays() != 0:
            failures.append("%s: absent count key booted plays=%r want 0"
                            % (tag, reader.plays()))
            return failures
        for seed in BEST_CORRUPT_SEEDS:
            page.evaluate("localStorage.setItem(%s, %s)"
                          % (json.dumps(BEST_KEY), json.dumps(seed)))
            page.reload(wait_until="load", timeout=15000)
            page.wait_for_timeout(700)
            reader.invalidate()
            if reader.best() != 0:
                failures.append("%s: corrupt best seed %r booted best=%r "
                                "want 0" % (tag, seed, reader.best()))
                return failures
        notes.append("%s corrupt seeds sanitize to 0 (%d count + absent + "
                     "%d best) ok" % (tag, len(CORRUPT_SEEDS),
                                      len(BEST_CORRUPT_SEEDS)))
        console_gate("corrupt flow")
        ctx.close()

        # --- blocked storage: silent, in-memory -------------------------
        ctx = browser.new_context(viewport=vp, has_touch=mobile,
                                  is_mobile=mobile)
        ctx.add_init_script(BLOCKED_STORAGE_SCRIPT)
        page = ctx.new_page()
        cerr, perr = [], []
        page.on("console",
                lambda m: cerr.append(m) if m.type == "error" else None)
        page.on("pageerror", lambda e: perr.append(str(e)))
        page.goto(url, wait_until="load", timeout=15000)
        page.wait_for_timeout(800)
        reader = Reader(page, origin)
        usable = page.evaluate(
            "(function () { try { localStorage.getItem('x');"
            " return 'USABLE'; } catch (e) { return 'BLOCKED'; } })()")
        if usable != "BLOCKED":
            failures.append("%s: storage not blocked, degraded mode unproven"
                            % tag)
            return failures
        if reader.plays_line() != "Plays on this browser: 0" \
                or reader.plays() != 0:
            failures.append("%s: blocked-storage boot line=%r plays=%r "
                            "want 0/0" % (tag, reader.plays_line(),
                                          reader.plays()))
            return failures
        if not press_start(reader, page, tag, mobile):
            failures.append("%s: blocked-storage Start did not reach RUN"
                            % tag)
            return failures
        if reader.plays() != 1:
            failures.append("%s: blocked-storage in-memory plays=%r want 1"
                            % (tag, reader.plays()))
            return failures
        notes.append("%s blocked storage silent, in-memory 0 -> 1 ok" % tag)
        console_gate("blocked-storage flow")
        ctx.close()
    except Exception as exc:  # noqa: BLE001
        failures.append("%s: exception %s" % (tag, exc))
    finally:
        try:
            ctx.close()
        except Exception:  # noqa: BLE001
            pass

    # --- touch pad path (mobile viewport; normative touch path) ---------
    if mobile and not failures:
        ctx = browser.new_context(viewport=vp, has_touch=True, is_mobile=True)
        page = ctx.new_page()
        cerr, perr = [], []
        page.on("console",
                lambda m: cerr.append(m) if m.type == "error" else None)
        page.on("pageerror", lambda e: perr.append(str(e)))
        try:
            page.goto(url, wait_until="load", timeout=15000)
            page.wait_for_timeout(800)
            reader = Reader(page, origin)
            if not press_start(reader, page, tag, mobile):
                failures.append("%s: pad-flow Start did not reach RUN" % tag)
            else:
                direction = first_legal_dir(layouts[0])
                pad = find_pad_button(page, direction)
                if pad is None:
                    failures.append("%s: pad button for direction %r not "
                                    "found" % (tag, direction))
                else:
                    before = reader.moves()
                    click_handle(page, pad, True)
                    if not wait_num_change(reader, reader.moves, before):
                        failures.append("%s: pad tap (%s) did not move the "
                                        "player" % (tag, direction))
                    else:
                        notes.append("%s pad tap %s moved ok" % (tag, direction))
                look_btn = find_look_button(page)
                if look_btn is None:
                    failures.append("%s: LOOK button not found" % tag)
                else:
                    before = reader.light()
                    click_handle(page, look_btn, True)
                    if not wait_num_change(reader, reader.light, before):
                        failures.append("%s: LOOK tap did not reveal "
                                        "(light %r)" % (tag, before))
                    else:
                        notes.append("%s LOOK tap revealed ok" % tag)
                        page.wait_for_timeout(REVEAL_MS + 150)
            errs = attributable_errors(cerr, perr, origin)
            if errs:
                failures.append("%s: pad-flow page-attributable errors: %s"
                                % (tag, errs[:5]))
            else:
                notes.append("%s pad flow console errors 0" % tag)
        except Exception as exc:  # noqa: BLE001
            failures.append("%s: pad-flow exception %s" % (tag, exc))
        finally:
            try:
                ctx.close()
            except Exception:  # noqa: BLE001
                pass

    return failures


def browser_legs(root, port, only_vp=None):
    """Serve the repo's website dir and run the Story 157 browser legs."""
    tags = [t for t, _, _ in VIEWPORTS if only_vp in (None, t)]
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        for t in tags:
            record("browser-%s" % t, False,
                   "playwright import failed: %s" % exc)
        return

    webdir = root / "website"
    origin = "http://127.0.0.1:%d" % port
    url = origin + "/games/lightfare.html"
    srv = None
    started = False
    for _ in range(3):
        srv = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port),
             "--directory", str(webdir)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                urllib.request.urlopen(url, timeout=1)
                started = True
                break
            except Exception:  # noqa: BLE001
                if srv.poll() is not None:
                    break
                time.sleep(0.2)
        if started:
            break
        try:
            srv.wait(timeout=2)
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    if not started:
        for t in tags:
            record("browser-%s" % t, False,
                   "local server did not start (port %d busy?)" % port)
        return

    layouts, _ = extract_layouts((root / GAME_REL).read_text())
    if len(layouts) != 5:
        for t in tags:
            record("browser-%s" % t, False,
                   "cannot extract 5 layouts for path driving (%d found)"
                   % len(layouts))
        return

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for tag, vp, mobile in VIEWPORTS:
                if only_vp and tag != only_vp:
                    continue
                notes = []
                failures = run_viewport(browser, url, origin, tag, vp,
                                        mobile, layouts, notes)
                detail = "; ".join(notes)
                if failures:
                    record("browser-%s" % tag, False,
                           " | ".join(failures) + " || " + detail)
                else:
                    record("browser-%s" % tag, True, detail)
            browser.close()
    finally:
        # Port-scoped cleanup only. Prefer fuser (matches the port, never a
        # cmdline) where present; otherwise pkill with a bracketed pattern so
        # the invoking shell cannot match itself. Never a broad kill.
        import shutil
        if shutil.which("fuser"):
            subprocess.run(["fuser", "-k", "%d/tcp" % port],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["pkill", "-f", "http[.]server %d" % port],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    sim_only = False
    port = BROWSER_PORT
    only_vp = None
    vp_error = None
    # Narrowing flags in argv order; each prints one SKIPPED line (Story 152).
    skip_flags = []  # list of (flag_literal, what)
    for arg in sys.argv[1:]:
        if arg == "--sim-only":
            sim_only = True
            skip_flags.append((arg, "browser leg"))
        elif arg.startswith("--viewport="):
            v = arg.split("=", 1)[1]
            only_vp = v
            skip_flags.append((arg, "all viewports except %s" % v))
            if v not in ("desktop", "mobile"):
                vp_error = ("unknown viewport %r in %s (want desktop|mobile)"
                            % (v, arg))
        elif arg.startswith("--port="):
            raw = arg.split("=", 1)[1]
            try:
                port = int(raw)
                if not (1 <= port <= 65535):
                    raise ValueError("out of range")
            except ValueError:
                print("FAIL: bad --port value %r: not a valid port "
                      "(reason: %s)" % (raw, arg))
                print("RESULT: FAIL (exit 1)")
                return 1
            skip_flags.append((arg, "default-port serve"))
        else:
            print("FAIL: unknown argument %r (valid: --sim-only, "
                  "--viewport=desktop|mobile, --port=N)" % arg)
            print("RESULT: FAIL (exit 1)")
            return 1

    root = repo_root()
    game = root / GAME_REL

    if not game.exists():
        print("RED: game file absent: %s" % game)
        print("The gate has no target. Refusing to stay green.")
        print("RESULT: FAIL (exit 2)")
        return 2
    try:
        text = game.read_text()
    except Exception as exc:  # noqa: BLE001
        print("RED: cannot read game file: %s" % exc)
        print("RESULT: FAIL (exit 2)")
        return 2

    # --- static legs -----------------------------------------------------
    layouts, found = extract_layouts(text)
    if len(layouts) != 5:
        record("static-layout-extract", False,
               "found %d valid 7x7 layout blocks in %s, want 5"
               % (found, GAME_REL))
        for flag, what in skip_flags:
            print("SKIPPED: %s (reason: %s)" % (what, flag))
        print("FAIL: static-layout-extract: found %d layout blocks, want 5"
              % found)
        for name, passed, detail in CHECKS:
            print("CHECK %s: %s (exit %d)%s"
                  % (name, "PASS" if passed else "FAIL",
                     0 if passed else 1,
                     " " + detail if detail else ""))
        print("RESULT: FAIL (exit 1)")
        return 1
    record("static-layout-extract", True,
           "5 layout strings extracted from %s" % GAME_REL)

    ok, detail = static_length_check(layouts)
    record("static-bfs-lengths", ok, detail)

    ok, detail = cost_mirror()
    record("static-cost-mirror", ok, detail)

    missing = shipped_cost_evidence(text)
    record("static-cost-shipped", not missing,
           "refusal line + price/budget evidence present" if not missing
           else "missing from shipped file: " + "; ".join(missing))

    # --- wrong-turn trials ----------------------------------------------
    per_level = run_trials(layouts)
    all_done = all(v["done"] == TRIALS_PER_LEVEL for v in per_level)
    record("trials-completion", all_done,
           "; ".join("L%d %d/%d within %d moves (max %d)"
                     % (v["level"], v["done"], TRIALS_PER_LEVEL,
                        MOVE_LIMIT, v["max_moves"]) for v in per_level))
    looks_ok = all(v["median"] <= v["par"] for v in per_level) and \
        all(v["max_looks"] <= 4 for v in per_level)
    record("trials-looks", looks_ok,
           "; ".join("L%d median %s <= par %d, max %d"
                     % (v["level"], v["median"], v["par"], v["max_looks"])
                     for v in per_level))

    # --- mutation control -------------------------------------------------
    ok, detail = mutation_control(layouts)
    record("mutation-control", ok, detail)

    # --- browser legs -----------------------------------------------------
    if vp_error:
        record("browser-legs", False, vp_error)
    elif not sim_only:
        browser_legs(root, port, only_vp)

    # --- report -----------------------------------------------------------
    for flag, what in skip_flags:
        print("SKIPPED: %s (reason: %s)" % (what, flag))
    print("LIGHTFARE proof harness (Story 157)  interpreter: team venv python")
    print("static gate: BFS lengths expect %s; costs 1/2/4/8; spends "
          "1/3/7/15; budget 15; 5th look refused"
          % EXPECTED_LENGTHS)
    print("trials: 50/level, seed L*1000+t (t 0..49), wrong-turn p 0.25, "
          "par %s" % PAR_LOOKS)
    print("")
    print(" L  | par | done   | median | max looks | max moves")
    for v in per_level:
        print(" L%d | %3d | %d/%-4d | %6s | %9d | %9d"
              % (v["level"], v["par"], v["done"], TRIALS_PER_LEVEL,
                 v["median"], v["max_looks"], v["max_moves"]))
    print("")
    code = 0
    for name, passed, detail in CHECKS:
        print("CHECK %s: %s (exit %d)%s"
              % (name, "PASS" if passed else "FAIL",
                 0 if passed else 1,
                 " " + detail if detail else ""))
        if not passed:
            code = 1
    if code == 0 and skip_flags:
        code = 3
    print("RESULT: %s (exit %d)"
          % ("PASS" if code == 0 else ("SKIP" if code == 3 else "FAIL"),
             code))
    return code


if __name__ == "__main__":
    sys.exit(main())
