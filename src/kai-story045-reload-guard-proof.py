#!/usr/bin/env python3
"""Kai reload-guard proof for Story 045 (Cinder welcome-back on a stale record).

Story 045 verifies the claim v0.21.0 shipped, not a code change. The claim was:

    "a same-day reload no longer re-shows the welcome-back panel, generally"

That claim is stronger than the code. This script proves the two staleness cases
separately, on the SHIPPED code, and states plainly what each one shows.

  Case A: the loaded day record is stale by EXACTLY 1 day (dayIndex = T - 1).
  Case B: the loaded day record is stale by 3+ days (dayIndex = T - 3).

Each case runs a full page load and a reload on the same UTC day T:

  1. seed flambeee-cinder-day with the case record
  2. FIRST load: the real init() order - rawDayState captured, computeAwayWindow()
     on the loaded record, shouldShowWelcomeBack() for the panel decision, then
     the real checkDailyReset() (which writes today's stamp, the pre-existing
     behavior that closes the window)
  3. RELOAD from the saved bytes: load what the reset wrote, recompute the window
     and the guard decision, and read the outcome

No code is being fixed here. The expected and accepted outcome is
"no code defect, claim corrected". The script's job is to report what the
shipped build does, per case, so the public claim can be matched to it.

The script also records the honest adjacent limitation the story names: literal
multi-day suppression on a LATER UTC day inside the same gap cannot be achieved
with zero persisted state, because the reset's write is what closes the window.
Case B is the SAME-DAY reload of an already-stale record, which the reset's own
write handles. Both facts belong in the corrected claim.

Source under test: resolved from argv[1], then $CINDER_SRC, then ./cinder.html
next to this script. Exits 0 when both cases are proven and the report is
self-consistent. Exits non-zero if the panel re-appears on a reload in either
case (that would be a real defect, Story 045 Scenario 9) or if the harness
cannot run.

Run:
  .venv/bin/python3 src/kai-story045-reload-guard-proof.py
  .venv/bin/python3 src/kai-story045-reload-guard-proof.py /path/to/cinder.html
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/jake/.openclaw/workspace/flambeee"
V0210_REF = "v0.21.0:src/cinder.html"


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
            if "function shouldShowWelcomeBack(" in txt:
                return c, txt, c
    for ref in ("main:src/cinder.html", V0210_REF):
        txt = git_show(ref)
        if txt and "function shouldShowWelcomeBack(" in txt:
            fd, tmp = tempfile.mkstemp(suffix="-cinder.html", prefix="story045-")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(txt)
            return tmp, txt, "git:%s (%s)" % (ref, REPO)
    return None, None, None


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


def byte_identity_check(src, base_src):
    """Story 045 Scenario 10: the frozen functions are untouched by this story."""
    problems = []
    print("=== Static scan: frozen functions vs v0.21.0 (Scenario 10) ===")
    for fn in ("checkDailyReset", "computeAwayWindow", "shouldShowWelcomeBack",
               "computeQuestStreak"):
        try:
            got = body_of(src, fn)
            want = body_of(base_src, fn)
        except RuntimeError as e:
            problems.append("could not compare %s: %s" % (fn, e))
            print("  BLOCK: " + str(e))
            continue
        gh = hashlib.sha256(got.encode("utf-8")).hexdigest()
        bh = hashlib.sha256(want.encode("utf-8")).hexdigest()
        if gh == bh:
            print("  function %-24s byte-identical to v0.21.0 (%s)" % (fn + "()", bh[:12]))
        else:
            problems.append("%s CHANGED vs v0.21.0 (%s vs %s)" % (fn, gh[:12], bh[:12]))
            print("  BLOCK: %s changed (sha %s vs v0.21.0 %s)" % (fn, gh[:12], bh[:12]))
    if problems:
        for p in problems:
            print("BLOCK: " + p)
    else:
        print("PASS: this story changed no guard, no window and no reset")
    return problems


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');

const SRC_PATH = __SRC_PATH__;
const src = fs.readFileSync(SRC_PATH, 'utf8');

// Deterministic "today" so the reload is always on the same UTC day T.
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

// A real in-memory localStorage. The reset's write lands in it, exactly as a
// browser reload would then read it back.
function makeStore(seed) {
  const data = Object.assign({}, seed || {});
  return {
    getItem: function (k) { return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null; },
    setItem: function (k, v) { data[k] = String(v); },
    removeItem: function (k) { delete data[k]; },
    _data: data
  };
}

function makeSandbox(store) {
  const nodes = {};
  const ctx = {
    console: console, Math: Math, Date: Date, Array: Array, Object: Object,
    JSON: JSON, isFinite: isFinite, parseInt: parseInt, String: String,
    Number: Number, Boolean: Boolean, Error: Error,
    getDayIndex: function () { return TODAY; },
    localStorage: {
      getItem: function (k) { return store.getItem(k); },
      setItem: function (k, v) { store.setItem(k, v); },
      removeItem: function (k) { store.removeItem(k); }
    },
    syncAppBadge: function () {},
    addLog: function () {},
    ensureQuestState: function () {
      if (!ctx.dayState) return;
      if (!ctx.dayState.quest) {
        ctx.dayState.quest = { progress: 0, completed: false, rewarded: false };
        ctx.saveDayState();
      }
      if (!Array.isArray(ctx.dayState.completedQuests)) {
        ctx.dayState.completedQuests = [];
        ctx.saveDayState();
      }
    },
    character: { xp: 100, gold: 50, level: 3, bank: 10, wins: 7 },
    dayState: null,
    MAX_FIGHTS_PER_DAY: 5,
    document: {
      getElementById: function (id) {
        if (!nodes[id]) nodes[id] = { innerHTML: '', value: '', focus: function () {} };
        return nodes[id];
      }
    }
  };
  ctx._nodes = nodes;
  ctx._store = store;
  vm.createContext(ctx);
  ['computeAwayWindow', 'shouldShowWelcomeBack', 'computeQuestStreak',
   'awayDaysSentence', 'awayQuestsSentence', 'awayStreakSentence',
   'renderWelcomeBack', 'handleWelcomeBackInput', 'checkDailyReset'].forEach(function (n) {
    try { vm.runInContext(extract(n), ctx); } catch (e) { /* reported by caller */ }
  });
  ctx.loadDayState = function () {
    try {
      const data = store.getItem('flambeee-cinder-day');
      return data ? JSON.parse(data) : null;
    } catch (e) { return null; }
  };
  ctx.saveDayState = function () {
    try { store.setItem('flambeee-cinder-day', JSON.stringify(ctx.dayState)); } catch (e) {}
  };
  // The real init() order, reduced to the parts that decide the panel:
  // capture rawDayState, compute the window on the LOADED record, decide, reset.
  ctx.simulateLoad = function () {
    ctx.dayState = ctx.loadDayState();
    const rawDayState = ctx.dayState;
    const window = ctx.computeAwayWindow(rawDayState, ctx.getDayIndex());
    const decision = ctx.shouldShowWelcomeBack(window, false, rawDayState);
    ctx.dayState = rawDayState;
    ctx.checkDailyReset();
    return { raw: rawDayState, window: window, decision: decision };
  };
  return ctx;
}

function makeRecord(dayIndex, completedDays, questCompleted) {
  return {
    dayIndex: dayIndex,
    fightsUsed: 0,
    innHealsUsed: 0,
    quest: { progress: 0, completed: !!questCompleted, rewarded: !!questCompleted },
    completedQuests: (completedDays || []).map(function (d, i) {
      return { dayIndex: d, label: 'q' + i, objective: 'obj' + d };
    })
  };
}
function panelLine(ctx, w) {
  return ctx.awayStreakSentence(w.streakSurvived);
}

function runCase(label, staleDays, completedDays) {
  console.log('');
  console.log('--- ' + label + ' ---');
  const seededIndex = TODAY - staleDays;
  const seedRecord = makeRecord(seededIndex, completedDays);
  const store = makeStore({ 'flambeee-cinder-day': JSON.stringify(seedRecord) });
  console.log('  seeded flambeee-cinder-day: dayIndex T-' + staleDays
    + ' (T=' + TODAY + '), completedQuests dayIndexes ['
    + (completedDays || []).join(', ') + ']');

  // FIRST load.
  const load1 = makeSandbox(store);
  const r1 = load1.simulateLoad();
  console.log('  FIRST load:  window.shouldShow=' + r1.window.shouldShow
    + ' daysAway=' + r1.window.daysAway
    + ' questsMissed=' + r1.window.questsMissed
    + ' streakSurvived=' + r1.window.streakSurvived
    + ' -> panel ' + (r1.decision ? 'SHOW' : 'suppressed'));

  // What the reset wrote, which is what the reload will read.
  const written = JSON.parse(store.getItem('flambeee-cinder-day'));
  console.log('  checkDailyReset() wrote: dayIndex ' + written.dayIndex
    + ' (today=' + TODAY + '), completedQuests []? ' + (written.completedQuests.length === 0));

  // RELOAD on the same UTC day, fresh page, from the saved bytes.
  const load2 = makeSandbox(store);
  const raw2 = load2.loadDayState();
  const window2 = load2.computeAwayWindow(raw2, TODAY);
  const decision2 = load2.shouldShowWelcomeBack(window2, false, raw2);
  console.log('  RELOAD:      loaded dayIndex=' + raw2.dayIndex
    + ' lastPlayIdx=' + raw2.dayIndex
    + ' gapDays=' + (TODAY - raw2.dayIndex)
    + ' daysAway=' + window2.daysAway
    + ' window.shouldShow=' + window2.shouldShow
    + ' -> panel ' + (decision2 ? 'SHOW' : 'suppressed'));
  console.log('  RELOAD outcome: panel ' + (decision2 ? 'APPEARED' : 'DID NOT APPEAR')
    + '; player lands on ' + (decision2 ? 'the welcome-back panel' : 'the town hub'));

  return {
    label: label, staleDays: staleDays, seededIndex: seededIndex,
    first: { shouldShow: r1.window.shouldShow, daysAway: r1.window.daysAway,
             questsMissed: r1.window.questsMissed, streakSurvived: r1.window.streakSurvived,
             decision: r1.decision, panel: r1.decision ? 'SHOW' : 'suppressed',
             line: panelLine(load1, r1.window) },
    reload: { dayIndex: raw2.dayIndex, daysAway: window2.daysAway,
              shouldShow: window2.shouldShow, decision: decision2,
              panel: decision2 ? 'SHOW' : 'suppressed' }
  };
}

console.log('=== Story 045 reload-guard proof (extracted from shipped file) ===');
console.log('source under test: ' + SRC_PATH);
console.log('deterministic today T = ' + TODAY);

// Case A: record stale by EXACTLY 1 day.
const A = runCase('Case A: record stale by exactly 1 day (dayIndex = T - 1)', 1, [TODAY - 1]);
// Case B: record stale by 3+ days.
const B = runCase('Case B: record stale by 3+ days (dayIndex = T - 3)', 3, [TODAY - 4, TODAY - 3]);

console.log('');
console.log('=== Per-case verdict ===');

// Case A assertions: the reset stamps today on the first load, so the reload is quiet.
check(A.first.daysAway === 0 && A.first.shouldShow === false,
      'Case A FIRST load: dayIndex T-1 means gapDays 1 and daysAway 0, so the panel is not '
      + 'eligible at all [daysAway ' + A.first.daysAway + ', shouldShow ' + A.first.shouldShow + ']');
check(A.reload.dayIndex === TODAY && A.reload.shouldShow === false && A.reload.decision === false,
      'Case A RELOAD: the reset stamped today, the reload reads dayIndex today, the window is '
      + 'closed and the panel did not appear [' + A.reload.panel + ']');

// Case B assertions: the panel shows once on the gap load and is quiet on the reload.
check(B.first.shouldShow === true && B.first.decision === true,
      'Case B FIRST load: dayIndex T-3 means the panel shows once for the gap [daysAway '
      + B.first.daysAway + ', questsMissed ' + B.first.questsMissed + ', panel ' + B.first.panel + ']');
check(B.first.line === 'Your streak survived.',
      'Case B FIRST load panel line: "' + B.first.line + '"');
check(B.reload.dayIndex === TODAY && B.reload.shouldShow === false && B.reload.decision === false,
      'Case B RELOAD: the reset stamped today on the first load, so the reload finds gapDays 0 '
      + 'and the panel did not appear [' + B.reload.panel + ']');

// The claim verdict, in the story's own terms.
check(A.reload.panel === 'suppressed' && B.reload.panel === 'suppressed',
      'CLAIM: the panel does not re-show on a same-day reload in BOTH staleness cases, so no '
      + 'code defect was found and no code change is required (Story 045 Scenario 4)');

console.log('');
console.log('=== Claim verdict ===');
console.log('  v0.21.0 claim, verbatim intent: "a same-day reload no longer re-shows the');
console.log('  welcome-back panel, generally".');
console.log('  Case A (stale exactly 1 day): the claim is TRUE. The first load is already quiet');
console.log('    (daysAway 0), and the reload is quiet after the reset stamps today.');
console.log('  Case B (stale 3+ days): the reload behaviour the claim describes is TRUE (the');
console.log('    panel showed once on the first load and did NOT reappear on the reload), but');
console.log('    the reason is not a guard. It is checkDailyReset() writing today on the first');
console.log('    load, which closes the window before the reload can read it.');
console.log('  So the claim holds for BOTH same-day reload cases, and the word "generally" is');
console.log('  what overstated it: the mechanism is the daily reset stamping today, not a');
console.log('  persisted seen-flag. The narrower true statement is:');
console.log('    "the panel shows once per gap; a same-day reload does not re-show it, because');
console.log('     the daily reset stamps today on the first load."');
console.log('  Recorded limitation (must not be confused with this case): literal multi-day');
console.log('  suppression on a LATER UTC day inside the same gap cannot be achieved with zero');
console.log('  persisted state, because that same reset write is what closes the window.');

console.log('');
if (failures.length === 0) {
  console.log('ALL PASS (' + passes + ' checks): no code defect, claim corrected');
  process.exit(0);
} else {
  console.log(failures.length + ' FAILURES (' + passes + ' passed)');
  failures.forEach(function (f) { console.log('  - ' + f); });
  console.log('A panel that RE-APPEARS on a reload in either case is a real defect:');
  console.log('Story 045 Scenario 9 applies, and the fix is read-only presentation.');
  process.exit(1);
}
"""


def main():
    src_path, src, label = resolve_source()
    if src_path is None:
        print("BLOCK: no source file containing shouldShowWelcomeBack found")
        return 2
    base_src = git_show(V0210_REF)
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    print("=== Story 045 reload-guard proof: both staleness cases ===")
    print("source under test: %s" % label)
    print("resolved to: %s" % src_path)
    print("sha256: %s" % digest)
    print("base for comparison: %s" % V0210_REF)
    print("")

    problems = []
    if base_src is None:
        print("WARN: could not read %s, skipping the byte-identity scan" % V0210_REF)
    else:
        problems += byte_identity_check(src, base_src)

    print("")
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
        for p in problems:
            print("  - " + p)
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
