#!/usr/bin/env node
/* Story 071 harness. No dependency beyond node itself.
 * Serves dev/fps-probe/echo-rounds-probe.html, launches a browser pointed
 * at it, collects the JSON the probe POSTs to /results, prints it.
 * Usage: node run-probe.js <chromium|firefox> [query]
 * Example: node run-probe.js chromium ""
 *          node run-probe.js firefox "empty=1"
 */
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const PROBE = path.join(__dirname, 'echo-rounds-probe.html');
const FIREFOX = '/home/jake/.hermes/profiles/flambeee/cache/scratch/firefox/firefox';

function launch(browser, url, profileDir) {
  if (browser === 'chromium') {
    return spawn('chromium', [
      '--headless=new', '--no-sandbox', '--disable-gpu',
      '--no-first-run', '--no-default-browser-check',
      '--user-data-dir=' + profileDir, url
    ], { stdio: 'ignore' });
  }
  return spawn(FIREFOX, [
    '--headless', '--no-remote', '--profile', profileDir, url
  ], { stdio: 'ignore' });
}

function main() {
  const browser = process.argv[2];
  const query = process.argv[3] || '';
  if (browser !== 'chromium' && browser !== 'firefox') {
    console.error('usage: node run-probe.js <chromium|firefox> [query]');
    process.exit(2);
  }
  const html = fs.readFileSync(PROBE, 'utf8');
  let child = null;
  let settled = false;
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'probe-' + browser + '-'));

  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/results') {
      let body = '';
      req.on('data', (c) => { body += c; });
      req.on('end', () => {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('ok');
        if (!settled) {
          settled = true;
          console.log(body);
          cleanup(0);
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
    const url = 'http://127.0.0.1:' + port + '/' + (query ? '?' + query : '');
    child = launch(browser, url, profileDir);
  });

  setTimeout(() => {
    if (!settled) {
      settled = true;
      console.error('TIMEOUT: no /results POST within 40s');
      cleanup(3);
    }
  }, 40000);
}

main();
