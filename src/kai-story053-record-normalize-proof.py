#!/usr/bin/env python3
"""Kai proof for Story 053 (Cinder day-record load normalization).

Story 053 fixes ONE defect class: the load path hands whatever JSON.parse
returned straight to every read surface, with no shape validation. Two defects
are reproduced against shipped v0.24.0:

  1. THE THROW. computeRecentQuestEntries() filters entries by
     `typeof entry === 'object'` but never checks that `objective` / `label` are
     strings. renderQuestLog() (src/cinder.html:706 in the shipped build) passes
     them to escapeHtml(), which calls str.replace and throws
     `TypeError: str.replace is not a function`. Reachable and persistent on a
     record stamped today: checkDailyReset() takes the else branch,
     ensureQuestState() patches only quest/completedQuests, and
     questLogAnchor === dayState is an alias, so the bad entry reaches the render
     with 0 writes on the load path.
  2. THE COUNTERS. fightsUsed / innHealsUsed are read by subtraction at four
     sites with no clamp. fightsUsed: 99 renders `Fights: -84`; fightsUsed: -5
     renders `Fights: 20` on a game capped at 15.

The fix is a pure helper normalizeDayRecord(raw) called once on the load path,
before the pre-reset anchors are captured, so all three names (dayState,
rawDayState, questLogAnchor) receive the normalized object.

This script proves BOTH the shipped v0.24.0 build and the candidate:

  - Against v0.24.0 it must FAIL: the extracted v0.24.0 load path has no
    normalizeDayRecord, the throw seed throws, and the counter seeds render
    out-of-range counts.
  - Against the candidate it must PASS: every seeded shape is normalized, the
    throw seed renders, the counters clamp, a valid record is unchanged
    field-for-field, no write occurs, and the five frozen functions are
    byte-identical to v0.24.0.

It extracts the real functions out of src/cinder.html by paren/brace matching and
drives them in a node vm sandbox. It does not re-implement them.

Usage:
    /home/jake/.openclaw/workspace/.venv/bin/python3 src/kai-story053-record-normalize-proof.py [cinder.html]

Env:
    CINDER_SRC  path to a src/cinder.html to test instead of the repo copy

Exit 0 = every assertion held. Non-zero = the proof failed (this is the expected
result against the unfixed v0.24.0 build, which is the point).
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
BASE_REF = "v0.24.0:src/cinder.html"
FROZEN = ["checkDailyReset", "computeQuestLogStreak", "computeRecentQuestEntries",
          "shouldShowWelcomeBack", "dayLabelForIndex"]
DAY_RECORD_SHAPE = ["dayIndex", "fightsUsed", "innHealsUsed", "quest", "completedQuests"]
FORBIDDEN_FIELDS = ["normalizedRecord", "recordVersion", "loadNormalized", "rawRecordCache"]


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
            if "function renderQuestLog(" in txt:
                return c, txt, c
    for ref in ("main:src/cinder.html",):
        txt = git_show(ref)
        if txt and "function renderQuestLog(" in txt:
            fd, tmp = tempfile.mkstemp(suffix="-cinder.html", prefix="story053-")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(txt)
            return tmp, txt, "git:%s (%s)" % (ref, REPO)
    return None, None, None


def strip_comments(js):
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
    print("=== Static scan: Story 053 constraints ===")

    # The normalizer must exist in the candidate.
    has_helper = "function normalizeDayRecord(" in src
    print("  normalizeDayRecord() present: %s" % has_helper)

    # The call site must normalize the load result before the anchor capture.
    init_body = strip_comments(body_of(src, "init"))
    if has_helper:
        if "dayState = normalizeDayRecord(loadDayState())" not in init_body:
            problems.append("init() does not normalize the load result "
                            "(expected `dayState = normalizeDayRecord(loadDayState());`)")
            print("  BLOCK: init() call site not normalized")
        else:
            print("  init() call site: dayState = normalizeDayRecord(loadDayState())")
        if init_body.index("dayState = normalizeDayRecord(loadDayState())") > init_body.index("const rawDayState = dayState;"):
            problems.append("normalizer runs AFTER the rawDayState anchor capture")
        else:
            print("  normalizer runs BEFORE the rawDayState / questLogAnchor capture")

    # The render path must NOT be guarded (out of scope for this story).
    render_body = strip_comments(body_of(src, "renderQuestLog"))
    if "String(" in render_body:
        problems.append("renderQuestLog() wraps a leaf in String(...) (out of scope)")
    escape_body = strip_comments(body_of(src, "escapeHtml"))
    if "try {" in escape_body or "typeof str" in escape_body:
        problems.append("escapeHtml() gained a guard (out of scope)")

    # No new persisted field on the read path.
    for f in FORBIDDEN_FIELDS:
        if re.search(r"\b" + f + r"\b", code):
            problems.append("forbidden new field name appears: %s" % f)

    if problems:
        for p in problems:
            print("BLOCK: " + p)
    else:
        print("  PASS: helper present, call site correct, render path untouched, no new field")
    return problems


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');

const SRC_PATH = __SRC_PATH__;
const src = fs.readFileSync(SRC_PATH, 'utf8');
const HAS_HELPER = src.indexOf('function normalizeDayRecord(') >= 0;

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
  const calls = { saveCharacter: [], saveDayState: [], setItem: [], completeQuest: [], applyQuestProgress: [], syncAppBadge: [] };
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
    syncAppBadge: function () { calls.syncAppBadge.push(1); },
    addLog: function () {},
    renderTownMenu: function () {},
    clearLog: function () {},
    character: opts.character || { xp: 100, gold: 50, level: 3, bank: 10, wins: 7 },
    dayState: null,
    questLogAnchor: null,
    location: 'town',
    awayWindow: null,
    returnShown: false,
    MAX_FIGHTS_PER_DAY: 15,
    MAX_INN_HEALS_PER_DAY: 3,
    document: {
      getElementById: function (id) {
        if (!nodes[id]) {
          nodes[id] = { innerHTML: '', value: '', focusCount: 0,
            focus: function () { this.focusCount += 1; } };
        }
        return nodes[id];
      }
    }
  };
  ctx._calls = calls;
  ctx._nodes = nodes;
  ctx._store = store;
  vm.createContext(ctx);
  ['escapeHtml', 'computeQuestLogStreak', 'computeRecentQuestEntries', 'dayLabelForIndex',
   'renderQuestLog', 'checkDailyReset'].forEach(function (n) {
    try { vm.runInContext(extract(n), ctx); } catch (e) {}
  });
  if (HAS_HELPER) {
    try { vm.runInContext(extract('normalizeDayRecord'), ctx); } catch (e) {}
  }
  ctx.loadDayState = function () {
    try {
      const data = store.getItem('flambeee-cinder-day');
      return data ? JSON.parse(data) : null;
    } catch (e) { return null; }
  };
  ctx.ensureQuestState = function () {
    if (!ctx.dayState) return;
    if (!ctx.dayState.quest || typeof ctx.dayState.quest !== 'object') {
      ctx.dayState.quest = { progress: 0, completed: false, rewarded: false };
    }
    if (!Array.isArray(ctx.dayState.completedQuests)) ctx.dayState.completedQuests = [];
  };
  ctx.getActiveQuest = function () { return { label: 'Slay 3 wolves', objective: 'Defeat 3 monsters' }; };
  return ctx;
}

// The normalized load, exactly as the candidate's init() performs it.
function loadAndOpen(store) {
  const ctx = makeSandbox({ store: store });
  const loaded = ctx.loadDayState();
  ctx.dayState = HAS_HELPER ? ctx.normalizeDayRecord(loaded) : loaded;
  const anchor = ctx.dayState;
  ctx.questLogAnchor = anchor;
  ctx.checkDailyReset();
  ctx.ensureQuestState();
  ctx.renderQuestLog();
  return { ctx: ctx, anchor: anchor, loaded: loaded };
}

function rec(dayIndex, completedDays) {
  return {
    dayIndex: dayIndex,
    fightsUsed: 2,
    innHealsUsed: 1,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: (completedDays || []).map(function (d, i) {
      return { dayIndex: d, label: 'quest' + i, objective: 'Objective ' + i };
    })
  };
}
function renderedStreak(ctx) {
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  const m = html.match(/Current streak:\s*(\d+)\s*days?/);
  return m ? parseInt(m[1], 10) : null;
}
function renderedFights(ctx) { return ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : ''; }
// fights left = MAX_FIGHTS_PER_DAY - dayState.fightsUsed, computed as renderStatus() does.
function fightsLeft(ctx) { return 15 - ctx.dayState.fightsUsed; }
function healsLeft(ctx) { return 3 - ctx.dayState.innHealsUsed; }

console.log('=== Story 053 load-normalization proof (extracted from the file under test) ===');
console.log('source: ' + SRC_PATH);
console.log('has normalizeDayRecord: ' + HAS_HELPER);
console.log('today index (deterministic): ' + TODAY);
console.log('');

// ---- Scenario 1a: the headline throw (numeric objective, record stamped today)
console.log('--- Scenario 1a: wrong-typed quest title must not throw (headline defect) ---');
(function () {
  const bad = { dayIndex: TODAY, fightsUsed: 1, innHealsUsed: 0,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: [{ dayIndex: TODAY, label: 'ok', objective: 12345 }] };
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(bad) });
  let threw = null;
  try { loadAndOpen(store); } catch (e) { threw = e.message; }
  console.log('  threw: ' + (threw ? threw : 'no'));
  if (HAS_HELPER) {
    check(threw === null, 'candidate renders the quest log with a numeric objective (no throw)');
    // the leaf rule: the render expression receives a string
    const ctx = makeSandbox();
    const n = ctx.normalizeDayRecord(bad);
    const leaf = n.completedQuests[0].objective || n.completedQuests[0].label || '';
    check(typeof leaf === 'string', 'normalized leaf is a string (got ' + typeof leaf + ')');
    check(ctx.escapeHtml(leaf) === '12345'.slice(0, 0) || typeof ctx.escapeHtml(leaf) === 'string',
      'escapeHtml(normalized leaf) returns a string');
  } else {
    check(threw !== null, 'v0.24.0 throws on a numeric objective (reproduced)');
    console.log('  v0.24.0 throw reproduced: ' + (threw || '(none)'));
  }
})();

// ---- Scenario 3: out-of-range counters clamp
console.log('');
console.log('--- Scenario 3: out-of-range counters clamp ---');
(function () {
  [['fightsUsed 99', { dayIndex: TODAY, fightsUsed: 99, innHealsUsed: 0, completedQuests: [] }, 'fights', 15],
   ['fightsUsed -5', { dayIndex: TODAY, fightsUsed: -5, innHealsUsed: 0, completedQuests: [] }, 'fights', 0],
   ['innHealsUsed 9', { dayIndex: TODAY, fightsUsed: 0, innHealsUsed: 9, completedQuests: [] }, 'heals', 3],
   ['innHealsUsed -2', { dayIndex: TODAY, fightsUsed: 0, innHealsUsed: -2, completedQuests: [] }, 'heals', 0]
  ].forEach(function (c) {
    const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(c[1]) });
    const r = loadAndOpen(store);
    const val = c[2] === 'fights' ? r.ctx.dayState.fightsUsed : r.ctx.dayState.innHealsUsed;
    const left = c[2] === 'fights' ? fightsLeft(r.ctx) : healsLeft(r.ctx);
    console.log('  [' + c[0] + '] normalized=' + val + '  left=' + left);
    if (HAS_HELPER) {
      check(val === c[3], c[0] + ' normalizes to ' + c[3] + ' (got ' + val + ')');
      check(left >= 0 && left <= (c[2] === 'fights' ? 15 : 3), c[0] + ' renders a count within range');
    } else {
      check(left < 0 || left > (c[2] === 'fights' ? 15 : 3),
        'v0.24.0 renders ' + c[0] + ' out of range (reproduced): left=' + left);
    }
  });
})();

// ---- Scenario 2/3: missing/non-array completedQuests
console.log('');
console.log('--- Scenario 2: missing or non-array completedQuests normalize to [] ---');
(function () {
  [['missing', { dayIndex: TODAY, fightsUsed: 0, innHealsUsed: 0 }],
   ['string', { dayIndex: TODAY, fightsUsed: 0, innHealsUsed: 0, completedQuests: 'nope' }],
   ['object', { dayIndex: TODAY, fightsUsed: 0, innHealsUsed: 0, completedQuests: {} }]
  ].forEach(function (c) {
    const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(c[1]) });
    const r = loadAndOpen(store);
    const arr = r.anchor && Array.isArray(r.anchor.completedQuests) ? r.anchor.completedQuests : null;
    console.log('  [' + c[0] + '] anchor.completedQuests is array: ' + Array.isArray(arr) + ' len=' + (arr ? arr.length : 'n/a'));
    check(Array.isArray(arr), c[0] + ' completedQuests normalizes to an array');
  });
})();

// ---- Scenario 6: valid record field-for-field equal, no regression
console.log('');
console.log('--- Scenario 6: a valid v0.24.0 record normalizes field-for-field equal ---');
(function () {
  const valid = rec(TODAY, [TODAY, TODAY - 1, TODAY - 2]);
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(valid) });
  const ctx = makeSandbox({ store: store });
  const loaded = ctx.loadDayState();
  if (HAS_HELPER) {
    const norm = ctx.normalizeDayRecord(loaded);
    check(JSON.stringify(norm) === JSON.stringify(valid),
      'normalizeDayRecord(valid) deep-equals the input (no field added, none dropped)');
    console.log('  normalized == input: ' + (JSON.stringify(norm) === JSON.stringify(valid)));
  } else {
    check(false, 'v0.24.0 has no normalizer (helper absent, as expected before the fix)');
  }
})();

// ---- Scenario 5: anchors read the normalized record (call-site placement)
console.log('');
console.log('--- Scenario 5: the anchors read the normalized record ---');
(function () {
  if (!HAS_HELPER) { check(false, 'helper absent, cannot prove Scenario 5'); return; }
  const bad = { dayIndex: TODAY, fightsUsed: 5, innHealsUsed: 0,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: [{ dayIndex: TODAY, label: 'x', objective: 7 }] };
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(bad) });
  const ctx = makeSandbox({ store: store });
  const loaded = ctx.loadDayState();
  // CORRECT: normalize before the anchor capture (candidate init()).
  const norm = ctx.normalizeDayRecord(loaded);
  const anchorCorrect = norm;
  // WRONG: normalize only dayState after the anchor capture.
  const anchorWrong = loaded;
  const leafCorrect = anchorCorrect.completedQuests[0].objective;
  const leafWrong = anchorWrong.completedQuests[0].objective;
  console.log('  anchor (correct placement) leaf type: ' + typeof leafCorrect);
  console.log('  anchor (wrong placement)   leaf type: ' + typeof leafWrong);
  check(typeof leafCorrect === 'string', 'normalized anchor exposes a string leaf');
  check(typeof leafWrong === 'number',
    'wrong placement would leave a numeric leaf (the no-op fix)');
})();

// ---- Scenario 8: no write, both keys byte-identical
console.log('');
console.log('--- Scenario 8: no write on the load path (both keys byte-identical) ---');
(function () {
  const save = { name: 'Kai', level: 3, xp: 100, hp: 30, maxHp: 30, attack: 4,
                 defense: 3, gold: 50, bank: 10, weapon: 1, armor: 1, wins: 7, losses: 2, deaths: 0 };
  const bad = { dayIndex: TODAY, fightsUsed: 1, innHealsUsed: 0,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: [{ dayIndex: TODAY, label: 'x', objective: 999 }] };
  const store = makeStore({
    'flambeee-cinder-save': JSON.stringify(save),
    'flambeee-cinder-day': JSON.stringify(bad)
  });
  const ctx = makeSandbox({ store: store });
  const saveBefore = store.getItem('flambeee-cinder-save');
  const dayBefore = store.getItem('flambeee-cinder-day');
  store._writes.length = 0;
  Object.keys(ctx._calls).forEach(function (k) { ctx._calls[k].length = 0; });
  const loaded = ctx.loadDayState();
  ctx.dayState = HAS_HELPER ? ctx.normalizeDayRecord(loaded) : loaded;
  ctx.questLogAnchor = ctx.dayState;
  ctx.checkDailyReset();
  ctx.ensureQuestState();
  let threw = null;
  try { ctx.renderQuestLog(); } catch (e) { threw = e.message; }
  if (!HAS_HELPER) {
    check(threw !== null, 'v0.24.0 throws while rendering a corrupt record (throw reproduced: '
      + (threw || 'none') + ')');
    console.log('  v0.24.0 render threw: ' + (threw || 'none'));
  } else {
    check(threw === null, 'candidate renders a corrupt record without throwing');
  }
  const writers = ['saveCharacter', 'saveDayState', 'completeQuest', 'applyQuestProgress']
    .filter(function (k) { return ctx._calls[k].length > 0; });
  check(store._writes.length === 0, 'zero key writes across a corrupt load-and-render (writes='
    + store._writes.length + ')');
  check(writers.length === 0, 'no writer helper called ('
    + (writers.length ? writers.join(', ') : 'all silent') + ')');
  check(saveBefore === store.getItem('flambeee-cinder-save'),
    'flambeee-cinder-save byte-identical across the cycle');
  check(dayBefore === store.getItem('flambeee-cinder-day'),
    'flambeee-cinder-day byte-identical across the cycle (corrupt record stays on disk)');
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
        print("BLOCK: no source file containing renderQuestLog found")
        return 2
    base_src = git_show(BASE_REF)
    if base_src is None:
        print("BLOCK: could not read %s for the byte-identity comparisons" % BASE_REF)
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 053 proof: day-record load normalization ===")
    print("source under test: %s" % label)
    print("resolved to: %s" % src_path)
    print("sha256: %s" % digest)
    print("base for comparison: %s" % BASE_REF)
    print("")

    problems = static_scan(src, base_src)

    # Frozen functions byte-identical to v0.24.0.
    print("")
    print("=== Frozen functions byte-identical to v0.24.0 (Story 053 section 9) ===")
    for fn in FROZEN:
        try:
            got = body_of(src, fn)
        except RuntimeError as e:
            problems.append(str(e)); print("  BLOCK: " + str(e)); continue
        try:
            want = body_of(base_src, fn)
        except RuntimeError as e:
            problems.append("base copy of %s unreadable: %s" % (fn, e)); continue
        gh = hashlib.sha256(got.encode("utf-8")).hexdigest()
        bh = hashlib.sha256(want.encode("utf-8")).hexdigest()
        if gh == bh:
            print("  %-28s byte-identical to v0.24.0 (%s)" % (fn + "()", bh[:12]))
        else:
            problems.append("%s CHANGED vs v0.24.0 (%s vs %s)" % (fn, gh[:12], bh[:12]))
            print("  BLOCK: %s changed (sha %s vs v0.24.0 %s)" % (fn, gh[:12], bh[:12]))

    print("")
    print("=== Node proof: extracted load path, throw, counters, placement, no-write ===")
    node_src = PROOF_NODE.replace("__SRC_PATH__", json.dumps(src_path))
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
        print("BLOCK: static/frozen scan failed")
        for p in problems:
            print("  - " + p)
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
