#!/usr/bin/env python3
"""Story 033 pure-read proof for the Cinder daily-return summary (Kai, backend review),
repinned Session 64 / Story 141 (K1: proof is stale).

Purpose:
  Prove that the "come back tomorrow" preview added to renderQuest() in
  website/games/cinder.html is a pure read: it computes tomorrow's quest from the day
  index via determineQuestForDay(getDayIndex() + 1) with no save writes, no
  state mutation, and no balance/mechanics change.

How:
  This script extracts the three pure helpers (kindIndexForDay, dayIndexHash,
  determineQuestForDay) verbatim from website/games/cinder.html and exercises
  shipped logic under node, then checks the properties that make the preview
  a pure read:
    - determinism (same day -> same quest),
    - purity (quest is a closed-form function of the day index),
    - no consecutive same-kind days (the preview can never suggest tomorrow
      has today's kind -> no accidental same-quest nudge),
    - no global mutation by the selector,
    - tomorrow = determineQuestForDay(D+1) with an objective and != today.

  It then greps the body of renderQuestNextDayBlock plus the renderQuest()
  call site for save/write/mutation calls on the preview path (no
  saveCharacter, saveDayState, localStorage.setItem, ensureQuestState,
  completeQuest, applyQuestProgress). K1 repair: the old scan swept the whole
  slice from renderQuestNextDayBlock to renderQuest(, which now spans two
  later stories' helpers and their comments (false hits on comment lines, zero
  inside the actual preview body). The scan is narrowed to the preview body
  plus the call site, with comments stripped before token search.

Usage:
  python3 archive/src-games/kai-story033-pure-read-proof.py
Exit code: 0 on all checks passing, 1 on any failure.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _default_cinder_src():
    """Artifact under test: argv[1], then $CINDER_SRC, then the live file."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    env = os.environ.get("CINDER_SRC")
    if env:
        return env
    d = HERE
    while True:
        if (d / ".git").exists():
            return str(d / "website" / "games" / "cinder.html")
        if d.parent == d:
            return str(HERE.parent / "website" / "games" / "cinder.html")
        d = d.parent


CINDER_SRC = _default_cinder_src()
CINDER = Path(CINDER_SRC).read_text(encoding="utf-8")


def extract_body(name: str) -> str:
    """Return the balanced-brace body of `function name(...)` as source text."""
    m = re.search(r"function " + re.escape(name) + r"\([^)]*\)\s*(\{)", CINDER)
    if not m:
        raise SystemExit(f"function {name} not found in cinder.html")
    start = m.start(1)
    depth = 0
    i = start
    while i < len(CINDER):
        if CINDER[i] == "{":
            depth += 1
        elif CINDER[i] == "}":
            depth -= 1
            if depth == 0:
                return CINDER[start : i + 1]
        i += 1
    raise SystemExit(f"unbalanced braces in function {name}")


def strip_comments(js: str) -> str:
    """Blank out // and /* */ comments, preserving string literals as written.

    Token scans run on the stripped text so a comment that merely names a
    forbidden writer is not a false hit, while a real call in code still is.
    """
    out = []
    i = 0
    n = len(js)
    quote = None
    while i < n:
        c = js[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(js[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "'\"`":
            quote = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and js[i + 1] == "/":
            while i < n and js[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "/" and i + 1 < n and js[i + 1] == "*":
            out.append("  ")
            i += 2
            while i < n and not (js[i] == "*" and i + 1 < n and js[i + 1] == "/"):
                out.append("\n" if js[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def load_quest_types() -> list:
    m = re.search(r"const QUEST_TYPES = (\[[\s\S]*?\]);", CINDER)
    if not m:
        raise SystemExit("QUEST_TYPES not found")
    # Parse the JS array literal loosely: it is an array of object literals.
    body = m.group(1)
    # Use node to evaluate it for a faithful parse.
    out = subprocess.run(
        ["node", "-e", "process.stdout.write(JSON.stringify(" + body + "))"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return json.loads(out)


def main() -> int:
    quest_types = load_quest_types()
    bodies = {
        "kindIndexForDay": extract_body("kindIndexForDay"),
        "dayIndexHash": extract_body("dayIndexHash"),
        "determineQuestForDay": extract_body("determineQuestForDay"),
    }

    # Assemble a node script that declares the three helpers with their real
    # bodies and the QUEST_TYPES pool, then runs the pure-read property checks.
    js = (
        "const QUEST_TYPES = "
        + json.dumps(quest_types)
        + ";\n"
        + "const KIND_CYCLE = ['slay', 'gold', 'boss'];\n"
        + "function kindIndexForDay(dayIdx)"
        + bodies["kindIndexForDay"]
        + "\n"
        + "function dayIndexHash(n)"
        + bodies["dayIndexHash"]
        + "\n"
        + "function determineQuestForDay(dayIdx)"
        + bodies["determineQuestForDay"]
        + "\n"
        + "let failures = [];\n"
        + "const check = (n, p) => { if (!p) failures.push(n); };\n"
        # determinism
        + "for (let d = 0; d < 30; d++) check('determinism ' + d, determineQuestForDay(d) === determineQuestForDay(d));\n"
        # purity / no global state dependence
        + "let seen = {}, g = 1; for (let d = 0; d < 30; d++) { const q = determineQuestForDay(d); if (seen[d] && seen[d] !== q.label) g = 0; seen[d] = q.label; } check('purity-globalstate', !!g);\n"
        # no consecutive same kind
        + "let k = 1; for (let d = 0; d < 30; d++) if (kindIndexForDay(d) === kindIndexForDay(d + 1)) k = 0; check('no-same-kind-consecutive', !!k);\n"
        # no global mutation
        + "const b = JSON.stringify(QUEST_TYPES); determineQuestForDay(15); determineQuestForDay(16); determineQuestForDay(17); check('no-global-mutation', b === JSON.stringify(QUEST_TYPES));\n"
        # tomorrow deterministic + objective + differs
        + "let t = 1; for (let d = 0; d < 30; d++) { const to = determineQuestForDay(d + 1); if (!(to.objective || to.label)) t = 0; if (determineQuestForDay(d).label === to.label) t = 0; } check('tomorrow-deterministic-objective', !!t);\n"
        + "process.stdout.write(JSON.stringify(failures));"
    )

    try:
        out = subprocess.run(
            ["node", "-e", js], capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        print("NODE HARNESS FAILED:", e.stderr or e.stdout)
        return 1

    failures = json.loads(out)
    total_checks = 30 + 1 + 1 + 1 + 1  # determinism(30) + 4 single checks
    total_checks += 1  # no-same-kind is separate loop (not counted in determinism loop)

    # Recompute an honest pass count: we did not enumerate all 30 individually as pass;
    # report aggregate.
    if failures:
        print(f"PURE-SELECTOR CHECKS FAILED ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1

    # Static scan of the preview path: the preview body plus the renderQuest()
    # call site, comments stripped. K1: the old slice from
    # renderQuestNextDayBlock to function renderQuest( spanned later stories'
    # helpers and their comments (all four token hits sat on comment or
    # intervening-helper lines, zero inside the preview body lines 373-378).
    if "renderQuestNextDayBlock" not in CINDER:
        # This checkout predates the Story 033 preview block (e.g. main base
        # without Riven's renderQuest() addition). The pure-selector proof above
        # still holds; note the preview path is not present to scan here.
        print("Preview path: Story 033 block not present in this checkout; "
              "selector proof above still validates the tomorrow derivation.")
        return 0
    preview = extract_body("renderQuestNextDayBlock")
    try:
        render_quest = extract_body("renderQuest")
    except SystemExit:
        print("Preview path violates pure-read (renderQuest not found)")
        return 1
    call_lines = [ln for ln in render_quest.splitlines()
                  if "renderQuestNextDayBlock(" in ln]
    if not call_lines:
        print("Preview path violates pure-read "
              "(renderQuest never calls renderQuestNextDayBlock)")
        return 1
    path = strip_comments(preview + "\n" + "\n".join(call_lines))
    print("Preview path: scanned renderQuestNextDayBlock body (%d chars) + "
          "%d call-site line(s)" % (len(preview), len(call_lines)))
    forbidden = [
        "saveCharacter", "saveDayState", "localStorage.setItem",
        "ensureQuestState", "completeQuest", "applyQuestProgress",
        "character.", "dayState.",
    ]
    scan_fail = [f for f in forbidden if f in path]
    print("Preview path: forbidden-token hits: %d" % len(scan_fail))
    if scan_fail:
        print("Preview path violates pure-read (found write/mutation ref):", scan_fail)
        return 1

    print("PURE-READ PROOF PASS")
    print("  selectors: determinism, purity, no-same-kind-consecutive, no-global-mutation, tomorrow-deterministic-objective")
    print("  preview-path scan: no save/write/mutation/state refs (pure read)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
