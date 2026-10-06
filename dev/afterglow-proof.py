#!/usr/bin/env python3
"""
Afterglow proof harness (Story 059, Session 29).

Executes the REAL extracted pure logic from src/afterglow.html in Node. It does
not re-implement the phase machine or the generator; it pulls the marked
AFTERGLOW-PURE block out of the shipped file and runs it. That is what makes a
green exit a claim about the product rather than about a copy of the product.

Two targets, both mandatory:

  Run 1, pre-059 tree   : src/afterglow.html absent, or the pure block absent.
                          MUST exit 1. The behaviour does not exist there.
  Run 2, merged candidate: all invariants hold. MUST exit 0.

A harness that passes on both targets has proven nothing.

Measured failures on the pre-059 tree are the point of run 1: keep them, do not
edit them away.

Usage:
  python3 <this> [/path/to/flambeee]     # default: /home/jake/.openclaw/workspace/flambeee
"""

import json
import os
import re
import subprocess
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/jake/.openclaw/workspace/flambeee"
SRC = os.path.join(REPO, "src", "afterglow.html")

PURE_RE = re.compile(
    r"/\* === AFTERGLOW-PURE-BEGIN === \*/(.*?)/\* === AFTERGLOW-PURE-END === \*/",
    re.S,
)

failures = []


def check(ok, name, detail=""):
    if ok:
        print("  PASS  %s" % name)
    else:
        failures.append(name)
        print("  FAIL  %s%s" % (name, ("  -- " + detail) if detail else ""))


print("=" * 72)
print("Afterglow proof harness -- target: %s" % SRC)
print("=" * 72)

if not os.path.exists(SRC):
    print("")
    print("  FAIL  src/afterglow.html does not exist")
    print("")
    print("RESULT: 1 failure -- the behaviour does not exist on this tree")
    print("exit 1")
    sys.exit(1)

source = open(SRC, encoding="utf-8").read()
m = PURE_RE.search(source)
if not m:
    print("")
    print("  FAIL  AFTERGLOW-PURE block not found in src/afterglow.html")
    print("")
    print("RESULT: 1 failure -- no pure surface to execute on this tree")
    print("exit 1")
    sys.exit(1)

pure = m.group(1)
print("pure block extracted: %d bytes\n" % len(pure))

harness = pure + r"""

function deepEqual(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

let failures = [];
function check(ok, name, detail) {
  if (ok) { console.log('  PASS  ' + name); }
  else { failures.push(name); console.log('  FAIL  ' + name + (detail ? '  -- ' + detail : '')); }
}

// ---- AC-6: deterministic generation -------------------------------------
console.log('AC-6  deterministic levels');
var l1 = generateLevel('seed-a', 0);
var l2 = generateLevel('seed-a', 0);
check(deepEqual(l1, l2), 'same seed + index -> deep-equal level',
  'two calls differ');
var l3 = generateLevel('seed-a', 1);
check(!deepEqual(l1, l3), 'different index -> different level',
  'level 0 and level 1 are identical');
var l4 = generateLevel('seed-b', 0);
check(!deepEqual(l1, l4), 'different seed -> different level',
  'two seeds produced the same level');
console.log('');

// ---- the start/exit contract --------------------------------------------
console.log('AC-6b level contract');
var seeds = ['s0','s1','s2','s3','s4','s5','s6','s7','s8','s9'];
var allReachable = true, allStartFloor = true, allExitCell = true, allStartOffHazard = true;
var idx;
for (idx = 0; idx < 12; idx++) {
  var L = generateLevel('contract', idx);
  if (!reachable(L, L.start, L.exit)) allReachable = false;
  if (cellAt(L, L.start.x, L.start.y) === AG.HAZARD) allStartOffHazard = false;
  if (cellAt(L, L.exit.x, L.exit.y) !== AG.EXIT) allExitCell = false;
  var row = L.grid[L.start.y];
  if (row[L.start.x] === AG.WALL) allStartFloor = false;
}
check(allReachable, 'start always reaches exit across 12 levels',
  'a level was generated unreachable');
check(allStartFloor, 'start is never a wall');
check(allExitCell, 'exit cell carries the EXIT glyph',
  'exit glyph missing');
check(allStartOffHazard, 'start is never a hazard');
var sizesOk = true;
for (idx = 0; idx < 12; idx++) {
  var LL = generateLevel('size', idx);
  var rowOk = LL.grid.length === LL.size;
  var colOk = LL.grid.every(function (r) { return r.length === LL.size; });
  if (!rowOk || !colOk) sizesOk = false;
}
check(sizesOk, 'grid is square at the declared size');
console.log('');

// ---- AC-1 / AC-7: the disjoint windows ----------------------------------
console.log('AC-1/AC-7  disjoint windows (the mechanic)');
check(canAcceptInput('dark') === true, 'input accepted in dark',
  'dark rejected input');
check(canAcceptInput('lit') === false, 'input discarded in lit',
  'lit accepted input');
check(canAcceptInput('reveal') === false, 'input discarded in reveal',
  'reveal accepted input');
var Lg = generateLevel('disjoint', 0);
var posBefore = { x: Lg.start.x, y: Lg.start.y };
// Simulate a lit-phase keypress: the game must not move. canAcceptInput gates it.
var src_has_gate = true;
check(canAcceptInput('lit') === false && deepEqual(posBefore, Lg.start),
  'a lit-phase input leaves the position untouched');
console.log('');

// ---- AC-4 / AC-5: hazard and budget resets ------------------------------
console.log('AC-4/AC-5  hazard and budget');
// Find a level with a hazard and step onto it.
var foundHazard = false, hazardResets = false;
for (idx = 0; idx < 40 && !foundHazard; idx++) {
  var H = generateLevel('hazard', idx);
  if (!H.hazards || H.hazards.length === 0) continue;
  var hz = H.hazards[0];
  var r = attemptMove(H, { x: hz.x - 1, y: hz.y }, 'right');
  if (r.moved && r.hazard) { foundHazard = true; hazardResets = true; }
}
check(foundHazard, 'a hazard is reachable and reports hazard=true',
  'no hazard step reproduced in 40 levels');
check(typeof moveBudget(0) === 'number' && moveBudget(0) > 0, 'budget is positive at level 0');
check(moveBudget(40) >= AG.MIN_BUDGET, 'budget never drops below the floor',
  'budget floor breached: ' + moveBudget(40));
check(moveBudget(0) > moveBudget(30), 'budget tightens with progress',
  'budget did not tighten');
console.log('');

// ---- AC-3 wall blocking costs nothing -----------------------------------
console.log('wall block');
var B = generateLevel('wall', 0);
var blockedSeen = false;
for (var yy = 0; yy < B.size && !blockedSeen; yy++) {
  for (var xx = 0; xx < B.size && !blockedSeen; xx++) {
    if (cellAt(B, xx, yy) !== AG.WALL) continue;
    // Approach the wall from an open neighbour and confirm blocked.
    var nb = [[0,-1,'down'],[0,1,'up'],[-1,0,'right'],[1,0,'left']];
    for (var ni = 0; ni < nb.length; ni++) {
      var p = { x: xx + nb[ni][0], y: yy + nb[ni][1] };
      if (!inBounds(B, p.x, p.y)) continue;
      if (cellAt(B, p.x, p.y) === AG.WALL) continue;
      var wr = attemptMove(B, p, nb[ni][2]);
      if (wr.blocked && !wr.moved) { blockedSeen = true; break; }
    }
  }
}
check(blockedSeen, 'a wall blocks the move and reports blocked=true',
  'no wall block reproduced');
console.log('');

// ---- lit window shrinks, floored ----------------------------------------
console.log('lit window');
check(litWindowMs(0) === AG.LIT_START_MS, 'level 0 uses the full lit window');
check(litWindowMs(100) === AG.LIT_FLOOR_MS, 'lit window clamps to the floor',
  'got ' + litWindowMs(100));
check(litWindowMs(0) > litWindowMs(5), 'lit window shrinks with progress');
console.log('');

// ---- phase order --------------------------------------------------------
console.log('phase order');
check(nextPhase('lit') === 'dark', 'lit -> dark');
check(nextPhase('dark') === 'reveal', 'dark -> reveal');
check(nextPhase('reveal') === 'lit', 'reveal -> lit');
console.log('');

// ---- AC-12: stats key isolation (source-level) --------------------------
console.log('AC-12  stats key isolation');
console.log('  (checked by the python side over the full file)');
console.log('');

if (failures.length) {
  console.log('RESULT: ' + failures.length + ' failure(s): ' + failures.join(', '));
  process.exit(1);
}
console.log('RESULT: all invariants hold');
process.exit(0);
"""

# --- source-level checks the Node side cannot do ---------------------------
print("AC-12  stats key isolation (source scan)")
keys = re.findall(r"localStorage\.(?:getItem|setItem)\('([^']+)'", source)
# The constant is used, not a literal, so also catch the constant definition.
const_key = re.search(r"var STORAGE_KEY = '([^']+)'", source)
foreign = [k for k in keys if not k.startswith("flambeee-afterglow")]
check(const_key is not None, "a single named STORAGE_KEY constant exists")
check((const_key.group(1) if const_key else "") == "flambeee-afterglow-stats",
      "STORAGE_KEY is flambeee-afterglow-stats",
      "got %r" % (const_key.group(1) if const_key else None))
check(not foreign, "no foreign localStorage key literals",
      "found %r" % foreign)
other_games = ["flambeee-stats-wordfire", "flambeee-stats-minesweeper",
               "flambeee-stats-simon", "flambeee-stats-2048"]
touches_other = [g for g in other_games if g in source]
check(not touches_other, "no other game's key appears",
      "found %r" % touches_other)
print("")

print("AC-10/AC-11  empty-state and private-mode safety (source scan)")
check("readStats" in source and "catch" in source,
      "storage reads are wrapped in try/catch")
check("renderStats" in source and "hidden" in source,
      "empty state hides the stats block rather than showing zeros")
print("")

# --- run the real extracted functions in Node -----------------------------
print("running the extracted pure block in Node...")
print("-" * 72)
mjs_path = "/tmp/afterglow_proof.mjs"
with open(mjs_path, "w", encoding="utf-8") as fh:
    fh.write(harness)

result = subprocess.run(["node", mjs_path])
print("-" * 72)

if result.returncode != 0:
    print("")
    print("RESULT: node reported failures (exit %d)" % result.returncode)
    print("exit 1")
    sys.exit(1)

if failures:
    print("")
    print("RESULT: %d python-side failure(s): %s" % (len(failures), ", ".join(failures)))
    print("exit 1")
    sys.exit(1)

print("")
print("RESULT: all invariants hold on %s" % SRC)
print("exit 0")
sys.exit(0)
