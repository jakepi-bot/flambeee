# Story 012 — Website: What's New Section

**Status:** Ready for development (v0.8.0)
**Author:** Ember (PM) + Quinn (BA)
**Priority:** Medium

## Why

The website (https://flambeee.com, source in `share/Flambeee/index.html`) is a brand surface and a standing focus of weekly work (CEO guidance 2026-08-14). It currently lists the four games but gives visitors no signal that the company ships regularly. A "What's New" section that names the latest release and links to the blog/releases turns the home page into a living product surface instead of a static card grid, and rewards repeat visits.

## User story

As a visitor to flambeee.com,
I want to see what the company shipped recently,
So that I know the games are actively maintained and can read about new releases.

## Acceptance criteria (BDD scenarios)

### Scenario 1: Latest release is shown
Given the site is loaded,
When I scroll to the What's New section,
Then I see the latest release version and a one-line description.

### Scenario 2: Release links are clickable
Given the What's New section is visible,
When I click the release link,
Then it opens the GitHub release page for that version in a new tab.

### Scenario 3: Blog link is present
Given the What's New section is visible,
When I look for the blog,
Then there is a link to the Flambeee blog (BLOG.md) that opens in a new tab.

### Scenario 4: On-brand styling
Given the What's New section is rendered,
When I compare it to the rest of the page,
Then it uses the same brand palette, typography, and card styling as the rest of the site.

### Scenario 5: Accurate and current
Given the latest release is v0.8.0,
When I read the What's New section,
Then it says v0.8.0 (not an older version), and every claim in it is true.

## Notes for developers

- Source of truth: `share/Flambeee/index.html` (Jake deploys this to the VPS with Caddy).
- Keep the section compact: one card between the Games grid and the Why section, or a small strip under the hero. Ember + Palette decide placement.
- The section must be updated every session when a release ships (part of the release checklist).
- No PII, no AI tells, CEO tone, plain punctuation.
