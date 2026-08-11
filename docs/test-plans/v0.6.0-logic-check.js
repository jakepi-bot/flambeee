#!/usr/bin/env node
/* v0.6.0 logic checks — Wordfire evaluate() duplicate rules + streak math + daily seeding.
 * Mirrors the exact algorithms in src/wordfire.html.
 * Run: node docs/test-plans/v0.6.0-logic-check.js
 */
'use strict';

let pass = 0, fail = 0;
function check(name, cond) {
  if (cond) { pass++; console.log('  PASS ' + name); }
  else { fail++; console.log('  FAIL ' + name); }
}

// --- evaluate(): must match src/wordfire.html ---
function evaluate(guess, ans) {
  const COLS = 5;
  const colors = new Array(COLS).fill('gray');
  const remaining = {};
  for (const ch of ans) remaining[ch] = (remaining[ch] || 0) + 1;
  for (let i = 0; i < COLS; i++) {
    if (guess[i] === ans[i]) {
      colors[i] = 'green';
      remaining[guess[i]]--;
    }
  }
  for (let i = 0; i < COLS; i++) {
    if (colors[i] === 'green') continue;
    const ch = guess[i];
    if (remaining[ch] > 0) {
      colors[i] = 'yellow';
      remaining[ch]--;
    }
  }
  return colors;
}

console.log('Tile evaluation:');
check('exact match all green', JSON.stringify(evaluate('train', 'train')) === JSON.stringify(['green','green','green','green','green']));
check('no shared letters all gray', JSON.stringify(evaluate('xyzzy', 'about')) === JSON.stringify(['gray','gray','gray','gray','gray']));
check('misplaced yellow', JSON.stringify(evaluate('board', 'about')) === JSON.stringify(['yellow','yellow','yellow','gray','gray']));
// board vs about: b yellow (in answer pos0), o yellow (pos1), a yellow (pos2)? No: a is at ans pos0.
// b->a? gray? b IS in about. about letters: a,b,o,u,t. board: b,o,a,r,d -> b yellow, o yellow, a yellow, r gray, d gray
check('eerie/erect single duplicate e', JSON.stringify(evaluate('erect', 'eerie')) === JSON.stringify(['green','yellow','yellow','gray','gray']));
// erect vs eerie: e=e green; r vs e yellow; e vs r yellow; c vs i gray; t vs e gray
check('geese/eerie two e counted', JSON.stringify(evaluate('geese', 'eerie')) === JSON.stringify(['gray','green','yellow','gray','green']));
// geese vs eerie: g gray; e=e green; e vs r yellow; s gray; e green
check('no false yellow for extra dup', JSON.stringify(evaluate('eerie', 'erect')) === JSON.stringify(['green','yellow','yellow','gray','gray']));
// eerie vs erect = e,r,e,c,t: e=e green; e vs r yellow; r vs e yellow; i gray; e vs t gray
check('answer repeated, guess single', JSON.stringify(evaluate('sasss', 'asset')) === JSON.stringify(['yellow','yellow','green','gray','gray']));
// sasss vs asset: s yellow (only 2 s in answer), a yellow, s green, s gray, s gray
// Wordle canonical: guess 'sassy' vs answer 'asset' -> s yellow, a yellow, s green, s gray, y gray
check('wordle canonical sassy/asset', JSON.stringify(evaluate('sassy', 'asset')) === JSON.stringify(['yellow','yellow','green','gray','gray']));

// --- Streak math: must match src/wordfire.html ---
function dayIndex(ts) { return Math.floor(ts / 86400000); }
function applyStreakGap(s, today) {
  if (s.lastSolvedDay < today - 1) s.current = 0;
  return s;
}
function recordDailyWin(s, today) {
  s = applyStreakGap(s, today);
  if (s.lastSolvedDay === today) return s;
  s.current = (s.lastSolvedDay === today - 1) ? s.current + 1 : 1;
  s.lastSolvedDay = today;
  if (s.current > s.best) s.best = s.current;
  return s;
}

console.log('Streak math:');
let s = { current: 0, best: 0, lastSolvedDay: -1 };
const T = 19000; // arbitrary day base
s = recordDailyWin(s, T);
check('first win current=1', s.current === 1 && s.best === 1);
s = recordDailyWin(s, T + 1);
check('consecutive win current=2', s.current === 2 && s.best === 2);
s = recordDailyWin(s, T + 2);
check('third day current=3 best=3', s.current === 3 && s.best === 3);
s = recordDailyWin(s, T + 4); // skipped T+3
check('gap resets current to 1', s.current === 1 && s.best === 3);
s = recordDailyWin(s, T + 5);
check('post-gap continues 2', s.current === 2 && s.best === 3);
s = recordDailyWin(s, T + 5); // same day again
check('same-day win no double count', s.current === 2 && s.best === 3 && s.lastSolvedDay === T + 5);
s = applyStreakGap({ current: 2, best: 3, lastSolvedDay: T + 5 }, T + 8);
check('two-day gap zeroes current', s.current === 0 && s.best === 3);

// --- Daily seeding: must match src/wordfire.html ---
console.log('Daily seeding:');
const ANSWERS = ['about', 'abuse', 'actor']; // stand-in for WORDFIRE_ANSWERS
function dailyAnswerFor(day) { return ANSWERS[day % ANSWERS.length]; }
check('seed wraps pool', dailyAnswerFor(0) === 'about' && dailyAnswerFor(3) === 'about');
check('seed deterministic', dailyAnswerFor(1000000) === dailyAnswerFor(1000000));
check('different days differ (within pool)', dailyAnswerFor(0) !== dailyAnswerFor(1));
const fs = require('fs');
const src = fs.readFileSync('src/wordfire-words.js', 'utf8');
let answers = [], guesses = [];
try {
  const loader = new Function(src + '; return { a: WORDFIRE_ANSWERS, g: WORDFIRE_GUESSES };');
  const pools = loader();
  answers = pools.a; guesses = pools.g;
  check('answer pool >= 1000', answers.length >= 1000);
  check('guess pool >= 3000', guesses.length >= 3000);
  check('every answer is a valid guess', answers.every(a => guesses.includes(a)));
  check('no duplicates in answers', new Set(answers).size === answers.length);
} catch (e) {
  check('word list file parseable', false);
  console.log('  parse error: ' + e.message);
}

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
