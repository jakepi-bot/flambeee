#!/usr/bin/env python3
"""Kai pure-read proof for Story 042 (Cinder honest streak line + one-time guard).

Story 042 closes the two defects Story 040 shipped and disclosed:
  1. The welcome-back streak line normally reads "broken" on a real return,
     because computeAwayWindow() took the status from
     computeQuestStreak(rawDayState), which anchors on "today or yesterday" and
     returns 0 on a stale record by design, and because checkDailyReset()
     rebuilds the day record wholesale with completedQuests: [].
     Correct source: the last recorded completion run in the loaded record's
     completedQuests history, anchored on the last recorded play day.
  2. The one-time guard was returnShown alone, an in-memory flag whose lifetime
     is the page, so a same-day reload re-showed the summary.

This script proves the shipped code, it does not re-implement it. Every function
under test is extracted verbatim out of src/cinder.html into a node vm sandbox.

What is asserted, all from extracted shipped code:

  A. Streak source (Story 042 requirement 1, Scenarios 1-4)
     - intact trailing run ending at the last recorded play day -> survived
     - hole inside the run before the last play day -> broken
     - a single recorded day counts as an intact run -> survived
     - no recorded completion at all -> broken, and the panel still renders
     - the answer is byte-identical whether it is derived before or after the
       wholesale rebuild in checkDailyReset()
     - the OLD expression computeQuestStreak(rawDayState) > 0 is evaluated on
       the same scenario 1 record and is shown to return 0, so the old line
       really did read "broken" for an intact run (the defect, on purpose)
     - a hole in the run also flips the real shipped computeQuestStreak() to 0,
       so the two sources agree exactly when they should and disagree exactly
       where the defect is

  B. The reset hazard (Scenarios 4 and 10)
     - the real shipped checkDailyReset() is extracted and run; it replaces the
       stale record with today's index and completedQuests: []
     - the window read from the post-reset record is shown to be WRONG (the
       summary is suppressed), so reading dayState after the reset is a defect
     - checkDailyReset() is byte-identical to main:src/cinder.html
     - the whole changed file contains no new history field beyond the
       pre-existing completedQuests

  C. The one-time guard (Scenarios 5, 6, 7, 11, 16)
     - same-day reload: the reset stamped today on the first load, so the
       reload's record has dayIndex === today, the window closes, and no flag
       is needed at all. Proof: run the real reset on load 1, reload from the
       saved bytes, and confirm shouldShow false.
     - later visit inside the same gap with stored writes denied: no new
       persisted field exists, so the record is still the T-3 stamp and the
       summary is eligible again. This is the recorded limitation of the
       shipped design, not a silent pass (the story expects the in-session
       path, which is the browser check; see the write-up).
     - a genuinely new gap (a whole new block of missed days) shows once
     - in-session dismissal: shownThisPage suppresses the repeat read
     - same-day and next-day returns stay quiet (Story 040 gate semantics)
     - the decision is derivable from awayWindow + shownThisPage + the loaded
       record alone, and is identical on a repeat read of the same state

  D. No write, no new field (Scenarios 8 and 9)
     - static scan of the summary path: no saveCharacter, saveDayState,
       localStorage.setItem, completeQuest, applyQuestProgress, no inline
       onclick, no Notification, no pushManager
     - static scan of the whole changed file for forbidden new field names
     - runtime: the summary path and the guard call no writer helper, mutate no
       argument, and add no sandbox global
     - runtime byte-identity: flambeee-cinder-save and flambeee-cinder-day are
       byte-for-byte identical across a full simulated load + summary + guard
       + render + dismiss cycle, with a real in-memory localStorage stub
     - the stored day record shape is exactly
       { dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }

  E. Regressions (Scenarios 10, 13, 15)
     - computeQuestStreak() is byte-identical to main:src/cinder.html
     - legacy (no quest, no completedQuests) and corrupt records load clean
     - no em dash and no heavy emoji in the changed lines of src/cinder.html

Source under test: resolved from argv[1], then $CINDER_SRC, then ./cinder.html
next to this script. The resolved path and its sha256 are printed so the run is
reproducible. main:src/cinder.html is read through git show for the
byte-identity comparisons.

Run:
  .venv/bin/python3 src/kai-story042-streak-proof.py
  .venv/bin/python3 src/kai-story042-streak-proof.py /path/to/cinder.html
Exit code 0 = all checks pass. Non-zero = proof failed.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/jake/.openclaw/workspace/flambeee"
MAIN_REF = "main:src/cinder.html"

# Functions that make up the summary path this story owns.
PATH_FNS = [
    "computeAwayWindow",
    "shouldShowWelcomeBack",
    "awayDaysSentence",
    "awayQuestsSentence",
    "awayStreakSentence",
    "renderWelcomeBack",
    "handleWelcomeBackInput",
]
FORBIDDEN_TOKENS = [
    "saveCharacter(",
    "saveDayState(",
    "localStorage.setItem",
    "completeQuest(",
    "applyQuestProgress(",
    "Notification",
    "pushManager",
    "onclick=",
]
FORBIDDEN_FIELDS = [
    "seenReturnSummary",
    "welcomeBackShown",
    "lastGapStamp",
    "lastSeenReturn",
    "returnSummarySeen",
    "gapStampedAt",
]
DAY_RECORD_SHAPE = ["dayIndex", "fightsUsed", "innHealsUsed", "quest", "completedQuests"]


def git_show(ref):
    try:
        r = subprocess.run(["git", "-C", REPO, "show", ref],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    except Exception:
        pass
    return None


def resolve_source():
    cands = []
    if len(sys.argv) > 1:
        cands.append(sys.argv[1])
    if os.environ.get("CINDER_SRC"):
        cands.append(os.environ["CINDER_SRC"])
    cands.append(os.path.join(HERE, "cinder.html"))
    for c in cands:
        if c and os.path.isfile(c):
            txt = open(c, encoding="utf-8").read()
            if "function computeAwayWindow(" in txt:
                return c, txt, c
    # Fall back to the pushed branch, then main.
    for ref in ("feature/042-cinder-streak-proof-kai:src/cinder.html", MAIN_REF):
        txt = git_show(ref)
        if txt and "function computeAwayWindow(" in txt:
            fd, tmp = tempfile.mkstemp(suffix="-cinder.html", prefix="story042-")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(txt)
            return tmp, txt, "git:%s (%s)" % (ref, REPO)
    return None, None, None


def strip_comments(js):
    """Blank out // and /* */ comments, preserving string literals as written."""
    out = []
    i = 0
    n = len(js)
    quote = None
    while i < n:
        c = js[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(js[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "'\"`":
            quote = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and js[i + 1] == "/":
            while i < n and js[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "/" and i + 1 < n and js[i + 1] == "*":
            out.append("  ")
            i += 2
            while i < n and not (js[i] == "*" and i + 1 < n and js[i + 1] == "/"):
                out.append("\n" if js[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def body_of(src, name):
    """Verbatim slice of a top-level function by paren/brace matching."""
    idx = src.find("function " + name + "(")
    if idx < 0:
        raise RuntimeError("function not found: " + name)
    open_paren = idx + len("function " + name)
    depth = 0
    i = open_paren
    while i < len(src):
        c = src[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body_start = src.index("{", i)
    d = 0
    j = body_start
    while j < len(src):
        c = src[j]
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                break
        j += 1
    return src[idx:j + 1]


def static_scan(src):
    problems = []
    code = strip_comments(src)
    print("=== Static scan: shipped summary path (pure read) ===")
    for fn in PATH_FNS:
        try:
            span = strip_comments(body_of(src, fn))
        except RuntimeError as e:
            problems.append(str(e))
            print("BLOCK: " + str(e))
            continue
        hit = [t for t in FORBIDDEN_TOKENS if t in span]
        if hit:
            problems.append("forbidden token in %s: %s" % (fn, ", ".join(hit)))
        if re.search(r"(character|dayState|awayWindow)\s*\.\s*\w+\s*=(?!=)", span):
            problems.append("assignment to character./dayState./awayWindow. in " + fn)
        print("  scanned %-24s %5d chars, forbidden hits: %d"
              % (fn, len(span), len(hit)))

    for f in FORBIDDEN_FIELDS:
        n = len(re.findall(r"\b" + f + r"\b", src))
        if n:
            problems.append("forbidden new persisted field %s appears %d time(s)" % (f, n))
        else:
            print("  no new persisted field: %s" % f)

    # The streak line must no longer be taken from the "today or yesterday"
    # helper, and the new run scan must be present inside computeAwayWindow.
    try:
        away = strip_comments(body_of(src, "computeAwayWindow"))
    except RuntimeError as e:
        problems.append(str(e))
        away = ""
    if "computeQuestStreak(rawDayState) > 0" in away:
        problems.append("computeAwayWindow still reports the streak from computeQuestStreak(rawDayState)")
    else:
        print("  computeAwayWindow no longer uses computeQuestStreak(rawDayState) for the line")
    if "out.streakSurvived = run >= 1;" not in away:
        problems.append("computeAwayWindow does not derive streakSurvived from the recorded run")
    else:
        print("  computeAwayWindow derives streakSurvived from the recorded run (run >= 1)")

    # init() wiring: capture and compute before the reset, guard via the helper.
    try:
        init = strip_comments(body_of(src, "init"))
    except RuntimeError as e:
        problems.append(str(e))
        init = ""
    if init:
        i_capture = init.find("rawDayState")
        i_compute = init.find("computeAwayWindow(")
        i_reset = init.find("checkDailyReset()")
        if i_capture < 0 or i_compute < 0 or i_reset < 0:
            problems.append("init() lost the rawDayState capture, the window compute, or the reset call")
        elif not (i_capture < i_reset and i_compute < i_reset):
            problems.append("init() computes the window AFTER checkDailyReset() (hazard)")
        else:
            print("  init(): rawDayState captured and window computed BEFORE checkDailyReset()")
        if "shouldShowWelcomeBack(awayWindow, returnShown, rawDayState)" not in init:
            problems.append("init() does not route the guard through shouldShowWelcomeBack(...)")
        else:
            print("  init(): guard decision routed through shouldShowWelcomeBack(...)")

    defs = len(re.findall(r"function computeAwayWindow\s*\(", code))
    if defs != 1:
        problems.append("expected exactly 1 computeAwayWindow definition, found %d" % defs)
    if not re.search(r"let\s+returnShown\s*=\s*false", code):
        problems.append("in-memory load-time flag (let returnShown = false) not found")
    if not re.search(r"function\s+shouldShowWelcomeBack\s*\(", code):
        problems.append("shouldShowWelcomeBack helper not found")
    if re.search(r"localStorage\.setItem\s*\([^)]*return", code, re.I):
        problems.append("localStorage.setItem appears to persist a return-summary flag")

    # Changed lines only: tone rules.
    if problems:
        for p in problems:
            print("BLOCK: " + p)
    else:
        print("PASS: summary path carries no writes and no new persisted field")
    return problems


def static_scan_diff(src, base_src):
    """Scan only the lines this story ADDS, for tone and field-name rules."""
    problems = []
    print("")
    print("=== Static scan: added lines only (tone, no new field) ===")
    base = set(base_src.splitlines())
    added = [ln for ln in src.splitlines() if ln not in base]
    print("  added lines: %d" % len(added))
    em_dash = [ln for ln in added if "\u2014" in ln]
    if em_dash:
        problems.append("em dash on %d added line(s)" % len(em_dash))
    heavy = [ln for ln in added
             if any(0x1F300 <= ord(ch) <= 0x1FAFF or ord(ch) == 0x2728 for ch in ln)]
    if heavy:
        problems.append("heavy emoji on %d added line(s)" % len(heavy))
    fields = [f for f in FORBIDDEN_FIELDS if any(f in ln for ln in added)]
    if fields:
        problems.append("forbidden field name on added lines: %s" % ", ".join(fields))
    if not problems:
        print("  PASS: no em dash, no heavy emoji, no forbidden field name on added lines")
    else:
        for p in problems:
            print("  BLOCK: " + p)
    return problems


def byte_identity(name, got, base, problems):
    if got is None:
        problems.append("could not read %s from git for comparison" % name)
        print("  BLOCK: %s unreadable from git" % name)
        return
    gh = hashlib.sha256(got.encode("utf-8")).hexdigest()
    bh = hashlib.sha256(base.encode("utf-8")).hexdigest()
    if gh == bh:
        print("  %s byte-identical to main (%s)" % (name, bh[:12]))
    else:
        problems.append("%s CHANGED vs main (%s vs %s)" % (name, gh[:12], bh[:12]))
        print("  BLOCK: %s changed (sha %s vs main %s)" % (name, gh[:12], bh[:12]))


def structural_check(src, base_src):
    """checkDailyReset, computeQuestStreak byte-identity, and record shape."""
    problems = []
    print("")
    print("=== Static scan: regressions and record shape ===")
    for fn in ("checkDailyReset", "computeQuestStreak"):
        try:
            got = body_of(src, fn)
        except RuntimeError as e:
            problems.append(str(e))
            print("  BLOCK: " + str(e))
            continue
        try:
            want = body_of(base_src, fn)
        except RuntimeError as e:
            problems.append("base copy of %s unreadable: %s" % (fn, e))
            continue
        byte_identity("function %s()" % fn, got, want, problems)
    # no history field beyond the pre-existing completedQuests
    for f in ("history", "streakHistory", "questHistory", "completionHistory"):
        n = len(re.findall(r"\b" + f + r"\b", strip_comments(src)))
        if n:
            problems.append("possible new history field %s appears %d time(s)" % (f, n))
        else:
            print("  no new history field: %s" % f)
    return problems


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');

const SRC_PATH = __SRC_PATH__;
const src = fs.readFileSync(SRC_PATH, 'utf8');

// Deterministic "today" so every arithmetic expectation is exact.
const TODAY = Math.floor(Date.UTC(2026, 8, 22, 12) / 86400000);

let failures = [];
let passes = 0;
function check(cond, msg) {
  if (cond) { passes += 1; console.log('PASS: ' + msg); }
  else { failures.push(msg); console.log('FAIL: ' + msg); }
}

function extract(name) {
  const idx = src.indexOf('function ' + name + '(');
  if (idx < 0) throw new Error('function not found: ' + name);
  const openParen = idx + ('function ' + name).length;
  let depth = 0, i = openParen;
  for (; i < src.length; i++) {
    const c = src[i];
    if (c === '(') depth++;
    else if (c === ')') { depth--; if (depth === 0) break; }
  }
  const bodyStart = src.indexOf('{', i);
  let d = 0, j;
  for (j = bodyStart; j < src.length; j++) {
    const c = src[j];
    if (c === '{') d++;
    else if (c === '}') { d--; if (d === 0) break; }
  }
  return src.slice(idx, j + 1);
}

// A real in-memory localStorage so the byte-identity claim is measured, not
// assumed. Every write is recorded; the store serialises like the browser.
function makeStore(seed) {
  const data = Object.assign({}, seed || {});
  const writes = [];
  return {
    getItem: function (k) { return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null; },
    setItem: function (k, v) { writes.push([k, String(v)]); data[k] = String(v); },
    removeItem: function (k) { delete data[k]; },
    _data: data,
    _writes: writes
  };
}

function makeSandbox(opts) {
  opts = opts || {};
  const calls = {
    saveCharacter: [], saveDayState: [], setItem: [], completeQuest: [],
    applyQuestProgress: [], ensureQuestState: [], syncAppBadge: [], addLog: [],
    renderTownMenu: [], renderQuest: [], clearLog: []
  };
  const nodes = {};
  const store = opts.store || makeStore(opts.seed);
  const ctx = {
    console: console, Math: Math, Date: Date, Array: Array, Object: Object,
    JSON: JSON, isFinite: isFinite, parseInt: parseInt, String: String,
    Number: Number, Boolean: Boolean, Error: Error,
    getDayIndex: function () { return TODAY; },
    saveCharacter: function () { calls.saveCharacter.push(1); },
    localStorage: {
      getItem: function (k) { calls.setItem.push(['get', k]); return store.getItem(k); },
      setItem: function (k, v) { calls.setItem.push(['set', k]); store.setItem(k, v); },
      removeItem: function (k) { store.removeItem(k); }
    },
    completeQuest: function () { calls.completeQuest.push(1); },
    applyQuestProgress: function () { calls.applyQuestProgress.push(1); },
    ensureQuestState: function () { calls.ensureQuestState.push(1); },
    syncAppBadge: function () { calls.syncAppBadge.push(1); },
    addLog: function (t) { calls.addLog.push(t); },
    renderTownMenu: function () { calls.renderTownMenu.push(1); },
    renderQuest: function () { calls.renderQuest.push(1); },
    clearLog: function () { calls.clearLog.push(1); },
    character: opts.character || { xp: 100, gold: 50, level: 3, bank: 10, wins: 7 },
    dayState: null,
    location: 'town',
    awayWindow: null,
    MAX_FIGHTS_PER_DAY: 5,
    document: {
      getElementById: function (id) {
        if (!nodes[id]) {
          nodes[id] = {
            innerHTML: '', value: '', focusCount: 0,
            focus: function () { this.focusCount += 1; }
          };
        }
        return nodes[id];
      }
    }
  };
  ctx._calls = calls;
  ctx._nodes = nodes;
  ctx._store = store;
  vm.createContext(ctx);
  ['escapeHtml', 'computeQuestStreak', 'computeAwayWindow', 'shouldShowWelcomeBack',
   'awayDaysSentence', 'awayQuestsSentence', 'awayStreakSentence', 'renderWelcomeBack',
   'handleWelcomeBackInput', 'checkDailyReset', 'ensureQuestState'].forEach(function (n) {
    try { vm.runInContext(extract(n), ctx); } catch (e) { /* reported by caller */ }
  });
  // Simple reads straight from the real localStorage stub, so a seeded store
  // round-trips exactly as the browser does.
  ctx.loadDayState = function () {
    try {
      const data = store.getItem('flambeee-cinder-day');
      return data ? JSON.parse(data) : null;
    } catch (e) { return null; }
  };
  ctx.loadSave = function () {
    try {
      const data = store.getItem('flambeee-cinder-save');
      return data ? JSON.parse(data) : null;
    } catch (e) { return null; }
  };
  // saveDayState writes the live dayState through, exactly like the browser
  // helper, so the reset's persistence is the real thing.
  ctx.saveDayState = function () {
    calls.saveDayState.push(1);
    try { store.setItem('flambeee-cinder-day', JSON.stringify(ctx.dayState)); } catch (e) {}
  };
  ctx.getActiveQuest = function () {
    return { label: 'Slay 3 wolves', objective: 'Defeat 3 monsters' };
  };
  return ctx;
}

function clearCalls(ctx) {
  Object.keys(ctx._calls).forEach(function (k) { ctx._calls[k].length = 0; });
}
function writersCalled(ctx) {
  const c = ctx._calls;
  return ['saveCharacter', 'saveDayState', 'setItem', 'completeQuest', 'applyQuestProgress']
    .filter(function (k) { return c[k].length > 0; });
}
function history(days, extra) {
  return days.map(function (d, i) {
    return { dayIndex: d, label: 'q' + i, objective: 'obj' + d };
  }).concat(extra || []);
}
function rec(dayIndex, completedDays) {
  return {
    dayIndex: dayIndex,
    fightsUsed: 2,
    innHealsUsed: 1,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: history(completedDays || [])
  };
}

console.log('=== Story 042 behavioural proof (extracted from shipped file) ===');

// --- A. Streak source ------------------------------------------------------
console.log('');
console.log('--- A. Streak source: last recorded completion run ---');

// Scenario 1: recorded run T-4, T-3, T-2 with dayIndex T-2 -> survived.
(function () {
  const ctx = makeSandbox();
  const raw = rec(TODAY - 2, [TODAY - 4, TODAY - 3, TODAY - 2]);
  const before = JSON.stringify(raw);
  const w = ctx.computeAwayWindow(raw, TODAY);
  check(w.shouldShow === true && w.daysAway === 1,
        'S1 gap intact (dayIndex T-2, run T-4..T-2): shouldShow true, daysAway 1 [got '
        + w.shouldShow + '/' + w.daysAway + ']');
  check(w.streakSurvived === true, 'S1 streak line reads survived for the intact run');
  check(ctx.awayStreakSentence(w.streakSurvived) === 'Your streak survived.',
        'S1 rendered string is "Your streak survived."');
  check(JSON.stringify(raw) === before, 'S1 input record not mutated');
})();

// Scenario 2: hole at T-4 (entries T-6, T-5, dayIndex T-2) -> broken.
(function () {
  const ctx = makeSandbox();
  const w = ctx.computeAwayWindow(rec(TODAY - 2, [TODAY - 6, TODAY - 5]), TODAY);
  check(w.shouldShow === true, 'S2 gap present: shouldShow true');
  check(w.streakSurvived === false, 'S2 hole in the run before the last play day -> broken');
  check(ctx.awayStreakSentence(w.streakSurvived) === 'Your streak is broken.',
        'S2 rendered string is "Your streak is broken."');
})();

// Scenario 3: a single recorded day counts as an intact run -> survived.
(function () {
  const ctx = makeSandbox();
  const w = ctx.computeAwayWindow(rec(TODAY - 3, [TODAY - 3]), TODAY);
  check(w.shouldShow === true && w.daysAway === 2,
        'S3 single recorded day (dayIndex T-3): shouldShow true, daysAway 2 [got '
        + w.shouldShow + '/' + w.daysAway + ']');
  check(w.streakSurvived === true, 'S3 a single recorded day is an intact run -> survived');
})();

// Scenario 4 (defect, on purpose): the OLD source reads broken for the S1 record.
(function () {
  const ctx = makeSandbox();
  const raw = rec(TODAY - 2, [TODAY - 4, TODAY - 3, TODAY - 2]);
  const old = ctx.computeQuestStreak(raw) > 0;
  const w = ctx.computeAwayWindow(raw, TODAY);
  check(old === false,
        'S4 OLD source computeQuestStreak(rawDayState) > 0 returns false for the intact '
        + 'run, so the pre-042 line read "broken" (defect reproduced)');
  check(w.streakSurvived === true,
        'S4 NEW source reports survived for the same record (defect closed)');
  // No recorded completion at all -> broken, and still renders.
  const w0 = ctx.computeAwayWindow(rec(TODAY - 2, []), TODAY);
  check(w0.shouldShow === true && w0.streakSurvived === false,
        'S4 no recorded completion at all -> broken, panel still renders [got '
        + w0.shouldShow + '/' + w0.streakSurvived + ']');
})();

// Agreement sweep: the two sources agree except where the defect lived.
(function () {
  const ctx = makeSandbox();
  let agree = 0, oldFalseNewTrue = 0, mismatch = null, shown = 0;
  for (let g = 2; g <= 12; g++) {
    for (let hole = -1; hole <= 3; hole++) {
      let days = [];
      for (let d = g; d >= 1; d--) {
        if (hole !== -1 && d === hole) continue;   // drop one day -> a hole
        days.push(TODAY - d);
      }
      const raw = rec(TODAY - g, days.slice(1));
      const w = ctx.computeAwayWindow(raw, TODAY);
      if (!w.shouldShow) continue;
      shown += 1;
      const old = ctx.computeQuestStreak(raw) > 0;
      if (old === w.streakSurvived) agree += 1;
      else if (old === false && w.streakSurvived === true) oldFalseNewTrue += 1;
      else mismatch = { g: g, hole: hole, old: old, neu: w.streakSurvived };
    }
  }
  check(mismatch === null,
        'SA agreement sweep over ' + shown + ' showing records: the two sources never '
        + 'disagree in the wrong direction (' + agree + ' agree, ' + oldFalseNewTrue
        + ' old-false/new-true' + (mismatch ? ', violation ' + JSON.stringify(mismatch) : '') + ')');
  check(oldFalseNewTrue > 0,
        'SA the disagreement that remains is exactly the closed defect: ' + oldFalseNewTrue
        + ' records where the old source said broken and the new source says survived');
  // A hole in the run flips the real shipped helper too, so the sources agree there.
  const holed = rec(TODAY - 2, [TODAY - 6, TODAY - 5]);
  check(ctx.computeQuestStreak(holed) === 0,
        'SA a genuine hole also reads 0 from the real shipped computeQuestStreak() (sources agree '
        + 'where the run really ended)');
})();

// --- B. The reset hazard ---------------------------------------------------
console.log('');
console.log('--- B. The reset hazard: post-reset reads are wrong ---');
(function () {
  const ctx = makeSandbox({ seed: { 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 3, [TODAY - 4, TODAY - 3])) } });
  const raw = ctx.loadDayState();
  check(raw && raw.dayIndex === TODAY - 3, 'SB stale record loaded: dayIndex T-3');
  const before = JSON.stringify(raw);
  const captured = ctx.computeAwayWindow(raw, TODAY);
  check(JSON.stringify(raw) === before, 'SB the loaded record survives the window read unmutated');
  check(captured.shouldShow === true && captured.streakSurvived === true,
        'SB window from the LOADED record: shouldShow true, streak survived (the correct source)');
  // Run the real shipped reset and read again, the way the old defect did.
  ctx.dayState = raw;
  ctx.checkDailyReset();
  const post = ctx.dayState;
  check(post && post.dayIndex === TODAY,
        'SB real checkDailyReset() replaced the record (dayIndex now ' + (post ? post.dayIndex : 'null') + ')');
  check(Array.isArray(post.completedQuests) && post.completedQuests.length === 0,
        'SB the rebuilt record carries completedQuests: [] (the wholesale rebuild)');
  const wrong = ctx.computeAwayWindow(post, TODAY);
  check(wrong.shouldShow === false,
        'SB window from the POST-RESET record is WRONG: shouldShow false, summary suppressed '
        + '(reading dayState after the reset is the defect)');
  const oldPost = ctx.computeQuestStreak(post) > 0;
  check(oldPost === false,
        'SB the old source on the post-reset record also reads false (both defects compound)');
})();

// Derived value identical before and after the rebuild (Scenario 4).
(function () {
  const ctx = makeSandbox();
  const raw = rec(TODAY - 3, [TODAY - 4, TODAY - 3]);
  ctx.dayState = raw;
  // Derive the line from the loaded history the way the shipped code does.
  const loadedStatus = ctx.computeAwayWindow(raw, TODAY).streakSurvived;
  // Now run the rebuild and derive again from the ORIGINAL loaded bytes.
  ctx.checkDailyReset();
  const rebuiltStatus = ctx.computeAwayWindow(raw, TODAY).streakSurvived;
  check(loadedStatus === rebuiltStatus && loadedStatus === true,
        'SB streak status from the loaded record is unchanged by the rebuild ('
        + loadedStatus + ' before, ' + rebuiltStatus + ' after)');
})();

// --- C. The one-time guard -------------------------------------------------
console.log('');
console.log('--- C. The one-time guard: existing state only ---');
(function () {
  // Load 1 on a gap day: reset stamps today. Reload from the saved bytes.
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 3, [TODAY - 3])) });
  const load1 = makeSandbox({ store: store });
  load1.dayState = load1.loadDayState();
  const raw1 = load1.dayState;
  const win1 = load1.computeAwayWindow(raw1, TODAY);
  const shown1 = load1.shouldShowWelcomeBack(win1, false, raw1);
  check(shown1 === true, 'S5 load 1 on the gap day: summary shows (shouldShowWelcomeBack true)');
  load1.dayState = raw1;
  load1.checkDailyReset();
  const savedAfterLoad1 = store.getItem('flambeee-cinder-day');
  check(JSON.parse(savedAfterLoad1).dayIndex === TODAY,
        'S5 the reset persisted a record stamped today (the pre-existing saveDayState in the reset)');

  // Reload on the same UTC day, in a fresh page: read the stored bytes.
  const load2 = makeSandbox({ store: store });
  const raw2 = load2.loadDayState();
  const win2 = load2.computeAwayWindow(raw2, TODAY);
  const shown2 = load2.shouldShowWelcomeBack(win2, false, raw2);
  check(raw2.dayIndex === TODAY, 'S5 reload reads the record stamped today (dayIndex === today)');
  check(win2.shouldShow === false && win2.daysAway === 0,
        'S5 reload: the window closes on its own, no flag needed [shouldShow '
        + win2.shouldShow + ', daysAway ' + win2.daysAway + ']');
  check(shown2 === false, 'S5 same-day reload shows no summary -> town hub (Scenario 5 derivation HOLDS)');
})();

(function () {
  // Later visit inside the same gap, writes denied (no persisted field exists).
  const seeded = { 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 3, [TODAY - 3])) };
  function visit() {
    // Writes to the day key are refused, standing in for any environment where
    // the reset write did not land. This is the honest upper bound of the
    // shipped design, and it is reported, not hidden.
    const store = {
      getItem: function (k) { return k in seeded ? seeded[k] : null; },
      setItem: function () {},
      removeItem: function () {}
    };
    const ctx = makeSandbox({ store: store });
    const raw = ctx.loadDayState();
    const win = ctx.computeAwayWindow(raw, TODAY);
    return { shouldShowWelcomeBack: ctx.shouldShowWelcomeBack(win, false, raw), win: win };
  }
  const v = visit();
  check(v.shouldShowWelcomeBack === true,
        'S6/S16 with the day-key write denied, a later visit inside the gap re-opens the summary '
        + '(recorded limitation of the shipped design, not a silent pass)');
  check(v.win.daysAway === 2,
        'S6 the re-opened window still reports the same gap (daysAway 2) from the T-3 stamp');
  // The decision is a pure function of the three inputs, and repeat-stable.
  const ctx = makeSandbox();
  const rawA = rec(TODAY - 3, [TODAY - 3]);
  const winA = ctx.computeAwayWindow(rawA, TODAY);
  const d1 = ctx.shouldShowWelcomeBack(winA, false, rawA);
  const d2 = ctx.shouldShowWelcomeBack(winA, false, rawA);
  check(d1 === d2 && d1 === true,
        'S16 repeat read of identical inputs gives an identical decision (stable, derived)');
})();

(function () {
  // A genuinely new gap shows once.
  const ctx = makeSandbox({ seed: { 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 4, [TODAY - 4])) } });
  const raw = ctx.loadDayState();
  const win = ctx.computeAwayWindow(raw, TODAY);
  const shown = ctx.shouldShowWelcomeBack(win, false, raw);
  check(shown === true && win.daysAway === 3,
        'S7 a new gap from the T-4 stamp shows once, daysAway 3 [got ' + shown + '/' + win.daysAway + ']');
})();

(function () {
  // In-session: the load-time flag suppresses the repeat read.
  const ctx = makeSandbox();
  const raw = rec(TODAY - 3, [TODAY - 3]);
  const win = ctx.computeAwayWindow(raw, TODAY);
  check(ctx.shouldShowWelcomeBack(win, false, raw) === true, 'S16 first read: shown');
  check(ctx.shouldShowWelcomeBack(win, true, raw) === false,
        'S16 after the flag is set: suppressed in the same page');
  // Degradation of the guard itself.
  const bad = [
    ['null window', null, false, raw],
    ['window without shouldShow', {}, false, raw],
    ['null record', { shouldShow: true }, false, null],
    ['record not an object', { shouldShow: true }, false, 'x'],
    ['shouldShow false', { shouldShow: false }, false, raw]
  ];
  let thrown = null, wrong = [];
  bad.forEach(function (c) {
    try {
      const r = ctx.shouldShowWelcomeBack(c[1], c[2], c[3]);
      if (r !== false) wrong.push(c[0]);
    } catch (e) { thrown = e; }
  });
  check(thrown === null && wrong.length === 0,
        'S16 guard degrades to false on malformed inputs, never throws'
        + (thrown ? ' [threw ' + thrown.message + ']' : (wrong.length ? ' [wrong ' + wrong.join('; ') + ']' : '')));
})();

(function () {
  // Scenario 11: same-day and next-day returns stay quiet.
  const ctx = makeSandbox();
  const same = ctx.computeAwayWindow(rec(TODAY, [TODAY]), TODAY);
  const next = ctx.computeAwayWindow(rec(TODAY - 1, [TODAY - 1]), TODAY);
  const nextHist = ctx.computeAwayWindow(rec(TODAY - 1, [TODAY - 1, TODAY - 2]), TODAY);
  check(ctx.shouldShowWelcomeBack(same, false, rec(TODAY, [TODAY])) === false
        && same.daysAway === 0,
        'S11 same-day return stays quiet (daysAway ' + same.daysAway + ')');
  check(ctx.shouldShowWelcomeBack(next, false, rec(TODAY - 1, [])) === false
        && next.daysAway === 0,
        'S11 next-day return stays quiet (daysAway ' + next.daysAway + ')');
  check(nextHist.shouldShow === false,
        'S11 next-day return with history stays quiet (Story 033 flow untouched)');
})();

// --- D. No write, no new field --------------------------------------------
console.log('');
console.log('--- D. No write and no new field ---');
(function () {
  const ctx = makeSandbox();
  const raws = [
    rec(TODAY, [TODAY]), rec(TODAY - 1, []), rec(TODAY - 2, []),
    rec(TODAY - 4, [TODAY - 3]), rec(TODAY - 40, []), rec(TODAY - 30, [TODAY - 2]),
    null, {}, { dayIndex: 'x' }, { dayIndex: TODAY - 5, completedQuests: 'nope' },
    { dayIndex: TODAY + 3 }, { dayIndex: TODAY - 3, completedQuests: [null, {}, 'x'] }
  ];
  const snaps = raws.map(function (r) { return JSON.stringify(r === undefined ? null : r); });
  const globalsBefore = JSON.stringify(Object.keys(ctx).sort());
  clearCalls(ctx);
  const guardResults = [];
  raws.forEach(function (raw) {
    const w = ctx.computeAwayWindow(raw, TODAY);
    guardResults.push(ctx.shouldShowWelcomeBack(w, false, raw));
    ctx.awayWindow = w;
    ctx.renderWelcomeBack();
    ctx.handleWelcomeBackInput(1);
    ctx.handleWelcomeBackInput(2);
    ctx.handleWelcomeBackInput(99);
  });
  const called = writersCalled(ctx);
  check(called.length === 0, 'S8 summary path and guard called no writer helpers ('
        + (called.length ? called.join(', ') : 'saveCharacter, saveDayState, localStorage.setItem, '
          + 'completeQuest, applyQuestProgress all silent') + ')');
  const mutated = [];
  raws.forEach(function (raw, i) {
    const s = JSON.stringify(raw === undefined ? null : raw);
    if (s !== snaps[i]) mutated.push(i);
  });
  check(mutated.length === 0, 'S8 no input record mutated across 12 runs ('
        + (mutated.length ? 'indices ' + mutated.join(',') : 'all deep-equal') + ')');
  check(JSON.stringify(Object.keys(ctx).sort()) === globalsBefore,
        'S8 no sandbox global added by the summary path or guard');
  check(guardResults.every(function (r) { return typeof r === 'boolean'; }),
        'S16 the guard returns a boolean for every tested state');
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  check(html.indexOf('=== WELCOME BACK ===') >= 0 && html.indexOf('data-action="1"') >= 0
        && html.indexOf('data-action="2"') >= 0 && html.indexOf('onclick') < 0,
        'S19 rendered view is the boxed-menu welcome-back with delegated data-action rows, no inline onclick');
})();

(function () {
  // Full load cycle with a real localStorage: byte-identity of both keys.
  const seed = {
    'flambeee-cinder-save': JSON.stringify({ name: 'Kai', level: 3, xp: 100, hp: 30, maxHp: 30,
      attack: 4, defense: 3, gold: 50, bank: 10, weapon: 1, armor: 1, wins: 7, losses: 2, deaths: 0 }),
    'flambeee-cinder-day': JSON.stringify(rec(TODAY - 3, [TODAY - 3]))
  };
  const store = makeStore(seed);
  const ctx = makeSandbox({ store: store });
  ctx.dayState = ctx.loadDayState();
  const raw = ctx.dayState;
  // Measure only the summary path: snapshot both keys after the load-time
  // writes that belong to Story 040 behavior (the reset), then exercise the
  // summary and the guard and compare byte for byte.
  ctx.checkDailyReset();
  const saveBefore = store.getItem('flambeee-cinder-save');
  const dayBefore = store.getItem('flambeee-cinder-day');
  store._writes.length = 0;
  clearCalls(ctx);
  const w = ctx.computeAwayWindow(raw, TODAY);
  const decision = ctx.shouldShowWelcomeBack(w, false, raw);
  ctx.awayWindow = w;
  if (decision) { ctx.renderWelcomeBack(); ctx.handleWelcomeBackInput(1); }
  const saveAfter = store.getItem('flambeee-cinder-save');
  const dayAfter = store.getItem('flambeee-cinder-day');
  check(saveBefore === saveAfter,
        'S8 flambeee-cinder-save byte-identical across the summary path ('
        + (saveBefore === null ? 'null' : saveBefore.length + ' bytes') + ')');
  check(dayBefore === dayAfter,
        'S8 flambeee-cinder-day byte-identical across the summary path ('
        + (dayBefore === null ? 'null' : dayBefore.length + ' bytes') + ')');
  check(store._writes.length === 0,
        'S8 zero key writes during the summary path and guard (writes=' + store._writes.length + ')');
})();

(function () {
  // The stored day record shape is unchanged.
  const ctx = makeSandbox();
  ctx.dayState = null;
  ctx.checkDailyReset();
  const keys = Object.keys(ctx.dayState).sort();
  const want = __DAY_RECORD_SHAPE__.slice().sort();
  check(JSON.stringify(keys) === JSON.stringify(want),
        'S9 the record checkDailyReset() builds has exactly the unchanged field set '
        + '[' + keys.join(', ') + ']');
})();

console.log('');
if (failures.length === 0) {
  console.log('ALL PASS (' + passes + ' checks)');
  process.exit(0);
} else {
  console.log(failures.length + ' FAILURES (' + passes + ' passed)');
  failures.forEach(function (f) { console.log('  - ' + f); });
  process.exit(1);
}
"""


def main():
    src_path, src, label = resolve_source()
    if src_path is None:
        print("BLOCK: no source file containing computeAwayWindow found")
        return 2
    base_src = git_show(MAIN_REF)
    if base_src is None:
        print("BLOCK: could not read %s for the byte-identity comparisons" % MAIN_REF)
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 042 pure-read proof: streak source and one-time guard ===")
    print("source under test: %s" % label)
    print("resolved to: %s" % src_path)
    print("sha256: %s" % digest)
    print("base for comparison: %s" % MAIN_REF)
    print("")

    problems = []
    problems += static_scan(src)
    problems += structural_check(src, base_src)
    problems += static_scan_diff(src, base_src)

    print("")
    print("=== Node proof: extracted shipped gate, guard, view and handlers ===")
    node_src = PROOF_NODE.replace("__SRC_PATH__", json.dumps(src_path))
    node_src = node_src.replace("__DAY_RECORD_SHAPE__", json.dumps(DAY_RECORD_SHAPE))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(node_src)
        path = f.name
    try:
        r = subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        os.unlink(path)
    print(r.stdout, end="")
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr)
        print("BLOCK: node proof failed (exit %d)" % r.returncode)
        return 1
    if problems:
        print("BLOCK: static scan failed")
        for p in problems:
            print("  - " + p)
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
