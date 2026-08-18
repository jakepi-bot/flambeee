#!/usr/bin/env node
// v0.9.0 static invariant checks (Scout)
// Verifies Wordfire guess distribution (Story 013) + website game screenshots (Story 014).
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', '..');
const wordfire = fs.readFileSync(path.join(ROOT, 'src', 'wordfire.html'), 'utf8');
const site = fs.readFileSync('/home/jake/.openclaw/workspace/share/Flambeee/index.html', 'utf8');
const assetsDir = '/home/jake/.openclaw/workspace/share/Flambeee/assets';

let pass = 0, fail = 0;
function check(name, cond, detail) {
  if (cond) { pass++; console.log('PASS ' + name); }
  else { fail++; console.log('FAIL ' + name + (detail ? ' :: ' + detail : '')); }
}

// --- B1: distribution storage key + shape ---
check('B1 DIST_KEY exists', /const DIST_KEY = 'flambeee-wordfire-distribution'/.test(wordfire), 'DIST_KEY missing');
check('B1 loadDist default shape', /guesses: \[0, 0, 0, 0, 0, 0\], played: 0, wins: 0/.test(wordfire), 'default shape missing');
check('B1 loadDist validates 6 slots', /d\.guesses\.length === 6/.test(wordfire), 'validation missing');

// --- B2: record rules ---
check('B2 daily win records', /recordDist\(true, guessIndex\)/.test(wordfire), 'win record call missing');
check('B2 daily loss records', /recordDist\(false, 0\)/.test(wordfire), 'loss record call missing');
check('B2 once per day flag', /recordedThisDay/.test(wordfire), 'no-double-count flag missing');
check('B2 guesses index n-1', /d\.guesses\[guessCount - 1\] \+= 1/.test(wordfire), 'index math missing');

// --- B3: panel render ---
check('B3 dist panel element', /id="distPanel"/.test(wordfire), 'panel missing');
check('B3 sub line', /d\.played \+ ' played · ' \+ d\.wins \+ ' won · ' \+ pct \+ '%'/.test(wordfire), 'sub line missing');
check('B3 six rows rendered', /for \(let i = 0; i < 6; i\+\+\)/.test(wordfire), '6-row loop missing');
check('B3 empty bar class', /dist-bar empty/.test(wordfire), 'empty bar style missing');
check('B3 bar width proportional', /Math\.round\(\(n \/ max\) \* 100\)/.test(wordfire), 'proportional width missing');
check('B3 render on init', /renderDist\(\)/.test(wordfire), 'initial render call missing');

// --- B4: site game screenshots ---
check('B4 wordfire shot', /assets\/game-wordfire\.png/.test(site), 'wordfire img missing');
check('B4 minesweeper shot', /assets\/game-minesweeper\.png/.test(site), 'minesweeper img missing');
check('B4 simon shot', /assets\/game-simon\.png/.test(site), 'simon img missing');
check('B4 2048 shot', /assets\/game-2048\.png/.test(site), '2048 img missing');
check('B4 emoji icons removed', !/game-icon">🔥|game-icon">💣|game-icon">🧠|game-icon">🔢/.test(site), 'old emoji icons still present');

// --- B5: assets exist on disk ---
['game-wordfire.png', 'game-minesweeper.png', 'game-simon.png', 'game-2048.png'].forEach((f) => {
  check('B5 asset ' + f, fs.existsSync(path.join(assetsDir, f)), 'missing file');
});

// --- B6: alt text on each screenshot ---
check('B6 wordfire alt', /alt="Wordfire word game board with colored letter tiles"/.test(site), 'wordfire alt missing');
check('B6 minesweeper alt', /alt="Minesweeper board with revealed cells and numbers"/.test(site), 'minesweeper alt missing');
check('B6 simon alt', /alt="Simon memory game with four colored pads"/.test(site), 'simon alt missing');
check('B6 2048 alt', /alt="2048 grid with numbered merge tiles"/.test(site), '2048 alt missing');

// --- B7: game-shot CSS present ---
check('B7 game-shot css', /\.game-shot \{/.test(site), 'game-shot CSS missing');
check('B7 aspect ratio', /aspect-ratio: 4 \/ 3/.test(site), 'aspect-ratio missing');

// --- B8: JS syntax on touched files ---
function syntaxOK(file, label) {
  const html = fs.readFileSync(file, 'utf8');
  const scripts = html.match(/<script>([\s\S]*?)<\/script>/g) || [];
  let ok = true;
  scripts.forEach((s) => {
    const js = s.replace(/^<script>/, '').replace(/<\/script>$/, '');
    try { new Function(js); } catch (e) { ok = false; console.log('  syntax error: ' + e.message); }
  });
  check('B8 syntax ' + label, ok);
}
syntaxOK(path.join(ROOT, 'src', 'wordfire.html'), 'wordfire');

// --- B9: no em dashes / AI tells in session docs? (docs are internal; skip) ---

console.log('\n' + pass + '/' + (pass + fail) + ' checks passed');
process.exit(fail ? 1 : 0);
