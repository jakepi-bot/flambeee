'use strict';
/* SALTLINE balance harness (Session 60, Stories 133 and 137).
 *
 * Plain node, no dependencies, nonzero exit on any gate miss. Run from the
 * repo root:  node docs/test-plans/session60-saltline-balance.js [G] [S] [D]
 * Optional overrides (Plan B levers, FR-20 order): G=GUST_P, S=STORM_P,
 * D=GAIN_DIV. Defaults are the game constants in website/games/saltline.html.
 *
 * Leg 1 (AC-8, gating): draw ten values from mulberry32(7). They must equal
 * 0.564225, 0.722005, 0.528207, 0.901646, 0.417482, 0.088381, 0.669771,
 * 0.932160, 0.406154, 0.985101, hence gust 0,0,0,0,1,1,0,0,1,0 at
 * GUST_P 0.40 / STORM_P 0.08. A naive JS `*` multiply on doubles gives
 * 0.901647, 0.932167, 0.985102 at positions 4, 8, 10 and FAILS. Exact 32-bit
 * multiply via Math.imul is required. The balance leg never runs if this
 * leg fails, because its numbers would mean nothing.
 *
 * Leg 2 (AC-9, gating): 400 seeds (0..399) x 3 policies = 1200 runs of
 * 60 ticks each. Tick order per run: (1) action: push resolves
 * p = min(PMAX, p + min(floor(passes^2/GAIN_DIV), GAIN_CAP)), passes = 0,
 * else passes = min(passes+1, PASSCAP); (2) gust: p = p - gust[t];
 * (3) flood: p <= 0 loses. Ticks survived counts completed ticks (death
 * during 0-indexed tick k records k+1); 60 completed ticks with p > 0 wins.
 * Policies: P_skill = push if p <= 1, else push if p <= 2 and passes >= 5;
 * P_rhythm = push every 6th tick, interpreted as 1-indexed ticks 6, 12, ...
 * 60 (0-indexed t with (t + 1) % 6 === 0); P_mash = push if passes >= 1.
 * Seeds are RAW (0..399 used directly, no generation re-roll); the page's
 * storm-in-first-20 re-roll only changes which seed is dealt, and the raw
 * reading reproduces the design calibration exactly (0.733/51.2,
 * 0.642/48.3, 0.000/11.3), so raw is the reproducible choice.
 */

function mulberry32(a){ a = a >>> 0; return function(){ a = (a + 0x6D2B79F5) >>> 0; let t = (a ^ (a >>> 15)) >>> 0; t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) >>> 0; t = (t ^ (t >>> 14)) >>> 0; return t / 4294967296; }; }

/* ---- tuning (game defaults; argv overrides for Plan B re-runs) ---- */
var TICKS = 60;
var P0 = 6;
var PMAX = 8;
var GAIN_CAP = 6;
var PASSCAP = 8;
var GUST_P = process.argv[2] === undefined ? 0.40 : parseFloat(process.argv[2]);
var STORM_P = process.argv[3] === undefined ? 0.08 : parseFloat(process.argv[3]);
var GAIN_DIV = process.argv[4] === undefined ? 6 : parseInt(process.argv[4], 10);

function fail(msg) { console.log('FAIL: ' + msg); process.exit(1); }

/* ---- Leg 1: AC-8 seed-7 vector ---- */
var EXPECTED = ['0.564225', '0.722005', '0.528207', '0.901646', '0.417482',
  '0.088381', '0.669771', '0.932160', '0.406154', '0.985101'];
var EXPECTED_GUST = [0, 0, 0, 0, 1, 1, 0, 0, 1, 0];
var REF_G = 0.40;
var REF_S = 0.08;

var rng = mulberry32(7);
var draws = [];
for (var i = 0; i < 10; i++) draws.push(rng());
var printed = draws.map(function (v) { return v.toFixed(6); });
console.log('AC-8 draws: ' + printed.join(', '));
var gustMap = draws.map(function (v) { return v < REF_S ? 2 : (v < REF_S + REF_G ? 1 : 0); });
console.log('AC-8 gust:  ' + gustMap.join(','));
for (var k = 0; k < 10; k++) {
  if (printed[k] !== EXPECTED[k]) fail('AC-8 draw ' + (k + 1) + ' is ' + printed[k] + ', want ' + EXPECTED[k]);
  if (gustMap[k] !== EXPECTED_GUST[k]) fail('AC-8 gust ' + (k + 1) + ' is ' + gustMap[k] + ', want ' + EXPECTED_GUST[k]);
}
console.log('AC-8 PASS');

/* ---- Leg 2: AC-9 balance model ---- */
function gustStream(seed) {
  var r = mulberry32(seed);
  var g = [];
  for (var t = 0; t < TICKS; t++) {
    var u = r();
    g.push(u < STORM_P ? 2 : (u < STORM_P + GUST_P ? 1 : 0));
  }
  return g;
}

function runSeed(seed, policy) {
  var p = P0;
  var passes = 0;
  var g = gustStream(seed);
  for (var t = 0; t < TICKS; t++) {
    if (policy(p, passes, t)) {
      var gain = Math.min(Math.floor((passes * passes) / GAIN_DIV), GAIN_CAP);
      p = Math.min(PMAX, p + gain);
      passes = 0;
    } else {
      passes = Math.min(passes + 1, PASSCAP);
    }
    p = p - g[t];
    if (p <= 0) return { win: false, ticks: t + 1 };
  }
  return { win: true, ticks: TICKS };
}

function pSkill(p, passes) { return p <= 1 ? true : (p <= 2 && passes >= 5); }
function pRhythm(p, passes, t) { return ((t + 1) % 6) === 0; }
function pMash(p, passes) { return passes >= 1; }

function summarize(name, policy) {
  var wins = 0;
  var tickSum = 0;
  var minTicks = TICKS;
  for (var s = 0; s < 400; s++) {
    var r = runSeed(s, policy);
    if (r.win) wins++;
    tickSum += r.ticks;
    if (r.ticks < minTicks) minTicks = r.ticks;
  }
  return { name: name, wr: wins / 400, mean: tickSum / 400, min: minTicks };
}

var skill = summarize('P_skill', pSkill);
var rhythm = summarize('P_rhythm', pRhythm);
var mash = summarize('P_mash', pMash);
var separation = skill.wr - mash.wr;
var meanGap = skill.mean - mash.mean;
var minAll = Math.min(skill.min, rhythm.min, mash.min);

console.log('tuning: GUST_P=' + GUST_P + ' STORM_P=' + STORM_P + ' GAIN_DIV=' + GAIN_DIV +
  ' (TICKS=60 P0=6 PMAX=8 GAIN_CAP=6 PASSCAP=8, seeds 0..399 raw)');
console.log('P_skill : win rate ' + skill.wr.toFixed(3) + ' mean ticks ' + skill.mean.toFixed(1));
console.log('P_rhythm: win rate ' + rhythm.wr.toFixed(3) + ' mean ticks ' + rhythm.mean.toFixed(1));
console.log('P_mash  : win rate ' + mash.wr.toFixed(3) + ' mean ticks ' + mash.mean.toFixed(1));
console.log('separation (skill-mash): ' + separation.toFixed(3));
console.log('mean gap (skill-mash):   ' + meanGap.toFixed(1));
console.log('min survival (1200 runs): ' + minAll);

var misses = [];
if (!(skill.wr >= 0.60)) misses.push('P_skill ' + skill.wr.toFixed(3) + ' < 0.60');
if (!(rhythm.wr >= 0.45 && rhythm.wr <= 0.80)) misses.push('P_rhythm ' + rhythm.wr.toFixed(3) + ' outside [0.45, 0.80]');
if (!(mash.wr <= 0.05)) misses.push('P_mash ' + mash.wr.toFixed(3) + ' > 0.05');
if (!(separation >= 0.55)) misses.push('separation ' + separation.toFixed(3) + ' < 0.55');
if (!(meanGap >= 30)) misses.push('mean gap ' + meanGap.toFixed(1) + ' < 30');
if (!(minAll >= 8)) misses.push('min survival ' + minAll + ' < 8');

if (misses.length > 0) {
  console.log('AC-9 GATE: MISS (' + misses.join('; ') + ')');
  process.exit(1);
}
console.log('AC-9 GATE: PASS');
