#!/usr/bin/env python3
"""Kai pure-mirror proof for Story 037 (Cinder install-aware app-icon badge).

Verifies from the shipped src/cinder.html that:
  1. syncAppBadge() computes the badge value from quest state alone:
       1  when today's quest is not completed,
       1  when completed but not yet rewarded (payout-once gate),
       0  when completed AND rewarded.
  2. The missing-API invocation path returns without throwing: a navigator with
     no Badging API, a navigator whose setAppBadge rejects, and a navigator
     whose setAppBadge throws synchronously.
  3. The badge path is a pure reader: no saveCharacter, no saveDayState, no
     localStorage.setItem, no ensureQuestState, no completeQuest, no
     applyQuestProgress, no Notification, no pushManager, and no assignment to
     character./dayState.
  4. getQuestState is stubbed in the sandbox so the extraction proves a read of
     quest state; a forbidden-write token inside syncAppBadge fails the proof.

Run:
  node src/kai-story037-badge-proof.js     (self-extracting, writes a temp file)

  Or directly:
  .venv/bin/python3 src/kai-story037-badge-proof.py
Exit code 0 = all checks pass. Non-zero = proof failed.
"""
import os
import re
import subprocess
import sys
import tempfile

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cinder.html")

PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');

const SRC_PATH = %(src)r;
const src = fs.readFileSync(SRC_PATH, 'utf8');

// --- extract a top-level function body verbatim by brace matching ---
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

const badgeBody = extract('syncAppBadge');

// --- static scan: forbidden write tokens inside the exact badge body ---
const FORBIDDEN = [
  'saveCharacter', 'saveDayState', 'localStorage', 'setItem',
  'ensureQuestState', 'completeQuest', 'applyQuestProgress',
  'Notification', 'pushManager', 'serviceWorker', 'requestPermission'
];
let failures = [];
function check(cond, msg) {
  if (cond) { console.log('PASS: ' + msg); }
  else { failures.push(msg); console.log('FAIL: ' + msg); }
}

console.log('=== Static scan: syncAppBadge body (pure mirror) ===');
FORBIDDEN.forEach(function (tok) {
  check(badgeBody.indexOf(tok) < 0, 'no forbidden token in syncAppBadge: ' + tok);
});
check(!/(^|[^.\w])(character|dayState)\s*\.\s*\w+\s*[+\-*/]?=/.test(badgeBody),
      'no assignment to character./dayState. in syncAppBadge');
check(/getQuestState\s*\(/.test(badgeBody),
      'badge value derived from getQuestState() (single source of truth)');
check(/\.catch\s*\(\s*function\s*\(\s*\)\s*\{\s*\}\s*\)/.test(badgeBody),
      'setAppBadge/clearAppBadge promise has .catch(function () {})');
check(/typeof\s+[\w.]*setAppBadge\s*===\s*'function'/.test(badgeBody),
      'feature-detects navigator.setAppBadge');
check(/typeof\s+[\w.]*clearAppBadge\s*===\s*'function'/.test(badgeBody),
      'feature-detects navigator.clearAppBadge');
check(/try\s*\{/.test(badgeBody) && /catch\s*\(/.test(badgeBody),
      'call wrapped in try/catch');

// --- build a sandbox and exercise the real shipped helper ---
function makeSandbox(quest, nav) {
  const ctx = {
    console: console,
    getQuestState: function () { return quest; }
  };
  if (nav !== undefined) ctx.navigator = nav;
  vm.createContext(ctx);
  vm.runInContext(badgeBody, ctx);
  return ctx;
}

console.log('');
console.log('=== Behavioural proof: badge value from quest state ===');

// Scenario 8 (P1): incomplete -> 1
(function () {
  const calls = [];
  const ctx = makeSandbox({ progress: 0, completed: false, rewarded: false },
    { setAppBadge: function (v) { calls.push(['set', v]); return Promise.resolve(); },
      clearAppBadge: function () { calls.push(['clear']); return Promise.resolve(); } });
  ctx.syncAppBadge();
  check(calls.length === 1 && calls[0][0] === 'set' && calls[0][1] === 1,
        'S1 incomplete quest -> setAppBadge(1) [got ' + JSON.stringify(calls) + ']');
})();

// Scenario 8 (P1): completed but NOT rewarded -> still pending, 1
(function () {
  const calls = [];
  const ctx = makeSandbox({ progress: 3, completed: true, rewarded: false },
    { setAppBadge: function (v) { calls.push(['set', v]); return Promise.resolve(); },
      clearAppBadge: function () { calls.push(['clear']); return Promise.resolve(); } });
  ctx.syncAppBadge();
  check(calls.length === 1 && calls[0][0] === 'set' && calls[0][1] === 1,
        'S8 completed-but-unrewarded -> setAppBadge(1) [got ' + JSON.stringify(calls) + ']');
})();

// Scenario 2 (P1): completed AND rewarded -> 0 (cleared)
(function () {
  const calls = [];
  const ctx = makeSandbox({ progress: 3, completed: true, rewarded: true },
    { setAppBadge: function (v) { calls.push(['set', v]); return Promise.resolve(); },
      clearAppBadge: function () { calls.push(['clear']); return Promise.resolve(); } });
  ctx.syncAppBadge();
  const isZero = (calls.length === 1 &&
    ((calls[0][0] === 'clear') || (calls[0][0] === 'set' && calls[0][1] === 0)));
  check(isZero, 'S2 completed-and-rewarded -> badge 0 / cleared [got ' + JSON.stringify(calls) + ']');
})();

// Scenario 11 (P1): rejected promise -> swallow
(function () {
  const ctx = makeSandbox({ progress: 0, completed: false, rewarded: false },
    { setAppBadge: function () { return Promise.reject(new Error('nope')); },
      clearAppBadge: function () { return Promise.resolve(); } });
  let threw = false;
  try { ctx.syncAppBadge(); } catch (e) { threw = true; }
  check(!threw, 'S11 rejected setAppBadge promise -> no throw from syncAppBadge');
})();

// Scenario 11 (P1): synchronous throw -> swallow
(function () {
  const ctx = makeSandbox({ progress: 0, completed: false, rewarded: false },
    { setAppBadge: function () { throw new Error('sync boom'); },
      clearAppBadge: function () { return Promise.resolve(); } });
  let threw = false;
  try { ctx.syncAppBadge(); } catch (e) { threw = true; }
  check(!threw, 'S11 synchronous throw in setAppBadge -> swallowed by try/catch');
})();

// Scenario 3 (P1): no API at all -> no-op, no throw
(function () {
  const ctx = makeSandbox({ progress: 0, completed: false, rewarded: false }, {});
  let threw = false, r;
  try { r = ctx.syncAppBadge(); } catch (e) { threw = true; }
  check(!threw, 'S3 navigator without Badging API -> no throw');
  check(r === false, 'S3 missing API returns false (clean no-op)');
})();

// Scenario 3 (P1): no navigator at all -> no-op, no throw
(function () {
  const ctx = makeSandbox({ progress: 1, completed: false, rewarded: false }, undefined);
  let threw = false, r;
  try { r = ctx.syncAppBadge(); } catch (e) { threw = true; }
  check(!threw && r === false, 'S3 undefined navigator -> no throw, returns false');
})();

// Scenario 6 (P1): corrupt / missing quest object -> valid value, no throw
(function () {
  [null, undefined, {}, 'nope', 7].forEach(function (q, i) {
    const ctx = makeSandbox(q, { setAppBadge: function () { return Promise.resolve(); },
                                 clearAppBadge: function () { return Promise.resolve(); } });
    let threw = false, r;
    try { r = ctx.syncAppBadge(); } catch (e) { threw = true; }
    check(!threw && r === true, 'S6 corrupt quest #' + i + ' -> no throw, resolves to a badge write');
  });
})();

// Scenario 7 (P1): storage helpers absent from sandbox entirely -> still works
(function () {
  const ctx = makeSandbox({ progress: 0, completed: false, rewarded: false },
    { setAppBadge: function () { return Promise.resolve(); } });
  let threw = false;
  try { ctx.syncAppBadge(); } catch (e) { threw = true; }
  check(!threw, 'S7 no save helpers in scope -> badge path never references them');
})();

// Idempotence: repeated calls with the same state are harmless
(function () {
  let n = 0;
  const ctx = makeSandbox({ progress: 0, completed: false, rewarded: false },
    { setAppBadge: function () { n++; return Promise.resolve(); } });
  ctx.syncAppBadge(); ctx.syncAppBadge(); ctx.syncAppBadge();
  check(n === 3, 'idempotent: repeated calls re-apply without error (3 calls seen)');
})();

console.log('');
if (failures.length === 0) {
  console.log('ALL PASS');
  process.exit(0);
} else {
  console.log(failures.length + ' FAILURES');
  process.exit(1);
}
""" % {"src": SRC}


def static_hook_scan():
    """Prove the three hook points exist and the helper is defined once."""
    src = open(SRC, encoding="utf-8").read()
    problems = []
    calls = len(re.findall(r"(?<!function )syncAppBadge\s*\(\s*\)\s*;", src))
    defs = len(re.findall(r"function syncAppBadge\s*\(", src))
    if defs != 1:
        problems.append("expected exactly 1 definition of syncAppBadge, found %d" % defs)
    if calls != 3:
        problems.append("expected exactly 3 call sites of syncAppBadge(), found %d" % calls)
    # hook point 1: end of init()
    if not re.search(r"syncAppBadge\(\);\s*\n\s*setInterval\(renderStatus", src):
        problems.append("hook 1 missing: no syncAppBadge() at end of init()")
    # hook point 2: end of completeQuest()
    if not re.search(r"syncAppBadge\(\);\s*\n\s*\}\s*\n\s*\n\s*// Apply a real combat outcome", src):
        problems.append("hook 2 missing: no syncAppBadge() after reward paid in completeQuest()")
    # hook point 3: after the daily reset branch
    if not re.search(r"ensureQuestState\(\); //[^\n]*\n\s*\}\s*\n\s*syncAppBadge\(\);", src):
        problems.append("hook 3 missing: no syncAppBadge() after the daily-reset branch")
    # no inline onclick introduced
    if re.search(r"onclick=", src):
        problems.append("inline onclick present in file (issue #46 pattern)")
    return problems, calls, defs


def main():
    print("=== Hook point scan: src/cinder.html ===")
    problems, calls, defs = static_hook_scan()
    print("syncAppBadge definitions: %d, call sites: %d" % (defs, calls))
    print("hook 1 = end of init(), hook 2 = end of completeQuest(), hook 3 = after checkDailyReset() branch")
    if problems:
        for p in problems:
            print("BLOCK: " + p)
        return 1
    print("PASS: exactly 3 hook points, no inline onclick")
    print("")

    print("=== Node proof: syncAppBadge value + no-throw + purity ===")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(PROOF_NODE)
        path = f.name
    try:
        r = subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        os.unlink(path)
    print(r.stdout)
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr)
        print("BLOCK: node proof failed")
        return 1

    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
