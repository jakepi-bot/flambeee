# 008 - TRACE traversal input: pad plus keys, never finger-drag, Session 73 (2026-11-26)

Date: 2026-11-26. Session: 73. Status: accepted. Stories: 166, 169. Design contract: flambeee-team/design-handoff.md, Section 1.1.

## Context

Backlog 001 asks whether traversal is keyboard-only or the same finger dragging again. DRAW already owns the finger on a single screen with no mode chrome to spare.

## Decision

RUN moves one cell per press via arrows or WASD plus the house 4-dir on-screen pad. The drawing finger never steers. DRAW keeps pointer input primary with an arrow-key paint cursor (one cell per press from the skeleton anchor, Enter finishes, Esc clears) as the parity path.

## Reason

Reusing the drag for walking needs a speed or direction model, and any speed model is momentum, which the originality constraint forbids. Discrete steps match the house vocabulary, are exactly testable per press (one press, at most one cell, wall bumps silent), and keep DRAW and RUN unmistakably separate. The drag path stays scroll-safe under `touch-action: none` with single-pointer tracking.

## What would change the decision

Playtest evidence that pad walking feels broken on phones reopens a tap-to-step cell path (still discrete, still one cell per tap), never a drag. Decided by Rook, next NEW-GAME session at the earliest.
