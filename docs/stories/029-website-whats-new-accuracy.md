# Story 029 — Website: "What's New" Accuracy Fix (Session 18, P0)

**Status:** Approved for dev wave (Session 18). Priority P0 — the one verifiable, user-visible website accuracy defect.
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** P0
**Assigned to:** Riven (frontend/website). No backend. No game-file change, so no `games/` resync is required unless a game file changes. Kai peer review. QA by Scout (real click + content check). Vigil verifies copy accuracy/compliance.
**Tracked by:** Session 18 plan, Priority 1. The website is a standing brand surface (CEO 2026-08-14). The "What's New" section shows stale release content, which is a real accuracy defect on the product's home page.

## Summary

The "What's New" section on flambeee.com still reads **v0.15.0** ("Cinder's daily quest + Game of the Week"). The true latest release is **v0.16.0** ("Cinder quest polish + Play today"), shipped 2026-09-08. The "Play today" strip (Story 028) shipped correctly in v0.16.0, but the "What's New" section was not bumped, so the site now presents stale release information to every visitor. This story fixes that single accuracy defect for the home page.

The change is a frontend (website) copy/content update on `share/Flambeee/index.html` (the live source of truth), mirrored to the repo's `website/index.html`. Both copies must stay byte-identical (standing rule; verify with `cmp`).

## Business value

- Fixes a visible inaccuracy on the product's home page: what the site advertises as "new" is a release behind reality.
- Keeps the brand surface truthful and current (culture.md: truthful and accurate info).
- Low risk: content-only, no structural/layout change, no game-file change.

## User Story

As a visitor to flambeee.com,
I want the "What's New" section to reflect the latest release (v0.16.0) with an accurate headline and summary,
So that what the site advertises as new is truthful and current.

## Requirements

1. **Accurate release headline.** The "What's New" section headline must reflect the latest release, **v0.16.0** ("Cinder quest polish + Play today").
2. **Accurate summary.** The summary must describe the v0.16.0 changes accurately: Cinder quest polish (completed quest tails read `[Done]`, gold quest counts combat gold only) and the "Play today" callout / daily-habit community surface. Do not invent features beyond the roadmap's v0.16.0 entry.
3. **Both copies in sync.** Update `share/Flambeee/index.html` and mirror to `website/index.html`; verify they are byte-identical (`cmp`), per the standing rule.
4. **No scope creep.** Content-only update. No layout change, no structural change, no game-file change, no service-worker change, no redesign. Do not touch other sections.

### Out of scope

- Any bump beyond reflecting the current release.
- Any redesign or layout overhaul of the site or the "What's New" section.
- Any game-file or gameplay change (Cinder balance is separately decided in Story 031, decision-record only).
- Any release notes or changelog edits beyond the website.

## Acceptance Criteria (BDD)

### Scenario 1: What's New reflects v0.16.0 (P0, Riven)
- **Given** I visit flambeee.com
- **When** I read the "What's New" section
- **Then** its headline identifies **v0.16.0** (not v0.15.0 or lower) as the latest release

### Scenario 2: What's New summary is accurate (P0, Riven)
- **Given** I read the "What's New" summary
- **When** I compare it to the v0.16.0 release notes in the roadmap
- **Then** it accurately describes the v0.16.0 changes (Cinder quest polish + Play today) and does not advertise features from a release newer than v0.16.0 or invent unreleased features

### Scenario 3: Repo mirror stays byte-identical (P0, Riven)
- **Given** both `share/Flambeee/index.html` and `website/index.html` have been updated
- **When** I run `cmp` on the two files
- **Then** they are byte-identical (standing deployment rule)

### Scenario 4: No layout/UX regression (P0, Riven)
- **Given** the "What's New" section is updated
- **When** the page renders on desktop and a narrow mobile viewport
- **Then** the section displays correctly with no broken layout, no horizontal scroll, and all existing links/taps still work

### Scenario 5: Copy is on-brand and accurate (P0, Riven + Vigil)
- **Given** the updated "What's New" copy
- **When** Vigil (compliance) and Riven review it
- **Then** it uses the CEO tone of voice, contains no em dashes or heavy emoji (per the 2026-08-07 no-AI-tells guidance), and is truthful and accurate (culture.md)

## Wireframe / visual description

No new layout. The existing "What's New" card/section keeps its present structure, styling, and position. Only the text content inside it changes:

- **Headline:** references v0.16.0 (exact wording set by Riven with Ember, following the CEO tone).
- **Summary:** one short, accurate line describing the v0.16.0 changes (Cinder quest polish + Play today), in plain punctuation, no em dashes, at most a single emoji where it genuinely fits.

Palette (brand) reviews only if Riven touches any visual styling; the expectation is text-only, so no palette change is expected.

## Open questions / ambiguities (need CEO input)

1. **Exact headline/summary wording (minor, optional):** Riven and Ember will propose the exact v0.16.0 text. If CEO prefers specific wording, confirm before the dev wave; otherwise ship the Ember/Riven wording within the requirements above.
2. **Link targets (confirm):** does the "What's New" section keep its existing Releases and Blog links (per Story 012), and should the headline link to the v0.16.0 release tag? Riven confirms against the live DOM; CEO confirm if a specific link behavior is preferred.
