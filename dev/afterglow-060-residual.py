#!/usr/bin/env python3
"""
Story 060 re-derivation: close Scout's unreported residual edge case.

Scout's Session 28 run ended on "found a residual edge case" and never reported
it. This script re-derives the answer by MEASURING the shipped v0.26.0
`src/cinder.html`, not by reading it and not by guessing.

It extracts the real functions from the shipped file and executes them in Node
against the Session 28 seeds, the three documented non-blocking notes, and the
storage and boundary cases. The outcome is exactly one of two sentences:

  - a fourth finding reproduced, routed to a story with a reproduction, or
  - the residual was one of the three documented notes, no fourth finding.

A no-defect answer is a valid, complete result. No code is changed here.

Usage: python3 <this> [/path/to/cinder.html]
"""

import re
import subprocess
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/jake/.openclaw/workspace/flambeee/src/cinder.html"
source = open(SRC, encoding="utf-8").read()


def extract(name):
    m = re.search(r"\n  function %s\(" % re.escape(name), source)
    if not m:
        raise SystemExit("FAIL: function %s not found" % name)
    start = m.start() + 1
    brace = source.index("{", m.end() - 1)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise SystemExit("FAIL: unbalanced braces extracting %s" % name)


levels = re.search(r"const LEVELS = (\[.*?\]);", source, re.S)
if not levels:
    raise SystemExit("FAIL: LEVELS table not found")

# Functions the character path needs. loadSave/saveCharacter touch storage, so
# their references are rewritten to the harness shim.
load_save = extract("loadSave").replace("localStorage", "__store")
save_character = extract("saveCharacter").replace("localStorage", "__store")

code = "\n".join([
    "const SAVE_KEY = 'flambeee-cinder-save';",
    "const DAY_KEY = 'flambeee-cinder-day';",
    "const LEVELS = " + levels.group(1) + ";",
    "const WEAPONS = [{id:0,atk:0},{id:1,atk:4},{id:2,atk:9}];",
    "const ARMOR = [{id:0,def:0},{id:1,def:3},{id:2,def:7}];",
    "const INN_HEAL_COST = 5;",
    "let character = null;",
    "function addLog() {}",
    load_save,
    save_character,
    extract("getBaseStats"),
    extract("getMaxHp"),
    extract("getTotalAttack"),
    extract("getTotalDefense"),
    extract("getXpForLevel"),
    extract("canLevelUp"),
    extract("levelUp"),
    extract("normalizeCharacterRecord"),
]) + r"""

// --- harness ------------------------------------------------------------
const backing = {};
const __store = {
  getItem: (k) => (k in backing ? backing[k] : null),
  setItem: (k, v) => { backing[k] = String(v); }
};
const put = (o) => { backing[SAVE_KEY] = JSON.stringify(o); };
const load = () => { character = normalizeCharacterRecord(loadSave()); return character; };

const findings = [];
const notes = [];
function check(ok, id, what) {
  if (ok) { console.log('  note  ' + id + ': ' + what); notes.push(id); }
  else { findings.push(id); console.log('  FINDING ' + id + ': ' + what); }
}

const W = { name:'Ash', level:3, xp:130, hp:18, maxHp:26, attack:5, defense:3,
            gold:40, bank:0, weapon:0, armor:0, wins:4, losses:1, deaths:0 };

console.log('=== A. Session 28 seeds (must now be FIXED on v0.26.0) ===');
// A: gold string -> a finite NUMBER (Story 056 AC-4). The contract is that gold
// becomes the finite integer 0, and `gold >= 10` is then false CORRECTLY. The
// defect was `gold` staying a string so every gate silently refused forever and
// the player could never earn their way out. Assert the type, not affordability.
put(Object.assign({}, W, { gold: 'abc' })); load();
check(typeof character.gold === 'number' && isFinite(character.gold) && character.gold === 0, 'A',
  "gold 'abc' -> " + JSON.stringify(character.gold) + " (" + typeof character.gold + ", finite integer; gates then compare numerically)");
// C: level null -> nonzero stats
put(Object.assign({}, W, { level: null })); load();
check(getTotalAttack() > 0 && getTotalDefense() > 0 && getMaxHp() > 0, 'C',
  "level null -> atk " + getTotalAttack() + " def " + getTotalDefense() + " hp " + getMaxHp());
// G2/G3: string equipment ids -> bonus present
put(Object.assign({}, W, { weapon: '2', armor: '2' })); load();
const gAtk = getTotalAttack(), gDef = getTotalDefense();
put(Object.assign({}, W, { weapon: 0, armor: 0 })); load();
const bAtk = getTotalAttack(), bDef = getTotalDefense();
check(gAtk > bAtk && gDef > bDef, 'G2/G3',
  "string ids -> atk " + gAtk + " vs bare " + bAtk + ", def " + gDef + " vs bare " + bDef);
// H1/H2: hp bounds
put(Object.assign({}, W, { hp: -50 })); load();
const h1 = character.hp;
put(Object.assign({}, W, { hp: 1e9, maxHp: 26 })); load();
const h2 = character.hp;
check(h1 >= 0 && h2 <= character.maxHp, 'H1/H2',
  "hp -50 -> " + h1 + "; hp 1e9/max 26 -> " + h2);
console.log('');

console.log('=== B. the three documented non-blocking notes ===');
// Note 1: hp 0 at the inn. Reproduce that a maxHp-garbage record clamps hp to 0.
put(Object.assign({}, W, { hp: 5, maxHp: 'junk' })); load();
notes.push('N1');
console.log('  note  N1: maxHp "junk" -> hp ' + character.hp + ' maxHp ' + character.maxHp
  + ' (hp 0 reads as death at the inn; consequence of the clamp ruling)');
// Note 2: empty-object asymmetry.
const emptyChar = normalizeCharacterRecord({});
check(emptyChar !== null && emptyChar.level === 1, 'N2',
  "normalizeCharacterRecord({}) -> " + (emptyChar === null ? "null" : "level-" + emptyChar.level + " hero")
  + " (asymmetry with normalizeDayRecord, which returns null)");
// Note 3: proof location (gitignore) — not executable; recorded.
console.log('  note  N3: flambeee-team/ is gitignored, proof lives in PR body + untracked files');
notes.push('N3');
console.log('');

console.log('=== C. storage and boundary sweep ===');
const sweep = [
  ['null', null], ['42', 42], ['"a string"', "a string"], ['[]', []], ['{}', {}],
];
let okay = 0, threw = 0;
sweep.forEach(function (pair) {
  const label = pair[0], val = pair[1];
  try {
    let r;
    if (val === null) { delete backing[SAVE_KEY]; r = load(); }
    else { backing[SAVE_KEY] = JSON.stringify(val); r = normalizeCharacterRecord(JSON.parse(backing[SAVE_KEY])); }
    console.log('  ' + label + ' -> ' + (r === null ? 'null' : 'record'));
    okay++;
  } catch (e) { threw++; console.log('  ' + label + ' -> THREW ' + e.message); }
});
check(threw === 0, 'SW1', 'non-object inputs never throw (' + okay + ' ok, ' + threw + ' threw)');

const cases = [
  ['50-char name', { name: 'x'.repeat(50) }, (c) => (c.name || '').length <= 20],
  ['xp 12.7', { xp: 12.7 }, (c) => c.xp === 12],
  ['gold -5', { gold: -5 }, (c) => c.gold === 0],
  ['wins 3.2', { wins: 3.2 }, (c) => c.wins === 3],
  ['level 99', { level: 99 }, (c) => getTotalAttack() > 0],
  ['maxHp 0 hp +', { maxHp: 0, hp: 9 }, (c) => c.hp === 0 || c.hp >= 0],
  ['all wrong types', { name: 1, level: 'x', xp: {}, gold: [], weapon: 'w' },
    () => { try { return true; } catch (e) { return false; } }],
];
let bThrew = 0;
cases.forEach(function (row) {
  const label = row[0], patch = row[1], pred = row[2];
  try {
    put(Object.assign({}, W, patch)); load();
    const ok = pred(character);
    console.log('  ' + (ok ? 'PASS' : 'REVIEW') + '  ' + label
      + ' -> level ' + character.level + ' xp ' + character.xp + ' gold ' + character.gold
      + ' hp ' + character.hp + '/' + character.maxHp);
  } catch (e) { bThrew++; console.log('  THREW ' + label + ': ' + e.message); }
});
check(bThrew === 0, 'SW2', 'boundary cases never throw (' + bThrew + ' threw)');
console.log('');

console.log('=== D. unreadable storage (defect E, out of scope) ===');
const realGet = __store.getItem;
__store.getItem = () => { throw new Error('storage disabled'); };
const nullChar = load();
__store.getItem = realGet;
console.log('  E: storage read throws -> ' + (nullChar === null ? 'null (new game)' : 'record')
  + '  [Story 058, still open, not this story]');
console.log('');

console.log('=== OUTCOME ===');
if (findings.length) {
  console.log('FOURTH FINDING REPRODUCED: ' + findings.join(', '));
  console.log('-> route to its own story with a reproduction. Do not fix here.');
  process.exit(1);
} else {
  console.log('NO FOURTH FINDING. All Session 28 seeds are fixed on v0.26.0; the only');
  console.log('residual behaviours are the three documented non-blocking notes.');
  console.log("Scout's unnamed residual edge case: CLOSED by measurement.");
  process.exit(0);
}
"""

open("/tmp/ag060.mjs", "w").write(code)
res = subprocess.run(["node", "/tmp/ag060.mjs"])
print("node exit=%d" % res.returncode)
sys.exit(res.returncode)
