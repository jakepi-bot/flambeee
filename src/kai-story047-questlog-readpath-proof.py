#!/usr/bin/env python3
"""Kai read-path proof for Story 047 (Cinder quest log, recent-quests list).

Story 044 fixed the quest log's STREAK NUMBER to read the player's recorded
history through the pre-reset anchor (questLogAnchor). It left the
RECENT-QUESTS LIST explicitly untouched. The list and the number are two
separate expressions over the day record:

  - the number: computeQuestLogStreak(dayState, questLogAnchor), reads the
    PRE-reset anchor (src/cinder.html:629);
  - the list:   dayState.completedQuests.slice(-5).reverse(), reads the
    POST-reset dayState (src/cinder.html:627-637).

On the first load of a gap day, checkDailyReset() (src/cinder.html:727-737) has
already rebuilt dayState wholesale with completedQuests: []. If the two
expressions do not describe the same record, the same screen prints a nonzero
streak beside an empty list: the same read-path contradiction Story 044 removed
for the number, now hunted for the list.

This script proves the SHIPPED code. It does not re-implement it: every function
under test is extracted verbatim out of src/cinder.html into a node vm sandbox,
and the render is driven through the real renderQuestLog().

It reports what the shipped build actually does, seeded in flambeee-cinder-day:

  1. first run / no record (no completedQuests)
  2. stale by exactly 1 day (dayIndex = T-1 with recorded completions)
  3. stale by 3 days
  4. stale by 6 days
  5. stale by 30 days
  6. same-day reload (record stamped today, load, reload)

For each it prints the rendered recent-quests list (entries + labels) and the
rendered streak number, and asserts consistency (nonzero streak implies a
non-empty list from the same run; empty list implies streak 0 or the documented
first-run empty state).

The reset hazard is proven DIRECTLY: the list is rendered from the loaded
record's history, then from the record after the real checkDailyReset() has
rebuilt it (completedQuests: []), and the two renders are compared. The
first-load vs reload difference is confirmed by RUNNING, not reasoning.

No-write / no-new-field: a static scan of the list+streak read path for
saveCharacter, saveDayState, localStorage.setItem, completeQuest,
applyQuestProgress and state-mutating character./dayState. writes, plus a
runtime check that flambeee-cinder-save and flambeee-cinder-day are
byte-identical before and after opening the log with a well-formed record
stamped today.

Frozen functions: checkDailyReset() and computeQuestStreak() are compared
byte-for-byte against v0.22.0:src/cinder.html (extract-and-compare by
paren/brace matching, sha256 of the verbatim slice).

Day-record shape: the record checkDailyReset() builds has exactly
{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }.

Source under test: argv[1], then $CINDER_SRC, then ./cinder.html next to this
script. The resolved path and its sha256 are printed so the run is reproducible.
v0.22.0:src/cinder.html is read through git show for the byte-identity checks.

Run:
  /home/jake/.openclaw/workspace/.venv/bin/python3 src/kai-story047-questlog-readpath-proof.py
  /home/jake/.openclaw/workspace/.venv/bin/python3 src/kai-story047-questlog-readpath-proof.py /path/to/cinder.html
Exit code 0 = the proof ran and every assertion held. Non-zero = proof failed.
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
BASE_REF = "v0.22.0:src/cinder.html"

# The quest-log read path this story owns: the list expression + its labels, and
# the streak source the number reads.
PATH_FNS = ["renderQuestLog", "computeQuestLogStreak", "computeRecentQuestEntries", "dayLabelForIndex"]
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
    "questLogList",
    "recentQuestsCache",
    "listAnchor",
    "questLogHistory",
    "readPathVersion",
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
            if "function renderQuestLog(" in txt and "function computeQuestLogStreak(" in txt:
                return c, txt, c
    for ref in ("feature/047-049-cinder-read-path-kai:src/cinder.html",
                "main:src/cinder.html"):
        txt = git_show(ref)
        if txt and "function renderQuestLog(" in txt:
            fd, tmp = tempfile.mkstemp(suffix="-cinder.html", prefix="story047-")
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

    # The list expression this story audits, exactly as shipped.
    try:
        log = strip_comments(body_of(src, "renderQuestLog"))
    except RuntimeError as e:
        problems.append(str(e))
        log = ""
    if "completed.slice(-5).reverse()" not in log:
        problems.append("renderQuestLog does not cap/order the list with completed.slice(-5).reverse()")
    else:
        print("  renderQuestLog list expression: completed.slice(-5).reverse() (cap 5, most recent first)")

    # The list source must read the pre-reset anchor, not the post-reset record.
    if "computeRecentQuestEntries(questLogAnchor, dayState)" not in log:
        problems.append("renderQuestLog does not source the list from "
                        "computeRecentQuestEntries(questLogAnchor, dayState)")
    else:
        print("  renderQuestLog sources the list from the pre-reset anchor "
              "computeRecentQuestEntries(questLogAnchor, dayState)")
    if "dayState.completedQuests" in log:
        problems.append("renderQuestLog still reads post-reset dayState.completedQuests directly")
    else:
        print("  renderQuestLog no longer reads post-reset dayState.completedQuests directly")

    try:
        helper = strip_comments(body_of(src, "computeRecentQuestEntries"))
    except RuntimeError as e:
        problems.append(str(e))
        helper = ""
    if helper and "anchor.completedQuests" not in helper:
        problems.append("computeRecentQuestEntries does not read the anchor history")
    if helper and "return []" not in helper:
        problems.append("computeRecentQuestEntries has no empty-array fallback")

    defs = len(re.findall(r"function renderQuestLog\s*\(", code))
    if defs != 1:
        problems.append("expected exactly 1 renderQuestLog definition, found %d" % defs)

    # Structural regressions: byte-identity of the two frozen functions.
    print("")
    print("=== Static scan: frozen functions byte-identical to v0.22.0 ===")
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
        gh = hashlib.sha256(got.encode("utf-8")).hexdigest()
        bh = hashlib.sha256(want.encode("utf-8")).hexdigest()
        if gh == bh:
            print("  function %-20s byte-identical to v0.22.0 (%s)" % (fn + "()", bh[:12]))
        else:
            problems.append("%s CHANGED vs v0.22.0 (%s vs %s)" % (fn, gh[:12], bh[:12]))
            print("  BLOCK: %s changed (sha %s vs v0.22.0 %s)" % (fn, gh[:12], bh[:12]))

    # The day-record shape built by the reset.
    print("")
    print("=== Static scan: day-record shape built by checkDailyReset() ===")
    if base_src:
        try:
            want = strip_comments(body_of(base_src, "checkDailyReset"))
        except RuntimeError:
            want = ""
        if want and want == strip_comments(body_of(src, "checkDailyReset")):
            print("  checkDailyReset() builds the same record shape as v0.22.0")
    shape_hits = [k for k in DAY_RECORD_SHAPE if k in code]
    if len(shape_hits) < len(DAY_RECORD_SHAPE):
        problems.append("day-record shape key missing from source: %s"
                        % ", ".join(set(DAY_RECORD_SHAPE) - set(shape_hits)))

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
const TODAY = Math.floor(Date.UTC(2026, 9, 27, 12) / 86400000);

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

// A real in-memory localStorage so byte-identity is measured, not assumed.
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
    renderTownMenu: [], clearLog: []
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
  ['escapeHtml', 'computeQuestStreak', 'computeQuestLogStreak', 'computeRecentQuestEntries',
   'computeAwayWindow', 'shouldShowWelcomeBack', 'dayLabelForIndex', 'renderQuestLog',
   'checkDailyReset', 'ensureQuestState'].forEach(function (n) {
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
function history(days) {
  return days.map(function (d, i) {
    return { dayIndex: d, label: 'quest' + i, objective: 'Objective ' + i };
  });
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
// The recent-quests list as renderQuestLog() prints it: the entries between the
// "Recent quests:" label and the following divider, each "<div>label: title</div>".
function renderedList(ctx) {
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  if (html.indexOf('Recent quests:') < 0) return null;
  const block = html.split('Recent quests:')[1].split('<div class="divider">')[0];
  const rows = [];
  const re = /<div>([^<]*)<\/div>/g;
  let m;
  while ((m = re.exec(block)) !== null) rows.push(m[1]);
  return rows;   // [] when the empty-state line is a .muted div and no plain rows exist
}
function listIsEmptyState(ctx) {
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  return html.indexOf('No quests recorded yet.') >= 0;
}

// Drive the REAL load path: load the day record, capture the pre-reset anchor
// exactly as init() does, run the shipped checkDailyReset() and
// ensureQuestState(), then open the log. Returns the sandbox and the anchor.
function loadAndOpen(store, opts) {
  opts = opts || {};
  const ctx = makeSandbox({ store: store });
  ctx.dayState = ctx.loadDayState();
  const anchor = ctx.dayState;              // init(): questLogAnchor = rawDayState
  ctx.questLogAnchor = anchor;
  ctx.checkDailyReset();                     // pre-existing load behavior
  ctx.ensureQuestState();
  if (opts.skipRender !== true) ctx.renderQuestLog();
  return { ctx: ctx, anchor: anchor };
}

console.log('=== Story 047 read-path proof (extracted from shipped file) ===');
console.log('today index (deterministic): ' + TODAY);

// Every seeded state is described in one table so the run prints the list and
// the number for each, side by side, and asserts consistency.
const STATES = [
  { key: 'S1 first run, no record',        rec: null,                                                 expect: 'empty-state + 0' },
  { key: 'S2 stale by exactly 1 day',      rec: rec(TODAY - 1, [TODAY - 1]),                          expect: 'list + 1' },
  { key: 'S3 stale by 3 days',             rec: rec(TODAY - 3, [TODAY - 3, TODAY - 4, TODAY - 5]),    expect: 'list + 3' },
  { key: 'S4 stale by 6 days',             rec: rec(TODAY - 6, [TODAY - 6, TODAY - 7]),               expect: 'list + 2' },
  { key: 'S5 stale by 30 days',            rec: rec(TODAY - 30, [TODAY - 30]),                        expect: 'list + 1' }
];

console.log('');
console.log('--- Section 1: the five seeded states, first load (list + number together) ---');
STATES.forEach(function (st) {
  const seed = {};
  if (st.rec) seed['flambeee-cinder-day'] = JSON.stringify(st.rec);
  const store = makeStore(seed);
  const r = loadAndOpen(store);
  const list = renderedList(r.ctx);
  const empty = listIsEmptyState(r.ctx);
  const streak = renderedStreak(r.ctx);
  console.log('');
  console.log('  [' + st.key + ']  expect: ' + st.expect);
  console.log('    rendered streak number: ' + streak);
  if (empty) {
    console.log('    rendered list: <empty-state> "No quests recorded yet. Finish today\'s quest to start your log."');
  } else {
    console.log('    rendered list (' + (list ? list.length : 0) + ' entries, most recent first):');
    (list || []).forEach(function (row) { console.log('      - ' + row); });
  }
  // Consistency: nonzero streak implies a non-empty list from the same run;
  // an empty list implies streak 0 or the documented first-run empty state.
  if (streak !== null && streak > 0) {
    check(!empty && list && list.length > 0,
          st.key + ': nonzero streak (' + streak + ') implies a non-empty list '
          + '(empty-state=' + empty + ', rows=' + (list ? list.length : 0) + ')');
  } else {
    check(empty || (list && list.length === 0),
          st.key + ': streak 0 implies the empty-state list (empty-state=' + empty + ')');
  }
});

console.log('');
console.log('--- Section 2: same-day reload (control) ---');
(function () {
  const seed = { 'flambeee-cinder-day': JSON.stringify(rec(TODAY, [TODAY, TODAY - 1, TODAY - 2])) };
  const store = makeStore(seed);
  // First load of a record already stamped today.
  const first = loadAndOpen(store);
  const firstList = renderedList(first.ctx);
  const firstStreak = renderedStreak(first.ctx);
  console.log('  first load  streak=' + firstStreak + '  list=' + JSON.stringify(firstList));
  // Reload: re-read the (unchanged) stored record and open again.
  const ctx2 = makeSandbox({ store: store });
  ctx2.dayState = ctx2.loadDayState();
  ctx2.questLogAnchor = ctx2.dayState;
  ctx2.checkDailyReset();
  ctx2.ensureQuestState();
  ctx2.renderQuestLog();
  const secondList = renderedList(ctx2);
  const secondStreak = renderedStreak(ctx2);
  console.log('  reload      streak=' + secondStreak + '  list=' + JSON.stringify(secondList));
  check(firstStreak === secondStreak,
        'S6 reload streak matches the first load (' + firstStreak + ' then ' + secondStreak + ')');
  check(JSON.stringify(firstList) === JSON.stringify(secondList),
        'S6 reload list matches the first load for the same recorded history');
  check(firstStreak === 3,
        'S6 same-day record stamped today with a 3-day run reads 3 (got ' + firstStreak + ')');
})();

console.log('');
console.log('--- Section 3: the reset hazard, proven directly ---');
(function () {
  // Render the list from the LOADED record's history, then from the record
  // after the real checkDailyReset() has rebuilt it. Report what ships.
  const raw = rec(TODAY - 3, [TODAY - 3, TODAY - 4, TODAY - 5]);
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(raw) });
  const ctx = makeSandbox({ store: store });
  ctx.dayState = ctx.loadDayState();
  const anchor = ctx.dayState;

  // (a) list rendered from the LOADED (pre-reset) record's history.
  ctx.questLogAnchor = anchor;
  const loadedList = (Array.isArray(anchor.completedQuests) ? anchor.completedQuests : [])
    .slice(-5).reverse().map(function (e) {
      return ctx.dayLabelForIndex(e.dayIndex) + ': ' + (e.objective || e.label || '');
    });
  console.log('  (a) list from the LOADED record history: ' + JSON.stringify(loadedList));

  // Run the real reset; it replaces dayState wholesale.
  ctx.checkDailyReset();
  console.log('  after checkDailyReset(): dayIndex=' + ctx.dayState.dayIndex
              + '  completedQuests.length=' + ctx.dayState.completedQuests.length);
  check(ctx.dayState.completedQuests.length === 0,
        'S7 the real checkDailyReset() rebuilt the record with completedQuests [] on a gap day');

  // (b) list rendered from the record AFTER the reset, via the SHIPPED render.
  ctx.renderQuestLog();
  const postList = renderedList(ctx);
  const postEmpty = listIsEmptyState(ctx);
  const postStreak = renderedStreak(ctx);
  console.log('  (b) list from the SHIPPED render AFTER the reset: '
              + (postEmpty ? '<empty-state>' : JSON.stringify(postList)));
  console.log('      streak number on that same render: ' + postStreak);

  // What the shipped build actually does, reported without spin.
  const contradicted = postStreak > 0 && postEmpty;
  console.log('  OBSERVED: shipped first-load render on a stale-by-3-day record -> '
              + 'streak=' + postStreak + ', list ' + (postEmpty ? 'EMPTY' : 'non-empty'));
  check(!contradicted,
        'S7/S3 shipped first load does NOT print a nonzero streak (' + postStreak
        + ') beside an empty list (this is the defect hunted)');
})();

console.log('');
console.log('--- Section 4: no write on the read path, byte-identical stores ---');
(function () {
  const save = { name: 'Kai', level: 3, xp: 100, hp: 30, maxHp: 30, attack: 4,
                 defense: 3, gold: 50, bank: 10, weapon: 1, armor: 1, wins: 7, losses: 2, deaths: 0 };
  const seed = {
    'flambeee-cinder-save': JSON.stringify(save),
    'flambeee-cinder-day': JSON.stringify(rec(TODAY, [TODAY, TODAY - 1]))
  };
  const store = makeStore(seed);
  const ctx = makeSandbox({ store: store });
  ctx.dayState = ctx.loadDayState();
  ctx.questLogAnchor = ctx.dayState;
  ctx.checkDailyReset();
  ctx.ensureQuestState();
  const saveBefore = store.getItem('flambeee-cinder-save');
  const dayBefore = store.getItem('flambeee-cinder-day');
  store._writes.length = 0;
  clearCalls(ctx);

  ctx.renderQuestLog();   // opening row 9

  const called = writersCalled(ctx);
  check(called.length === 0,
        'S10 opening the log called no writer helper ('
        + (called.length ? called.join(', ')
           : 'saveCharacter, saveDayState, localStorage.setItem, completeQuest, '
             + 'applyQuestProgress all silent') + ')');
  check(store._writes.length === 0,
        'S10 zero key writes while rendering the log (writes=' + store._writes.length + ')');
  check(saveBefore === store.getItem('flambeee-cinder-save'),
        'S10 flambeee-cinder-save byte-identical across the log render ('
        + (saveBefore === null ? 'null' : saveBefore.length + ' bytes') + ')');
  check(dayBefore === store.getItem('flambeee-cinder-day'),
        'S10 flambeee-cinder-day byte-identical across the log render ('
        + (dayBefore === null ? 'null' : dayBefore.length + ' bytes') + ')');
  console.log('  save before/after identical: ' + (saveBefore === store.getItem('flambeee-cinder-save')));
  console.log('  day  before/after identical: ' + (dayBefore === store.getItem('flambeee-cinder-day')));
})();

console.log('');
console.log('--- Section 5: day-record shape unchanged, degradation, no argument mutation ---');
(function () {
  const ctx = makeSandbox();
  ctx.dayState = null;
  ctx.checkDailyReset();
  const keys = Object.keys(ctx.dayState).sort();
  const want = __DAY_RECORD_SHAPE__.slice().sort();
  check(JSON.stringify(keys) === JSON.stringify(want),
        'S11 the record checkDailyReset() builds has exactly the unchanged field set ['
        + keys.join(', ') + ']');
})();

(function () {
  // Degradation: the render must not throw on legacy, corrupt, partial records,
  // and the helper must return a finite number.
  const ctx = makeSandbox();
  const cases = [
    ['legacy record, no completedQuests key', { dayIndex: TODAY - 2, fightsUsed: 1, innHealsUsed: 0 }],
    ['completedQuests is a string', { dayIndex: TODAY - 2, completedQuests: 'nope' }],
    ['completedQuests is an object', { dayIndex: TODAY - 2, completedQuests: {} }],
    ['entry with a non-numeric dayIndex', { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: 'x' }, { dayIndex: TODAY - 2 }] }],
    ['entry with a non-finite dayIndex', { dayIndex: TODAY - 2, completedQuests: [{ dayIndex: Infinity }] }],
    ['null entries in the array', { dayIndex: TODAY - 3, completedQuests: [null, {}, 'x', { dayIndex: TODAY - 3 }] }],
  ];
  let thrown = null, bad = [];
  cases.forEach(function (c) {
    try {
      const r = ctx.computeQuestLogStreak(null, c[1]);
      if (typeof r !== 'number' || !isFinite(r)) bad.push(c[0]);
      ctx.questLogAnchor = c[1];
      ctx.dayState = c[1];
      ctx.renderQuestLog();
    } catch (e) { thrown = c[0] + ': ' + e.message; }
  });
  check(thrown === null, 'S14 legacy/corrupt records never throw in the read path'
        + (thrown ? ' [threw ' + thrown + ']' : ''));
  check(bad.length === 0, 'S14 every degraded record yields a finite number'
        + (bad.length ? ' [bad: ' + bad.join('; ') + ']' : ''));
})();

(function () {
  // No argument mutation and no new global across a wide input set.
  const ctx = makeSandbox();
  const raws = [
    rec(TODAY, [TODAY]), rec(TODAY - 1, []), rec(TODAY - 2, []),
    rec(TODAY - 4, [TODAY - 3]), rec(TODAY - 40, []), rec(TODAY - 30, [TODAY - 2]),
    { dayIndex: 'x' }, { dayIndex: TODAY - 5, completedQuests: 'nope' },
    { dayIndex: TODAY - 3, completedQuests: [null, {}, 'x'] }
  ];
  const snaps = raws.map(function (r) { return JSON.stringify(r); });
  const globalsBefore = JSON.stringify(Object.keys(ctx).sort());
  clearCalls(ctx);
  const renderThrew = [];
  raws.forEach(function (raw) {
    ctx.questLogAnchor = raw;
    ctx.dayState = raw;
    try { ctx.renderQuestLog(); } catch (e) { renderThrew.push(e.message); }
  });
  const called = writersCalled(ctx);
  check(called.length === 0, 'S10 no writer helper called across ' + raws.length + ' renders ('
        + (called.length ? called.join(', ') : 'all silent') + ')');
  const mutated = [];
  raws.forEach(function (raw, i) {
    if (JSON.stringify(raw) !== snaps[i]) mutated.push(i);
  });
  check(mutated.length === 0, 'S10 no input record mutated across ' + raws.length + ' renders ('
        + (mutated.length ? 'indices ' + mutated.join(',') : 'all deep-equal') + ')');
  check(JSON.stringify(Object.keys(ctx).sort()) === globalsBefore,
        'S10 no sandbox global added by the log path');
  check(renderThrew.length === 0, 'S14 rendering on every object-shaped record did not throw'
        + (renderThrew.length ? ' [threw: ' + renderThrew[0] + ']' : ''));
})();

console.log('');
console.log('--- Section 6: list contract unchanged (order, cap 5, labels, empty state) ---');
(function () {
  const seven = [TODAY - 7, TODAY - 6, TODAY - 5, TODAY - 4, TODAY - 3, TODAY - 2, TODAY - 1];
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(rec(TODAY - 1, seven)) });
  const ctx = makeSandbox({ store: store });
  ctx.questLogAnchor = ctx.loadDayState();
  ctx.dayState = ctx.loadDayState();
  ctx.renderQuestLog();
  const list = renderedList(ctx);
  check(list.length === 5, 'S13 the list is capped at 5 entries (got ' + list.length + ')');
  check(list[0].indexOf('yesterday') === 0, 'S13 most recent first: first row is "yesterday" (got "' + list[0] + '")');
  const expected = history(seven).slice(-5).reverse().map(function (e) {
    return ctx.dayLabelForIndex(e.dayIndex) + ': ' + e.objective;
  });
  check(JSON.stringify(list) === JSON.stringify(expected),
        'S13 the rendered list equals the shipped expression completed.slice(-5).reverse() with dayLabelForIndex labels');
  console.log('  rendered 5 rows:');
  list.forEach(function (row) { console.log('    - ' + row); });
})();

console.log('');
console.log('--- Section 7: no inline onclick, delegated data-action intact ---');
(function () {
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(rec(TODAY, [TODAY])) });
  const ctx = makeSandbox({ store: store });
  ctx.questLogAnchor = ctx.loadDayState();
  ctx.dayState = ctx.loadDayState();
  ctx.checkDailyReset();
  ctx.renderQuestLog();
  const html = ctx._nodes['display'].innerHTML;
  check(html.indexOf('=== QUEST LOG ===') >= 0, 'S22 the panel is the quest log, unregressed');
  check(html.indexOf('data-action="1"') >= 0, 'S22 the Back to Town row keeps data-action delegation');
  check(html.indexOf('onclick') < 0, 'S22 no inline onclick in the rendered log');
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
        print("BLOCK: no source file containing renderQuestLog + computeQuestLogStreak found")
        return 2
    base_src = git_show(BASE_REF)
    if base_src is None:
        print("BLOCK: could not read %s for the byte-identity comparisons" % BASE_REF)
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 047 read-path proof: recent-quests list ===")
    print("source under test: %s" % label)
    print("resolved to: %s" % src_path)
    print("sha256: %s" % digest)
    print("base for comparison: %s" % BASE_REF)
    print("")

    problems = static_scan(src, base_src)

    print("")
    print("=== Node proof: extracted shipped list, number, reset ===")
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
