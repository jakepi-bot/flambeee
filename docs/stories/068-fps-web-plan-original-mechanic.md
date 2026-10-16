# Story 068: FPS web-first plan with original mechanic + viability test (Session 32, P1, Planning)

**Status:** Ready for review (Session 32, 2026-10-16). **Planning doc. No game code.**
**Author:** Quinn (Business Analyst), Wave 2.
**Priority:** P1 (planning; CEO override item 1, directive 6 governs).
**Assigned to:** **Parent-owned doc.** **Kai/Riven** consult on viability-test shape only if needed. No game-file change.
**Tracked by:** Session 32 plan, Story 068. References `flambeee-team/CEO-DIRECTIVES.md` sections 6 and 7, `docs/roadmap.md` Now section.
**Depends on:** Story 059 (originality precedent, Afterglow). No code dependency.

## Summary

Plan the FPS headline before any build. This doc names one candidate original mechanic, states why it is not a reskin, and defines the web viability test keyed to that mechanic's input and render needs, with the falsifying test named and the native-fallback trigger stated. If the doc cannot name the mechanic, it is not done. No game file, no prototype, no toolchain change this half.

## jakebot decision (advisory only, recorded)

**Question put to jakebot (Session 32, 2026-10-16 ~01:13 CDT, session 20261016_011401_2a5865):** Is the right Wave 1-2 set (a) one FPS viability planning story + (b) Apps one-pager + (c) website-currency verification, all planning/docs shaped, vs splitting FPS into viability + mechanic design.

**Answer:** **Set (a)+(b)+(c) is right. Do not split FPS.** A standalone viability story answers a known-yes (gamepad + pointer lock work) and enables a reskin; viability and mechanic constrain each other. The single FPS doc must (i) name at least one candidate original mechanic with why it is not a reskin (directive 6, load-bearing), and (ii) define the viability test against that mechanic's input/render needs with the falsifying test named and the native-fallback trigger stated. If the doc cannot name the mechanic, it is not done. Keep three stories; splitting to four burns a wave slot on two parent-owned planning docs with no independent work. Priority: FPS P1, Apps P1, currency P2. Docs-only release is legitimate (precedent 031/039/058).

**Citation:** `flambeee-team/session-plan.md`, Session 32 (2026-10-16), section "jakebot decision (advisory only, recorded)", session 20261016_011401_2a5865.

## Directives this story serves

Quoted from `CEO-DIRECTIVES.md` section 6 (traceable source, not paraphrase):

> Do not get fixated on it being doom. Keep the small web games. You just need to do
> something original and creative for a game instead of knockoffs of other games.
> This should be number 1 on your plan for the next build.

Quoted from `CEO-DIRECTIVES.md` section 7 (CEO override 2026-10-15, convo 3mwvyou25ec2p, message 3mxvvvuomct2n):

> It's time to expand what we are doing. I want a first person shooter with full controller support. If this is not viable as a web game, let's make it a cross platform game available for windows, Mac, and Linux.

Decision recorded in section 7, both ACCEPTED: (1) FPS with full controller support, web build first with explicit viability test, native as fallback exactly as framed, leading with one genuinely original mechanic per directive 6; (2) Flambeee Apps as second division. Small web games stay.

## Candidate original mechanic (one only, defer-first)

**Candidate name: echo-rounds (light-ammo FPS).**

The arena is dark. You fire light, not bullets. Each shot emits a short light pulse that reveals geometry and targets while it lasts, then fades. Hits count only on lit targets. Movement is silent and keeps you hidden; firing reveals you as well as the target. The core loop is a tradeoff you manage every shot: see more, be seen more.

Why this is the candidate: it makes the FPS about visibility budgeting under first-person controller input, not about weapon roster or map skin. It reuses nothing from our shipped loops as its core (Cinder is a menu RPG, Afterglow is a grid memory puzzle) and it is testable in a browser because its input needs (look + move + fire at once) and its render needs (dark scene, transient light, hit check against lit state) are exactly what the viability test measures.

**Why not a reskin (directive 6 reskin test, load-bearing):** A reskin passes if you can describe it as an existing named title with swapped art. This candidate fails that description on purpose: remove the art and the remaining rule (shots are the light source, hits require lit state, firing exposes the shooter) is not Doom, not a Doom-like, and not any of our six shipped games. If the dev-wave playtest reads as "Doom clone with dark lighting," the fix is to sharpen the light-ammo tradeoff (shorter pulse, stricter lit-to-hit gate, louder self-reveal), not to add weapons or maps. No second mechanic is named here; alternatives defer to the dev wave.

## Viability test keyed to that mechanic

Constraint from roadmap line 11 carried forward: single-file no-build static HTML/JS stays the default unless the test falsifies it; a full controller FPS is not assumed to fit it.

The viability test measures the mechanic's actual needs, not API existence (Pointer Lock + Gamepad API existence is already known-yes per the Session 32 market check; the unknown is mechanic-specific):

1. Input: simultaneous Pointer Lock look + WASD/keys + Gamepad API poll (left stick move, right stick look, trigger fire) with no stuck input and no pointer-loss lockup during fire-move-look.
2. Render: dark first-person scene with transient per-shot light, lit-state hit gate, sustained readable frame rate on desktop Chromium and Firefox with no build step.
3. Session: playable in one file with no downloads, matching zero-friction and mobile-degrades-gracefully expectations (desktop + controller is the target; touch is fallback, not the gate).

**Falsifying test (named):** Web viability is falsified if, on the mechanic's minimal probe (dark scene + one light pulse per shot + simultaneous move/look/fire), either (a) sustained Pointer Lock + Gamepad polling drops or desyncs input under load, or (b) the single-file no-build render cannot hold a readable frame rate with the transient light + lit-state hit check. A probe that passes on an empty scene and fails once the light-ammo loop runs still falsifies; the test is keyed to the mechanic, not to a hello-world page.

**Native-fallback trigger (stated):** Fallback to native Windows/Mac/Linux triggers only on recorded evidence of the falsifying test above, with the failing numbers quoted. No parallel native promise, no toolchain work before that evidence exists. Phase 1 proves web; Phase 2 native only if Phase 1 fails with evidence.

## Requirements

### 1. Mechanic named, reskin test stated

- Exactly one candidate mechanic named in this doc (echo-rounds above). No second candidate, no prototype.
- Reskin test written in plain language: could this be described as a named existing title with swapped art. Answer recorded as no, with the reason tied to the light-ammo rule.

### 2. Viability test defined against the mechanic

- Test names the three input/render needs above (Pointer Lock + Gamepad simultaneous input, transient-light render, single-file session).
- Falsifying test named explicitly; native-fallback trigger stated as evidence-gated, not parallel.

### 3. Planning only

- No change to `src/`, `website/`, `share/Flambeee/`, `scripts/`, game files, sw.js, blog, or releases.
- No native toolchain, no dependency, no build step introduced by this story.

## BDD scenarios

**Scenario 1: Candidate mechanic named.**
Given the Session 32 plan requires an original mechanic, when this doc is read, then it names exactly one candidate mechanic (echo-rounds: shots emit the light that hits require) and defers all alternatives.

**Scenario 2: Not a reskin per directive 6.**
Given directive 6 (quoted above), when the reskin test is applied, then the doc states why the candidate is not describable as a named existing title with swapped art, and names sharpening the light-ammo tradeoff as the fix if the playtest reads as a clone.

**Scenario 3: Viability test keyed to the mechanic.**
Given the candidate's input and render needs, when the viability test is read, then it covers simultaneous Pointer Lock + Gamepad input, transient-light render with lit-state hit gate, and single-file no-build session play, not bare API existence.

**Scenario 4: Falsifying test named.**
Given the viability test, when it is evaluated, then the doc names what fails web viability (input drop/desync under mechanic load, or unreadable frame rate once the light-ammo loop runs).

**Scenario 5: Native-fallback trigger stated.**
Given a falsified web test, when the fallback question is asked, then the doc states native Windows/Mac/Linux triggers only on recorded failing evidence, with numbers quoted, and forbids parallel native work before that.

**Scenario 6: No game code.**
Given this story's diff, when it is inspected, then it contains only this Markdown file, no `src/` or game-file change, no toolchain or dependency, and no website/blog/release edit.

**Scenario 7: jakebot citation present.**
Given the Wave 1-2 set decision, when this doc is reviewed, then it records the question, the answer (set a+b+c right, do not split FPS), and the citation session 20261016_011401_2a5865.

## Acceptance Criteria

**AC-1.** One candidate original mechanic named with reskin reasoning tied to directive 6 (Scenarios 1, 2).
**AC-2.** Viability test defined against that mechanic's input/render needs (Scenario 3).
**AC-3.** Falsifying test named and native-fallback trigger stated as evidence-gated (Scenarios 4, 5).
**AC-4.** Planning only: no game code, no toolchain, no website/blog/release change (Scenario 6).
**AC-5.** jakebot question/answer/citation recorded verbatim as above (Scenario 7).
**AC-6.** Copy uses plain punctuation, no em dashes, no heavy emoji.

## Non-Goals

- A second mechanic, a shortlist, or a mechanic vote. One candidate, defer-first.
- Any prototype, probe build, or harness code. The dev wave designs the probe from this test.
- Any native toolchain, engine choice, or parallel native plan.
- Any change to small web games, the site, or the release process.

## Open questions for dev wave

1. Probe shape (Kai/Riven consult): minimal single-file scene that loads the mechanic enough to run the falsifying test, nothing more.
2. Frame-rate readability bar: numeric floor for "readable" under the light-ammo loop (dev wave proposes, parent confirms).
3. Controller matrix: which Gamepad layouts must the probe poll (dev wave proposes minimum: Chromium + Firefox desktop).
