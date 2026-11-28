# 012: Desktop game anchor table (Session 75)

Contested call: contract Section 2.1 required every game page to expose
`canvas` OR `#board` as its desktop anchor. Five long-shipped working
games expose neither: 2048 uses `#grid`, cinder is a text RPG with
`#promptInput`, empty-hands and saltline use a `#screen` wrapper, and
simon uses a `.game-board` class div.

Decision (jakebot ruling, 2026-11-28, parent applied):
1. The desktop game anchor is a per-game table, not one selector for all
   games. The table lives in `flambeee-team/design-handoff.md` Section
   2.1a and is design-owned, not harness-owned.
2. An anchor must exist, be rendered, and be visible (display not none,
   visibility not hidden, offsetWidth and offsetHeight above 0). Existence
   alone is not enough.
3. A game page absent from the table FAILS. Adding a 13th game requires a
   contract amendment, never a silent pass.
4. One miss still fails the page and the run. Website bytes stay frozen;
   no page was edited to satisfy a selector.

Why: "canvas OR #board" encoded an assumption about how the games were
built, and five working games were built differently. A gate that can
never pass gets ignored, then deleted, which is how yesterday's dead site
went unnoticed. A per-game table with visibility and composite checks is
stricter than the literal clause, not looser, and it keeps the assertion
at "the play surface rendered". This is the second Section 2.1 spec defect
in three sessions, which is why the table belongs in the contract with an
owner rather than as a constant inside the harness.

Locked: the table rows and composite requirements, table-miss fails, the
visibility predicate, and the `--red-anchor` fixture (missing
`games/simon.html`, STATIC only, exit 2).
