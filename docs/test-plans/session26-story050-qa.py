#!/usr/bin/env python3
"""Session 26 Story 050 test plan and executable checks (Scout, QA).

Story: 050-cinder-questlog-day-labels.md
Deliverable under test: src/cinder.html (candidate = main + PR #105 + PR #106).

Core defect: dayLabelForIndex() measured its difference from getDayIndex()
(today) while the streak number (computeQuestLogStreak) and the recent-quests
list (computeRecentQuestEntries) measured from the record's own anchor. A
30-day-stale record printed "Current streak: 1 day" beside "30 days ago: <last
quest played>" in one boxed menu.

This file is the Story 050 test plan. It enumerates the BDD scenarios as
numbered cases with method, input, expected and pass/fail, and it can be run as
an executable check of the three pure functions (dayLabelForIndex,
computeQuestLogStreak, computeRecentQuestEntries) plus the frozen-function
extraction. Real-browser verification lives in
flambeee-team/scout-qa-session26-browser.py.

Usage:
    /home/jake/.openclaw/workspace/.venv/bin/python3 session26-story050-qa.py
Optional env:
    CINDER_PATH  path to the candidate src/cinder.html
                 (default: /tmp/flambeee-wt-scout-merge/src/cinder.html)
    BASE_REF     git ref of shipped v0.23.0 in the repo that contains the file
                 (default: v0.23.0)
"""
import os
import re
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Test plan (BDD scenarios, Story 050)
# ---------------------------------------------------------------------------
TEST_PLAN = [
    (1, "30-day-stale record: newest entry label is relative to the record anchor",
     "Render the quest log from a record whose anchor is TODAY-30 with one completion on the anchor day.",
     "Newest entry label is 'today', NOT '30 days ago'. Streak reads 1.", "P1 core"),
    (2, "Label uses the same anchor as the number and the list",
     "Call dayLabelForIndex with the anchor derived as computeQuestLogStreak/computeRecentQuestEntries derive it.",
     "Difference = anchor - entry.dayIndex; number, list and labels describe one window.", "P1"),
    (3, "Same-day reload renders exactly as v0.23.0",
     "Record stamped today; render with candidate and with v0.23.0.",
     "Identical labels, streak, list.", "P1 control"),
    (4, "Next-day return renders exactly as v0.23.0",
     "Record stamped T-1, nothing fully missed; render candidate vs v0.23.0.",
     "Identical render; Story 033 preview and Story 037 badge not regressed.", "P1 control"),
    (5, "Stale-by-1 record labels its entry 'today'",
     "Record whose newest recorded day equals the anchor (diff 0).",
     "Newest entry reads 'today', not '1 day ago'.", "P1 proof"),
    (6, "Label difference is anchor - entry, never today - entry",
     "Call dayLabelForIndex with anchor/entry pairs (diff 0,1,3,30) in a sandbox.",
     "today / yesterday / 3 days ago / 30 days ago; pre-fix build fails these.", "P1 proof"),
    (7, "Proof fails against shipped v0.23.0",
     "Run the label assertions against v0.23.0's dayLabelForIndex.",
     "Fails on the stale-anchor labels; passes on the candidate (exit 0).", "P1 proof"),
    (8, "Frozen functions byte-identical to v0.23.0",
     "Extract checkDailyReset, computeQuestLogStreak, computeRecentQuestEntries.",
     "Textually unchanged from v0.23.0.", "P1 proof"),
    (9, "Read path writes nothing and adds no field",
     "Static scan of label + render path; runtime byte-identity of both keys.",
     "No saveCharacter/saveDayState/setItem; keys byte-identical; no new field.", "P1 proof"),
    (10, "List contract unchanged for the same history",
     "Render the pre-fix and post-fix list for the same history.",
     "Identical order, cap 5, titles, empty state; differ only in the label reference point.", "P1"),
    (11, "Legacy, corrupt and partial records degrade cleanly",
     "No completedQuests; completedQuests a string; non-numeric dayIndex; dayState null.",
     "Renders without error; falls back to existing label form; nothing throws.", "P1 regression"),
    (12, "Storage unavailable / private mode",
     "localStorage throwing and swallowed.",
     "Game runs from in-memory state; log behaves the same; nothing throws.", "P1"),
    (13, "Story 042/044 panel and welcome-back window not regressed",
     "Intact recorded run and a genuine hole on a multi-day gap.",
     "Panel sentences and log streak unchanged from v0.23.0.", "P1 regression"),
    (14, "Out-of-scope references and forbidden fallbacks absent (D1/D2)",
     "Scan the merged diff.",
     "No var referenced outside its owning scope; no post-reset fallback; fallback form, not throw.", "P1"),
    (15, "Mobile-safe, Back to Town tappable, no inline onclick",
     "Render at 375x667 and desktop with wrapping labels; tap Back to Town.",
     "Delegated data-action fires; hub renders; no horizontal overflow; no onclick.", "P1 browser"),
    (16, "No notifications, push, permission prompt or install nag",
     "Static scan and browser exercise.",
     "No Notification request, no pushManager, no subscription, no prompt.", "P1"),
    (17, "Tone: no em dashes, no heavy emoji",
     "Scan added/changed user-visible strings.",
     "Plain punctuation, dry Cinder voice.", "P2"),
    (18, "Worktree and ownership rule followed",
     "Review PR bodies and merged candidate.",
     "One owner per helper and call-site line; Scout scanned the merged candidate.", "P1"),
]

SAVE_KEY = "flambeee-cinder-save"
DAY_KEY = "flambeee-cinder-day"
TODAY = int(time.time() * 1000 // 86400000)

COUNT = {"pass": 0, "fail": 0}
RESULTS = []


def check(cond, name, detail=""):
    ok = bool(cond)
    RESULTS.append((name, ok, detail))
    COUNT["pass" if ok else "fail"] += 1
    line = ("PASS" if ok else "FAIL") + ": " + name
    if detail:
        line += "  | " + str(detail)
    print(line, flush=True)
    return ok


def group(name):
    print("\n--- %s ---" % name, flush=True)


# ---------------------------------------------------------------------------
# Source extraction
# ---------------------------------------------------------------------------
def extract_function(src, name):
    """Extract `function <name>(...) { ... }` by brace matching. None if absent."""
    m = re.search(r"\bfunction\s+" + re.escape(name) + r"\s*\(", src)
    if not m:
        return None
    start = m.start()
    j = src.find("{", m.end())
    if j < 0:
        return None
    depth = 0
    k = j
    while k < len(src):
        c = src[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[start:k + 1]
        k += 1
    return None


def main():
    cinder_path = os.environ.get(
        "CINDER_PATH", "/tmp/flambeee-wt-scout-merge/src/cinder.html")
    base_ref = os.environ.get("BASE_REF", "v0.23.0")
    repo = os.environ.get("REPO", "/home/jake/.openclaw/workspace/flambeee")

    if not os.path.isfile(cinder_path):
        print("candidate not found: %s" % cinder_path)
        return 2

    src = open(cinder_path, encoding="utf-8").read()
    cand_sha = subprocess.run(["sha256sum", cinder_path], capture_output=True,
                              text=True).stdout.split()[0]

    print("=== Session 26 Story 050 QA: quest-log day labels ===")
    print("test plan cases: %d" % len(TEST_PLAN))
    print("candidate      : %s" % cinder_path)
    print("candidate sha  : %s" % cand_sha)
    print("base ref       : %s" % base_ref)

    # --- Static extraction of the functions under test and the frozen set ---
    group("Extraction")
    label = extract_function(src, "dayLabelForIndex")
    streak = extract_function(src, "computeQuestLogStreak")
    recent = extract_function(src, "computeRecentQuestEntries")
    check(label is not None, "dayLabelForIndex() extracted from candidate")
    check(streak is not None, "computeQuestLogStreak() extracted from candidate")
    check(recent is not None, "computeRecentQuestEntries() extracted from candidate")

    # --- Static scan: no writes / no new field / no inline onclick (cases 9,16) ---
    group("Static scan: pure read, no new field, no inline onclick")
    for fn_name, body in (("dayLabelForIndex", label or ""),
                          ("computeQuestLogStreak", streak or ""),
                          ("computeRecentQuestEntries", recent or "")):
        hits = [w for w in ("saveCharacter(", "saveDayState(", "localStorage.setItem",
                            "completeQuest(", "applyQuestProgress(") if w in body]
        check(not hits, "%s carries no writer helper" % fn_name, "hits=%s" % hits)
    check(src.count("onclick=") == 0, "no inline onclick in candidate",
          "count=%d" % src.count("onclick="))
    check("Notification" not in src, "no Notification API use")
    check("pushManager" not in src, "no pushManager use")
    for field in ("questLogStreak", "cachedStreak", "streakCache", "lastStreak",
                  "streakAnchor", "seenStreak", "labelAnchor"):
        check(field not in src, "no new persisted field: %s" % field)

    # --- Frozen-function byte-identity vs v0.23.0 (case 8) ---
    group("Frozen functions byte-identical to %s" % base_ref)
    base_proc = subprocess.run(["git", "-C", repo, "show",
                                "%s:src/cinder.html" % base_ref],
                               capture_output=True, text=True)
    if base_proc.returncode != 0:
        check(False, "could extract %s:src/cinder.html" % base_ref,
              base_proc.stderr.strip()[:120])
    else:
        base_src = base_proc.stdout
        for fn in ("checkDailyReset", "computeQuestLogStreak",
                   "computeRecentQuestEntries", "shouldShowWelcomeBack",
                   "computeAwayWindow"):
            a = extract_function(base_src, fn)
            b = extract_function(src, fn)
            same = a is not None and a == b
            check(same, "%s() byte-identical to %s" % (fn, base_ref),
                  "candidate_chars=%d" % (len(b) if b else -1))

    # --- The label semantics, exercised in a node sandbox (cases 2,5,6,7,11) ---
    group("Label semantics in a node sandbox (anchor-relative)")
    node = which_node()
    if not node:
        check(False, "node available for the label sandbox")
    else:
        # dayLabelForIndex only needs getDayIndex + a numeric anchor. Run both
        # the candidate helper and the v0.23.0 helper over the same inputs.
        cand_label = label or ""
        base_label = extract_function(base_proc.stdout, "dayLabelForIndex") \
            if base_proc.returncode == 0 else None

        def run_label(fn_body, cases):
            script = """
const TODAY = %d;
function getDayIndex() { return TODAY; }
%s
const cases = %s;
for (const c of cases) {
  let out;
  try { out = String(dayLabelForIndex(c.dayIdx, c.anchor)); }
  catch (e) { out = 'THROW:' + e.name; }
  console.log(JSON.stringify(out));
}
""" % (TODAY, fn_body, js_array(cases))
            p = subprocess.run([node, "-e", script], capture_output=True, text=True)
            if p.returncode != 0:
                return ["ERR:" + p.stderr.strip()[:100]] * len(cases)
            return [l for l in p.stdout.splitlines() if l.strip()]

        anchor_record = {"dayIndex": TODAY - 30,
                         "completedQuests": [{"dayIndex": TODAY - 30}]}
        cases = [
            {"dayIdx": TODAY - 30, "anchor": anchor_record, "want": "today"},
            {"dayIdx": TODAY - 31, "anchor": anchor_record, "want": "yesterday"},
            {"dayIdx": TODAY - 33, "anchor": anchor_record, "want": "3 days ago"},
            {"dayIdx": TODAY, "anchor": anchor_record, "want": "day %d" % TODAY},
            {"dayIdx": TODAY, "anchor": None, "want": "today"},
            {"dayIdx": TODAY - 2, "anchor": {}, "want": "2 days ago"},
        ]
        got = run_label(cand_label, cases)
        for c, g in zip(cases, got):
            want = '"%s"' % c["want"]
            check(g == want,
                  "label anchor=%s entry=%s -> %s" % (
                      ("T-30" if c["anchor"] is anchor_record else
                       ("None" if c["anchor"] is None else "{}")),
                      "T" if c["dayIdx"] == TODAY else "T%+d" % (c["dayIdx"] - TODAY),
                      c["want"]),
                  "got %s" % g)

        # Case 7: the pre-fix build fails the anchor-relative assertions.
        if base_label:
            base_cases = [cases[0], cases[1], cases[2]]
            base_got = run_label(base_label, base_cases)
            fails = sum(1 for c, g in zip(base_cases, base_got) if g != '"%s"' % c["want"])
            check(fails == len(base_cases),
                  "pre-fix v0.23.0 label FAILS all anchor-relative cases (isolates the fix)",
                  "v0.23.0 got %s" % base_got)
        else:
            check(False, "v0.23.0 dayLabelForIndex extracted for the fail-against-shipped proof")

    # --- List contract (case 10): cap 5, most recent first, same titles ---
    # The cap/order live in renderQuestLog(), not in the list-source helper.
    group("List contract (order, cap 5, titles)")
    render_fn = extract_function(src, "renderQuestLog")
    if render_fn:
        check("slice(-5)" in render_fn and ".reverse()" in render_fn,
              "renderQuestLog keeps slice(-5).reverse() (cap 5, most recent first)")
        check(("entry.objective || entry.label || ''") in render_fn,
              "renderQuestLog keeps the entry-title expression")
        check("No quests recorded yet" in render_fn,
              "renderQuestLog keeps the empty-state line")
    else:
        check(False, "renderQuestLog() extracted for the list-contract checks")
    check(src.count("slice(-5).reverse()") == 1,
          "exactly one slice(-5).reverse() in the file",
          "count=%d" % src.count("slice(-5).reverse()"))
    call_re = re.search(r"dayLabelForIndex\(entry\.dayIndex,\s*questLogAnchor\)", src)
    check(call_re is not None,
          "call site passes questLogAnchor: dayLabelForIndex(entry.dayIndex, questLogAnchor)")
    check(src.count("dayLabelForIndex(") == 2,
          "dayLabelForIndex has exactly one call site plus its definition",
          "count=%d" % src.count("dayLabelForIndex("))

    # --- Tone (case 17): no em dash / heavy emoji in the added lines ---
    group("Tone on the merged candidate")
    check("\u2014" not in src, "no em dash anywhere in candidate")
    heavy = re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]", src)
    check(heavy is None, "no heavy emoji in candidate",
          "" if heavy is None else repr(heavy.group(0)))

    print("\n%d checks, %d failed" % (COUNT["pass"] + COUNT["fail"], COUNT["fail"]))
    print("TEST PLAN CASES: %d" % len(TEST_PLAN))
    for num, name, _method, _expect, sev in TEST_PLAN:
        print("  case %-2d [%s] %s" % (num, sev, name))
    verdict = "ALL CHECKS PASS" if COUNT["fail"] == 0 else "CHECKS FAILED"
    print(verdict)
    return 0 if COUNT["fail"] == 0 else 1


def js_array(cases):
    def one(c):
        anchor = c["anchor"]
        if anchor is None:
            a = "null"
        elif anchor == {}:
            a = "{}"
        else:
            a = ("{dayIndex:%d, completedQuests:[{dayIndex:%d}]}" % (
                anchor["dayIndex"], anchor["completedQuests"][0]["dayIndex"]))
        return "{dayIdx:%d, anchor:%s}" % (c["dayIdx"], a)
    return "[" + ",".join(one(c) for c in cases) + "]"


def which_node():
    for cand in ("node", "/usr/bin/node", "/usr/local/bin/node"):
        p = subprocess.run(["bash", "-lc", "command -v %s" % cand],
                           capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    return None


if __name__ == "__main__":
    sys.exit(main())
