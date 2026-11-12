# 005. Session 59 archive retarget recount (Rook, 2026-11-12)

Status: accepted for Session 59 dev wave. Base `3a60d21` (main, v0.49.0).

## Calls

Four contested calls, each verified against the tree at `3a60d21`, not taken from the session brief.

1. The retarget set is 19 files, not 16. jakebot enumerated 16 (11 proofs plus 3 JS plans plus `discover()` plus README) and ruled separately that the 3 dev utilities retarget rather than delete. The session-plan handoff line lists all five groups yet sums them as 16. The sum is wrong: 11 + 3 + 3 + 1 + 1 = 19. There is no 20th; every other live-tree `src/` candidate is leave-alone by rule (historical git-show refs, CONTROL_PIN, website comments, frozen records).
2. `kai-story033` needs no functional change. The brief described it as a single-level climb (`HERE.parent`). The file at lines 48-51 walks up from itself to the enclosing `.git` entry and resolves the live game from there, which is depth-agnostic and survives the move unchanged. The `HERE.parent` expression at line 53 is the fallback for running outside any checkout, which never fires in family runs. Only its usage docstring (line 28) is retargeted.
3. The three dev utilities retarget to `archive/src-games/`, never to `website/games/`, never deleted. Archive retarget preserves behavior exactly (same bytes, new path); website retarget would silently switch `capture-game-shots.py` to different live bytes and would let `gen-words.py` write a live precached asset. A move must not smuggle a behavior change.
4. The 066 `BASELINE_REF` default must be pinned to the pre-move main HEAD hex, resolved once at branch time. A path constant cannot fix it because the ref resolves against the object store, not the working tree, and the proof BLOCKs (exit 2) when the baseline is unreadable. Floating refs (`origin/main`, `main`) change meaning across the merge; only a commit hex is stable on both sides.

## Reversal rule

If a 20th live reference is found during the dev wave, it is added to the E2 table with its line number and disposition before any edit, and the count in section E is corrected in the same PR. The count is measured, never argued.
