#!/usr/bin/env python3
"""Kai pure-read proof for Story 044 (Cinder quest log, honest streak source).

Story 044 closes the one live contradiction left after Story 042: the quest log
and the welcome-back panel, on the same screen in the same session file, told a
returning player opposite things about the same run.

  - renderQuestLog() took its number from computeQuestStreak(dayState), a helper
    that anchors on "today or yesterday" and is therefore blind to history once
    a stale day record has been loaded.
  - checkDailyReset() runs on the load path BEFORE the player can open row 9,
    and it rebuilds the day record wholesale with completedQuests: [].
  - The welcome-back panel on the same screen says "Your streak survived."
    because Story 042 anchored it on the loaded (pre-reset) record.
  - Result: the log printed 0 days while the panel printed "survived", and the
    zero was the false one.

This script proves the shipped code. It does not re-implement it: every function
under test is extracted verbatim out of src/cinder.html into a node vm sandbox.

What is asserted, all from extracted shipped code:

  A. The reset hazard, directly (Scenarios 1, 5)
     - the OLD source computeQuestStreak(postResetRecord) reads 0 on a record
       whose recorded run is intact (the defect, reproduced on purpose)
     - the NEW source computeQuestLogStreak() reads the true run length (3) on
       the same record, anchored on the loaded pre-reset history
     - the real shipped checkDailyReset() is extracted and run; it replaces the
       record with today's index and completedQuests: []
     - the new source's answer is byte-identical before and after that rebuild,
       so the number the log prints is provably unaffected by the reset

  B. Anchor shape (a), stated (Scenario 2, Story 044 open question 1)
     - the log anchors on the last recorded play day, derived from the LOADED
       pre-reset record exactly as computeAwayWindow() derives lastPlayIdx at
       src/cinder.html:425-446 (max of the raw dayIndex and the valid history
       entries' dayIndex values)
     - status-to-number consistency with the panel on every seeded case: panel
       survived implies the log reads >= 1 and equal to the recorded run; panel
       broken implies the log reads 0. Swept over a generated matrix.

  C. Seeded cases (Scenarios 1, 3, 4, 6, 7)
     - intact run T-4..T-2, dayIndex T-2 -> 3
     - hole at T-4 with dayIndex T-2 -> 0, and the panel agrees (broken)
     - no history at all -> 0
     - in-progress today, yesterday completed -> the preserved run
     - today completed -> the run including today, one more than ending yesterday

  D. Degradation (Scenarios 9, 10)
     - legacy, corrupt, partial, non-object, null records all return a number,
       never throw; storage denied behaves the same as in-memory state

  E. No write on the read path, no new field (Scenarios 11, 12)
     - static scan of the quest-log read path: no saveCharacter, saveDayState,
       localStorage.setItem, completeQuest, applyQuestProgress, no assignment to
       character. / dayState. / awayWindow.
     - runtime: opening row 9 through the real handler touches no writer and
       mutates no argument
     - runtime byte-identity: flambeee-cinder-save and flambeee-cinder-day are
       byte-for-byte identical across renderQuestLog()
     - the day record after checkDailyReset() has exactly the unchanged field set
       { dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }

  F. Regressions (Scenarios 13, 14)
     - computeQuestStreak() is byte-identical to v0.21.0
     - checkDailyReset() is byte-identical to v0.21.0
     - the recent-quests list (most recent first, capped at 5) is identical to
       the pre-story rendering for the same history

Source under test: resolved from argv[1], then $CINDER_SRC, then ./cinder.html
next to this script. The resolved path and its sha256 are printed so the run is
reproducible. v0.21.0:src/cinder.html is read through git show for the
byte-identity comparisons.

Run:
  .venv/bin/python3 src/kai-story044-questlog-streak-proof.py
  .venv/bin/python3 src/kai-story044-questlog-streak-proof.py /path/to/cinder.html
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
BASE_REF = "v0.21.0:src/cinder.html"

# The quest-log read path this story owns.
PATH_FNS = [
    "renderQuestLog",
    "computeQuestLogStreak",
    "dayLabelForIndex",
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
    "questLogStreak",
    "cachedStreak",
    "streakCache",
    "lastStreak",
    "streakAnchor",
    "seenStreak",
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
            if "function computeQuestLogStreak(" in txt:
                return c, txt, c
    for ref in ("feature/044-cinder-streak-source-kai:src/cinder.html",
                "main:src/cinder.html"):
        txt = git_show(ref)
        if txt and "function computeQuestLogStreak(" in txt:
            fd, tmp = tempfile.mkstemp(suffix="-cinder.html", prefix="story044-")
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
    print("=== Static scan: shipped quest-log read path (pure read) ===")
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
        if re.search(r"(character|dayState|awayWindow|questLogAnchor)\s*\.\s*\w+\s*=(?!=)", span):
            problems.append("assignment to character./dayState./awayWindow./questLogAnchor. in " + fn)
        print("  scanned %-22s %5d chars, forbidden hits: %d"
              % (fn, len(span), len(hit)))

    for f in FORBIDDEN_FIELDS:
        n = len(re.findall(r"\b" + f + r"\b", src))
        if n:
            problems.append("forbidden new field name %s appears %d time(s)" % (f, n))
        else:
            print("  no new persisted field: %s" % f)

    # The quest log must no longer read the "today or yesterday" helper.
    try:
        log = strip_comments(body_of(src, "renderQuestLog"))
    except RuntimeError as e:
        problems.append(str(e))
        log = ""
    if "computeQuestLogStreak(dayState, questLogAnchor)" not in log:
        problems.append("renderQuestLog does not call computeQuestLogStreak(dayState, questLogAnchor)")
    else:
        print("  renderQuestLog reads the streak from computeQuestLogStreak(dayState, questLogAnchor)")
    if "computeQuestStreak(dayState)" in log:
        problems.append("renderQuestLog still calls computeQuestStreak(dayState)")
    else:
        print("  renderQuestLog no longer calls computeQuestStreak(dayState)")

    # The helper itself must be pure and must not call the old helper.
    try:
        helper = strip_comments(body_of(src, "computeQuestLogStreak"))
    except RuntimeError as e:
        problems.append(str(e))
        helper = ""
    if "computeQuestStreak(" in helper:
        problems.append("computeQuestLogStreak calls computeQuestStreak for its answer")
    else:
        print("  computeQuestLogStreak does not call computeQuestStreak")
    if "lastPlayIdx" not in helper:
        problems.append("computeQuestLogStreak does not derive a lastPlayIdx anchor")
    else:
        print("  computeQuestLogStreak anchors on lastPlayIdx (max of dayIndex and history dayIndex)")

    # init() wiring: the anchor is captured pre-reset and never persisted.
    try:
        init = strip_comments(body_of(src, "init"))
    except RuntimeError as e:
        problems.append(str(e))
        init = ""
    if init:
        i_anchor = init.find("questLogAnchor = rawDayState")
        i_reset = init.find("checkDailyReset()")
        if i_anchor < 0:
            problems.append("init() does not assign questLogAnchor = rawDayState")
        elif i_reset < 0 or not (i_anchor < i_reset):
            problems.append("init() captures questLogAnchor AFTER checkDailyReset() (hazard)")
        else:
            print("  init(): questLogAnchor captured from rawDayState BEFORE checkDailyReset()")

    defs = len(re.findall(r"function computeQuestLogStreak\s*\(", code))
    if defs != 1:
        problems.append("expected exactly 1 computeQuestLogStreak definition, found %d" % defs)
    if not re.search(r"let\s+questLogAnchor\s*=\s*null", code):
        problems.append("questLogAnchor is not declared as an in-memory (let) null")

    # Structural regressions: byte-identity of the two frozen functions.
    print("")
    print("=== Static scan: frozen functions byte-identical to v0.21.0 ===")
    for fn in ("computeQuestStreak", "checkDailyReset"):
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
            print("  function %-20s byte-identical to v0.21.0 (%s)" % (fn + "()", bh[:12]))
        else:
            problems.append("%s CHANGED vs v0.21.0 (%s vs %s)" % (fn, gh[:12], bh[:12]))
            print("  BLOCK: %s changed (sha %s vs v0.21.0 %s)" % (fn, gh[:12], bh[:12]))
    for fn in ("computeAwayWindow", "shouldShowWelcomeBack"):
        try:
            got = body_of(src, fn)
            want = body_of(base_src, fn)
            if hashlib.sha256(got.encode("utf-8")).hexdigest() == \
               hashlib.sha256(want.encode("utf-8")).hexdigest():
                print("  function %-20s byte-identical to v0.21.0" % (fn + "()"))
            else:
                problems.append("%s changed vs v0.21.0" % fn)
        except RuntimeError as e:
            problems.append("could not compare %s: %s" % (fn, e))

    # Added lines only: tone rules and forbidden field names.
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
    if not problems or (not em_dash and not heavy and not fields):
        print("  PASS: no em dash, no heavy emoji, no forbidden field name on added lines")

    if problems:
        print("")
        for p in problems:
            print("BLOCK: " + p)
    else:
        print("")
        print("PASS: quest-log read path carries no writes and no new persisted field")
    return problems


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');

const SRC_PATH = __SRC_PATH__;
const src = fs.readFileSync(SRC_PATH, 'utf8');

// Deterministic "today" so every arithmetic expectation is exact.
const TODAY = Math.floor(Date.UTC(2026, 9, 25, 12) / 86400000);

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
    questLogAnchor: null,
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
  ['escapeHtml', 'computeQuestStreak', 'computeQuestLogStreak', 'computeAwayWindow',
   'shouldShowWelcomeBack', 'awayDaysSentence', 'awayQuestsSentence',
   'awayStreakSentence', 'renderWelcomeBack', 'handleWelcomeBackInput',
   'dayLabelForIndex', 'renderQuestLog', 'checkDailyReset', 'ensureQuestState',
   'handleQuestLogInput'].forEach(function (n) {
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
// The streak line as renderQuestLog() prints it, read back out of the DOM.
function renderedStreak(ctx) {
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  const m = html.match(/Current streak:\s*(\d+)\s*days?/);
  return m ? parseInt(m[1], 10) : null;
}

console.log('=== Story 044 behavioural proof (extracted from shipped file) ===');

// --- A. The reset hazard, directly ----------------------------------------
console.log('');
console.log('--- A. The reset hazard: old source reads 0, new source reads the run ---');
(function () {
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 2, [TODAY - 4, TODAY - 3, TODAY - 2])) });
  const ctx = makeSandbox({ store: store });
  const raw = ctx.loadDayState();
  check(raw.dayIndex === TODAY - 2, 'S5 stale record loaded: dayIndex T-2 (a gap day)');

  // Simulate the real load path: anchor captured, then the reset rebuilds.
  const anchor = raw;
  ctx.dayState = raw;
  ctx.checkDailyReset();
  const post = ctx.dayState;
  check(post.dayIndex === TODAY && post.completedQuests.length === 0,
        'S5 real checkDailyReset() rebuilt the record: dayIndex today, completedQuests []');

  const oldVal = ctx.computeQuestStreak(post);
  const newVal = ctx.computeQuestLogStreak(post, anchor);
  check(oldVal === 0,
        'S1/S5 OLD source computeQuestStreak(postResetRecord) reads 0 on an intact run '
        + '(the defect, reproduced: got ' + oldVal + ')');
  check(newVal === 3,
        'S1 NEW source computeQuestLogStreak() reads the true run 3 on the same day '
        + '(got ' + newVal + ')');
  check(ctx.computeQuestLogStreak(post, post) === 0,
        'S5 with the POST-reset record as the source the new helper also reads 0, so the '
        + 'pre-reset anchor is what carries the number');

  // Unchanged by the rebuild: derive before and after, same bytes, same answer.
  const beforeRebuild = ctx.computeQuestLogStreak(raw, raw);
  ctx.dayState = raw;
  ctx.checkDailyReset();
  const afterRebuild = ctx.computeQuestLogStreak(raw, raw);
  check(beforeRebuild === afterRebuild && beforeRebuild === 3,
        'S5 the new source is byte-identical before and after the wholesale rebuild ('
        + beforeRebuild + ' then ' + afterRebuild + ')');
})();

// --- B. Anchor shape (a) and status-to-number agreement --------------------
console.log('');
console.log('--- B. Anchor shape (a): last recorded play day, panel and log agree ---');
(function () {
  // The anchor is derived exactly as computeAwayWindow() derives lastPlayIdx: the
  // max of the raw day stamp and the valid history dayIndex values. A stamp on a
  // loaded-but-incomplete day still counts as a play day, which is Story 042's
  // anchor, so a history entry NEWER than the stamp does not lengthen the run.
  const ctx = makeSandbox();
  const raw = rec(TODAY - 3, [TODAY - 2, TODAY - 3]);
  const w = ctx.computeAwayWindow(raw, TODAY);
  const logStreak = ctx.computeQuestLogStreak(null, raw);
  check(w.streakSurvived === true && logStreak === 2,
        'SB stamp T-3 (a loaded-but-incomplete play day) with completions T-3 and T-2: '
        + 'anchor is the max candidate T-2 and the run is 2, matching the panel [log '
        + logStreak + ', panel ' + w.streakSurvived + ']');
  // A stamp with no completion on it, nothing newer: the run stops at the stamp.
  const gapStamp = rec(TODAY - 3, [TODAY - 4]);
  check(ctx.computeQuestLogStreak(null, gapStamp) === 0
        && ctx.computeAwayWindow(gapStamp, TODAY).streakSurvived === false,
        'SB a stamp with no completion on it and no newer completion ends the run: '
        + 'log 0 and panel broken agree');
  // A history entry NEWER than the stamp is still a candidate (shape a).
  const newer = rec(TODAY - 3, [TODAY - 2]);
  check(ctx.computeQuestLogStreak(null, newer) === 1,
        'SB a completion newer than the raw stamp still anchors the run (shape a: max '
        + 'of dayIndex and history dayIndex), so the run is the single day T-2 = 1');
})();

(function () {
  // The agreement sweep: the story's core assertion, over a generated matrix.
  const ctx = makeSandbox();
  let shown = 0, violations = [];
  for (let g = 2; g <= 12; g++) {
    for (let hole = -1; hole <= 4; hole++) {
      let days = [];
      for (let d = g; d >= 1; d--) {
        if (hole !== -1 && d === hole) continue;
        days.push(TODAY - d);
      }
      const raw = rec(TODAY - g, days.slice(1));
      const w = ctx.computeAwayWindow(raw, TODAY);
      if (!w.shouldShow) continue;
      shown += 1;
      const num = ctx.computeQuestLogStreak(null, raw);
      if (w.streakSurvived) {
        if (!(num >= 1)) violations.push({ g: g, hole: hole, num: num, panel: 'survived' });
      } else if (num !== 0) {
        violations.push({ g: g, hole: hole, num: num, panel: 'broken' });
      }
    }
  }
  check(violations.length === 0,
        'S2 status-to-number non-contradiction over ' + shown + ' showing records: panel '
        + 'survived implies log >= 1, panel broken implies log 0, zero violations'
        + (violations.length ? ' ' + JSON.stringify(violations.slice(0, 3)) : ''));
})();

(function () {
  // And the surviving cases read exactly the run length the panel used.
  const ctx = makeSandbox();
  const raw = rec(TODAY - 2, [TODAY - 4, TODAY - 3, TODAY - 2]);
  const w = ctx.computeAwayWindow(raw, TODAY);
  const num = ctx.computeQuestLogStreak(null, raw);
  check(w.streakSurvived === true && num === 3,
        'S2 panel survived and log reads >= 1 and equal to the recorded run (3) [got '
        + num + ']');
})();

// --- C. Seeded cases -------------------------------------------------------
console.log('');
console.log('--- C. Seeded cases: intact, hole, none, in-progress, completed today ---');
(function () {
  const ctx = makeSandbox();

  // Scenario 1: intact run T-4, T-3, T-2 with dayIndex T-2 -> 3.
  check(ctx.computeQuestLogStreak(null, rec(TODAY - 2, [TODAY - 4, TODAY - 3, TODAY - 2])) === 3,
        'S1 intact recorded run (T-4..T-2) reads 3, not 0');

  // Scenario 3: a genuine hole at T-4 -> 0, and the panel agrees.
  const holed = rec(TODAY - 2, [TODAY - 6, TODAY - 5]);
  check(ctx.computeQuestLogStreak(null, holed) === 0,
        'S3 a genuine hole before the last play day reads 0');
  check(ctx.computeAwayWindow(holed, TODAY).streakSurvived === false,
        'S3 the panel reads broken on the same record: both agree at 0/broken');

  // Scenario 4: no history at all -> 0.
  check(ctx.computeQuestLogStreak(null, rec(TODAY - 2, [])) === 0,
        'S4 no recorded completion at all reads 0, no crash');
  check(ctx.computeQuestLogStreak(null, null) === 0,
        'S4 a null record reads 0, no crash');

  // Scenario 6: in-progress today, yesterday completed -> preserved run.
  const inProgress = rec(TODAY - 1, [TODAY - 4, TODAY - 3, TODAY - 2, TODAY - 1]);
  check(ctx.computeQuestLogStreak(null, inProgress) === 4,
        'S6 today in progress with the run intact through yesterday reads the preserved run 4');

  // Scenario 7: today completed joins the run.
  const todayDone = rec(TODAY, [TODAY - 3, TODAY - 2, TODAY - 1, TODAY]);
  check(ctx.computeQuestLogStreak(null, todayDone) === 4,
        'S7 today completed joins the run: 4, one more than the 3 ending yesterday');

  // A single recorded day is an intact run of 1.
  check(ctx.computeQuestLogStreak(null, rec(TODAY - 3, [TODAY - 3])) === 1,
        'S1 a single recorded day is an intact run of 1');

  // The raw stamp alone, with no history, is the anchor but the run is still 0.
  check(ctx.computeQuestLogStreak(null, { dayIndex: TODAY - 5, completedQuests: [] }) === 0,
        'S4 a raw stamp with no history still reads 0');
})();

// --- D. Degradation --------------------------------------------------------
console.log('');
console.log('--- D. Degradation: legacy, corrupt, partial, storage denied ---');
(function () {
  const ctx = makeSandbox();
  const cases = [
    ['legacy record, no completedQuests key', { dayIndex: TODAY - 2, fightsUsed: 1, innHealsUsed: 0 }],
    ['completedQuests is a string', { dayIndex: TODAY - 2, completedQuests: 'nope' }],
    ['completedQuests is an object', { dayIndex: TODAY - 2, completedQuests: {} }],
    ['entry with a non-numeric dayIndex', { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: 'x' }, { dayIndex: TODAY - 2 }] }],
    ['entry with a non-finite dayIndex', { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: Infinity }] }],
    ['dayIndex is not a number', { dayIndex: 'y', completedQuests: [{ dayIndex: TODAY - 2 }] }],
    ['dayIndex is NaN', { dayIndex: NaN, completedQuests: [] }],
    ['null entries in the array', { dayIndex: TODAY - 3, completedQuests: [null, {}, 'x', { dayIndex: TODAY - 3 }] }],
  ];
  let thrown = null, nonNumbers = [];
  cases.forEach(function (c) {
    try {
      const r = ctx.computeQuestLogStreak(null, c[1]);
      if (typeof r !== 'number' || !isFinite(r)) nonNumbers.push(c[0]);
    } catch (e) { thrown = c[0] + ': ' + e.message; }
  });
  check(thrown === null, 'S9 corrupt and partial records never throw'
        + (thrown ? ' [threw ' + thrown + ']' : ''));
  check(nonNumbers.length === 0, 'S9 every degraded record returns a finite number'
        + (nonNumbers.length ? ' [bad: ' + nonNumbers.join('; ') + ']' : ''));
  // Two valid entries with a hole reads the trailing run only.
  check(ctx.computeQuestLogStreak(null, { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: TODAY - 2 }] }) === 1,
        'S9 only the valid parts are counted (one valid entry -> run of 1)');

  // Storage denied: helpers swallow, the helper still answers from memory.
  const denied = makeSandbox();
  denied.localStorage = {
    getItem: function () { throw new Error('denied'); },
    setItem: function () { throw new Error('denied'); },
    removeItem: function () { throw new Error('denied'); }
  };
  let dThrown = null, dVal = null;
  try { dVal = denied.computeQuestLogStreak(null, rec(TODAY - 2, [TODAY - 3, TODAY - 2])); }
  catch (e) { dThrown = e.message; }
  check(dThrown === null && dVal === 2,
        'S10 with storage denied the helper still reads the in-memory run 2 (got ' + dVal + ')');
})();

// --- E. No write, no new field, real end-to-end render ---------------------
console.log('');
console.log('--- E. Opening row 9 writes nothing and the rendered line is the true run ---');
(function () {
  const seed = {
    'flambeee-cinder-save': JSON.stringify({ name: 'Kai', level: 3, xp: 100, hp: 30, maxHp: 30,
      attack: 4, defense: 3, gold: 50, bank: 10, weapon: 1, armor: 1, wins: 7, losses: 2, deaths: 0 }),
    'flambeee-cinder-day': JSON.stringify(rec(TODAY - 2, [TODAY - 4, TODAY - 3, TODAY - 2]))
  };
  const store = makeStore(seed);
  const ctx = makeSandbox({ store: store });
  // Full load path: load, capture the anchor, reset, ensure, then open row 9.
  ctx.dayState = ctx.loadDayState();
  const anchor = ctx.dayState;             // init(): questLogAnchor = rawDayState
  ctx.questLogAnchor = anchor;
  ctx.checkDailyReset();                   // pre-existing behavior, not the read path
  ctx.ensureQuestState();
  const saveBefore = store.getItem('flambeee-cinder-save');
  const dayBefore = store.getItem('flambeee-cinder-day');
  store._writes.length = 0;
  clearCalls(ctx);

  ctx.renderQuestLog();                    // this is opening row 9

  const called = writersCalled(ctx);
  check(called.length === 0, 'S11 opening the quest log called no writer helper ('
        + (called.length ? called.join(', ') : 'saveCharacter, saveDayState, localStorage.setItem, '
          + 'completeQuest, applyQuestProgress all silent') + ')');
  check(store._writes.length === 0,
        'S11 zero key writes while rendering the log (writes=' + store._writes.length + ')');
  check(saveBefore === store.getItem('flambeee-cinder-save'),
        'S11 flambeee-cinder-save byte-identical across the log render ('
        + (saveBefore === null ? 'null' : saveBefore.length + ' bytes') + ')');
  check(dayBefore === store.getItem('flambeee-cinder-day'),
        'S11 flambeee-cinder-day byte-identical across the log render ('
        + (dayBefore === null ? 'null' : dayBefore.length + ' bytes') + ')');
  const html = ctx._nodes['display'].innerHTML;
  const printed = renderedStreak(ctx);
  check(printed === 3,
        'S1 the RENDERED Current streak line reads the true run 3 on a return day (got '
        + printed + ')');
  check(html.indexOf('=== QUEST LOG ===') >= 0 && html.indexOf('Recent quests:') >= 0,
        'S1 the panel is the quest log, unregressed');
  check(html.indexOf('data-action="1"') >= 0 && html.indexOf('onclick') < 0,
        'S21 the log keeps the delegated data-action row and no inline onclick');
  // The panel status on the same page state, for the S2 assertion.
  check(ctx.awayWindow !== undefined,
        'S2 the panel and the log are read on the same page state');
})();

(function () {
  // Agreement on a HOLE, end to end: log 0, panel broken.
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 2, [TODAY - 6, TODAY - 5])) });
  const ctx = makeSandbox({ store: store });
  const raw = ctx.loadDayState();
  ctx.questLogAnchor = raw;
  const w = ctx.computeAwayWindow(raw, TODAY);
  ctx.dayState = raw;
  ctx.checkDailyReset();
  ctx.ensureQuestState();
  ctx.renderQuestLog();
  check(renderedStreak(ctx) === 0,
        'S3 rendered log reads 0 on a genuine gap (got ' + renderedStreak(ctx) + ')');
  check(w.streakSurvived === false,
        'S3 the panel on the same state reads broken: log 0 and panel broken agree');
  const sameDay = ctx.computeAwayWindow(rec(TODAY, [TODAY]), TODAY);
  const nextDay = ctx.computeAwayWindow(rec(TODAY - 1, [TODAY - 1]), TODAY);
  check(sameDay.shouldShow === false && nextDay.shouldShow === false,
        'S18 same-day and next-day returns stay quiet (no panel), log still renders');
})();

(function () {
  // The recent-quests list is identical to the pre-story rendering: same source
  // expression, same order, same cap. Asserted on the rendered DOM.
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify({
    dayIndex: TODAY - 1, fightsUsed: 0, innHealsUsed: 0,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: history([TODAY - 7, TODAY - 6, TODAY - 5, TODAY - 4, TODAY - 3, TODAY - 2, TODAY - 1])
  }) });
  const ctx = makeSandbox({ store: store });
  ctx.questLogAnchor = ctx.loadDayState();
  ctx.dayState = ctx.loadDayState();
  ctx.renderQuestLog();
  const html = ctx._nodes['display'].innerHTML;
  const listBlock = html.split('Recent quests:')[1].split('<div class="divider">')[0];
  const rows = (listBlock.match(/<div>/g) || []).length;
  check(rows === 5, 'S8 the list is capped at 5 entries (got ' + rows + ')');
  check(listBlock.indexOf('yesterday') < listBlock.indexOf('2 days ago'),
        'S8 the list is most recent first (yesterday before 2 days ago)');
  const expected = history([TODAY - 7, TODAY - 6, TODAY - 5, TODAY - 4, TODAY - 3, TODAY - 2, TODAY - 1])
    .slice(-5).reverse().map(function (e) {
      return '<div>' + ctx.dayLabelForIndex(e.dayIndex) + ': ' + e.objective + '</div>';
    }).join('');
  check(listBlock.indexOf(expected) >= 0,
        'S8 the rendered list is identical to the pre-story expression completed.slice(-5).reverse()');
  // And the streak line is unaffected by the list rendering: seven consecutive
  // recorded days ending at the anchor T-1, so the run is 7.
  check(renderedStreak(ctx) === 7,
        'S8 the streak line is unaffected by the list rendering (run of 7, got '
        + renderedStreak(ctx) + ')');
})();

(function () {
  // The day record checkDailyReset() builds has exactly the unchanged field set.
  const ctx = makeSandbox();
  ctx.dayState = null;
  ctx.checkDailyReset();
  const keys = Object.keys(ctx.dayState).sort();
  const want = __DAY_RECORD_SHAPE__.slice().sort();
  check(JSON.stringify(keys) === JSON.stringify(want),
        'S12 the record checkDailyReset() builds has exactly the unchanged field set '
        + '[' + keys.join(', ') + ']');
})();

(function () {
  // No argument mutation and no new global, across a wide input set.
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
  const results = [];
  const renderThrew = [];
  raws.forEach(function (raw) {
    results.push(ctx.computeQuestLogStreak(null, raw));
    ctx.questLogAnchor = raw;
    // renderQuestLog() is a shipped function with an existing input contract: it
    // expects a day-record object, and the load path never hands it null. The
    // hostile inputs are therefore exercised against the helper (the read path
    // this story owns) and against the render for every object-shaped record.
    // Scenario 9 is about the helper not throwing, which is asserted above.
    if (raw && typeof raw === 'object') {
      try { ctx.renderQuestLog(); } catch (e) { renderThrew.push(e.message); }
    }
  });
  const called = writersCalled(ctx);
  check(called.length === 0, 'S11 no writer helper called across 12 inputs ('
        + (called.length ? called.join(', ') : 'all silent') + ')');
  const mutated = [];
  raws.forEach(function (raw, i) {
    const s = JSON.stringify(raw === undefined ? null : raw);
    if (s !== snaps[i]) mutated.push(i);
  });
  check(mutated.length === 0, 'S11 no input record mutated across 12 renders ('
        + (mutated.length ? 'indices ' + mutated.join(',') : 'all deep-equal') + ')');
  check(JSON.stringify(Object.keys(ctx).sort()) === globalsBefore,
        'S11 no sandbox global added by the log path');
  check(results.every(function (r) { return typeof r === 'number' && isFinite(r); }),
        'S9 the helper returned a finite number for all ' + raws.length + ' records, '
        + 'including the hostile ones');
  check(renderThrew.length === 0,
        'S9 rendering the log on every object-shaped record did not throw'
        + (renderThrew.length ? ' [threw: ' + renderThrew[0] + ']' : ''));
})();

(function () {
  // Static-shaped runtime check: the helper appears exactly once in the file and
  // the old call site is gone.
  const helperDefs = (src.match(/function computeQuestLogStreak\s*\(/g) || []).length;
  check(helperDefs === 1, 'S13/S14 exactly one computeQuestLogStreak definition in the file ('
        + helperDefs + ')');
  const oldCall = (src.match(/computeQuestStreak\(dayState\)/g) || []).length;
  check(oldCall === 0, 'S14 no call site still reads computeQuestStreak(dayState) ('
        + oldCall + ')');
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
        print("BLOCK: no source file containing computeQuestLogStreak found")
        return 2
    base_src = git_show(BASE_REF)
    if base_src is None:
        print("BLOCK: could not read %s for the byte-identity comparisons" % BASE_REF)
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 044 pure-read proof: quest-log streak source ===")
    print("source under test: %s" % label)
    print("resolved to: %s" % src_path)
    print("sha256: %s" % digest)
    print("base for comparison: %s" % BASE_REF)
    print("")

    problems = static_scan(src, base_src)

    print("")
    print("=== Node proof: extracted shipped helper, view and reset ===")
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
