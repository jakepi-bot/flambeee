# Backlog 001: Drawn Levels (personal input becomes the level)

**Filed:** 2026-11-25, Session 72 planning (parent). **Status:** backlog, not
scheduled. **Gate:** do not build until the open defect queue is clear and a
jakebot consult picks a new-game day.

## Why this exists

The freshest browser-game signal of the month is CAEN Inc's *Kyokara Omaeha /
Sign Your Name Away*: 14.56 million plays in its first five days (16.7 million
by 2026-11-23), free, no account, processed locally in the browser, result
shared as an image. The player draws a signature with a finger or mouse and the
game clips and rearranges the surviving strokes into a new name.

The transferable insight is not "names". It is that a player's own mark is
content they will share, and that the transformation is legible in one screen.

## The mechanic sketch (to be designed by Rook, not by this note)

One continuous stroke drawn by the player becomes the level geometry they then
traverse. The game measures the stroke's length, curvature, and self-crossings,
and builds a short path with walls exactly where the drawn line crosses itself.
The player then walks that path in the same tab with the same controls. One
session is draw, then traverse, then a score based on how much of the drawn line
survived (straight lines erode less; loops become rooms).

Working name: **Trace**.

## Hard constraint (from the Session 72 jakebot consult)

**It must not share the letterform-cutting interaction.** No character
recognition, no clipping strokes into kanji or letters, no "the game renames
you". The subject is the line as geometry, not the line as a glyph. If the build
cannot be described without referencing letterform cutting, it is not this idea
and should be killed rather than reskinned.

## Other constraints

- Single HTML file, zero dependencies, no network after load, mobile-first
  (finger drawing must work), keyboard parity for traversal.
- Original mechanic per CEO directive 6. A Line Rider reskin does not satisfy
  it: the novelty must be the drawn line becoming walls, not a track.
- No new storage key unless it follows `docs/play-counter-pattern.md`.
- Two devs, one session, one file. If it cannot fit, it waits.

## Open questions for Rook

1. What makes a bad drawing a bad level without telling the player they drew
   badly? The transformation must be forgiving first, expressive second.
2. Is the traversal phase keyboard-only, or does the same finger drag again?
3. What is the shortest line that still produces a playable level, and what does
   the game do below it?
4. Does the score need to be shareable as an image, and if so what does it show
   without exposing handwriting?

## Evidence to cite when it is scheduled

- CAEN release note, 2026-11-20: 14.56M plays in five days (caen.co.jp).
- CAEN official guide, 2026-11-23: 16.7M plays total, local-only processing,
  share image/video (caen.games).
- Sensor Tower 2026 cohort: indie breakouts 43 percent of 500k+ first-month
  launches; winning pattern is instant readability plus systemic depth.
