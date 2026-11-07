# 002 - GOTW rotation ruling, Session 54 (2026-11-07)

Date: 2026-11-07. Session: 54 (LEGACY day). Issue: #214. Status: accepted.
Story: 125. Design contract: flambeee-team/design-handoff.md, Section 2.

## Context

Echo Rounds and Typewreck are shipped and precached but hold no Game of the Week slot. Issue #214 permits two outcomes: admit them to GAME_ORDER, or record why each stays out with a revisit condition. This record takes the second path for both. It changes no code.

## Measured mechanic

website/index.html:1169 defines the rotation:

var GAME_ORDER = ['cinder', 'wordfire', 'minesweeper', 'simon', '2048', 'afterglow'];

Six entries. The featured game is picked by ISO-week index (week - 1) % 6, so each game is Game of the Week once every six weeks and the homepage shows one featured card. renderGameOfTheWeek() degrades safely: a missing game, playLink, or name hides the card.

## Decision

Neither Echo Rounds nor Typewreck enters the rotation today.

| Game | Decision | Reason | Revisit |
|---|---|---|---|
| Echo Rounds | stays out | Keyboard-only prototype, no touch input, no detail view. Per #214, promotion is a separate NEW-GAME-day proposal, not a GOTW edit. | Gated on touch controls plus a detail view (Story 015 pattern) plus one month of issue signal. No calendar date; gated on the build. |
| Typewreck | stays out | Shipped 2026-11-05, one day old, zero issue signal. A GOTW slot is a 7-day homepage placement; spending it on day-2 software displaces an established game for a full week. | 2026-12-07 (one month). Admission needs 3 or more external signals (issue, mention, or share) or 20 or more local plays across the new counters. |

## Rotation-width rationale

Six slots give each game one featured week in six. At eight slots each game is featured once in eight weeks, a 33 percent increase in time-to-feature for every existing game, while the homepage still shows one card either way. The rotation is a schedule, not a shelf. Adding a title costs all six incumbents something and buys the newcomer one week. That trade is only worth making on evidence, and evidence is what the play counters exist to produce.

## What would change the decision

Echo Rounds: a NEW-GAME-day promotion proposal that ships touch controls and a detail view, followed by one month of issue signal. No calendar date is set because the gate is the build.

Typewreck: 3 or more external signals or 20 or more local plays by the 2026-12-07 revisit.

Who decides: the next LEGACY-day planner, with the issue signal and counter data in hand.

## Code impact

None. This record changes no code. GAME_ORDER is byte-identical to base 1ea559f: six entries, same order, same rotation logic.
