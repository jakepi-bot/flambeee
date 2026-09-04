# Story 024 - PWA Offline: Service Worker + Shell Precache (Session 15, v0.14.0)

**Status:** Ready for development (Session 15, v0.14.0)
**Author:** Quinn (Business Analyst)
**Priority:** P0 (headline feature of v0.14.0; second half of the PWA packaging work, ships with Story 023)
**Assigned to:** Kai (backend/static infra: service worker, precache list, cache strategy). Riven (frontend: hub registration, integration with Story 023 install flow). Peer review across the aisle. QA by Scout (real browser taps + network-disabled reload required, per Session 14 QA bar).
**Tracked by:** Roadmap Future item "Mobile app packaging (PWA)". No community issue; retention-driven per the Session 15 plan.

## Summary

An installed app only earns its home-screen icon if it opens fast and works when the network is bad or gone. This story makes Flambeee offline-capable: a service worker precaches the entire static shell (hub, manifest, icons, all 5 games, and the Wordfire word list) on first visit, serves it cache-first, and replaces stale assets cleanly when a new version ships.

The games stay single-file and dependency-free. There is no build step, no runtime, no bundler. The service worker is a plain static file at the site root, registered from the hub.

Story 023 covers manifest and install; this story covers the service worker that makes installability and offline play real. The two land together.

## Business value

- Offline-first is what makes the app feel native: the hub and every game load instantly from cache after the first visit, and keep working with no network at all.
- Retention play: a player who opens the app on a commute, in a dead zone, or after losing connection still gets their games and their stats.
- Versioned caches give the release process a safe upgrade path: new assets replace old ones without stale mixes or user-visible breakage.

## Requirements

1. **Service worker file** `sw.js` at the site root (same directory as the hub), registered from index.html on page load. Scope covers the whole site (hub + `games/`).
2. **Precache the static shell** on install, under a versioned cache name (`flambeee-shell-v<version>`):
   - `index.html` (hub)
   - `manifest.webmanifest`
   - the 192, 512, and 180 icon files plus the favicon
   - all 5 game HTML files: `minesweeper.html`, `simon.html`, `2048.html`, `wordfire.html`, `cinder.html`
   - `wordfire-words.js` (Wordfire's word list; the game is broken without it)
3. **Cache-first with network fallback.** Intercepted requests for precached assets serve from cache (fast, no flicker); cache misses go to the network. Failed network requests for a cache miss fall back to a clear error, never a crash.
4. **Offline reload works.** After one successful online visit, the hub and every game load and play with the network disabled. No game file is edited; the cache alone makes this work.
5. **Cache version bump replaces stale assets.** When the precache list or any asset changes, bump the cache name (v1 to v2). On the next visit the new shell installs and activates, the old cache is deleted, and no request ever mixes assets from two versions (for example, a new index.html that references a missing game file).
6. **Storage is never cached.** The service worker only caches static files from the precache list. localStorage (stats, saves, streaks, settings) is untouched by the worker, its cache, or cache deletions.
7. **Registration is harmless in private mode and on failure.** If registration or the worker fails, the site still loads and plays exactly as before.
8. **Deploy both copies, byte-identical.** All new/changed website files land in BOTH:
   - `/home/jake/.openclaw/workspace/share/Flambeee/` (live site, ABSOLUTE path; `share/` is outside the repo)
   - `website/` mirror in this repo
   - `cmp` passes for every file that exists in both places (standing practice from v0.12.0/v0.13.1).

### Out of scope

- Manifest / install control (Story 023).
- Runtime or API caching; there is none, the product is static by design.
- New games, leaderboards, multiplayer, accounts. No storage-format changes.

## Acceptance Criteria (BDD)

### Scenario 1: Service worker registers (P0, Kai/Riven)
- **Given** I load the hub online in a browser that supports service workers
- **When** the page finishes loading
- **Then** `navigator.serviceWorker` registers `sw.js`, the registration succeeds with no console error, and the worker becomes active for the scope

### Scenario 2: Shell is precached on first visit (P0, Kai)
- **Given** I have visited the hub once online
- **When** I inspect the cache named `flambeee-shell-v<version>`
- **Then** it contains index.html, manifest.webmanifest, the icon files, the favicon, all 5 game HTML files, and `wordfire-words.js`

### Scenario 3: Offline reload of the hub (P0, Kai)
- **Given** I have visited the hub once online
- **When** I disable the network and reload the hub
- **Then** the hub renders fully from cache: layout, styles, game cards, and modals work, with no console errors

### Scenario 4: Offline reload of every game (P0, Kai)
- **Given** I have visited each game once online
- **When** I disable the network and load each game page (Minesweeper, Simon, 2048, Wordfire, Cinder) from the hub
- **Then** each game loads and is playable offline; Wordfire's daily puzzle works (its word list comes from the precached `wordfire-words.js`)

### Scenario 5: Cache-first with network fallback (P0, Kai)
- **Given** the shell is precached and I am online
- **When** I request a precached asset (e.g. a game page)
- **Then** the response comes from cache without a network round trip, and for a cache miss the request goes to the network and serves fresh content

### Scenario 6: Cache version bump replaces stale assets (P0, Kai)
- **Given** version 1 of the shell cache exists and the site deploys version 2 with an updated asset (for example a changed game file or index.html)
- **When** I visit the hub again online
- **Then** the new shell installs and activates, `flambeee-shell-v1` is deleted, and all pages under the scope consistently serve only version-2 assets with no stale mix

### Scenario 7: Stats and saves survive offline play and cache swaps (P0, Kai)
- **Given** I have stats, scores, and streaks in localStorage and the shell cache exists
- **When** I play offline and then a cache version bump happens on the next online visit
- **Then** every localStorage key and value is unchanged by the worker and its cache lifecycle, and my stats are exactly as before

### Scenario 8: Private mode and worker failure are safe (P1, Kai)
- **Given** I open the site in a private window, or the service worker fails to register or activate
- **When** I load the hub
- **Then** the site loads and plays exactly as before the worker existed, with no crash and no failed request that blocks the page

### Scenario 9: First visit requires network (expected, documented) (P1, Kai)
- **Given** I visit the hub for the very first time with the network disabled
- **When** the page loads
- **Then** the browser's offline behavior applies (no cached shell exists yet); this is expected and documented, not a defect. The shell exists after the first successful online visit.

## Technical notes (Quinn)

- **Verified current state (2026-09-04):** no service worker, no manifest on the site; all requests are same-origin and relative. Shell files to precache, from `share/Flambeee/:` index.html (34KB), assets/favicon.ico, plus `games/` = 2048.html, cinder.html, minesweeper.html, simon.html, wordfire.html, wordfire-words.js (58KB). Story 023 adds manifest.webmanifest + icon files to this list.
- **Versioning:** cache name `flambeee-shell-v<N>`. Bump strategy: new version installs and activates, then deletes older `flambeee-shell-v*` caches in the activate handler. Precache failures during install skip the failed entry (or abort install per dev choice); whichever is chosen, the page must never be blocked on a missing precache entry.
- **Activation control:** use `self.skipWaiting()` and `clients.claim()` only if integration testing shows stale-first-visit problems; otherwise prefer default activation semantics. Kai decides and documents in the PR.
- **Plain classic script:** `sw.js` is a classic script, no module, no build step. Register from index.html with `navigator.serviceWorker.register('sw.js')`.
- **Browser-proof bar (Session 14):** QA must prove offline with the network actually disabled (Playwright context offline / devtools offline), not just by claiming cache hits. Real taps required for playability claims.
- **Ownership split:** sw.js + cache strategy + versioning (Kai); registration call + any hub markup glue + offline-state UI if needed (Riven). Both peer-review each other.

## Visual description

None required: this story is invisible by design. The only allowed visible effect is that offline reloads render identically to online reloads. If anything looks different offline, it is a bug.

## Open questions

1. **Failed precache entries.** Skip-on-failure vs install-abort on any failure. Kai decides; the page must never block either way. Requested: document the choice in the PR.
2. **Activation timing.** Whether to use skipWaiting/clients.claim depends on how the dev wave ships the v2 bump. Kai verifies with a two-version local test and documents the result.
3. **Wordfire daily seed offline.** The word list is precached and daily seeds are UTC-time-based (Story 016), so offline play needs no network. Scout should confirm one offline daily solve as part of Scenario 4 so nobody has to guess later.