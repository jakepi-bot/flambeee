# Test plan — Stories 159-162, LIGHTFARE Session 71 (Scout, QA)

Source: `docs/stories/159/160/161/162-*-session71.md` + `flambeee-team/design-handoff.md` (contract
sections 1-4). Executed 2026-11-24 against the integrated #289+#290 tree; 119 browser checks +
6 harness runs, all green. QA script (scratch): `s71-qa/qa_s71.py` (Playwright, system Chromium,
`env -u PYTHONPATH <venv>/python`, serve `<wt>/website` on 8971, harness default 8943).

## 159 — input guard + TITLE affordance (game file only)

1. 1280x800, fresh context per state. TITLE: press each of ArrowUp/Down/Left/Right, w/W/a/A/s/S/d/D;
   assert `window.scrollY` stays 0, `__lightfare.state()` TITLE, plays unchanged, `#msg` `''`.
2. Reach RUN (click Start), LEVELCLEAR (solve L1: RRRRDDDD), WIN (solve L2 DDDRRUUURR, L3
   DDRRUURRDDDD, L4 DDDDRRUUURRDDD, L5 RRRRDDLLLLDDRRRR), LOSE (fresh L1 run, 40x Right/Left wander,
   80 moves). In each state: `scrollTo(0,0)`, press all 12 keys, assert scrollY 0 + state + plays pinned.
3. Negative control (1280x400, scrollable doc): PageDown must scroll (0 -> 350); ArrowDown after must
   not add scroll (350 -> 350).
4. TITLE taps: `#btnUp` and `#btnLook` each render exactly
   `Press Start to play. Use the pad once your run begins.` (54 chars) with state TITLE, plays/pos
   unchanged, light 15, looks 0. Five taps byte-identical. Re-read after 2 s: string persists.
5. Focus: `#startBtn` focused + Enter = exactly one run (plays +1). RUN Enter = no-op.
   WIN Enter with blurred focus = back to TITLE (focused-button Enter activates natively by design).
6. Reveal freeze: LOOK in RUN, then arrows/pad: pos/moves unchanged, no scroll; reveal ends ~1 s.
7. Threshold: 100% of key presses 0 px scroll; 5/5 TITLE taps exact with no state change.

## 160 — fold fit + next-look price (game file + 1 sw.js line)

1. Viewports 375x667, 360x740, 390x844 (mobile context, touch), `scrollY=0` forced. TITLE: `#startBtn`
   rect top >= 0, bottom <= vh. RUN (click Start): `#pad` and `#btnLook` rects inside vh. Ends: force
   LOSE via 80 real moves, `#againBtn` rect inside vh. 13 rect sets, 0 px overflow allowed.
2. Doc ceilings: TITLE <= 667 @375x667, <= 740 @360x740; RUN <= 727 @375x667 (keys line only overflow),
   <= 800 @360x740. Measured: 667/667, 740/740 (390x844: no ceiling, rects fit).
3. Readout: fresh RUN reads `Next look: 1`; spend 1+2+4+8 (wait out each 1 s reveal) reads
   `Next look: 2/4/8`, then `Looks maxed` at looks 4, light 0. 5th look: `Not enough light.`,
   HUD still `Looks maxed`, light unchanged. 5/5 strings byte-equal.
4. Economy regression: harness static/trials/mutation CHECKs (BFS [8,10,12,14,16], 50/50 trials,
   mutation red) must repeat identical PASS.
5. sw.js: `CACHE_VERSION` 34, exactly 24 precache entries, every other line byte-identical to base.

## 161 — harness port ownership (dev file only)

1. Free 8943: full harness, expect exit 0, standard report, 8943 closed after, no stray processes.
2. Stranger `python3 -m http.server 8943 --directory /tmp` (answers 200): harness default port,
   expect exit 1 with the exact `FAIL: port-ownership: ... (reason: --port=8943 or default 8943)`,
   `CHECK browser-legs: FAIL (exit 1) port 8943 occupied at preflight; no server started, none killed`,
   `RESULT: FAIL (exit 1)`; stranger still 200 after; sole 8943 listener is the stranger PID.
3. Stranger up + `--sim-only`: exit 3, SKIPPED, zero `port-ownership` lines.
4. Stranger up + `--viewport=desktop`: exit 1 refusal (FAIL dominates SKIP). Kill only the stranger PID.
5. `grep -n 'fuser\|pkill' dev/lightfare-proof.py`: no matches.
6. RED anchor on plain base (game file absent, `--sim-only` fine): exit 2.

## 162 — probe-count doc fix (story file only)

Line 30 shows `19 members, no plays getter` (line-488 ref intact); line 96 shows
`19 members become 20` (getter snippet + `reset()` sentence intact). Diffstat exactly that file,
2-line shape; `grep -c "18 members"` = 0; zero code bytes.
