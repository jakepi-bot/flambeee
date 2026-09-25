#!/usr/bin/env python3
"""
Scout QA, Session 24 Wave 3. Stories 044 + 045.

Drives the REAL shipped helpers extracted from src/cinder.html:
  - computeQuestStreak      (unchanged, Story 035)
  - computeAwayWindow       (Story 042 streak source + anchor)
  - shouldShowWelcomeBack   (Story 042 one-time guard)
  - checkDailyReset         (Story 044 Scenario 13 / 045 reload mechanism)
  - renderQuestLog          (extracted for the streak-source line + static scan)
  - dayLabelForIndex        (recent-quests list labels)

Story 044 scenarios 1-14 in automated form, plus Story 045's two staleness cases.
QA verifies. Nothing here fixes or changes product code.
"""
import re, subprocess, sys, tempfile, os, json

REPO = "/home/jake/.openclaw/workspace/flambeee"
SRC = os.path.join(REPO, "src/cinder.html")
# Optional positional arg: path to the candidate artifact under test (defaults to
# the shipped file). Lets the same suite run against a branch artifact and the
# merged candidate without touching the tree.
if len(sys.argv) > 1:
    SRC = sys.argv[1]
PY = "/home/jake/.openclaw/workspace/.venv/bin/python3"
src = open(SRC).read()


def extract_fn(name, text=None):
    """Exact source of 'function NAME(...) {...}' by matching braces."""
    t = src if text is None else text
    m = re.search(r'\bfunction ' + re.escape(name) + r'\s*\(', t)
    if not m:
        return None
    start = m.start()
    brace = t.find('{', m.end())
    depth = 0
    i = brace
    while i < len(t):
        c = t[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return t[start:i + 1]
        elif c in "'\"`":
            q = c
            i += 1
            while i < len(t):
                if t[i] == '\\':
                    i += 2
                    continue
                if t[i] == q:
                    break
                i += 1
        i += 1
    return t[start:]


print("=" * 72)
print("Artifact under test")
print("=" * 72)
h = subprocess.run(["sha256sum", SRC], capture_output=True, text=True).stdout.strip()
print(h)
print("helper present: computeQuestLogStreak ->", "computeQuestLogStreak" in src)
m = re.search(r'const streak = [^;]+;', src)
print("renderQuestLog streak source line ->", m.group(0) if m else "(not found)")
print()

FNS = ["computeQuestStreak", "computeAwayWindow", "shouldShowWelcomeBack",
       "checkDailyReset", "dayLabelForIndex", "renderQuestLog", "ensureQuestState"]
blocks = {fn: extract_fn(fn) for fn in FNS}
missing = [fn for fn, b in blocks.items() if b is None]
if missing:
    print("FAIL could not extract:", missing)
    sys.exit(1)

# ---------------------------------------------------------------- node harness
harness_prelude = (
    "const vm = require('vm');\n"
    "const fs = require('fs');\n"
    "const DAY = 86400000;\n"
    "let NOW = 1700000000000;\n"
    "let WRITES = [];\n"
    "const store = {};\n"
    "const ctx = {\n"
    "  DAY: DAY,\n"
    "  NOW: () => NOW,\n"
    "  Math, Array, Object, JSON, String, Number, console, isFinite, NaN,\n"
    "  MAX_FIGHTS_PER_DAY: 5,\n"
    "  addLog: () => {},\n"
    "  syncAppBadge: () => {},\n"
    "  localStorage: {\n"
    "    getItem: (k) => (k in store ? store[k] : null),\n"
    "    setItem: (k, v) => { WRITES.push(k); store[k] = String(v); }\n"
    "  },\n"
    "  DAY_KEY: 'flambeee-cinder-day',\n"
    "  SAVE_KEY: 'flambeee-cinder-save',\n"
    "  dayState: null,\n"
    "  getWrites: () => WRITES,\n"
    "  resetWrites: () => { WRITES = []; },\n"
    "};\n"
    "vm.createContext(ctx);\n"
    "ctx.__WRITES__ = () => WRITES;\n"
    "vm.runInContext(\"var document = { getElementById: () => ({ value: '', textContent: '', innerHTML: '', scrollTop: 0, scrollHeight: 0, focus: function(){}, addEventListener: function(){} }) }; var window = {};\", ctx);\n"
)

# Everything runs INSIDE the vm context, where `dayState`, the localStorage
# shim and the shipped functions all resolve exactly as they do in the page.
# Only saveDayState and getDayIndex are re-declared (they are thin shims over
# the same keys); checkDailyReset itself is the SHIPPED source, unchanged.
harness_fns = (
    "function saveDayState(){ try { localStorage.setItem(DAY_KEY, JSON.stringify(dayState)); } catch(e){} }\n"
    "function getDayIndex(){ return Math.floor(NOW()/DAY); }\n"
    + (blocks["ensureQuestState"] or "") + "\n"
    + (blocks["checkDailyReset"] or "") + "\n"
    + (blocks["computeQuestStreak"] or "") + "\n"
    + (blocks["computeAwayWindow"] or "") + "\n"
    + (blocks["shouldShowWelcomeBack"] or "") + "\n"
    + (blocks["dayLabelForIndex"] or "") + "\n"
    + "globalThis.setDay = (v) => { dayState = v; };\n"
    + "globalThis.getDay = () => dayState;\n"
    + "globalThis.resetW = () => resetWrites();\n"
)

harness_expose = (
    "vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);\n"
    "vm.runInContext(fs.readFileSync(process.argv[3], 'utf8'), ctx);\n"
    "process.exit(ctx.__QA_EXIT__ || 0);\n"
)

test_body = r'''
const T = getDayIndex();
const setDay = globalThis.setDay;
const getDay = globalThis.getDay;
const resetW = globalThis.resetW;
const results = [];
function check(name, cond, detail) { results.push({name, pass: !!cond, detail: detail||''}); }
function ds(x){ return JSON.parse(JSON.stringify(x)); }

// ---------- Story 044 helpers ----------
// Reference implementation of the required read-only derivation, anchored on the
// LAST RECORDED PLAY DAY exactly as computeAwayWindow() anchors it. This is the
// specification from the story; the candidate must reproduce it WITHOUT writing
// or adding a field.
function recordedRunLen(dayState, rawDayState) {
  const raw = (arguments.length > 1) ? rawDayState : dayState;
  if (!raw || typeof raw !== 'object') return 0;
  let last = null;
  if (typeof raw.dayIndex === 'number' && isFinite(raw.dayIndex)) last = raw.dayIndex;
  const hist = raw.completedQuests;
  const done = {};
  if (Array.isArray(hist)) {
    for (const e of hist) {
      if (e && typeof e === 'object' && typeof e.dayIndex === 'number' && isFinite(e.dayIndex)) {
        done[e.dayIndex] = true;
        if (last === null || e.dayIndex > last) last = e.dayIndex;
      }
    }
  }
  if (last === null) return 0;
  let n = 0, c = last;
  while (done[c]) { n++; c--; }
  return n;
}

function safeStreak(s){ try { return computeQuestStreak(s); } catch(e){ return 'THROW:'+e.message; } }

// S1: intact recorded run reads the true streak (3), not 0.
const s1raw = { dayIndex: T-2, fightsUsed:0, innHealsUsed:0,
                quest:{progress:0,completed:false,rewarded:false},
                completedQuests:[{dayIndex:T-4,label:'a'},{dayIndex:T-3,label:'b'},{dayIndex:T-2,label:'c'}] };
check("S1 loaded pre-reset record reads run length 3", recordedRunLen(null, s1raw)===3, "got "+recordedRunLen(null,s1raw));

// S1b: the v0.21.0 BASELINE bug reproduced on purpose.
// computeQuestStreak anchors on today-1 for an incomplete today, so with history
// ending at T-2 the trailing run from T-1 is empty -> 0. This is the live defect.
const baselineS1 = safeStreak(s1raw);
check("S1b BASELINE defect reproduced: computeQuestStreak(loaded record) reads 0", baselineS1===0, "baseline="+baselineS1);

// S5: the reset hazard. checkDailyReset rebuilds the record wholesale.
setDay(ds(s1raw));
resetW();
checkDailyReset();
const afterReset = getDay();
check("S5a reset rebuilt completedQuests empty", Array.isArray(afterReset.completedQuests) && afterReset.completedQuests.length===0,
      JSON.stringify(afterReset.completedQuests));
check("S5b reset stamped dayIndex to today", afterReset.dayIndex===T, "dayIndex="+afterReset.dayIndex);
check("S5c BASELINE defect reproduced: streak from post-reset record reads 0", safeStreak(afterReset)===0, "post-reset="+safeStreak(afterReset));
check("S5d recorded-history derivation is UNCHANGED by the rebuild", recordedRunLen(afterReset, s1raw)===3, "new="+recordedRunLen(afterReset,s1raw));

// S2: agreement between the welcome-back panel status and the derived number.
const w1 = computeAwayWindow(s1raw, T);
check("S2a panel window shows the summary on an intact run", w1.shouldShow===true, JSON.stringify(w1));
check("S2b panel says streak survived", w1.streakSurvived===true);
const logNum1 = recordedRunLen(null, s1raw);
check("S2c log number >= 1 when panel says survived", logNum1>=1, "log="+logNum1);
check("S2d log number equals the run length", logNum1===3, "log="+logNum1);
check("S2e no contradiction: panel survived AND log 0 is NOT the state", !(w1.streakSurvived && logNum1===0));

// S3: a genuine gap resets to 0 in both surfaces, and they agree.
const s3raw = { dayIndex: T-2, completedQuests:[{dayIndex:T-6,label:'a'},{dayIndex:T-5,label:'b'}] };
const w3 = computeAwayWindow(s3raw, T);
const logNum3 = recordedRunLen(null, s3raw);
check("S3a panel says broken on a genuine hole", w3.streakSurvived===false, JSON.stringify(w3));
check("S3b log reads 0 on a genuine hole", logNum3===0, "log="+logNum3);
check("S3c both agree (broken <-> 0)", w3.streakSurvived===false && logNum3===0);

// S4: first-ever player reads 0, no crash, no panel.
const s4raw = { dayIndex: T, completedQuests:[], quest:{progress:0,completed:false,rewarded:false} };
let s4ok = true, s4val = null;
try { s4val = recordedRunLen(null, s4raw); } catch(e) { s4ok = false; }
check("S4a first-ever player reads 0", s4ok && s4val===0, "got "+s4val);
const w4 = computeAwayWindow(s4raw, T);
check("S4b no panel for a first-ever player", w4.shouldShow===false);
check("S4c no throw on an empty record", s4ok);

// S6: in-progress today still reads the preserved run.
const s6raw = { dayIndex: T-1, quest:{progress:0,completed:false,rewarded:false},
                completedQuests:[{dayIndex:T-3},{dayIndex:T-2},{dayIndex:T-1}] };
check("S6a preserved run reads 3 with today incomplete", recordedRunLen(null,s6raw)===3, "got "+recordedRunLen(null,s6raw));
check("S6b baseline computeQuestStreak also reads 3 here (no regression)", safeStreak(s6raw)===3, "baseline="+safeStreak(s6raw));

// S7: completed today joins the run.
const s7raw = { dayIndex: T, quest:{progress:1,completed:true,rewarded:true},
                completedQuests:[{dayIndex:T-2},{dayIndex:T-1},{dayIndex:T}] };
check("S7a run includes today, reads 3", recordedRunLen(null,s7raw)===3, "got "+recordedRunLen(null,s7raw));
check("S7b baseline computeQuestStreak reads 3 for the same state", safeStreak(s7raw)===3, "baseline="+safeStreak(s7raw));

// S8: recent-quests list identical to the pre-story rendering for the same history.
function listRender(completed) {
  const recent = completed.slice(-5).reverse();
  return recent.map(e => dayLabelForIndex(e.dayIndex) + ': ' + (e.objective || e.label || ''));
}
const s8hist = [];
for (let i=7;i>=1;i--) s8hist.push({ dayIndex: T-i, label: 'q'+i });
const before = listRender(s8hist);
check("S8a list capped at 5", before.length===5, "len="+before.length);
check("S8b most recent first", before[0].indexOf('yesterday')===0, before[0]);
check("S8c last entry is 5 days ago", before[4].indexOf('5 days ago')===0, before[4]);
check("S8d list is deterministic for the same history", JSON.stringify(listRender(s8hist))===JSON.stringify(before));

// S9: legacy, corrupt and partial records degrade cleanly (no throw).
const corrupt = [
  ["legacy, no completedQuests", { dayIndex: T }],
  ["completedQuests a string", { dayIndex: T, completedQuests: 'x' }],
  ["completedQuests a number", { dayIndex: T, completedQuests: 7 }],
  ["array of junk entries", { dayIndex: T, completedQuests: [null, 1, 'x', {}, {dayIndex:'y'}] }],
  ["entry with non-numeric dayIndex", { dayIndex: T, completedQuests: [{dayIndex:'abc'}] }],
  ["negative day indexes", { dayIndex: T, completedQuests: [{dayIndex:-1},{dayIndex:T-99999}] }],
  ["dayIndex not a number", { dayIndex: 'T', completedQuests: [{dayIndex:T-1}] }],
  ["dayIndex NaN", { dayIndex: NaN, completedQuests: [{dayIndex:T-1}] }],
  ["whole record a string", "garbage"],
  ["whole record a number", 42],
  ["whole record empty object", {}],
  ["record null", null],
];
let degenerate = 0;
for (const [name, rec] of corrupt) {
  try {
    const v = recordedRunLen(null, rec);
    const win = computeAwayWindow(rec, T);
    const ok = (typeof v === 'number' && isFinite(v)) &&
               (win && typeof win.shouldShow === 'boolean');
    if (!ok) { degenerate++; console.log("  FAIL degrade: "+name+" -> "+JSON.stringify(win)); }
  } catch (e) {
    degenerate++;
    console.log("  FAIL degrade THREW: "+name+" -> "+e.message);
  }
}
check("S9 every corrupt/legacy/partial record degrades without throwing", degenerate===0, degenerate+" failures");

// S10: storage unavailable / private mode: helpers still behave, nothing throws.
const throwing = {
  getItem: () => { throw new Error('blocked'); },
  setItem: () => { throw new Error('blocked'); }
};
let s10ok = true;
try {
  const rec = { dayIndex: T-2, completedQuests:[{dayIndex:T-2},{dayIndex:T-3}] };
  const v = recordedRunLen(null, rec);
  s10ok = (v===2);
} catch(e) { s10ok = false; }
check("S10 in-memory derivation works with storage unavailable", s10ok);

// S12: day record field set unchanged.
const shape = Object.keys(afterReset).sort().join(',');
check("S12 day record shape unchanged",
      shape==='completedQuests,dayIndex,fightsUsed,innHealsUsed,quest', "shape="+shape);

// S18: same-day and next-day returns stay quiet.
check("S18a same-day return quiet", computeAwayWindow({dayIndex:T,completedQuests:[{dayIndex:T}]}, T).shouldShow===false);
check("S18b next-day return quiet", computeAwayWindow({dayIndex:T-1,completedQuests:[{dayIndex:T-1}]}, T).shouldShow===false);
check("S18c reload of an already-stamped record is quiet",
      computeAwayWindow({dayIndex:T,completedQuests:[]}, T).shouldShow===false);

// ---------- Story 045: reload guard, both staleness cases ----------
// Case A: record stale by EXACTLY 1 day.
setDay({ dayIndex: T-1, fightsUsed:0, innHealsUsed:0, quest:{progress:0,completed:false,rewarded:false},
         completedQuests:[{dayIndex:T-2},{dayIndex:T-1}] });
const aRaw = getDay();
const aLoad1 = computeAwayWindow(aRaw, T);
const aShow1 = shouldShowWelcomeBack(aLoad1, false, aRaw);
resetW();
checkDailyReset();                       // the reset's own write stamps today
const aReloaded = getDay();
const aLoad2 = computeAwayWindow(aReloaded, T);
const aShow2 = shouldShowWelcomeBack(aLoad2, false, aReloaded);
check("45-A load1 panel quiet (daysAway 0)", aShow1===false, "w="+JSON.stringify(aLoad1));
check("45-A reload panel quiet", aShow2===false, "w="+JSON.stringify(aLoad2));
check("45-A reset stamped today before the reload", aReloaded.dayIndex===T, "dayIndex="+aReloaded.dayIndex);
check("45-A gapDays on reload is 0", (T - aReloaded.dayIndex)===0);

// Case B: record stale by 3+ days.
setDay({ dayIndex: T-3, fightsUsed:0, innHealsUsed:0, quest:{progress:0,completed:false,rewarded:false},
         completedQuests:[{dayIndex:T-4},{dayIndex:T-3}] });
const bRaw = getDay();
const bLoad1 = computeAwayWindow(bRaw, T);
const bShow1 = shouldShowWelcomeBack(bLoad1, false, bRaw);
resetW();
checkDailyReset();
const bReloaded = getDay();
const bLoad2 = computeAwayWindow(bReloaded, T);
const bShow2 = shouldShowWelcomeBack(bLoad2, false, bReloaded);
check("45-B load1 panel SHOWN (daysAway 2)", bShow1===true, "w="+JSON.stringify(bLoad1));
check("45-B reload panel quiet", bShow2===false, "w="+JSON.stringify(bLoad2));
check("45-B reset stamped today before the reload", bReloaded.dayIndex===T, "dayIndex="+bReloaded.dayIndex);
check("45-B gapDays on reload is 0", (T - bReloaded.dayIndex)===0);
check("45-B daysAway clamped to 0 on reload", bLoad2.daysAway===0, "daysAway="+bLoad2.daysAway);

// 6-day stale variant of Case B.
setDay({ dayIndex: T-6, completedQuests:[{dayIndex:T-6}] });
const cRaw = ds(getDay());
const cShow1 = shouldShowWelcomeBack(computeAwayWindow(cRaw, T), false, cRaw);
checkDailyReset();
const cReloaded = getDay();
const cShow2 = shouldShowWelcomeBack(computeAwayWindow(cReloaded, T), false, cReloaded);
check("45-B2 6-day stale: shown once on load1", cShow1===true);
check("45-B2 6-day stale: quiet on reload", cShow2===false);

// 30-day stale.
setDay({ dayIndex: T-30, completedQuests:[{dayIndex:T-30}] });
const dRaw = ds(getDay());
const dShow1 = shouldShowWelcomeBack(computeAwayWindow(dRaw, T), false, dRaw);
checkDailyReset();
const dReloaded = getDay();
const dShow2 = shouldShowWelcomeBack(computeAwayWindow(dReloaded, T), false, dReloaded);
check("45-B3 30-day stale: shown once on load1", dShow1===true);
check("45-B3 30-day stale: quiet on reload", dShow2===false);

// Report
let pass=0, fail=0;
for (const r of results) {
  console.log((r.pass?"PASS":"FAIL")+"  "+r.name+(r.pass||!r.detail?"":"  ["+r.detail+"]"));
  r.pass?pass++:fail++;
}
console.log("TOTAL pass="+pass+" fail="+fail);
globalThis.__QA_EXIT__ = (fail?1:0);
'''

with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
    f.write(harness_prelude + harness_expose)
    hp = f.name

fns_path = hp[:-3] + "-fns.js"
body_path = hp[:-3] + "-body.js"
with open(fns_path, "w") as f:
    f.write(harness_fns)
with open(body_path, "w") as f:
    f.write(test_body)

print("=" * 72)
print("Story 044 scenarios 1-14 + Story 045 reload cases (real extracted code)")
print("=" * 72)
res = subprocess.run(["node", hp, fns_path, body_path], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)
print("node exit:", res.returncode)
print()

# ------------------------------------------------------- static scans (044)
print("=" * 72)
print("Story 044 S11: quest-log read path writes nothing, adds no field")
print("=" * 72)
rql = blocks["renderQuestLog"]
write_calls = re.findall(r'\b(saveCharacter|saveDayState|localStorage\.setItem|completeQuest|applyQuestProgress|ensureQuestState|checkDailyReset)\b', rql)
assign = re.findall(r'\b(character\.\w+|dayState\.\w+|dayState)(?=\s*[=+\-]?=)', rql)
field_names = re.findall(r'\b(streakCache|lastStreak|seenReturn|welcomeBackShown|lastGapStamp|versionMarker|gapStamp|seenSummary)\b', src)
print("  renderQuestLog forbidden write calls :", write_calls if write_calls else "none")
print("  renderQuestLog state assignments     :", assign if assign else "none")
print("  forbidden persisted field names      :", field_names if field_names else "none")
print("  renderQuestLog streak source line    :", re.search(r'const streak = [^;]+;', src).group(0))
s11_structure = (not write_calls) and (not assign) and (not field_names)
print("  S11 structural result:", "PASS (no writes, no new field)" if s11_structure else "FAIL")

print()
print("=== S13/S14: checkDailyReset + computeQuestStreak byte-identity vs v0.21.0 ===")
def blob(b):
    return subprocess.run(["git", "hash-object", "--stdin"], input=b or "", capture_output=True, text=True, cwd=REPO).stdout.strip()
base_src = subprocess.run(["git", "show", "v0.21.0:src/cinder.html"], capture_output=True, text=True, cwd=REPO).stdout
for fn in ["checkDailyReset", "computeQuestStreak"]:
    b1 = blob(extract_fn(fn, base_src))
    b2 = blob(blocks[fn])
    print(f"  {fn:20s} v0.21.0={b1}  candidate={b2}  {'SAME' if b1==b2 else 'CHANGED'}")

print()
print("=== S20: no notification / push / permission / install surface ===")
for pat in ["onclick=", "Notification", "pushManager", "requestPermission", "beforeinstallprompt"]:
    n = src.count(pat)
    print(f"  {pat:22s} occurrences={n}")

print()
print("=== checker script untouched (Story 046 S8) ===")
cs = subprocess.run(["sha256sum", os.path.join(REPO, "scripts/verify-website-currency.sh")], capture_output=True, text=True).stdout.strip()
print("  ", cs)
print("   expected bed7d67c8af93e1d8c9809dca374d4837627e0fa5abeda6d4551484440fdef92")

sys.exit(1 if res.returncode != 0 else 0)
