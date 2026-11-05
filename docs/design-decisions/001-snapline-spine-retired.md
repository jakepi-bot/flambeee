# 001 - Snapline spine retired (2026-11-05)

## Context

Session 51 shipped Snapline (Story 116 game, Story 117 site) to PR #206 (`feat/session51-116-117-snapline`, head `22e4ce2`) against the Session 51 mechanic contract. The spine: every fired orb sticks permanently and adds one load to a ceiling-hung strand, strands detach past anchor strength, the ceiling descends on a shot clock. The contract's falsifier was a 200-seed sim (greedy clears at least 120, random at most 30) plus real-input design review.

## Evidence

- Dev harness on the shipped file: straight-up greedy clears 4/200 vs bar 120; random clears 3/200; taught-strand reachability within 3 loads holds 35/200 vs bar every seed. Plan B numerics already applied, gap unchanged.
- Rook design review (30+ real-input games): 1 win in 21 aimed games; 12 of 13 losses land before shot 15; the taught column grows downward toward the line row, so doing what the UI teaches loses at shot 3 to 4 with score 0 on most seeds.
- QA independent harness: aimed greedy 3/200, reachability 52/200 plus 7 already-over boards, generation guarantee fails outright on 5/200.
- The file header's 124/200 claim reproduces only under a non-ballistic placement policy the dev record itself calls partly unreachable; it must not be read as ballistic evidence and needs correction or removal on the next touch.

## Decision

The Snapline spine is RETIRED, not reworked. PR #206 stays OPEN as reference only; nothing from it merges. Session 52 builds the new original game (Typewreck) instead. The CEO "Do Snood next" reply stays acknowledged-but-declined under directive 6 (no reskins without an explicit override); only an explicit CEO override changes that.

## Reversal condition

A future rework (Snapline or otherwise) needs a new design that clears honest ballistic thresholds with real-input play across a seed sample, plus removal or correction of the 124/200 header claim. Tuning inside the retired contract's table cannot reverse this: the failure is structural (density trades winnability against top-up room in opposite directions), not numeric.
