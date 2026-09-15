# Story 036: Website Latest-Release Currency and Mirror Byte-Identity Verification (Session 20, P2)

**Status:** Ready for verification (Session 20, first half, 2026-09-15).
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (brand surface accuracy, post-release; verify, do not build).
**Assigned to:** Verification is a shared exercise. Scout owns the executable check (adapt prior website checks). Riven (frontend, owns `share/Flambeee/index.html` and the repo mirror `website/index.html`) fixes anything off target. Kai peer-review only if a fix is needed.
**Tracked by:** Session 20 plan Priority 2 (confirm the live site's What's New names the true latest release, v0.18.0, and that live + mirror are byte-identical). CEO directive: "Website is a brand surface; keep current every session."

## Summary

The Flambeee home page (`share/Flambeee/index.html` absolute path, with a byte-identical repo mirror at `website/index.html`) carries a What's New box that must always name the true latest release and describe it accurately. This is a **standing verification**, not a build. The session-plan planning pass and this requirements pass confirmed the site is already current:

- The true latest release is **v0.18.0** (2026-09-13, "Cinder daily-return preview + website accuracy"), tagged on origin at `b9a6fc6`.
- The What's New heading reads exactly: **"v0.18.0: Cinder tells you to come back tomorrow"**, with a summary that says only what v0.18.0 actually shipped (Story 033's tomorrow preview; same quests, same rewards, no new mechanics).
- Live and mirror are byte-identical (`cmp` PASS; `website/index.html` is 43383 bytes, md5 equal to the live file).

A deterministic, repeatable check means currency and accuracy are proven every session instead of asserted. This story codifies that standing check for v0.18.0 and the mirror pair. Verification only; no fix path unless a mismatch surfaces.

## Business value

- The What's New box is the single most visible claim on the brand surface. A stale or invented entry (as v0.15.0 was in Story 029) is a credibility defect.
- A repeatable check catches drift: a new release not backfilled, or invented feature copy slipping in, is flagged the same session.

## User Story

As the team,
I want to prove after every session that the website's What's New box names the true latest release and describes it accurately, and that the live site and repo mirror are in sync,
So that visitors never see stale or invented claims on the brand surface.

## Requirements

1. **Latest-version truth.** The What's New heading names the exact latest tagged release, **v0.18.0** (2026-09-13). Any newer unreleased work is never described as shipped. The local tag list can be stale if not fetched; the source of truth is the latest tag on `origin` (`git ls-remote --tags origin`), which currently reads `v0.18.0` at commit `b9a6fc6`.
2. **Accurate summary.** The What's New summary describes only what v0.18.0 shipped. Verified copy: "Cinder's daily quest is a loop, but a player who finished today saw nothing that said so. Now when you complete and collect today's quest, the view names tomorrow's objective and tells you to come back after midnight to start it. Same quests, same rewards, no new mechanics. Today's quest always shows tomorrow's preview; every visitor sees the same one that day." No invented or upcoming features.
3. **Live and mirror in sync.** `share/Flambeee/index.html` (live, absolute path) and `website/index.html` (repo mirror) are byte-identical (`cmp` PASS).
4. **Releases and Blog links work.** The What's New box links to the GitHub Releases page and the BLOG.md file; both are real clickable `<a href>` links, never bare text (Palette UX directive: links must be clickable).
5. **Fix path, not a redesign.** If any check fails, the fix makes the copy/version true; no redesign or layout change is in scope. A failed check is a small accuracy PR (base main), not a silent rewrite.

### Out of scope

- Any website redesign, layout change, or new What's New feature.
- Any game code change (Cinder, Wordfire, Minesweeper, Simon, 2048).
- Backfilling or rewriting release-note history beyond an accuracy fix.

## Acceptance Criteria (BDD)

### Scenario 1: What's New names the true latest release (P2, Scout)
- **Given** the current latest tagged release on origin is v0.18.0
- **When** I read the What's New heading
- **Then** it names exactly "v0.18.0" and no unreleased or newer version appears as shipped (checked against `git ls-remote --tags origin`, not the local tag list)

### Scenario 2: Summary matches what shipped (P2, Scout + Vigil)
- **Given** the v0.18.0 ship notes (Story 033)
- **When** I read the What's New summary
- **Then** it says only what v0.18.0 shipped, with no invented or upcoming features, in the CEO tone (no em dashes, no heavy emoji)

### Scenario 3: Live and mirror are byte-identical (P2, Riven + Scout)
- **Given** the live site and the repo mirror
- **When** I run `cmp /home/jake/.openclaw/workspace/share/Flambeee/index.html /home/jake/.openclaw/workspace/flambeee/website/index.html`
- **Then** they match exactly (byte-identical), and this session's observed `cmp PASS` holds

### Scenario 4: Releases and Blog links are real and clickable (P2, Palette + Scout)
- **Given** the What's New box on the live page
- **When** I inspect and click the Releases and Blog links
- **Then** both are real `<a href>` links that navigate to the GitHub Releases page and BLOG.md respectively, with no bare-text URLs

### Scenario 5: Failed accuracy check flags a defect (P2, Scout)
- **Given** a future session's verification finds the What's New stale or a summary that invents a feature
- **When** the check runs
- **Then** it records a defect with reproduction, and the fix lands as a small accuracy PR (base main) before the release is considered current

## Technical notes (Quinn)

- **Live site:** `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE path; `share/` is outside the repo). **Repo mirror:** `website/index.html` in this repo, kept byte-identical (verify with `cmp`). If a future What's New change ships, both copies must receive it and `cmp` must pass.
- **Source of truth for "latest release":** the latest tag on `origin` via `git ls-remote --tags origin`, currently `v0.18.0` at `b9a6fc6` (annotated). Do not rely on the local fetch; local tags can lag. The web page must be checked against the remote latest, not what the copy claims.
- **Scope guard:** an accuracy fix is a single-surface copy/version change. It never grows into a redesign and never touches game code.
- **No AI tells:** any copy touched by a future fix keeps plain punctuation, no em dashes, no heavy emoji.

## Visual Description (Quinn)

No visual change. The What's New block renders as a full-width strip below the hero: a small flame "What's new" badge, a bold latest-version heading ("v0.18.0: Cinder tells you to come back tomorrow"), a two-line summary in muted text, and Releases + Blog links on the right. On mobile the links wrap below the text. The verification confirms this exact block is true and in sync.

## Open questions

None blocking. The verification ran clean in this planning/requirements pass (What's New reads v0.18.0 accurately against the origin tag, `cmp` PASS, links present). No CEO input required; this story codifies an already-correct state as a standing check.
