#!/usr/bin/env python3
"""Kai verification proof for Story 051 (Cinder welcome-back day count).

Story 051 is a VERIFICATION story with NO CODE CHANGE. It resolves the
definition of "days away" against the Story 039 decision record and the Story
040 acceptance criteria, and this script proves the shipped boundary behaviour
matches that resolution.

  daysAway = gapDays - 1   (clamped at 0)
  gapDays  = todayIdx - lastPlayIdx

where daysAway is the count of FULLY MISSED UTC days in the gap, exclusive at
both ends. Same-day (gapDays 0) and next-day (gapDays 1) returns stay quiet;
gapDays 2 fires the panel with daysAway = 1 and the one-day phrasing.

THIS PROOF PASSES AGAINST SHIPPED v0.23.0 BY DESIGN. Story 051 intends no code
change, so a passing run is the expected result, not a defect signal. Where the
Story 050/047 proofs are fail-against-shipped (they isolate a real fix), this
proof is pass-against-shipped (it reaffirms a resolved definition).

This script does NOT re-implement the functions under test. computeAwayWindow(),
awayDaysSentence(), awayQuestsSentence(), awayStreakSentence(),
shouldShowWelcomeBack() and checkDailyReset() are extracted verbatim out of
src/cinder.html into a node vm sandbox and driven there. The extraction is a
verbatim slice by paren/brace matching; the shipped file's own bytes are run.

What it proves, with pasted output:

  1. Boundary sweep over gapDays 0, 1, 2, 3, 7, 14 and 30. For each: daysAway
     (= gapDays - 1 clamped at 0), questsMissed, shouldShow, and the exact
     sentence from awayDaysSentence().
       - gapDays 0 and 1: shouldShow false, daysAway 0 (control, stays quiet).
       - gapDays 2: daysAway 1, questsMissed 1, "You were away for a day.".
       - daysAway >= 14: long-absence phrasing "You were away for a while.".
         The sweep's largest gapDays is 30 (daysAway 29); the >= 14 branch is
         also seeded directly at daysAway 14 and 15 so the boundary is exact.
  2. The invariant questsMissed <= daysAway holds at every sweep point.
  3. computeAwayWindow(), shouldShowWelcomeBack() and checkDailyReset() are
     byte-identical to v0.23.0 (git show v0.23.0:src/cinder.html, extract each
     verbatim slice, sha256 the two slices and compare).
  4. The summary path writes nothing: a static scan of the away-window read
     path for saveCharacter/saveDayState/localStorage.setItem/completeQuest/
     applyQuestProgress/state-mutating writes, plus a runtime byte-identity
     check of flambeee-cinder-save and flambeee-cinder-day across a full load
     that renders the welcome-back panel on a well-formed gapDays = 2 record.
  5. The day-record field set is unchanged: exactly
     { dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }.
  6. Degradation: completedQuests a string, an entry with a non-numeric
     dayIndex, dayState null, and storage unavailable all return "show nothing"
     without throwing.

Run:
  /home/jake/.openclaw/workspace/.venv/bin/python3 src/kai-story051-away-window-proof.py
  /home/jake/.openclaw/workspace/.venv/bin/python3 src/kai-story051-away-window-proof.py /path/to/cinder.html
Exit code 0 = the proof ran and every assertion held (expected against
v0.23.0). Non-zero = the run found a real divergence or the proof itself broke.
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
BASE_REF = "v0.23.0:src/cinder.html"

# Frozen / no-change functions for Story 051 (byte-identity proven by extraction).
FROZEN_FNS = ["computeAwayWindow", "shouldShowWelcomeBack", "checkDailyReset"]
# The away-window read path this story audits for writes.
PATH_FNS = ["computeAwayWindow", "shouldShowWelcomeBack", "awayDaysSentence",
            "awayQuestsSentence", "awayStreakSentence", "renderWelcomeBack"]
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
    "awayWindowStamp",
    "gapStamp",
    "daysAwayCache",
    "awayVersion",
    "welcomeBackSeen",
]
DAY_RECORD_SHAPE = ["dayIndex", "fightsUsed", "innHealsUsed", "quest", "completedQuests"]

# The resolved definition, restated so the sweep is asserted against it, not
# against what the code happens to return.
SWEEP = [0, 1, 2, 3, 7, 14, 30]


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
            if "function computeAwayWindow(" in txt and "function awayDaysSentence(" in txt:
                return c, txt, c
    for ref in ("feature/051-cinder-away-verify-kai:src/cinder.html",
                "main:src/cinder.html"):
        txt = git_show(ref)
        if txt and "function computeAwayWindow(" in txt:
            fd, tmp = tempfile.mkstemp(suffix="-cinder.html", prefix="story051-")
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


def static_scan(src, base_src):
    problems = []
    code = strip_comments(src)
    print("=== Static scan: shipped away-window read path (pure read) ===")
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
        if re.search(r"(character|dayState|awayWindow|rawDayState)\s*\.\s*\w+\s*=(?!=)", span):
            problems.append("assignment to character./dayState./awayWindow./rawDayState. in " + fn)
        print("  scanned %-22s %5d chars, forbidden hits: %d"
              % (fn, len(span), len(hit)))

    for f in FORBIDDEN_FIELDS:
        n = len(re.findall(r"\b" + f + r"\b", src))
        if n:
            problems.append("forbidden new field name %s appears %d time(s)" % (f, n))
        else:
            print("  no new persisted field: %s" % f)

    # The resolved definition must be present exactly as shipped.
    try:
        aw = strip_comments(body_of(src, "computeAwayWindow"))
    except RuntimeError as e:
        problems.append(str(e))
        aw = ""
    if "const daysAway = gapDays - 1;" not in aw:
        problems.append("computeAwayWindow does not compute daysAway as gapDays - 1")
    else:
        print("  computeAwayWindow: const daysAway = gapDays - 1; (the resolved definition)")
    if "daysAway > 0 ? daysAway : 0" not in aw:
        problems.append("computeAwayWindow does not clamp daysAway at 0")
    else:
        print("  computeAwayWindow: daysAway clamped at 0")

    # The day-record shape built by the reset.
    print("")
    print("=== Static scan: day-record shape built by checkDailyReset() ===")
    shape_hits = [k for k in DAY_RECORD_SHAPE if k in code]
    if len(shape_hits) < len(DAY_RECORD_SHAPE):
        problems.append("day-record shape key missing from source: %s"
                        % ", ".join(set(DAY_RECORD_SHAPE) - set(shape_hits)))
    else:
        print("  every record key present: " + ", ".join(DAY_RECORD_SHAPE))

    # Structural: exactly one definition of each frozen function.
    defs = len(re.findall(r"function computeAwayWindow\s*\(", code))
    if defs != 1:
        problems.append("expected exactly 1 computeAwayWindow definition, found %d" % defs)

    # Byte-identity of the frozen / no-change functions.
    print("")
    print("=== Static scan: frozen functions byte-identical to v0.23.0 ===")
    for fn in FROZEN_FNS:
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
        gh = hashlib.sha256(got.encode("utf-8")).hexdigest()
        bh = hashlib.sha256(want.encode("utf-8")).hexdigest()
        if gh == bh:
            print("  function %-24s byte-identical to v0.23.0 (%s)" % (fn + "()", bh[:12]))
        else:
            problems.append("%s CHANGED vs v0.23.0 (%s vs %s)" % (fn, gh[:12], bh[:12]))
            print("  BLOCK: %s changed (sha %s vs v0.23.0 %s)" % (fn, gh[:12], bh[:12]))

    if problems:
        print("")
        for p in problems:
            print("BLOCK: " + p)
    else:
        print("")
        print("PASS: away-window read path carries no writes and no new persisted field")
    return problems


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');

const SRC_PATH = __SRC_PATH__;
const src = fs.readFileSync(SRC_PATH, 'utf8');

// Deterministic "today" so every arithmetic expectation is exact.
const TODAY = Math.floor(Date.UTC(2026, 9, 29, 12) / 86400000);

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

function makeStore(seed) {
  const data = Object.assign({}, seed || {});
  const writes = [];
  let available = true;
  return {
    getItem: function (k) {
      if (!available) throw new Error('storage unavailable');
      return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null;
    },
    setItem: function (k, v) {
      if (!available) throw new Error('storage unavailable');
      writes.push([k, String(v)]); data[k] = String(v);
    },
    removeItem: function (k) { delete data[k]; },
    setUnavailable: function () { available = false; },
    _data: data,
    _writes: writes
  };
}

function makeSandbox(opts) {
  opts = opts || {};
  const calls = {
    saveCharacter: [], saveDayState: [], setItem: [], completeQuest: [],
    applyQuestProgress: [], addLog: [], syncAppBadge: [], renderTownMenu: [],
    clearLog: [], renderStatus: [], showCharacterCreation: []
  };
  const nodes = {};
  const store = opts.store || makeStore(opts.seed);
  const ctx = {
    console: console, Math: Math, Date: Date, Array: Array, Object: Object,
    JSON: JSON, isFinite: isFinite, parseInt: parseInt, String: String,
    Number: Number, Boolean: Boolean, Error: Error,
    getDayIndex: function () { return TODAY; },
    getActiveQuest: function () {
      return { label: 'Slay the cave bat', objective: 'Slay the cave bat' };
    },
    escapeHtml: function (s) {
      return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },
    localStorage: {
      getItem: function (k) { calls.setItem.push(['get', k]); return store.getItem(k); },
      setItem: function (k, v) { calls.setItem.push(['set', k]); store.setItem(k, v); },
      removeItem: function (k) { store.removeItem(k); }
    },
    saveCharacter: function () { calls.saveCharacter.push(1); },
    completeQuest: function () { calls.completeQuest.push(1); },
    applyQuestProgress: function () { calls.applyQuestProgress.push(1); },
    addLog: function (t) { calls.addLog.push(t); },
    syncAppBadge: function () { calls.syncAppBadge.push(1); },
    renderTownMenu: function () { calls.renderTownMenu.push(1); },
    clearLog: function () { calls.clearLog.push(1); },
    renderStatus: function () { calls.renderStatus.push(1); },
    showCharacterCreation: function () { calls.showCharacterCreation.push(1); },
    ensureQuestState: function () {},
    character: opts.character || { name: 'Kai', level: 3, xp: 100, gold: 50 },
    dayState: null,
    awayWindow: null,
    location: 'town',
    returnShown: false,
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
  ['escapeHtml', 'awayDaysSentence', 'awayQuestsSentence', 'awayStreakSentence',
   'computeAwayWindow', 'shouldShowWelcomeBack', 'renderWelcomeBack',
   'checkDailyReset'].forEach(function (n) {
    try { vm.runInContext(extract(n), ctx); } catch (e) { /* reported by caller */ }
  });
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
  ctx.saveDayState = function () {
    calls.saveDayState.push(1);
    try { store.setItem('flambeee-cinder-day', JSON.stringify(ctx.dayState)); } catch (e) {}
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
function rec(dayIndex, completedDays) {
  return {
    dayIndex: dayIndex,
    fightsUsed: 2,
    innHealsUsed: 1,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: (completedDays || []).map(function (d) {
      return { dayIndex: d, label: 'q' + d, objective: 'Objective ' + d };
    })
  };
}
// The welcome-back panel as renderWelcomeBack() prints it.
function renderedPanel(ctx) {
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  return html;
}

// Drive the REAL load path for a seeded record: load the day record, derive the
// away window BEFORE the reset exactly as init() does, run the shipped
// checkDailyReset(), then decide and render the panel through the shipped
// shouldShowWelcomeBack() + renderWelcomeBack().
function loadAndMaybeRender(store) {
  const ctx = makeSandbox({ store: store });
  ctx.dayState = ctx.loadDayState();
  const rawDayState = ctx.dayState;
  ctx.awayWindow = ctx.computeAwayWindow(rawDayState, ctx.getDayIndex());
  ctx.checkDailyReset();
  const show = ctx.shouldShowWelcomeBack(ctx.awayWindow, false, rawDayState);
  if (show) { ctx.returnShown = true; ctx.renderWelcomeBack(); }
  return { ctx: ctx, window: ctx.awayWindow, show: show, raw: rawDayState };
}

console.log('=== Story 051 away-window proof (extracted from shipped file) ===');
console.log('today index (deterministic): ' + TODAY);
console.log('');
console.log('PASS BY DESIGN: this proof is intended to pass against shipped ');
console.log('v0.23.0, because Story 051 makes no code change. A green run here ');
console.log('reaffirms the resolved definition, it does not report a defect.');
console.log('');

// ---------------------------------------------------------------------------
console.log('--- Section 1: boundary sweep gapDays ' + __SWEEP__.join(', ') + ' ---');
console.log('');
console.log('  lastPlayIdx is seeded at TODAY - gapDays, so gapDays is exact.');
console.log('  The day is fully recorded (a completion on lastPlayIdx), which is the');
console.log('  valid-record case: questsMissed counts the interior days with no play.');
console.log('');
(function () {
  __SWEEP__.forEach(function (gapDays) {
    const lastPlayIdx = TODAY - gapDays;
    const seed = { 'flambeee-cinder-day': JSON.stringify(rec(lastPlayIdx, [lastPlayIdx])) };
    const r = loadAndMaybeRender(makeStore(seed));
    const w = r.window;
    const daysAwayExpected = Math.max(gapDays - 1, 0);
    const sentence = r.ctx.awayDaysSentence(w.daysAway);
    const control = gapDays <= 1;

    console.log('  [gapDays ' + gapDays + ']  lastPlayIdx=TODAY-' + gapDays
                + '  shouldShow=' + w.shouldShow + '  daysAway=' + w.daysAway
                + '  questsMissed=' + w.questsMissed);
    console.log('    sentence: "' + sentence + '"');

    check(w.daysAway === daysAwayExpected,
          'gapDays ' + gapDays + ': daysAway is ' + daysAwayExpected
          + ' (= gapDays - 1 clamped at 0), got ' + w.daysAway);
    check(w.questsMissed <= w.daysAway,
          'gapDays ' + gapDays + ': invariant questsMissed <= daysAway holds ('
          + w.questsMissed + ' <= ' + w.daysAway + ')');
    if (control) {
      check(w.shouldShow === false,
            'gapDays ' + gapDays + ': control stays quiet (shouldShow false), got ' + w.shouldShow);
      check(w.daysAway === 0, 'gapDays ' + gapDays + ': daysAway 0 on the control');
    } else {
      check(w.shouldShow === true,
            'gapDays ' + gapDays + ': panel fires (shouldShow true), got ' + w.shouldShow);
    }
    if (gapDays === 2) {
      check(w.daysAway === 1 && w.questsMissed === 1,
            'gapDays 2: daysAway 1 and questsMissed 1 (got ' + w.daysAway
            + ' / ' + w.questsMissed + ')');
      check(sentence === 'You were away for a day.',
            'gapDays 2: sentence is "You were away for a day.", got "' + sentence + '"');
    }
  });
})();

// ---------------------------------------------------------------------------
console.log('');
console.log('--- Section 2: long-absence phrasing boundary (daysAway >= 14) ---');
console.log('');
console.log('  The sweep tops out at gapDays 30 -> daysAway 29, which is already in the');
console.log('  long-absence branch. To pin the exact boundary the >= 14 threshold is');
console.log('  also seeded directly at gapDays 15 (daysAway 14) and gapDays 16');
console.log('  (daysAway 15), plus gapDays 14 (daysAway 13, the last counted phrasing).');
console.log('');
(function () {
  [14, 15, 16].forEach(function (gapDays) {
    const lastPlayIdx = TODAY - gapDays;
    const seed = { 'flambeee-cinder-day': JSON.stringify(rec(lastPlayIdx, [lastPlayIdx])) };
    const r = loadAndMaybeRender(makeStore(seed));
    const w = r.window;
    const sentence = r.ctx.awayDaysSentence(w.daysAway);
    console.log('  [gapDays ' + gapDays + ']  daysAway=' + w.daysAway
                + '  sentence: "' + sentence + '"');
    if (gapDays === 15) {
      check(w.daysAway === 14, 'gapDays 15: daysAway 14 (the >= 14 boundary), got ' + w.daysAway);
    }
    if (w.daysAway >= 14) {
      check(sentence === 'You were away for a while.',
            'daysAway ' + w.daysAway + ': long-absence phrasing, got "' + sentence + '"');
    } else {
      check(sentence === 'You were away for ' + w.daysAway + ' days.',
            'daysAway ' + w.daysAway + ': counted phrasing, got "' + sentence + '"');
    }
  });
  // The shipped sweep's gapDays 30 point, restated with its sentence.
  const lastPlayIdx = TODAY - 30;
  const seed = { 'flambeee-cinder-day': JSON.stringify(rec(lastPlayIdx, [lastPlayIdx])) };
  const r = loadAndMaybeRender(makeStore(seed));
  const sentence = r.ctx.awayDaysSentence(r.window.daysAway);
  console.log('  [gapDays 30, the sweep top]  daysAway=' + r.window.daysAway
              + '  sentence: "' + sentence + '"');
  check(sentence === 'You were away for a while.',
        'gapDays 30: long-absence phrasing, got "' + sentence + '"');
})();

// ---------------------------------------------------------------------------
console.log('');
console.log('--- Section 3: end-to-end panel render at gapDays 2 (the story example) ---');
(function () {
  const lastPlayIdx = TODAY - 2;
  const seed = { 'flambeee-cinder-day': JSON.stringify(rec(lastPlayIdx, [lastPlayIdx])) };
  const r = loadAndMaybeRender(makeStore(seed));
  const html = renderedPanel(r.ctx);
  const lines = html.split('<div').slice(1).map(function (s) {
    return s.replace(/^[^>]*>/, '').replace(/<[^>]*>/g, '').trim();
  }).filter(function (s) { return s.length; });
  console.log('  panel rendered (shouldShow=' + r.show + '):');
  lines.forEach(function (l) { console.log('    | ' + l); });
  check(r.show === true, 'gapDays 2: the shipped load path shows the panel');
  check(html.indexOf('You were away for a day.') >= 0,
        'gapDays 2: panel prints "You were away for a day."');
  check(html.indexOf('1 quest went uncompleted while you were gone.') >= 0,
        'gapDays 2: panel prints "1 quest went uncompleted while you were gone."');
  check(html.indexOf('=== WELCOME BACK ===') >= 0, 'gapDays 2: panel header intact');
  check(html.indexOf('onclick') < 0, 'gapDays 2: no inline onclick in the panel');
})();

// ---------------------------------------------------------------------------
console.log('');
console.log('--- Section 4: no write on the away-window read path, byte-identical stores ---');
(function () {
  const save = { name: 'Kai', level: 3, xp: 100, hp: 30, maxHp: 30, attack: 4,
                 defense: 3, gold: 50, bank: 10, weapon: 1, armor: 1, wins: 7, losses: 2, deaths: 0 };
  const seed = {
    'flambeee-cinder-save': JSON.stringify(save),
    'flambeee-cinder-day': JSON.stringify(rec(TODAY - 2, [TODAY - 2]))
  };
  const store = makeStore(seed);
  const ctx = makeSandbox({ store: store });
  ctx.dayState = ctx.loadDayState();
  const rawDayState = ctx.dayState;
  ctx.awayWindow = ctx.computeAwayWindow(rawDayState, ctx.getDayIndex());
  ctx.checkDailyReset();
  const show = ctx.shouldShowWelcomeBack(ctx.awayWindow, false, rawDayState);

  const saveBefore = store.getItem('flambeee-cinder-save');
  const dayBefore = store.getItem('flambeee-cinder-day');
  store._writes.length = 0;
  clearCalls(ctx);

  if (show) ctx.renderWelcomeBack();   // the panel render itself

  const called = writersCalled(ctx);
  check(called.length === 0,
        'opening the panel called no writer helper ('
        + (called.length ? called.join(', ')
           : 'saveCharacter, saveDayState, localStorage.setItem, completeQuest, '
             + 'applyQuestProgress all silent') + ')');
  check(store._writes.length === 0,
        'zero key writes while rendering the panel (writes=' + store._writes.length + ')');
  check(saveBefore === store.getItem('flambeee-cinder-save'),
        'flambeee-cinder-save byte-identical across the panel render ('
        + (saveBefore === null ? 'null' : saveBefore.length + ' bytes') + ')');
  check(dayBefore === store.getItem('flambeee-cinder-day'),
        'flambeee-cinder-day byte-identical across the panel render ('
        + (dayBefore === null ? 'null' : dayBefore.length + ' bytes') + ')');
  console.log('  save before/after identical: '
              + (saveBefore === store.getItem('flambeee-cinder-save')));
  console.log('  day  before/after identical: '
              + (dayBefore === store.getItem('flambeee-cinder-day')));
})();

// ---------------------------------------------------------------------------
console.log('');
console.log('--- Section 5: day-record field set unchanged ---');
(function () {
  const ctx = makeSandbox();
  ctx.dayState = null;
  ctx.checkDailyReset();
  const keys = Object.keys(ctx.dayState).sort();
  const want = __DAY_RECORD_SHAPE__.slice().sort();
  check(JSON.stringify(keys) === JSON.stringify(want),
        'the record checkDailyReset() builds has exactly the unchanged field set ['
        + keys.join(', ') + ']');
  console.log('  record built on a fresh day: [' + keys.join(', ') + ']');
})();

// ---------------------------------------------------------------------------
console.log('');
console.log('--- Section 6: degradation returns "show nothing" without throwing ---');
(function () {
  const hidden = { shouldShow: false, daysAway: 0, questsMissed: 0, streakSurvived: false };
  const ctx = makeSandbox();
  const cases = [
    ['completedQuests is a string',        { dayIndex: TODAY - 2, completedQuests: 'nope' }],
    ['completedQuests is an object',       { dayIndex: TODAY - 2, completedQuests: {} }],
    ['entry with a non-numeric dayIndex',  { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: 'x' }] }],
    ['entry with a non-finite dayIndex',   { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: Infinity }] }],
    ['null entries mixed with one valid',  { dayIndex: TODAY - 3, completedQuests: [null, {}, 'x', { dayIndex: TODAY - 3 }] }],
    ['dayState is null',                   null],
    ['dayState is a string',               'nope'],
    ['dayState has no dayIndex',           { completedQuests: [] }]
  ];
  let thrown = null;
  cases.forEach(function (c) {
    try {
      const w = ctx.computeAwayWindow(c[1], TODAY);
      check(w && typeof w.shouldShow === 'boolean',
            c[0] + ': computeAwayWindow returns a window object');
    } catch (e) { thrown = c[0] + ': ' + e.message; }
  });
  check(thrown === null, 'no degradation case threw in computeAwayWindow'
        + (thrown ? ' [threw ' + thrown + ']' : ''));

  // The null and string records must return exactly the hidden window.
  const wn = ctx.computeAwayWindow(null, TODAY);
  const ws = ctx.computeAwayWindow('nope', TODAY);
  check(JSON.stringify(wn) === JSON.stringify(hidden),
        'dayState null returns exactly the hidden window ' + JSON.stringify(hidden));
  check(JSON.stringify(ws) === JSON.stringify(hidden),
        'dayState a string returns exactly the hidden window');
  // A non-numeric todayIdx is also hidden, never thrown.
  const wt = ctx.computeAwayWindow(rec(TODAY - 5, [TODAY - 5]), 'x');
  check(wt.shouldShow === false, 'non-numeric todayIdx returns the hidden window');
})();

(function () {
  // Storage unavailable: the shipped load path must not throw and must not show.
  const store = makeStore();
  store.setUnavailable();
  let threw = null, show = null, err = null;
  try {
    const ctx = makeSandbox({ store: store });
    const rawDayState = ctx.loadDayState();          // swallows, returns null
    ctx.awayWindow = ctx.computeAwayWindow(rawDayState, ctx.getDayIndex());
    ctx.checkDailyReset();                            // saveDayState swallows
    show = ctx.shouldShowWelcomeBack(ctx.awayWindow, false, rawDayState);
  } catch (e) { threw = e.message; err = e; }
  check(threw === null, 'storage unavailable: the load path does not throw'
        + (threw ? ' [threw ' + threw + ']' : ''));
  check(show === false, 'storage unavailable: the panel shows nothing (show=' + show + ')');
})();

console.log('');
if (failures.length === 0) {
  console.log('ALL PASS (' + passes + ' checks)');
  console.log('');
  console.log('VERDICT: shipped v0.23.0 matches the Story 051 resolved definition at');
  console.log('every sweep point. No code change is required or made. The passing run');
  console.log('is the expected outcome for a verification story.');
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
        print("BLOCK: no source file containing computeAwayWindow + awayDaysSentence found")
        return 2
    base_src = git_show(BASE_REF)
    if base_src is None:
        print("BLOCK: could not read %s for the byte-identity comparisons" % BASE_REF)
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 051 away-window proof: resolved days-away definition ===")
    print("source under test: %s" % label)
    print("resolved to: %s" % src_path)
    print("sha256: %s" % digest)
    print("base for comparison: %s" % BASE_REF)
    if digest == hashlib.sha256(base_src.encode("utf-8")).hexdigest():
        print("NOTE: the file under test is byte-identical to v0.23.0 "
              "(whole-file sha256 matches).")
    print("")

    problems = static_scan(src, base_src)

    print("")
    print("=== Node proof: extracted shipped away window, sentences, panel ===")
    node_src = PROOF_NODE.replace("__SRC_PATH__", json.dumps(src_path))
    node_src = node_src.replace("__DAY_RECORD_SHAPE__", json.dumps(DAY_RECORD_SHAPE))
    node_src = node_src.replace("__SWEEP__", json.dumps(SWEEP))
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
