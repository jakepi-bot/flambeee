# Story 174: public-leg probe plus noon poster gate (Session 75, P0)

**Status:** Ready for development (Session 75, 2026-11-28).
**Author:** Quinn, Business Analyst.
**Priority:** P0 (the session; ships alone if the wave runs short).
**Assigned to:** **Kai**, sole code owner.
**Files touched:** new `scripts/public-leg-probe.py` (stdlib only); one scoped insertion in the live poster `/home/jake/.hermes/flambeee/scripts/flambeee-post-noon.py`; mirror `scripts/flambeee-post-noon.mirror.py` plus pin `scripts/flambeee-post-noon.mirror.py.sha256`; new matrix cases in `scripts/test-noon-failure-alert.sh`. No other files.
**Depends on:** `flambeee-team/design-handoff.md` Section 1 (Session 75) and decision 011; held post `flambeee-team/state/held-post-v0.61.0.txt` stays staged, nothing posts from this story.

## Context

Yesterday the public site was dark for about 24 hours while the container stayed healthy, and the only detector was a human reading a release log at 02:55.
The noon poster guards length, stale version, and creds but has no public-leg check, so it would have posted a flambeee.com link straight into that outage, which is why the v0.61.0 announcement was held.
This story adds a stdlib preflight probe plus a scoped poster gate so a dead public leg blocks loudly with pending kept, and keeps the audit mirror byte-identical.

## Functional requirements

FR-1 (probe legs). Per-hostname leg order is normative with short-circuit: (a) DNS via `socket.getaddrinfo(host, 443)` returns at least one address or the leg ends FAIL with no TLS attempt; (b) TLS plus HTTP via stdlib `ssl.create_default_context()` with `http.client.HTTPSConnection(host, 443, context=ctx, timeout=PROBE_TIMEOUT_S)` and `GET /`, requiring a handshake, a cert valid for that hostname (SAN match, dates live), and HTTP exactly 200; (c) sha256 equality of raw body bytes against the tailnet origin. Never call `ssl.match_hostname` (removed in Python 3.13).
FR-2 (origin and verdict). Fetch the origin baseline `http://100.65.253.95:8080/index.html` once in SETUP with `ORIGIN_TIMEOUT_S`; on failure exit RED 2 with no verdict. Apex FAIL gives exit 1. Apex PASS plus www FAIL prints one loud `NOTE: www public leg failed (<reason>)` line and exits 0. Both PASS exits 0 with one PASS line per leg plus one RESULT line. `--red-anchor` runs loopback fixtures only and exits 2. Exit discipline: 0 PASS, 1 FAIL, 2 RED.
FR-3 (gate). Normative position: after the version guard ALLOW, after the `FLAMBEEE_DRY_RUN` early return, after all existing pre-flights, immediately before the STAGED POST print. Predicate: `flambeee.com` in `text.casefold()`, no boundary exceptions. On match, run the probe with `GATE_TIMEOUT_S`; exit 0 posts, nonzero routes through `fail_loud("public-leg", <last 300 chars>, code=<exit>)` with pending kept and one alert line. Never log-and-continue.
FR-4 (tuning). `PROBE_TIMEOUT_S` 12 s per op (matches the incident probes), `HOST_BUDGET_S` 45 s per leg, `ORIGIN_TIMEOUT_S` 12 s, `GATE_TIMEOUT_S` 120 s. Probe constants live in `scripts/public-leg-probe.py`; the gate timeout lives in the live poster (mirrored). `FLAMBEEE_PUBLIC_PROBE` overrides the probe path for the stub matrix; `FLAMBEEE_REPO` is honored as today.
FR-5 (mirror protocol). After the gate lands, update the mirror and the sha256 pin so `scripts/verify-poster-mirror.sh` exits 0 printing `mirror == live == pin`. Mirror, live, and pin disagreeing means this story is not done.
FR-6 (edge cases). Uppercase `FLAMBEEE.COM` fires the gate; pending-absent and empty-buffer paths run before the gate so it is unreachable there; a probe slower than `GATE_TIMEOUT_S` or a missing probe file counts as probe-nonzero with pending kept; an origin failure blocks via fail_loud and the release wave reruns the probe by hand.

## Acceptance criteria (BDD, contract 1.7 verbatim)

1. Given staged text naming `https://flambeee.com` and a stub probe exiting 1 with a marker file, when the poster runs, then it exits 1, the alert log gains a `mode=public-leg` line with that exit, pending is kept byte-identical, and the marker file exists.
2. Given staged text naming `flambeee.com`, a stub probe exiting 0, dummy creds, and a fake helper printing an `at://` URI, when the poster runs, then it exits 0 and pending is cleared.
3. Given staged text with no `flambeee.com` substring and a stub probe exiting 1, when the poster runs with the fake helper, then it exits 0 and the stub marker file is absent.
4. Given the gate landed, when `scripts/verify-poster-mirror.sh` runs, then it exits 0 printing `mirror == live == pin`.
5. Given `--red-anchor`, when the probe runs with no external network, then it exits 2 deterministically naming the divergent loopback fixture.
6. Given apex down and www up (stubbed per-leg), when the probe runs, then it exits 1. Given apex up and www down, when the probe runs, then it exits 0 with a loud NOTE line.

## Out of scope

OUT OF SCOPE: no cron change, no `deploy-website.sh` change, no website bytes, no new schedule; unlinked text never probes; www failure never blocks; apex failure is never a NOTE; verdicts are absolute, never statistical.

## Proof required in the dev record

PROOF: paste the four-case matrix log from `scripts/test-noon-failure-alert.sh` (probe-fail blocks, probe-pass allows, no-link text skips the probe, `scripts/verify-poster-mirror.sh` exits 0 with `mirror == live == pin`) plus the real `scripts/public-leg-probe.py` RESULT line the release wave reruns by hand.

## Notes

Normative source is contract Section 1 (1.1 states and transitions, 1.2 formulas, 1.3 tuning, 1.4 edge cases, 1.5 failure modes, 1.6 Plan B, 1.7 BDD, 1.8 rationale) with reading choices 1 and 2 at the top (substring predicate, www NOTE-only).
Plan B: if the gate cannot be proven against the real poster file without risking the live path, ship the probe alone and keep the gate as a named follow-up; never weaken to log-and-continue.
Dry runs never probe: placement after the `FLAMBEEE_DRY_RUN` return keeps the existing dry-run matrix case network-free.
Stories 175 and 176 are independent and cut after this one per the cut order; this story never carries their bytes.
