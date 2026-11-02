# Test plan: Story 114 — Tally floor at 0 with status note (Session 49)

**Story:** `docs/stories/114-tally-floor-session49.md` (12 BDD scenarios, AC-1..AC-14).
**Pattern model:** Story 098 (timer) / Story 112 (dice) status-note shape.
**Expected note text (verbatim):** `Count is at 0. Nothing to remove.`
**Storage key:** `flambeee-apps-tally`, shape `{label, count}` only.
**CACHE:** `website/sw.js` line `var CACHE_VERSION = 17;` to `18`; precache line `  './apps/tally.html',` byte-identical.
**Proof bar:** static serve, real clicks, desktop 1280x800 + mobile 375x667, overflow 0 both, zero page-attributable console errors both, RED (exit 1) on pre-change tree then GREEN (exit 0) on merged tree.

## Floor probe (node + playwright-core + /usr/bin/chromium, real clicks)

Probe: `s49qa/probe.js`. Usage: `node probe.js <url> <width> <height>`.
Exits 0 when all cases pass, 1 otherwise. Prints one JSON line per case plus a summary line
(summary, overflow, consoleErrors vs envNoise, storage readout).

Setup per case: fresh context storage state (cleared or seeded), `reload`, then real
`locator.click()` steps. The status element `#tallyStatus` is read with a tolerant helper
(missing element reads as `null`, which fails any note expectation on the RED tree).

| # | Case | BDD / AC | Steps | Expect (GREEN) |
|---|---|---|---|---|
| 1 | minus-at-0 | Sc 2 / AC-2 | clear storage, reload, click minus once | count `0`, status = note verbatim, storage `{label:"",count:0}` |
| 2 | three-minus | Sc 2 / AC-2 | clear, reload, click minus x3 | count `0`, note shown |
| 3 | seeded-minus-3-reload (RED anchor) | Sc 3 / AC-3 | seed `{label:"",count:-3}`, reload, no clicks | count `0` (RED tree: stays `-3`) |
| 4 | plus-minus-plus | Sc 4 / AC-4 | clear, reload, click plus, minus, plus | count `1`, no note on valid steps |
| 5 | reset-from-2 | Sc 5 / AC-5 | clear, reload, plus x2, reset | count `0`, no note |
| 6 | note-clears-on-plus | Sc 6 / AC-6 | clear, reload, minus (note on), plus | count `1`, status empty |
| 7 | note-clears-on-reset | Sc 6 / AC-6 | clear, reload, minus (note on), reset | count `0`, status empty |
| 8 | plus-from-0 | Req / AC-4 | clear, reload, plus | count `1`, no note |
| 9 | label-persist | Req / AC-7 | clear, reload, type label `Cups of water`, plus x2, reload | label line + field `Cups of water`, count `2` |
| 10 | storage-shape | Sc 7 / AC-7 | after floor + plus + reset paths, reload | only key `flambeee-apps-tally`, parsed keys exactly `[count,label]` |
| 11 | owner-record | Sc 1 / AC-1 | inspect dev record | names Riven as single code owner (app file + CACHE bump) |
| 12 | cache-ownership | Sc 8 / AC-8 | `git diff` base..head for `website/sw.js` | version line 17 to 18 only; `./apps/tally.html` precache line present both trees, byte-identical |
| 13 | scope-guard | Sc 9 / AC-9 | `git diff --stat` base..head | at most `website/apps/tally.html` + one `sw.js` line; no other app/game/schedule/checker diff |
| 14 | desktop-proof | Sc 10 / AC-10 | full probe at 1280x800 | exit 0, overflow 0, zero page-attributable errors |
| 15 | mobile-proof | Sc 11 / AC-11 | full probe at 375x667 | exit 0, overflow 0, zero page-attributable errors |
| 16 | release-gate | Sc 12 / AC-13 | proof bar result | green keeps v0.42.0 on table; red/slip means no tag |

## Edge cases (beyond the 12 scenarios)

| # | Case | Steps | Expect (GREEN) |
|---|---|---|---|
| E1 | seeded-large-negative | seed `{label:"",count:-999999}`, reload | count `0` |
| E2 | seeded-non-integer | seed `{label:"",count:2.7}`, reload | count `2` (truncation preserved, as today) |
| E3 | seeded-negative-decimal | seed `{label:"",count:-2.7}`, reload | count `0` (negative clamps after trunc) |
| E4 | rapid-minus | clear, reload, 10 rapid minus clicks | count `0`, note shown |
| E5 | rapid-plus-then-minus | clear, reload, 5 rapid plus then 5 rapid minus | count `0` |
| E6 | seeded-garbage | seed `not-json`, reload | count `0`, no crash, no page error |
| E7 | minus-never-writes-negative | minus at 0, read storage | stored count is `0`, never negative |
| E8 | copy-hygiene | read note text + page copy | plain punctuation, no em dashes, no heavy emoji |

## RED run (pre-change tree, must exit 1)

```
git worktree add --detach s49qa/wt-base main
python3 -m http.server 8941 --directory s49qa/wt-base/website
node s49qa/probe.js http://127.0.0.1:8941/apps/tally.html 1280 800    # expect exit 1
node s49qa/probe.js http://127.0.0.1:8941/apps/tally.html 375 667     # expect exit 1
```

Required RED evidence: per-case measured values; seeded -3 reload stays `-3`;
minus clicks reach `-1/-2/-3`; no status element exists; console-error split recorded.

## GREEN run (Riven's branch head, must exit 0)

```
git worktree add --detach s49qa/wt-green <riven-head-sha>
python3 -m http.server 8942 --directory s49qa/wt-green/website
node s49qa/probe.js http://127.0.0.1:8942/apps/tally.html 1280 800     # expect exit 0
node s49qa/probe.js http://127.0.0.1:8942/apps/tally.html 375 667     # expect exit 0
git diff <base>..<head> --stat                                        # scope guard
grep -n CACHE_VERSION s49qa/wt-green/website/sw.js                    # reads 18
```

## PR review

`gh pr view <n>`, `gh pr diff <n>`, then `gh pr review <n> --approve` (or request-changes).
Auth is jakepi-bot, so a formal approval may be blocked; if blocked, post findings as a
PR comment review instead and record that in qa-results.md.
