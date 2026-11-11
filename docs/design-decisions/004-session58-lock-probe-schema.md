# 004. Session 58 lock-probe schema (Rook, 2026-11-11)

Status: accepted for Session 58 dev wave. Base `f029493`.

## Call

Story 130 ships four probe fields (`lockAcqs`, `firstMx`, `firstMy`, `lockPending`) and no guard. The 200 px figure survives only as a post-hoc analysis threshold applied to recorded data, never as code.

## Why four fields and not two

Session 57 specced two fields (`guardArmed`, `guardDrops`) sized for a guard that no longer ships. Without the guard there is nothing to arm and nothing to drop, so both names would lie. The headed question is whether the warp exists and how big it is. That needs, at minimum: how many acquisitions happened (counter, else multi-click runs are unreadable), the actual first-move delta pair in event pixels (else pixels-to-radians conversion is a guess), and a flag separating acquired-but-unmoved from moved (else a null pair reads as either). Four fields is the minimum that answers the question; fewer cannot.

## Why the threshold stays out of the code

Putting any `GUARD_PX`-like constant in the file ships half the held guard: a future session reads it as intent and wires the predicate back in without the headed evidence jakebot required. Analysis thresholds live in the handoff (section A2), not in the tuning block.

## Reversal rule

If a headed run reproduces the warp on 2 of 3 runs per the section A8 protocol, Story 130's guard becomes P1 and its two guard fields are specced then. This record does not prejudge their names.
