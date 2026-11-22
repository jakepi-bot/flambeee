#!/usr/bin/env python3
"""EMPTY HANDS proof harness and balance gate (Story 144, Session 65).

Runs under: env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python dev/empty-hands-proof.py

What it does:
  1. Locates the repo root from its own path and requires
     website/games/empty-hands.html. Absent file -> RED anchor, exit 2.
  2. Parses the shipped CONFIG object and fails on any drift from the
     mirrored M.3 constants (names the drifted constant).
  3. Loads the committed seed manifest dev/empty-hands-seeds.json
     (SEED_BASE 3000, level L seeds 3000 + L*1000 + s, s 0..199).
  4. Mirrors the dealer (mulberry32 exactly per M.2), val_at shrink rule,
     and exact interval DP optimal spend / purse formula.
  5. Plays four policies per level shape (solver, fixed-greedy, random
     legal-end, never-give) and enforces gates 1-6.
  6. Drives the shipped page in real Chromium at 1280x800 and 375x667
     with real clicks and taps (gate 7).

Exit codes: 0 every check green; 2 game file absent (RED anchor);
1 any other failure, with the failing check named; 3 a skip flag
(--sim-only/--viewport=/--port=) narrowed the run while every executed
check passed (FAIL dominates SKIP, so any CHECK FAIL still exits 1).
"""

import json
import random
import re
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# --------------------------------------------------------------------------
# Mirrored M.3 constants. The shipped CONFIG must match these exactly.
# --------------------------------------------------------------------------
EXPECTED = {
    "N_PER_LEVEL": [8, 9, 10, 11, 12, 12],
    "VMIN": 1,
    "VMAX": 9,
    "SLACK_PER_LEVEL": [3, 2, 1, 0, 0, 0],
    "LEVEL_CAP": 6,
    "SHRINK_STEP": 1,
    "SHRINK_FLOOR": 1,
    "BEST_KEY": "flambeee-empty-hands-best",
}

SEED_BASE = 3000
RUNS_PER_LEVEL = 200
GAME_REL = Path("website/games/empty-hands.html")
MANIFEST_NAME = "dev/empty-hands-seeds.json"
BROWSER_PORT = 8932

CHECKS = []  # (name, passed: bool, detail: str)


def record(name, passed, detail=""):
    CHECKS.append((name, bool(passed), detail))
    return passed


def repo_root():
    # dev/empty-hands-proof.py -> repo root is the parent of dev/.
    return Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# M.2 mirror: dealer, shrink rule, interval DP.
# --------------------------------------------------------------------------
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


def deal(seed, n, vmax=9):
    r = mulberry32(seed)
    return [1 + int(r() * vmax) for _ in range(n)]


def val_at(v, turn):
    return max(1, v - (turn - 1))


def optimal_spend(coins):
    n = len(coins)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = val_at(coins[i], n)
    for length in range(2, n + 1):
        t = n - length + 1
        for i in range(0, n - length + 1):
            j = i + length - 1
            left = val_at(coins[i], t) + dp[i + 1][j]
            right = val_at(coins[j], t) + dp[i][j - 1]
            dp[i][j] = left if left <= right else right
    return dp[0][n - 1]


def play(coins, purse, policy, rng=None, trace=None):
    """Play one board. Returns (win, spent, purses_after_each_gift).

    trace, when a list, receives the purse value after every gift so the
    caller can assert strict monotonic decrease.
    """
    row = list(coins)
    spent = 0
    turn = 0
    while row:
        turn += 1
        lv = val_at(row[0], turn)
        rv = val_at(row[-1], turn)
        if lv > purse and rv > purse:
            return False, spent, trace
        if policy == "solver":
            take = solver_take(row, turn)
        elif policy == "greedy":
            take = 0 if lv <= rv else 1
        elif policy == "worst":
            take = 0 if lv >= rv else 1
        elif policy == "random":
            choices = []
            if lv <= purse:
                choices.append(0)
            if rv <= purse:
                choices.append(1)
            take = rng.choice(choices)
        elif policy == "never":
            return False, spent, trace
        else:
            raise ValueError("unknown policy %r" % policy)
        cost = lv if take == 0 else rv
        if cost > purse:
            return False, spent, trace
        purse -= cost
        spent += cost
        if trace is not None:
            trace.append(purse)
        if take == 0:
            row.pop(0)
        else:
            row.pop()
    return True, spent, trace


def solver_take_live(cur):
    """Optimal end choice for CURRENT (already shrunk) row values.

    Used by the browser leg, where row() returns post-shrink values.
    Future gifts shrink survivors by 1 per turn, floor 1.
    """
    memo = {}

    def shrink(vals):
        return [v - 1 if v > 1 else 1 for v in vals]

    def solve(vals):
        key = tuple(vals)
        if key in memo:
            return memo[key]
        if len(vals) == 1:
            out = vals[0]
        else:
            out = min(
                vals[0] + solve(shrink(vals[1:])),
                vals[-1] + solve(shrink(vals[:-1])),
            )
        memo[key] = out
        return out

    if len(cur) == 1:
        return 0
    left = cur[0] + solve(shrink(cur[1:]))
    right = cur[-1] + solve(shrink(cur[:-1]))
    return 0 if left <= right else 1


def solver_take(row, turn):
    """Optimal end choice for the dealt row (unshrunk values) at 1-indexed turn.

    row holds dealt values; val_at maps them to the current turn, so the
    recursion advances the turn without touching the values.
    """
    memo = {}

    def solve(vals, t):
        key = (tuple(vals), t)
        if key in memo:
            return memo[key]
        if len(vals) == 1:
            out = val_at(vals[0], t)
        else:
            out = min(
                val_at(vals[0], t) + solve(vals[1:], t + 1),
                val_at(vals[-1], t) + solve(vals[:-1], t + 1),
            )
        memo[key] = out
        return out

    if len(row) == 1:
        return 0
    left = val_at(row[0], turn) + solve(row[1:], turn + 1)
    right = val_at(row[-1], turn) + solve(row[:-1], turn + 1)
    return 0 if left <= right else 1


# --------------------------------------------------------------------------
# Shipped file: CONFIG parse and drift check.
# --------------------------------------------------------------------------
def parse_shipped_config(text):
    m = re.search(r"CONFIG\s*=\s*\{", text)
    if not m:
        return None, "no CONFIG object found"
    depth = 0
    start = m.end() - 1
    end = None
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        return None, "CONFIG object has unbalanced braces"
    body = text[start : end + 1]

    def get_int(key):
        mm = re.search(key + r"\s*:\s*(-?\d+)", body)
        return int(mm.group(1)) if mm else None

    def get_list(key):
        mm = re.search(key + r"\s*:\s*\[([^\]]*)\]", body)
        if not mm:
            return None
        return [int(x) for x in re.findall(r"-?\d+", mm.group(1))]

    def get_str(key):
        mm = re.search(key + r"""\s*:\s*['"]([^'"]+)['"]""", body)
        return mm.group(1) if mm else None

    return (
        {
            "N_PER_LEVEL": get_list("N_PER_LEVEL"),
            "VMIN": get_int("VMIN"),
            "VMAX": get_int("VMAX"),
            "SLACK_PER_LEVEL": get_list("SLACK_PER_LEVEL"),
            "LEVEL_CAP": get_int("LEVEL_CAP"),
            "SHRINK_STEP": get_int("SHRINK_STEP"),
            "SHRINK_FLOOR": get_int("SHRINK_FLOOR"),
            "BEST_KEY": get_str("BEST_KEY"),
        },
        "",
    )


def check_drift(shipped):
    drifts = []
    for key, want in EXPECTED.items():
        got = shipped.get(key)
        if got != want:
            drifts.append("%s: shipped %r != contract %r" % (key, got, want))
    return drifts


# --------------------------------------------------------------------------
# Gate 6 static scan: no waiting-action handler in the shipped file.
# --------------------------------------------------------------------------
WAITING_WORDS = ("pass", "hold", "skip", "undo")


def static_wait_scan(text):
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        code = line.split("//")[0]
        for word in WAITING_WORDS:
            for mm in re.finditer(r"\b%s\b" % word, code, re.IGNORECASE):
                ctx = code[max(0, mm.start() - 60) : mm.end() + 60]
                if re.search(
                    r"addEventListener|onclick|onkey|data-action|\bid\s*=|"
                    r"class\s*=|aria-label|button|key\s*[:=]|action|handler",
                    ctx,
                    re.IGNORECASE,
                ):
                    hits.append("line %d: %s" % (lineno, code.strip()[:120]))
    return hits


# --------------------------------------------------------------------------
# Sim band.
# --------------------------------------------------------------------------
def level_shapes():
    n_list = EXPECTED["N_PER_LEVEL"]
    s_list = EXPECTED["SLACK_PER_LEVEL"]
    return [
        (L, n_list[L - 1], s_list[L - 1]) for L in range(1, EXPECTED["LEVEL_CAP"] + 1)
    ]


def run_sim(manifest):
    per_level = {}
    for L, n, slack in level_shapes():
        seeds = manifest["levels"][str(L)]
        solver_w = greedy_w = 0
        rand_acc = 0.0
        nevers = 0
        spends = []
        solvable = 0
        mono_ok = 0
        for seed in seeds:
            coins = deal(seed, n, EXPECTED["VMAX"])
            opt = optimal_spend(coins)
            purse = opt + slack
            spends.append(opt)
            if opt <= purse:
                solvable += 1
            trace = []
            w, _, _ = play(coins, purse, "solver", trace=trace)
            solver_w += w
            # Every recorded gift must strictly drop the purse, however long
            # the run lasted (BUST traces are shorter but still monotone).
            mono_ok += all(b < a for a, b in zip([purse] + trace[:-1], trace))
            trace = []
            w, _, _ = play(coins, purse, "greedy", trace=trace)
            greedy_w += w
            rng = random.Random(seed ^ 0xE17)
            tot = 0
            for _ in range(3):
                w, _, _ = play(coins, purse, "random", rng=rng)
                tot += w
            rand_acc += tot / 3.0
            w, _, _ = play(coins, purse, "never")
            nevers += w
        per_level[L] = {
            "n": n,
            "slack": slack,
            "solvable": solvable,
            "solver": solver_w / len(seeds),
            "greedy": greedy_w / len(seeds),
            "random": rand_acc / len(seeds),
            "gap_pts": round((solver_w - greedy_w) / len(seeds) * 100, 1),
            "mean_opt": round(statistics.mean(spends), 2),
            "mono_solver": mono_ok,
            "never_wins": nevers,
        }
    return per_level


# --------------------------------------------------------------------------
# Browser leg (gate 7).
# --------------------------------------------------------------------------
def browser_leg(root, game_rel, port, only_vp=None):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        return record("gate7-browser", False, "playwright import failed: %s" % exc)

    webdir = root / "website"
    srv = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--directory", str(webdir)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(
                    "http://127.0.0.1:%d/games/empty-hands.html" % port, timeout=1
                )
                break
            except Exception:  # noqa: BLE001
                if srv.poll() is not None:
                    return record("gate7-browser", False,
                                  "local server exited code %s (port %d busy?)" % (srv.returncode, port))
                time.sleep(0.2)
        else:
            return record("gate7-browser", False, "local server did not start")

        failures = []
        notes = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for vp, mobile in (
                ({"width": 1280, "height": 800}, False),
                ({"width": 375, "height": 667}, True),
            ):
                tag = "mobile" if mobile else "desktop"
                if only_vp and tag != only_vp:
                    continue
                ctx = browser.new_context(
                    viewport=vp, has_touch=mobile, is_mobile=mobile
                )
                page = ctx.new_page()
                console_errors = []
                page.on("console", lambda m: console_errors.append(m) if m.type == "error" else None)
                page_errors = []
                page.on("pageerror", lambda e: page_errors.append(str(e)))
                post_load_requests = []
                monitor = {"on": False}
                page.on(
                    "request",
                    lambda r: post_load_requests.append(r.url) if monitor["on"] else None,
                )
                try:
                    page.goto(
                        "http://127.0.0.1:%d/games/empty-hands.html" % port,
                        wait_until="load",
                        timeout=15000,
                    )
                    page.wait_for_timeout(800)
                    monitor["on"] = True

                    def surf(fn, *args):
                        return page.evaluate("window.__empty.%s(%s)" % (fn, ",".join(
                            json.dumps(a) for a in args)))

                    if page.evaluate("typeof window.__empty") == "undefined":
                        failures.append("%s: window.__empty missing" % tag)
                        ctx.close()
                        continue
                    if surf("state") != "TITLE":
                        failures.append("%s: first load state=%s, want TITLE" % (tag, surf("state")))
                    ow = page.evaluate("document.documentElement.scrollWidth")
                    if ow > vp["width"]:
                        failures.append("%s: TITLE overflow scrollWidth=%s > %s" % (tag, ow, vp["width"]))
                    notes.append("%s TITLE scrollWidth=%s vw=%s" % (tag, ow, vp["width"]))

                    # TITLE -> RUN with a real click on the start button.
                    start_btn = find_button(page, r"start|begin|play", 0)
                    if start_btn is None:
                        failures.append("%s: no start button found" % tag)
                        ctx.close()
                        continue
                    click_handle(page, start_btn, mobile)
                    wait_state(page, "RUN", 5000)
                    if surf("state") != "RUN":
                        failures.append("%s: TITLE->RUN failed, state=%s" % (tag, surf("state")))
                        ctx.close()
                        continue

                    # Full board clear via real end-coin inputs, solver order,
                    # key-press-first with a loud click fallback.
                    gifts = 0
                    stuck = 0
                    attempt = 0
                    while surf("state") == "RUN":
                        row = surf("row")
                        n0 = len(row)
                        purse = surf("purse")
                        take = solver_take_live(row)
                        cost = row[0] if take == 0 else row[-1]  # take is an end, not an index
                        attempt += 1
                        step = "%s L%s gift %s" % (tag, surf("level"), attempt)
                        ok = gift_by_key_first(page, surf, take, mobile, step)
                        if not ok:
                            failures.append("%s: coin click failed at rowLen=%s" % (tag, n0))
                            break
                        if not wait_for_change(page, surf, n0, purse, 2500):
                            # Click may have landed inside the gift animation
                            # lockout (inputs ignored, <=120ms). Retry.
                            stuck += 1
                            if stuck > 6:
                                failures.append("%s: board stopped advancing at rowLen=%s" % (tag, n0))
                                break
                            page.wait_for_timeout(400)
                            continue
                        stuck = 0
                        purse_after = surf("purse")
                        dbg("%s row=%s take=%d cost=%s purse %s->%s" % (
                            tag, row, take, cost, purse, purse_after))
                        if purse_after != purse - cost:
                            failures.append(
                                "%s: purse %s->%s, want -%s" % (tag, purse, purse_after, cost))
                            break
                        gifts += 1
                        if gifts > 40:
                            failures.append("%s: clear loop did not finish" % tag)
                            break
                    if surf("state") != "WIN":
                        failures.append("%s: full clear ended state=%s" % (tag, surf("state")))
                    else:
                        notes.append("%s clear gifts=%s score=%s" % (tag, gifts, surf("score")))
                        # Middle-coin no-op is checked on the next board; level advance first.
                        lvl = surf("level")
                        adv = find_button(page, r"next", 0)
                        if adv is None:
                            failures.append("%s: no WIN advance button" % tag)
                        else:
                            click_handle(page, adv, mobile)
                            wait_state(page, "RUN", 5000)
                            if surf("level") != lvl + 1:
                                failures.append("%s: advance level=%s want %s" % (tag, surf("level"), lvl + 1))
                            else:
                                notes.append("%s advance L%s->L%s" % (tag, lvl, lvl + 1))
                                # Middle tap no-op on the fresh board.
                                if surf("rowLen") >= 3:
                                    p0 = surf("purse")
                                    r0 = surf("rowLen")
                                    tap_middle(page, mobile)
                                    page.wait_for_timeout(400)
                                    if surf("purse") != p0 or surf("rowLen") != r0:
                                        failures.append("%s: middle tap changed state" % tag)
                                    else:
                                        notes.append("%s middle-tap no-op ok" % tag)

                    # Deliberate BUST by worst-end legal play.
                    bust = False
                    for _ in range(6):
                        if surf("state") == "BUST":
                            bust = True
                            break
                        if surf("state") == "WIN":
                            adv = find_button(page, r"next", 0)
                            if adv is None:
                                break
                            click_handle(page, adv, mobile)
                            wait_state(page, "RUN", 5000)
                        if surf("state") == "TITLE":
                            start_btn = find_button(page, r"start|begin|play", 0)
                            if start_btn is None:
                                break
                            click_handle(page, start_btn, mobile)
                            wait_state(page, "RUN", 5000)
                        if surf("state") != "RUN":
                            page.evaluate("window.__empty.reset()")
                            page.wait_for_timeout(300)
                            start_btn = find_button(page, r"start|begin|play", 0)
                            if start_btn is None:
                                break
                            click_handle(page, start_btn, mobile)
                            wait_state(page, "RUN", 5000)
                        steps = 0
                        while surf("state") == "RUN" and steps < 40:
                            row = surf("row")
                            n0 = len(row)
                            purse = surf("purse")
                            lv = row[0]
                            rv = row[-1]
                            afford = [i for i, c in ((0, lv), (1, rv)) if c <= purse]
                            if not afford:
                                # Neither end affordable: BUST evaluates now.
                                page.wait_for_timeout(800)
                                break
                            # Worst affordable end: burn the purse as fast as
                            # legally possible so the bust is deliberate.
                            take = max(afford, key=lambda i: lv if i == 0 else rv)
                            step = "%s L%s gift %s" % (tag, surf("level"), steps + 1)
                            if not click_end(page, take, mobile, n0, step):
                                break
                            wait_for_change(page, surf, n0, purse, 2500)
                            steps += 1
                        if surf("state") == "BUST":
                            bust = True
                            break
                        page.evaluate("window.__empty.reset()")
                        page.wait_for_timeout(300)
                    if not bust:
                        failures.append("%s: deliberate BUST never reached" % tag)
                    else:
                        notes.append("%s deliberate BUST ok" % tag)
                        best = surf("best")
                        score = surf("score")
                        if best < score or best <= 0:
                            failures.append("%s: best=%s score=%s" % (tag, best, score))
                        else:
                            # Reload is harness-induced traffic, not page traffic:
                            # pause monitoring across it and clear the buffer.
                            monitor["on"] = False
                            page.reload(wait_until="load", timeout=15000)
                            page.wait_for_timeout(800)
                            del post_load_requests[:]
                            monitor["on"] = True
                            if surf("best") != best:
                                failures.append(
                                    "%s: best persistence %s != %s" % (tag, surf("best"), best))
                            else:
                                notes.append("%s best=%s persists" % (tag, best))

                    ow = page.evaluate("document.documentElement.scrollWidth")
                    if ow > vp["width"]:
                        failures.append("%s: end overflow scrollWidth=%s" % (tag, ow))
                    if console_errors or page_errors:
                        failures.append(
                            "%s: console errors %s %s"
                            % (tag, [e.text for e in console_errors], page_errors))
                    else:
                        notes.append("%s console errors 0" % tag)
                    if post_load_requests:
                        failures.append("%s: post-load net %s" % (tag, post_load_requests[:5]))
                    else:
                        notes.append("%s post-load net 0" % tag)
                except Exception as exc:  # noqa: BLE001
                    failures.append("%s: exception %s" % (tag, exc))
                finally:
                    ctx.close()
            browser.close()
        detail = "; ".join(notes)
        if failures:
            return record("gate7-browser", False, " | ".join(failures) + " || " + detail)
        return record("gate7-browser", True, detail)
    finally:
        # Port-scoped cleanup only. Prefer fuser (matches the port, never a
        # cmdline) where present; otherwise pkill with a bracketed pattern so
        # the invoking shell cannot match itself. Never a broad kill.
        import shutil
        if shutil.which("fuser"):
            subprocess.run(["fuser", "-k", "%d/tcp" % port],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["pkill", "-f", "http[.]server %d" % port],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------
# Browser leg gate 8: EMPTY HANDS play counter (Story 154, Session 69).
# Fresh profile, real clicks/keys, both viewports, in order: fresh boot 0,
# Start 1, reload keeps 1, WIN advance +0, BUST restart exactly +1,
# localStorage JSON number matching the probe, corrupt seeds boot to 0,
# blocked storage increments in memory silently. A pre-153 file (no #plays
# line, no plays() probe) FAILs here; that red is the mutation control,
# not a defect. Zero website bytes: this harness file is the only touch.
# --------------------------------------------------------------------------
COUNT_KEY = "flambeee-empty-hands-plays"
COUNT_CORRUPT_SEEDS = ["abc", "-1", "1.5", "null", "{bad json"]
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


def gate8_surf(page):
    def surf(fn, *args):
        return page.evaluate("window.__empty.%s(%s)" % (fn, ",".join(
            json.dumps(a) for a in args)))
    return surf


def gate8_line(page):
    """HUD plays line text ('Plays on this browser: N'), or None."""
    try:
        el = page.query_selector("#plays")
    except Exception:  # noqa: BLE001
        return None
    if el is None:
        return None
    try:
        txt = el.evaluate(
            "e => e.parentElement ? e.parentElement.innerText : e.innerText")
    except Exception:  # noqa: BLE001
        return None
    if txt is None:
        return None
    return " ".join(str(txt).split())


def gate8_probe(page):
    """__empty.plays(), or None when the probe is absent/broken."""
    try:
        v = page.evaluate(
            "typeof window.__empty !== 'undefined'"
            " && typeof window.__empty.plays === 'function'"
            " ? window.__empty.plays() : 'MISSING'")
    except Exception:  # noqa: BLE001
        return None
    return None if v == "MISSING" else v


def gate8_click_start(page, mobile):
    btn = find_button(page, r"start|begin|play", 0)
    if btn is None:
        return False
    click_handle(page, btn, mobile)
    return wait_state(page, "RUN", 5000)


def gate8_gifts_until_end(page, surf, tag, mobile, failures, mode):
    """Drive RUN toward WIN (mode 'solver') or BUST (mode 'worst').

    Returns the state reached. Key-press-first with the same loud
    FALLBACK discipline as gate7.
    """
    steps = 0
    stuck = 0
    while surf("state") == "RUN" and steps < 40:
        row = surf("row")
        n0 = len(row)
        purse = surf("purse")
        if mode == "solver":
            take = solver_take_live(row)
        else:
            lv, rv = row[0], row[-1]
            afford = [i for i, c in ((0, lv), (1, rv)) if c <= purse]
            if not afford:
                # Neither end affordable: BUST evaluates now.
                page.wait_for_timeout(800)
                break
            take = max(afford, key=lambda i: lv if i == 0 else rv)
        step = "%s L%s gift %s" % (tag, surf("level"), steps + 1)
        if mode == "solver":
            ok = gift_by_key_first(page, surf, take, mobile, step)
        else:
            ok = click_end(page, take, mobile, n0, step)
        if not ok:
            failures.append("%s: counter %s stalled at rowLen=%s" % (tag, mode, n0))
            return surf("state")
        if not wait_for_change(page, surf, n0, purse, 2500):
            # Gift-animation input lockout (<=120ms). Retry.
            stuck += 1
            if stuck > 6:
                failures.append(
                    "%s: counter %s stopped advancing at rowLen=%s" % (tag, mode, n0))
                return surf("state")
            page.wait_for_timeout(400)
            continue
        stuck = 0
        steps += 1
    return surf("state")


def browser_leg_gate8(root, port, only_vp=None):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        return record("gate8-plays-counter", False, "playwright import failed: %s" % exc)

    webdir = root / "website"
    srv = None
    started = False
    for _ in range(3):
        srv = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port), "--directory", str(webdir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(50):
            try:
                urllib.request.urlopen(
                    "http://127.0.0.1:%d/games/empty-hands.html" % port, timeout=1
                )
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
        return record("gate8-plays-counter", False,
                      "local server did not start (port %d busy?)" % port)
    try:
        failures = []
        notes = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for vp, mobile in (
                ({"width": 1280, "height": 800}, False),
                ({"width": 375, "height": 667}, True),
            ):
                tag = "mobile" if mobile else "desktop"
                if only_vp and tag != only_vp:
                    continue
                url = "http://127.0.0.1:%d/games/empty-hands.html" % port
                try:
                    # --- fresh profile: boot 0, Start 1, reload keeps 1 ---
                    ctx = browser.new_context(
                        viewport=vp, has_touch=mobile, is_mobile=mobile
                    )
                    page = ctx.new_page()
                    cerr = []
                    perr = []
                    page.on("console",
                            lambda m: cerr.append(m) if m.type == "error" else None)
                    page.on("pageerror", lambda e: perr.append(str(e)))
                    surf = gate8_surf(page)
                    page.goto(url, wait_until="load", timeout=15000)
                    page.wait_for_timeout(800)
                    if page.evaluate("typeof window.__empty") == "undefined":
                        failures.append("%s: window.__empty missing" % tag)
                        ctx.close()
                        continue
                    if gate8_line(page) is None:
                        failures.append(
                            "%s: no #plays line on fresh boot (pre-153 file?)" % tag)
                        ctx.close()
                        continue
                    if gate8_line(page) != "Plays on this browser: 0":
                        failures.append(
                            "%s: fresh line %r, want 'Plays on this browser: 0'"
                            % (tag, gate8_line(page)))
                        ctx.close()
                        continue
                    if gate8_probe(page) is None:
                        failures.append("%s: __empty.plays() probe missing" % tag)
                        ctx.close()
                        continue
                    if gate8_probe(page) != 0:
                        failures.append(
                            "%s: fresh probe %r, want 0" % (tag, gate8_probe(page)))
                        ctx.close()
                        continue
                    notes.append("%s fresh 0 ok" % tag)
                    if not gate8_click_start(page, mobile) or surf("state") != "RUN":
                        failures.append("%s: Start click did not reach RUN" % tag)
                        ctx.close()
                        continue
                    if (gate8_line(page) != "Plays on this browser: 1"
                            or gate8_probe(page) != 1):
                        failures.append(
                            "%s: after Start line=%r probe=%r, want 1/1"
                            % (tag, gate8_line(page), gate8_probe(page)))
                        ctx.close()
                        continue
                    notes.append("%s start 1 ok" % tag)
                    page.reload(wait_until="load", timeout=15000)
                    page.wait_for_timeout(800)
                    if surf("state") != "TITLE":
                        failures.append(
                            "%s: post-reload state=%s, want TITLE" % (tag, surf("state")))
                    if (gate8_line(page) != "Plays on this browser: 1"
                            or gate8_probe(page) != 1):
                        failures.append(
                            "%s: after reload line=%r probe=%r, want 1/1"
                            % (tag, gate8_line(page), gate8_probe(page)))
                    else:
                        notes.append("%s reload keeps 1 ok" % tag)
                    if cerr or perr:
                        failures.append(
                            "%s: reload-flow console errors %s %s"
                            % (tag, [e.text for e in cerr], perr))
                    else:
                        notes.append("%s reload-flow console errors 0" % tag)
                    ctx.close()

                    # --- fresh profile: Start 1, WIN advance +0,
                    #     BUST restart exactly +1, storage matches probe ---
                    ctx = browser.new_context(
                        viewport=vp, has_touch=mobile, is_mobile=mobile
                    )
                    page = ctx.new_page()
                    cerr = []
                    perr = []
                    page.on("console",
                            lambda m: cerr.append(m) if m.type == "error" else None)
                    page.on("pageerror", lambda e: perr.append(str(e)))
                    surf = gate8_surf(page)
                    page.goto(url, wait_until="load", timeout=15000)
                    page.wait_for_timeout(800)
                    if (gate8_line(page) != "Plays on this browser: 0"
                            or gate8_probe(page) != 0):
                        failures.append("%s: win-flow fresh boot not 0/0" % tag)
                        ctx.close()
                        continue
                    if not gate8_click_start(page, mobile) or surf("state") != "RUN":
                        failures.append("%s: win-flow Start did not reach RUN" % tag)
                        ctx.close()
                        continue
                    if gate8_probe(page) != 1:
                        failures.append(
                            "%s: win-flow Start probe=%r, want 1" % (tag, gate8_probe(page)))
                        ctx.close()
                        continue
                    if gate8_gifts_until_end(
                            page, surf, tag, mobile, failures, "solver") != "WIN":
                        failures.append(
                            "%s: solver did not reach WIN (state=%s)"
                            % (tag, surf("state")))
                        ctx.close()
                        continue
                    before = gate8_probe(page)
                    adv = find_button(page, r"next", 0)
                    if adv is None:
                        failures.append("%s: no WIN advance button" % tag)
                        ctx.close()
                        continue
                    lvl = surf("level")
                    click_handle(page, adv, mobile)
                    wait_state(page, "RUN", 5000)
                    if surf("level") != lvl + 1:
                        failures.append(
                            "%s: advance level=%s want %s" % (tag, surf("level"), lvl + 1))
                        ctx.close()
                        continue
                    if gate8_probe(page) != before:
                        failures.append(
                            "%s: WIN advance moved probe %r->%r, want no change"
                            % (tag, before, gate8_probe(page)))
                        ctx.close()
                        continue
                    notes.append("%s win-advance no-op at %r ok" % (tag, before))
                    bust = surf("state") == "BUST"
                    for _ in range(6):
                        if bust:
                            break
                        st = surf("state")
                        if st == "WIN":
                            b = find_button(page, r"next", 0)
                            if b is None:
                                failures.append("%s: bust-flow no advance button" % tag)
                                break
                            prew = gate8_probe(page)
                            click_handle(page, b, mobile)
                            wait_state(page, "RUN", 5000)
                            if gate8_probe(page) != prew:
                                failures.append(
                                    "%s: bust-flow advance moved probe" % tag)
                                break
                        elif st == "RUN":
                            if gate8_gifts_until_end(
                                    page, surf, tag, mobile, failures, "worst") == "BUST":
                                bust = True
                                break
                        else:
                            failures.append(
                                "%s: bust-flow unexpected state %s" % (tag, st))
                            break
                    if not bust:
                        bust = surf("state") == "BUST"
                    if not bust:
                        failures.append("%s: deliberate BUST never reached" % tag)
                        ctx.close()
                        continue
                    notes.append("%s deliberate BUST ok" % tag)
                    preR = gate8_probe(page)
                    if preR != 1:
                        failures.append(
                            "%s: pre-restart probe=%r, want 1" % (tag, preR))
                        ctx.close()
                        continue
                    rst = find_button(page, r"new run", 0)
                    if rst is None:
                        failures.append("%s: no BUST restart button" % tag)
                        ctx.close()
                        continue
                    click_handle(page, rst, mobile)
                    wait_state(page, "RUN", 5000)
                    if surf("state") != "RUN":
                        failures.append("%s: restart did not reach RUN" % tag)
                        ctx.close()
                        continue
                    postR = gate8_probe(page)
                    if surf("level") != 1:
                        failures.append(
                            "%s: restart level=%s, want 1" % (tag, surf("level")))
                    if postR != 2:
                        failures.append(
                            "%s: restart moved probe %r->%r, want exactly +1 (2)"
                            % (tag, preR, postR))
                        ctx.close()
                        continue
                    notes.append("%s bust-restart +1 to 2 ok" % tag)
                    try:
                        raw = page.evaluate(
                            "localStorage.getItem(%s)" % json.dumps(COUNT_KEY))
                    except Exception as exc:  # noqa: BLE001
                        failures.append("%s: storage read threw: %s" % (tag, exc))
                        ctx.close()
                        continue
                    try:
                        sval = json.loads(raw) if raw is not None else None
                    except Exception:  # noqa: BLE001
                        sval = "BADJSON:%r" % (raw,)
                    if isinstance(sval, float) and sval.is_integer():
                        sval = int(sval)
                    if isinstance(sval, bool) or not isinstance(sval, int):
                        failures.append(
                            "%s: storage %r not a JSON number" % (tag, raw))
                        ctx.close()
                        continue
                    if sval != postR:
                        failures.append(
                            "%s: storage %r != probe %r" % (tag, sval, postR))
                    else:
                        notes.append("%s storage %r matches probe ok" % (tag, sval))
                    if cerr or perr:
                        failures.append(
                            "%s: win-flow console errors %s %s"
                            % (tag, [e.text for e in cerr], perr))
                    else:
                        notes.append("%s win-flow console errors 0" % tag)
                    ctx.close()

                    # --- corrupt seeds boot to 0 ---
                    ctx = browser.new_context(
                        viewport=vp, has_touch=mobile, is_mobile=mobile
                    )
                    page = ctx.new_page()
                    cerr = []
                    perr = []
                    page.on("console",
                            lambda m: cerr.append(m) if m.type == "error" else None)
                    page.on("pageerror", lambda e: perr.append(str(e)))
                    page.goto(url, wait_until="load", timeout=15000)
                    page.wait_for_timeout(800)
                    for seed in COUNT_CORRUPT_SEEDS:
                        page.evaluate(
                            "localStorage.setItem(%s, %s)"
                            % (json.dumps(COUNT_KEY), json.dumps(seed)))
                        page.reload(wait_until="load", timeout=15000)
                        page.wait_for_timeout(800)
                        ln = gate8_line(page)
                        pv = gate8_probe(page)
                        if ln != "Plays on this browser: 0" or pv != 0:
                            failures.append(
                                "%s: corrupt seed %r booted line=%r probe=%r, want 0/0"
                                % (tag, seed, ln, pv))
                        else:
                            notes.append("%s corrupt %r -> 0 ok" % (tag, seed))
                    if cerr or perr:
                        failures.append(
                            "%s: corrupt-flow console errors %s %s"
                            % (tag, [e.text for e in cerr], perr))
                    else:
                        notes.append("%s corrupt-flow console errors 0" % tag)
                    ctx.close()

                    # --- blocked storage: in-memory increment, silent ---
                    ctx = browser.new_context(
                        viewport=vp, has_touch=mobile, is_mobile=mobile
                    )
                    ctx.add_init_script(BLOCKED_STORAGE_SCRIPT)
                    page = ctx.new_page()
                    cerr = []
                    perr = []
                    page.on("console",
                            lambda m: cerr.append(m) if m.type == "error" else None)
                    page.on("pageerror", lambda e: perr.append(str(e)))
                    surf = gate8_surf(page)
                    try:
                        page.goto(url, wait_until="load", timeout=15000)
                        page.wait_for_timeout(800)
                    except Exception as exc:  # noqa: BLE001
                        failures.append(
                            "%s: blocked-storage load threw: %s" % (tag, exc))
                        ctx.close()
                        continue
                    try:
                        usable = page.evaluate(
                            "(function(){ try { localStorage.getItem('x');"
                            " return 'USABLE'; } catch (e) { return 'BLOCKED'; } })()")
                    except Exception:  # noqa: BLE001
                        usable = "BLOCKED"
                    if usable != "BLOCKED":
                        failures.append(
                            "%s: storage not blocked, degraded mode unproven" % tag)
                        ctx.close()
                        continue
                    if (gate8_line(page) != "Plays on this browser: 0"
                            or gate8_probe(page) != 0):
                        failures.append(
                            "%s: blocked-storage fresh boot not 0/0" % tag)
                        ctx.close()
                        continue
                    try:
                        started = gate8_click_start(page, mobile)
                    except Exception as exc:  # noqa: BLE001
                        failures.append(
                            "%s: blocked-storage Start threw: %s" % (tag, exc))
                        ctx.close()
                        continue
                    if not started or surf("state") != "RUN":
                        failures.append(
                            "%s: blocked-storage Start did not reach RUN" % tag)
                        ctx.close()
                        continue
                    if (gate8_line(page) != "Plays on this browser: 1"
                            or gate8_probe(page) != 1):
                        failures.append(
                            "%s: blocked-storage in-memory line=%r probe=%r, want 1/1"
                            % (tag, gate8_line(page), gate8_probe(page)))
                    else:
                        notes.append("%s blocked-storage in-memory 1 ok" % tag)
                    if cerr or perr:
                        failures.append(
                            "%s: blocked-storage console errors %s %s"
                            % (tag, [e.text for e in cerr], perr))
                    else:
                        notes.append("%s blocked-storage silent ok" % tag)
                    ctx.close()
                except Exception as exc:  # noqa: BLE001
                    failures.append("%s: exception %s" % (tag, exc))
            browser.close()
        detail = "; ".join(notes)
        if failures:
            return record("gate8-plays-counter", False, " | ".join(failures) + " || " + detail)
        return record("gate8-plays-counter", True, detail)
    finally:
        # Port-scoped cleanup only. Prefer fuser (matches the port, never a
        # cmdline) where present; otherwise pkill with a bracketed pattern so
        # the invoking shell cannot match itself. Never a broad kill.
        import shutil
        if shutil.which("fuser"):
            subprocess.run(["fuser", "-k", "%d/tcp" % port],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["pkill", "-f", "http[.]server %d" % port],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_state(page, want, timeout_ms):
    end = time.time() + timeout_ms / 1000.0
    while time.time() < end:
        try:
            if page.evaluate("window.__empty.state()") == want:
                return True
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(100)
    return False


def wait_for_change(page, surf, n0, purse0, timeout_ms):
    end = time.time() + timeout_ms / 1000.0
    while time.time() < end:
        try:
            if surf("rowLen") != n0 or surf("purse") != purse0:
                return True
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(80)
    return False


COIN_SELECTORS = [
    "[data-coin]",
    "[data-idx]",
    "[data-index]",
    ".coin",
    "#row button",
    "#row > *",
    "#coins button",
    "#coins > *",
]

DEBUG = False


def dbg(msg):
    if DEBUG:
        print("DBG %s" % msg, flush=True)


def coin_handles(page, n0):
    for sel in COIN_SELECTORS:
        try:
            els = page.query_selector_all(sel)
        except Exception:  # noqa: BLE001
            continue
        vis = [e for e in els if e.is_visible()]
        if len(vis) == n0 and n0 > 0:
            return vis
    return []


def click_end(page, take, mobile, n0, step):
    els = coin_handles(page, n0)
    if not els:
        # Fallback: contracted keyboard input (still a real input path).
        print("FALLBACK click->key at %s" % step, flush=True)
        page.keyboard.press("ArrowLeft" if take == 0 else "ArrowRight")
        return True
    boxes = [(e.bounding_box(), e) for e in els]
    boxes = [(b, e) for b, e in boxes if b]
    if len(boxes) != n0:
        print("FALLBACK click->key at %s" % step, flush=True)
        page.keyboard.press("ArrowLeft" if take == 0 else "ArrowRight")
        return True
    boxes.sort(key=lambda be: be[0]["x"])
    el = boxes[0][1] if take == 0 else boxes[-1][1]
    dbg("click take=%d xs=%s" % (take, [round(b["x"]) for b, _ in boxes]))
    click_handle(page, el, mobile)
    return True


def gift_by_key_first(page, surf, take, mobile, step):
    """Key-press-first gameplay step; degrades loudly to a click.

    <step> is "<desktop|mobile> L<level> gift <n>" with n the 1-indexed
    gift attempt on the current board. Prints exactly one
    FALLBACK key->click line per degraded step, never debug-gated.
    """
    n0 = surf("rowLen")
    purse0 = surf("purse")
    # Let any gift-animation input lockout (<=120ms) clear so a healthy
    # key press is never swallowed and misreported as a degradation.
    page.wait_for_timeout(150)
    page.keyboard.press("ArrowLeft" if take == 0 else "ArrowRight")
    if wait_for_change(page, surf, n0, purse0, 1500):
        return True
    print("FALLBACK key->click at %s" % step, flush=True)
    return click_end(page, take, mobile, n0, step)


def tap_middle(page, mobile):
    try:
        n0 = page.evaluate("window.__empty.rowLen()")
    except Exception:  # noqa: BLE001
        return
    els = coin_handles(page, n0)
    if not els or len(els) < 3:
        return
    boxes = [(e.bounding_box(), e) for e in els]
    boxes = [(b, e) for b, e in boxes if b]
    if len(boxes) < 3:
        return
    boxes.sort(key=lambda be: be[0]["x"])
    click_handle(page, boxes[len(boxes) // 2][1], mobile)


def find_button(page, pattern, index=0):
    try:
        btns = page.query_selector_all("button")
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


def click_handle(page, handle, mobile):
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


# --------------------------------------------------------------------------
# Main gate.
# --------------------------------------------------------------------------
def main():
    import os
    global DEBUG
    DEBUG = os.environ.get("KAI_DEBUG") == "1"
    sim_only = False
    port = BROWSER_PORT
    only_vp = None
    # Narrowing flags in argv order; each prints one SKIPPED line (Story 152).
    skip_flags = []  # list of (flag_literal, what)
    for arg in sys.argv[1:]:
        if arg == "--sim-only":
            sim_only = True
            skip_flags.append((arg, "browser leg"))
        elif arg.startswith("--port="):
            raw = arg.split("=", 1)[1]
            try:
                port = int(raw)
            except ValueError:
                print("FAIL: bad --port value %r: not an integer (reason: %s)" % (raw, arg))
                print("RESULT: FAIL (exit 1)")
                return 1
            skip_flags.append((arg, "default-port serve"))
        elif arg.startswith("--viewport="):
            only_vp = arg.split("=", 1)[1]
            skip_flags.append((arg, "all viewports except %s" % only_vp))
    root = repo_root()
    game = root / GAME_REL
    manifest_path = root / MANIFEST_NAME

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

    if not manifest_path.exists():
        print("FAIL: seed manifest absent: %s" % manifest_path)
        print("RESULT: FAIL (exit 1)")
        return 1
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as exc:  # noqa: BLE001
        print("FAIL: seed manifest unreadable: %s" % exc)
        print("RESULT: FAIL (exit 1)")
        return 1

    # AC-2: manifest schedule.
    ok_manifest = (
        manifest.get("seed_base") == SEED_BASE
        and manifest.get("runs_per_level") == RUNS_PER_LEVEL
        and set(manifest.get("levels", {}).keys()) == {"1", "2", "3", "4", "5", "6"}
        and all(
            manifest["levels"][str(L)] == [SEED_BASE + L * 1000 + s for s in range(RUNS_PER_LEVEL)]
            for L in range(1, 7)
        )
    )
    record("manifest-schedule", ok_manifest,
           "SEED_BASE 3000, L*1000+s, 200/level" if ok_manifest else "manifest mismatch")
    if not ok_manifest:
        print("FAIL: manifest does not replay M.9 schedule")
        print("RESULT: FAIL (exit 1)")
        return 1

    # FR-2 drift check.
    shipped, err = parse_shipped_config(text)
    if shipped is None:
        record("config-drift", False, err)
        print("FAIL: config-drift: %s" % err)
        print("RESULT: FAIL (exit 1)")
        return 1
    drifts = check_drift(shipped)
    record("config-drift", not drifts, "; ".join(drifts) if drifts else "CONFIG matches M.3")
    if drifts:
        for d in drifts:
            print("FAIL: drift: %s" % d)
        print("RESULT: FAIL (exit 1)")
        return 1

    per_level = run_sim(manifest)

    # Gate 1: solvable 200/200 every level.
    g1 = all(v["solvable"] == RUNS_PER_LEVEL for v in per_level.values())
    record("gate1-solvable", g1,
           ",".join("L%d %d/200" % (L, v["solvable"]) for L, v in per_level.items()))

    # Gates 2-4 on the hardest level L6.
    l6 = per_level[6]
    g2 = 0.15 <= l6["greedy"] <= 0.60
    record("gate2-greedy-band", g2, "L6 greedy %.2f in [0.15,0.60]" % l6["greedy"])
    g3 = l6["gap_pts"] >= 25
    record("gate3-skill-gap", g3, "L6 solver-greedy gap %.1f pts" % l6["gap_pts"])
    g4 = l6["random"] <= 0.10
    record("gate4-random-cap", g4, "L6 random %.3f <= 0.10" % l6["random"])

    # Gate 5: purse strictly decreases on every gift (solver traces).
    g5 = all(v["mono_solver"] == RUNS_PER_LEVEL for v in per_level.values())
    record("gate5-monotone", g5,
           ",".join("L%d %d/200" % (L, v["mono_solver"]) for L, v in per_level.items()))

    # Gate 6: never-give 0/200 plus static scan.
    g6a = all(v["never_wins"] == 0 for v in per_level.values())
    hits = static_wait_scan(text)
    g6 = g6a and not hits
    record("gate6-no-waiting", g6,
           "never-give 0/200%s" % ("; static hits: %s" % hits if hits else ", static scan clean"))

    if not sim_only:
        if only_vp is not None and only_vp not in ("desktop", "mobile"):
            record("gate7-browser", False,
                   "unknown viewport %r in --viewport=%s (want desktop|mobile)"
                   % (only_vp, only_vp))
        else:
            browser_leg(root, game, port, only_vp)
            browser_leg_gate8(root, port, only_vp)

    # ---- report ----
    for flag, what in skip_flags:
        print("SKIPPED: %s (reason: %s)" % (what, flag))
    print("EMPTY HANDS gate (Story 144)  interpreter: team venv python")
    print("seed set: SEED_BASE 3000, L*1000+s, 200 runs/level")
    print("")
    print(" L | n | slack | solver | greedy | random | gap_pts | mean_opt | solv/monotone")
    for L, v in per_level.items():
        print(" L%d | %2d | %3d | %.2f | %.2f | %.3f | %6.1f | %8.2f | %d/200 %d/200" % (
            L, v["n"], v["slack"], v["solver"], v["greedy"], v["random"],
            v["gap_pts"], v["mean_opt"], v["solvable"], v["mono_solver"]))
    print("")
    code = 0
    for name, passed, detail in CHECKS:
        print("CHECK %s: %s (exit %d)%s" % (name, "PASS" if passed else "FAIL",
                                            0 if passed else 1,
                                            " " + detail if detail else ""))
        if not passed:
            code = 1
    if code == 0 and skip_flags:
        code = 3
    print("RESULT: %s (exit %d)" % (
        "PASS" if code == 0 else ("SKIP" if code == 3 else "FAIL"), code))
    return code


if __name__ == "__main__":
    sys.exit(main())
