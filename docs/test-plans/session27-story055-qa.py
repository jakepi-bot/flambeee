#!/usr/bin/env python3
"""Session 27 QA - Story 055 (Scout).

Cinder Record Family, Decision Record and Next Candidate Surface.

Story 055 is documentation only, so its testable surface is exactly three
things, and all three are mechanical checks against TAGGED v0.24.0 rather than
against whatever happens to be in the working tree:

  1. Every line reference the record cites resolves to the function or
     statement the record names. One reference was already corrected from
     `:754` to `:759` in Wave 2; this harness re-verifies it and the rest.

  2. The open candidate (welcome-back suppression across a later UTC day
     inside one gap) is REPRODUCED BY EXECUTION, not accepted from the record's
     own text. The three-visit trace is driven through the real shipped
     `computeAwayWindow()` and `shouldShowWelcomeBack()` extracted verbatim
     from `git show v0.24.0:src/cinder.html` into a node vm sandbox.

  3. The record is TRUTHFUL about Story 053: the load-normalization row must
     say in-flight / pending merge, never shipped, until the merged-candidate
     run actually passes.

Usage:
    /home/jake/.openclaw/workspace/.venv/bin/python3 session27-story055-qa.py
Env:
    REPO    path to the flambeee repo
    RECORD  path to the decision record under test
"""
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("REPO", "/home/jake/.openclaw/workspace/flambeee")
RECORD = os.environ.get(
    "RECORD", os.path.join(
        REPO, "docs", "stories",
        "055-cinder-record-family-decision-record.md"))

COUNT = {"pass": 0, "fail": 0}


def check(cond, name, detail=""):
    ok = bool(cond)
    COUNT["pass" if ok else "fail"] += 1
    line = ("PASS" if ok else "FAIL") + ": " + name
    if detail:
        line += " (" + str(detail) + ")"
    print(line, flush=True)
    return ok


def group(name):
    print("\n--- %s ---" % name, flush=True)


def run(cmd):
    p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True,
                       text=True)
    return p.returncode, p.stdout


def tagged_v0240():
    _, out = run("git show v0.24.0:src/cinder.html")
    return out


def line_of(lines, n):
    return lines[n - 1] if 0 < n <= len(lines) else "<out of range>"


def find_line_refs(text):
    """Every `src/cinder.html:<n>` or bare `(:<n>)` style reference."""
    refs = []
    for m in re.finditer(r"(?:src/cinder\.html)?:(\d{2,5})\b", text):
        refs.append(int(m.group(1)))
    return refs


def main():
    print("=== Session 27 Story 055 QA (Scout) ===")
    print("repo   : %s" % REPO)
    print("record : %s" % RECORD)

    src = tagged_v0240()
    lines = src.splitlines()
    if not src.strip():
        print("FAIL: could not read tagged v0.24.0:src/cinder.html")
        return 1

    # ---------------------------------------------------------------- part 1
    group("Part 1: named line references against tagged v0.24.0")

    expected = {
        522: "function computeAwayWindow(",
        615: "function shouldShowWelcomeBack(",
        664: "function dayLabelForIndex(",
        759: "let returnShown",
        1472: "shouldShowWelcomeBack(",
        1473: "returnShown = true;",
        797: "function checkDailyReset(",
        778: "function loadDayState(",
        495: "function computeRecentQuestEntries(",
        432: "function computeQuestLogStreak(",
        706: "escapeHtml(",
    }
    for ln, needle in sorted(expected.items()):
        text = line_of(lines, ln)
        check(needle in text,
              "v0.24.0 line %d is %s" % (ln, needle), repr(text.strip()))

    group("Part 1b: the corrected reference (Wave 2 fix :754 -> :759)")
    check("let returnShown" in line_of(lines, 759),
          ":759 is the returnShown declaration")
    check("returnShown" not in line_of(lines, 754),
          ":754 is NOT returnShown (the old wrong reference)")
    print("  :754 -> %r" % line_of(lines, 754).strip(), flush=True)
    print("  :759 -> %r" % line_of(lines, 759).strip(), flush=True)

    # ---------------------------------------------------------------- part 2
    group("Part 2: the open candidate REPRODUCED by execution")

    def extract(name):
        m = re.search(r"^\s*function\s+%s\s*\(" % re.escape(name), src, re.M)
        if not m:
            return None
        i = src.index("{", m.end() - 1)
        depth = 0
        for j in range(i, len(src)):
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    return src[m.start():j + 1]
        return None

    parts = {n: extract(n) for n in
             ("computeAwayWindow", "shouldShowWelcomeBack",
              "computeQuestStreak", "dayLabelForIndex")}
    for n, body in parts.items():
        check(bool(body), "%s extracted verbatim from v0.24.0" % n)

    js = r"""
const computeAwayWindow = %s;
const shouldShowWelcomeBack = %s;
const computeQuestStreak = %s;
const dayLabelForIndex = %s;
const out = [];
// Seed: last played day 100 with one completion that day.
function seeded() {
  return {dayIndex: 100, fightsUsed: 0, innHealsUsed: 0,
          quest: {progress:0, completed:false, rewarded:false},
          completedQuests: [{dayIndex: 100, objective: "Hunt the wolf",
                             label: "Hunt the wolf"}]};
}
let rec = seeded();

// One page load against a record. Models the SHIPPED load path: the window is
// derived from the loaded record BEFORE checkDailyReset(), and then the reset
// stamps the visit day into the record (that is the existing write the panel
// guard depends on). Modelling the reset write is what makes the day-104
// visit read daysAway 1 rather than 3.
function visit(dayIdx, shownThisPage, label) {
  const w = computeAwayWindow(rec, dayIdx);
  const gate = shouldShowWelcomeBack(w, shownThisPage, rec);
  out.push({label, dayIdx, shouldShow: w.shouldShow, daysAway: w.daysAway,
            questsMissed: w.questsMissed, gate: gate,
            streak: w.streakSurvived, loadedDayIndex: rec.dayIndex});
  return w;
}

visit(102, false, "visit day 102 (first)");
// checkDailyReset() on the day-102 load stamps 102 into the record.
rec = seeded(); rec.dayIndex = 102; rec.completedQuests = [];
visit(102, true, "reload day 102 (same day, record now stamped 102)");
// Still the same absence. The player plays on day 102, so the record is
// stamped 102 again; the panel must re-fire on the next new UTC day.
rec = seeded(); rec.dayIndex = 102; rec.completedQuests = [];
visit(104, false, "visit day 104 (new day, same absence)");
console.log(JSON.stringify(out, null, 2));
""" % tuple(parts[n] for n in
            ("computeAwayWindow", "shouldShowWelcomeBack",
             "computeQuestStreak", "dayLabelForIndex"))

    p = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    print(p.stdout, end="", flush=True)
    if p.returncode != 0:
        print(p.stderr, flush=True)
    check(p.returncode == 0, "the three-visit trace executed in node")
    if p.returncode != 0:
        return 1

    rows = json.loads(p.stdout)
    v102, reload102, v104 = rows[0], rows[1], rows[2]

    check(v102["shouldShow"] is True,
          "candidate reproduced: day 102 visit shows the panel",
          "shouldShow=%s daysAway=%s" % (v102["shouldShow"], v102["daysAway"]))
    check(v102["daysAway"] == 1,
          "day 102 visit reads daysAway 1, as the record states",
          "daysAway=%s" % v102["daysAway"])
    check(reload102["gate"] is False,
          "same-day day-102 reload is quiet (the Story 045 case)",
          "gate=%s" % reload102["gate"])
    check(v104["shouldShow"] is True,
          "candidate reproduced: day 104 shows the panel AGAIN, "
          "once per new UTC day inside one absence",
          "shouldShow=%s daysAway=%s" % (v104["shouldShow"], v104["daysAway"]))
    check(v104["daysAway"] == 1,
          "day 104 visit reads daysAway 1, as the record states "
          "(this requires the load path's own reset write to be modelled)",
          "daysAway=%s" % v104["daysAway"])

    group("Part 2b: the guard really is per-page-load, not persisted")
    idx = src.index("let returnShown")
    check("localStorage" not in src[idx:idx + 200],
          "returnShown is declared adjacent to no storage write")
    check(re.search(r"let\s+returnShown\s*=\s*false", src) is not None,
          "returnShown is re-initialized to false on every page load")

    # ---------------------------------------------------------------- part 3
    group("Part 3: the record is TRUTHFUL about Story 053")
    if not os.path.isfile(RECORD):
        d = os.path.join(REPO, "docs")
        hits = []
        for root, _dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".md") and "055" in f:
                    hits.append(os.path.join(root, f))
        print("  record not at the expected path; candidates: %r" % hits)
        check(False, "decision record file exists at %s" % RECORD)
    else:
        rec = open(RECORD, encoding="utf-8").read()
        low = rec.lower()
        row = [ln for ln in rec.splitlines() if "053" in ln]
        print("  Story 053 row(s) in the record:", flush=True)
        for ln in row:
            print("    " + ln.strip(), flush=True)
        in_flight = any(re.search(r"in[- ]flight|pending merge|not shipped|"
                                  r"pending, not shipped|claim under test",
                                  ln, re.I) for ln in row)
        check(in_flight,
              "the Story 053 row is marked in-flight / pending merge")
        bad = [ln for ln in row
               if re.search(r"\bshipped\b", ln, re.I)
               and not re.search(r"in[- ]flight|pending|not shipped|"
                                  r"claim under test", ln, re.I)]
        check(not bad,
              "the Story 053 row does not claim 053 shipped",
              "offending rows: %r" % bad)

        group("Part 3b: no em dashes in the record (culture rule)")
        check("\u2014" not in rec, "record contains no em dash")

    total = COUNT["pass"] + COUNT["fail"]
    print("\n=== %d checks, %d failed ===" % (total, COUNT["fail"]))
    print("RESULT: " + ("PASS" if COUNT["fail"] == 0 else "FAIL"))
    return 1 if COUNT["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())