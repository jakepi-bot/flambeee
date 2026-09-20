#!/usr/bin/env python3
"""Session 22 Story 040 browser verification (Scout).

Runs the pinned Story 040 artifact (src/cinder.html at commit 28e5c49) over http
in real Chromium via Playwright, covering the 14 BDD scenarios plus negative
tests. The main-build artifact (77acd25) is used as a byte-safety control.

Usage: /home/jake/.openclaw/workspace/.venv/bin/python3 qa-story040.py
Env: QA_ART_DIR (default = script dir), QA_PORT (default 8731)
"""
import http.server
import json
import os
import re
import socketserver
import sys
import threading
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ART_DIR = os.environ.get("QA_ART_DIR", HERE)
PORT = int(os.environ.get("QA_PORT", "8731"))
BASE = "http://127.0.0.1:%d" % PORT
TODAY = int(time.time() * 1000 // 86400000)

SAVE_KEY = "flambeee-cinder-save"
DAY_KEY = "flambeee-cinder-day"

RESULTS = []
COUNT = {"pass": 0, "fail": 0}


def check(cond, name, detail=""):
    ok = bool(cond)
    RESULTS.append(ok)
    if ok:
        COUNT["pass"] += 1
    else:
        COUNT["fail"] += 1
    line = ("PASS" if ok else "FAIL") + ": " + name
    if detail != "":
        line += "  | " + str(detail)
    print(line, flush=True)
    return ok


def group(name):
    print("\n--- %s ---" % name, flush=True)


# ---------------------------------------------------------------- artifacts
LEGACY_CHAR = {
    "name": "ScoutX", "level": 3, "xp": 70, "hp": 24, "maxHp": 24,
    "attack": 6, "defense": 3, "gold": 120, "bank": 300,
    "weapon": 1, "armor": 1, "wins": 9, "losses": 2, "deaths": 1,
}
LEGACY_CHAR_KEYS = sorted(LEGACY_CHAR.keys())


def day(**kw):
    d = {
        "dayIndex": TODAY, "fightsUsed": 0, "innHealsUsed": 0,
        "quest": {"progress": 0, "completed": False, "rewarded": False},
        "completedQuests": [],
    }
    d.update(kw)
    return d


def J(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)


WRAPPER = """
window.__writes = [];
(function () {
  var orig = Storage.prototype.setItem;
  Storage.prototype.setItem = function (k, v) {
    window.__writes.push({ k: String(k), v: String(v), stack: (new Error()).stack || '' });
    return orig.call(this, k, v);
  };
})();
"""

THROW_ALL = """
Object.defineProperty(window, 'localStorage', {
  configurable: true,
  get: function () { throw new Error('storage denied (private mode)'); }
});
"""

THROW_SET = """
Storage.prototype.setItem = function () { throw new Error('quota exceeded'); };
"""


def lit(v):
    """JS string literal. A str is treated as raw JSON text; anything else is encoded."""
    if isinstance(v, str):
        return json.dumps(v)
    return json.dumps(json.dumps(v))


def seed_script(save=None, day_raw=None, marker="qa22-seed"):
    parts = []
    if save is not None:
        parts.append('localStorage.setItem("%s", %s);' % (SAVE_KEY, lit(save)))
    if day_raw is not None:
        parts.append('localStorage.setItem("%s", %s);' % (DAY_KEY, lit(day_raw)))
    body = "\n      ".join(parts)
    return """
(function () {
  try {
    if (!sessionStorage.getItem('%s')) {
      %s
      sessionStorage.setItem('%s', '1');
    }
  } catch (e) { window.__seedError = String(e); }
  if (window.__writes) { window.__writes.length = 0; }
})();
""" % (marker, body, marker)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    handler = lambda *a, **kw: Quiet(*a, directory=ART_DIR, **kw)
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def open_page(browser, save=None, day_raw=None, viewport=None, touch=False,
              throw_all=False, throw_set=False, artifact="cinder.html"):
    ctx = browser.new_context(viewport=viewport or {"width": 1280, "height": 800},
                              has_touch=touch)
    ctx.add_init_script(script=WRAPPER)
    if save is not None or day_raw is not None:
        ctx.add_init_script(script=seed_script(save, day_raw))
    if throw_all:
        ctx.add_init_script(script=THROW_ALL)
    elif throw_set:
        ctx.add_init_script(script=THROW_SET)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("%s/%s" % (BASE, artifact), wait_until="load")
    page.wait_for_timeout(150)
    return ctx, page, errors


def txt(page):
    return page.inner_text("#display")


def stored(page):
    return page.evaluate(
        "() => ({save: localStorage.getItem('%s'), day: localStorage.getItem('%s')})"
        % (SAVE_KEY, DAY_KEY))


def writes(page):
    return page.evaluate("() => window.__writes")


def tap_row(page, action):
    box = page.locator('.menu-row[data-action="%s"]' % action).first.bounding_box()
    assert box, "row %s has no box" % action
    page.touchscreen.tap(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_timeout(120)


def overflow(page):
    return page.evaluate("""() => {
      const d = document.getElementById('display');
      const b = document.querySelector('.boxed-menu');
      return {
        docScroll: document.documentElement.scrollWidth,
        win: window.innerWidth,
        displayScroll: d ? d.scrollWidth : null,
        displayClient: d ? d.clientWidth : null,
        boxScroll: b ? b.scrollWidth : null,
        boxClient: b ? b.clientWidth : null,
      };
    }""")


EM_DASH = "\u2014"
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF"
    "\U0001F1E6-\U0001F1FF\uFE0F\u2705\u274C\u2B50\u2764\u2728]")


def scan_copy(text):
    return (EM_DASH in text, sorted(set(EMOJI_RE.findall(text))))


def main():
    httpd = serve()
    print("serving %s on %s (todayIdx=%d)" % (ART_DIR, BASE, TODAY), flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ================================================== S1
        group("S1 one fully missed day: summary once, all four facts")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2, fightsUsed=4)))
        t = txt(page)
        check("WELCOME BACK" in t, "S1 summary renders", t.splitlines()[0] if t else "")
        check(t.count("WELCOME BACK") == 1, "S1 summary header appears exactly once")
        check("You were away for a day." in t, "S1 fact 1 days away (one-day phrasing)")
        check("1 quest went uncompleted while you were gone." in t, "S1 fact 2 quests missed")
        check("Your streak is broken." in t, "S1 fact 3 streak status explicit")
        check("Today's quest: " in t, "S1 fact 4 today's quest pointer")
        quest_lines = [l for l in t.splitlines() if l.startswith("Today's quest: ")]
        check(len(quest_lines) == 1, "S1 exactly one today's-quest line", quest_lines)
        quest_line = quest_lines[0] if quest_lines else ""
        check(len(quest_line) > len("Today's quest: "), "S1 pointer names an objective",
              quest_line)
        check("Back to Town" in t, "S1 Back to Town action present")
        check(errs == [], "S1 no page errors", errs)
        # character save untouched by the whole load
        s = stored(page)
        check(json.loads(s["save"]) == LEGACY_CHAR, "S1 character save untouched by load",
              sorted(json.loads(s["save"]).keys()))
        ctx.close()

        # ================================================== S2
        group("S2 same-day return and next-day return: no summary")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY)))
        t = txt(page)
        check("WELCOME BACK" not in t, "S2 same-day return shows no summary")
        check("TOWN SQUARE" in t, "S2 hub renders normally", t.splitlines()[0])
        check(len(page.locator(".menu-row").all()) >= 9, "S2 hub rows intact",
              page.locator(".menu-row").count())
        check(errs == [], "S2 no page errors", errs)
        ctx.close()

        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 1, fightsUsed=7)))
        t = txt(page)
        check("WELCOME BACK" not in t, "S2 next-day return (gap 1) shows no summary")
        check("TOWN SQUARE" in t, "S2 next-day return hub renders")
        check(errs == [], "S2 no page errors (next-day)", errs)
        ctx.close()

        # ================================================== S3
        group("S3 one-time per gap within the session")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2)))
        check("WELCOME BACK" in txt(page), "S3 seeded summary shown")
        page.locator('.menu-row[data-action="1"]').first.click()
        page.wait_for_timeout(120)
        check("TOWN SQUARE" in txt(page), "S3 Back to Town renders the hub")
        page.locator('.menu-row[data-action="8"]').first.click()
        page.wait_for_timeout(120)
        check("WELCOME BACK" not in txt(page), "S3 navigating into today's quest does not re-show")
        page.locator('.menu-row[data-action="1"]').first.click()
        page.wait_for_timeout(120)
        check("TOWN SQUARE" in txt(page), "S3 back at the hub")
        for action, back in (("4", "3"), ("5", "1"), ("7", "2"), ("9", "1")):
            page.locator('.menu-row[data-action="%s"]' % action).first.click()
            page.wait_for_timeout(80)
            page.locator('.menu-row[data-action="%s"]' % back).first.click()
            page.wait_for_timeout(80)
            check("TOWN SQUARE" in txt(page), "S3 round-trip via view %s returns to the hub" % action)
            check("WELCOME BACK" not in txt(page), "S3 no re-show after view %s" % action)
        t = txt(page)
        check("WELCOME BACK" not in t, "S3 no summary after 4 further view round-trips")
        check("TOWN SQUARE" in t, "S3 hub still home")
        check(errs == [], "S3 no page errors", errs)
        page.reload(wait_until="load")
        page.wait_for_timeout(150)
        t = txt(page)
        check("WELCOME BACK" not in t, "S3 same-day reload after the reset does not re-nag",
              t.splitlines()[0] if t else "")
        check("TOWN SQUARE" in t, "S3 hub after reload")
        ctx.close()

        # ================================================== S4
        group("S4 summary path writes nothing")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2)))
        check("WELCOME BACK" in txt(page), "S4 summary shown for the no-write run")
        load_writes = writes(page)
        check(all(SAVE_KEY not in w["k"] for w in load_writes),
              "S4 load wrote nothing to the character save",
              [w["k"] for w in load_writes])
        check(len(load_writes) <= 1 and (not load_writes or load_writes[0]["k"] == DAY_KEY),
              "S4 load writes are only the pre-existing daily reset",
              [(w["k"], len(w["v"])) for w in load_writes])
        check(all(("renderWelcomeBack" not in w["stack"]) and ("computeAwayWindow" not in w["stack"])
                  for w in load_writes),
              "S4 no write originates in the summary path",
              [w["stack"].splitlines()[0:3] for w in load_writes])
        before = stored(page)
        page.evaluate("() => { window.__writes.length = 0; }")
        page.locator('.menu-row[data-action="2"]').first.click()
        page.wait_for_timeout(120)
        check("WELCOME BACK" not in txt(page), "S4 row 2 left the summary")
        page.locator('.menu-row[data-action="1"]').first.click()
        page.wait_for_timeout(120)
        inter = writes(page)
        check(inter == [], "S4 zero localStorage writes on the summary interaction path",
              [w["k"] for w in inter])
        after = stored(page)
        check(after["save"] == before["save"], "S4 save key byte-identical before/after summary",
              "len %s vs %s" % (len(before["save"] or ""), len(after["save"] or "")))
        check(after["day"] == before["day"], "S4 day key byte-identical before/after summary")
        check(len(before["save"] or "") > 0 and json.loads(before["save"]) == LEGACY_CHAR,
              "S4 stored character still the seeded one")
        check(errs == [], "S4 no page errors", errs)
        ctx.close()

        # ================================================== S5
        group("S5 legacy save: no field loss, no new key")
        legacy_day = J({"dayIndex": TODAY - 3, "fightsUsed": 2, "innHealsUsed": 0})
        ctx, page, errs = open_page(browser, LEGACY_CHAR, legacy_day)
        t = txt(page)
        check("WELCOME BACK" in t, "S5 summary shown for a legacy multi-day gap")
        check("You were away for 2 days." in t, "S5 days away correct from a pre-040 record",
              [l for l in t.splitlines() if "away" in l])
        s = stored(page)
        after_char = json.loads(s["save"])
        check(sorted(after_char.keys()) == LEGACY_CHAR_KEYS, "S5 legacy save gains no new field",
              sorted(after_char.keys()))
        check(after_char == LEGACY_CHAR, "S5 legacy save values unchanged")
        for k in ("level", "gold", "xp", "bank", "wins"):
            check(after_char[k] == LEGACY_CHAR[k], "S5 %s unchanged" % k, after_char[k])
        check("quest" in json.loads(s["day"]) and "completedQuests" in json.loads(s["day"]),
              "S5 day record backfilled by ensureQuestState only",
              sorted(json.loads(s["day"]).keys()))
        check(errs == [], "S5 no page errors", errs)
        ctx.close()

        # control: same seed on the pre-040 build, storage bytes must match
        if os.path.exists(os.path.join(ART_DIR, "cinder-main.html")):
            ctx_m, page_m, errs_m = open_page(browser, LEGACY_CHAR, legacy_day,
                                              artifact="cinder-main.html")
            t_m = txt(page_m)
            check("WELCOME BACK" not in t_m and "TOWN SQUARE" in t_m,
                  "S5c control: pre-040 build shows the hub for the same seed")
            s_m = stored(page_m)
            ctx, page, errs = open_page(browser, LEGACY_CHAR, legacy_day)
            s_new = stored(page)
            check(s_m["save"] == s_new["save"], "S5c character save byte-identical to pre-040 build")
            check(s_m["day"] == s_new["day"], "S5c day record byte-identical to pre-040 build",
                  "main=%s" % (s_m["day"],))
            check(errs == [] and errs_m == [], "S5c no page errors on either build")
            ctx.close()
            ctx_m.close()
        else:
            check(False, "S5c control artifact cinder-main.html missing")

        # ================================================== S6
        group("S6 no economy or balance change on return")
        seed_day = J(day(dayIndex=TODAY - 5, fightsUsed=11, innHealsUsed=3,
                         quest={"progress": 4, "completed": False, "rewarded": False},
                         completedQuests=[{"dayIndex": TODAY - 12, "objective": "old", "label": "old"}]))
        ctx, page, errs = open_page(browser, LEGACY_CHAR, seed_day)
        check("WELCOME BACK" in txt(page), "S6 summary shown")
        at_summary = stored(page)
        char_at = json.loads(at_summary["save"])
        day_at = json.loads(at_summary["day"])
        page.locator('.menu-row[data-action="1"]').first.click()
        page.wait_for_timeout(120)
        after_summary = stored(page)
        char_after = json.loads(after_summary["save"])
        day_after = json.loads(after_summary["day"])
        for k in ("gold", "xp", "level", "bank", "wins", "hp", "deaths"):
            check(char_after.get(k) == char_at.get(k),
                  "S6 character %s identical at and after the summary" % k,
                  "%s vs %s" % (char_at.get(k), char_after.get(k)))
        check(char_after == LEGACY_CHAR, "S6 whole character save unchanged from the seed")
        for k in ("dayIndex", "fightsUsed", "innHealsUsed", "quest", "completedQuests"):
            check(day_after.get(k) == day_at.get(k),
                  "S6 day record %s identical at and after the summary" % k,
                  "%s vs %s" % (day_at.get(k), day_after.get(k)))
        check(day_at["quest"] == {"progress": 0, "completed": False, "rewarded": False},
              "S6 fresh day quest state is the pre-existing reset, not a 040 change",
              day_at["quest"])
        check(day_at["completedQuests"] == [],
              "S6 completedQuests after reset is empty (pre-existing reset behavior)")
        lt = txt(page)
        check("TOWN SQUARE" in lt, "S6 hub renders after dismissal")
        check(errs == [], "S6 no page errors", errs)
        ctx.close()

        # ================================================== S7
        group("S7 quests missed accurate for a known window")
        for gap, expected in ((2, 1), (3, 2), (6, 5), (13, 12)):
            ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - gap)))
            t = txt(page)
            want = ("1 quest went uncompleted" if expected == 1
                    else "%d quests went uncompleted" % expected)
            check(want in t, "S7 gap %d -> %d quests missed" % (gap, expected),
                  [l for l in t.splitlines() if "uncompleted" in l])
            ctx.close()
        anchor_day = J(day(dayIndex=TODAY - 4,
                          completedQuests=[{"dayIndex": TODAY - 10, "objective": "a", "label": "a"},
                                           {"dayIndex": TODAY - 4, "objective": "b", "label": "b"}]))
        ctx, page, errs = open_page(browser, LEGACY_CHAR, anchor_day)
        t = txt(page)
        check("You were away for 3 days." in t, "S7 history anchor: 3 days away",
              [l for l in t.splitlines() if "away" in l])
        check("3 quests went uncompleted while you were gone." in t,
              "S7 known window (3 days, no completion inside) reports exactly 3")
        check("4 quests went uncompleted" not in t, "S7 no invented count")
        ctx.close()

        # ================================================== S8
        group("S8 both streak branches render explicitly")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2)))
        t = txt(page)
        check("Your streak is broken." in t, "S8 broken branch renders explicitly")
        check("Your streak survived." not in t, "S8 broken branch is not the survived line")
        ctx.close()

        survived_day = J(day(dayIndex=TODAY - 3,
                             quest={"progress": 0, "completed": True, "rewarded": True}))
        ctx, page, errs = open_page(browser, LEGACY_CHAR, survived_day)
        t = txt(page)
        check("WELCOME BACK" in t, "S8 survived seed still shows the summary")
        check("Your streak survived." in t, "S8 survived branch renders explicitly",
              [l for l in t.splitlines() if "streak" in l])
        check("Your streak is broken." not in t, "S8 survived branch is not the broken line")
        check("You were away for 2 days." in t, "S8 window still correct in the survived seed")
        ctx.close()

        # ================================================== S9
        group("S9 private mode / storage unavailable")
        ctx, page, errs = open_page(browser, throw_all=True)
        t = txt(page)
        check("CHARACTER CREATION" in t, "S9a no storage: boots to character creation", t.splitlines()[0])
        page.fill("#promptInput", "NoStore")
        page.keyboard.press("Enter")
        page.wait_for_timeout(150)
        t = txt(page)
        check("TOWN SQUARE" in t, "S9a in-memory play reaches the hub")
        check("NoStore" in page.inner_text("#statusLine"), "S9a in-memory character is live",
              page.inner_text("#statusLine")[:60])
        check(errs == [], "S9a nothing threw", errs)
        ctx.close()

        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2)), throw_set=True)
        t = txt(page)
        check("WELCOME BACK" in t, "S9b unreadable storage, readable state: summary renders",
              t.splitlines()[0] if t else "")
        check("You were away for a day." in t and "Your streak is broken." in t,
              "S9b summary facts intact")
        page.locator('.menu-row[data-action="1"]').first.click()
        page.wait_for_timeout(120)
        check("TOWN SQUARE" in txt(page), "S9b play continues from memory")
        check(errs == [], "S9b nothing threw", errs)
        ctx.close()

        # ================================================== S10 + NEG
        group("S10 corrupt day record and negative inputs")
        corrupts = [
            ("quest missing", {"dayIndex": TODAY - 2, "fightsUsed": 0, "innHealsUsed": 0}),
            ("quest is a string", {"dayIndex": TODAY - 2, "quest": "nope", "completedQuests": []}),
            ("quest null", {"dayIndex": TODAY - 2, "quest": None, "completedQuests": []}),
            ("completedQuests not an array",
             {"dayIndex": TODAY - 2, "quest": {"progress": 0, "completed": False, "rewarded": False},
              "completedQuests": "nope"}),
            ("completedQuests is a number",
             {"dayIndex": TODAY - 2, "completedQuests": 42}),
            ("non-numeric dayIndex", {"dayIndex": "today", "completedQuests": []}),
            ("NaN dayIndex", {"dayIndex": None, "completedQuests": []}),
            ("junk history entries",
             {"dayIndex": TODAY - 3, "completedQuests": [None, 7, "x", {"dayIndex": "y"},
                                                         {"dayIndex": TODAY - 3}]}),
            ("future dayIndex", {"dayIndex": TODAY + 5, "completedQuests": []}),
            ("day record is garbage", ["not", "an", "object"]),
            ("day record is a string", "garbage"),
            ("day record is a number", 12345),
            ("empty object", {}),
        ]
        for name, rec in corrupts:
            raw = rec if isinstance(rec, str) and rec == "garbage" else json.dumps(rec)
            ctx, page, errs = open_page(browser, LEGACY_CHAR, raw)
            t = txt(page)
            view_ok = ("TOWN SQUARE" in t) or ("WELCOME BACK" in t)
            check(errs == [], "S10/neg %s: no exception" % name, errs)
            check(view_ok, "S10/neg %s: a view renders" % name, (t.splitlines() or [""])[0])
            if name in ("future dayIndex", "non-numeric dayIndex", "NaN dayIndex",
                        "day record is a string", "day record is a number", "empty object"):
                check("WELCOME BACK" not in t, "S10/neg %s: no summary" % name)
            if name == "dayIndex only" or name == "quest missing":
                pass
            ctx.close()
        # garbage but still a usable shape: boolean-ish dayIndex
        ctx, page, errs = open_page(browser, LEGACY_CHAR, "not json")
        t = txt(page)
        check(errs == [], "neg unparseable day record: no exception", errs)
        check("TOWN SQUARE" in t or "WELCOME BACK" in t,
              "neg unparseable day record: a view renders", (t.splitlines() or [""])[0])
        ctx.close()

        # corrupt with a valid anchor: summary still correct
        ctx, page, errs = open_page(browser, LEGACY_CHAR,
                                    J({"dayIndex": TODAY - 2, "completedQuests": "nope"}))
        t = txt(page)
        check("WELCOME BACK" in t and "You were away for a day." in t,
              "S10 corrupt completedQuests still yields a correct summary",
              [l for l in t.splitlines() if "away" in l][:1])
        check(errs == [], "S10 corrupt completedQuests: no exception", errs)
        ctx.close()

        # ================================================== S11
        group("S11 returning after 30+ days")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 31)))
        t = txt(page)
        lines = [l.strip() for l in t.splitlines() if l.strip()]
        check("You were away for a while." in t, "S11 long gap uses the phrased sentence",
              [l for l in lines if "away" in l])
        check("30 quests went uncompleted while you were gone." in t,
              "S11 quests-missed line carries the count in a sentence")
        check(not any(re.fullmatch(r"\d+", l) for l in lines),
              "S11 no bare counter alone on a line", lines)
        check("Today's quest: " in t, "S11 today's quest named")
        check("Your streak is broken." in t, "S11 streak line explicit")
        ov = overflow(page)
        check(ov["docScroll"] <= ov["win"], "S11 no horizontal overflow (desktop)", ov)
        check(ov["boxScroll"] <= ov["boxClient"] + 1, "S11 panel does not overflow", ov)
        check(errs == [], "S11 no page errors", errs)
        ctx.close()

        # ================================================== S12
        group("S12 no notifications, push, permission prompt, install nag")
        src = open(os.path.join(ART_DIR, "cinder.html"), encoding="utf-8").read()
        for token in ("Notification", "pushManager", "requestPermission",
                      "serviceWorker", "beforeinstallprompt", "onclick="):
            check(src.count(token) == 0, "S12 static scan: no %r in the artifact" % token,
                  src.count(token))
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2)))
        dialogs = []
        page.on("dialog", lambda d: (dialogs.append(d.type), d.dismiss()))
        page.wait_for_timeout(200)
        dom = page.evaluate("() => document.body.innerText.toLowerCase()")
        check("install" not in dom, "S12 no install text in the rendered DOM")
        check("permission" not in dom, "S12 no permission text in the rendered DOM")
        check(dialogs == [], "S12 no permission prompt dialog", dialogs)
        check(errs == [], "S12 no page errors", errs)
        ctx.close()

        # ================================================== S13
        group("S13 mobile 375x667 with a real tap")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 2)),
                                    viewport={"width": 375, "height": 667}, touch=True)
        t = txt(page)
        check("WELCOME BACK" in t, "S13 summary at 375x667")
        ov = overflow(page)
        check(ov["docScroll"] <= ov["win"], "S13 no horizontal overflow at 375px", ov)
        check(ov["displayScroll"] <= ov["displayClient"] + 1, "S13 display does not scroll sideways", ov)
        check(ov["boxScroll"] <= ov["boxClient"] + 1, "S13 summary panel fits the viewport", ov)
        check(page.evaluate("() => document.querySelectorAll('[onclick]').length") == 0,
              "S13 no rendered inline onclick attribute")
        markup = page.evaluate("() => document.querySelector('.boxed-menu').outerHTML")
        check("onclick" not in markup, "S13 new markup carries no inline onclick")
        box = page.locator('.menu-row[data-action="1"]').first.bounding_box()
        check(box["y"] >= 0 and box["y"] + box["height"] <= 667 and box["height"] >= 24,
              "S13 Back to Town row is on screen and tappable", box)
        tap_row(page, "1")
        t = txt(page)
        check("TOWN SQUARE" in t, "S13 real tap on Back to Town renders the hub")
        check("WELCOME BACK" not in t, "S13 tap dismissed the summary")
        check(errs == [], "S13 no page errors", errs)
        ctx.close()

        # ================================================== S14
        group("S14 tone: no em dashes, no heavy emoji in new copy")
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 31)))
        t = txt(page)
        has_dash, emojis = scan_copy(t)
        check(not has_dash, "S14 rendered summary has no em dash")
        check(not emojis, "S14 rendered summary has no heavy emoji", emojis)
        ctx.close()
        ctx, page, errs = open_page(browser, LEGACY_CHAR, J(day(dayIndex=TODAY - 3,
                                    quest={"progress": 0, "completed": True, "rewarded": True})))
        has_dash, emojis = scan_copy(txt(page))
        check(not has_dash, "S14 survived-branch copy has no em dash")
        check(not emojis, "S14 survived-branch copy has no heavy emoji", emojis)
        ctx.close()

        browser.close()
    httpd.shutdown()

    print("\n%d checks, %d failed" % (COUNT["pass"] + COUNT["fail"], COUNT["fail"]), flush=True)
    return 1 if COUNT["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
