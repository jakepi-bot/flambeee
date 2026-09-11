# Test Plan — Story 030 Brand Text Cleanup: No-AI-Tells Pass (P1)

**Author:** Scout (QA) | **Date:** 2026-09-11 | **Source:** `docs/stories/030-brand-text-cleanup-no-ai-tells.md`
**Testable code:** **YES** — static content check on `website/index.html` (title/About copy), `BLOG.md`, and any release-note copy. No unit-test suite; verifiable via character grep + emoji count + `cmp`. Text-only changes.

## Scope

Verify em dashes (`—` U+2014) are removed and heavy emoji reduced (≤1 genuine fit per passage) across external-facing brand text: `BLOG.md` (all posts), `website/index.html` title/About copy, and release notes. Preserve meaning/tone. Mirror stays byte-identical.

## Test cases (mirror BDD scenarios 1–6)

| ID | BDD Scenario | Check | Expected |
|----|--------------|-------|----------|
| 030-T1 | S1 (no em dashes) | `grep -c $'\u2014' website/index.html` | 0 outside permitted verbatim names |
| 030-T2 | S1 (BLOG) | `grep -c $'\u2014' BLOG.md` | 0 outside permitted verbatim names |
| 030-T3 | S2 (emoji reduced) | Count emoji in each edited external passage (grep unicode ranges) | ≤1 genuine fit per passage, decorative removed |
| 030-T4 | S3 (meaning preserved) | Manual before/after diff of edited passages | Meaning/tone/dry humor preserved; no content lost |
| 030-T5 | S4 (repo mirror) | `cmp website/index.html share/Flambeee/index.html` | BYTE-IDENTICAL |
| 030-T6 | S6 (no regression) | Playwright render desktop + mobile | No broken layout, links/taps work |

## Test code / commands (ACTUAL)

- `grep -c $'\u2014' website/index.html`
- `grep -c $'\u2014' BLOG.md`
- Emoji count (rough unicode scan): `grep -oP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{FE0F}]' <file> | wc -l`
- Mirror: `cmp website/index.html share/Flambeee/index.html`

## Result (filled at execution)

- **Status:** PENDING DEV WAVE — no implementation PR exists; files not yet cleaned.
