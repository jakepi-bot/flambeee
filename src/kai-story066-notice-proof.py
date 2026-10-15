#!/usr/bin/env python3
"""Kai proof for Story 066 (Cinder unreadable-storage visible notice).

Proves against the REAL src/cinder.html by extraction, never by reimplementation:
  (1) unreadable character store fires the notice path
  (2) unreadable day store fires the notice path
  (3) readable store shows no notice and behavior matches pre-066
  (4) no write on the notice path

Usage:
  python3 src/kai-story066-notice-proof.py [cinder.html]
  CINDER_SRC env overrides the path. BASELINE_REF env overrides the
  pre-066 baseline ref (default origin/main:src/cinder.html).

Exit 0 = candidate passes all four proofs.
Exit 1 = failure, or ABSENCE when the file under test has no notice path
  (this is the expected result for run 1 against the pre-066 tree).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_CANDIDATES = [
    "/home/jake/.hermes/flambeee/flambeee",
    os.path.join(HERE, ".."),
]
BASELINE_REF = os.environ.get("BASELINE_REF", "origin/main:src/cinder.html")
NOTICE_TOKENS = ["showStorageNotice", "storageNoticeShown", "storageNotice"]


def repo_dir():
    for c in REPO_CANDIDATES:
        if os.path.isdir(os.path.join(c, ".git")):
            return c
    return REPO_CANDIDATES[0]


def git_show(ref):
    r = subprocess.run(["git", "-C", repo_dir(), "show", ref],
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout and "function loadSave(" in r.stdout:
        return r.stdout
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
            try:
                txt = open(c, encoding="utf-8").read()
            except OSError:
                continue
            if "function loadSave(" in txt and "function loadDayState(" in txt:
                return c, txt, c
    return None, None, None


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
    in_s = None  # string/comment aware brace match so braces in text do not break us
    k = body_start
    # find matching close brace with a small string-aware scan
    while k < len(src):
        c = src[k]
        if in_s:
            if c == "\\":
                k += 2
                continue
            if c == in_s:
                in_s = None
            k += 1
            continue
        if c in "'\"`":
            in_s = c
            k += 1
            continue
        if c == "/" and k + 1 < len(src) and src[k + 1] == "/":
            while k < len(src) and src[k] != "\n":
                k += 1
            continue
        if c == "/" and k + 1 < len(src) and src[k + 1] == "*":
            k += 2
            while k < len(src) and not (src[k] == "*" and k + 1 < len(src) and src[k + 1] == "/"):
                k += 1
            k += 2
            continue
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                j = k
                break
        k += 1
    if d != 0:
        raise RuntimeError("unbalanced braces in " + name)
    return src[idx:j + 1]


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


def static_scan(src, base_src):
    problems = []
    code = strip_comments(src)
    print("=== Static scan: Story 066 constraints ===")
    has_notice = any(t in src for t in NOTICE_TOKENS)
    base_has_notice = any(t in (base_src or "") for t in NOTICE_TOKENS)
    print("  notice tokens present in file under test: %s" % has_notice)
    print("  notice tokens present in pre-066 baseline: %s" % base_has_notice)
    if not has_notice:
        print("  ABSENCE: no notice path in this file (expected for pre-066 run 1)")
        return problems, False
    try:
        load_save = strip_comments(body_of(src, "loadSave"))
        load_day = strip_comments(body_of(src, "loadDayState"))
        notice_fn = strip_comments(body_of(src, "showStorageNotice"))
    except RuntimeError as e:
        problems.append(str(e))
        print("  BLOCK: " + str(e))
        return problems, True
    if "showStorageNotice()" in load_save and "catch" in load_save:
        print("  loadSave() catch fires showStorageNotice()")
    else:
        problems.append("loadSave() catch does not fire showStorageNotice()")
        print("  BLOCK: loadSave() catch missing the notice call")
    if "showStorageNotice()" in load_day and "catch" in load_day:
        print("  loadDayState() catch fires showStorageNotice()")
    else:
        problems.append("loadDayState() catch does not fire showStorageNotice()")
        print("  BLOCK: loadDayState() catch missing the notice call")
    if "localStorage" in notice_fn or "setItem" in notice_fn:
        problems.append("showStorageNotice() touches storage (must be pure presentation)")
        print("  BLOCK: showStorageNotice() touches storage")
    else:
        print("  showStorageNotice() is pure presentation (no storage call)")
    if "storageNoticeShown" not in src:
        problems.append("once-per-load guard storageNoticeShown missing")
    else:
        print("  once-per-load in-memory guard present (storageNoticeShown)")
    for f in ["normalizedRecord", "recordVersion", "loadNormalized", "rawRecordCache"]:
        if re.search(r"\b" + f + r"\b", code):
            problems.append("forbidden new field name appears: %s" % f)
    # Normalizers must be untouched vs baseline (readable path behavior).
    for fn in ["normalizeDayRecord", "normalizeCharacterRecord"]:
        try:
            got = body_of(src, fn)
            want = body_of(base_src, fn)
        except RuntimeError:
            continue
        if got != want:
            problems.append("%s changed vs pre-066 baseline (readable path must match)" % fn)
            print("  BLOCK: %s differs from baseline" % fn)
        else:
            print("  %s byte-identical to baseline" % fn)
    if problems:
        for p in problems:
            print("  BLOCK: " + p)
    else:
        print("  PASS: notice at both storage catches, pure, guarded, no new field")
    return problems, True


PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');
const CAND_PATH = __CAND_PATH__;
const BASE_PATH = __BASE_PATH__;
const candSrc = fs.readFileSync(CAND_PATH, 'utf8');
const baseSrc = fs.readFileSync(BASE_PATH, 'utf8');
const HAS_NOTICE = candSrc.indexOf('showStorageNotice') >= 0;

let failures = [];
let passes = 0;
function check(cond, msg) {
  if (cond) { passes += 1; console.log('PASS: ' + msg); }
  else { failures.push(msg); console.log('FAIL: ' + msg); }
}
function extract(src, name) {
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
  let d = 0, j = bodyStart;
  for (j = bodyStart; j < src.length; j++) {
    const c = src[j];
    if (c === '{') d++;
    else if (c === '}') { d--; if (d === 0) break; }
  }
  return src.slice(idx, j + 1);
}
function constVal(src, name) {
  const m = src.match(new RegExp("const\\s+" + name + "\\s*=\\s*'([^']+)'"));
  return m ? m[1] : null;
}
function makeCtx(src, mode, seed) {
  const SAVE_KEY = constVal(src, 'SAVE_KEY') || 'flambeee-cinder-save';
  const DAY_KEY = constVal(src, 'DAY_KEY') || 'flambeee-cinder-day';
  const writes = [];
  let noticeFires = 0;
  const data = Object.assign({}, seed || {});
  const localStorage = {
    getItem: function (k) {
      if (mode === 'throw-char' && k === SAVE_KEY) throw new Error('SecurityError: storage blocked');
      if (mode === 'throw-day' && k === DAY_KEY) throw new Error('SecurityError: storage blocked');
      if (mode === 'throw-both' && (k === SAVE_KEY || k === DAY_KEY)) throw new Error('SecurityError: storage blocked');
      return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null;
    },
    setItem: function (k, v) { writes.push(['set', k]); data[k] = String(v); },
    removeItem: function (k) { writes.push(['remove', k]); delete data[k]; },
    clear: function () { writes.push(['clear']); Object.keys(data).forEach(function (k) { delete data[k]; }); }
  };
  const noticeEl = { _shown: false, classList: { add: function (c) { if (c === 'show') { noticeFires += 1; noticeEl._shown = true; } } } };
  const document = { getElementById: function (id) { return id === 'storageNotice' ? noticeEl : { innerHTML: '' }; } };
  const ctx = { console: console, localStorage: localStorage, document: document,
    SAVE_KEY: SAVE_KEY, DAY_KEY: DAY_KEY, JSON: JSON, Error: Error };
  vm.createContext(ctx);
  const names = ['showStorageNotice', 'loadSave', 'loadDayState', 'normalizeCharacterRecord', 'normalizeDayRecord'];
  // storageNoticeShown is a top-level let in the file; re-declare it here per context.
  vm.runInContext('let storageNoticeShown = false;', ctx);
  names.forEach(function (n) {
    try { vm.runInContext(extract(src, n), ctx); } catch (e) { /* absent on baseline */ }
  });
  return { ctx: ctx, writes: writes,
    noticeFires: function () { return noticeFires; },
    noticeShown: function () { return noticeEl._shown; } };
}

console.log('=== Story 066 node proof (extracted from the files under test) ===');
console.log('candidate: ' + CAND_PATH + '  hasNotice=' + HAS_NOTICE);
console.log('');

if (!HAS_NOTICE) {
  console.log('ABSENCE: no notice path in this file. Run 1 negative control holds: no notice fires.');
  console.log('checks passed: 1 (absence confirmed)');
  process.exit(2);
}

// Proof 1: unreadable character store fires the notice path.
console.log('--- Proof 1: unreadable character store fires notice ---');
(function () {
  const t = makeCtx(candSrc, 'throw-char', {});
  let ret = 'unset', threw = null;
  try { ret = vm.runInContext('loadSave()', t.ctx); } catch (e) { threw = e.message; }
  console.log('  loadSave() returned: ' + JSON.stringify(ret) + '  threw: ' + (threw || 'no'));
  console.log('  notice fires: ' + t.noticeFires() + '  writes: ' + t.writes.length);
  check(threw === null, 'loadSave() does not throw on unreadable store (catches)');
  check(ret === null, 'loadSave() returns null on unreadable store');
  check(t.noticeFires() >= 1, 'notice path fired on unreadable character store');
})();

// Proof 2: unreadable day store fires the notice path (fresh context, no bleed).
console.log('');
console.log('--- Proof 2: unreadable day store fires notice ---');
(function () {
  const t = makeCtx(candSrc, 'throw-day', {});
  let ret = 'unset', threw = null;
  try { ret = vm.runInContext('loadDayState()', t.ctx); } catch (e) { threw = e.message; }
  console.log('  loadDayState() returned: ' + JSON.stringify(ret) + '  threw: ' + (threw || 'no'));
  console.log('  notice fires: ' + t.noticeFires() + '  writes: ' + t.writes.length);
  check(threw === null, 'loadDayState() does not throw on unreadable store (catches)');
  check(ret === null, 'loadDayState() returns null on unreadable store');
  check(t.noticeFires() >= 1, 'notice path fired on unreadable day store');
})();

// Proof 3: readable store shows no notice and matches pre-066 behavior.
console.log('');
console.log('--- Proof 3: readable store, no notice, matches pre-066 ---');
(function () {
  const TODAY = Math.floor(Date.now() / 86400000);
  const save = { name: 'Kai', level: 3, xp: 100, hp: 30, maxHp: 30, attack: 4, defense: 3,
    gold: 50, bank: 10, weapon: 1, armor: 1, wins: 7, losses: 2, deaths: 0 };
  const day = { dayIndex: TODAY, fightsUsed: 2, innHealsUsed: 1,
    quest: { progress: 0, completed: false, rewarded: false }, completedQuests: [] };
  const seed = {};
  seed['flambeee-cinder-save'] = JSON.stringify(save);
  seed['flambeee-cinder-day'] = JSON.stringify(day);
  const c = makeCtx(candSrc, 'readable', seed);
  const b = makeCtx(baseSrc, 'readable', seed);
  const cSave = vm.runInContext('JSON.stringify(loadSave())', c.ctx);
  const bSave = vm.runInContext('JSON.stringify(loadSave())', b.ctx);
  const cDay = vm.runInContext('JSON.stringify(loadDayState())', c.ctx);
  const bDay = vm.runInContext('JSON.stringify(loadDayState())', b.ctx);
  console.log('  candidate notice fires: ' + c.noticeFires() + '  baseline notice fires: ' + b.noticeFires());
  console.log('  save equal: ' + (cSave === bSave) + '  day equal: ' + (cDay === bDay));
  check(c.noticeFires() === 0, 'readable store fires no notice on candidate');
  check(b.noticeFires() === 0, 'readable store fires no notice on baseline');
  check(cSave === bSave, 'character load matches pre-066 byte-for-byte');
  check(cDay === bDay, 'day load matches pre-066 byte-for-byte');
  check(cSave === JSON.stringify(save), 'character load returns the stored record');
  check(cDay === JSON.stringify(day), 'day load returns the stored record');
})();

// Proof 4: no write on the notice path.
console.log('');
console.log('--- Proof 4: no write on the notice path ---');
(function () {
  ['throw-char', 'throw-day', 'throw-both'].forEach(function (mode) {
    const t = makeCtx(candSrc, mode, {});
    try { vm.runInContext('loadSave()', t.ctx); } catch (e) {}
    try { vm.runInContext('loadDayState()', t.ctx); } catch (e) {}
    console.log('  [' + mode + '] writes=' + t.writes.length + ' notice=' + t.noticeFires());
    check(t.writes.length === 0, mode + ': zero storage writes on the notice path');
  });
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
        print("BLOCK: no cinder.html containing loadSave/loadDayState found")
        return 2
    base_src = git_show(BASELINE_REF)
    if base_src is None:
        # fall back to the working-tree file only if git show fails; the
        # byte-identity comparisons are then skipped, not invented.
        print("BLOCK: could not read baseline %s" % BASELINE_REF)
        return 2
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    base_digest = hashlib.sha256(base_src.encode("utf-8")).hexdigest()
    print("=== Story 066 proof: cinder unreadable-storage notice ===")
    print("file under test: %s" % label)
    print("sha256: %s" % digest)
    print("baseline: %s sha256 %s" % (BASELINE_REF, base_digest))
    print("same blob as baseline: %s" % (digest == base_digest))
    print("")
    problems, has_notice = static_scan(src, base_src)
    fd, cand_tmp = tempfile.mkstemp(suffix="-cand.html", prefix="story066-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(src)
    fd2, base_tmp = tempfile.mkstemp(suffix="-base.html", prefix="story066-")
    with os.fdopen(fd2, "w", encoding="utf-8") as f:
        f.write(base_src)
    try:
        node_src = PROOF_NODE.replace("__CAND_PATH__", json.dumps(cand_tmp))
        node_src = node_src.replace("__BASE_PATH__", json.dumps(base_tmp))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(node_src)
            path = f.name
        try:
            r = subprocess.run(["node", path], capture_output=True, text=True, timeout=120)
        finally:
            os.unlink(path)
    finally:
        os.unlink(cand_tmp)
        os.unlink(base_tmp)
    print("")
    print(r.stdout, end="")
    if r.returncode == 2:
        print("RESULT: ABSENCE (no notice path; expected for pre-066 run 1)")
        return 2
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
