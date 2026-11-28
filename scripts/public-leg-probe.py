#!/usr/bin/env python3
"""Flambeee public-leg probe (Story 174, Session 75).

Checks that the public site serves the deployed build, per hostname, in
strict order: DNS, then hostname-verified TLS plus HTTP 200, then sha256
parity of the raw served body against the tailnet origin baseline.

Stdlib only. No third-party imports.

Leg order per hostname (normative, short-circuit):
1. DNS: socket.getaddrinfo(host, 443) must return at least one address.
   On failure the leg ends here as FAIL; no TLS or fetch is attempted.
2. TLS plus HTTP: ssl.create_default_context() (check_hostname True,
   verify_mode CERT_REQUIRED) with http.client.HTTPSConnection and
   GET /. Requires a handshake, a cert valid for that hostname (SAN
   match plus live dates, checked by the context), and HTTP exactly 200.
   Never call ssl.match_hostname: Python 3.13 removed it.
3. Parity: sha256(body) == sha256(origin_body), raw bytes, no decode.

SETUP fetches the origin baseline once. If the origin fetch fails the
probe exits RED 2 immediately: no baseline means no verdict is possible.

Verdict: apex FAIL gives exit 1. Apex PASS plus www FAIL prints one loud
NOTE line and exits 0. Both PASS exits 0 with one PASS line per leg.
--red-anchor runs comparison plus DNS-failure paths against loopback
fixtures only and exits 2 deterministically.

Exit codes: 0 PASS, 1 FAIL (apex leg down), 2 RED (no baseline,
internal error, or --red-anchor).
"""

import hashlib
import http.client
import http.server
import socket
import ssl
import sys
import threading
import time
import urllib.request

PROBE_TIMEOUT_S = 12
HOST_BUDGET_S = 45
ORIGIN_TIMEOUT_S = 12
ORIGIN_URL = "http://100.65.253.95:8080/index.html"
APEX_HOST = "flambeee.com"
WWW_HOST = "www.flambeee.com"


def _fetch_origin():
    """Fetch the tailnet baseline once. Raises on any failure."""
    req = urllib.request.Request(ORIGIN_URL, method="GET")
    with urllib.request.urlopen(req, timeout=ORIGIN_TIMEOUT_S) as resp:
        if resp.status != 200:
            raise IOError("origin status %s (want 200)" % resp.status)
        return resp.read()


def run_leg(host, origin_hex):
    """Run one hostname leg. Returns (passed: bool, reason: str)."""
    deadline = time.monotonic() + HOST_BUDGET_S
    try:
        addrs = socket.getaddrinfo(host, 443)
    except socket.gaierror as exc:
        return (False, "DNS lookup failed for %s (%s)" % (host, exc))
    except Exception as exc:
        return (False, "DNS error for %s (%s)" % (host, exc))
    if not addrs:
        return (False, "DNS returned no addresses for %s" % host)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return (False, "host budget exhausted before TLS for %s" % host)
    timeout = min(PROBE_TIMEOUT_S, remaining)
    try:
        ctx = ssl.create_default_context()
        conn = http.client.HTTPSConnection(
            host, 443, context=ctx, timeout=timeout)
        try:
            conn.request("GET", "/")
            resp = conn.getresponse()
            status = resp.status
            body = resp.read()
        finally:
            conn.close()
    except ssl.SSLCertVerificationError as exc:
        return (False, "TLS cert invalid for %s (%s)" % (host, exc))
    except ssl.SSLError as exc:
        return (False, "TLS failed for %s (%s)" % (host, exc))
    except (socket.timeout, TimeoutError) as exc:
        return (False, "HTTP timeout for %s (%s)" % (host, exc))
    except Exception as exc:
        return (False, "HTTP fetch failed for %s (%s)" % (host, exc))
    if status != 200:
        return (False, "HTTP %s returned status %s (want 200)"
                % (host, status))
    digest = hashlib.sha256(body).hexdigest()
    if digest != origin_hex:
        return (False, "sha256 mismatch for %s (public %s != origin %s)"
                % (host, digest[:16], origin_hex[:16]))
    return (True, "sha256 %s" % digest[:16])


def _serve_bytes(payload):
    """Serve fixed bytes on 127.0.0.1, ephemeral port. Returns the server."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format, *args):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    return srv


def _fetch_loopback(port):
    conn = http.client.HTTPConnection(
        "127.0.0.1", port, timeout=PROBE_TIMEOUT_S)
    try:
        conn.request("GET", "/")
        resp = conn.getresponse()
        if resp.status != 200:
            raise IOError("loopback status %s" % resp.status)
        return resp.read()
    finally:
        conn.close()


def run_red_anchor():
    """Loopback-only fixture check. Always exits 2.

    Exercises the comparison path (two divergent bodies must mismatch)
    and the DNS-failure path (a reserved .invalid name must not resolve),
    naming the divergent fixture on every run. No external network.
    """
    srv_a = _serve_bytes(b"red-anchor origin baseline body")
    srv_b = _serve_bytes(b"red-anchor leg body DIVERGENT")
    try:
        port_a = srv_a.server_address[1]
        port_b = srv_b.server_address[1]
        body_a = _fetch_loopback(port_a)
        body_b = _fetch_loopback(port_b)
    finally:
        srv_a.shutdown()
        srv_b.shutdown()
    hex_a = hashlib.sha256(body_a).hexdigest()
    hex_b = hashlib.sha256(body_b).hexdigest()
    if hex_a == hex_b:
        print("FAIL red-anchor-fixture: loopback bodies unexpectedly agree")
    else:
        print("FAIL red-anchor-fixture www-leg: sha256 mismatch "
              "(divergent loopback fixture red-anchor-bodies "
              "%s != %s)" % (hex_b[:16], hex_a[:16]))
    try:
        socket.getaddrinfo("red-anchor.invalid", 443)
        print("FAIL red-anchor-fixture dns-path: reserved name resolved, "
              "expected DNS failure")
    except socket.gaierror as exc:
        print("FAIL red-anchor-fixture dns-path: DNS failure as expected "
              "(%s)" % exc)
    except Exception as exc:
        print("FAIL red-anchor-fixture dns-path: DNS error as expected "
              "(%s)" % exc)
    print("RESULT: RED (exit 2)")
    return 2


def main(argv):
    if argv == ["--red-anchor"]:
        return run_red_anchor()
    if argv:
        print("FAIL: unknown argument %r (want --red-anchor)" % (argv,))
        print("RESULT: RED (exit 2)")
        return 2
    try:
        origin_body = _fetch_origin()
    except Exception as exc:
        print("FAIL origin baseline %s: %s" % (ORIGIN_URL, exc))
        print("RESULT: RED (exit 2)")
        return 2
    origin_hex = hashlib.sha256(origin_body).hexdigest()
    apex_ok, apex_reason = run_leg(APEX_HOST, origin_hex)
    if apex_ok:
        print("PASS apex public leg (%s)" % apex_reason)
    else:
        print("FAIL apex public leg (%s)" % apex_reason)
        print("RESULT: FAIL (exit 1)")
        return 1
    www_ok, www_reason = run_leg(WWW_HOST, origin_hex)
    if www_ok:
        print("PASS www public leg (%s)" % www_reason)
    else:
        print("NOTE: www public leg failed (%s)" % www_reason)
    print("RESULT: PASS (exit 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
