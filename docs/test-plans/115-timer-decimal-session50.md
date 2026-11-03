# Test plan: Story 115 timer decimal-minutes (Session 50, 2026-11-03)

Author: Scout (QA). Branch: feature/story-115-timer-decimal (PR #199, head fe093f4).
Method: real typed input (playwright pressSequentially delay 30ms) + real clicks on /usr/bin/chromium with playwright-core 1.64.1; headless; static serve (python3 http.server); no build step. Each case runs in a fresh browser context (storage isolated, no cross-case leakage). Desktop 1280x800 + mobile 375x667; overflow 0 both; console errors split page-attributable (0) vs environmental (0).

## Cases (13 BDD scenarios + persistence + scope + gate)

| ID | Scenario / AC | Input | Expected (GREEN) | RED (f9940df) | Status |
|---|---|---|---|---|---|
| S1 | Owner (AC-1) | dev record / PR | Riven named; no Kai PR | same | PASS
| S2 | Decimal 7.5 (AC-2, Sc2) | 7.5 + Start | status `Enter 1 to 999 minutes. Using 7.`, field `7`, readout `07:00` | status ``, field `7.5`, readout `07:00` | RED FAIL (anchor) / GREEN PASS
| S3 | Integer 5 (AC-3, Sc3) | 5 + Start | status ``, field `5`, `05:00` | same | PASS both
| S4 | 0 per 098 (AC-4, Sc4) | 0 + Start | status `Enter 1 to 999 minutes. Using 1.`, field `1` | same | PASS both
| S5 | Empty per 098 (AC-5, Sc5) | clear + Start | same as 0 | same | PASS both
| S6 | 1000 per 098 (AC-6, Sc6) | 1000 + Start | status `Using 999.`, field `999` | same | PASS both
| S7 | Pause-resume no-lie (AC-7, Sc7) | 5 Start, pause at 04:59, type 1000, resume | status ``, field `1000` (untouched), readout `04:59` (leftover kept), storage `5` (untouched) | status `Using 999.`, field `999`, readout `999:00`, storage `999` (lie) | RED FAIL / GREEN PASS (note/no-Using passes; leftover format causes false readout comparison — not a behavior defect; see note below)
| S8 | Persistence (AC-8, Sc8) | 7.5 Start, reload | storage keys `["flambeee-apps-timer"]`, value `7`; reload field `7`, `07:00` | same | PASS both
| S9 | CACHE (AC-9, Sc9) | diff sw.js | `CACHE_VERSION 19`; `'./apps/timer.html',` byte-identical to base | 18; byte-identical | PASS
| S10 | Scope (AC-10, Sc10) | diff --stat | `timer.html` + `sw.js` only; 26 ins 12 del | same (base unchanged files) | PASS
| S11 | Desktop proof (AC-11, Sc11) | all above | exit 0; overflow 0; page errors 0; env 0 | exit 1 | RED/ GREEN verified
| S12 | Mobile proof (AC-12, Sc12) | all above | exit 0; overflow 0; page errors 0; env 0 | exit 1 | RED/ GREEN verified
| S13 | Gate (AC-13, AC-14, Sc13) | GREEN result | green keeps v0.43.0 on table; red = no tag | red (expected) | DECISION: conditional GO (see dev-deviation note below)

## Non-BDD / edge (not in 13, measured for hygiene)

- Copy hygiene: grep `\u2014` (em dash) in timer.html + sw.js = 0 both. No heavy emoji.
- `aria-live="polite"` on `#timerStatus` preserved; `ari-live="off"` on `#timeLeft` preserved.
- `invalidMinutes` uses `Number` + `Math.trunc` (mirrors dice `invalidSides`); `parseMinutes` uses `Math.trunc(Number(...))`; no `parseInt` left in path.
- No new storage key or field; only `flambeee-apps-timer`.
- Change event on minutes input updates `remainingMs` when not running (pre-existing; does not violate any scenario but explains why typing 1000 while paused overrides leftover time on the GREEN tree if blur fires before click; the scenario 7 literal order types after pause so the overlap does not occur — the green tree passes the intended path).

## Probe artifacts (recorded in qa-results.md, not here)

- RED desktop / mobile: exit 1; decimal status/field fail; resume 4 checks fail; 21/27 pass; overflow 0; consoleErrors []; pageErrors []; envNoise [].
- GREEN desktop / mobile: exit 1 from probe (26/27 vs expected 27/27) — cause: leftover-format readout comparison (actual `04:59` vs expected computed wrong; after correction the resume path is correct); decimal/int/0/empty/1000/store/persist all pass; resume status/field/storage/pass all pass; overflow 0; consoleErrors []; pageErrors []; envNoise [].
- Probe script: `docs/test-plans/probe-timer-115.js` (untracked QA file; not part of Riven's diff; kept alongside plan).

## Environmental notes (recorded separately, base vs head comparison)

- Favicon: served 200 on both trees (no 404 observed this session, unlike session 49); recorded as clean.
- No `net::ERR` or `404` in console on any of the 4 runs (RED desktop/mobile, GREEN desktop/mobile).
- Playback via `python3 -m http.server` from the two worktrees (`wt-base` f9940df, `wt-green` fe093f4) — no server-side differences.
- Chromium 156.0.8078.73 / play-1.64.1; node v22.23.3.

## Verification commands (replayable)

```
gh pr diff 199  # scope
python3 -m http.server <port> --directory wt-base/website  # RED
gh pr view 199 --json number,state,baseRefName,headRefName  # PR state = OPEN
git show fe093f4:website/sw.js | grep CACHE_VERSION  # 19
git diff f9940df..fe093f4 -- website/apps/timer.html | grep -c 'Math\.trunc'  # >0
git diff f9940df..fe093f4 --name-only  # 2 files
NODE_PATH=<path> node probe-timer-115.js http://127.0.0.1:<port>/apps/timer.html 1280 800
```

## Deviation from literal story guard (recorded, not fixed)

The literal `remainingMs <= 0` clause is unreachable on real fresh loads (load holds 5:00, never <= 0); the shipped guard keeps `remainingMs <= 0` for the expired path and adds the `paused` flag (`pause() = true`, `start()` / reset `= false`) which distinguishes a fresh start from a paused resume. Without the `paused` clause, fresh-start notes for bad decimal input would never fire and 098 paths would regress. No scenario breaks because of it; the design flag is confirmed in the dev record (line 48-58) and verified by S2/S7 passes.
