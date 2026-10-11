#!/usr/bin/env python3
"""
Afterglow daily-seed proof harness (Story 064, Session 30, Kai scope).

Executes the REAL extracted pure logic from src/afterglow.html in Node. It does
not re-implement the generator; it pulls the marked AFTERGLOW-PURE block out of
the shipped file and runs it. That is what makes a green exit a claim about the
product rather than about a copy of the product.

Contract under test (Story 064):
  dayIndex = Math.floor(Date.now() / 86400000), the UTC-day index the other
  daily games use. Daily mode calls generateLevel(seed, index) with the
  day-derived seed. The generator itself is unchanged from Story 059.

Two targets, both mandatory:

  Run 1, pre-064 tree   : no daily entry point (no dailySeedForDay in the pure
                          block, no 86400000 day-index derivation).
                          MUST exit 1. The behaviour does not exist there.
  Run 2, merged candidate: daily entry point present, same day index yields a
                          deep-equal level sequence, a different day yields a
                          different one. MUST exit 0.

A harness that passes on both targets has proven nothing. Measured failure on
the pre-064 tree is the point of run 1: keep it, do not edit it away.

Seed source rule: when the pure block defines dailySeedForDay, the harness
calls the PRODUCT's function. Only when it is absent does the harness fall back
to the canonical derivation for the generator-readiness demonstration, and the
entry-point failure still forces exit 1.

Usage:
  python3 dev/afterglow-daily-proof.py [/path/to/flambeee]
"""

import json
import os
import re
import subprocess
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/jake/.hermes/flambeee/flambeee"
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
print("Afterglow daily-seed proof (Story 064) -- target: %s" % SRC)
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

# --- entry-point probe: the run-1 finding lives here ------------------------
print("daily entry-point probe (source scan)")
has_pure_fn = re.search(r"function\s+dailySeedForDay\s*\(", pure) is not None
has_day_index = "86400000" in source
print("  pure dailySeedForDay : %s" % ("PRESENT" if has_pure_fn else "ABSENT"))
print("  86400000 derivation  : %s" % ("PRESENT" if has_day_index else "ABSENT"))
check(has_pure_fn, "pure block exposes dailySeedForDay(dayIndex)",
      "no daily entry point on this tree")
check(has_day_index, "file derives the UTC day index (Date.now() / 86400000)",
      "no day-index derivation on this tree")
print("")

# --- purity guard: the AFTERGLOW-PURE block stays pure (Story 064, req 2) ----
print("purity guard (source scan)")
code_only = re.sub(r"/\*.*?\*/", "", pure, flags=re.S)
code_only = re.sub(r"//[^\n]*", "", code_only)
dom_refs = []
for pat in (r"document\.", r"(?<![A-Za-z])window\.",
            r"localStorage", r"setTimeout\s*\(", r"setInterval\s*\("):
    if re.search(pat, code_only):
        dom_refs.append(pat)
check(not dom_refs, "pure block has no DOM/storage/timer references",
      "matched %r" % dom_refs)
print("")

harness = pure + r"""
function deepEqual(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

// FNV-1a over the JSON form: a short quotable level/sequence signature.
function sig(obj) {
  var s = JSON.stringify(obj);
  var h = 2166136261;
  for (var i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ('0000000' + (h >>> 0).toString(16)).slice(-8);
}

let failures = [];
function check(ok, name, detail) {
  if (ok) { console.log('  PASS  ' + name); }
  else { failures.push(name); console.log('  FAIL  ' + name + (detail ? '  -- ' + detail : '')); }
}

var usesProductSeed = (typeof dailySeedForDay === 'function');
function seedForDay(d) {
  if (usesProductSeed) return dailySeedForDay(d);
  return 'afterglow-daily:' + String(d >>> 0); // canonical fallback, absence already fails
}
console.log('seed source: ' + (usesProductSeed ? 'PRODUCT dailySeedForDay' : 'harness-canonical (no product entry point)'));

var DAY_A = Math.floor(Date.now() / 86400000); // today, UTC
var DAY_B = DAY_A + 1;                          // tomorrow, UTC
var NLEVELS = 4;
function dailySeq(day) {
  var out = [];
  for (var i = 0; i < NLEVELS; i++) out.push(generateLevel(seedForDay(day), i));
  return out;
}

console.log('');
console.log('Story 064 AC-1  same UTC day, same sequence');
var seqA1 = dailySeq(DAY_A);
var seqA2 = dailySeq(DAY_A);
check(deepEqual(seqA1, seqA2), 'same day index -> deep-equal sequence',
  'two runs on one day differ');
var seqB = dailySeq(DAY_B);
check(!deepEqual(seqA1, seqB), 'different day index -> different sequence',
  'two days produced the same sequence');
check(seedForDay(DAY_A) === seedForDay(DAY_A), 'day seed is deterministic');
check(seedForDay(DAY_A) !== seedForDay(DAY_B), 'day seed is day-sensitive',
  'adjacent days share a seed');
console.log('');
console.log('  day indices quoted: DAY_A=' + DAY_A + ' DAY_B=' + DAY_B);
console.log('  seeds quoted: ' + JSON.stringify(seedForDay(DAY_A)) + ' vs ' + JSON.stringify(seedForDay(DAY_B)));
console.log('  level-0 signatures quoted: ' + sig(seqA1[0]) + ' vs ' + sig(seqB[0]));
console.log('  4-level sequence signatures quoted: ' + sig(seqA1) + ' vs ' + sig(seqB));
console.log('');

if (failures.length) {
  console.log('RESULT: ' + failures.length + ' failure(s): ' + failures.join(', '));
  process.exit(1);
}
console.log('RESULT: daily determinism holds');
process.exit(0);
"""

# --- run the real extracted functions in Node -------------------------------
print("running the extracted pure block in Node...")
print("-" * 72)
sys.stdout.flush()
mjs_path = "/home/jake/.hermes/cache/scratch/afterglow_daily_proof.mjs"
with open(mjs_path, "w", encoding="utf-8") as fh:
    fh.write(harness)

result = subprocess.run(["node", mjs_path])
print("-" * 72)

if result.returncode != 0:
    failures.append("node-daily-determinism")

if failures:
    print("")
    print("RESULT: %d failure(s): %s" % (len(failures), ", ".join(failures)))
    print("exit 1")
    sys.exit(1)

print("")
print("RESULT: daily entry point present and deterministic on %s" % SRC)
print("exit 0")
sys.exit(0)
