# Test Plan: Story 109 FPS Decision Record, Docs Only (Session 46)

**Story:** `docs/stories/109-fps-decision-record-session46.md` (P2, rides along,
does not justify a cut).
**Owner:** Kai. **QA:** Scout. **PR:** #183, branch `kai/109-fps-decision-record-session46`.
**Artifact:** `docs/fps-input-decision-record-session46.md` (33 lines, only functional change).

## Scope
In scope: the one decision-record file under `docs/`. Out of scope:
`website/`, `dev/fps-probe/`, `src/`, `games/`, `scripts/`, `share/`,
probe code, harness runs, any version cut. Any changed line there fails the plan.
No harness output is required or accepted as proof for this story.

## Checks (each maps to an AC)

| # | AC | Check | Method | Expected |
|---|---|-------|--------|----------|
| 1 | AC-1 | Record file exists under `docs/`, only functional change | `git diff --name-only` vs base | Exactly `docs/fps-input-decision-record-session46.md` |
| 2 | AC-2 | Path A (physical gamepad, closes gate) and path B (keyboard-only shipped) each with a cost line | Read record | Both paths present, each with a `Cost:` line |
| 3 | AC-3 | 104 pointer-lock correction stated | Read record | Never proven, headless error on both browsers, no X on build box |
| 4 | AC-4 | Gamepad gate status stated | Read record | OPEN-BLOCKED-ON-HARDWARE, 16th session |
| 5 | AC-5 | Docs-only no-cut precedent stated | Read record | Sessions 38/40 precedent, no cut follows |
| 6 | AC-6 | Exactly one recommendation with one-line reason | grep `Recommendation: Path` | Count 1 (Path B), reason on the same line block |
| 7 | AC-7 | Zero changed lines under `website/` and `dev/fps-probe/` | `git diff --numstat` on those paths | Empty (added 0, deleted 0) |
| 8 | AC-8 | Zero changed lines under `src/`, `games/`, `scripts/`, `share/` | `git diff --numstat` on those paths | Empty (added 0, deleted 0) |
| 9 | AC-9 | Copy tone | grep for em dash | 0 em dashes, no heavy emoji |

## Result (Scout verification, 2026-10-30)
Doc assertions verified from disk against the PR head plus `git diff --numstat`
output. Pass/fail counts and pasted evidence in `flambeee-team/qa-results.md`.
