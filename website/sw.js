/*
 * Flambeee service worker (Story 024, Session 15, v0.14.0)
 * Classic script, no build step. Scope: site root (hub + games/).
 *
 * Decisions (documented in PR for stories 023/024):
 *  - Precache failures: skip the failed entry and keep installing. The page
 *    must never block on a missing precache entry; a skipped asset simply
 *    falls back to network when online and is absent offline.
 *  - Cache versioning: bump CACHE_VERSION below whenever any shell asset
 *    changes. The new version installs, then deletes every older
 *    flambeee-shell-v* cache on activate. No stale asset mixing.
 *  - Activation semantics: skipWaiting + clients.claim. The two-version
 *    local test showed default semantics never activate the new cache while
 *    a tab stays open (old shell keeps serving, old cache never deleted);
 *    skipWaiting/claim make the bump land on the next reload.
 *  - Storage: this worker only touches its own cache namespace. It never
 *    reads or writes localStorage; cache deletions cannot affect it.
 */
'use strict';

var CACHE_VERSION = 1;
var CACHE_NAME = 'flambeee-shell-v' + CACHE_VERSION;

var PRECACHE_URLS = [
  './index.html',
  './manifest.webmanifest',
  './assets/favicon.ico',
  './assets/icon-192.png',
  './assets/icon-512.png',
  './assets/apple-touch-icon-180.png',
  './games/2048.html',
  './games/cinder.html',
  './games/minesweeper.html',
  './games/simon.html',
  './games/wordfire.html',
  './games/wordfire-words.js'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      // Individual adds, each with its own catch: skip-on-failure policy.
      return Promise.all(PRECACHE_URLS.map(function (url) {
        return cache.add(url).catch(function (err) {
          console.warn('[flambeee-sw] precache skipped (not fatal): ' + url, err);
        });
      }));
    }).then(function () {
      // Activate immediately. The two-version local test (dev-results.md)
      // showed default semantics keep the old shell serving until every
      // tab closes; skipWaiting makes the cache bump actually land.
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys
          .filter(function (key) {
            return key.indexOf('flambeee-shell-') === 0 && key !== CACHE_NAME;
          })
          .map(function (key) {
            return caches.delete(key);
          })
      );
    }).then(function () {
      // Take control of the already-open page so the new cache applies on
      // the next reload instead of the next tab open.
      return self.clients.claim();
    })
  );
});

self.addEventListener('fetch', function (event) {
  var request = event.request;
  if (request.method !== 'GET') return;
  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // same-origin only
  event.respondWith(cacheFirst(request));
});

function cacheFirst(request) {
  return caches.match(request).then(function (cached) {
    if (cached) return cached;
    return fetch(request).catch(function () {
      // Offline + cache miss. Navigations fall back to the cached shell so the
      // hub still loads from a deep link or the site root. Everything else
      // gets a clear error, never a crash.
      if (request.mode === 'navigate') {
        return caches.match('./index.html').then(function (index) {
          if (index) return index;
          return new Response('Offline. Nothing is cached yet.', {
            status: 503,
            statusText: 'Offline',
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      }
      return new Response('Offline. This asset is not cached.', {
        status: 503,
        statusText: 'Offline',
        headers: { 'Content-Type': 'text/plain' }
      });
    });
  });
}