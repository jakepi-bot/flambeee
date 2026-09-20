#!/usr/bin/env python3
"""Kai pure-read proof for Story 040 (Cinder welcome-back return summary).

Proves the shipped `computeAwayWindow(rawDayState, todayIdx)` gate against the
binding Session 22 gate spec (flambeee-team/state/040-gate-spec.md) by extracting
the real function bodies out of src/cinder.html into a node vm sandbox and
asserting against them. Nothing here re-implements the logic under test.

Asserted, all from extracted shipped code:
  1. Same-day return: no summary (shouldShow false, daysAway <= 0).
  2. Next-day return: no summary. Story 033 come-back-tomorrow flow untouched.
  3. One fully missed UTC day: shouldShow true, daysAway 1, questsMissed exact.
  4. Multi-day and 30+ day gaps: correct daysAway/questsMissed, questsMissed <=
     daysAway always (including a deterministic sweep over 0..60 day gaps).
  5. THE FLAGGED HAZARD: the window is computed from the LOADED record. With the
     real checkDailyReset() extracted and run, a record whose dayIndex is old
     yields the correct window, and the post-reset record yields the WRONG answer
     (no summary). Reading dayState after the reset is shown to be a defect.
  6. questsMissed is derived from completedQuests: a known window with a known
     completed-day set yields the exact count and excludes completed days.
  7. streakSurvived covers both branches: helper > 0 -> survived, 0 -> broken,
     plus the renderer line for both branches.
  8. Degradation: null, {}, non-numeric dayIndex, non-array completedQuests,
     junk entries, future dayIndex, non-object input, non-numeric todayIdx.
     No throw anywhere and a sane result each time.
  9. No-write proof: saveCharacter, saveDayState, localStorage.setItem,
     completeQuest, applyQuestProgress are instrumented and NONE are called on
     the summary path (computeAwayWindow + renderWelcomeBack +
     handleWelcomeBackInput). The input argument object is deep-compared
     before/after and no sandbox global is added.
 10. Static scan of the shipped summary path: no saveCharacter(, saveDayState(,
     localStorage.setItem, completeQuest(, applyQuestProgress(, Notification,
     pushManager, onclick=; and no new persisted field (seenReturnSummary,
     lastSeenReturn, welcomeBackShown) anywhere in the file.

Source under test: resolved from argv[1], then $CINDER_SRC, then ./cinder.html
next to this script, then Riven's parallel worktree (the implementing branch).
The resolved path and its sha256 are printed so the run is reproducible.

Run:
  .venv/bin/python3 src/kai-story040-pure-read-proof.py
  .venv/bin/python3 src/kai-story040-pure-read-proof.py /path/to/cinder.html
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
RIVEN_WT = "/tmp/flambeee-wt-riven/src/cinder.html"

# The shipped summary path this proof holds to the contract.
PATH_FNS = [
    "computeAwayWindow",
    "awayDaysSentence",
    "awayQuestsSentence",
    "awayStreakSentence",
    "renderWelcomeBack",
    "handleWelcomeBackInput",
]
# Tokens that must never appear inside the summary path.
FORBIDDEN = [
    "saveCharacter(",
    "saveDayState(",
    "localStorage.setItem",
    "completeQuest(",
    "applyQuestProgress(",
    "Notification",
    "pushManager",
    "onclick=",
]
# New persisted fields the story forbids, anywhere in the file.
FORBIDDEN_FIELDS = ["seenReturnSummary", "lastSeenReturn", "welcomeBackShown"]


def resolve_source():
    cands = []
    if len(sys.argv) > 1:
        cands.append(sys.argv[1])
    if os.environ.get("CINDER_SRC"):
        cands.append(os.environ["CINDER_SRC"])
    cands.append(os.path.join(HERE, "cinder.html"))
    cands.append(RIVEN_WT)
    for c in cands:
        if c and os.path.isfile(c):
            txt = open(c, encoding="utf-8").read()
            if "function computeAwayWindow(" in txt:
                return c, txt
    return None, None


def strip_comments(js):
    """Blank out // and /* */ comments, preserving string literals as written.

    Token scans run on the stripped text so a comment that merely names a
    forbidden writer (for example "no saveCharacter()") is not a false hit,
    while a real call in code still is.
    """
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
        hit = [t for t in FORBIDDEN if t in span]
        if hit:
            problems.append("forbidden token in %s: %s" % (fn, ", ".join(hit)))
        if re.search(r"(character|dayState|awayWindow)\s*\.\s*\w+\s*=(?!=)", span):
            problems.append("assignment to character./dayState./awayWindow. in " + fn)
        print("  scanned %-24s %5d chars, forbidden hits: %d"
              % (fn, len(span), len(hit)))

    for f in FORBIDDEN_FIELDS:
        n = len(re.findall(r"\b" + f + r"\b", src))
        if n:
            problems.append("forbidden new persisted field %s appears %d time(s) in file" % (f, n))
        else:
            print("  no new persisted field: %s" % f)

    defs = len(re.findall(r"function computeAwayWindow\s*\(", code))
    if defs != 1:
        problems.append("expected exactly 1 definition of computeAwayWindow, found %d" % defs)
    else:
        print("  computeAwayWindow defined exactly once")

    calls = len(re.findall(r"computeAwayWindow\s*\(", code)) - defs
    if calls < 1:
        problems.append("computeAwayWindow is never called from the shipped code")
    else:
        print("  computeAwayWindow called from shipped code: %d call site(s)" % calls)

    # Wiring order: the capture + compute must precede checkDailyReset() in init().
    try:
        init = strip_comments(body_of(src, "init"))
    except RuntimeError as e:
        problems.append(str(e))
        init = ""
    if init:
        i_capture = init.find("rawDayState")
        i_compute = init.find("computeAwayWindow(")
        i_reset = init.find("checkDailyReset()")
        if i_capture < 0:
            problems.append("init() does not capture a rawDayState before the reset")
        if i_compute < 0:
            problems.append("init() does not call computeAwayWindow")
        if i_reset < 0:
            problems.append("init() no longer calls checkDailyReset()")
        if i_capture >= 0 and i_compute >= 0 and i_reset >= 0:
            if not (i_capture < i_reset and i_compute < i_reset):
                problems.append("init() computes the window AFTER checkDailyReset() (hazard)")
            else:
                print("  init(): rawDayState captured and window computed BEFORE checkDailyReset()")

    # One-time guard must be in-memory, and no persisted flag is allowed.
    if re.search(r"localStorage\.setItem\s*\([^)]*return", code, re.I):
        problems.append("localStorage.setItem appears to persist a return-summary flag")
    if not re.search(r"let\s+returnShown\s*=\s*false", code):
        problems.append("in-memory one-time guard (let returnShown = false) not found")

    if problems:
        for p in problems:
            print("BLOCK: " + p)
    else:
        print("PASS: summary path carries no writes and no new persisted field")
    return problems


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');

const SRC_PATH = __SRC_PATH__;
const src = fs.readFileSync(SRC_PATH, 'utf8');

// Deterministic "today" so every arithmetic expectation is exact.
const TODAY = Math.floor(Date.UTC(2026, 8, 20, 12) / 86400000);

let failures = [];
let passes = 0;
function check(cond, msg) {
  if (cond) { passes += 1; console.log('PASS: ' + msg); }
  else { failures.push(msg); console.log('FAIL: ' + msg); }
}

// Extract a top-level function body verbatim by paren/brace matching.
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

// --- write instrument: every forbidden writer records an invocation ---
function makeSandbox(opts) {
  opts = opts || {};
  const calls = {
    saveCharacter: [], saveDayState: [], setItem: [], completeQuest: [],
    applyQuestProgress: [], ensureQuestState: [], syncAppBadge: [], addLog: [],
    renderTownMenu: [], renderQuest: [], clearLog: []
  };
  const nodes = {};
  const ctx = {
    console: console, Math: Math, Date: Date, Array: Array, Object: Object,
    JSON: JSON, isFinite: isFinite, parseInt: parseInt, String: String,
    Number: Number, Boolean: Boolean, Error: Error,
    getDayIndex: function () { return TODAY; },
    saveCharacter: function () { calls.saveCharacter.push(1); },
    saveDayState: function () { calls.saveDayState.push(1); },
    localStorage: {
      getItem: function () { return null; },
      setItem: function (k, v) { calls.setItem.push([k, v]); },
      removeItem: function () {}
    },
    completeQuest: function () { calls.completeQuest.push(1); },
    applyQuestProgress: function () { calls.applyQuestProgress.push(1); },
    ensureQuestState: function () { calls.ensureQuestState.push(1); },
    syncAppBadge: function () { calls.syncAppBadge.push(1); },
    addLog: function (t) { calls.addLog.push(t); },
    renderTownMenu: function () { calls.renderTownMenu.push(1); },
    renderQuest: function () { calls.renderQuest.push(1); },
    clearLog: function () { calls.clearLog.push(1); },
    character: { xp: 100, gold: 50, level: 3, bank: 10, wins: 7 },
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
  if (opts.streakStub !== undefined) {
    ctx.computeQuestStreak = function () { return opts.streakStub; };
  }
  vm.createContext(ctx);
  // Real shipped helpers only (except an explicit streak stub, reported below).
  vm.runInContext(extract('escapeHtml'), ctx);
  if (opts.streakStub === undefined) {
    vm.runInContext(extract('computeQuestStreak'), ctx);
  }
  vm.runInContext(extract('computeAwayWindow'), ctx);
  ['awayDaysSentence', 'awayQuestsSentence', 'awayStreakSentence', 'renderWelcomeBack']
    .forEach(function (n) { vm.runInContext(extract(n), ctx); });
  if (opts.withHandlers) {
    vm.runInContext(extract('handleWelcomeBackInput'), ctx);
  }
  if (opts.withReset) {
    vm.runInContext(extract('checkDailyReset'), ctx);
  }
  // Real getActiveQuest() needs the quest table; the pointer text is Riven's
  // copy, not the gate, so it is stubbed and reported honestly.
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
    fightsUsed: 0,
    innHealsUsed: 0,
    quest: { progress: 0, completed: false, rewarded: false },
    completedQuests: history(completedDays || [])
  };
}

console.log('=== Behavioural proof: computeAwayWindow (extracted from shipped file) ===');

// 1. Same-day return -> no summary.
(function () {
  const ctx = makeSandbox();
  const raw = rec(TODAY, [TODAY]);
  const before = JSON.stringify(raw);
  const w = ctx.computeAwayWindow(raw, TODAY);
  check(w.shouldShow === false, 'S1 same-day return: shouldShow false [got ' + w.shouldShow + ']');
  check(w.daysAway <= 0, 'S1 same-day return: daysAway <= 0, clamped to ' + w.daysAway);
  check(JSON.stringify(raw) === before, 'S1 same-day return: input record not mutated');
})();

// 2. Next-day return -> no summary (Story 033 flow untouched).
(function () {
  const ctx = makeSandbox();
  const w = ctx.computeAwayWindow(rec(TODAY - 1, [TODAY - 1]), TODAY);
  const w2 = ctx.computeAwayWindow(rec(TODAY - 1, [TODAY - 1, TODAY - 2]), TODAY);
  check(w.shouldShow === false && w.daysAway === 0,
        'S2 next-day return (dayIndex today-1): shouldShow false, daysAway ' + w.daysAway);
  check(w2.shouldShow === false && w2.daysAway === 0,
        'S2 next-day return with history: shouldShow false, daysAway ' + w2.daysAway);
})();

// 3. One fully missed UTC day -> summary, daysAway 1.
(function () {
  const ctx = makeSandbox();
  const w = ctx.computeAwayWindow(rec(TODAY - 2, []), TODAY);
  check(w.shouldShow === true, 'S3 one missed day: shouldShow true');
  check(w.daysAway === 1, 'S3 one missed day: daysAway 1 [got ' + w.daysAway + ']');
  check(w.questsMissed === 1, 'S3 one missed day: questsMissed 1 [got ' + w.questsMissed + ']');
})();

// 4. Multi-day gaps and a long gap.
(function () {
  const ctx = makeSandbox();
  const w4 = ctx.computeAwayWindow(rec(TODAY - 4, []), TODAY);
  check(w4.shouldShow === true && w4.daysAway === 3 && w4.questsMissed === 3,
        'S4a todayIdx-4: daysAway 3, questsMissed 3 [got ' + w4.daysAway + '/' + w4.questsMissed + ']');
  const w40 = ctx.computeAwayWindow(rec(TODAY - 40, []), TODAY);
  check(w40.shouldShow === true && w40.daysAway === 39 && w40.questsMissed === 39,
        'S4b 30+ day gap (todayIdx-40): daysAway 39, questsMissed 39 [got ' + w40.daysAway + '/' + w40.questsMissed + ']');
  // deterministic sweep: questsMissed <= daysAway for every gap 0..60
  let bad = null, shown = 0, hidden = 0;
  for (let g = 0; g <= 60; g++) {
    const w = ctx.computeAwayWindow(rec(TODAY - g, []), TODAY);
    if (w.questsMissed > w.daysAway) bad = { g: g, w: w };
    if (w.shouldShow) shown += 1; else hidden += 1;
    if (g <= 1 && w.shouldShow) bad = { g: g, w: w };
    if (g >= 2 && !w.shouldShow) bad = { g: g, w: w };
  }
  check(bad === null, 'S4c sweep gap 0..60: questsMissed <= daysAway and gate flips exactly at gap 2'
        + (bad ? ' [violation ' + JSON.stringify(bad) + ']' : '') + ' (' + shown + ' shown / ' + hidden + ' hidden)');
})();

// 5. THE FLAGGED HAZARD: loaded record vs post-reset record.
(function () {
  const ctx = makeSandbox({ withReset: true });
  const raw = rec(TODAY - 3, [TODAY - 4]);
  ctx.dayState = raw;
  const before = JSON.stringify(raw);
  // Correct capture point: before the reset, exactly as init() does.
  const captured = ctx.computeAwayWindow(raw, TODAY);
  check(JSON.stringify(raw) === before,
        'S5 loaded record survives the window computation unmutated');
  // Run the real shipped reset and see what dayState becomes.
  ctx.checkDailyReset();
  const postReset = ctx.dayState;
  const wrong = ctx.computeAwayWindow(postReset, TODAY);
  check(postReset && postReset.dayIndex === TODAY,
        'S5 real checkDailyReset() replaced dayState with today\'s index ('
        + (postReset ? postReset.dayIndex : 'null') + ')');
  check(captured.shouldShow === true && captured.daysAway === 2,
        'S5 window from LOADED record (dayIndex today-3): shouldShow true, daysAway 2 [got '
        + captured.shouldShow + '/' + captured.daysAway + ']');
  check(wrong.shouldShow === false,
        'S5 window from POST-RESET record: shouldShow false -> reading dayState after the '
        + 'reset is wrong and suppresses the summary (hazard proven)');
})();

// 6. questsMissed derived from completedQuests, never invented.
(function () {
  const ctx = makeSandbox();
  // Anchor day TODAY-6, completions all at or before the anchor, so the window
  // TODAY-5..TODAY-1 is five days with no completion on record.
  const w = ctx.computeAwayWindow(rec(TODAY - 6, [TODAY - 6, TODAY - 9, TODAY - 8]), TODAY);
  check(w.daysAway === 5 && w.questsMissed === 5,
        'S6 known window (5 days, 3 completed days all at/before the anchor): questsMissed 5 [got '
        + w.daysAway + '/' + w.questsMissed + ']');
  // Exclusion mechanism: a completion inside the nominal gap is not counted as
  // missed, it moves the anchor forward and shrinks the window.
  const wIn = ctx.computeAwayWindow(rec(TODAY - 6, [TODAY - 3]), TODAY);
  check(wIn.daysAway === 2 && wIn.questsMissed === 2,
        'S6 completion at TODAY-3 inside the nominal gap moves the anchor: daysAway 2, '
        + 'questsMissed 2, that day not counted as missed [got '
        + wIn.daysAway + '/' + wIn.questsMissed + ']');
  // all window days completed -> 0 missed
  const w0 = ctx.computeAwayWindow(
    rec(TODAY - 6, [TODAY - 5, TODAY - 4, TODAY - 3, TODAY - 2, TODAY - 1]), TODAY);
  check(w0.questsMissed === 0 && w0.shouldShow === false,
        'S6 every gap day completed: questsMissed 0 and no summary [got '
        + w0.daysAway + '/' + w0.questsMissed + '/' + w0.shouldShow + ']');
  // junk entries are ignored, valid ones still count
  const wj = ctx.computeAwayWindow(
    { dayIndex: TODAY - 5, completedQuests: [null, 'x', {}, { dayIndex: 'y' }] }, TODAY);
  check(wj.daysAway === 4 && wj.questsMissed === 4,
        'S6 junk history entries ignored, valid anchor kept: daysAway 4, questsMissed 4 [got '
        + wj.daysAway + '/' + wj.questsMissed + ']');
  // Structural property implied by the spec (lastPlayIdx = max over BOTH the day
  // stamp and every completed day): a completion can never sit strictly inside
  // the window, so questsMissed equals daysAway whenever the summary shows.
  let mismatch = null, shown = 0;
  for (let g = 2; g <= 60; g++) {
    for (let c = 0; c < 4; c++) {
      const days = [TODAY - g];
      if (c === 1) days.push(TODAY - 1);
      if (c === 2) days.push(TODAY - g + 1);
      if (c === 3) { days.push(TODAY - 1); days.push(TODAY - 2); }
      const w = ctx.computeAwayWindow(rec(TODAY - g, days.slice(1)), TODAY);
      if (w.shouldShow) {
        shown += 1;
        if (w.questsMissed !== w.daysAway) mismatch = { g: g, c: c, w: w };
      }
    }
  }
  check(mismatch === null,
        'S6 structural: across ' + shown + ' showing records, questsMissed === daysAway '
        + '(a completion is the max anchor, so no completed day can fall inside the window)'
        + (mismatch ? ' [violation ' + JSON.stringify(mismatch) + ']' : ''));
})();

// 7. streakSurvived: both branches.
(function () {
  const live = makeSandbox({ streakStub: 3 });   // instrumented helper, reported
  const dead = makeSandbox({ streakStub: 0 });
  const wl = live.computeAwayWindow(rec(TODAY - 3, []), TODAY);
  const wd = dead.computeAwayWindow(rec(TODAY - 3, []), TODAY);
  check(wl.streakSurvived === true, 'S7 helper > 0 -> streakSurvived true');
  check(wd.streakSurvived === false, 'S7 helper 0 -> streakSurvived false');
  const ctxR = makeSandbox();
  const s = ctxR.awayStreakSentence;
  check(s(true) === 'Your streak survived.',
        'S7 renderer survived line: "' + s(true) + '"');
  check(s(false) === 'Your streak is broken.',
        'S7 renderer broken line: "' + s(false) + '"');
  // honesty: with the real shipped computeQuestStreak, can both be true?
  const real = makeSandbox();
  let coOccur = 0;
  for (let g = 2; g <= 20; g++) {
    const w = real.computeAwayWindow(rec(TODAY - g, [TODAY - 1, TODAY - 2]), TODAY);
    if (w.shouldShow && w.streakSurvived) coOccur += 1;
  }
  console.log('NOTE: with the shipped computeQuestStreak(), shouldShow && streakSurvived co-occurred in '
    + coOccur + '/19 gap-return cases (gate spec section 4 records this: the reset rebuilds the '
    + 'record, so the line is normally "broken"; both renderer branches stay verified above).');
})();

// 8. Degradation: no throw, sane result.
(function () {
  const ctx = makeSandbox();
  const cases = [
    ['null rawDayState', null],
    ['undefined rawDayState', undefined],
    ['string rawDayState', 'nope'],
    ['number rawDayState', 7],
    ['empty object', {}],
    ['non-numeric dayIndex', { dayIndex: 'x', completedQuests: [] }],
    ['NaN dayIndex', { dayIndex: NaN, completedQuests: [] }],
    ['completedQuests not an array', { dayIndex: TODAY - 5, completedQuests: 'nope' }],
    ['completedQuests null', { dayIndex: TODAY - 5, completedQuests: null }],
    ['junk completedQuests entries', { dayIndex: TODAY - 5,
       completedQuests: [null, 'x', 7, {}, { dayIndex: 'y' }, { dayIndex: TODAY - 4 }] }],
    ['future dayIndex', { dayIndex: TODAY + 5, completedQuests: [] }],
    ['dayIndex only, no history', { dayIndex: TODAY - 2 }]
  ];
  let bad = [];
  cases.forEach(function (c) {
    let threw = null, w = null;
    try { w = ctx.computeAwayWindow(c[1], TODAY); } catch (e) { threw = e; }
    const shape = w && typeof w.shouldShow === 'boolean'
      && typeof w.daysAway === 'number' && typeof w.questsMissed === 'number'
      && typeof w.streakSurvived === 'boolean' && w.daysAway >= 0 && w.questsMissed >= 0
      && w.questsMissed <= Math.max(w.daysAway, w.questsMissed);
    if (threw || !shape) bad.push(c[0] + (threw ? ' [threw ' + threw.message + ']' : ' [bad shape ' + JSON.stringify(w) + ']'));
    console.log('   ' + (threw ? 'THREW ' : 'ok    ') + c[0] + ' -> ' + JSON.stringify(w));
  });
  check(bad.length === 0, 'S8 all ' + cases.length + ' degradation inputs: no throw, sane clamped result'
        + (bad.length ? ' [' + bad.join('; ') + ']' : ''));
  // bad todayIdx
  let badToday = [];
  [undefined, null, NaN, 'x', {}, Infinity].forEach(function (t) {
    let threw = null, w = null;
    try { w = ctx.computeAwayWindow(rec(TODAY - 5, []), t); } catch (e) { threw = e; }
    if (threw || !w || w.shouldShow !== false) badToday.push(JSON.stringify(t));
  });
  check(badToday.length === 0, 'S8 non-numeric/absent todayIdx never shows and never throws'
        + (badToday.length ? ' [' + badToday.join(', ') + ']' : ''));
  // future record with valid history must not divide backwards
  const wf = ctx.computeAwayWindow({ dayIndex: TODAY + 5, completedQuests: [{ dayIndex: TODAY - 1 }] }, TODAY);
  check(wf.shouldShow === false && wf.daysAway === 0,
        'S8 future dayIndex with valid history: no show, daysAway 0 [got ' + JSON.stringify(wf) + ']');
})();

// 9. No-write proof on the summary path.
(function () {
  const ctx = makeSandbox({ withHandlers: true });
  const raws = [
    rec(TODAY, [TODAY]), rec(TODAY - 1, []), rec(TODAY - 2, []),
    rec(TODAY - 4, [TODAY - 3]), rec(TODAY - 40, []), rec(TODAY - 30, [TODAY - 2]),
    null, {}, { dayIndex: 'x' }, { dayIndex: TODAY - 5, completedQuests: 'nope' },
    { dayIndex: TODAY + 3 }, { dayIndex: TODAY - 3, completedQuests: [null, {}, 'x'] }
  ];
  const snapshots = raws.map(function (r) { return JSON.stringify(r === undefined ? null : r); });
  const globalsBefore = JSON.stringify(Object.keys(ctx).sort());
  clearCalls(ctx);
  raws.forEach(function (raw) {
    const w = ctx.computeAwayWindow(raw, TODAY);
    ctx.awayWindow = w;
    ctx.renderWelcomeBack();
    ctx.handleWelcomeBackInput(1);
    ctx.handleWelcomeBackInput(2);
    ctx.handleWelcomeBackInput(99);
  });
  const called = writersCalled(ctx);
  check(called.length === 0, 'S9 summary path called no writer helpers ('
        + (called.length ? called.join(', ') : 'saveCharacter, saveDayState, localStorage.setItem, '
          + 'completeQuest, applyQuestProgress all silent') + ')');
  const mutated = [];
  raws.forEach(function (raw, i) {
    const s = JSON.stringify(raw === undefined ? null : raw);
    if (s !== snapshots[i]) mutated.push(i);
  });
  check(mutated.length === 0, 'S9 no input record mutated across 12 runs (' + (mutated.length ? 'indices ' + mutated.join(',') : 'all deep-equal') + ')');
  check(JSON.stringify(Object.keys(ctx).sort()) === globalsBefore,
        'S9 no sandbox global added by the summary path');
  const html = ctx._nodes['display'] ? ctx._nodes['display'].innerHTML : '';
  check(html.indexOf('=== WELCOME BACK ===') >= 0 && html.indexOf('data-action="1"') >= 0
        && html.indexOf('data-action="2"') >= 0 && html.indexOf('onclick') < 0,
        'S9 rendered view is the boxed-menu welcome-back with delegated data-action rows, no inline onclick');
  check(ctx._nodes['promptInput'] && ctx._nodes['promptInput'].focusCount >= 12,
        'S9 renderWelcomeBack re-focused the prompt '
        + (ctx._nodes['promptInput'] ? ctx._nodes['promptInput'].focusCount : 0)
        + ' times (no throw across all states)');
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
    src_path, src = resolve_source()
    if src_path is None:
        print("BLOCK: no source file containing computeAwayWindow found")
        print("       tried argv[1], $CINDER_SRC, %s, %s" % (os.path.join(HERE, "cinder.html"), RIVEN_WT))
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 040 pure-read proof: computeAwayWindow ===")
    print("source under test: %s" % src_path)
    print("sha256: %s" % digest)
    print("")

    problems = static_scan(src)
    print("")
    print("=== Node proof: extracted shipped gate + view + handlers ===")
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
        print("BLOCK: static scan failed")
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
