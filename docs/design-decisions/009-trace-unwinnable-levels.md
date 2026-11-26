# 009 - TRACE unwinnable levels: carve plus stitch, never blame the player, Session 73 (2026-11-26)

Date: 2026-11-26. Session: 73. Status: accepted. Stories: 166, 167. Design contract: flambeee-team/design-handoff.md, Sections 1.2 and 2.1.

## Context

A freehand stroke can cover the start, cover the exit, or wall the exit off entirely. Any of these would produce an unwinnable level through no fault the player can see, which breaks the forgiveness-first requirement.

## Decision

There is no unwinnable-level state. FORGE carves START and EXIT to floor unconditionally, then BFS-checks reachability and silently carves a shortest row-first L corridor if the exit is unreached. FORGE to RUN is therefore unconditional. No message explains the stitch; the end sentence reports coverage of the player's own ink only (skeleton and stitch cells never enter the denominator).

## Reason

A redraw-required failure state would punish expressive lines and need its own copy, states, and harness legs in a one-wave build. The stitch touches at most 12 interior cells, preserves every ink cell the player drew, and keeps the BFS proof trivial (200/200 within 80 moves). Carving the endpoints first handles the common seal case without invoking the corridor at all.

## What would change the decision

Telemetry or QA showing players notice and dislike the corridor (straight hallway through dense ink on most days) reopens a visible-stitch variant that renders corridor cells distinctly. Frequency first: if the stitch fires on fewer than 5 percent of proof-suite forges, invisibility stands. Decided by Rook, next NEW-GAME session at the earliest.
