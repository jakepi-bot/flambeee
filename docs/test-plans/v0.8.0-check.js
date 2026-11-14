#!/usr/bin/env node
// v0.8.0 static invariant checks (Scout)
// Verifies Wordfire share, Minesweeper per-difficulty stats, website What's New.
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', '..');
const wordfire = fs.readFileSync(path.join(ROOT, 'archive', 'src-games', 'wordfire.html'), 'utf8');
const minesweeper = fs.readFileSync(path.join(ROOT, 'archive', 'src-games', 'minesweeper.html'), 'utf8');
const hub = fs.readFileSync(path.join(ROOT, 'archive', 'src-games', 'index.html'), 'utf8');
const site = fs.readFileSync(path.join(ROOT, 'website', 'index.html'), 'utf8');

let pass = 0, fail = 0;
function check(name, cond, detail) {
  if (cond) { pass++; console.log('PASS ' + name); }
  else { fail++; console.log('FAIL ' + name + (detail ? ' :: ' + detail : '')); }
}

// --- A1: share button exists in overlay ---
check('A1 share button in overlay', /id="overlayShareBtn"/.test(wordfire), 'overlayShareBtn missing');

// --- A2: share button hidden by default ---
check('A2 share hidden by default', /overlayShareBtn" style="display:none"/.test(wordfire), 'not hidden by default');

// --- A3: share text builder produces grid, no letters ---
check('A3 buildShareText exists', /function buildShareText/.test(wordfire));
check('A3 grid uses 6 rows', /for \(let r = 0; r < ROWS; r\+\+\)/.test(wordfire));
check('A3 no letters in grid', /row\.colors\[c\] === 'green' \? green/.test(wordfire), 'grid built from colors not letters');

// --- A4: colorblind share uses shapes ---
check('A4 cb shapes', /const green = cb \? '●' : '🟩'/.test(wordfire), 'colorblind shape mapping missing');

// --- A5: share header format ---
check('A5 share header mode label', /const modeLabel = difficulty === 'hard' \? 'Wordfire Hard ' : 'Wordfire ';/.test(wordfire))
check('A5 share header format', /modeLabel \+ guesses \+ '\/6'/.test(wordfire))

// --- A6: Minesweeper per-difficulty shape ---
check('A6 per-diff stats shape', /bestTime: \{ easy: null, medium: null, hard: null \}/.test(minesweeper), 'per-diff shape missing');
check('A6 DIFF_KEYS', /const DIFF_KEYS = \['easy', 'medium', 'hard'\]/.test(minesweeper), 'DIFF_KEYS missing');

// --- A7: legacy migration ---
check('A7 legacy migration', /Migrate legacy flat shape/.test(minesweeper), 'migration comment missing');
check('A7 migration logic', /typeof parsed\.plays === 'number'/.test(minesweeper), 'legacy detection missing');

// --- A8: recordGame per difficulty ---
check('A8 recordGame per-diff', /stats\.plays\[currentDiff\] \+= 1/.test(minesweeper), 'plays not per-diff');
check('A8 bestTime per-diff', /stats\.bestTime\[currentDiff\]/.test(minesweeper), 'bestTime not per-diff');
check('A8 currentDiff set on switch', /currentDiff = btn\.dataset\.diff/.test(minesweeper), 'currentDiff not set');

// --- A9: hub handles new shape ---
check('A9 hub new shape', /s\.plays && typeof s\.plays === 'object'/.test(hub), 'hub new-shape branch missing');
check('A9 hub E/M/H bests', /bests\.push\('E ' \+ fmtTime/.test(hub), 'E/M/H bests missing');

// --- A10: website What's New ---
check('A10 site whats-new section', /id="whats-new"/.test(site), 'whats-new section missing');
check('A10 site releases link', /github\.com\/jakepi-bot\/flambeee\/releases/.test(site), 'releases link missing');
check('A10 site blog link', /BLOG\.md/.test(site), 'blog link missing');

// --- A11: JS syntax on all touched files ---
function syntaxOK(file, label) {
  const html = fs.readFileSync(file, 'utf8');
  const scripts = html.match(/<script>([\s\S]*?)<\/script>/g) || [];
  let ok = true;
  scripts.forEach((s) => {
    const js = s.replace(/^<script>/, '').replace(/<\/script>$/, '');
    try { new Function(js); } catch (e) { ok = false; console.log('  syntax error: ' + e.message); }
  });
  check('A11 syntax ' + label, ok);
}
syntaxOK(path.join(ROOT, 'archive', 'src-games', 'wordfire.html'), 'wordfire');
syntaxOK(path.join(ROOT, 'archive', 'src-games', 'minesweeper.html'), 'minesweeper');
syntaxOK(path.join(ROOT, 'archive', 'src-games', 'index.html'), 'hub');

console.log('\n' + pass + '/' + (pass + fail) + ' checks passed');
process.exit(fail ? 1 : 0);
