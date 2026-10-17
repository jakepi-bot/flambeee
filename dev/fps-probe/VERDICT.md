# Story 071 VERDICT: echo-rounds FPS viability probe (Session 33)

Base: 54925ce (origin/main, confirmed by rev-parse before branch).
Branch: feat/session33-071-fps-probe.
Owner: Kai (probe plus harness). Riven consult input/render. Scout proves falsifying test.
jakebot citation: 20261017_011130_01bb1d (Session 33 Wave 1-2 set, Option A, recorded in Story 071 and session-plan.md).
Copy rule: plain punctuation, no em dashes, minimal emoji (none).

## Scope guardrails honored (no-sprawl)

New files only under dev/fps-probe/. No package.json, no node_modules, no native toolchain, no engine choice, no FPS build beyond the probe. Probe is single-file no-build HTML/JS. Harness is plain node with no new dependency. No touch of website/index.html, website/sw.js, website/apps/, src/, website/games/, docs/stories/, scripts/verify-website-currency.sh.

## Falsifying test (Story 068 lines 56-58, quoted verbatim via Story 071)

> **Falsifying test (named):** Web viability is falsified if, on the mechanic's minimal probe (dark scene + one light pulse per shot + simultaneous move/look/fire), either (a) sustained Pointer Lock + Gamepad polling drops or desyncs input under load, or (b) the single-file no-build render cannot hold a readable frame rate with the transient light + lit-state hit check. A probe that passes on an empty scene and fails once the light-ammo loop runs still falsifies; the test is keyed to the mechanic, not to a hello-world page.
>
> **Native-fallback trigger (stated):** Fallback to native Windows/Mac/Linux triggers only on recorded evidence of the falsifying test above, with the failing numbers quoted. No parallel native promise, no toolchain work before that evidence exists. Phase 1 proves web; Phase 2 native only if Phase 1 fails with evidence.

## Controller matrix (resolved BEFORE probe runs, 068 open Q3)

Run box checks, measured 2026-10-17:
- /dev/input/js*: absent (no joystick nodes). /proc/bus/input/devices: 0 matches for joystick/gamepad/xbox/playstation. Devices present: AT keyboard, power button, VMware VMMouse, QEMU USB tablet, PC speaker. No physical gamepad on this box.
- Browsers: Chromium 155.0.8059.79 (system chromium, headless=new). Firefox 158.0 (Mozilla tarball under scratch cache, headless). Minimum matrix Chromium plus Firefox desktop: SATISFIED for the render and input-event path.
- Gamepad API polled every frame by the probe: 0 non-empty samples on all runs (Chromium mechanic-loop 0/601, Firefox 0/602). navigator.getGamepads path exercised, no pad connected.
- Pointer Lock in headless: "error" on both browsers (no user gesture/display in headless). Recorded, not a mechanic failure. Real Pointer Lock with gesture needs a headed run.
- LIMITATION (binding): this run is keyboard plus scripted synthetic input only. Per Story 071 Scenario 5 a keyboard-only run is a recorded limitation, never a pass for the full simultaneous look/move/fire plus gamepad leg. The numbers below pass the measurable axes; the gamepad leg stays OPEN and must be re-run on a box with a physical pad before any ship claim.

## Numeric floor for readable frame rate (dev proposes, parent confirms)

Proposed floor (carried from Session 32 Kai consult on Story 068): sustained mean at or above 30 FPS with p95 frame time at or below 33.4 ms, reference target 60 FPS. Below that floor on the mechanic-loop run is a readability fail and falsifies web viability on the render axis. Headed vs headless caveat: headless has no vsync/GPU path, so these numbers measure compute headroom with the light-ammo loop running, not a real display. Stated so the numbers do not overclaim.

## Probe and harness

- dev/fps-probe/echo-rounds-probe.html: dark canvas scene, one light pulse per shot, lit-state hit gate, shooter-reveal on fire (visibleUntil now plus 150ms), scripted simultaneous move/look/fire for 10 s, shot every about 120 ms. Modes: default mechanic-loop, ?empty=1 empty scene (no pulses), ?sabotage=1 full loop plus 50 ms busy-wait per frame (negative control).
- dev/fps-probe/run-probe.js: plain-node server plus browser launcher, collects the JSON the probe POSTs to /results. Usage: node dev/fps-probe/run-probe.js <chromium|firefox> [query]. No new dependency.
- Negative-control proof (Scout leg): the sabotage runs FAIL the floor on both browsers (see numbers), so a green run is a measurement, not a tautology. Empty-scene control passes on both browsers, and the mechanic-loop run also passes, so Scenario 4 (empty passes but loop fails) does NOT trigger: verdict keyed to the mechanic, loop holds.

## Real harness output (verbatim JSON, 2026-10-17 run box)

Chromium mechanic-loop:
{"mode":"mechanic-loop","runMs":10016,"frames":600,"frameMeanMs":16.69,"frameP50Ms":16.7,"frameP95Ms":16.8,"frameP99Ms":16.8,"fpsMean":59.9,"slowFramesOver33ms":0,"shots":75,"pulsesEmitted":75,"gatedHits":0,"gatedMisses":75,"shooterReveals":75,"inputInjected":244,"inputObserved":244,"inputDrops":0,"holdPhaseFrames":601,"holdPhaseSawDown":601,"holdAgreementPct":100,"subframeTaps":101,"subframeTapsEventSeen":101,"subframeTapsPollSeen":0,"pointerLock":"error","gamepadSamples":601,"gamepadNonEmpty":0,"gamepadEmpty":601,"userAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"}

Firefox mechanic-loop:
{"mode":"mechanic-loop","runMs":10017,"frames":601,"frameMeanMs":16.67,"frameP50Ms":17.06,"frameP95Ms":17.16,"frameP99Ms":17.26,"fpsMean":60,"slowFramesOver33ms":0,"shots":75,"pulsesEmitted":75,"gatedHits":0,"gatedMisses":75,"shooterReveals":75,"inputInjected":244,"inputObserved":244,"inputDrops":0,"holdPhaseFrames":602,"holdPhaseSawDown":602,"holdAgreementPct":100,"subframeTaps":101,"subframeTapsEventSeen":101,"subframeTapsPollSeen":0,"pointerLock":"error","gamepadSamples":602,"gamepadNonEmpty":0,"gamepadEmpty":602,"userAgent":"Mozilla/5.0 (X11; Linux x86_64; rv:158.0) Gecko/20100101 Firefox/158.0"}

Chromium empty-scene control:
{"mode":"empty-scene","runMs":10016,"frames":601,"frameMeanMs":16.67,"frameP50Ms":16.7,"frameP95Ms":16.7,"frameP99Ms":16.8,"fpsMean":60,"slowFramesOver33ms":0,"shots":75,"pulsesEmitted":0,"gatedHits":0,"gatedMisses":0,"shooterReveals":75,"inputInjected":244,"inputObserved":244,"inputDrops":0,"holdPhaseFrames":602,"holdPhaseSawDown":602,"holdAgreementPct":100,"subframeTaps":101,"subframeTapsEventSeen":101,"subframeTapsPollSeen":0,"pointerLock":"error","gamepadSamples":602,"gamepadNonEmpty":0,"gamepadEmpty":602,"userAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"}

Firefox empty-scene control:
{"mode":"empty-scene","runMs":10016,"frames":601,"frameMeanMs":16.67,"frameP50Ms":17.04,"frameP95Ms":17.16,"frameP99Ms":17.2,"fpsMean":60,"slowFramesOver33ms":0,"shots":75,"pulsesEmitted":0,"gatedHits":0,"gatedMisses":0,"shooterReveals":75,"inputInjected":244,"inputObserved":244,"inputDrops":0,"holdPhaseFrames":602,"holdPhaseSawDown":602,"holdAgreementPct":100,"subframeTaps":101,"subframeTapsEventSeen":101,"subframeTapsPollSeen":0,"pointerLock":"error","gamepadSamples":602,"gamepadNonEmpty":0,"gamepadEmpty":602,"userAgent":"Mozilla/5.0 (X11; Linux x86_64; rv:158.0) Gecko/20100101 Firefox/158.0"}

Chromium sabotage (negative control, must FAIL):
{"mode":"sabotage","runMs":10033,"frames":196,"frameMeanMs":51.19,"frameP50Ms":50,"frameP95Ms":66.6,"frameP99Ms":66.7,"fpsMean":19.5,"slowFramesOver33ms":196,"shots":24,"pulsesEmitted":24,"gatedHits":0,"gatedMisses":24,"shooterReveals":24,"inputInjected":244,"inputObserved":244,"inputDrops":0,"holdPhaseFrames":197,"holdPhaseSawDown":197,"holdAgreementPct":100,"subframeTaps":101,"subframeTapsEventSeen":101,"subframeTapsPollSeen":0,"pointerLock":"error","gamepadSamples":197,"gamepadNonEmpty":0,"gamepadEmpty":197,"userAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"}

Firefox sabotage (negative control, must FAIL):
{"mode":"sabotage","runMs":10033,"frames":200,"frameMeanMs":50.16,"frameP50Ms":50.32,"frameP95Ms":50.5,"frameP99Ms":66.52,"fpsMean":19.9,"slowFramesOver33ms":199,"shots":25,"pulsesEmitted":25,"gatedHits":0,"gatedMisses":25,"shooterReveals":25,"inputInjected":244,"inputObserved":244,"inputDrops":0,"holdPhaseFrames":201,"holdPhaseSawDown":201,"holdAgreementPct":100,"subframeTaps":101,"subframeTapsEventSeen":101,"subframeTapsPollSeen":0,"pointerLock":"error","gamepadSamples":201,"gamepadNonEmpty":0,"gamepadEmpty":201,"userAgent":"Mozilla/5.0 (X11; Linux x86_64; rv:158.0) Gecko/20100101 Firefox/158.0"}

Notes read with the numbers: gatedHits 0 with gatedMisses 75 means the scripted yaw sweep aimed at nothing; the lit-state gate executed every shot (pulses lit targets, crosshair ray checked lit state) but hit no target. That exercises the gate path, not aim skill. subframeTapsPollSeen 0 is expected by construction (down plus up injected between polls; event listeners saw all 101 pairs, poll saw none) and is reported informationally, not counted as drops. inputDrops 0 and holdAgreementPct 100 on all real runs.

## Verdict

CONDITIONAL PASS with recorded limitations. Render axis: PASS on both browsers (Chromium 59.9 FPS mean, p95 16.8 ms; Firefox 60 FPS mean, p95 17.16 ms; 0 slow frames; floor is 30 FPS mean with p95 at or below 33.4 ms). Input-event axis: PASS (0 drops over 244 injected edges, 100 percent hold agreement, both browsers). Negative control: FAILS as required (19.5 and 19.9 FPS), so the harness is not a tautology. Falsification triggers: neither (a) nor (b) fired on the measurable axes. No native-fallback trigger: no recorded failing numbers, so no Phase 2 native decision. Binding limitations: keyboard-only (no gamepad on run box, 0 non-empty gamepad samples), headless Pointer Lock error, headless FPS is compute headroom not display proof. A pass here does not grow into building the FPS; the probe stops at this verdict per the no-sprawl rule.
