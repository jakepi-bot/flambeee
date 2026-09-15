# Test Plan 036: Website Latest-Release Currency and Mirror Byte-Identity

Story: `docs/stories/036-website-currency-verification.md` (P2)
QA: Scout. Written 2026-09-15 (Session 20).
Scope: standing verification, no build. Verify only; a mismatch is reported as a defect for a small accuracy PR, never a redesign.

## Files under test

- Live site: `/home/jake/.openclaw/workspace/share/Flambeee/index.html` (ABSOLUTE path, outside repo).
- Repo mirror: `/home/jake/.openclaw/workspace/flambeee/website/index.html`.
- Source of truth for latest release: `git ls-remote --tags origin` (`origin` remote of the flambeee repo). NOT the local tag list (local can lag).

---

## Scenario 1 (P2): What's New names the true latest release

**Given** the current latest tagged release on origin.
**When** I read the What's New heading.
**Then** it names exactly "v0.18.0" and no unreleased or newer version appears as shipped.

### 1.1 Origin is source of truth
- Run `git ls-remote --tags origin` in `/home/jake/.openclaw/workspace/flambeee`.
- Determine the highest semver tag on origin. ASSERT: the max tag = `v0.18.0` (annotated at `b9a6fc6`).
- Note: do not rely on local `git tag` (may lag at v0.17.1).

### 1.2 Heading matches
- Grep the live `index.html` for the What's New `h3`. ASSERT: it reads exactly `v0.18.0: Cinder tells you to come back tomorrow`.
- ASSERT: no other version appears as the latest / shipped in the What's New block.

### 1.3 Negative: no invented version
- Assert the What's New heading does NOT name any version newer than `v0.18.0` as shipped (no forward-looking/unreleased claims).

---

## Scenario 2 (P2): Summary matches what shipped

**Given** the v0.18.0 ship notes (Story 033).
**When** I read the What's New summary.
**Then** it says only what v0.18.0 shipped, with no invented or upcoming features, in the CEO tone (no em dashes, no heavy emoji).

### 2.1 Accuracy
- Compare the summary paragraph against the v0.18.0 scope: "Cinder daily-return preview + website accuracy" (Story 033's tomorrow preview).
- ASSERT: summary names only the tomorrow preview; no balance/reward/mechanic changes, no invented features, no roadmap promises.

### 2.2 Tone / no-AI-tells
- Scan the summary for `—` (em dash) and heavy emoji. ASSERT: none.

### 2.3 Negative: invented feature
- If the summary claims a feature not in v0.18.0 (e.g. a new mechanic, leaderboard, or future release), report as an accuracy defect (severity High, credibility issue).

---

## Scenario 3 (P2): Live and mirror are byte-identical

**Given** the live site and the repo mirror.
**When** I run `cmp`.
**Then** they match exactly.

### 3.1 cmp
- `cmp /home/jake/.openclaw/workspace/share/Flambeee/index.html /home/jake/.openclaw/workspace/flambeee/website/index.html`
- ASSERT: exit 0, "CMP PASS". Expected 43383 bytes each.
- Confirm identical `md5sum` on both.

### 3.2 Negative: drift detection
- If `cmp` fails, report byte-identity FAIL with byte offset; the fix is a single-surface copy sync (accuracy PR base main), not a redesign.

---

## Scenario 4 (P2): Releases and Blog links are real and clickable

**Given** the What's New box on the live page.
**When** I inspect and click the Releases and Blog links.
**Then** both are real `<a href>` links navigating to the GitHub Releases page and BLOG.md, with no bare-text URLs.

### 4.1 Link presence (Palette UX directive)
- Grep the live index What's New `wn-links` block for `<a href`.
- ASSERT:
  - Releases: href = `https://github.com/jakepi-bot/flambeee/releases`, `target="_blank"` + `rel="noopener"`.
  - Blog: href = `https://github.com/jakepi-bot/flambeee/blob/main/BLOG.md`, `target="_blank"` + `rel="noopener"`.
- ASSERT: both are real clickable `<a href>` elements, never bare plain-text URLs.

### 4.2 Click-through (browser)
- In Playwright, click Releases -> resolves to the GitHub releases URL; click Blog -> resolves to the BLOG.md URL. ASSERT correct navigation (no 404).

### 4.3 Negative: bare URL
- If any intended link is plain text (no `<a href>`), report as a defect per Palette directive.

---

## Scenario 5 (P2): Failed accuracy check flags a defect

**Given** a future verification finds the What's New stale or a summary that invents a feature.
**When** the check runs.
**Then** it records a defect with reproduction, and the fix lands as a small accuracy PR (base main) before the release is considered current.

### 5.1 Defect record
- If any Scenario 1-4 check fails, log a structured defect: severity, reproduction steps, expected vs actual, environment.
- ASSERT: the defect is recorded and routed to Riven (fix) + Kai (peer review), fix is a small accuracy PR base main.

### 5.2 Scope guard
- ASSERT the fix does NOT grow into a redesign or touch game code.

---

## Pass/fail summary format

Per scenario: PASS / FAIL / N/A (with reason). Overall PASS for 036 = all Scenarios 1-4 green. Any FAIL = accuracy defect for a small PR.
