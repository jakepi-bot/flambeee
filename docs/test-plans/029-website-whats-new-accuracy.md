# Test Plan — Story 029 Website "What's New" Accuracy (P0)

**Author:** Scout (QA) | **Date:** 2026-09-11 | **Source:** `docs/stories/029-website-whats-new-accuracy.md`
**Testable code:** **YES** — static content check on `website/index.html` (single-file static site; no unit-test suite). Verifiable via content grep + `cmp` + optional Playwright render. No backend logic changes.

## Scope

Verify the "What's New" section on the website reflects v0.16.0 (not v0.15.0 or lower), with an accurate summary, and that the repo mirror `website/index.html` stays byte-identical to the live `share/Flambeee/index.html`.

## Test cases (mirror BDD scenarios 1–5)

| ID | BDD Scenario | Check | Expected |
|----|--------------|-------|----------|
| 029-T1 | S1 (headline) | `grep -n "v0.1" website/index.html` | What's New headline identifies **v0.16.0**, not v0.15.0/lower |
| 029-T2 | S2 (summary accuracy) | Read the `#whats-new` summary text; compare to roadmap v0.16.0 entry | Summary = Cinder quest polish ([Done] tail, gold counts combat gold) + Play today; NO features newer than v0.16.0 invented |
| 029-T3 | S3 (repo mirror) | `cmp flambeee/website/index.html share/Flambeee/index.html` | BYTE-IDENTICAL |
| 029-T4 | S4 (no layout/UX regression) | Playwright render desktop + 375px mobile; check no horizontal scroll, links reachable | No regression (only applicable if code changed) |
| 029-T5 | S5 (on-brand, no AI tells) | grep for em dash `—` and count emoji within What's New copy | No em dashes, ≤1 emoji, CEO tone, truthful |

## Test code / commands (ACTUAL)

- Content check (headline + summary): `grep -n "v0.1[56].0" website/index.html`
- v0.16.0 source-of-truth note: `docs/roadmap.md` line 9: `v0.16.0 — Cinder quest polish + website Play today (shipped 2026-09-08)`
- Mirror check: `cmp website/index.html share/Flambeee/index.html`
- Em-dash / emoji check within the What's New block.

## Result (filled at execution)

- **Status:** PENDING DEV WAVE — no implementation PR exists; file not yet updated.
