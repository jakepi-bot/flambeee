#!/usr/bin/env node
/* Story 091 RED/GREEN harness: FPS playable echo-rounds slice in harness.
 * Plain node, no dependency. Serves dev/fps-probe/echo-rounds-slice-091.html
 * with ?slice091=1, launches Chromium at 1280x800 DPR 1x, collects the JSON
 * the slice POSTs to /results, then asserts the playable-round acceptance
 * checks. Exit 0 on green, 1 on RED/failure.
 * Usage: node playable-slice-check-091.js [chromium|firefox]
 *
 * Falsifying rule (stated before code, Story 091 section 1): a slice that
 * drops input under the real loop is a fail. If, once the full round runs
 * (dark room plus targets plus pulses plus hit gate), simultaneous
 * move/look/fire drops or desyncs input, or the frame rate falls out of
 * readability, the slice fails and no acceptance is claimed.
 */
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const PROBE = path.join(__dirname, 'echo-rounds-slice-091.html');
const FIREFOX = '/home/jake/.hermes/profiles/flambeee/cache/scratch/firefox/firefox';
const P95_LO = 15.84, P95_HI = 17.50, WARMUP = 30, MIN_FRAMES = 600;
const WANT_W = 1280, WANT_H = 800;

function launch(browser, url, profileDir) {
  if (browser === 'chromium') {
    return spawn('chromium', [
      '--headless=new', '--no-sandbox', '--disable-gpu',
      '--window-size=' + WANT_W + ',' + WANT_H,
      '--force-device-scale-factor=1',
      '--no-first-run', '--no-default-browser-check',
      '--user-data-dir=' + profileDir, url
    ], { stdio: 'ignore' });
  }
  return spawn(FIREFOX, ['--headless', '--no-remote', '--profile', profileDir, url],
    { stdio: 'ignore' });
}

function check(name, cond, detail) {
  return { name: name, pass: !!cond, detail: detail };
}

function evaluate(r) {
  if (!r || r.mode !== 'playable-slice-091') {
    return { green: false, red: true, rows: [],
      note: 'RED: no playable-slice-091 mode in probe result (mode=' +
        ((r && r.mode) || 'missing') + '). Playable slice not implemented.' };
  }
  const rows = [];
  rows.push(check('round renders at 1280x800 DPR 1x',
    r.renderW === WANT_W && r.renderH === WANT_H && r.devicePixelRatio === 1,
    'render=' + r.renderW + 'x' + r.renderH + ' dpr=' + r.devicePixelRatio +
    ' viewport=' + r.viewportW + 'x' + r.viewportH));
  rows.push(check('one round plays end to end (win or lose screen)',
    (r.roundOutcome === 'win' || r.roundOutcome === 'lose') &&
    (r.winScreen === true || r.loseScreen === true) && r.roomCleared === (r.roundOutcome === 'win'),
    'outcome=' + r.roundOutcome + ' win=' + r.winScreen + ' lose=' + r.loseScreen +
    ' cleared=' + r.roomCleared));
  rows.push(check('look yaw tracks mouse input',
    r.lookEventsInjected > 0 && r.lookEventsApplied === r.lookEventsInjected &&
    Math.abs(r.lookYawDelta) > 0,
    'injected=' + r.lookEventsInjected + ' applied=' + r.lookEventsApplied +
    ' yawDelta=' + r.lookYawDelta));
  rows.push(check('look pitch tracks mouse input',
    Math.abs(r.lookPitchDelta) > 0,
    'pitchDelta=' + r.lookPitchDelta));
  rows.push(check('fire-move-look survives, no stuck input',
    r.fireMoveLookSurvived === true && r.stuckInputs === 0 && r.inputDrops === 0,
    'survived=' + r.fireMoveLookSurvived + ' stuck=' + r.stuckInputs +
    ' drops=' + r.inputDrops + ' pointerLock=' + r.pointerLock));
  rows.push(check('click-to-shoot one-click-one-pulse with fade',
    r.clickShots > 0 && r.pulsesEmitted === r.clickShots &&
    r.pulsesFaded === r.pulsesEmitted,
    'clicks=' + r.clickShots + ' pulses=' + r.pulsesEmitted +
    ' faded=' + r.pulsesFaded));
  rows.push(check('lit-target hit gate (lit hits, unlit misses)',
    r.litHits >= 1 && r.litHitRate === 1 && r.unlitShots >= 1 && r.unlitHits === 0,
    'litHits=' + r.litHits + ' unlitShots=' + r.unlitShots +
    ' unlitHits=' + r.unlitHits));
  rows.push(check('shooter-revealed flag per shot',
    r.shots > 0 && r.shooterReveals === r.shots,
    'shots=' + r.shots + ' reveals=' + r.shooterReveals));
  rows.push(check('frame count after warmup >= 600',
    r.framesCounted >= MIN_FRAMES && r.warmupExcluded === WARMUP,
    'counted=' + r.framesCounted + ' warmup=' + r.warmupExcluded +
    ' total=' + r.framesTotal));
  const p95ok = typeof r.frameP95MsCounted === 'number' &&
    r.frameP95MsCounted >= P95_LO && r.frameP95MsCounted <= P95_HI;
  rows.push(check('p95 in 15.84-17.50ms band',
    p95ok, 'p95=' + r.frameP95MsCounted + ' mean=' + r.frameMeanMsCounted));
  rows.push(check('slow frames over 33ms reported',
    typeof r.slowFramesOver33ms === 'number',
    'slow=' + r.slowFramesOver33ms));
  const slowOk = r.slowFramesOver33ms === 0;
  const green = rows.every((x) => x.pass) && p95ok && slowOk;
  return { green: green, red: false, rows: rows,
    note: green ? 'GREEN: playable echo-rounds slice proven.' :
      'FAIL: one or more playable-slice checks failed (see rows).' };
}

function main() {
  const browser = process.argv[2] || 'chromium';
  if (browser !== 'chromium' && browser !== 'firefox') {
    console.error('usage: node playable-slice-check-091.js [chromium|firefox]');
    process.exit(2);
  }
  let html = null;
  try { html = fs.readFileSync(PROBE, 'utf8'); } catch (e) { html = null; }
  const need = ['slice091', 'roomCleared', 'roundOutcome', 'winScreen',
    'lookPitchDelta', 'clickShots', 'litHits', 'framesCounted'];
  const missing = !html ? need :
    need.filter((k) => html.indexOf(k) === -1);
  let child = null, settled = false;
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'slice091-' + browser + '-'));
  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/results') {
      let body = '';
      req.on('data', (c) => { body += c; });
      req.on('end', () => {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('ok');
        if (!settled) {
          settled = true;
          let result = null;
          try { result = JSON.parse(body); } catch (e) { result = null; }
          console.log('raw: ' + body);
          if (missing.length) {
            console.log('RED: slice HTML lacks playable-round symbols: ' +
              missing.join(', '));
            console.log('gamepad leg: OPEN-BLOCKED-ON-HARDWARE ' +
              '(zero gamepad samples claimed by this run: none taken here).');
            cleanup(1);
            return;
          }
          const v = evaluate(result);
          v.rows.forEach((x) => console.log(
            (x.pass ? 'PASS' : 'FAIL') + ' ' + x.name + ' [' + x.detail + ']'));
          console.log(v.note);
          console.log('gamepad leg: OPEN-BLOCKED-ON-HARDWARE ' +
            '(gamepadNonEmpty=' +
            ((result && result.gamepadNonEmpty) || 0) +
            ', no controller claim).');
          cleanup(v.green ? 0 : 1);
        }
      });
    } else {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(html || 'missing');
    }
  });
  function cleanup(code) {
    try { if (child) child.kill('SIGKILL'); } catch (e) { /* gone */ }
    server.close(() => process.exit(code));
    setTimeout(() => process.exit(code), 2000).unref();
  }
  server.listen(0, '127.0.0.1', () => {
    if (missing.length && !html) {
      settled = true;
      console.log('RED: slice HTML not found at dev/fps-probe/echo-rounds-slice-091.html.');
      console.log('Falsifying rule: a slice that drops input under the real loop is a fail.');
      console.log('gamepad leg: OPEN-BLOCKED-ON-HARDWARE ' +
        '(zero gamepad samples claimed by this run: none taken here).');
      cleanup(1);
      return;
    }
    const port = server.address().port;
    const url = 'http://127.0.0.1:' + port + '/?slice091=1';
    try {
      child = launch(browser, url, profileDir);
      child.on('error', (e) => {
        if (!settled) {
          settled = true;
          console.log('LAUNCH-ERROR: ' + e.message);
          cleanup(1);
        }
      });
    } catch (e) {
      if (!settled) {
        settled = true;
        console.log('LAUNCH-ERROR: ' + e.message);
        cleanup(1);
      }
    }
  });
  setTimeout(() => {
    if (!settled) {
      settled = true;
      console.error('TIMEOUT: no /results POST within 60s');
      cleanup(3);
    }
  }, 60000);
}

main();
