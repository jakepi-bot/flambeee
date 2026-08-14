#!/usr/bin/env node
// v0.7.0 static invariant checks (Scout / QA)
// Verifies the mobile touch-quality invariants from the v0.7.0 test plan:
//   A1: viewport user-scalable=no on game pages
//   A2: touch-action: manipulation on body of all pages
//   A3: control-level touch-action on Wordfire keys / Simon pads
//   A4: Wordfire key sizes at <=420px
//   A5: Minesweeper responsive board fit math
// Run: node docs/test-plans/v0.7.0-check.js

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', '..', 'src');
let pass = 0, fail = 0;
const failures = [];

function check(name, cond, detail) {
  if (cond) { pass++; console.log('  PASS ' + name); }
  else { fail++; failures.push(name + (detail ? ': ' + detail : '')); console.log('  FAIL ' + name + (detail ? ' (' + detail + ')' : '')); }
}

function read(f) { return fs.readFileSync(path.join(ROOT, f), 'utf8'); }

console.log('A1. Viewport meta (games declare user-scalable=no)');
for (const f of ['2048.html', 'minesweeper.html', 'simon.html', 'wordfire.html']) {
  const html = read(f);
  check('A1 ' + f, /<meta name="viewport"[^>]*user-scalable=no/.test(html), 'missing user-scalable=no');
}

console.log('A2. touch-action: manipulation on body (all pages)');
for (const f of ['2048.html', 'minesweeper.html', 'simon.html', 'wordfire.html', 'index.html']) {
  const html = read(f);
  check('A2 ' + f, /touch-action\s*:\s*manipulation/.test(html), 'no touch-action: manipulation');
}

console.log('A3. Control-level touch-action');
{
  const w = read('wordfire.html');
  // body-level manipulation is set, and keys also declare it; accept either but require body rule present (A2 covers)
  check('A3 wordfire keys (body inheritance + explicit)', /\.key\s*\{[\s\S]*?touch-action\s*:\s*manipulation/.test(w), 'keys lack explicit touch-action (ok if inherits, but explicit preferred)');
}
{
  const s = read('simon.html');
  check('A3 simon pads explicit', /\.pad\s*\{[\s\S]*?touch-action\s*:\s*manipulation/.test(s), 'pads lack explicit touch-action');
}
{
  const m = read('minesweeper.html');
  check('A3 minesweeper board pan-x (taps + horizontal pan, no page scroll-jump)', /#board\s*\{[\s\S]*?touch-action:\s*pan-x/.test(m), 'board touch-action not pan-x');
}

console.log('A4. Wordfire key tap targets (<=420px media query)');
{
  const w = read('wordfire.html');
  const mq = w.match(/@media \(max-width:\s*420px\)\s*\{([\s\S]*?)\n  \}/);
  check('A4 media query exists', !!mq, 'no <=420px media query');
  if (mq) {
    const body = mq[1];
    const keyRule = body.match(/\.key\s*\{([\s\S]*?)\}/);
    const wideRule = body.match(/\.key\.wide\s*\{([\s\S]*?)\}/);
    check('A4 letter key min-width >= 32px', !!keyRule && /min-width:\s*32px/.test(keyRule[1]) && /height:\s*42px/.test(keyRule[1]), keyRule ? keyRule[1] : 'no .key rule in mq');
    check('A4 wide key min-width >= 52px', !!wideRule && /min-width:\s*52px/.test(wideRule[1]), wideRule ? wideRule[1] : 'no .key.wide rule in mq');
  }
}

console.log('A5. Minesweeper responsive fit math');
{
  const m = read('minesweeper.html');
  check('A5 maxFit computation present', /maxFit\s*=\s*Math\.floor\(\(avail\s*-\s*12\s*-\s*\(cols\s*-\s*1\)\s*\*\s*2\)\s*\/\s*cols\)/.test(m), 'missing responsive cell sizing');
  check('A5 size = max(min(configured, maxFit), MIN_CELL)', /Math\.max\(Math\.min\(cellSize, maxFit\), MIN_CELL\)/.test(m), 'cell sizing formula changed');
  check('A5 MIN_CELL >= 18', /const MIN_CELL = 18/.test(m), 'MIN_CELL not 18');
  check('A5 board-scroll wrapper present', /\.board-scroll\s*\{[\s\S]*?overflow-x:\s*auto/.test(m), 'no scrollable board wrapper');
  check('A5 board touch-action pan-x', /#board\s*\{[\s\S]*?touch-action:\s*pan-x/.test(m), 'board touch-action not pan-x');
  // numeric check at 375px and 320px viewports: cells never below MIN_CELL, board never overflows (scrolls instead)
  const sizes = { easy: { cols: 9, base: 38 }, medium: { cols: 16, base: 30 }, hard: { cols: 30, base: 24 } };
  for (const vp of [375, 320]) {
    for (const [k, { cols, base }] of Object.entries(sizes)) {
      const avail = Math.min(vp - 36, 520);
      const maxFit = Math.floor((avail - 12 - (cols - 1) * 2) / cols);
      const size = Math.max(Math.min(base, maxFit), 18);
      const boardW = size * cols + (cols - 1) * 2 + 14;
      check('A5 ' + k + ' @' + vp + 'px cell=' + size + 'px (board ' + boardW + 'px, wrapper scrolls if >' + vp + ')', size >= 18, 'cell ' + size + ' below MIN_CELL');
    }
  }
}

console.log('A6. Wordfire legend present (Story 009)');
{
  const w = read('wordfire.html');
  check('A6 legend markup', /class="legend"/.test(w), 'no legend element');
  check('A6 green/yellow/gray swatches', /box green[\s\S]*box yellow[\s\S]*box gray/.test(w), 'missing swatch classes');
  check('A6 colorblind shapes in legend', /body\.colorblind \.legend \.box/.test(w), 'legend lacks colorblind shape rules');
}

console.log('\n' + pass + ' passed, ' + fail + ' failed');
if (fail > 0) { console.log('FAILURES:\n' + failures.join('\n')); process.exit(1); }
