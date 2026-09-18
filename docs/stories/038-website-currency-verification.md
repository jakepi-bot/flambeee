# Story 038: Website Latest-Release Currency and Mirror Byte-Identity Verification (Session 21, P2)

**Status:** Ready for verification (Session 21, first half, 2026-09-18).
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (brand surface accuracy, post-release; verify, do not build).
**Assigned to:** Verification is a shared exercise. Scout owns the executable check (adapt the Story 034/036 website checks). **Riven** (frontend, owns `share/Flambeee/index.html` and the repo mirror `website/index.html`) fixes anything off target. Kai peer-reviews only if a fix is needed.
**Tracked by:** Session 21 plan Priority 2 (confirm the live site's What's New names the true latest release and that live + mirror are byte-identical). CEO directive: "Website is a brand surface; keep current every session." Reuses the Story 034/036 procedure.

## Summary

The Flambeee home page (`share/Flambeee/index.html`, ABSOLUTE path, with a byte-identical repo mirror at `website/index.html`) carries a What's New box that must always name the true latest release and describe it accurately.

This is a **standing verification**, not a build. The session-plan planning pass and this requirements pass confirmed the site is already correct:

- The true latest release on origin is **v0.18.1** (2026-09-15, "Cinder quest log + quest streak"). Confirmed against `git ls-remote --tags origin`, not the local tag list.
- The What's New heading reads exactly: **"v0.18.1: Cinder keeps a quest log and your streak"**, with a summary that says only what v0.18.1 shipped (the Quest Log, recent completed quests, current consecutive-day streak, no new mechanics, no balance or reward changes, history starts when it ships).
- Live and mirror are byte-identical (`cmp` PASS; `share/Flambeee/index.html` and `website/index.html` are both 1320 lines).
- Releases and Blog links are real clickable `<a href>` links to the GitHub Releases page and BLOG.md.

A deterministic, repeatable check means currency and accuracy are proven every session instead of asserted. This story codifies that standing check for v0.18.1 and the mirror pair. Verification only; no fix path unless a mismatch surfaces.

## Business value

- The What's New box is the single most visible claim on the brand surface. A stale or invented entry (as v0.15.0 was in Story 029) is a credibility defect.
- A repeatable check catches drift the same session it appears: a new release not backfilled, or invented feature copy slipping in.
- Cheap insurance: the check is fast, and it keeps the release note, the website, and the repo mirror telling the same story.

## User Story

As the team,
I want to prove after every session that the website's What's New box names the true latest release and describes it accurately, and that the live site and the repo mirror are in sync,
So that visitors never see stale or invented claims on the brand surface.

## Requirements

1. **Latest-version truth.** The What's New heading names the exact latest tagged release, currently **v0.18.1** (2026-09-15). Any newer unreleased work is never described as shipped. The local tag list can be stale if not fetched; the source of truth is the latest tag on `origin` via `git ls-remote --tags origin`, which currently reads `v0.18.1`.
2. **Accurate summary.** The What's New summary describes only what v0.18.1 shipped: the Quest Log reachable from the town hub, the recent completed quests (most recent first, capped at the most recent entries), and the current consecutive-day streak. It states that it is a record of what the player already did, with no new mechanics and no balance or reward changes, and that the history starts the day it ships. No invented or upcoming features.
3. **Live and mirror in sync.** `share/Flambeee/index.html` (live, ABSOLUTE path) and `website/index.html` (repo mirror) are byte-identical (`cmp` PASS). Both were 1320 lines at verification time this session.
4. **Releases and Blog links work.** The What's New box links to the GitHub Releases page and BLOG.md; both are real clickable `<a href>` links with `target="_blank" rel="noopener"`, never bare text (Palette UX directive: links must be clickable).
5. **Fix path, not a redesign.** If any check fails, the fix makes the copy or the version true; no redesign or layout change is in scope. A failed check is a small accuracy PR (base main), not a silent rewrite.

### Out of scope

- Any website redesign, layout change, or new What's New feature.
- Any game code change (Cinder, Wordfire, Minesweeper, Simon, 2048).
- Backfilling or rewriting release-note history beyond an accuracy fix.
- Any change to the deploy pipeline or the service worker cache version.

## Acceptance Criteria (BDD)

### Scenario 1: What's New names the true latest release (P2, Scout)
- **Given** the current latest tagged release on origin is v0.18.1
- **When** I read the What's New heading on the live page
- **Then** it names exactly "v0.18.1" and no unreleased or newer version appears as shipped, checked against `git ls-remote --tags origin` and not the local tag list

### Scenario 2: Summary matches what shipped (P2, Scout + Vigil)
- **Given** the v0.18.1 ship notes (Story 035: Quest Log, recent completed quests, current streak, read-only, no new mechanics)
- **When** I read the What's New summary
- **Then** it says only what v0.18.1 shipped, with no invented or upcoming features, in the CEO tone (no em dashes, no heavy emoji)

### Scenario 3: Live and mirror are byte-identical (P2, Riven + Scout)
- **Given** the live site and the repo mirror
- **When** I run `cmp /home/jake/.openclaw/workspace/share/Flambeee/index.html /home/jake/.openclaw/workspace/flambeee/website/index.html`
- **Then** they match exactly (byte-identical, exit 0) and this session's observed `cmp PASS` holds

### Scenario 4: Releases and Blog links are real and clickable (P2, Palette + Scout)
- **Given** the What's New box on the live page
- **When** I inspect and click the Releases and Blog links
- **Then** both are real `<a href>` links that navigate to the GitHub Releases page and BLOG.md respectively, with no bare-text URLs

### Scenario 5: Failed accuracy check flags a defect (P2, Scout)
- **Given** a future session's verification finds the What's New stale, or a summary that invents a feature, or a mirror mismatch
- **When** the check runs
- **Then** it records a defect with reproduction steps, and the fix lands as a small accuracy PR (base main) before the release is considered current

### Scenario 6: No regressions from a fix (P2, Scout)
- **Given** an accuracy fix was required and applied
- **When** the fix lands
- **Then** the live file and the repo mirror are re-synced and `cmp` passes, the Releases and Blog links still work, and no layout or content beyond the corrected What's New text changed

## Technical notes (Quinn)

- **Live site:** `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE path; `share/` is outside the repo). **Repo mirror:** `website/index.html` in this repo, kept byte-identical (verify with `cmp`). If a What's New change ships, both copies receive it and `cmp` must pass.
- **Source of truth for "latest release":** the latest tag on `origin` via `git ls-remote --tags origin`. Do not rely on the local fetch; local tags can lag. At verification time this session the local list stopped at v0.9.0 while origin carried v0.18.1, which is exactly the drift this check is designed to catch.
- **Baseline observed this session (planning + requirements pass):** heading reads `v0.18.1: Cinder keeps a quest log and your streak`; summary describes the Quest Log and streak only; `cmp` PASS on the mirror pair (both 1320 lines); Releases and Blog links present as real anchors. No defect found.
- **Scope guard:** an accuracy fix is a single-surface copy/version change. It never grows into a redesign and never touches game code.
- **No AI tells:** any copy touched by a future fix keeps plain punctuation, no em dashes, no heavy emoji.
- **Verification output:** Scout's check should print the origin latest tag, the heading text found, the `cmp` exit code, and the two link hrefs, so the pass or fail is auditable without opening the file.

## Visual Description (Quinn)

No visual change. The What's New block renders as a full-width strip below the hero: a small flame "What's new" badge on the left, then a bold latest-version heading ("v0.18.1: Cinder keeps a quest log and your streak"), a two-line summary in muted text, and Releases + Blog links on the right. On mobile the links wrap below the text. The verification confirms this exact block is true and in sync; it does not change how it looks.

## Open questions

None blocking. The verification ran clean in this planning/requirements pass (What's New reads v0.18.1 accurately against the origin tag, `cmp` PASS, both links present). No CEO input required; this story codifies an already-correct state as a standing check.
