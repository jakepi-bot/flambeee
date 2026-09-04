# Story 023 - PWA Install: Manifest, Theme Meta, Install Control (Session 15, v0.14.0)

**Status:** Ready for development (Session 15, v0.14.0)
**Author:** Quinn (Business Analyst)
**Priority:** P0 (headline feature of v0.14.0; first half of the PWA packaging work)
**Assigned to:** Kai (static infra: manifest, icon wiring). Riven (frontend: theme meta, install control, hub integration). Peer review across the aisle. QA by Scout (real browser taps required, per Session 14 QA bar).
**Tracked by:** Roadmap Future item "Mobile app packaging (PWA)". No community issue; this is retention-driven per the Session 15 plan (PWA is priority 1, the strongest retention play available without a new pull signal).

## Summary

Flambeee is a set of instantly-playable web games, all static single-file HTML served from one origin (flambeee.com). Today there is no way to "keep" the product. Players open a tab, play, lose the tab, and churn.

This story makes Flambeee installable as a home-screen web app. An installed app gets an icon on the phone (a permanent return path), launches in standalone mode (no browser chrome), and keeps working with the browser's native install prompt. This story covers the install half of the PWA packaging: the web app manifest, the theme/meta updates, and the install control on the hub. Offline behavior is Story 024.

The product remains exactly as it is: same origin, same static files, same localStorage stats, no accounts, no build step.

## Business value

- Retention is the session priority. An icon on the phone is a pull mechanism that costs the player nothing and removes the "lost the tab" churn driver.
- Installability is the natural 2026 packaging move for browser games: app-store-like return path without a store.
- The games are already static and same-origin, so the cost of this story is small: one manifest, a few meta tags, and a small install control.

## Requirements

1. **Web app manifest** at the site root (`manifest.webmanifest`), JSON, with:
   - `name` and `short_name` for Flambeee (names per the site: short_name short enough for a home-screen label)
   - `start_url` pointing at the hub (the site root)
   - `display: standalone`
   - `theme_color` and `background_color` matching the brand: `theme_color` `#1a1a2e` (navy surface), `background_color` `#0f1428` (site background). These are the existing `:root` values in index.html (`--surface`, `--bg`); the manifest must stay consistent with them.
   - `icons` array with a 192x192 and a 512x512 PNG, both on-brand
   - `scope` covering the whole site (hub + `games/`)
2. **On-brand icons.** 192px and 512px PNG icons generated from the Flambeee flame mark on the navy `#1a1a2e` surface with flame `#e94560` accent (Palette owns the icon art; Kai wires the files into the manifest and markup). An 180px `apple-touch-icon` is included for iOS. For storage space, the 512 icon must also look sharp at 192 (no aliasing downscale surprises).
3. **Theme and viewport meta on index.html** (Riven): a `theme-color` meta tag matching the manifest `theme_color`, so the mobile browser chrome matches the app in standalone and in the browser. Confirm the existing viewport tag is correct for standalone (no zoom issues); update only if needed.
4. **Install prompt handling** (Riven): capture `beforeinstallprompt`, prevent the default browser mini-infobar (no interstitial nagging), and expose the prompt through a small, on-brand Install control on the hub.
5. **Install control on the hub** (Riven): a single, unobtrusive Install button. It appears only when the app is installable, and it is hidden when the browser never fires `beforeinstallprompt` (already installed, unsupported browser, iOS Safari). No dead buttons, no error toast.
6. **No interstitial nagging.** The install prompt fires only from an explicit tap on the control. One attempt per session unless the user dismisses and taps again.
7. **Stats survive install.** Installing the app must not affect per-game stats, saves, or streaks. All localStorage keys continue to read and write exactly as in the browser tab. The games themselves are untouched.
8. **Deploy both copies, byte-identical.** All new/changed website files land in BOTH:
   - `/home/jake/.openclaw/workspace/share/Flambeee/` (live site, ABSOLUTE path; `share/` is outside the repo)
   - `website/` mirror in this repo
   - `cmp` passes for every file that exists in both places (standing practice from v0.12.0/v0.13.1).
9. **No game file changes.** The 5 game HTML files and `wordfire-words.js` are not edited in this story. Any needed game-page change must be raised as an open question in the PR first.
10. **No build step.** Static files only, same as today.

### Out of scope

- Service worker / offline caching (Story 024).
- New games, leaderboards, multiplayer, accounts. No storage-format changes.

## Acceptance Criteria (BDD)

### Scenario 1: Manifest serves and parses (P0, Kai)
- **Given** I request `https://flambeee.com/manifest.webmanifest`
- **When** the response returns
- **Then** it is HTTP 200 with a JSON body that includes `name`, `short_name`, `start_url`, `display` set to `standalone`, `theme_color`, `background_color`, and an `icons` array with at least one 192x192 and one 512x512 entry

### Scenario 2: Icons resolve and match brand (P0, Kai/Palette)
- **Given** the manifest and index.html reference the icon files
- **When** I load each referenced icon URL and the 180px apple-touch-icon
- **Then** each returns HTTP 200, is a square PNG at the declared size, and uses the navy `#1a1a2e` surface with the flame `#e94560` accent (checked visually by Palette)

### Scenario 3: Theme meta matches manifest (P0, Riven)
- **Given** index.html is updated
- **When** I read the `theme-color` meta tag and the manifest `theme_color`
- **Then** they are the same value (`#1a1a2e`) and the page renders dark with no white flash on load

### Scenario 4: Install prompt is intercepted (P0, Riven/Kai)
- **Given** a Chromium-based browser where the site meets install criteria (HTTPS, manifest present, service worker from Story 024 present)
- **When** I load the hub
- **Then** the page captures the `beforeinstallprompt` event, prevents the default browser infobar, and the Install control becomes visible

### Scenario 5: Install control installs the app (P0, Riven)
- **Given** the Install control is visible and the app is installable
- **When** I tap the Install control
- **Then** the native install prompt appears; when I accept, the `appinstalled` event fires, the control hides, and the app opens in standalone mode (no browser address bar)

### Scenario 6: Control hidden when not installable (P0, Riven)
- **Given** the app is not installable (already installed, or a browser that never fires `beforeinstallprompt`, such as iOS Safari)
- **When** I load the hub
- **Then** the Install control is not rendered at all, and no error appears in the console

### Scenario 7: No interstitial nagging (P1, Riven)
- **Given** I load the hub and have not tapped the Install control
- **When** I browse the site normally
- **Then** no install prompt or banner appears on its own; the prompt only follows an explicit tap on the control

### Scenario 8: Stats and saves survive install (P0, integration)
- **Given** I have existing plays, wins, scores, and streaks across the games in localStorage
- **When** I install the app and launch it from the home screen
- **Then** the hub shows the same stats as before, each game reads and writes its stats/saves exactly as in the browser tab, and no localStorage key or value is changed by the install

## Technical notes (Quinn)

- **Verified current state (2026-09-04):** `share/Flambeee/index.html` has a viewport meta but no `theme-color` meta, no manifest link, no service worker. Site dark theme variables: `--bg #0f1428`, `--surface #1a1a2e`, `--accent #e94560`. Existing brand icons are 16-512px in `brand/logo/`; the PWA icons are generated from the flame mark, not reused game screenshots.
- **`beforeinstallprompt` mechanics:** the event fires per session and may not refire after dismiss; keep the stored prompt reference and call `prompt()` on tap, then clear it after `appinstalled` or `beforeinstallprompt` rejection. Chrome requires a registered service worker (Story 024) plus valid manifest plus icons, so 023 and 024 must land together to be demonstrable.
- **iOS:** Safari does not fire `beforeinstallprompt`. The control stays hidden there; iOS users still get Add to Home Screen via Safari's share sheet. The 180px apple-touch-icon makes that path look right. Documented so nobody files a bug about a missing button on iOS.
- **Ownership split:** manifest + icons (Kai, static infra); theme meta + control + prompt wiring + hub integration (Riven). Both peer-review each other; Scout's test plan covers scenarios 1-8 with real browser taps.

## Visual description

Install control wireframe (text):
- Placement: top-right of the hub nav bar, beside the existing nav links. Small pill button, roughly 92x36px, flame gradient background (`#e94560` to `#ff5a75`, the existing `.btn-primary` gradient) with white 13px semibold label "Install" and a small download/plus glyph at left. Rounded 10px corners matching `.btn` radius. No icon when the label alone fits.
- Hover: translate up 1-2px with the existing flame shadow (`0 8px 24px rgba(233,69,96,0.4)`).
- Hidden state: `display: none`, no layout gap. When install completes, the button disappears; the nav returns to its pre-PWA layout exactly.
- The button is the only PWA chrome on the page. The hub itself is untouched: dark navy surface, flame accents, existing cards and modals.

## Open questions

1. **Install control placement.** Nav bar (top-right, always visible) vs hero CTA row (more visible, scrolls away). Recommended: nav bar. Riven confirms against actual nav layout during build and notes the choice in the PR.
2. **Icon art.** Palette delivers 192/512/180 from the flame mark. Kai should confirm the 512 renders crisply at 192 before signing off (Chrome uses the closest match).
3. **Game page meta.** If adding `theme-color` to game pages turns out to be needed for standalone polish, Riven raises it in the PR before touching game files (this story's baseline is zero game file edits).