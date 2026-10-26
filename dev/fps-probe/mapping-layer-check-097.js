#!/usr/bin/env node
/* Story 097 RED/GREEN harness: FPS controller-mapping-layer slice in harness.
 * Plain node, no dependency. Serves
 * dev/fps-probe/echo-rounds-mapped-097.html, launches Chromium at 1280x800
 * DPR 1x, collects the JSON the mapped slice POSTs to /results, then asserts
 * the mapping-layer acceptance checks. Exit 0 on green, 1 on RED/failure.
 * Usage: node mapping-layer-check-097.js [chromium]
 *
 * Falsifying rule (Story 097 section: wire-drivable slice cited, or P1 is
 * the wrong shape): a layer that drops input under the real loop is a fail.
 */
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const LAYER = path.join(__dirname, 'input-mapping-layer-097.js');
const MAPPED = path.join(__dirname, 'echo-rounds-mapped-097.html');
const P95_LO = 15.84, P95_HI = 17.50, WARMUP = 30, MIN_FRAMES = 600;
const WANT_W = 1280, WANT_H = 800;

function launch(url, profileDir) {
  return spawn('chromium', [
    '--headless=new', '--no-sandbox', '--disable-gpu',
    '--window-size=' + WANT_W + ',' + WANT_H,
    '--force-device-scale-factor=1',
    '--no-first-run', '--no-default-browser-check',
    '--user-data-dir=' + profileDir, url
  ], { stdio: 'ignore' });
}

function check(name, cond, detail) {
  return { name: name, pass: !!cond, detail: detail };
}

function evaluate(r) {
  if (!r || r.mode !== 'mapped-slice-097') {
    return { green: false, red: true, rows: [],
      note: 'RED: no mapped-slice-097 mode in probe result (mode=' +
        ((r && r.mode) || 'missing') + '). Mapping layer not implemented.' };
  }
  const rows = [];
  rows.push(check('mapping layer present and drove the round',
    r.mappingLayer === true && r.layerResolutions > 0,
    'mappingLayer=' + r.mappingLayer + ' resolutions=' + r.layerResolutions));
  rows.push(check('keyboard path through layer (WASD + look + click fire)',
    r.kbMoveFrames > 0 && r.kbLookEvents > 0 && r.kbFireIntents > 0,
    'kbMove=' + r.kbMoveFrames + ' kbLook=' + r.kbLookEvents +
    ' kbFire=' + r.kbFireIntents));
  rows.push(check('round renders at 1280x800 DPR 1x',
    r.renderW === WANT_W && r.renderH === WANT_H && r.devicePixelRatio === 1,
    'render=' + r.renderW + 'x' + r.renderH + ' dpr=' + r.devicePixelRatio +
    ' viewport=' + r.viewportW + 'x' + r.viewportH));
  rows.push(check('one round plays end to end (win or lose screen)',
    (r.roundOutcome === 'win' || r.roundOutcome === 'lose') &&
    (r.winScreen === true || r.loseScreen === true) &&
    r.roomCleared === (r.roundOutcome === 'win'),
    'outcome=' + r.roundOutcome + ' win=' + r.winScreen + ' lose=' +
    r.loseScreen + ' cleared=' + r.roomCleared));
  rows.push(check('look yaw tracks input through layer',
    r.lookEventsInjected > 0 && r.lookEventsApplied === r.lookEventsInjected &&
    Math.abs(r.lookYawDelta) > 0,
    'injected=' + r.lookEventsInjected + ' applied=' + r.lookEventsApplied +
    ' yawDelta=' + r.lookYawDelta));
  rows.push(check('look pitch tracks input through layer',
    Math.abs(r.lookPitchDelta) > 0,
    'pitchDelta=' + r.lookPitchDelta));
  rows.push(check('fire-move-look survives, no stuck input',
    r.fireMoveLookSurvived === true && r.stuckInputs === 0 &&
    r.inputDrops === 0,
    'survived=' + r.fireMoveLookSurvived + ' stuck=' + r.stuckInputs +
    ' drops=' + r.inputDrops + ' pointerLock=' + r.pointerLock));
  rows.push(check('click-to-shoot one-click-one-pulse with fade',
    r.clickShots > 0 && r.pulsesEmitted === r.clickShots &&
    r.pulsesFaded === r.pulsesEmitted,
    'clicks=' + r.clickShots + ' pulses=' + r.pulsesEmitted +
    ' faded=' + r.pulsesFaded));
  rows.push(check('lit-target hit gate (lit hits, unlit misses)',
    r.litHits >= 1 && r.litHitRate === 1 && r.unlitShots >= 1 &&
    r.unlitHits === 0,
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
  rows.push(check('synthetic gamepad table resolves (STRUCTURAL ONLY)',
    r.synthTablePass === true && r.synthHardwareSamples === 0,
    'pass=' + r.synthTablePass + ' hwSamples=' + r.synthHardwareSamples +
    ' cases=' + r.synthCasesRun + '/' + r.synthCasesTotal));
  const slowOk = r.slowFramesOver33ms === 0;
  const green = rows.every((x) => x.pass) && p95ok && slowOk;
  return { green: green, red: false, rows: rows,
    note: green ? 'GREEN: mapping layer proven through keyboard path.' :
      'FAIL: one or more mapping-layer checks failed (see rows).' };
}

function staticCheck() {
  let layer = null, mapped = null;
  try { layer = fs.readFileSync(LAYER, 'utf8'); } catch (e) { layer = null; }
  try { mapped = fs.readFileSync(MAPPED, 'utf8'); } catch (e) {
    mapped = null;
  }
  const needLayer = ['mapping097', 'resolveGamepadPoll',
    'resolveKeyboardIntent', 'INTENT_TABLE'];
  const missingLayer = !layer ? needLayer :
    needLayer.filter((k) => layer.indexOf(k) === -1);
  const needMapped = ['mapped097', 'mapping097', 'mapped-slice-097',
    'resolveKeyboardIntent', 'resolveGamepadPoll', 'synthTablePass'];
  const missingMapped = !mapped ? needMapped :
    needMapped.filter((k) => mapped.indexOf(k) === -1);
  return { missingLayer: missingLayer, missingMapped: missingMapped };
}

function main() {
  const missing = staticCheck();
  if (missing.missingLayer.length || missing.missingMapped.length) {
    console.log('RED: mapping layer not implemented on this tree.');
    if (missing.missingLayer.length) {
      console.log('RED: layer file lacks symbols: ' +
        missing.missingLayer.join(', '));
    }
    if (missing.missingMapped.length) {
      console.log('RED: mapped slice lacks symbols: ' +
        missing.missingMapped.join(', '));
    }
    console.log('Falsifying rule: a layer that drops input under the ' +
      'real loop is a fail.');
    console.log('gamepad leg: OPEN-BLOCKED-ON-HARDWARE ' +
      '(zero gamepad samples claimed by this run: none taken here).');
    process.exit(1);
  }
  let html = null;
  try { html = fs.readFileSync(MAPPED, 'utf8'); } catch (e) { html = null; }
  if (!html) {
    console.log('RED: mapped slice not found at ' +
      'dev/fps-probe/echo-rounds-mapped-097.html.');
    process.exit(1);
  }
  let child = null, settled = false;
  const profileDir =
    fs.mkdtempSync(path.join(os.tmpdir(), 'mapped097-chromium-'));
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
          const v = evaluate(result);
          v.rows.forEach((x) => console.log(
            (x.pass ? 'PASS' : 'FAIL') + ' ' + x.name + ' [' + x.detail +
            ']'));
          console.log(v.note);
          console.log('gamepad leg: OPEN-BLOCKED-ON-HARDWARE ' +
            '(gamepadNonEmpty=' +
            ((result && result.gamepadNonEmpty) || 0) +
            ', synthHardwareSamples=' +
            ((result && result.synthHardwareSamples) || 0) +
            ', no controller claim).');
          cleanup(v.green ? 0 : 1);
        }
      });
    } else {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(html);
    }
  });
  function cleanup(code) {
    try { if (child) child.kill('SIGKILL'); } catch (e) { /* gone */ }
    server.close(() => process.exit(code));
    setTimeout(() => process.exit(code), 2000).unref();
  }
  server.listen(0, '127.0.0.1', () => {
    const port = server.address().port;
    const url = 'http://127.0.0.1:' + port + '/?mapped097=1';
    try {
      child = launch(url, profileDir);
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
