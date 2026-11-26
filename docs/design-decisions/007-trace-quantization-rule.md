# 007 - TRACE quantization rule: resample 2 px, floor, clamp, Session 73 (2026-11-26)

Date: 2026-11-26. Session: 73. Status: accepted. Story: 166. Design contract: flambeee-team/design-handoff.md, Section 1.2.

## Context

Two visually identical freehand strokes must forge identical walls or the daily seed is meaningless. Raw pointer events differ between browsers in count, spacing, and coalescing, so quantizing raw points directly would make the forge browser-dependent.

## Decision

Resample the polyline at fixed RESAMPLE_STEP_PX 2 px arc-length steps (linear interpolation, endpoints included), then map each point with floor(x / 36) and floor(y / 36), clamped to 0..8. Tie-break: boundary points fall to the higher-index cell; outer-edge points clamp to 8. Keyboard-painted cells skip resampling and enter the same cell-set pipeline. No timestamps, no velocity, no smoothing.

## Reason

Resampling erases event-timing differences while preserving loops and crossings at 36 px cells (2 px is 1/18 of a cell, far below any visible feature). Floor plus clamp is a total function, so determinism holds by construction and the Python harness can reimplement it byte for byte. Rejected: raw-point raster (browser-dependent), stroke-center sampling (drops hairpins), snap-to-nearest-center (ambiguous ties with no natural rule).

## What would change the decision

Harness evidence that 2 px resampling flakes the tie-break across browsers moves RESAMPLE_STEP_PX to 4 with the new number recorded in CONFIG. Any change to GRID or CELL_PX reopens this record. Decided by Rook, next NEW-GAME session at the earliest.
