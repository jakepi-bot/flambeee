#!/usr/bin/env python3
"""Flambeee live-site smoke harness (Story 175, Session 75).

Proves the deployed copy is the repo copy: a STATIC leg over all 19 pages
(hub, 12 games, 6 app pages) plus a headless-Chromium desktop leg over all 19
and a mobile leg over the hub plus 3 fixed sampled games.

Modes: --base (default https://flambeee.com), --local (serve website/ on
127.0.0.1 from a fixed port range), --pages (comma subset filter for
triage), --red-anchor (scratch copy of website/ minus games/simon.html,
STATIC leg only, expects failure).

Exit discipline: 0 PASS, 1 FAIL, 2 RED, 3 SKIP (Playwright absent).
Cleanup kills only the spawned server PID, never ps scans or bare pkill.

Normative source: flambeee-team/design-handoff.md Section 2.
"""

import argparse
import hashlib
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

PAGE_COUNT = 19
PRECACHE_EXPECTED = 25

GAME_PAGES = [
    "games/2048.html",
    "games/afterglow.html",
    "games/cinder.html",
    "games/echo-rounds.html",
    "games/empty-hands.html",
    "games/lightfare.html",
    "games/minesweeper.html",
    "games/saltline.html",
    "games/simon.html",
    "games/trace.html",
    "games/typewreck.html",
    "games/wordfire.html",
]

APP_PAGES = [
    "apps/coin.html",
    "apps/convert.html",
    "apps/dice.html",
    "apps/tally.html",
    "apps/timer.html",
]

HUB_PAGE = "index.html"
APPS_INDEX = "apps/index.html"

ALL_PAGES = [HUB_PAGE] + GAME_PAGES + [APPS_INDEX] + APP_PAGES

MOBILE_SAMPLE = ["games/trace.html", "games/2048.html", "games/wordfire.html"]
MOBILE_PAGES = [HUB_PAGE] + MOBILE_SAMPLE

NAV_TIMEOUT_MS = 15000
MAX_RETRIES = 1
DESKTOP_VIEWPORT = {"width": 1280, "height": 800}
MOBILE_VIEWPORT = {"width": 375, "height": 667}
WAIT_UNTIL = "load"

HTTP_TIMEOUT_S = 15
PORT_RANGE_START = 49152
PORT_RANGE_END = 49215

RED_ANCHOR_MISSING = "games/simon.html"

CACHE_VERSION_RE = re.compile(r"var\s+CACHE_VERSION\s*=\s*(\d+)\s*;")
PRECACHE_BLOCK_RE = re.compile(r"PRECACHE_URLS\s*=\s*\[(.*?)\]", re.S)
PRECACHE_ENTRY_RE = re.compile(r"""['"]([^'"]+)['"]""")
HREF_RE = re.compile(r'href="(games/[^"]*\.html|apps/[^"]*\.html)"')


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def newest_tag(repo):
    out = subprocess.run(
        ["git", "tag", "--sort=-v:refname"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if out.returncode != 0:
        raise RuntimeError("git tag failed: %s" % out.stderr.strip()[:200])
    tags = [t for t in out.stdout.split() if t]
    if not tags:
        raise RuntimeError("no git tags found")
    return tags[0]


def fetch(url, timeout=HTTP_TIMEOUT_S):
    """GET url. Returns (status, content_type, body) or raises RuntimeError."""
    req = urllib.request.Request(url, headers={"User-Agent": "flambeee-site-smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:
        raise RuntimeError("%s: %s" % (type(e).__name__, str(e)[:160]))


def parse_precache(sw_text):
    m = PRECACHE_BLOCK_RE.search(sw_text)
    if not m:
        raise ValueError("PRECACHE_URLS block not found in sw.js")
    entries = PRECACHE_ENTRY_RE.findall(m.group(1))
    seen = []
    for e in entries:
        e = e.lstrip("./")
        if e and e not in seen:
            seen.append(e)
    return seen


def static_leg(base, repo, pages=None, sweeps=True):
    """Run the STATIC leg. Returns (pages_ok, failing, info).

    pages restricts the per-page 200 checks (subset triage). sweeps
    enables the hub-link, precache, version, sha and tag checks, which
    fetch URLs beyond the named pages and run on full runs only.
    """
    failing = []
    pages_ok = 0
    if pages is None:
        pages = list(ALL_PAGES)

    try:
        tag = newest_tag(repo)
    except Exception as e:
        raise RuntimeError("tag oracle unavailable: %s" % e)

    try:
        with open(os.path.join(repo, "website", "sw.js"), "r") as f:
            repo_sw = f.read()
    except Exception as e:
        raise RuntimeError("repo sw.js unreadable: %s" % e)
    m = CACHE_VERSION_RE.search(repo_sw)
    if not m:
        raise RuntimeError("CACHE_VERSION not found in repo sw.js")
    repo_version = m.group(1)

    try:
        with open(os.path.join(repo, "website", "index.html"), "rb") as f:
            repo_index = f.read()
    except Exception as e:
        raise RuntimeError("repo index.html unreadable: %s" % e)
    repo_sha = hashlib.sha256(repo_index).hexdigest()

    if not sweeps:
        for rel in pages:
            url = base + "/" + rel
            try:
                es, ect, _ = fetch(url)
            except RuntimeError as e:
                failing.append(("FAIL", url, "STATIC", "page fetch error %s" % e))
                continue
            if es == 200 and "text/html" in (ect or ""):
                pages_ok += 1
            else:
                failing.append(("FAIL", url, "STATIC",
                                "status=%s content-type=%r" % (es, ect)))
        info = {"tag": tag, "repo_version": repo_version,
                "served_version": None, "repo_sha": repo_sha,
                "served_sha": None, "precache": []}
        return pages_ok, failing, info

    try:
        st, ct, hub_body = fetch(base + "/" + HUB_PAGE)
    except RuntimeError as e:
        failing.append(("FAIL", base + "/" + HUB_PAGE, "STATIC", "hub fetch error %s" % e))
        return 0, failing, {"tag": tag, "repo_version": repo_version,
                            "served_version": None, "repo_sha": repo_sha,
                            "served_sha": None, "precache": []}
    hub_text = hub_body.decode("utf-8", "replace")

    if st != 200 or "text/html" not in (ct or ""):
        failing.append(("FAIL", base + "/" + HUB_PAGE, "STATIC",
                        "hub status=%s content-type=%r" % (st, ct)))

    try:
        st, ct, sw_body = fetch(base + "/sw.js")
    except RuntimeError as e:
        failing.append(("FAIL", base + "/sw.js", "STATIC", "sw.js fetch error %s" % e))
        sw_body, st = None, None
    served_version = None
    precache = []
    if sw_body is not None:
        if st != 200:
            failing.append(("FAIL", base + "/sw.js", "STATIC",
                            "sw.js status=%s" % st))
        else:
            sw_text = sw_body.decode("utf-8", "replace")
            mv = CACHE_VERSION_RE.search(sw_text)
            served_version = mv.group(1) if mv else None
            if served_version != repo_version:
                failing.append(("FAIL", base + "/sw.js", "STATIC",
                                "CACHE_VERSION served=%s repo=%s" % (served_version, repo_version)))
            try:
                precache = parse_precache(sw_text)
            except ValueError as e:
                failing.append(("FAIL", base + "/sw.js", "STATIC", str(e)))
            if len(precache) != PRECACHE_EXPECTED:
                failing.append(("FAIL", base + "/sw.js", "STATIC",
                                "precache count=%d expected=%d" % (len(precache), PRECACHE_EXPECTED)))
            for entry in precache:
                url = base + "/" + entry
                try:
                    es, _, _ = fetch(url)
                except RuntimeError as e:
                    failing.append(("FAIL", url, "STATIC", "precache fetch error %s" % e))
                    continue
                if es != 200:
                    failing.append(("FAIL", url, "STATIC",
                                    "precache status=%s" % es))

    served_sha = hashlib.sha256(hub_body).hexdigest()
    if served_sha != repo_sha:
        failing.append(("FAIL", base + "/" + HUB_PAGE, "STATIC",
                        "index sha256 served=%s repo=%s" % (served_sha[:12], repo_sha[:12])))

    if tag not in hub_text:
        failing.append(("FAIL", base + "/" + HUB_PAGE, "STATIC",
                        "hub heading names no tag %s" % tag))

    for href in sorted(set(HREF_RE.findall(hub_text))):
        url = base + "/" + href
        try:
            es, _, _ = fetch(url)
        except RuntimeError as e:
            failing.append(("FAIL", url, "STATIC", "hub link fetch error %s" % e))
            continue
        if es != 200:
            failing.append(("FAIL", url, "STATIC", "hub link status=%s" % es))

    for rel in pages:
        url = base + "/" + rel
        try:
            es, ect, _ = fetch(url)
        except RuntimeError as e:
            failing.append(("FAIL", url, "STATIC", "page fetch error %s" % e))
            continue
        if es == 200 and "text/html" in (ect or ""):
            pages_ok += 1
        else:
            failing.append(("FAIL", url, "STATIC",
                            "status=%s content-type=%r" % (es, ect)))

    info = {"tag": tag, "repo_version": repo_version,
            "served_version": served_version, "repo_sha": repo_sha,
            "served_sha": served_sha, "precache": precache}
    return pages_ok, failing, info


def wait_for_port(port, proc, deadline_s=10):
    end = time.time() + deadline_s
    while time.time() < end:
        if proc.poll() is not None:
            return False
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return proc.poll() is None


def serve_local(root, start=PORT_RANGE_START, end=PORT_RANGE_END):
    """Serve root on 127.0.0.1 from a fixed port range.

    Returns (proc, port). Raises RuntimeError if no port is free.
    Only the spawned PID is ever signalled by stop_server().
    """
    tried = end - start + 1
    for port in range(start, end + 1):
        proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port),
             "--bind", "127.0.0.1", "--directory", root],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if wait_for_port(port, proc):
            return proc, port
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    raise RuntimeError("no free port in range %d-%d (%d tried)" % (start, end, tried))


def stop_server(proc):
    if proc is None:
        return
    try:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:
        pass


ANCHOR_JS = """() => ({
  h1: (document.querySelector('h1') || {textContent: ''}).textContent.trim(),
  title: document.title.trim(),
  control: !!document.querySelector('input, button')
})"""

GAME_ANCHORS = {
    "games/2048.html": ("#grid", "none"),
    "games/afterglow.html": ("#board", "none"),
    "games/cinder.html": ("#promptInput", "none"),
    "games/echo-rounds.html": ("canvas", "none"),
    "games/empty-hands.html": ("#screen", "buttons"),
    "games/lightfare.html": ("#board", "none"),
    "games/minesweeper.html": ("#board", "none"),
    "games/saltline.html": ("#screen", "buttons"),
    "games/simon.html": (".game-board", "pads"),
    "games/trace.html": ("canvas", "none"),
    "games/typewreck.html": ("canvas", "none"),
    "games/wordfire.html": ("#board", "none"),
}

GAME_ANCHOR_JS = """(a) => {
  var el = document.querySelector(a.sel);
  if (!el) return 'missing ' + a.sel;
  var cs = getComputedStyle(el);
  if (cs.display === 'none') return a.sel + ' display none';
  if (cs.visibility === 'hidden') return a.sel + ' visibility hidden';
  if (!(el.offsetWidth > 0 && el.offsetHeight > 0)) return a.sel + ' zero size';
  if (a.comp === 'buttons') {
    var n = el.querySelectorAll('button').length;
    if (n < 1) return a.sel + ' has no button inside';
  } else if (a.comp === 'pads') {
    var p = el.querySelectorAll('.pad').length;
    if (p !== 4) return a.sel + ' has ' + p + ' .pad children, want 4';
  }
  return '';
}"""

OVERFLOW_JS = ("document.documentElement.scrollWidth <= window.innerWidth "
               "? '' : ('overflow scrollWidth=' + "
               "document.documentElement.scrollWidth + ' innerWidth=' + window.innerWidth)")


def browser_legs(base, desktop_pages, mobile_pages):
    """Run BROWSER_DESKTOP and BROWSER_MOBILE. Returns (desk_ok, mob_ok, failing).

    Raises RuntimeError with a SKIPPED message when Playwright is absent
    or Chromium cannot launch. Retries exactly 1 per page on navigation
    timeout only; console errors and anchor misses never retry.
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    except Exception as e:
        raise RuntimeError("SKIPPED: browser leg (playwright import failed: %s)" % e)

    failing = []
    desk_ok = 0
    mob_ok = 0
    try:
        pw = sync_playwright().start()
    except Exception as e:
        raise RuntimeError("SKIPPED: browser leg (playwright start failed: %s)" % e)
    try:
        try:
            browser = pw.chromium.launch()
        except Exception as e:
            raise RuntimeError("SKIPPED: browser leg (chromium launch failed: %s)" % e)
        try:
            ctx = browser.new_context(viewport=dict(DESKTOP_VIEWPORT))
            page = ctx.new_page()
            derrors = attach_error_tap(page)
            for rel in desktop_pages:
                url = base + "/" + rel
                if run_desktop_page(page, url, rel, PwTimeout, failing, derrors):
                    desk_ok += 1
            page.close()
            ctx.close()

            mctx = browser.new_context(viewport=dict(MOBILE_VIEWPORT))
            mpage = mctx.new_page()
            merrors = attach_error_tap(mpage)
            for rel in mobile_pages:
                url = base + "/" + rel
                if run_mobile_page(mpage, url, rel, PwTimeout, failing, merrors):
                    mob_ok += 1
            mpage.close()
            mctx.close()
        finally:
            browser.close()
    finally:
        pw.stop()
    return desk_ok, mob_ok, failing


def attach_error_tap(page):
    errors = []
    page.on("console", lambda msg: errors.append("console:%s" % msg.text[:160])
            if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append("pageerror:%s" % str(exc)[:160]))
    return errors


def goto_once(page, url, PwTimeout, errors):
    del errors[:]
    page.goto(url, wait_until=WAIT_UNTIL, timeout=NAV_TIMEOUT_MS)


def run_desktop_page(page, url, rel, PwTimeout, failing, errors):
    try:
        goto_once(page, url, PwTimeout, errors)
    except Exception as e:
        if "Timeout" in type(e).__name__ or "timeout" in str(e)[:64].lower():
            print("RETRY: %s (navigation timeout, attempt 2/2)" % url, flush=True)
            try:
                goto_once(page, url, PwTimeout, errors)
            except Exception as e2:
                failing.append(("FAIL", url, "DESKTOP",
                                "navigation timeout twice: %s" % str(e2)[:120]))
                return False
        else:
            failing.append(("FAIL", url, "DESKTOP", "load error: %s" % str(e)[:160]))
            return False
    if errors:
        failing.append(("FAIL", url, "DESKTOP",
                        "%d console/page error(s), first: %s" % (len(errors), errors[0])))
        check_desktop_anchor(page, url, rel, failing)
        return False
    return check_desktop_anchor(page, url, rel, failing)


def check_desktop_anchor(page, url, rel, failing):
    try:
        r = page.evaluate(ANCHOR_JS)
    except Exception as e:
        failing.append(("FAIL", url, "DESKTOP", "anchor eval error: %s" % str(e)[:120]))
        return False
    if rel == HUB_PAGE:
        if r["h1"]:
            return True
        failing.append(("FAIL", url, "DESKTOP", "anchor: empty h1"))
        return False
    if rel in GAME_PAGES:
        missing = []
        if not r["title"]:
            missing.append("empty title")
        row = GAME_ANCHORS.get(rel)
        if row is None:
            missing.append("no anchor row in table for %s" % rel)
        else:
            try:
                detail = page.evaluate(GAME_ANCHOR_JS,
                                       {"sel": row[0], "comp": row[1]})
            except Exception as e:
                missing.append("anchor eval error: %s" % str(e)[:120])
                detail = None
            if detail:
                missing.append(detail)
        if not missing:
            return True
        failing.append(("FAIL", url, "DESKTOP", "anchor: %s" % " and ".join(missing)))
        return False
    if rel == APPS_INDEX:
        if r["h1"] and r["control"]:
            return True
        missing = []
        if not r["h1"]:
            missing.append("empty h1")
        if not r["control"]:
            missing.append("no input or button")
        failing.append(("FAIL", url, "DESKTOP", "anchor: %s" % " and ".join(missing)))
        return False
    if r["control"]:
        return True
    failing.append(("FAIL", url, "DESKTOP", "anchor: no input or button"))
    return False


def run_mobile_page(page, url, rel, PwTimeout, failing, errors):
    try:
        goto_once(page, url, PwTimeout, errors)
    except Exception as e:
        if "Timeout" in type(e).__name__ or "timeout" in str(e)[:64].lower():
            print("RETRY: %s (navigation timeout, attempt 2/2)" % url, flush=True)
            try:
                goto_once(page, url, PwTimeout, errors)
            except Exception as e2:
                failing.append(("FAIL", url, "MOBILE",
                                "navigation timeout twice: %s" % str(e2)[:120]))
                return False
        else:
            failing.append(("FAIL", url, "MOBILE", "load error: %s" % str(e)[:160]))
            return False
    if errors:
        failing.append(("FAIL", url, "MOBILE",
                        "%d console/page error(s), first: %s" % (len(errors), errors[0])))
        return False
    try:
        overflow = page.evaluate(OVERFLOW_JS)
    except Exception as e:
        failing.append(("FAIL", url, "MOBILE", "overflow eval error: %s" % str(e)[:120]))
        return False
    if overflow:
        failing.append(("FAIL", url, "MOBILE", overflow))
        return False
    return True


def resolve_pages(tokens):
    if not tokens:
        return list(ALL_PAGES)
    wanted = []
    for tok in tokens:
        tok = tok.strip().lstrip("./")
        if not tok:
            continue
        if "/" in tok:
            match = tok if tok in ALL_PAGES else None
        else:
            hits = [p for p in ALL_PAGES if p == tok or p.endswith("/" + tok)]
            match = hits[0] if len(hits) == 1 else None
            if len(hits) > 1:
                match = None
        if match is None:
            raise RuntimeError("unknown page in --pages: %r (choose from %s)" % (tok, ", ".join(ALL_PAGES)))
        if match not in wanted:
            wanted.append(match)
    return wanted


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flambeee live-site smoke harness (Story 175).")
    ap.add_argument("--base", default="https://flambeee.com",
                    help="base URL under test (default https://flambeee.com)")
    ap.add_argument("--local", action="store_true",
                    help="serve website/ on 127.0.0.1 from a fixed port range")
    ap.add_argument("--pages", default="",
                    help="comma subset filter, e.g. --pages trace.html")
    ap.add_argument("--red-anchor", action="store_true",
                    help="serve a scratch copy minus games/simon.html, STATIC only, expect RED")
    args = ap.parse_args(argv)

    repo = repo_root()
    try:
        wanted = resolve_pages([t for t in args.pages.split(",") if t.strip()])
    except RuntimeError as e:
        print("RED: %s" % e)
        return 2
    subset = bool(args.pages.strip())

    server_proc = None
    scratch = None
    base = args.base.rstrip("/")
    red_mode = args.red_anchor
    try:
        if red_mode:
            scratch = tempfile.mkdtemp(prefix="site-smoke-red-")
            shutil.copytree(os.path.join(repo, "website"), os.path.join(scratch, "site"),
                            ignore=shutil.ignore_patterns("simon.html"))
            try:
                server_proc, port = serve_local(os.path.join(scratch, "site"))
            except RuntimeError as e:
                print("RED: local server: %s" % e)
                return 2
            base = "http://127.0.0.1:%d" % port
            print("BASE %s (red-anchor scratch, missing %s)" % (base, RED_ANCHOR_MISSING))
        elif args.local:
            try:
                server_proc, port = serve_local(os.path.join(repo, "website"))
            except RuntimeError as e:
                print("RED: local server: %s" % e)
                return 2
            base = "http://127.0.0.1:%d" % port
            print("BASE %s (local)" % base)
        else:
            print("BASE %s" % base)

        try:
            static_ok, failing, info = static_leg(base, repo, pages=wanted,
                                                 sweeps=not subset)
        except RuntimeError as e:
            print("RED: static leg: %s" % e)
            return 2
        if subset:
            print("SUBSET %s (sweeps skipped: hub links, precache, version, sha, tag)" % ",".join(wanted))
        else:
            print("CACHE_VERSION served=%s repo=%s" % (info["served_version"], info["repo_version"]))
            print("TAG newest=%s heading-match=%s" % (
                info["tag"],
                "yes" if not any("names no tag" in f[3] for f in failing) else "no"))
            print("INDEX sha256 served=%s repo=%s match=%s" % (
                (info["served_sha"] or "?")[:12], info["repo_sha"][:12],
                "yes" if info["served_sha"] == info["repo_sha"] else "no"))
            print("PRECACHE entries=%d expected=%d" % (len(info["precache"]), PRECACHE_EXPECTED))

        if red_mode:
            for sev, url, leg, reason in failing:
                print("FAILING: %s %s %s" % (url, leg, reason))
            n = len(wanted)
            print("PAGES %d/%d STATIC %d/%d BROWSER 0/0 MOBILE 0/0 (red-anchor, STATIC only)"
                  % (static_ok, n, static_ok, n))
            if any(RED_ANCHOR_MISSING in u for _, u, _, _ in failing):
                print("RED: red-anchor check failed as expected, missing %s" % RED_ANCHOR_MISSING)
                return 2
            print("FAIL: red-anchor fixture unexpectedly green")
            return 1

        desk_pages = [p for p in wanted]
        mob_pages = [p for p in wanted if p in MOBILE_PAGES]
        try:
            desk_ok, mob_ok, bfail = browser_legs(base, desk_pages, mob_pages)
        except RuntimeError as e:
            msg = str(e)
            if msg.startswith("SKIPPED:"):
                for sev, url, leg, reason in failing:
                    print("FAILING: %s %s %s" % (url, leg, reason))
                print(msg)
                n = len(wanted)
                print("PAGES %d/%d STATIC %d/%d BROWSER SKIPPED MOBILE SKIPPED"
                      % (static_ok, n, static_ok, n))
                return 3
            print("RED: browser leg: %s" % msg)
            return 2
        failing.extend(bfail)

        for sev, url, leg, reason in failing:
            print("FAILING: %s %s %s" % (url, leg, reason))

        n = len(wanted)
        dn = len(desk_pages)
        mn = len(mob_pages)
        if subset:
            names = ",".join(wanted)
            print("PAGES %d/%d (subset: %s) STATIC %d/%d BROWSER %d/%d MOBILE %d/%d"
                  % (static_ok, n, names, static_ok, n, desk_ok, dn, mob_ok, mn))
            if not failing:
                print("PASS (subset: %s)" % names)
                return 0
            print("FAIL (subset: %s)" % names)
            return 1

        print("PAGES %d/19 STATIC %d/19 BROWSER %d/19 MOBILE %d/4"
              % (static_ok, static_ok, desk_ok, mob_ok))
        if not failing and static_ok == PAGE_COUNT and desk_ok == PAGE_COUNT \
                and mob_ok == len(MOBILE_PAGES):
            print("PASS")
            return 0
        print("FAIL")
        return 1
    finally:
        stop_server(server_proc)
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
