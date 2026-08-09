#!/usr/bin/env node
/* v0.5.0 logic checks — Simon difficulty timing + stats record logic.
 * Mirrors the exact math in src/simon.html and the stats helpers in the games.
 * Run: node docs/test-plans/v0.5.0-logic-check.js
 */
'use strict';

let pass = 0, fail = 0;
function check(name, cond) {
  if (cond) { pass++; console.log('  PASS ' + name); }
  else { fail++; console.log('  FAIL ' + name); }
}

// --- Simon difficulty presets (must match src/simon.html) ---
const DIFFICULTIES = {
  easy:   { flash: 800, gap: 300, flashStep: 20, gapStep: 10, flashFloor: 350, gapFloor: 120 },
  classic: { flash: 600, gap: 200, flashStep: 30, gapStep: 10, flashFloor: 200, gapFloor: 80 },
  hard:   { flash: 450, gap: 150, flashStep: 40, gapStep: 15, flashFloor: 120, gapFloor: 50 }
};

function getFlashDuration(diff, round) {
  const d = DIFFICULTIES[diff];
  return Math.max(d.flashFloor, d.flash - (round - 1) * d.flashStep);
}
function getGapDuration(diff, round) {
  const d = DIFFICULTIES[diff];
  return Math.max(d.gapFloor, d.gap - (round - 1) * d.gapStep);
}

console.log('Simon difficulty timing:');
// Round 1 ordering: easy > classic > hard
check('round1 flash easy(800) > classic(600)', getFlashDuration('easy', 1) > getFlashDuration('classic', 1));
check('round1 flash classic(600) > hard(450)', getFlashDuration('classic', 1) > getFlashDuration('hard', 1));
check('round1 gap easy(300) > classic(200)', getGapDuration('easy', 1) > getGapDuration('classic', 1));
check('round1 gap classic(200) > hard(150)', getGapDuration('classic', 1) > getGapDuration('hard', 1));
// Floors respected
check('easy flash floor 350', getFlashDuration('easy', 100) === 350);
check('classic flash floor 200', getFlashDuration('classic', 100) === 200);
check('hard flash floor 120', getFlashDuration('hard', 100) === 120);
check('easy gap floor 120', getGapDuration('easy', 100) === 120);
check('classic gap floor 80', getGapDuration('classic', 100) === 80);
check('hard gap floor 50', getGapDuration('hard', 100) === 50);
// Monotonic non-increasing
check('hard round2 flash <= round1', getFlashDuration('hard', 2) <= getFlashDuration('hard', 1));
check('easy round2 gap <= round1', getGapDuration('easy', 2) <= getGapDuration('easy', 1));

// --- Per-difficulty best key (must match src/simon.html) ---
function bestKey(diff) {
  return diff === 'classic' ? 'flambeee-simon-best' : 'flambeee-simon-best-' + diff;
}
console.log('Simon best keys:');
check('classic uses legacy key', bestKey('classic') === 'flambeee-simon-best');
check('easy key', bestKey('easy') === 'flambeee-simon-best-easy');
check('hard key', bestKey('hard') === 'flambeee-simon-best-hard');

// --- Stats record logic (mirrors minesweeper/2048/simon helpers) ---
function recordGame(stats, won, elapsed) {
  stats.plays += 1;
  if (won) {
    stats.wins += 1;
    if (stats.bestTime === null || elapsed < stats.bestTime) stats.bestTime = elapsed;
  }
  return stats;
}
console.log('Stats record logic:');
let s = { plays: 0, wins: 0, bestTime: null };
recordGame(s, false, 12);
check('loss counts play only', s.plays === 1 && s.wins === 0 && s.bestTime === null);
recordGame(s, true, 10);
check('win counts play+win, sets bestTime', s.plays === 2 && s.wins === 1 && s.bestTime === 10);
recordGame(s, true, 8);
check('faster win updates bestTime', s.bestTime === 8);
recordGame(s, true, 15);
check('slower win keeps bestTime', s.bestTime === 8);

// 2048: win = play + win (single record)
function record2048Win(stats) { stats.plays += 1; stats.wins += 1; return stats; }
let t = { plays: 0, wins: 0 };
record2048Win(t);
check('2048 win counts play+win once', t.plays === 1 && t.wins === 1);

// Corrupt JSON handling: loadStats returns defaults
function loadStats(raw) {
  try { if (raw) return JSON.parse(raw); } catch (e) { /* private mode */ }
  return { plays: 0, wins: 0 };
}
check('corrupt stats JSON -> defaults', loadStats('{not json').plays === 0);
check('null stats -> defaults', loadStats(null).plays === 0);
check('valid stats parsed', loadStats('{"plays":3,"wins":1}').plays === 3);

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
