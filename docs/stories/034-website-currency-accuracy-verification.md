# Story 034 — Website Currency and Accuracy Verification (Session 19, P2)

**Status:** Ready for verification (Session 19, 2026-09-13). The session-plan planning pass found the website already current and accurate; this is a standing verification story, not a build.
**Author:** Quinn (Business Analyst), with Ember (Product) and Scout (QA).
**Priority:** P2 (brand surface accuracy, post-release; verify, do not build).
**Assigned to:** Verification is a shared QA exercise. Scout owns the executable checkbook; Riven (frontend, owns `share/Flambeee/index.html` and the repo mirror `website/index.html`) fixes anything the check finds off target. Kai peer-review only if a fix is needed.
**Tracked by:** Session 19 plan Priority 2 (confirm What's New reads the true latest release, v0.17.1, and that no copy drifted). CEO directive: "Website is a brand surface; keep current every session."

## Summary

The Flambeee home page (`share/Flambeee/index.html`, with an identical repo mirror at `website/index.html`) carries a What's New box and game links that must always tell the truth: the highlighted release is the true latest one, and the summary says only what that release actually shipped. This story is a **standing content-accuracy verification** procedure with BDD scenarios, so that after every session the QA pass confirms the brand surface is current and accurate. In the Session 19 planning pass the live site was verified current (What's New reads v0.17.1 with an accurate boss-day summary; live and mirror are byte-identical, `cmp` PASS), so this story is written as a passing verification with a lightweight fix path if regression is ever found. It does not change what any visitor sees; it proves what they see is true.

## Business value

- The What's New box is the single most visible claim on the brand surface. A stale or invented entry (as v0.15.0 was, fixed in Story 029) is a credibility defect for the whole project.
- A deterministic, repeatable check means currency and accuracy are proven every session instead of asserted, catching drift (new release not backfilled, an invented feature slipped into copy) before it ships.

## User Story

As the team,
I want to prove after every session that the website's What's New box names the true latest release and describes it accurately, and that the live site and repo mirror are in sync,
So that visitors never see stale or invented claims on the brand surface.

## Requirements

1. **Latest-version truth.** The What's New heading names the exact latest tagged release (currently v0.17.1). Any newer unreleased work is never described as shipped.
2. **Accurate summary.** The What's New summary describes only what that release actually shipped; no invented or upcoming features. For v0.17.1 the summary read: "Cinder's boss-day quest used to roll random fights ... boss days field boss-tier fights only, same biggest reward ... Old release notes also got their last em dashes scrubbed." (Verified in the planning pass.)
3. **Live and mirror in sync.** `share/Flambeee/index.html` (live, absolute path) and the repo mirror `website/index.html` are byte-identical (`cmp` PASS).
4. **Releases and Blog links work.** The What's New box links to the GitHub Releases page and the BLOG.md file, and both are real clickable links (Palette UX directive: links must be clickable, never bare text).
5. **Fix path, not a redesign.** If any check fails, the fix makes the copy/version true; no redesign, no layout change is in scope unless the accuracy fix requires it, and a failed check is treated as a defect with a small PR, not a silent rewrite.

### Out of scope

- Any website redesign, layout change, or new What's New features.
- Any game code change (Cinder, Wordfire, Minesweeper, Simon, 2048).
- Backfilling or rewriting release-note history beyond the accuracy fix.

## Acceptance Criteria (BDD)

### Scenario 1: What's New names the true latest release (P2, Scout)
- **Given** the current latest tagged release is the one the website should show
- **When** I read the What's New heading
- **Then** it names that exact release version, and no unreleased or newer version appears as shipped

### Scenario 2: Summary matches what shipped (P2, Scout + Vigil)
- **Given** the latest release's actual ship notes
- **When** I read the What's New summary
- **Then** it says only what that release shipped, with no invented or upcoming features, in the CEO tone (no em dashes, no heavy emoji)

### Scenario 3: Live and mirror are byte-identical (P2, Riven)
- **Given** the live site and the repo mirror
- **When** I run `cmp share/Flambeee/index.html flambeee/website/index.html`
- **Then** they match exactly (byte-identical), and the planning pass's observed `cmp PASS` holds

### Scenario 4: Releases and Blog links are real and clickable (P2, Palette + Scout)
- **Given** the What's New box on the live page
- **When** I inspect and click the Releases and Blog links
- **Then** both are real `<a href>` links that navigate to the GitHub Releases page and BLOG.md respectively, with no bare-text URLs

### Scenario 5: Failed accuracy check flags a defect (P2, Scout)
- **Given** a future session's verification finds the What's New stale or a summary that invents a feature
- **When** the QA check runs
- **Then** it records a defect with reproduction, and the fix lands as a small accuracy PR (base main) before the release is considered current

## Technical notes (Quinn)

- **Live site:** `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE path; `share/` is outside the repo). **Repo mirror:** `website/index.html` in this repo, kept byte-identical (verify with `cmp`). If a future What's New change ships, both copies must receive it and `cmp` must pass.
- **Source of truth for "latest release":** the latest GitHub tag/release (currently v0.17.1, 2026-09-11). The check compares the What's New heading and the actual latest tag, not what the copy claims.
- **Scope guard:** a What's New accuracy fix is a small, single-surface change. It never grows into a redesign, and it never touches game code. This story exists to make the standing check explicit and repeatable, not to add product scope.
- **No AI tells:** any copy touched by a future fix keeps plain punctuation, no em dashes, no heavy emoji.

## Visual Description (Quinn)

No visual change. This story verifies the existing What's New block, which renders as a full-width strip below the hero: a small flame "What's New" badge, a bold latest-version heading (currently "v0.17.1: Boss days finally have bosses"), a one-to-two-line summary in muted text, and Releases + Blog links on the right. On mobile the links wrap below the text; the current rendering is mobile-safe (verified in the planning pass). The verification confirms this exact block is true and in sync.

## Open questions

None blocking. The verification ran clean in the Session 19 planning pass (What's New reads v0.17.1 accurately, `cmp` PASS, links present). No CEO input required for this story; it codifies an already-correct state as a standing check.
