#!/usr/bin/env python3
"""Session 26 Story 051 test plan and executable checks (Scout, QA).

Story: 051-cinder-welcomeback-day-count.md
Deliverable under test: src/cinder.html (candidate = main + PR #105 + PR #106).
Story 051 is a verification story: NO code change. Its deliverable is the proof
src/kai-story051-away-window-proof.py and the recorded decision.

Resolved definition (do not re-litigate):
    gapDays  = todayIdx - lastPlayIdx
    daysAway = gapDays - 1   (clamped at 0)   <- count of fully missed UTC days

This file is the Story 051 test plan. It enumerates the BDD scenarios as
numbered cases with method, input, expected and pass/fail, and it can be run as
an executable check that (a) the shipped candidate still matches the resolved
definition at every sweep point, (b) the frozen functions are byte-identical to
v0.23.0, and (c) the proof is non-vacuous (fails against a daysAway=gapDays
mutant).

Usage:
    /home/jake/.openclaw/workspace/.venv/bin/python3 session26-story051-qa.py
Optional env:
    CINDER_PATH  path to the candidate src/cinder.html
                 (default: /tmp/flambeee-wt-scout-merge/src/cinder.html)
    BASE_REF     git ref of shipped v0.23.0 (default: v0.23.0)
    REPO         repo that contains the v0.23.0 tag
                 (default: /home/jake/.openclaw/workspace/flambeee)
"""
import os
import re
import subprocess
import sys
import time

TEST_PLAN = [
    (1, "Definition recorded and unambiguous",
     "Read the story's Resolved definition section.",
     "daysAway = gapDays - 1, fully missed UTC days, authority named, distinguished from gapDays and the label.",
     "P2 record"),
    (2, "Two-day gap shows the one-missed-day panel consistently",
     "Record whose last play day is 2 UTC days before today (one fully missed day).",
     '"You were away for a day.", "1 quest went uncompleted...", daysAway 1, questsMissed 1, questsMissed <= daysAway.',
     "P2"),
    (3, "Same-day and next-day returns stay quiet",
     "gapDays 0 and gapDays 1.",
     "Panel stays quiet exactly as v0.23.0; daysAway 0 in both.",
     "P2 control"),
    (4, "Boundary sweep correct for every documented gap",
     "Sweep gapDays 0,1,2,3,7,14,30.",
     "daysAway, questsMissed, shouldShow and the exact sentence each asserted; questsMissed <= daysAway holds.",
     "P2 proof"),
    (5, "Long-absence phrasing unchanged",
     "daysAway >= 14 (boundary pinned at gapDays 15).",
     'Existing form "You were away for a while.", plain punctuation, no emoji.',
     "P2"),
    (6, "No code change was made",
     "Inspect the diff for this story in src/cinder.html.",
     "computeAwayWindow, shouldShowWelcomeBack and checkDailyReset byte-identical to v0.23.0; no other line changed.",
     "P2 core"),
    (7, "Frozen functions byte-identical to v0.23.0",
     "Extract shouldShowWelcomeBack and checkDailyReset (plus computeAwayWindow).",
     "Textually identical.",
     "P2 proof"),
    (8, "Summary path writes nothing and adds no field",
     "Render the panel; compare both keys; scan the diff.",
     "Both keys byte-identical; no new field name.",
     "P2 proof"),
    (9, "Corrupt and partial records degrade cleanly",
     "Legacy record, corrupt record, null record, storage unavailable.",
     "Panel shows nothing rather than throwing; town hub renders normally.",
     "P2 regression"),
    (10, "Cross-surface question routed, not silently resolved",
     "Panel days-away value vs quest-log label for the same span.",
     "Recorded as a CEO decision; no code change forces agreement.",
     "P2"),
    (11, "Stories 050 and 051 do not collide",
     "Review both PRs.",
     "050 changed only the label reference point; 051 changed no code; computeAwayWindow untouched by both.",
     "P2"),
    (12, "Tone and no-AI-tells",
     "Review new/changed copy and the decision text.",
     "No em dashes, no heavy emoji, plain-punctuation voice.",
     "P2"),
]

TODAY = int(time.time() * 1000 // 86400000)
COUNT = {"pass": 0, "fail": 0}


def check(cond, name, detail=""):
    ok = bool(cond)
    COUNT["pass" if ok else "fail"] += 1
    line = ("PASS" if ok else "FAIL") + ": " + name
    if detail:
        line += "  | " + str(detail)
    print(line, flush=True)
    return ok


def group(name):
    print("\n--- %s ---" % name, flush=True)


def extract_function(src, name):
    m = re.search(r"\bfunction\s+" + re.escape(name) + r"\s*\(", src)
    if not m:
        return None
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
                return src[m.start():k + 1]
        k += 1
    return None


def which_node():
    for cand in ("node", "/usr/bin/node", "/usr/local/bin/node"):
        p = subprocess.run(["bash", "-lc", "command -v %s" % cand],
                           capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    return None


def sweep(node, fn_bodies, days_away_expr=None):
    """Drive the shipped away-window path over gapDays 0,1,2,3,7,14,30."""
    days_sentence, quests_sentence, streak_sentence, window = fn_bodies
    if days_away_expr:
        window = window.replace("const daysAway = gapDays - 1;", days_away_expr)
    script = """
const TODAY = %d;
%s
%s
%s
%s
const out = [];
for (const g of [0,1,2,3,7,14,15,16,30]) {
  const last = TODAY - g;
  const rec = { dayIndex: last, fightsUsed: 0, innHealsUsed: 0, quest: 'x',
                completedQuests: [{ dayIndex: last }] };
  let w;
  try { w = computeAwayWindow(rec, TODAY); } catch (e) { w = { ERROR: e.name }; }
  let sent = '';
  try { sent = awayDaysSentence(w.daysAway); } catch (e) { sent = 'THROW:' + e.name; }
  out.push({ g: g, daysAway: w.daysAway, questsMissed: w.questsMissed,
             shouldShow: w.shouldShow, sentence: sent });
}
console.log(JSON.stringify(out));
""" % (TODAY, window, days_sentence, quests_sentence, streak_sentence)
    p = subprocess.run([node, "-e", script], capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr.strip()[:400])
        return None
    import json
    return json.loads(p.stdout.strip().splitlines()[-1])


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

    print("=== Session 26 Story 051 QA: welcome-back day count ===")
    print("test plan cases: %d" % len(TEST_PLAN))
    print("candidate      : %s" % cinder_path)
    print("candidate sha  : %s" % cand_sha)
    print("base ref       : %s" % base_ref)

    # --- Frozen functions byte-identical to v0.23.0 (cases 6,7) ---
    group("Frozen functions byte-identical to %s (no code change)" % base_ref)
    base_proc = subprocess.run(["git", "-C", repo, "show",
                                "%s:src/cinder.html" % base_ref],
                               capture_output=True, text=True)
    if base_proc.returncode != 0:
        check(False, "could extract %s:src/cinder.html" % base_ref,
              base_proc.stderr.strip()[:120])
    else:
        for fn in ("computeAwayWindow", "shouldShowWelcomeBack",
                   "checkDailyReset", "computeQuestLogStreak",
                   "computeRecentQuestEntries"):
            a = extract_function(base_proc.stdout, fn)
            b = extract_function(src, fn)
            check(a is not None and a == b,
                  "%s() byte-identical to %s" % (fn, base_ref),
                  "chars=%d" % (len(b) if b else -1))

    # --- Definition present in the code (case 1) ---
    group("Definition present in the shipped code")
    window_fn = extract_function(src, "computeAwayWindow") or ""
    check("const daysAway = gapDays - 1;" in window_fn,
          "computeAwayWindow uses daysAway = gapDays - 1")
    check("daysAway > 0 ? daysAway : 0" in window_fn,
          "daysAway clamped at 0 (daysAway > 0 ? daysAway : 0)")

    # --- Boundary sweep (cases 2,3,4,5) ---
    group("Boundary sweep gapDays 0,1,2,3,7,14,15,16,30")
    node = which_node()
    if not node:
        check(False, "node available for the away-window sandbox")
    else:
        bodies = (extract_function(src, "awayDaysSentence") or "",
                  extract_function(src, "awayQuestsSentence") or "",
                  extract_function(src, "awayStreakSentence") or "",
                  window_fn)
        rows = sweep(node, bodies)
        if rows is None:
            check(False, "the away-window sandbox ran")
        else:
            # For gapDays 0/1 the control is that the panel is NOT shown, so the
            # days sentence is not rendered. The helper still returns the one-day
            # form for daysAway 0, which is fine; the control assertion is shouldShow.
            want_sentences = {0: "You were away for a day.",
                              1: "You were away for a day.",
                              2: "You were away for a day.",
                              3: "You were away for 2 days.",
                              7: "You were away for 6 days.",
                              14: "You were away for 13 days.",
                              15: "You were away for a while.",
                              16: "You were away for a while.",
                              30: "You were away for a while."}
            for r in rows:
                g = r["g"]
                if g < 2:
                    check(r["daysAway"] == 0 and r["shouldShow"] is False,
                          "gapDays %d control: quiet, daysAway 0" % g,
                          "daysAway=%s shouldShow=%s" % (r["daysAway"], r["shouldShow"]))
                    check(r["questsMissed"] == 0,
                          "gapDays %d control: no quests reported missed" % g,
                          "questsMissed=%s" % r["questsMissed"])
                    continue
                else:
                    exp_days = g - 1
                    exp_show = True
                    check(r["daysAway"] == exp_days and r["questsMissed"] == exp_days,
                          "gapDays %d: daysAway=%d questsMissed=%d" % (g, exp_days, exp_days),
                          "got daysAway=%s questsMissed=%s" % (r["daysAway"], r["questsMissed"]))
                    check(r["shouldShow"] is exp_show,
                          "gapDays %d: panel shows" % g, "shouldShow=%s" % r["shouldShow"])
                check(r["sentence"] == want_sentences[g],
                      "gapDays %d sentence" % g, "got %r" % r["sentence"])
                check(r["questsMissed"] <= r["daysAway"],
                      "gapDays %d invariant questsMissed <= daysAway" % g,
                      "%s <= %s" % (r["questsMissed"], r["daysAway"]))
            check(rows[-1]["sentence"] == "You were away for a while.",
                  "long-absence phrasing at the top of the sweep")

        # --- Proof is non-vacuous: mutant daysAway = gapDays fails (case 4/6) ---
        group("Non-vacuity: mutant daysAway = gapDays")
        mutant = sweep(node, bodies, days_away_expr="const daysAway = gapDays;")
        if mutant is None:
            check(False, "the mutant sandbox ran")
        else:
            bad = [r for r in mutant if r["g"] == 2 and r["daysAway"] != 1]
            check(bool(bad), "mutant gapDays 2 yields daysAway != 1 (proof is not a tautology)",
                  "mutant daysAway=%s" % (mutant[2]["daysAway"] if len(mutant) > 2 else "?"))

    # --- Tone + no new field (cases 8,12) ---
    group("Static scan: tone, no new field, no inline onclick")
    check("\u2014" not in src, "no em dash anywhere in candidate")
    heavy = re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]", src)
    check(heavy is None, "no heavy emoji in candidate",
          "" if heavy is None else repr(heavy.group(0)))
    check(src.count("onclick=") == 0, "no inline onclick in candidate")
    for field in ("awayWindowStamp", "gapStamp", "daysAwayCache",
                  "awayVersion", "welcomeBackSeen"):
        check(field not in src, "no new persisted field: %s" % field)
    # Day-record shape built by checkDailyReset()
    reset = extract_function(src, "checkDailyReset") or ""
    for key in ("dayIndex", "fightsUsed", "innHealsUsed", "quest", "completedQuests"):
        check(key in reset, "checkDailyReset() builds record key: %s" % key)

    print("\n%d checks, %d failed" % (COUNT["pass"] + COUNT["fail"], COUNT["fail"]))
    print("TEST PLAN CASES: %d" % len(TEST_PLAN))
    for num, name, _m, _e, sev in TEST_PLAN:
        print("  case %-2d [%s] %s" % (num, sev, name))
    verdict = "ALL CHECKS PASS" if COUNT["fail"] == 0 else "CHECKS FAILED"
    print(verdict)
    return 0 if COUNT["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
