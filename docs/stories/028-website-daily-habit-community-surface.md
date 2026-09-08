# Story 028 — Website: Daily-Habit / Community Surface (Session 17, v0.16.0)

**Status:** Candidate — scope to be confirmed in the dev wave (Session 17, v0.16.0)
**Author:** Quinn (Business Analyst), with Ember (Product)
**Priority:** P1 (candidate; confirm scope in dev wave)
**Assigned to:** Riven (frontend: website surface). Palette (brand check) per the standing brand-surface directive. Kai peer review. QA by Scout (real click + narrow mobile viewport check).
**Tracked by:** Session 17 plan Priority 2. The website is a standing brand surface (CEO 2026-08-14). Game of the Week shipped in v0.15.0 (Story 026); this adds a small retention/community surface that reinforces the daily-habit loop. Only if it adds real value without scope creep; the dev wave confirms final scope.

## Summary

flambeee.com is the product's home page and a standing brand surface. v0.15.0 added a Game of the Week banner. This candidate story adds a small, on-brand retention/community surface that reinforces the daily-habit loop the product now has (Wordfire's daily word + streak, Cinder's daily quest). The exact form is confirmed in the dev wave, but the candidate directions are:

- A **"Play today" / daily-habit callout** that points players at the day's daily content (e.g. "Today's Cinder quest is live" or "Solve today's Wordfire"), reinforcing the reason to return each day.
- A **community/feedback link** (e.g. a "Join the community" or "Report a bug / request a feature" link to the GitHub repo), turning the site into a two-way surface.

The scope is deliberately small and additive: no new game, no service-worker change, no redesign, no layout break on mobile. It must add real value without scope creep; if the dev wave judges it doesn't, the story is dropped and only Story 027 ships.

## Business value

- Reinforces the daily-habit loop (the product's strongest retention signal) directly on the home page, where returning players land.
- Turns the site into a two-way community surface, consistent with the open-source, community-driven mission.
- Small, safe, on-brand addition that keeps the newest retention features discoverable.

## User Story

As a returning visitor to flambeee.com,
I want to see a small, on-brand callout that points me at today's daily content and/or how to reach the community,
So that I have a concrete reason to return each day and a clear path to give feedback.

## Requirements (candidate — confirm scope in dev wave)

1. **Small, on-brand surface on flambeee.com.** A compact callout (e.g. a "Play today" strip or a community/feedback link) that reinforces the daily-habit loop. Uses the existing brand palette (navy `#1a1a2e`, flame `#e94560`), no layout break, mobile-safe.
2. **Reinforces the daily habit.** If a daily-habit callout: points at the day's daily content (Cinder's daily quest and/or Wordfire's daily word) with a relative play link. If a community link: a real, clickable link to the GitHub repo (issues/feedback).
3. **Graceful degrade.** If the referenced content or link is missing/invalid, the surface hides or degrades gracefully with no unhandled error and no broken layout.
4. **No scope creep.** No new game, no service-worker change, no redesign, no new page. Strictly additive to the existing `share/Flambeee/index.html` (the live source of truth) and its repo mirror `website/index.html` (must stay byte-identical; verify `cmp`).

### Out of scope

- Any new game, leaderboard, account system, or backend.
- Any change to the Game of the Week banner (Story 026) beyond coexistence.
- Any redesign or layout overhaul of the site.

## Acceptance Criteria (BDD)

### Scenario 1: Daily-habit/community surface renders on the site (P1, Riven)
- **Given** I visit flambeee.com
- **When** the page loads
- **Then** a small, on-brand callout (daily-habit and/or community link, per confirmed scope) is visible and does not break the existing layout

### Scenario 2: Surface points at real, working content (P1, Riven)
- **Given** the callout is a daily-habit strip
- **When** I tap/click it
- **Then** it links to the day's daily content (Cinder daily quest and/or Wordfire daily word) via a relative play link that loads the game with readable same-origin stats

### Scenario 3: Community link is a real clickable link (P1, Riven)
- **Given** the callout includes a community/feedback link
- **When** I tap/click it
- **Then** it opens the GitHub repo (issues/feedback) in a new context, and is a real anchor link (not a fake button)

### Scenario 4: Mobile renders with no layout break (P1, Riven)
- **Given** I view the site on a narrow mobile viewport
- **When** the callout is present
- **Then** it stacks full-width with no horizontal scroll and remains tappable

### Scenario 5: Missing/invalid content degrades gracefully (P1, Riven)
- **Given** the referenced daily content or community link is missing/invalid
- **When** the page loads
- **Then** the callout hides or degrades gracefully with no unhandled error and no broken layout

### Scenario 6: On-brand visuals (P1, Riven + Palette)
- **Given** the callout is rendered
- **When** I inspect its styling
- **Then** it uses the brand palette (navy `#1a1a2e`, flame `#e94560`) and matches the site's visual identity (Palette confirms)

## Open questions / ambiguities (need CEO input)

1. **Scope confirmation (required):** Which form does the dev wave confirm — a daily-habit "Play today" callout, a community/feedback link, or both? The story is a candidate; the dev wave decides final scope, and if it adds no real value the story is dropped.
2. **Placement:** Where on the page does the callout sit (e.g. near the Game of the Week banner, in the footer, or in the nav)? Riven confirms against the live DOM; CEO confirm if a specific look is preferred.
3. **Daily content source:** If a daily-habit callout, how does it determine "today's" content (e.g. reuse the deterministic UTC-day logic from Cinder/Wordfire)? Riven confirms the mechanism; no server/state.
