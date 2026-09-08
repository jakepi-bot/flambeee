# Test Plan — Story 028: Website Daily-Habit / Community Surface (v0.16.0)

**QA:** Scout | **Date:** 2026-09-08 | **Source:** `docs/stories/028-website-daily-habit-community-surface.md`
**QA bar:** Session 14 — real click + narrow mobile viewport check.

## Scope

A small, on-brand retention/community surface on flambeee.com: a "Play today" callout strip (rotates Cinder daily quest / Wordfire daily word by UTC day) plus a "Join the community" anchor to the GitHub repo. Live file `share/Flambeee/index.html`; repo mirror `website/index.html` must be byte-identical.

## Test Environment

- Browser: Chromium via Playwright (`.venv/bin/python3`).
- Files under test: repo `website/index.html` and live `share/Flambeee/index.html`.
- Brand palette: navy `#1a1a2e`, flame `#e94560`.

## BDD Scenario → Test Case Mapping

### Scenario 1: Surface renders on the site (P1)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 028-1.1 | Play today strip visible | Load index.html; wait for render | `#playToday` visible, not hidden; contains "Play today" eyebrow |
| 028-1.2 | No layout break | Desktop viewport (1280px) | No horizontal scroll; existing Game of the Week banner still present |

### Scenario 2: Surface points at real, working content (P1)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 028-2.1 | Relative play link loads game | Click Play button | Navigates to `games/cinder.html` or `games/wordfire.html` (relative, same-origin) |
| 028-2.2 | Deterministic UTC rotation | Evaluate `renderPlayToday` logic | Even UTC day → Cinder, odd → Wordfire; same for all visitors that day |
| 028-2.3 | Boundary: day index parity | Check `dayIdx % 2` | Both branches produce a valid play link |

### Scenario 3: Community link is a real clickable link (P1)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 028-3.1 | Real anchor to GitHub | Inspect `.play-today-community` | `<a href="https://github.com/jakepi-bot/flambeee" target="_blank" rel="noopener">`, not a fake button |
| 028-3.2 | Opens in new context | Check `target="_blank"` + `rel="noopener"` | New tab, no opener leak |

### Scenario 4: Mobile renders with no layout break (P1)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 028-4.1 | Narrow viewport stacks full-width | 375px viewport | `.play-today` stacks (flex-direction column); no horizontal scroll (`scrollWidth <= clientWidth`) |
| 028-4.2 | Tappable on mobile | 375px; click Play and community links | Both clickable, hit targets not overlapped |
| 028-4.3 | Boundary: 320px (smallest common) | 320px viewport | Still no horizontal scroll, tappable |

### Scenario 5: Missing/invalid content degrades gracefully (P1)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 028-5.1 | Missing play link | Stub `DAILY_ORDER` item with no `playLink` | Strip hides (`hidden=true`), no unhandled error |
| 028-5.2 | Missing name | Stub item with no `name` | Strip hides, no error |
| 028-5.3 | Missing element | Remove `#playToday` from DOM | `renderPlayToday` returns early, no throw |
| 028-5.4 | Invalid content | Stub item with null/undefined | Strip hides, no broken layout |

### Scenario 6: On-brand visuals (P1 + Palette)
| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| 028-6.1 | Brand palette used | Inspect computed styles | Navy `#1a1a2e` and flame `#e94560` present in callout styling |
| 028-6.2 | Matches site identity | Visual check | Consistent with Game of the Week banner and site theme |

## Edge Cases / Boundary Conditions

- **UTC day parity** (even/odd) both produce valid content.
- **320px and 375px** mobile widths.
- **Missing/invalid content** (playLink, name, element) → graceful hide, no throw.
- **Deployment sync:** repo `website/index.html` and live `share/Flambeee/index.html` byte-identical (`cmp`).

## Negative Tests

- `#playToday` element removed → no unhandled error.
- `DAILY_ORDER` item missing `playLink`/`name` → strip hides.
- Null/undefined item → strip hides, no broken layout.
