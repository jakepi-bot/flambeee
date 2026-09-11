# Story 030 — Brand Text Cleanup: No-AI-Tells Pass (Session 18, P1)

**Status:** Approved for dev wave (Session 18). Priority P1 — a real, verifiable polish item carried from prior QA; non-blocking but low-risk and worth closing.
**Author:** Quinn (Business Analyst), with Ember (Product) and Vigil (Compliance, info-note source)
**Priority:** P1
**Assigned to:** Riven (website copy) + optionally Kai for any release-note copy. Compliance (Vigil) verifies in the QA wave. Ember owns BLOG.md and release-note copy tone. Palette (brand) light-touch review if any visual styling changes (expected copy-only). Scout QA.
**Tracked by:** Session 18 plan, Priority 2. Vigil info-note cleanup: older BLOG.md posts and the website title/About still carry em dashes and heavier emoji from before the 2026-08-07 no-AI-tells guidance.

## Summary

The CEO's 2026-08-07 guidance established that external-facing communication must avoid the "AI tells": heavy emoji use and em dashes (—). Use plain punctuation, at most a single emoji where it genuinely fits, no em-dash flourishes. Content published before that guidance still carries those tells. This story is a cleanup pass over the external-facing brand text so it complies with the current guidance:

- **BLOG.md** — older posts (plus any new posts) still containing em dashes and heavy emoji.
- **Website `index.html` title/About copy** — any em dashes / heavy emoji in the site's title and About text.
- **Release notes** — any that carry em dashes or heavy emoji.

This is a copy edit pass. It changes text, not structure or behavior. Keep the CEO tone: direct, technically precise, no filler, dry humor carried by content, not typographic garnish.

## Business value

- Brings all external-facing brand text in line with CEO guidance (culture.md, 2026-08-07) — a consistent, human, trustworthy brand voice across blog, site, and release notes.
- Real, verifiable polish item that is safe to close this session (no scope creep into new features).
- Low risk: text-only, no functional change.

## User Story

As a visitor to flambeee.com, the blog, and the release notes,
I want external-facing copy that reads like a person — plain punctuation, minimal emoji, no em dashes,
So that the brand voice is consistent and doesn't carry obvious AI tells.

## Requirements

1. **Em dashes removed.** Replace em dashes (—) in external-facing copy (BLOG.md, website title/About, release notes) with plain punctuation (commas, periods, or reworded phrasing) per CEO tone. (Keep content meaning and dryness; do not rewrite for style beyond removing the tells.)
2. **Heavy emoji reduced.** Reduce heavy emoji use to at most a single emoji where it genuinely fits; remove decorative emoji flourishes.
3. **Scope the pass to external-facing text.** BLOG.md, `share/Flambeee/index.html` (title/About and any other external-facing copy), `website/index.html` (byte-identical mirror), and any release-note copy. Internal docs/stories are not the target unless they appear externally.
4. **Preserve meaning and structure.** No content loss, no layout change, no structural change. Copy edit only.
5. **Repo mirror in sync.** If `share/Flambeee/index.html` copy changes, mirror to `website/index.html` (byte-identical; `cmp`).

### Out of scope

- Any new feature, game, layout change, or redesign.
- Rewriting copy for style beyond removing the AI tells (em dash + heavy emoji) — keep existing meaning, voice, and dry humor.
- Changing product behavior or gameplay.

## Acceptance Criteria (BDD)

### Scenario 1: No em dashes in external copy (P1, Riven + Kai + Ember)
- **Given** I scan BLOG.md, the website title/About copy, and release notes
- **When** I check for the em dash character (—)
- **Then** none appear in the edited external-facing text (any remaining are only where an exact quoted title/name requires it and is unavoidable)

### Scenario 2: Emoji reduced to at most one genuine fit (P1, Riven + Ember)
- **Given** I review each edited external-facing passage
- **When** I count emoji
- **Then** each passage uses at most a single emoji and only where it genuinely fits the content (heavy/decorative emoji removed)

### Scenario 3: Meaning and tone preserved (P1, all)
- **Given** the cleanup edits
- **When** I compare before/after copy
- **Then** the meaning, technical precision, dryness, and CEO tone are preserved (no content lost, no rewriting that changes substance)

### Scenario 4: Website mirror stays byte-identical (P1, Riven)
- **Given** website copy is edited in `share/Flambeee/index.html`
- **When** I run `cmp` on it and `website/index.html`
- **Then** the two files are byte-identical (standing deployment rule)

### Scenario 5: Compliance verifies (P1, Vigil)
- **Given** the cleanup pass is complete
- **When** Vigil (compliance) reviews the edited external-facing text and posts against culture.md (2026-08-07 guidance) and CEO tone
- **Then** the edited copy is compliant (Vigil APPROVE)

### Scenario 6: No functional/layout regression (P1, Riven + Scout)
- **Given** the copy edits
- **When** the website renders on desktop and a narrow mobile viewport
- **Then** the site displays correctly with no broken layout and all existing links/taps still work

## Wireframe / visual description

Text-only cleanup. No layout or visual change. Em dashes become plain punctuation (commas/periods/reworded), decorative emoji removed, at most one genuine emoji retained. The website title and About text keep their existing position and styling, just with cleaner, on-tone copy. Palette (brand) light-touch review only if Riven changes any styling (not expected).

## Open questions / ambiguities (need CEO input)

1. **Release-notes scope (confirm):** which release notes, if any, should carry the cleanup? The guidance targets external-facing communication. Riven/Ember confirm against the repo; CEO confirm if release-note cleanup should be included or deferred (they are git history, so editing retroactive release notes is optional).
2. **BLOG.md depth (confirm):** how far back should the pass go on older BLOG.md posts? The Vigil note flags "older" posts. Ember proposes the cutoff (e.g. all posts, or only posts published after a set date); CEO confirm if a specific cutoff is preferred.
3. **Acceptable remaining em dashes (clarify):** are em dashes permitted inside verbatim quoted titles/names (e.g. a quoted product name that contains one), or must every occurrence be reworded? Default: reword unless it's a verbatim name that cannot change.
