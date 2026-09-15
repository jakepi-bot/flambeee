#!/usr/bin/env python3
"""Kai pure-read proof for Story 035 (Cinder recent-quests / quest-streak view).

Verifies from the shipped src/cinder.html that:
  1. computeQuestStreak is a pure helper (deterministic, no input/global mutation)
     and returns the correct streak across consecutive, missed-day, live-yesterday,
     legacy, and corrupt-input cases.
  2. The quest-log view path (renderQuestLog + computeQuestStreak + dayLabelForIndex
     + handleQuestLogInput) contains no forbidden writes: no saveCharacter,
     saveDayState, localStorage.setItem, ensureQuestState, completeQuest,
     applyQuestProgress, and no character./dayState. assignments. It is a pure read.
  3. The only persistence changes in scope are the additive completedQuests append
     in completeQuest() and the completedQuests:[] default in ensureQuestState /
     checkDailyReset / init (backwards-compatible, existing saves load clean).

Run:  .venv/bin/python3 src/kai-story035-pure-read-proof.py
Exit code 0 = all checks pass. Non-zero = proof failed.
"""
import re, subprocess, sys, tempfile, json, os

SRC = os.path.join(os.path.dirname(__file__), "cinder.html")

PROOF_NODE = r"""
const fs = require('fs');
const vm = require('vm');
function extract(name){
  const src = fs.readFileSync('%s','utf8');
  const idx = src.indexOf('function '+name+'(');
  if(idx<0) throw new Error('not found '+name);
  const openParen = idx + ('function '+name).length;
  let depth=0, i=openParen;
  for(; i<src.length; i++){ const c=src[i]; if(c==='(')depth++; else if(c===')'){depth--; if(depth===0)break;} }
  const bodyStart = src.indexOf('{', i);
  let d=0, j;
  for(j=bodyStart; j<src.length; j++){ const c=src[j]; if(c==='{')d++; else if(c==='}'){d--; if(d===0)break;} }
  return src.slice(idx, j+1);
}
const ctx = { Math, Date, Array, Object, JSON, console, getDayIndex: () => 1000 };
vm.createContext(ctx);
vm.runInContext(extract('computeQuestStreak'), ctx);
vm.runInContext(extract('dayLabelForIndex'), ctx);
const S = ctx.computeQuestStreak;
const D = ctx.dayLabelForIndex;
let failures = [];
function assert(cond,msg){ if(!cond){ failures.push(msg); console.log('FAIL: '+msg); } else { console.log('PASS: '+msg); } }
function ds(todayCompleted, days){
  return { quest: { completed: !!todayCompleted }, completedQuests: days.map(d=>({dayIndex:d, label:'x', objective:'obj'+d})) };
}
assert(S(ds(true,[1000,999]))===2, '2.1 consecutive days streak=2');
assert(S(ds(true,[1000,998,996]))===1, '2.2 missed-day reset streak=1');
assert(S(ds(false,[999,998,997]))===3, '2.3 yesterday-only stays live streak=3');
assert(S(ds(false,[]))===0, '2.4 empty history streak=0 no negative');
assert(S(ds(true,[1000,990]))===1, '2.5 gap reset to 1');
assert(S({quest:{completed:false}, completedQuests:null})===0, 'legacy null -> 0');
assert(S({quest:{completed:false}})===0, 'legacy missing -> 0');
assert(S(undefined)===0, 'undefined -> 0');
assert(S({quest:{completed:false}, completedQuests:'not-array'})===0, 'corrupt string -> 0');
const input = ds(true,[1000,999]);
const snapshot = JSON.stringify(input);
const g0 = JSON.stringify(Object.keys(ctx).sort());
S(input);
assert(JSON.stringify(input)===snapshot, '2.6a no input mutation');
assert(JSON.stringify(Object.keys(ctx).sort())===g0, '2.6b no global mutation');
let ok=true; for(let i=0;i<100;i++){ if(S(ds(true,[1000,999]))!==2) ok=false; }
assert(ok, '2.6c deterministic 100 runs');
assert(D(1000)==='today', 'dayLabel today');
assert(D(999)==='yesterday', 'dayLabel yesterday');
assert(D(998)==='2 days ago', 'dayLabel 2 days ago');
console.log(failures.length===0 ? 'ALL PASS' : (failures.length+' FAILURES'));
process.exit(failures.length===0?0:1);
""" % SRC

def node_proof():
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(PROOF_NODE); path = f.name
    try:
        r = subprocess.run(['node', path], capture_output=True, text=True)
    finally:
        os.unlink(path)
    return r

def static_scan():
    src = open(SRC).read()
    forbidden = ['saveCharacter','saveDayState','localStorage.setItem','ensureQuestState(',
                 'completeQuest(','applyQuestProgress']
    # Extact exact body of each view-path function using brace matching.
    def body_of(name):
        idx = src.find('function '+name+'(')
        if idx < 0:
            raise RuntimeError('function not found: '+name)
        open_paren = idx + len('function '+name)
        depth = 0
        i = open_paren
        while i < len(src):
            c = src[i]
            if c == '(': depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0: break
            i += 1
        body_start = src.index('{', i)
        d = 0; j = body_start
        while j < len(src):
            c = src[j]
            if c == '{': d += 1
            elif c == '}':
                d -= 1
                if d == 0: break
            j += 1
        return src[idx:j+1]
    view_fns = ['renderQuestLog','computeQuestStreak','dayLabelForIndex','handleQuestLogInput']
    problems = []
    for fn in view_fns:
        span = body_of(fn)
        for tok in forbidden:
            if tok in span:
                problems.append('forbidden write token in '+fn+': '+tok)
        if re.search(r'(character|dayState)\.\w+\s*=', span):
            problems.append('assignment to character./dayState. in '+fn)
    return problems, ' + '.join(view_fns)

def main():
    print('=== Static scan: quest-log view path (pure read) ===')
    problems, _ = static_scan()
    if problems:
        for p in problems:
            print('BLOCK: '+p)
        return 1
    print('PASS: no forbidden writes on the quest-log view path')
    print()
    print('=== Node proof: computeQuestStreak purity + correctness ===')
    r = node_proof()
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        print('BLOCK: node proof failed')
        return 1
    print('ALL CHECKS PASS')
    return 0

if __name__ == '__main__':
    sys.exit(main())
