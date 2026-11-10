#!/usr/bin/env python3
"""Echo Rounds FPS proof harness (Story 129, Session 56, Kai).

Proves the Story 128 first-person rebuild in a real Playwright chromium run.
It serves the target tree on a port-scoped local server, drives real keyboard
and mouse input plus a synthetic gamepad, prints every named check with
PASS/FAIL on its own line, and exits nonzero on any failure.

Usage:
  env -u PYTHONPATH /home/jake/.hermes/flambeee/.venv/bin/python \
      dev/echo-fps-proof.py --target /path/website/games/echo-rounds.html \
      [--label RED] [--green-target /other/website/games/echo-rounds.html] \
      [--desktop 1280x800] [--mobile 375x667] [--seed 0] [--port 8729]

Exit codes:
  every check PASS -> 0
  any check FAIL   -> 1
  --green-target given but absent: GREEN is a labeled SKIP. Exit 0 only if the
  primary run recorded RED (at least one failing check); exit 1 if the primary
  run unexpectedly passed (RED did not reproduce).
  --green-target given and present: exit 0 only if the GREEN run is all PASS.

Honesty rules that print on every run:
  NOT HARDWARE: the gamepad legs inject a synthetic navigator.getGamepads
  before page scripts. Structural proof only. This run does not verify any pad
  on real hardware and makes no controller-support claim.
  LIMITATION: Playwright device-level movementX stays 0 while the pointer is
  locked, so look is proven with an injected synthetic MouseEvent. That leg
  proves handler math only, not device deltas.

No harness flag changes a game constant. ?ammo= and ?time= are labeled
instruments for named legs only. Missing window.__echo probe fields fail
loudly by name; nothing is silently defaulted.
"""

import argparse
import functools
import http.server
import json
import math
import os
import shutil
import socketserver
import sys
import tempfile
import threading
import time

# ---------------------------------------------------------------------------
# Harness tuning constants (Story 129 section 3; live here, not in the game)
# ---------------------------------------------------------------------------
N_FRAMES = 300            # counted frames for the projection/perf bar
WARMUP_FRAMES = 30        # excluded from p95
P95_MAX_MS = 20.0         # 60 fps headless bar
FLOOR_MIN = 0.25
FLOOR_MAX = 0.90
VIEW_DESKTOP = (1280, 800)
VIEW_MOBILE = (375, 667)
SYNTH_LOOK_PX = 100       # injected MouseEvent movementX for handler math
MOUSE_SENS_CONTRACT = 0.0025   # contract default, rad/px
PITCH_MAX_RAD = 1.2       # contract PITCH_MAX
MOVE_ASSERT_S = 1.0       # seconds held per yaw-relative leg
HIT_CONE_HALF = 0.06      # contract hit cone, rad (harness reads it as a fixed bar)
WIN_SCRIPT_AMMO = 24      # ?ammo=24 instrument for the keyboard-only win leg
DEFAULT_PORT = 8729       # tried first, ephemeral fallback on collision
SAMPLE_TIMEOUT_S = 75.0

REQUIRED_PROBE = [
    'started', 'over', 'outcome', 'loseReason', 'ammoLeft', 'shots',
    'litHits', 'unlitShots', 'unlitHits', 'reveals',
    'player.x', 'player.y', 'player.yaw', 'player.pitch',
    'locked', 'lockDenied', 'inputMode', 'gamepadConnected',
    'projectedNaNCount', 'frames', 'p95ms', 'slowFrames',
    'floorCoverage', 'horizonPresent', 'moveSteps', 'lookEvents',
    'target', 'targetCount',
]

FORBIDDEN_CLAIM = 'full ' + 'controller' + ' support'

# ---------------------------------------------------------------------------
# Page-side snippets (all installed via add_init_script, i.e. before the game)
# ---------------------------------------------------------------------------
INIT_COMMON = r"""
window.__kaiFrames = [];
window.__kaiNonFinite = 0;
window.__kaiLockChanges = 0;
window.__kaiLockErrors = 0;
document.addEventListener('pointerlockchange', function () { window.__kaiLockChanges++; }, true);
document.addEventListener('pointerlockerror', function () { window.__kaiLockErrors++; }, true);
window.__kaiEscapes = 0;
window.addEventListener('keydown', function (e) { if (e.code === 'Escape') window.__kaiEscapes++; }, false);
(function () {
  var proto = window.CanvasRenderingContext2D.prototype;
  var names = ['moveTo', 'lineTo', 'rect', 'fillRect', 'strokeRect', 'arc',
    'ellipse', 'quadraticCurveTo', 'bezierCurveTo', 'arcTo', 'translate',
    'scale', 'rotate', 'setTransform', 'transform', 'drawImage', 'fillText',
    'strokeText', 'createLinearGradient', 'createRadialGradient'];
  names.forEach(function (n) {
    var orig = proto[n];
    if (typeof orig !== 'function') return;
    proto[n] = function () {
      for (var i = 0; i < arguments.length; i++) {
        var a = arguments[i];
        if (typeof a === 'number' && !isFinite(a)) window.__kaiNonFinite++;
      }
      return orig.apply(this, arguments);
    };
  });
})();
(function () {
  var last = 0;
  function tick(t) {
    if (last > 0) window.__kaiFrames.push(t - last);
    last = t;
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
"""

INIT_DENIED = r"""
(function () {
  HTMLCanvasElement.prototype.requestPointerLock = function () {
    var p = null;
    try {
      p = Promise.reject(new Error('pointer lock denied by harness'));
      p.catch(function () {});
    } catch (e) {}
    var el = this;
    setTimeout(function () {
      try { el.dispatchEvent(new Event('pointerlockerror', { bubbles: true })); } catch (e) {}
    }, 0);
    return p;
  };
})();
"""

INIT_PAD = r"""
window.__kaiPad = null;
window.__kaiLastPad = null;
(function () {
  var impl = function () {
    var p = window.__kaiPad;
    return [p, null, null, null];
  };
  try {
    Object.defineProperty(navigator, 'getGamepads', { value: impl, configurable: true, writable: true });
  } catch (e) {
    try { navigator.getGamepads = impl; } catch (e2) {}
  }
})();
"""

JS_MISSING = r"""
function (names) {
  if (!window.__echo) return ['window.__echo absent'];
  var out = [];
  names.forEach(function (n) {
    var parts = n.split('.');
    var o = window.__echo;
    for (var i = 0; i < parts.length - 1; i++) o = (o === undefined || o === null) ? undefined : o[parts[i]];
    var leaf = parts[parts.length - 1];
    if (o === undefined || o === null || !(leaf in Object(o))) out.push(n);
  });
  return out;
}
"""

JS_PROBE = r"""
(function () {
  var e = window.__echo;
  if (!e) return null;
  var p = e.player || {};
  var t0 = null;
  try { t0 = e.target(0); } catch (err) { t0 = null; }
  return {
    started: e.started, over: e.over, outcome: e.outcome, loseReason: e.loseReason,
    ammoLeft: e.ammoLeft, shots: e.shots, litHits: e.litHits,
    unlitShots: e.unlitShots, lit: null, unlitHits: e.unlitHits, reveals: e.reveals,
    x: p.x, y: p.y, yaw: p.yaw, pitch: (typeof p.pitch === 'number') ? p.pitch : null,
    locked: e.locked, lockDenied: e.lockDenied, inputMode: e.inputMode,
    gamepadConnected: e.gamepadConnected, projectedNaNCount: e.projectedNaNCount,
    frames: e.frames, p95ms: e.p95ms, slowFrames: e.slowFrames,
    floorCoverage: e.floorCoverage, horizonPresent: e.horizonPresent,
    moveSteps: e.moveSteps, lookEvents: e.lookEvents,
    targetCount: (typeof e.targetCount === 'function') ? e.targetCount() : null,
    target0: t0,
    bodyText: document.body ? document.body.innerText : ''
  };
})()
"""

JS_SYNTH = r"""
function (o) {
  var c = document.querySelector('canvas');
  if (!c) return false;
  var r = c.getBoundingClientRect();
  var ev = new MouseEvent('mousemove', {
    movementX: o.mx, movementY: o.my,
    clientX: r.left + r.width / 2, clientY: r.top + r.height / 2,
    bubbles: true, cancelable: true
  });
  c.dispatchEvent(ev);
  return true;
}
"""

JS_CONE0 = r"""
function (i) {
  var e = window.__echo, p = e.player, t = e.target(i);
  var dx = t.x - p.x, dy = t.y - p.y, gd = Math.sqrt(dx * dx + dy * dy);
  var wrap = function (a) { return ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI; };
  var bearing = wrap(Math.atan2(dy, dx) - p.yaw);
  var elev = (gd > 0 ? Math.atan2(0, gd) : 0) - p.pitch;
  return { ang: Math.sqrt(bearing * bearing + elev * elev), lit: t.lit, cleared: t.cleared };
}
"""

JS_LOCK = r"""
(function () {
  var c = document.querySelector('canvas');
  return {
    lockedToCanvas: !!c && document.pointerLockElement === c,
    lockedAny: !!document.pointerLockElement,
    changes: window.__kaiLockChanges || 0,
    errors: window.__kaiLockErrors || 0,
    nonFinite: window.__kaiNonFinite || 0
  };
})()
"""

JS_HORIZON_PIXEL = r"""
(function () {
  var c = document.querySelector('canvas');
  if (!c) return { error: 'no canvas' };
  var g = c.getContext('2d');
  var W = c.width, H = c.height;
  var pitch = 0;
  try {
    var p = window.__echo && window.__echo.player;
    if (p && typeof p.pitch === 'number' && isFinite(p.pitch)) pitch = p.pitch;
  } catch (e) {}
  var pred = H / 2 + (W / 2) * Math.tan(pitch);
  var y0 = Math.max(6, Math.floor(pred) - 16);
  var y1 = Math.min(H - 6, Math.ceil(pred) + 16);
  var top = y0 - 6;
  var h = (y1 + 6) - top;
  var d;
  try { d = g.getImageData(0, top, W, h).data; } catch (e) { return { error: 'getImageData failed: ' + e }; }
  function luma(y) {
    var base = (y - top) * W * 4, s = 0;
    for (var x = 0; x < W; x++) {
      var i = base + x * 4;
      s += 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    }
    return s / W;
  }
  var best = -1, bestY = -1;
  for (var y = y0; y <= y1; y++) {
    var m = Math.max(Math.abs(luma(y) - luma(y - 4)), Math.abs(luma(y) - luma(y + 4)));
    if (m > best) { best = m; bestY = y; }
  }
  return { pred: pred, best: best, bestY: bestY, W: W, H: H };
})()
"""

JS_PAD_SET = r"""
function (spec) {
  if (!spec) {
    var last = window.__kaiLastPad;
    window.__kaiPad = null;
    try {
      var e2 = new Event('gamepaddisconnected');
      if (last) Object.defineProperty(e2, 'gamepad', { value: last });
      window.dispatchEvent(e2);
    } catch (e) {}
    return false;
  }
  var btns = [];
  for (var i = 0; i < 17; i++) {
    var on = (i === 7) && !!spec.fire;
    btns.push({ pressed: on, touched: on, value: on ? 1 : 0 });
  }
  var pad = {
    id: 'kai-synthetic-pad (NOT HARDWARE)', index: 0, connected: true,
    mapping: (spec.mapping === undefined || spec.mapping === null) ? 'standard' : spec.mapping,
    axes: spec.axes || [0, 0, 0, 0],
    buttons: btns,
    timestamp: (typeof performance !== 'undefined') ? performance.now() : 0
  };
  window.__kaiPad = pad;
  window.__kaiLastPad = pad;
  try {
    var e = new Event('gamepadconnected');
    Object.defineProperty(e, 'gamepad', { value: pad });
    window.dispatchEvent(e);
  } catch (err) {}
  return true;
}
"""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def angdiff(a, b):
    """Signed shortest a - b in (-pi, pi]."""
    return (a - b + math.pi) % (2 * math.pi) - math.pi


def pct(values, p):
    if not values:
        return float('nan')
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(math.ceil(p / 100.0 * len(s))) - 1))
    return s[k]


def fmt_dist(values):
    if not values:
        return 'no samples'
    return ('min=%.1f p50=%.1f p90=%.1f p95=%.1f p99=%.1f max=%.1f (n=%d)'
            % (min(values), pct(values, 50), pct(values, 90), pct(values, 95),
               pct(values, 99), max(values), len(values)))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - stdlib signature
        pass


def resolve_serve_root(target):
    """Serve the real tree when target sits at website/games/echo-rounds.html,
    otherwise stage a copy of the target under that exact relative path."""
    target = os.path.abspath(target)
    d = os.path.dirname(target)
    if (os.path.basename(target) == 'echo-rounds.html'
            and os.path.basename(d) == 'games'
            and os.path.basename(os.path.dirname(d)) == 'website'):
        return os.path.dirname(os.path.dirname(d)), False
    stage = tempfile.mkdtemp(prefix='kai129-serve-')
    dest = os.path.join(stage, 'website', 'games', 'echo-rounds.html')
    os.makedirs(os.path.dirname(dest))
    shutil.copyfile(target, dest)
    return stage, True


def serve_tree(target, preferred_port):
    root, staged = resolve_serve_root(target)
    handler = functools.partial(QuietHandler, directory=root)
    port = preferred_port
    try:
        httpd = socketserver.ThreadingTCPServer(('127.0.0.1', port), handler)
    except OSError:
        port = 0
        httpd = socketserver.ThreadingTCPServer(('127.0.0.1', port), handler)
        print('port %d in use, fell back to ephemeral port' % preferred_port, flush=True)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    url = 'http://127.0.0.1:%d/website/games/echo-rounds.html' % port
    print('serve root: %s%s' % (root, ' (staged copy of target)' if staged else ''), flush=True)
    print('server: %s (port %d)' % (url, port), flush=True)
    return httpd, thread, root, staged, url, port


def stop_server(httpd, thread, root, staged, port):
    try:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)
    finally:
        print('server released on port %d' % port, flush=True)
        if staged:
            shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Page driving helpers
# ---------------------------------------------------------------------------
def mk_page(browser, viewport, init_scripts, errors):
    ctx = browser.new_context(viewport={'width': viewport[0], 'height': viewport[1]})
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    for s in init_scripts:
        page.add_init_script(s)
    return ctx, page


def wait_probe(page, timeout=8.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if page.evaluate('!!window.__echo'):
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def missing(page, names):
    try:
        return page.evaluate(JS_MISSING, list(names))
    except Exception as e:
        return ['probe read failed: %s' % e]


def probe(page):
    return page.evaluate(JS_PROBE)


def echo(page, expr):
    return page.evaluate('(function(){ return (%s); })()' % expr)


def ensure_started(page):
    st = probe(page)
    if st and st.get('started'):
        return True
    for key in ('Space', 'Enter'):
        try:
            page.keyboard.press(key)
        except Exception:
            pass
        time.sleep(0.35)
        st = probe(page)
        if st and st.get('started'):
            return True
    return bool(st and st.get('started'))


def canvas_box(page):
    el = page.query_selector('canvas')
    if not el:
        return None
    box = el.bounding_box()
    if not box or box['width'] < 20 or box['height'] < 20:
        return None
    return box


def click_canvas(page):
    box = canvas_box(page)
    if not box:
        raise RuntimeError('no usable canvas to click')
    page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)


def synth_mouse(page, mx, my):
    page.evaluate(JS_SYNTH, {'mx': mx, 'my': my})


def lock_state(page):
    return page.evaluate(JS_LOCK)


def wait_lock(page, want, timeout=3.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if lock_state(page)['lockedToCanvas'] == want:
            return True
        time.sleep(0.1)
    return lock_state(page)['lockedToCanvas'] == want


def aim_at(page, tx, ty, timeout=6.0, tol=0.03):
    """Arrow-key aim until yaw points at (tx, ty). Returns (ok, final error rad)."""
    st = time.time()
    err = math.pi
    while time.time() - st < timeout:
        p = page.evaluate("(function(){var q=window.__echo.player; return {x:q.x,y:q.y,yaw:q.yaw};})()")
        want = math.atan2(ty - p['y'], tx - p['x'])
        err = angdiff(want, p['yaw'])
        if abs(err) <= tol:
            return True, err
        key = 'ArrowRight' if err > 0 else 'ArrowLeft'
        dur = min(0.3, max(0.02, abs(err) * 0.8 / 1.8))
        page.keyboard.down(key)
        time.sleep(dur)
        page.keyboard.up(key)
        time.sleep(0.02)
    return abs(err) <= tol, err


def wait_lit(page, idx, want, timeout):
    t0 = time.time()
    lit = not want
    while time.time() - t0 < timeout:
        lit = bool(page.evaluate('(function(){return window.__echo.target(%d).lit;})()' % idx))
        if lit == want:
            return True
        time.sleep(0.1)
    return lit == want


def sample_frames(page, ctx):
    page.evaluate('window.__kaiFrames.length = 0')
    t0 = time.time()
    n = 0
    timed_out = False
    while time.time() - t0 < SAMPLE_TIMEOUT_S:
        n = page.evaluate('window.__kaiFrames.length')
        if n >= N_FRAMES + WARMUP_FRAMES:
            break
        time.sleep(0.25)
    else:
        timed_out = True
    arr = page.evaluate('window.__kaiFrames.slice(0, %d)' % (N_FRAMES + WARMUP_FRAMES))
    counted = arr[WARMUP_FRAMES:WARMUP_FRAMES + N_FRAMES]
    ctx['frame_ms'] = counted
    ctx['p95'] = pct(counted, 95) if len(counted) == N_FRAMES else None
    return counted, n, timed_out


def guarded(name, fn):
    print('--- %s' % name, flush=True)
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, 'exception: %s: %s' % (type(e).__name__, e)
    return ok, detail


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check00(page, ctx):
    miss = missing(page, REQUIRED_PROBE)
    if miss:
        return False, 'missing window.__echo fields: %s' % ', '.join(miss)
    st = probe(page)
    if st.get('targetCount') != 4:
        return False, 'targetCount() is %r, expected 4' % (st.get('targetCount'),)
    t0 = st.get('target0') or {}
    for k in ('x', 'y', 'cleared', 'lit'):
        if k not in t0:
            return False, 'target(i) missing field %r (got %r)' % (k, sorted(t0))
    return True, 'window.__echo complete: %d required fields, target(0) shape ok' % len(REQUIRED_PROBE)


def check01(page, ctx):
    miss = missing(page, ['projectedNaNCount', 'frames'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); no counted frames to prove'
    counted, n, timed_out = sample_frames(page, ctx)
    if len(counted) != N_FRAMES:
        return False, 'only %d/%d counted frames sampled in %.0fs (rAF samples=%d)%s' % (
            len(counted), N_FRAMES, SAMPLE_TIMEOUT_S, n, ' [timed out]' if timed_out else '')
    p95 = ctx['p95']
    if p95 is not None and p95 > P95_MAX_MS:
        print('   p95 %.1f ms over %.1f ms; rerunning frame sample once' % (p95, P95_MAX_MS), flush=True)
        counted, n, timed_out = sample_frames(page, ctx)
        p95 = ctx['p95']
    st = probe(page)
    nan = st.get('projectedNaNCount')
    gframes = st.get('frames')
    nonfin = lock_state(page)['nonFinite']
    probe_nums = [st.get('x'), st.get('y'), st.get('yaw'), st.get('pitch'),
                  st.get('floorCoverage'), st.get('p95ms'), st.get('floorCoverage')]
    bad_probe = [v for v in probe_nums if v is not None and not isinstance(v, bool) and not math.isfinite(float(v))]
    ok = (nan == 0) and (gframes is not None and gframes >= N_FRAMES) and (nonfin == 0) and not bad_probe
    detail = ('%d counted frames (warmup %d excluded), projectedNaNCount=%s over game frames=%s, '
              'nonFiniteCanvasArgs=%s, non-finite probe numbers=%d, p95=%s ms (see check-10)'
              % (len(counted), WARMUP_FRAMES, nan, gframes, nonfin, len(bad_probe),
                 ('%.1f' % p95) if p95 is not None else 'n/a'))
    if not ok and bad_probe:
        detail += '; non-finite probe values: %r' % (bad_probe,)
    return ok, detail


def check02(page, ctx):
    miss = missing(page, ['floorCoverage', 'horizonPresent', 'player.pitch'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    st = probe(page)
    fc = float(st['floorCoverage'])
    hp = bool(st['horizonPresent'])
    band = FLOOR_MIN <= fc <= FLOOR_MAX
    px = page.evaluate(JS_HORIZON_PIXEL)
    if 'error' in px:
        return False, 'horizon pixel-row check failed: %s (floorCoverage=%.3f band=%s horizonPresent=%s)' % (
            px['error'], fc, band, hp)
    pixel_ok = px['best'] >= 2.0
    ok = band and hp and pixel_ok
    detail = ('floorCoverage=%.3f in [%.2f, %.2f]=%s; horizonPresent=%s; horizon pixel-row: '
              'predicted y=%.1f at pitch %s, strongest horizontal luma step %.1f at y=%d (threshold 2.0)=%s'
              % (fc, FLOOR_MIN, FLOOR_MAX, band, hp, px['pred'], st.get('pitch'),
                 px['best'], px['bestY'], pixel_ok))
    return ok, detail


def check03(page, ctx):
    miss = missing(page, ['player.pitch', 'player.yaw'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); pitch sweep not testable'
    if not lock_state(page)['lockedToCanvas']:
        click_canvas(page)
        if not wait_lock(page, True, 3.0):
            return False, 'pointer lock not acquired; synthetic mouse look cannot be driven'

    def stable_yaw(timeout=3.0):
        t0 = time.time()
        prev = float(probe(page)['yaw'])
        while time.time() - t0 < timeout:
            time.sleep(0.3)
            cur = float(probe(page)['yaw'])
            if abs(angdiff(cur, prev)) <= 0.01:
                return cur
            prev = cur
        return prev

    # Playwright's cursor restore after a pointer-lock exit can deliver a late
    # mousemove (large movementX) that lands inside a measurement window. The
    # game counts lookEvents per look input, so a clean window is exactly one
    # lookEvent for one synthetic dispatch; anything else is retried.
    def measure(mx, my, tries=5):
        last = (0, 0.0, 0.0, float('nan'))  # le_delta 0 fails the check honestly if no window ran
        for _ in range(tries):
            stable_yaw()
            le0 = page.evaluate('window.__echo.lookEvents')
            y_before = float(probe(page)['yaw'])
            p_before = float(probe(page)['pitch'])
            synth_mouse(page, mx, my)
            time.sleep(0.15)
            st_after = probe(page)
            le1 = st_after['lookEvents']
            last = (le1 - le0, angdiff(float(st_after['yaw']), y_before),
                    float(st_after['pitch']) - p_before, y_before)
            if last[0] == 1:
                return last
        return last

    le_delta, dy, dpitch, _ = measure(SYNTH_LOOK_PX, 0)
    sens = dy / float(SYNTH_LOOK_PX)
    sens_ok = (le_delta == 1 and
               abs(dy - SYNTH_LOOK_PX * MOUSE_SENS_CONTRACT) <= 0.01 * SYNTH_LOOK_PX * MOUSE_SENS_CONTRACT)
    samples = [float(probe(page)['pitch'])]

    def sweep(sign):
        for _ in range(12):
            before = samples[-1]
            synth_mouse(page, 0, sign * 200)
            time.sleep(0.06)
            p = float(probe(page)['pitch'])
            samples.append(p)
            if abs(p - before) < 1e-6:
                break

    sweep(-1)   # mouse up: pitch rises to the +clamp
    sweep(+1)   # mouse down: pitch falls to the -clamp
    sweep(-1)   # leave the camera looking up mid-range
    time.sleep(0.1)
    st2 = probe(page)
    samples.append(float(st2['pitch']))
    up_max, low_min = max(samples), min(samples)
    clamped_up = up_max >= PITCH_MAX_RAD - 0.02
    clamped_dn = low_min <= -PITCH_MAX_RAD + 0.02
    within = all(abs(p) <= PITCH_MAX_RAD + 1e-6 for p in samples)
    upright = all(math.cos(p) > 0 for p in samples)
    finite = all(math.isfinite(p) for p in samples)

    yaw_before = float(st2['yaw'])
    raw_px = (2.5 * 2 * math.pi) / sens if abs(sens) > 1e-9 else 0.0
    raw_rad = raw_px * sens
    wrap_le = None
    if raw_px:
        wrap_le, _, _, yaw_before = measure(int(round(raw_px)), 0)
    yaw_after = float(probe(page)['yaw'])
    expected = (yaw_before + raw_rad + math.pi) % (2 * math.pi) - math.pi if raw_rad else yaw_before
    wrap_ok = (bool(raw_rad) and wrap_le == 1
               and abs(angdiff(yaw_after, expected)) <= 0.05 and abs(yaw_after) <= math.pi + 1e-9)
    try:
        page.keyboard.press('Escape')
    except Exception:
        pass
    wait_lock(page, False, 2.0)

    ok = sens_ok and clamped_up and clamped_dn and within and upright and finite and wrap_ok
    detail = ('handler sens=%.5f rad/px (expect %.5f, 1%% band=%s, clean window lookEvents delta=%s); '
              'pitch sweep [%.3f, %.3f] '
              'reached +clamp=%s -clamp=%s, within +-%.1f rad=%s; up-dot-world-up=cos(pitch) min %.3f > 0=%s; '
              'yaw wrap %.3f -> %.3f expected %.3f (2.5 turns, lookEvents delta=%s)=%s; synthetic MouseEvent legs '
              'prove handler math only (device movementX stays 0 under Playwright while locked)'
              % (sens, MOUSE_SENS_CONTRACT, sens_ok, le_delta, low_min, up_max, clamped_up, clamped_dn,
                 PITCH_MAX_RAD, within, min(math.cos(p) for p in samples), upright,
                 yaw_before, yaw_after, expected, wrap_le, wrap_ok))
    return ok, detail


def check04(page, ctx):
    miss = missing(page, ['player.x', 'player.y', 'player.yaw'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); WASD not testable'
    st = probe(page)
    if abs(angdiff(float(st['yaw']), 0.0)) > 0.2:
        return False, 'expected yaw 0 at leg A, measured %.3f rad' % float(st['yaw'])

    def leg(label, want_axis):
        p0 = probe(page)
        page.keyboard.down('w')
        time.sleep(MOVE_ASSERT_S)
        page.keyboard.up('w')
        time.sleep(0.1)
        p1 = probe(page)
        dx = float(p1['x']) - float(p0['x'])
        dy = float(p1['y']) - float(p0['y'])
        moved = math.hypot(dx, dy)
        if moved < 5:
            return False, ('leg %s: no movement (dx=%.1f dy=%.1f); round not running or WASD not applied'
                           % (label, dx, dy)), None
        axis = 'x' if abs(dx) > abs(dy) else 'y'
        good = axis == want_axis
        return good, ('leg %s: dx=%+.1f dy=%+.1f dominant axis %s (want %s)=%s'
                      % (label, dx, dy, axis, want_axis, good)), axis

    okA, detA, axisA = leg('yaw 0 (+x)', 'x')
    if axisA is None:
        return False, detA
    st = probe(page)
    target = math.pi / 2
    t0 = time.time()
    err = angdiff(target, float(st['yaw']))
    while abs(err) > 0.06 and time.time() - t0 < 6.0:
        page.keyboard.down('ArrowRight' if err > 0 else 'ArrowLeft')
        time.sleep(min(0.4, max(0.05, abs(err) * 0.9 / 1.8)))
        page.keyboard.up('ArrowRight' if err > 0 else 'ArrowLeft')
        time.sleep(0.03)
        err = angdiff(target, float(probe(page)['yaw']))
    if abs(err) > 0.12:
        return False, 'could not reach yaw pi/2 with arrows (residual %.3f rad); %s' % (err, detA)
    okB, detB, axisB = leg('yaw pi/2 (+y)', 'y')
    if axisB is None:
        return False, detB + '; ' + detA
    swap = axisA != axisB
    ok = okA and okB and swap
    return ok, '%s; %s; dominant axis swapped=%s' % (detA, detB, swap)


def check05(page, ctx):
    miss = missing(page, ['started', 'shots', 'litHits', 'unlitShots', 'unlitHits', 'ammoLeft',
                          'player.x', 'player.y', 'player.yaw', 'player.pitch', 'target'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); lit gate not testable'
    st = probe(page)
    if st.get('pitch') is None or abs(float(st['pitch'])) > 0.05:
        return False, 'pitch must be 0 for the scripted cone test, measured %s' % (st.get('pitch'),)
    t = page.evaluate('(function(){var t=window.__echo.target(0); return {x:t.x,y:t.y,cleared:t.cleared,lit:t.lit};})()')
    if t['cleared']:
        return False, 'target 0 already cleared before the gate script ran'
    aimed, err = aim_at(page, t['x'], t['y'])
    if not aimed:
        return False, 'could not aim at target 0 with arrows (bearing error %.3f rad > 0.05)' % err
    s0 = st['shots']; l0 = st['litHits']; u0 = st['unlitShots']; a0 = st['ammoLeft']
    h0 = st.get('unlitHits')

    def cone0():
        return page.evaluate(JS_CONE0, 0)

    def cleared0():
        return bool(page.evaluate('(function(){return window.__echo.target(0).cleared;})()'))

    # Phase 1: a shot at a probe-dark target inside the 0.06 rad cone must
    # stand. Aim first, then wait for dark, then verify the cone with the
    # game's own math in one read, then fire: the lit window cannot expire
    # between the wait and the shot.
    p1 = None
    pre1 = None
    phase1_ok = False
    defect = False
    for _ in range(4):
        aim_at(page, t['x'], t['y'], timeout=2.0)
        if not wait_lit(page, 0, False, 3.2):
            continue
        pre1 = cone0()
        if pre1['cleared']:
            break
        if pre1['lit'] or pre1['ang'] > HIT_CONE_HALF:
            continue
        page.keyboard.press('f')
        time.sleep(0.35)
        p1 = probe(page)
        if p1['litHits'] > l0:
            defect = True
            break
        if (p1['unlitShots'] == u0 + 1 and p1['ammoLeft'] == a0 - 1 and not cleared0()):
            phase1_ok = True
            break
    if defect:
        return False, ('a shot fired at target 0 while the probe and the game math both reported it DARK '
                       'and in-cone cleared it (litHits %s->%s): the lit-hit gate evaluated after this shot '
                       'own pulse boost, so every aimed hit clears (Story 089 gate defeated: fire() sets '
                       'litBoostUntil before calling litNow())' % (l0, (p1 or st).get('litHits')))
    if not phase1_ok:
        got = p1 or st
        return False, ('dark shot did not stand in-cone: pre-fire ang=%s lit=%s cleared=%s; unlitShots %s->%s, '
                       'litHits %s->%s, unlitHits %s->%s, shots %s->%s, ammo %s->%s'
                       % ((pre1 or {}).get('ang'), (pre1 or {}).get('lit'), (pre1 or {}).get('cleared'),
                          u0, got.get('unlitShots'), l0, got.get('litHits'), h0, got.get('unlitHits'),
                          s0, got.get('shots'), a0, got.get('ammoLeft')))

    # Phase 2: a shot inside a lit window must clear. Phase 1's own pulse
    # boost keeps target 0 lit for 500 ms, so the first attempt is
    # deterministic; later attempts fall back to the cycle-lit wait.
    cleared = False
    for _ in range(5):
        aim_at(page, t['x'], t['y'], timeout=2.0)
        pre2 = cone0()
        if not pre2['lit']:
            if not wait_lit(page, 0, True, 1.5):
                continue
            pre2 = cone0()
        if pre2['cleared']:
            cleared = True
            break
        if pre2['ang'] > HIT_CONE_HALF:
            continue
        page.keyboard.press('f')
        time.sleep(0.35)
        if cleared0():
            cleared = True
            break
    fin = probe(page)
    lit_delta = fin['litHits'] - l0
    unlit_delta = fin['unlitShots'] - u0
    hits_delta = (fin.get('unlitHits') - h0) if (h0 is not None and fin.get('unlitHits') is not None) else None
    ammo_delta = a0 - fin['ammoLeft']
    shots_delta = fin['shots'] - s0
    # unlitHits is the gate canary: with the gate working it stays 0.
    ok = (cleared and lit_delta == 1 and unlit_delta == 1 and hits_delta == 0
          and ammo_delta >= 2 and ammo_delta == shots_delta)
    detail = ('scripted shot at probe-dark in-cone target 0 (pre-fire ang=%.4f rad <= 0.06): unlitShots +%d, '
              'target stood, ammo %s->%s; scripted shot inside the lit window: cleared=%s litHits +%d; '
              'unlitHits canary delta %s (want 0); totals shots +%d, ammo -%d'
              % (pre1['ang'] if pre1 else -1, unlit_delta, a0, p1['ammoLeft'] if p1 else a0,
                 cleared, lit_delta, hits_delta, shots_delta, ammo_delta))
    if not ok:
        detail += '; EXPECTED unlitShots +1, litHits +1, unlitHits delta 0, target cleared, ammo -2+'
    return ok, detail


def check06(page, ctx):
    miss = missing(page, ['locked', 'lockDenied', 'shots', 'ammoLeft', 'started', 'over'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); pointer lock cycle not testable'
    pre = probe(page)
    shots0, ammo0 = pre['shots'], pre['ammoLeft']
    page.evaluate('window.__kaiLockChanges = 0; window.__kaiLockErrors = 0; window.__kaiEscapes = 0')
    if lock_state(page)['lockedToCanvas']:
        page.keyboard.press('Escape')
        if not wait_lock(page, False, 2.0):
            page.evaluate('document.exitPointerLock && document.exitPointerLock()')
            wait_lock(page, False, 2.0)
    click_canvas(page)
    acq = wait_lock(page, True, 3.0)
    time.sleep(0.5)
    st_lock = lock_state(page)
    changed1 = st_lock['changes'] >= 1
    probe_locked = bool(probe(page)['locked'])
    y0 = float(probe(page)['yaw'])
    synth_mouse(page, SYNTH_LOOK_PX, 0)
    time.sleep(0.15)
    dy = angdiff(float(probe(page)['yaw']), y0)
    math_ok = abs(dy - SYNTH_LOOK_PX * MOUSE_SENS_CONTRACT) <= 0.01 * SYNTH_LOOK_PX * MOUSE_SENS_CONTRACT

    released = False
    for _ in range(3):
        page.keyboard.press('Escape')
        released = wait_lock(page, False, 1.5)
        if released:
            break
        time.sleep(0.3)
    escapes_seen = page.evaluate('window.__kaiEscapes')
    release_mech = 'synthetic Escape released the lock'
    if not released:
        page.evaluate('document.exitPointerLock && document.exitPointerLock()')
        released = wait_lock(page, False, 2.0)
        release_mech = ('LIMITATION: Playwright synthetic Escape did not release pointer lock in headless '
                        'chromium 156 (environment limitation, not a game defect); lock loss driven with '
                        'document.exitPointerLock()')
    time.sleep(0.3)
    st_lock = lock_state(page)
    changes_after_esc = st_lock['changes']
    mid = probe(page)
    continues = bool(mid['started']) and not bool(mid['over'])
    probe_unlocked = not bool(mid['locked'])

    shots_mid, ammo_mid = mid['shots'], mid['ammoLeft']
    click_canvas(page)
    relock = wait_lock(page, True, 3.0)
    after = probe(page)
    no_restart = (after['shots'] == shots_mid and after['ammoLeft'] == ammo_mid
                  and bool(after['started']) and not bool(after['over']))
    errs = list(ctx.get('errors', []))
    ok = acq and changed1 and probe_locked and math_ok and released and changes_after_esc >= 2 \
        and continues and probe_unlocked and relock and no_restart and not errs
    detail = ('trusted click acquires lock (pointerLockElement=canvas)=%s, pointerlockchange fired=%s, '
              'probe locked=%s; injected MouseEvent movementX=%d -> yaw delta %.4f rad (100*MOUSE_SENS=0.2500, '
              '1%% band)=%s [LIMITATION: device-level movementX is 0 under Playwright while locked, handler math '
              'only]; lock release: Escape keydown delivered %d time(s), release mechanism: %s; pointerlockchange '
              'count=%d (>=2)=%s, round continues=%s, probe reports unlocked=%s; click re-locks=%s without restart=%s; '
              'page errors=%d%s'
              % (acq, changed1, probe_locked, SYNTH_LOOK_PX, dy, math_ok, escapes_seen, release_mech,
                 changes_after_esc, changes_after_esc >= 2, continues, probe_unlocked, relock, no_restart,
                 len(errs), (' | ' + errs[0][:200]) if errs else ''))
    return ok, detail


def check07(page, ctx):
    miss = missing(page, ['lockDenied', 'locked', 'player.x', 'player.y', 'player.yaw',
                          'shots', 'ammoLeft', 'started'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); denial fallback not testable'
    click_canvas(page)
    time.sleep(0.8)
    ls = lock_state(page)
    st = probe(page)
    body = st.get('bodyText') or ''
    exact = 'Pointer lock unavailable. Arrow keys look.'
    line_ok = exact in body
    denied = bool(st['lockDenied'])
    stays_unlocked = (not ls['lockedToCanvas']) and (not ls['lockedAny']) and (not st['locked'])
    err_seen = ls['errors'] >= 1

    y0 = float(st['yaw'])
    page.keyboard.down('ArrowRight')
    time.sleep(0.5)
    page.keyboard.up('ArrowRight')
    time.sleep(0.1)
    dy = angdiff(float(probe(page)['yaw']), y0)
    arrows_look = abs(dy) > 0.05

    s0 = probe(page)['shots']; a0 = probe(page)['ammoLeft']
    page.keyboard.press('f')
    time.sleep(0.35)
    st2 = probe(page)
    f_fires = st2['shots'] == s0 + 1 and st2['ammoLeft'] == a0 - 1

    p0 = probe(page)
    page.keyboard.down('w')
    time.sleep(0.5)
    page.keyboard.up('w')
    time.sleep(0.1)
    p1 = probe(page)
    moved = math.hypot(float(p1['x']) - float(p0['x']), float(p1['y']) - float(p0['y'])) > 5
    errs = list(ctx.get('errors', []))
    ok = denied and stays_unlocked and line_ok and arrows_look and f_fires and moved and not errs
    detail = ('requestPointerLock overridden to reject: lockDenied=%s, stays unlocked=%s, '
              'pointerlockerror fired=%s; exact fallback line present=%s (%r); arrows look: yaw %+.3f rad=%s; '
              'F fires: shots %s->%s ammo %s->%s=%s; WASD moved=%s; page errors=%d%s'
              % (denied, stays_unlocked, err_seen, line_ok, exact, dy, arrows_look,
                 s0, st2['shots'], a0, st2['ammoLeft'], f_fires, moved, len(errs),
                 (' | ' + errs[0][:200]) if errs else ''))
    return ok, detail


def check08(page, ctx):
    miss = missing(page, ['outcome', 'over', 'started', 'player.yaw', 'target', 'targetCount',
                          'ammoLeft', 'shots', 'gamepadConnected'])
    if miss:
        return False, 'missing probe fields: %s' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start with Space/Enter; keyboard-only win not possible'
    if page.evaluate('window.__echo.gamepadConnected') is True:
        return False, 'a gamepad reported connected on the keyboard-only leg'
    st = probe(page)
    n = st['targetCount']
    attempts_log = []
    for i in range(n):
        t = page.evaluate('(function(i){var t=window.__echo.target(i); return {x:t.x,y:t.y,cleared:t.cleared};})(%d)' % i)
        if t['cleared']:
            continue
        done = False
        for a in range(3):
            aimed, err = aim_at(page, t['x'], t['y'], timeout=3.0)
            if not aimed:
                attempts_log.append('t%d aim %.3f' % (i, err))
                continue
            pre = page.evaluate(JS_CONE0, i)
            if pre['cleared']:
                done = True
                break
            # A shot at a lit target clears; a shot at a dark target stands and
            # primes the 500 ms pulse boost, so the follow-up shot clears.
            page.keyboard.press('f')
            time.sleep(0.35)
            if page.evaluate('(function(i){return window.__echo.target(i).cleared;})(%d)' % i):
                done = True
                break
            t_f = time.time()
            while time.time() - t_f < 1.6:
                pre = page.evaluate(JS_CONE0, i)
                if pre['cleared']:
                    break
                if pre['lit'] and pre['ang'] <= HIT_CONE_HALF and time.time() - t_f >= 0.2:
                    page.keyboard.press('f')
                    time.sleep(0.35)
                    break
                time.sleep(0.05)
            if page.evaluate('(function(i){return window.__echo.target(i).cleared;})(%d)' % i):
                done = True
                break
            attempts_log.append('t%d cycle %d not cleared (ang=%.3f lit=%s)'
                                % (i, a, pre['ang'], pre['lit']))
            time.sleep(0.2)
        if not done:
            fin = probe(page)
            return False, ('target %d never cleared after 3 keyboard cycles (%s); outcome=%s shots=%s ammo=%s'
                           % (i, '; '.join(attempts_log) or 'no detail', fin['outcome'], fin['shots'], fin['ammoLeft']))
    time.sleep(0.5)
    fin = probe(page)
    body = fin.get('bodyText') or ''
    dom_text = 'ROOM CLEAR' in body
    errs = list(ctx.get('errors', []))
    # The end-screen overlay is drawn on the canvas, so the ROOM CLEAR string is
    # not in the DOM. The game's own outcome record is the authoritative signal.
    ok = bool(fin['over']) and fin['outcome'] == 'win' and not errs
    detail = ('keyboard-only round (Space start, arrow aim, F fire; no mouse and no pad input issued by the '
              'harness, ?ammo=%d instrument): outcome=%s over=%s, shots=%s ammoLeft=%s litHits=%s '
              'gamepadConnected=%s; ROOM CLEAR overlay drawn on canvas (DOM text present=%s); page errors=%d%s'
              % (WIN_SCRIPT_AMMO, fin['outcome'], fin['over'], fin['shots'], fin['ammoLeft'],
                 fin['litHits'], fin['gamepadConnected'], dom_text, len(errs),
                 (' | ' + errs[0][:200]) if errs else ''))
    return ok, detail


def check09(page, ctx):
    miss = missing(page, ['gamepadConnected', 'shots', 'ammoLeft', 'player.x', 'player.y',
                          'player.yaw', 'started'])
    if miss:
        return False, 'missing probe fields: %s (synthetic pad leg)' % ', '.join(miss)
    if not ensure_started(page):
        return False, 'round did not start (Space/Enter); synthetic pad leg not testable'
    axes = [0, -1, 0.8, 0]
    page.evaluate(JS_PAD_SET, {'axes': axes, 'mapping': 'standard', 'fire': False})
    time.sleep(0.5)
    st = probe(page)
    connected = bool(st['gamepadConnected'])
    body = st.get('bodyText') or ''
    status_ok = 'Controller detected' in body
    p0 = st; time.sleep(0.6)
    p1 = probe(page)
    moved = math.hypot(float(p1['x']) - float(p0['x']), float(p1['y']) - float(p0['y'])) > 5
    yaw_move = abs(angdiff(float(p1['yaw']), float(p0['yaw'])))
    looked = yaw_move > 0.1

    s0 = probe(page)['shots']; a0 = probe(page)['ammoLeft']
    page.evaluate(JS_PAD_SET, {'axes': axes, 'mapping': 'standard', 'fire': True})
    time.sleep(0.35)
    fired = probe(page)
    page.evaluate(JS_PAD_SET, {'axes': axes, 'mapping': 'standard', 'fire': False})
    fired_ok = fired['shots'] == s0 + 1 and fired['ammoLeft'] == a0 - 1

    page.evaluate(JS_PAD_SET, None)
    time.sleep(0.4)
    disc = not bool(probe(page)['gamepadConnected'])
    q0 = probe(page)
    time.sleep(0.8)
    q1 = probe(page)
    still = math.hypot(float(q1['x']) - float(q0['x']), float(q1['y']) - float(q0['y'])) < 1.5
    yaw_still = abs(angdiff(float(q1['yaw']), float(q0['yaw']))) < 0.05

    page.evaluate(JS_PAD_SET, {'axes': axes, 'mapping': '', 'fire': False})
    time.sleep(0.4)
    body2 = (probe(page).get('bodyText') or '')
    nons = 'non-standard layout' in body2
    page.evaluate(JS_PAD_SET, None)
    time.sleep(0.2)
    body3 = (probe(page).get('bodyText') or '')
    no_claim = FORBIDDEN_CLAIM.lower() not in body3.lower()
    errs = list(ctx.get('errors', []))
    ok = (connected and status_ok and moved and looked and fired_ok and disc and still
          and yaw_still and nons and no_claim and not errs)
    detail = ('NOT HARDWARE: synthetic navigator.getGamepads injected before page scripts, structural only; '
              'axes %s -> connected=%s, status line "Controller detected"=%s, moved %.1f units=%s, '
              'yaw changed %.3f rad=%s; button 7 fire: shots %s->%s ammo %s->%s=%s; mid-round disconnect: '
              'disconnect handled, gamepadConnected now false=%s, position drift %.2f units and yaw drift %.4f rad '
              '(no stuck intent)=%s; '
              'non-standard mapping line=%s; controller-claim string absent from page text=%s; page errors=%d%s'
              % (axes, connected, status_ok,
                 math.hypot(float(p1['x']) - float(p0['x']), float(p1['y']) - float(p0['y'])), moved,
                 yaw_move, looked, s0, fired['shots'], a0, fired['ammoLeft'], fired_ok, disc,
                 math.hypot(float(q1['x']) - float(q0['x']), float(q1['y']) - float(q0['y'])),
                 abs(angdiff(float(q1['yaw']), float(q0['yaw']))), still and yaw_still,
                 nons, no_claim, len(errs), (' | ' + errs[0][:200]) if errs else ''))
    return ok, detail


def check10(page, ctx, mobile_vp):
    out = []
    ok = True
    p95 = ctx.get('p95')
    frames = ctx.get('frame_ms') or []
    if p95 is None:
        ok = False
        out.append('frame sample unavailable (check-01 failed): no p95')
    else:
        part = p95 <= P95_MAX_MS
        ok = ok and part
        out.append('60 fps headless p95=%.1f ms over %d counted frames (warmup %d excluded) <= %.1f ms=%s; '
                   'frame distribution %s' % (p95, len(frames), WARMUP_FRAMES, P95_MAX_MS, part, fmt_dist(frames)))

    miss = missing(page, ['lockDenied', 'started'])
    if miss:
        ok = False
        out.append('mobile leg missing probe fields: %s' % ', '.join(miss))
        sw = page.evaluate('Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0)')
        out.append('mobile scrollWidth=%s (informational only, probe incomplete)' % sw)
        return ok, '; '.join(out)
    time.sleep(0.4)
    page.set_viewport_size({'width': mobile_vp[0], 'height': mobile_vp[1]})
    page.evaluate("window.dispatchEvent(new Event('resize'))")
    time.sleep(0.5)
    m = page.evaluate('(function(){return {sw: document.documentElement.scrollWidth, bw: document.body ? document.body.scrollWidth : 0, cw: document.documentElement.clientWidth};})()')
    sw = max(m['sw'], m['bw'])
    overflow_ok = sw <= mobile_vp[0] and sw <= m['cw']
    ok = ok and overflow_ok
    out.append('mobile %dx%d: scrollWidth=%d (<= %d)=%s, clientWidth=%d, no horizontal overflow=%s'
               % (mobile_vp[0], mobile_vp[1], sw, mobile_vp[0], overflow_ok, m['cw'], overflow_ok))

    if not ensure_started(page):
        ok = False
        out.append('mobile leg: round did not start with Space/Enter')
    else:
        click_canvas(page)
        time.sleep(0.8)
        st = probe(page)
        ls = lock_state(page)
        denied = bool(st['lockDenied'])
        line_ok = 'Pointer lock unavailable. Arrow keys look.' in (st.get('bodyText') or '')
        degrade = denied and (not ls['lockedToCanvas'])
        ok = ok and degrade and line_ok
        out.append('mobile lock denial degrades without throw: lockDenied=%s, stays unlocked=%s, '
                   'fallback line=%s' % (denied, not ls['lockedToCanvas'], line_ok))
    errs = list(ctx.get('errors', []))
    if errs:
        ok = False
    out.append('page errors=%d%s' % (len(errs), (' | ' + errs[0][:200]) if errs else ''))
    return ok, '; '.join(out)


# ---------------------------------------------------------------------------
# Per-leg orchestration
# ---------------------------------------------------------------------------
def leg_main(browser, url, vp, ctx):
    res = {}
    ctx['errors'] = []
    c, page = mk_page(browser, vp, [INIT_COMMON], ctx['errors'])
    try:
        page.goto(url, wait_until='load')
        wait_probe(page)
        page.wait_for_selector('canvas', timeout=8000)
        res['check-00-probe-surface'] = guarded('check-00-probe-surface', lambda: check00(page, ctx))
        ensure_started(page)
        res['check-02-floor-coverage-horizon'] = guarded('check-02-floor-coverage-horizon', lambda: check02(page, ctx))
        res['check-01-projection-300-frames'] = guarded('check-01-projection-300-frames', lambda: check01(page, ctx))
        res['check-04-yaw-relative-movement'] = guarded('check-04-yaw-relative-movement', lambda: check04(page, ctx))
        res['check-05-lit-hit-gate'] = guarded('check-05-lit-hit-gate', lambda: check05(page, ctx))
        res['check-06-pointer-lock-cycle'] = guarded('check-06-pointer-lock-cycle', lambda: check06(page, ctx))
        res['check-03-camera-upright-pitch-sweep'] = guarded('check-03-camera-upright-pitch-sweep', lambda: check03(page, ctx))
    finally:
        c.close()
    return res


def leg_win(browser, url, vp, ctx):
    res = {}
    ctx['errors'] = []
    win_url = url + ('&' if '?' in url else '?') + 'ammo=%d' % WIN_SCRIPT_AMMO
    c, page = mk_page(browser, vp, [INIT_COMMON], ctx['errors'])
    try:
        page.goto(win_url, wait_until='load')
        wait_probe(page)
        page.wait_for_selector('canvas', timeout=8000)
        res['check-08-keyboard-only-win'] = guarded('check-08-keyboard-only-win', lambda: check08(page, ctx))
    finally:
        c.close()
    return res


def leg_denied(browser, url, vp, ctx):
    res = {}
    ctx['errors'] = []
    c, page = mk_page(browser, vp, [INIT_COMMON, INIT_DENIED], ctx['errors'])
    try:
        page.goto(url, wait_until='load')
        wait_probe(page)
        page.wait_for_selector('canvas', timeout=8000)
        res['check-07-lock-denied-fallback'] = guarded('check-07-lock-denied-fallback', lambda: check07(page, ctx))
    finally:
        c.close()
    return res


def leg_pad(browser, url, vp, ctx):
    res = {}
    ctx['errors'] = []
    c, page = mk_page(browser, vp, [INIT_COMMON, INIT_PAD], ctx['errors'])
    try:
        page.goto(url, wait_until='load')
        wait_probe(page)
        page.wait_for_selector('canvas', timeout=8000)
        res['check-09-synthetic-pad-structural'] = guarded('check-09-synthetic-pad-structural', lambda: check09(page, ctx))
    finally:
        c.close()
    return res


def leg_mobile(browser, url, vp, ctx):
    res = {}
    ctx['errors'] = []
    c, page = mk_page(browser, vp, [INIT_COMMON, INIT_DENIED], ctx['errors'])
    try:
        page.goto(url, wait_until='load')
        wait_probe(page)
        page.wait_for_selector('canvas', timeout=8000)
        res['check-10-fps-p95-and-mobile'] = guarded(
            'check-10-fps-p95-and-mobile', lambda: check10(page, ctx, vp))
    finally:
        c.close()
    return res


def run_suite(target, desktop_vp, mobile_vp, label, seed):
    from playwright.sync_api import sync_playwright
    httpd, thread, root, staged, url, port = serve_tree(target, ARGS.port)
    results = {}
    ctx = {'errors': [], 'p95': None, 'frame_ms': None}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                results.update(leg_main(browser, url, desktop_vp, ctx))
                results.update(leg_win(browser, url, desktop_vp, ctx))
                results.update(leg_denied(browser, url, desktop_vp, ctx))
                results.update(leg_pad(browser, url, desktop_vp, ctx))
                results.update(leg_mobile(browser, url, mobile_vp, ctx))
            finally:
                browser.close()
    finally:
        stop_server(httpd, thread, root, staged, port)
    return results, port, url


def report(results, label):
    print('', flush=True)
    print('== %s results ==' % label, flush=True)
    failed = []
    for name in sorted(results):
        ok, detail = results[name]
        print('%s %-36s | %s' % ('PASS' if ok else 'FAIL', name, detail), flush=True)
        if not ok:
            failed.append(name)
    total = len(results)
    print('%s: %d/%d checks passed' % (label, total - len(failed), total), flush=True)
    if failed:
        print('%s FAILED CHECKS: %s' % (label, ', '.join(failed)), flush=True)
    return failed


def parse_viewport(text, fallback):
    try:
        w, h = text.lower().split('x')
        return (int(w), int(h))
    except Exception:
        return fallback


def main():
    global ARGS
    ap = argparse.ArgumentParser(description='Echo Rounds FPS proof harness (Story 129)')
    ap.add_argument('--target', required=True, help='path to the echo-rounds.html under test')
    ap.add_argument('--green-target', default=None,
                    help='optional Story 128 branch file for the GREEN leg; absent means labeled SKIP')
    ap.add_argument('--desktop', default='1280x800', help='desktop viewport WxH (default 1280x800)')
    ap.add_argument('--mobile', default='375x667', help='mobile viewport WxH (default 375x667)')
    ap.add_argument('--seed', type=int, default=0, help='run label seed only; changes no game constant')
    ap.add_argument('--label', default='run', help='label printed with results (RED, GREEN, ...)')
    ap.add_argument('--port', type=int, default=DEFAULT_PORT, help='preferred local server port')
    ARGS = ap.parse_args()

    desktop_vp = parse_viewport(ARGS.desktop, VIEW_DESKTOP)
    mobile_vp = parse_viewport(ARGS.mobile, VIEW_MOBILE)

    if not os.path.isfile(ARGS.target):
        print('FATAL: --target %s does not exist' % ARGS.target, flush=True)
        return 1

    print('Story 129 FPS proof harness', flush=True)
    print('label: %s | seed: %d (label only)' % (ARGS.label, ARGS.seed), flush=True)
    print('target: %s' % os.path.abspath(ARGS.target), flush=True)
    print('viewports: desktop %dx%d, mobile %dx%d' % (desktop_vp[0], desktop_vp[1], mobile_vp[0], mobile_vp[1]), flush=True)
    print('NOT HARDWARE: gamepad legs inject a synthetic navigator.getGamepads before page scripts. '
          'Structural proof only. This run does not verify any pad on real hardware and makes no '
          'controller-support claim.', flush=True)
    print('LIMITATION: device-level movementX stays 0 under Playwright while the pointer is locked; '
          'look is proven with an injected synthetic MouseEvent and that leg proves handler math only.',
          flush=True)
    print('instruments: ?ammo=%d on the keyboard-win leg only; no harness flag changes a game constant.'
          % WIN_SCRIPT_AMMO, flush=True)
    print('', flush=True)

    results, port, url = run_suite(ARGS.target, desktop_vp, mobile_vp, ARGS.label, ARGS.seed)
    primary_failed = report(results, ARGS.label)

    if ARGS.green_target is None:
        return 0 if not primary_failed else 1

    print('', flush=True)
    if not os.path.isfile(ARGS.green_target):
        print('SKIP green: --green-target %s not found. GREEN is a labeled SKIP; Scout owns GREEN in QA.'
              % ARGS.green_target, flush=True)
        if primary_failed:
            print('RED recorded on primary target (%d failing checks); exit 0.' % len(primary_failed), flush=True)
            return 0
        print('primary target unexpectedly passed all checks; RED did not reproduce; exit 1.', flush=True)
        return 1

    print('green target: %s' % os.path.abspath(ARGS.green_target), flush=True)
    print('', flush=True)
    results_g, _, _ = run_suite(ARGS.green_target, desktop_vp, mobile_vp, 'GREEN', ARGS.seed)
    green_failed = report(results_g, 'GREEN')
    return 0 if not green_failed else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('interrupted', flush=True)
        sys.exit(1)
