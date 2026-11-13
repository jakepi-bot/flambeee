'use strict';
/* SALTLINE balance harness (Session 60, Stories 133 and 137).
 * Amended 2026-11-13 in the release wave under the jakebot ruling of 02:15 CST
 * and the parent/Scout NO-GO of the dev wave: the gate population is the set
 * of seeds the page can actually deal, and minimum survival is gated per
 * policy (P_skill >= 8, P_rhythm >= 8, P_mash report-only).
 *
 * Plain node, no dependencies, nonzero exit on any gate miss. Run from the
 * repo root:  node docs/test-plans/session60-saltline-balance.js [G] [S] [D]
 * Optional overrides (Plan B levers, FR-20 order): G=GUST_P, S=STORM_P,
 * D=GAIN_DIV. Defaults are read from website/games/saltline.html and asserted
 * equal, so the harness cannot silently drift from the shipped file.
 *
 * Leg 0 (mirror): the tuning constants in website/games/saltline.html must
 * equal the values this harness uses (TICKS, TICK_MS, P0, PMAX, GAIN_DIV,
 * GAIN_CAP, PASSCAP, GUST_P, STORM_P, FAIR_TICKS). A drift fails the run.
 *
 * Leg 1 (AC-8, gating): draw ten values from mulberry32(7). They must equal
 * 0.564225, 0.722005, 0.528207, 0.901646, 0.417482, 0.088381, 0.669771,
 * 0.932160, 0.406154, 0.985101, hence gust 0,0,0,0,1,1,0,0,1,0 at
 * GUST_P 0.40 / STORM_P 0.08. A naive JS `*` multiply on doubles gives
 * 0.901647, 0.932167, 0.985102 at positions 4, 8, 10 and FAILS. Exact 32-bit
 * multiply via Math.imul is required. The balance legs never run if this
 * leg fails, because their numbers would mean nothing.
 *
 * Leg 2 (deal construction, gating): a seed is dealt only if ticks 0..19
 * contain a storm and the first FAIR_TICKS=8 ticks survive under both
 * disciplined policies. This mirrors dealAccepts() in the game file. The
 * population is reported as three integers: raw seeds in range, seeds that
 * pass the storm rule, seeds that pass both rules.
 *
 * Leg 3 (AC-9, gating, accepted population): every accepted seed of 0..399
 * under all three policies. Thresholds: P_skill win rate >= 0.60; P_rhythm
 * in [0.45, 0.80]; P_mash <= 0.05; separation P_skill minus P_mash >= 0.55;
 * mean ticks P_skill minus P_mash >= 30; P_skill minimum survival >= 8;
 * P_rhythm minimum survival >= 8. P_mash minimum survival is reported, never
 * gated (mashing is the taught failure). The aggregate all-policy minimum is
 * retired as a gate and reported as a statistic.
 *
 * Leg 4 (structural, gating): for every accepted seed, max-achievable
 * survival over the first 8 ticks (state-space search with full knowledge of
 * the gust stream) is >= 8. Acceptance already implies this through
 * P_skill >= 8; the leg exists so a later filter change cannot reopen the
 * defect that blocked the Session 60 dev wave.
 *
 * Leg 5 (report only): the same three policies over the raw 0..399 set with
 * no deal filter, printed alongside so the dealt numbers have a baseline.
 *
 * Plan B levers apply only to the win-rate, separation, and gap legs. A
 * minimum-survival miss is a deal-construction defect: it is not tuned away.
 */
var fs = require('fs');
var path = require('path');

function mulberry32(a){ a = a >>> 0; return function(){ a = (a + 0x6D2B79F5) >>> 0; let t = (a ^ (a >>> 15)) >>> 0; t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) >>> 0; t = (t ^ (t >>> 14)) >>> 0; return t / 4294967296; }; }

/* ---- tuning (game defaults; argv overrides for Plan B re-runs) ---- */
var TICKS = 60;
var TICK_MS = 600;
var P0 = 6;
var PMAX = 8;
var GAIN_CAP = 6;
var PASSCAP = 8;
var FAIR_TICKS = 8;
/* Tuning overrides are positional only (G S D); flags like --accepts must
 * never be parsed as numbers. */
var posArgs = process.argv.slice(2).filter(function (a) { return !/^--/.test(a); });
var GUST_P = posArgs[0] === undefined ? 0.40 : parseFloat(posArgs[0]);
var STORM_P = posArgs[1] === undefined ? 0.08 : parseFloat(posArgs[1]);
var GAIN_DIV = posArgs[2] === undefined ? 6 : parseInt(posArgs[2], 10);

function fail(msg) { console.log('FAIL: ' + msg); process.exit(1); }
if (!isFinite(GUST_P) || !isFinite(STORM_P) || !isFinite(GAIN_DIV)) {
  fail('tuning arguments must be numbers: GUST_P=' + GUST_P + ' STORM_P=' + STORM_P + ' GAIN_DIV=' + GAIN_DIV);
}
if (posArgs.length > 3) fail('at most three tuning arguments (G S D), got ' + posArgs.length);

/* ---- Leg 0: mirror the shipped constants ---- */
var GAME = 'website/games/saltline.html';
var src;
try { src = fs.readFileSync(path.join(process.cwd(), GAME), 'utf8'); }
catch (e) { fail('cannot read ' + GAME + ' from ' + process.cwd()); }
function constOf(name) {
  var m = src.match(new RegExp('var\\s+' + name + '\\s*=\\s*([0-9.]+)\\s*;'));
  if (!m) fail('Leg 0: constant ' + name + ' not found in ' + GAME);
  return parseFloat(m[1]);
}
var mirror = { TICKS: TICKS, TICK_MS: TICK_MS, P0: P0, PMAX: PMAX, GAIN_DIV: GAIN_DIV, GAIN_CAP: GAIN_CAP, PASSCAP: PASSCAP, GUST_P: GUST_P, STORM_P: STORM_P, FAIR_TICKS: FAIR_TICKS };
var drift = [];
Object.keys(mirror).forEach(function (k) {
  var got = constOf(k);
  if (!(Math.abs(got - mirror[k]) <= 1e-12)) drift.push(k + ' game=' + got + ' harness=' + mirror[k]);
});
if (drift.length) fail('Leg 0: tuning drift between game and harness: ' + drift.join('; '));
console.log('Leg 0 mirror: PASS (10 constants equal in ' + GAME + ')');

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

/* ---- deal construction: mirror of the game's dealAccepts ---- */
function gustStream(seed) {
  var r = mulberry32(seed);
  var g = [];
  for (var t = 0; t < TICKS; t++) {
    var u = r();
    g.push(u < STORM_P ? 2 : (u < STORM_P + GUST_P ? 1 : 0));
  }
  return g;
}
function gainFor(ps) { return Math.min(Math.floor((ps * ps) / GAIN_DIV), GAIN_CAP); }
var pSkill = function (p, passes) { return p <= 1 ? true : (p <= 2 && passes >= 5); };
var pRhythm = function (p, passes, t) { return ((t + 1) % 6) === 0; };
var pMash = function (p, passes) { return passes >= 1; };

/* First FAIR_TICKS of one policy; returns ticks survived 1..FAIR_TICKS. */
function openingSurvival(g, policy) {
  var q = P0, held = 0;
  for (var t = 0; t < FAIR_TICKS; t++) {
    if (policy(q, held, t)) { q = Math.min(PMAX, q + gainFor(held)); held = 0; }
    else { held = Math.min(held + 1, PASSCAP); }
    q -= g[t];
    if (q <= 0) return t + 1;
  }
  return FAIR_TICKS;
}
function hasStormFirst20(g) {
  for (var i = 0; i < 20; i++) if (g[i] === 2) return true;
  return false;
}
function dealAccepts(seed) {
  var g = gustStream(seed);
  if (!hasStormFirst20(g)) return false;
  return openingSurvival(g, pSkill) >= FAIR_TICKS && openingSurvival(g, pRhythm) >= FAIR_TICKS;
}

/* Test hook for the browser mirror leg: --accepts prints one JSON bitmap of
 * dealAccepts for seeds 0..399, then exits. Used by QA to compare the page's
 * window.__saltline.accepts() against this harness implementation. */
if (process.argv.indexOf('--accepts') !== -1) {
  var bitmap = [];
  for (var b = 0; b < 400; b++) bitmap.push(dealAccepts(b) ? 1 : 0);
  console.log('ACCEPTS_JSON: ' + JSON.stringify(bitmap));
  process.exit(0);
}

/* Max-achievable survival over the first H ticks, full knowledge, exact. */
function optimalSurvival(seed, H) {
  var g = gustStream(seed);
  var states = [[P0, 0]];
  var best = 0;
  for (var t = 0; t < H; t++) {
    var seen = {}, next = [];
    for (var i2 = 0; i2 < states.length; i2++) {
      var p = states[i2][0], passes = states[i2][1];
      var cand = [[p - g[t], Math.min(passes + 1, PASSCAP)],
                  [Math.min(PMAX, p + gainFor(passes)) - g[t], 0]];
      for (var c = 0; c < 2; c++) {
        var q = cand[c];
        if (q[0] > 0) { var key = q[0] + ',' + q[1]; if (!seen[key]) { seen[key] = 1; next.push(q); } }
      }
    }
    if (next.length === 0) return t + 1;
    states = next; best = t + 1;
  }
  return best;
}

function runSeed(seed, policy) {
  var p = P0, passes = 0, g = gustStream(seed);
  for (var t = 0; t < TICKS; t++) {
    if (policy(p, passes, t)) { p = Math.min(PMAX, p + gainFor(passes)); passes = 0; }
    else { passes = Math.min(passes + 1, PASSCAP); }
    p -= g[t];
    if (p <= 0) return { win: false, ticks: t + 1 };
  }
  return { win: true, ticks: TICKS };
}

var raw = [];
for (var s = 0; s < 400; s++) raw.push(s);
var storm = raw.filter(function (x) { return hasStormFirst20(gustStream(x)); });
var accepted = raw.filter(dealAccepts);
var rejected = storm.filter(function (x) { return !dealAccepts(x); });
console.log('deal population: raw ' + raw.length + ' | storm-passing ' + storm.length +
  ' | accepted ' + accepted.length + ' (' + (100 * accepted.length / storm.length).toFixed(1) + '% of storm-passing)');
console.log('rejected by the fairness rule: ' + rejected.length + (rejected.length ? ' -> ' + rejected.join(' ') : ''));

function summarize(label, policy, seeds) {
  var wins = 0, sum = 0, min = TICKS, short = [];
  seeds.forEach(function (x) {
    var r = runSeed(x, policy);
    if (r.win) wins++;
    sum += r.ticks;
    if (r.ticks < min) min = r.ticks;
    if (r.ticks < 8) short.push(x + '->' + r.ticks);
  });
  console.log(label + ': win rate ' + (wins / seeds.length).toFixed(3) + ' mean ticks ' +
    (sum / seeds.length).toFixed(1) + ' min survival ' + min +
    ' sub-8 ' + short.length + (short.length ? ' [' + short.join(' ') + ']' : ''));
  return { win: wins / seeds.length, mean: sum / seeds.length, min: min, short: short };
}

/* ---- Leg 3: AC-9 gates on the accepted population ---- */
var tuning = 'GUST_P=' + GUST_P + ' STORM_P=' + STORM_P + ' GAIN_DIV=' + GAIN_DIV +
  ' (TICKS=60 P0=6 PMAX=8 GAIN_CAP=6 PASSCAP=8 FAIR_TICKS=8)';
console.log('tuning: ' + tuning);
console.log('population: accepted seeds (the deals the page can hand out)');
var skill = summarize('P_skill ', pSkill, accepted);
var rhythm = summarize('P_rhythm', pRhythm, accepted);
var mash = summarize('P_mash  ', pMash, accepted);
var separation = skill.win - mash.win;
var meanGap = skill.mean - mash.mean;
console.log('separation (skill-mash): ' + separation.toFixed(3));
console.log('mean gap (skill-mash):   ' + meanGap.toFixed(1));
console.log('aggregate min survival (statistic, not a gate): ' + Math.min(skill.min, rhythm.min, mash.min));

/* ---- Leg 4: structural optimal-survival leg ---- */
var optBad = [];
accepted.forEach(function (x) { var v = optimalSurvival(x, 8); if (v < 8) optBad.push(x + '->' + v); });
console.log('structural: max-achievable survival >= 8 on ' + accepted.length + ' accepted seeds: ' +
  (optBad.length ? 'FAIL ' + optBad.join(' ') : 'PASS'));

/* ---- Leg 5: raw report only ---- */
console.log('raw population (report only, no deal filter):');
var rawSkill = summarize('  P_skill ', pSkill, raw);
var rawRhythm = summarize('  P_rhythm', pRhythm, raw);
var rawMash = summarize('  P_mash  ', pMash, raw);

/* ---- gates ---- */
var misses = [];
if (!(skill.win >= 0.60)) misses.push('P_skill win ' + skill.win.toFixed(3) + ' < 0.60');
if (!(rhythm.win >= 0.45 && rhythm.win <= 0.80)) misses.push('P_rhythm win ' + rhythm.win.toFixed(3) + ' outside [0.45, 0.80]');
if (!(mash.win <= 0.05)) misses.push('P_mash win ' + mash.win.toFixed(3) + ' > 0.05');
if (!(separation >= 0.55)) misses.push('separation ' + separation.toFixed(3) + ' < 0.55');
if (!(meanGap >= 30)) misses.push('mean gap ' + meanGap.toFixed(1) + ' < 30');
if (!(skill.min >= 8)) misses.push('P_skill min survival ' + skill.min + ' < 8');
if (!(rhythm.min >= 8)) misses.push('P_rhythm min survival ' + rhythm.min + ' < 8');
if (optBad.length) misses.push('structural: accepted seed dies before 8 under optimal play');
if (!(accepted.length / storm.length >= 0.85)) misses.push('deal acceptance ' + accepted.length + '/' + storm.length + ' < 0.85');

if (misses.length > 0) {
  console.log('AC-9 GATE: MISS (' + misses.join('; ') + ')');
  process.exit(1);
}
console.log('AC-9 GATE: PASS');
