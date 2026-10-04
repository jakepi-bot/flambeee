# Flambeee Product Roadmap

## Vision

Flambeee builds snackable, instantly-playable web games. No downloads, no signups, no friction. Open source, community-driven, fun first.

## Current State

- **v0.26.0** — Cinder normalizes the character record once on load (shipped 2026-10-04)
  - Story 056 (P1, corrective, helper + call site): closes the character-record half of the same defect class Story 053 closed for the day record. `loadSave()` (`src/cinder.html:827`) returned the raw `JSON.parse` product to every stat helper, every shop gate and the bank, with no shape check. Six measured defects, all silent (none threw): **A** `gold` as a string made every affordability gate return false forever (shop, inn, bank) with no on-screen error; **C** `level: null` loaded a hero with `attack=0 defense=0 maxHp=0`; **G2/G3** string `weapon`/`armor` ids matched nothing under the strict `===` in `WEAPONS.find(...)`/`ARMOR.find(...)`, so gear bonuses vanished silently; **H1/H2** `hp` loaded as -50 or as 1e9 against a max of 26. Fixed with one new pure helper `normalizeCharacterRecord(raw)` called once at the `init()` load call site (`character = normalizeCharacterRecord(loadSave())`), mirroring `normalizeDayRecord`. `loadSave()` itself byte-identical and still the raw reader; `level` floored at 1; `weapon`/`armor` coerced to finite integers; `hp` clamped to `[0, maxHp]` after `maxHp` normalizes; `name` trimmed to 20 chars; `attack`/`defense` pass through untouched (measured dead: two write sites, zero read sites). **Pure: no new persisted field, no write on the load path, stored shape unchanged at 14 keys in order.** All 14 frozen functions and the three tables byte-identical to v0.25.0 by content extraction. Defect E (unreadable storage silently starting a new game) is **explicitly not fixed here** and is routed to Story 058.
  - Integration: ownership named before dev started per the Story 048 protocol (`flambeee-team/briefs/PARENT-RULINGS-session28.md`, 09:47). Unlike Sessions 23/24/27, the helper and its call site went to **one owner**, which made overlap impossible by construction rather than by luck. PR #115, commit `1d42173`; Riven owned PR #114 (`website/sw.js` line 21, `CACHE_VERSION` 3 to 4, one line) and was never given `src/cinder.html`.
  - A real defect was caught in the PR before merge: Kai's `toInt` used `typeof value === 'number' ? ... : 0`, which discards a numeric string instead of reading it, so `weapon: "2"` normalized to 0 rather than 2. Defects G2/G3 would have stayed broken **behind a green proof**, because the harness's identity-normalizer fallback prints the defect on the baseline and "INVARIANT HOLDS" for whatever the helper returns. Replaced with `toNum` feeding `toInt`. Found by reading the diff, not by reading a worker's status.
  - QA: **GO, 0 blocking defects, 13 checks.** Proof harness `flambeee-team/runs/session28-loadsave-repro.py` **extended in place** (distinct implementation count 1 across all three on-disk copies; the others are per-ref snapshot trees): **exit 1 against tagged v0.25.0** (10 in-scope defects reproduced, A C G2 G3 H1 H2 I1 I2 J1 J4) and **exit 0 against the merged commit `6ca46c5`** (0 unfixed). Re-run by the release job against the merged commit per Riven's closing instruction: v0.25.0 exit 1, merged exit 0. Real-Chromium Playwright QA, both builds, desktop 1280x800 and mobile 375x667, damaged saves seeded before load: well-formed save renders byte-identical on both builds at both viewports (`Ash | Lv.3 | HP 18/26 | ATK 9 | DEF 7 | Gold 40 | Bank 7 | Fights: 15` on v0.25.0 and on the candidate), and each defect fixed in the rendered DOM (`Gold abc` to `Gold 0`, `Lv.null` to `Lv.1`, `ATK 6` to `ATK 11`, `DEF 3` to `DEF 7`, `HP -50/26` to `HP 0/26`, `HP 1000000000/26` to `HP 26/26`). No page errors, no console errors, the fix is silent. Zero writes added: 2 writes on load on both builds, byte-identical (`flambeee-cinder-save` is the harness's own seed, `flambeee-cinder-day` is the pre-existing `checkDailyReset()` write), stored bytes unchanged.
  - Three non-blocking notes carried forward, none a release blocker: `hp: 0` renders "You are dead. Reviving..." at the inn under the clamp-to-0 ruling (self-heals next visit, and is a consequence of a parent ruling made before dev started, so the release notes must not describe it as new behavior); `normalizeCharacterRecord({})` returns a level-1 hero where `normalizeDayRecord` returns `null` (asymmetry recorded, real saves always carry `name` and `level`); `flambeee-team/` is gitignored, so the proof lives in the PR body plus untracked files.
  - Story 057 (P2, standing verification): website currency checker, two runs. Run 1 pre-release PASS (exit 0, heading v0.25.0, `cmp` exit 0, 5 Play links, checker blob unmodified). Run 2 post-release: heading **v0.26.0**. Cinder deploy mirror re-synced post-merge and verified byte-identical: `cmp` exit 0, sha256 `a18cbd1180ef770a00f465ccd9126019dceea751a1204a9d03ee837333554701` on both `src/cinder.html` and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. `CACHE_VERSION` bumped 3 to 4 on both `website/sw.js` and `share/Flambeee/sw.js` (`cmp` exit 0, sha256 `4f02856a34e7f7a517b3b0a0d56ca7a3ca4809bdad2331a86614ac2860be851f`), which is load-bearing: `sw.js:33` precaches `./games/cinder.html`, so without it a returning visitor is served the pre-056 shell from cache and the release reads as a no-op.
  - Story 058 (P3, decision record): records the unreadable-storage question across **both** records, with three options (silent new game, which is today's behaviour; a visible notice with play still allowed; refuse to start), and the related point that `normalizeDayRecord` returning `null` for a malformed record routes to the same new-game path. **No behavior change shipped.** Any option that adds a user-facing message needs CEO sign-off. Committed with Stories 056/057 in `b2e0842` (PR #113).
  - Deploy: `share/Flambeee/index.html` and `website/index.html` byte-identical (`cmp` exit 0, sha256 `b08877ac9f59603d3b61b1d520352b3652f0eefc3e15036e7b92e39aa5e20fce`).
  - Harness-defect record, kept because it is this team's recurring failure mode: five harness defects in Wave 1 and two more while proving Story 056, every one of which initially printed as product behaviour. Including a counter that printed three reproduced defects directly above `DEFECTS REPRODUCED: 0` and exited 0 because it only asserted on "did it throw" (A, C, E, G2 and G3 all exit 0; they are silent), and an assertion that would have failed a correct fix for `"abc"` gold. **A green exit from a proof script is a claim about the script, not about the product.**
  - Worker-health record: this session lost Quinn in Wave 2 and Scout in Wave 3 to the same failure (a turn ending on a progress statement, "Writing the stories now", with no artifact written), and Kai died mid-phase at 15m32s leaving an uncommitted working tree. Riven delivered both PRs and the peer review. Three sessions running, five workers lost. The detection method did not change and it still works: read the filesystem, not the status line.

- **v0.25.0** — Cinder normalizes the day record once on load (shipped 2026-10-02)
  - Story 053 (P1, corrective, helper + call site): closes the "which recorded run does this screen describe" family on its last unhardened surface, the record itself. The read surfaces were each hardened one at a time (Stories 044/047/050) to tolerate a corrupt or partial day record, but the **load** path that parses the stored record before any reader sees it had no equivalent normalization: `loadDayState()` returned the raw `JSON.parse` product, and only the individual read helpers were expected to survive it. A record written by an older build, hand-edited, or truncated mid-write reached the first reader with a shape no single reader owned; the empty-state/fallback behaviour held only because every reader duplicated its own guard, and a numeric leaf where text was expected still threw (`str.replace is not a function`). Fixed with one new pure helper `normalizeDayRecord()` that normalizes the record once into the documented shape `{ dayIndex, fightsUsed, innHealsUsed, quest, completedQuests }` (numeric day index, counters clamped to `MAX_FIGHTS_PER_DAY`/`MAX_INN_HEALS_PER_DAY`, filtered quest history, entry leaves coerced to strings), called once at the `init()` load call site (`dayState = normalizeDayRecord(loadDayState())`). Every read helper continues to work on the normalized record; no read helper's behaviour changes. **Pure: no new persisted field, no write on the read path, day record shape unchanged, `checkDailyReset()`, `computeQuestLogStreak()`, `computeRecentQuestEntries()`, `shouldShowWelcomeBack()` and `dayLabelForIndex()` byte-identical to v0.24.0.** Corrupt, partial, null, wrong-type and storage-unavailable inputs degrade to the existing empty state; same-day, next-day and long-absence flows render exactly as v0.24.0.
  - Integration: Story 053 put two devs on one file (`src/cinder.html`). Ownership named before dev started per the Story 048 protocol (Kai: new helper + proof; Riven: the one `init()` call-site line at `src/cinder.html:1454`). Ranges disjoint; PR #111 was re-cut mid-session to remove a stacked helper commit so the ownership invariant held. Merged candidate sha256 `eb0123587d502ee2efde6786075298c618ff5c156f201a8e78144baf6c1c032b`, matching the value QA tested against. **Merged after PR #110 (helper first) so `normalizeDayRecord` resolves; merged alone the call site is a `ReferenceError` by design.**
  - QA: parent-executed (the Wave 3 workers returned no artifacts; recorded honestly in `dev-results.md` and `qa-results.md`). Kai's pure-function proof **22 checks, exit 0** against the merged candidate, and **exit 1 against tagged v0.24.0** reproducing the throw and the out-of-range counter renders (`fightsUsed 99 -> Fights: -84`, `fightsUsed -5 -> Fights: 20`), so the green run is a measurement, not a tautology. Real-browser Chromium isolation (Playwright) **32 checks, 0 failed** across desktop 1280x800 and mobile 375x667: v0.24.0 throws `str.replace is not a function` on the numeric-objective seed and renders negative/over-cap counters; the candidate renders the quest log cleanly and clamps the counters. Frozen five byte-identical to v0.24.0 by extraction (`checkDailyReset` `37790ab4ae2d`, `computeQuestLogStreak` `21f0acfca50a`, `computeRecentQuestEntries` `6d97619ae81d`, `shouldShowWelcomeBack` `667559cd7d16`, `dayLabelForIndex` `ccccd52dc064`). No-write check: zero key writes across a corrupt load-and-render; both localStorage keys byte-identical. No blocking defects. Test plans PR #112.
  - Story 054 (P2, standing verification): website currency checker, two runs (pre-release and post-release) plus the Cinder deploy-mirror check, retargeted to v0.25.0. Run 1 green at session start (exit 0, heading v0.24.0, `cmp` exit 0, 5 Play links, checker blob `9b1058b1` unmodified since v0.19.0). Run 2 after the What's New update: heading **v0.25.0**. Cinder deploy mirror re-synced post-merge and verified byte-identical: `cmp` exit 0, sha256 `eb012358` on both `src/cinder.html` and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`.
  - Story 055 (P3, decision record): records the Cinder record family as closed under proofs (streak number, recent-quests list, day labels, reload guard, load normalization), names the one remaining candidate surface (welcome-back **suppression** on a later visit on a different UTC day inside the same gap, carried from the Story 042 limitation), and states plainly that closing it requires a persisted field and therefore a Story 039 decision-record amendment plus CEO sign-off. Decision recorded: **do not implement this session.** No code.
  - Deploy: `share/Flambeee/index.html` and `website/index.html` byte-identical (`cmp` exit 0, sha256 `a8ff79ec`).
  - Open item, recorded not hidden: `memory/flambeee-community.md` logging has regressed (newest entry 2026-08-22). The community-check crons are not appending and are flagged to the CEO; this session did not hand-edit the log. The Session 26 recommendation to split Wave 3 (dev+QA) from Waves 4-6 (release) into separate jobs remains a cron change this job may not make.

- **v0.24.0** — Cinder quest log day labels read the record's own anchor (shipped 2026-09-29)
  - Story 050 (P1, corrective): the last surface of the "which recorded run does this screen describe" family. `renderQuestLog()` rendered each recent entry through `dayLabelForIndex(entry.dayIndex)`, which computed its diff against `getDayIndex()` (today) instead of the anchor the list and the streak number already used. On a stale record the list was correctly non-empty (Story 047) and the streak number was correct (Stories 044/047), but every label was shifted by the whole absence: a player back after 30 days whose last recorded quest was completed on day D saw "Current streak: 1 day" above "30 days ago: <last quest played>". Fixed with the Story 044/047 pattern: `dayLabelForIndex()` now derives from the record's last recorded play day (`lastPlayIdx`), the same anchor `computeQuestLogStreak()` and `computeRecentQuestEntries()` use, and its one call site at `renderQuestLog()` passes it through. **No new persisted field, no write on the read path, day record shape unchanged, `checkDailyReset()`, `computeQuestLogStreak()`, `computeRecentQuestEntries()` and `shouldShowWelcomeBack()` byte-identical to v0.23.0**, list contract unchanged (most recent first, cap 5, same titles, same empty-state line), `day N` fallback preserved.

  - Story 051 (P2, verification-shaped, **no code change**): the Wave 1 hypothesis that `daysAway = gapDays - 1` was off by one is **withdrawn**. Quinn read `computeAwayWindow()` against the Story 039 D3 decision record and Story 040 requirements 1 and 4: `daysAway` is the count of fully missed UTC days (exclusive at both ends), it is consistent with the `questsMissed` loop, and it satisfies `questsMissed <= daysAway`. Shipped as a proof with the definition recorded: **`daysAway` counts fully missed UTC days; it is not `gapDays` (elapsed) and it is not the Story 050 label (record-relative).** Proof sweeps gapDays 0, 1, 2, 3, 7, 14, 15, 16 and 30, asserting `daysAway`, `questsMissed`, `shouldShow` and the sentence; pointed at a `daysAway = gapDays` mutant it fails with exit 1, so the green run is a measurement, not a tautology.
  - Integration: Stories 050 and 051 both touched `src/cinder.html`. Ownership was named before dev started (Riven: `dayLabelForIndex()` and its one call site; Kai: Story 051 proof script only, no game-file change). Ranges disjoint, verified independently by extraction rather than from PR text.
  - QA: Scout harness against the merged candidate, **36 checks (Story 050) + 54 checks (Story 051)**, plus **24 real-browser Playwright checks** across desktop 1280x800 and 375x667 (stale record, same-day control, gapDays=2 panel, Back to Town tap, overflow, onclick, pure read, page errors). Kai's Story 051 proof re-run on the merged candidate: 54 checks, exit 0. Frozen-function extraction vs v0.23.0: five functions IDENTICAL (`checkDailyReset` 37790ab4ae2d, `computeQuestLogStreak` 21f0acfca50a, `computeRecentQuestEntries` 6d97619ae81d, `computeAwayWindow` 6d29b6d58788, `shouldShowWelcomeBack` 667559cd7d16). Pre-fix v0.23.0 `dayLabelForIndex` fails all anchor-relative cases (`30 days ago` / `31 days ago` / `33 days ago`), isolating the fix. No blocking defects. Test plans PR #107.
  - Story 052 (P3, standing verification): website currency checker, two runs (pre-release and post-release) plus the Cinder deploy-mirror check. Run 1 green at session start (heading v0.23.0, `cmp` exit 0). Run 2 after the What's New update: heading **v0.24.0**. Cinder deploy mirror re-synced post-merge and verified byte-identical: `cmp` exit 0, sha256 `7616c7fd` on both `src/cinder.html` and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Checker script unmodified.
  - Deploy: `share/Flambeee/index.html` and `website/index.html` byte-identical (`cmp` exit 0).
  - Open item, recorded not hidden: the cross-surface presentation question (the welcome-back panel's fully-missed-days count vs the quest-log label's record-relative day for one gap) is a **CEO product call**. Both numbers are correct on their own terms. Default option (a), leave as is, **confirmed by the CEO 2026-09-29**. No code change while it is open.

- **v0.23.0** — Cinder quest log recent-quests list reads the recorded history (shipped 2026-09-27)
  - Story 047 (P1, corrective, both devs): the quest log's **recent-quests list** printed an empty list beneath a live streak on the first load of any stale day record. The list read the post-reset `dayState.completedQuests` (`src/cinder.html:627`) while the streak number read the pre-reset anchor (`computeQuestLogStreak(dayState, questLogAnchor)`), and `checkDailyReset()` rebuilds `dayState` wholesale with `completedQuests: []` before the log opens. A proof built from the shipped code reproduced the contradiction on 4 of the 5 seeded states (stale by 1, 3, 6, and 30 days); the same-day reload was correct and served as the control. A second defect on the same path: a `null` entry in `completedQuests` threw at the list `map`. Both fixed with the Story 044 pattern: one new pure-read helper `computeRecentQuestEntries(anchor, fallback)` sourced from `questLogAnchor`, and one call-site change in `renderQuestLog()`. **No new persisted field, no write on the read path, day record shape unchanged, `checkDailyReset()` and `computeQuestStreak()` byte-identical to v0.22.0.** The list's rendering contract is unchanged: most recent first, cap 5, same relative day labels, same empty-state line.
  - Integration: Stories 047 and 048 again put two devs on one file (`src/cinder.html`). Kai owned the read-path proof and the pure-read helper; Riven owned the render call site and the docs spec. Both branches carried the identical `src/cinder.html` blob (`734def4b`), so the parent merged one hunk and kept the change single-owner, exactly the hazard Story 048's protocol names.
  - Story 048 (P2, docs-only): `docs/integration-ownership-protocol.md`, one page, formalises the rule the last two sessions improvised. One owner per helper and per call-site line named before dev starts; exact line range in each PR body against the base commit; overlap not mergeable until re-cut and recorded; one required pre-merge check by the non-owning developer running the D1/D2 scan on the **merged** candidate; separate worktrees per dev. No code, no script, no hook, no CI job, no linter rule.
  - QA: Scout harness **36/36 pass, exit 0** against the merged candidate (node sandbox), **24/24 pass, exit 0** in real Chromium at desktop and 375x667; the pre-fix build failed 11 sandbox checks and 2 browser checks, isolating the fix. Kai's independent proof `src/kai-story047-questlog-readpath-proof.py` **27/27, exit 0** (7 failures against shipped v0.22.0). No writes on the read path, frozen functions byte-identical, D1/D2 scans clean. Test plans PR #102.
  - Story 049 (P3, standing verification): two-run currency checker. Run 1 before release green (exit 0, heading v0.22.0, `cmp` exit 0, 5 Play links). Run 2 after the What's New update and live sync green (exit 0, heading **v0.23.0**). Cinder deploy mirror synced post-merge and verified byte-identical: `cmp` exit 0, sha256 `e3f0ef69` on both `src/cinder.html` and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Checker script unmodified.

- **v0.22.0** — Cinder quest log tells the truth on a return day (shipped 2026-09-25)
  - Story 044 (P1, corrective): the quest log and the welcome-back panel could contradict each other on the same screen. `renderQuestLog()` took its number from `computeQuestStreak(dayState)`, which anchors on today or yesterday, and the load path runs `checkDailyReset()` before the log can be opened. That reset rebuilds the day record wholesale with `completedQuests: []`, so on a return day the log read 0 while the panel on the same screen read "Your streak survived." The fix is one new pure-read helper, `computeQuestLogStreak(dayState, rawDayState)`, that derives the run from the loaded (pre-reset) record's `completedQuests` history, anchored on the last recorded play day, exactly as `computeAwayWindow()` anchors its window. The helper is called with `questLogAnchor`, an in-memory `let` captured from the loaded record at init before `checkDailyReset()`, so the log and the panel describe one window and cannot disagree. When `rawDayState` is unavailable the helper returns 0 rather than reading the rebuilt record. **No new persisted field, no write on the read path, day record shape unchanged, `checkDailyReset()` and `computeQuestStreak()` byte-identical to v0.21.0**, no economy change, no new hub row, no banner, no notification, no push, no permission prompt, no install nag, no inline onclick.
  - Story 045 (P2, verification-shaped): proved the reload-guard behaviour on a record stale by exactly one day and on a record stale by 3+ days. **No code defect found; the behaviour is correct and the public claim was corrected.** The reload is quiet in both cases, closed by the daily reset's own write stamping today on the first load (`gapDays === 0` on the reload), not by any additional guard. The narrower true statement was applied to the published v0.21.0 release notes, the roadmap, and the website What's New; the general promise was walked back to the one-day case it actually proves. Proofs: `src/kai-story045-reload-guard-proof.py`, ALL PASS (6 checks), exit 0.
  - Integration: Stories 044 and 045 again put two devs on one file (`src/cinder.html`). Kai built the streak source and the proofs; Riven wired the view and corrected the Story 045 copy. Both halves touched the same call-site line. Reconciled into one coherent change (PR #96): kept Kai's helper and the `questLogAnchor` call form, dropped Riven's out-of-scope `rawDayState` form, and dropped the post-reset fallback in the helper. Two QA blocking defects (D1 out-of-scope binding, D2 post-reset fallback) were found by Scout and fixed before merge.
  - QA: Scout harness **44/44 pass, exit 0** against the merged candidate; Kai's independent proofs **47/47 (Story 044) and 6/6 (Story 045), exit 0**. All four frozen functions (`checkDailyReset`, `computeQuestStreak`, `computeAwayWindow`, `shouldShowWelcomeBack`) byte-identical to v0.21.0 by rigorous extraction. Test plans PR #97.
  - Story 046 (P3, standing verification): two-run currency checker. Run 1 before release green (exit 0, heading v0.21.0, `cmp` exit 0, 5 Play links). Run 2 after the What's New update and live sync green (exit 0, heading **v0.22.0**). Cinder deploy mirror synced post-merge and verified byte-identical: `cmp` exit 0, sha256 `0dd0c010` on both `src/cinder.html` and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Checker script unmodified.

- **v0.21.0** — Cinder welcome-back summary corrected: honest streak line and one-time-per-gap guard (shipped 2026-09-22)
  - Story 042 (P1, corrective): closes both limitations Story 040 shipped and disclosed. (1) **The streak line.** `computeAwayWindow()` read the status from `computeQuestStreak(rawDayState)`, but `checkDailyReset()` rebuilds the day record wholesale with `completedQuests: []` when the stored index is stale, so the helper returned 0 and a player with an intact recorded run was told their streak was broken. The line now derives from the last recorded completion run in the loaded record's `completedQuests` history, anchored on the last recorded play day (the same anchor the window already uses for `daysAway` and `questsMissed`). Intact run including a single recorded day reads "Your streak survived."; a genuine hole before the last play day reads "Your streak is broken." (2) **The one-time guard.** The guard was `returnShown`, an in-memory flag for the life of the page, so a same-day reload re-showed the summary. It now also reads the loaded day record: on the first load of a stale day the pre-existing `saveDayState()` call inside `checkDailyReset()` stamps today into the record, so the reload finds the record already carries today and the panel stays quiet. **Scope of that claim (Session 24, Story 045): the guard covers the reload that lands on a record stale by exactly one day**, where `todayIdx === raw.dayIndex + 1`. A record already stale by more than one day (the normal state of a player who has been away) is closed by the daily reset's own write on the first load, which stamps today, so the reload finds `gapDays === 0` and the panel is not eligible. The panel is shown once per gap in both cases; no additional guard runs. Proven and recorded in Session 24, Story 045. Derived from existing state only. **No new persisted field, no write on the summary path, day record shape unchanged, `checkDailyReset()` and `computeQuestStreak()` byte-identical to v0.20.0**, no economy change, no new hub row, no banner, no notification, no push, no permission prompt, no install nag, no inline onclick.
  - Integration: Story 042 again put two devs on one file (`src/cinder.html`). Kai (PR #91) and Riven (PR #89) each independently solved both problems with their own helpers. Both were correct; merging both would have shipped two implementations of each fix. Reconciled into one coherent change (PR #92): kept Kai's `computeAwayWindow()` streak source (the value stays on the window object `renderWelcomeBack()` already consumes, so the view half needed no edit) and Kai's `shouldShowWelcomeBack()` gate, dropped Riven's two now-redundant helpers. QA proved the two guards behaviourally equivalent on every reachable input.
  - QA: **91 real-browser checks, 0 failed, exit 0, reproduced twice** against the merged artifact (Playwright, real Chromium, real taps at 375x667). Kai's independent node proof **47/47, exit 0** on the same file. A control run against the pre-042 build fails **exactly the four checks this release fixes**, which isolates Story 042 as the only behaviour change. Static scans find no forbidden writer calls or field names; both localStorage keys are byte-identical across the summary path; 22 negative cases (legacy records, 11 corrupt shapes, storage unavailable) load clean with no exception. Test plans PR #90.
  - Story 043 (P2, standing verification): the two-run currency checker. Run 1 before release green (exit 0, heading v0.20.0, `cmp` exit 0, 5 Play links). Run 2 after the What's New update and live sync green (exit 0, heading **v0.21.0**). The checker also caught the real post-merge pre-tag drift (heading named v0.21.0 while the tag did not exist yet, exit 1), which is exactly the drift class Story 041 exists to catch. Cinder deploy mirror synced post-merge and verified byte-identical: `cmp` exit 0, sha256 `e48a1040` on both `src/cinder.html` and `/home/jake/.openclaw/workspace/share/Flambeee/games/cinder.html`. Checker script unmodified (blob `9b1058b1`, identical to v0.19.0).
  - Deploy: `share/Flambeee/index.html` and `website/index.html` byte-identical (`cmp` exit 0, sha256 `fd30f1e5`).
  - Honest limitation, recorded not hidden: BDD Scenario 6 in its literal form (a later visit on a **different UTC day** inside the same gap) cannot be suppressed with zero persisted state, because the reset's write stamps today on the first load and that write is what closes the window. A literal multi-day suppression would need a **Story 039 decision-record amendment plus CEO sign-off** (requirement 9). The same-day reload case (Scenario 5) holds and is proven in both the node sandbox and the browser.
  - QA: no blocking defects.

- **v0.20.0** — Cinder welcome-back return summary (shipped 2026-09-20)
  - Story 039 (P1, docs-only): the away-time decision record. Decision: **no offline resource accrual**. Gold, XP, quest progress and boss fights do not accrue while the player is away, daily fights do not bank or stack, and the fight economy is untouched. Instead Cinder acknowledges the absence with a return summary (pure presentation). Rationale recorded: the September 2026 genre check treats save continuity as table stakes while idle accrual belongs to a game with an idle loop, accrual cannot be additive (it must mutate gold/XP/quest state, the class of change byte-safety exists to slow), accrual is a balance change by definition and has no CEO sign-off, and paying for missed days weakens the daily-return loop. Satisfies the prerequisite Session 21 required before any away-time code.
  - Story 040 (P1, retention): the welcome-back return summary. When a player returns after at least one fully missed UTC day, Cinder shows a one-time boxed-menu summary: days away, quests missed, streak status (stated, never implied), and a pointer to today's quest, with Back to Town and a second row into today's quest. Pure presentation: reads existing state, writes nothing, adds **no new persisted field**. The gate helper `computeAwayWindow(rawDayState, todayIdx)` takes the day record as loaded **before** `checkDailyReset()` replaces it wholesale (the flagged defect hazard: a post-reset read reports today, not the last play day). One-time guard is in-memory for the page, so a same-day reload shows it again and a back-navigation does not. No economy change, no notifications, no push, no permission prompt, no install nag, no new hub row. PR #83, proof PR #85.
  - Story 041 (P2, standing verification): the currency checker is now a **two-run release step**. Run 1 before release proves the entering state is current; run 2 after the What's New update and live sync proves the released version is named and the mirror is still byte-identical. Both recorded in `release-chain.md` with command, exit code and auditable output. Closes the Session 21 gap where the checker ran pre-release only and the post-release website drift reached compliance review instead of the checker. Checker script unmodified (blob hash `9b1058b1`, identical to the v0.19.0 shipped version).
  - QA: 167 real-browser checks, 0 failed, exit 0, reproduced twice against the pinned commit; Kai's independent node proof 43/43, exit 0. Coverage includes the no-write proof (zero localStorage writes on the summary path, both stored keys byte-identical), the reset hazard proven directly, both streak branches exercised, 12 corrupt-input cases with no exception, a real tap at 375x667, and a control run against the pre-040 build that isolates Story 040 as the only difference. Test plans PR #86.
  - Deploy: `share/Flambeee/games/cinder.html` synced byte-identical to `src/cinder.html` (`cmp` exit 0, sha256 `dde7125b`); `share/Flambeee/index.html` and `website/index.html` byte-identical (`cmp` exit 0, sha256 `b9a8b7c8`).
  - Honest limitations, recorded not hidden: a same-day page reload re-shows the summary (in-memory guard, accepted by the gate spec and Story 040 open question 1); the streak line normally reads "broken" on a real return because `checkDailyReset()` rebuilds the day record, so both branches exist and both are exercised while preserving cross-day history across the reset stays a separate decision.
  - QA: no blocking defects.

- **v0.19.0** — Cinder install-aware app-icon badge (shipped 2026-09-18)
  - Story 037 (P1, retention): installed Cinder now carries a PWA app-icon badge that mirrors today's quest. One guarded helper, `syncAppBadge()`, feature-detects `navigator.setAppBadge` / `navigator.clearAppBadge`, derives the value purely from `getQuestState()` (`1` while today's quest is not `completed && rewarded`, `0` otherwise), wraps the call in `try/catch` plus `.catch(function () {})`, and no-ops cleanly when the API is absent (Firefox, iOS Safari, non-installed contexts). Wired at three points: end of `init()`, end of `completeQuest()` after the reward is paid, and after the daily-reset branch in `checkDailyReset()`. Pure mirror: no new save field, no `localStorage` write from the badge path, no notifications, no push, no permission prompt, no install nag, no new hub row. Kai proof `src/kai-story037-badge-proof.py` 34/34 PASS exit 0 (the proof caught a real first-pass defect: a rejected promise escapes `try/catch`, so the explicit `.catch` was added). Scout re-derivation + real Chromium (Playwright) 24/24 checks PASS, exit 0; save and day record byte-identical across the badge path (`flambeee-cinder-save` 175 chars, `flambeee-cinder-day` 143 chars); negative run with the API deleted produced 0 console errors and the quest still completed. PR #80.
  - Story 038 (P2, standing verification): new repeatable checker `scripts/verify-website-currency.sh` resolves the latest tag from `git ls-remote --tags origin` at run time (not hardcoded, so it survives v0.19.0) and checks live-vs-mirror `cmp` byte-identity, the What's New heading, no em dashes or heavy emoji, real clickable Releases/Blog anchors, and relative `games/*.html` Play links whose targets exist. First real run: all checks PASS, exit 0. No fix path triggered, no website change needed. PR #79. QA test plans PR #81.
  - Deploy: `share/Flambeee/games/cinder.html` synced byte-identical to `src/cinder.html` (`cmp` PASS); `share/Flambeee/index.html` and `website/index.html` remain byte-identical (no website change this release).
  - QA: no blocking defects. Two informational notes: the double `setAppBadge(1)` on load is the designed idempotent behaviour (both hooks compute 1); the live mirror sync is the parent deploy step, not a PR defect.

- **v0.18.1** — Cinder recent-quests / quest-streak view (shipped 2026-09-15)
  - Story 035 (P1, retention): the Cinder town hub now has a Quest Log (row 9). `renderQuestLog()` shows the last 5 completed quests (most-recent-first, `.slice(-5).reverse()`) and the current streak via the pure `computeQuestStreak(dayStateRef)` helper. Additive backwards-compatible `completedQuests` array on `dayState`, defaulted `[]` in `ensureQuestState()`/`checkDailyReset()`/`init()` and guarded with `Array.isArray`, so legacy saves (no field) and corrupt values load clean with no loss. Append happens exactly once per completed-and-rewarded quest under the payout-once gate. View is a pure read (Kai pure-read proof PR #76, 15/15 node assertions + static scan exit 0); delegated `data-action` tap handler, mobile-safe boxed-menu, no inline onclick, no horizontal overflow (Playwright 375x667 PASS). Backwards-compat backfill verified: level/gold/XP/wins unchanged. PRs #75 + #76 + #77.
  - Story 036 (P2, standing verification): What's New names the true latest release against `git ls-remote --tags origin` (v0.18.0 at verify time), live site and repo mirror byte-identical (`cmp` PASS), Releases + Blog real clickable links. Passed; no fix path. Website What's New updated to v0.18.1 for this release; game mirror (`share/Flambeee/games/cinder.html`) synced byte-identical.
  - QA: 035 streak proof 15/15 + static scan PASS; browser (legacy load, quest log render, no overflow, Back to Town) PASS; 036 website checks all PASS. No blocking defects.

- **v0.18.0** — Cinder daily-return preview + website accuracy verified (shipped 2026-09-13)
  - Story 033 (P1, retention): Cinder's completed quest view now names tomorrow's objective and tells the player to come back after midnight. `renderQuestNextDayBlock()` renders only when today's quest is completed AND rewarded; tomorrow's objective is `determineQuestForDay(getDayIndex() + 1)`, a pure read with no save writes, no state mutation, no balance/mechanics change. In-progress view byte-identical; block flows inside `boxed-menu` (mobile-safe, Back to Town tappable); copy plain punctuation, no em dashes, no emoji. Kai's pure-read proof PASSed (exit 0). PRs #72 + #73.
  - Story 034 (P2, standing verification): confirmed the website's What's New names the true latest release (v0.17.1) with an accurate summary, and the live site and repo mirror are byte-identical. Verification passed; no fix path triggered.
  - QA: Story 033 6/6 scenarios PASS; Story 034 4/4 scenarios PASS (live + mirror cmp PASS); deploy cinder mirror synced byte-identical.

- **v0.17.1** — Cinder boss-day balance: boss fights actually appear (shipped 2026-09-11)
  - Story 032 (P1, follow-up): boss-day quest was RNG-blocked — `startCombat()`'s random capped pool could exclude every boss, making the boss quest unadvanceable. Boss days now field boss-tier monsters only (id >= BOSS_TIER); too-weak players get the weakest boss as a stretch fight (Run available); non-boss days byte-for-byte unchanged. Rewards/rotation/payout untouched. CEO delegation 2026-09-11 recorded as the Story 031 sign-off. QA harness 6/6 (200x15 simulated boss days, 100% boss-only; normal-day equivalence). PR #69.
  - Retroactive release-note cleanup (Story 030 open item): all 18 GitHub release titles + 10 bodies scrubbed of em dashes / stray flame emoji back to v0.1.0.
  - QA: node --check PASS; scout-qa-session19-032.py 6/6; deploy copy synced byte-identical.

- **v0.17.0** — Website accuracy + brand text cleanup (shipped 2026-09-11)
  - Story 029 (P0): Website "What's New" now reads the true latest release (v0.16.0, Cinder quest polish + Play today) instead of stale v0.15.0; summary accurate, no invented features; Releases/Blog links preserved
  - Story 030 (P1): no-AI-tells cleanup across all external copy. BLOG.md: 37 em dashes removed (all posts, back to session 2), heavy/decorative emoji stripped, flame kept as single one-per-post sign-off. Website title + About: em dashes removed, plain punctuation. CEO tone + dry humor preserved
  - Story 031 (P2): boss-day F1 decision formally recorded (conscious stretch goal, rotates next day, largest bonus, no balance change; see `docs/stories/031-cinder-boss-day-stretch-decision-record.md`)
  - QA: 0 em dashes in website + blog, accurate What's New, no invented features, no layout regression; mirror synced byte-identical (cmp pass)

- **v0.16.0** — Cinder quest polish + website Play today (shipped 2026-09-08)
  - F2: completed quest tail reads `[Done]` (matches spec) instead of `[COMPLETE]`; detail view unchanged; in-progress tails unchanged
  - F1 (recorded): boss-day quest stays a conscious stretch goal for low-level players (rotates away next day, largest bonus); no balance change
  - F3 (confirmed): gold quest counts combat gold only, matching its "from combat" text; treasure gold intentionally excluded
  - Website: "Play today" callout below Game of the Week, deterministic UTC-day rotation (Cinder quest / Wordfire word), relative play link, real GitHub community link, mobile-safe, graceful degrade
  - QA: 027 11/11 (repo + live after deploy sync), 028 28/28 (real clicks + 375px/320px mobile); no blocking defects

- **v0.15.0** — Cinder daily quest + website Game of the Week (shipped 2026-09-06)
  - One deterministic quest per UTC day in Cinder (slay/gold/boss), same objective for every player, no rerolls
  - No-consecutive-repeat quest rotation (verified 2M days); progress from real combat outcomes
  - Bonus XP/gold paid exactly once; state persists until UTC reset; existing-save + private-mode safe
  - "Today's quest" town-hub row 8 + quest detail view, tap support via v0.13.1 event delegation
  - Website: Game of the Week banner above the grid, ISO-week rotation over all 5 games, relative Play link, mobile-safe, graceful degrade
  - QA: 28/28 browser passes (real taps + mobile viewport), 12/12 logic passes, no blocking defects; 2 minor findings carried

- **v0.14.0** — PWA packaging: install like an app, play offline (shipped 2026-09-04)
  - Manifest + 192/512 icons, standalone display, theme-color navigation
  - Service worker precaches the whole shell (hub, 5 games, word list), cache-first, offline-capable
  - Install control on the hub, native prompt only on explicit tap, zero layout gap when hidden
  - No game file changes, no build step; localStorage stats untouched

- **v0.13.1** — Cinder menu + combat patch (shipped 2026-09-01)
  - Player-reported fix session: issues #45 + #46 (BigFunger, within the hour post-launch)
  - Menu tap/click fix: event delegation replaces 28 unreachable inline handlers; mobile play restored
  - Combat routing fix: fight inputs reached the wilderness handler; combat was unwinnable by any input
  - QA bar raised: real browser taps on every menu row are now mandatory test proof
  - README lists all 5 games with flambeee.com links; repo About/description + homepage set

- **v0.13.0** — Cinder: BBS-Style Text RPG (shipped 2026-08-30)
  - Single-player BBS door game: town hub, wilderness combat, XP/leveling
  - 15 fights/day, UTC-midnight reset, localStorage persistence
  - 15 monsters, 20 events, 8 weapon/armor tiers, 10 levels, tavern rumors
  - Death loses carried gold, bank is safe. Built from community issue #41
  - Website: 5th game card + detail modal + What's New

- **v0.1.0** — Minesweeper (shipped 2026-07-29)
  - 3 difficulty levels (Easy 9x9, Medium 16x16, Hard 30x16)
  - Mobile support (long-press to flag, flag mode toggle)
  - First-click-safe, flood fill, win/lose detection, timer
  - Single-file HTML/CSS/JS, no dependencies

- **v0.2.0** — Game Hub + Simon (shipped 2026-07-31)
  - Game hub launcher at index.html with game cards
  - Simon memory game with 4 pads, Web Audio tones, speed scaling
  - Colorblind accessibility (shape symbols)
  - Keyboard support (QWAS)
  - localStorage best score persistence
  - BDD stories, test plan, roadmap docs added

- **v0.3.0** — 2048 (shipped 2026-08-04)
  - Merge-puzzle, 4x4 classic + 5x5 Hard, arrow/WASD keys, swipe
  - localStorage best score, win/game-over overlays, Game Hub card

- **v0.4.0** — 2048 Polish Pass (shipped 2026-08-07)
  - Brand palette alignment (navy #1a1a2e, flame #e94560) — CEO feedback
  - Mobile scroll fix (issue #12) — touch-action + overscroll-behavior
  - Precise merge animation (only actually-merged tiles pulse)
  - Board size persistence via localStorage
  - Game-over detection fix (no-op moves now trigger it)

- **v0.5.0** — Game Stats + Simon Difficulty (shipped 2026-08-09)
  - Per-game stats tracking (plays, wins, best times) with Game Hub display
  - Simon difficulty levels (Easy/Classic/Hard) with per-difficulty bests
  - 25/25 logic checks; peer review caught 2 real bugs before merge

- **v0.6.0** — Wordfire (shipped 2026-08-11)
  - Fourth game: daily 5-letter word puzzle, UTC-seeded (same word for everyone)
  - Streak counter (gap reset + best), daily lockout after solve
  - Practice mode (random puzzles, no streak impact)
  - Colorblind mode (shape symbols), on-screen + physical keyboard, mobile-first
  - Stats integration + hub card; 1432 curated answers / 4656 guesses
  - 22/22 logic checks + DOM smoke test; peer review + brand + compliance APPROVE

- **v0.7.0** — Mobile Touch Quality Pass (shipped 2026-08-14)
  - CEO directive (2026-08-11) + community issue #26 (Wordfire iOS zoom/scroll): standardized the mobile touch baseline across all 4 games + hub
  - Wordfire: double-tap zoom fix (APPLE double-P), no tap delay, larger keys, color legend
  - Simon: zoom-safe rapid taps; Minesweeper: responsive cells, scrollable hard board, long-press flag fix
  - 32/32 static invariant checks + real-device manual test plan (B1-B8)
  - Story 008 + 009; issue #26 closed

- **v0.8.0** — Wordfire Share + Per-Difficulty Stats (shipped 2026-08-16)
  - Wordfire: shareable daily results (Story 010) — spoiler-free N/6 + streak + 6x5 grid, colorblind shapes, Web Share/clipboard/fallback
  - Minesweeper: per-difficulty stats (Story 011) — plays/wins/bestTime per difficulty, legacy migration, hub E/M/H bests
  - Website: What's New section (Story 012) on flambeee.com — latest release + Releases/Blog links
  - 23/23 static invariant checks + browser smoke tests (daily win share, no share on loss/practice, migration, per-diff recording)
  - Market note: puzzle games are the most-played browser category (23% of sessions); sharing is the most literal pull signal per PMF notes

- **v0.9.0** — Wordfire Guess Distribution + Website Screenshots (shipped 2026-08-18)
  - Wordfire: guess-distribution panel (Story 013) — bars for wins in 1-6 guesses, played/won/win%, daily-only, once per day, practice isolated
  - Website: game card screenshots (Story 014) — real board captures from actual game HTML, alt text, responsive 4:3, no more emoji icons
  - 29/29 static invariant checks + 6 browser smoke tests; peer review APPROVE + Palette APPROVE + Vigil APPROVE
  - Market note: word games growing ~31.7% (2023-2026, Wordle pipeline); daily-puzzle habits dominate browser gaming; distribution is the standard companion to shares

## Roadmap

### v0.20.0 — Session 22 (2026-09-20) ✅ Shipped
- **Cinder away-time decision record (Story 039, P1, docs-only)** — records the delegated decision: no offline resource accrual, a welcome-back return summary instead. Gold, XP, quests and boss fights do not progress while away; daily fights do not bank; the fight economy is untouched. Rationale: genre check, byte-safety (accrual cannot be additive), no balance change without CEO sign-off, and retention framing. This was the prerequisite Session 21 required before any away-time code.
- **Cinder welcome-back return summary (Story 040, P1)** — return after one or more fully missed UTC days and Cinder shows a one-time summary: days away, quests missed, streak status stated plainly, and a pointer to today's quest. Pure presentation, no new persisted field, no economy change, no notifications or install nag. `computeAwayWindow()` reads the day record captured before `checkDailyReset()` overwrites it. Kai pure-read proof 43/43 exit 0; Scout 167 real-browser checks 0 failed; test plans PR #86.
- **Website currency verification, two-run release step (Story 041, P2)** — run the checker before release AND after the What's New update and live sync, recording both in `release-chain.md`. Closes the Session 21 process gap. Checker unmodified.
- Process: separate git worktrees per dev (the prescribed fix for the Session 20/21 branch-collision hazard) and a parent-authored gate spec so the two halves of a single-file story could not collide.
- Vigil compliance PASS; deploy mirrors synced byte-identical.

### v0.18.0 — Session 19 (2026-09-13) ✅ Shipped
- **Cinder daily-return preview (Story 033, P1)** — deepen the daily-habit loop with a small, single-file addition to `src/cinder.html`. When today's quest is completed and rewarded, the quest detail view names tomorrow's objective and calls the player back after the UTC midnight reset. Tomorrow's quest is `determineQuestForDay(getDayIndex() + 1)`, the same pure-day-seed selection the live loop uses, shifted one day. Pure read: no save writes, no state mutation, no balance/rotation/payout change (Kai's proof, PR #72, exit 0). In-progress view byte-identical (regression safe); block flows inside `boxed-menu` so mobile has no horizontal overflow and Back to Town stays tappable. Copy plain punctuation, no em dashes, no emoji.
- **Website currency verification (Story 034, P2)** — a standing content-accuracy check, not a build. Confirmed What's New names the true latest release (v0.17.1) with an accurate summary, and the live site and repo mirror are byte-identical (`cmp` PASS). Passed clean in this session; no fix path triggered.
- 6/6 Story 033 BDD scenarios PASS (QA), 4/4 Story 034 scenarios PASS; Kai pure-read proof PASS; Vigil compliance PASS (no em/en dashes, no heavy emoji in new copy); deploy mirror synced byte-identical.

### v0.17.0 — Session 18 (2026-09-11) ✅ Shipped
- **Website What's New accuracy fix (Story 029, P0)** — the home page's What's New box still showed v0.15.0 (stale by two releases). Now reads v0.16.0 with an accurate summary of what that release actually shipped (`[Done]` quest tail, gold quest counts combat gold, Play today callout). No newer/unreleased features invented; Releases/Blog links kept. The one verifiable website accuracy defect, fixed.
- **Brand text cleanup, no-AI-tells (Story 030, P1)** — Vigil's carried note: older/blog content still used em dashes and heavy emoji predating the 2026-08-07 guidance. Kai cleaned all of BLOG.md (37 em dashes removed, decorative emoji stripped, one 🔥 sign-off kept per post); Riven cleaned the website title and About copy. Meaning, tone, and dry humor preserved. Whole voice now matches the rule.
- **Boss-day decision record (Story 031, P2, docs-only)** — the F1 boss-day stretch decision (conscious stretch goal, rotates away next day, largest bonus, no balance change) is formally recorded in the story doc; roadmap cross-links it. No code or balance change without explicit CEO sign-off.

- **PWA packaging (Stories 023 + 024)** — installable + offline-capable, the roadmap's top Future item. Retention play: a home-screen icon is a permanent return path; no new pull signal since v0.13.1, so the product gets optimized for retention.
- **Install (Story 023)** — web manifest (name, short_name, start_url, display standalone, theme #1a1a2e, background #0f1428), on-brand 192/512 icons rendered from the flame mark at native size, theme-color meta, apple-touch-icon, `beforeinstallprompt` captured with default prevented, small Install control in the nav that only appears when installable and leaves zero layout gap when hidden. No interstitial, prompt fires only on explicit tap.
- **Offline (Story 024)** — classic-script service worker `sw.js`, versioned precache `flambeee-shell-v<N>` (hub, manifest, icons, favicon, all 5 games, wordfire-words.js), cache-first with network fallback, skip-on-failure precache policy, skipWaiting + clients.claim after the two-version test showed default semantics never activate the new shell while a tab is open, old-cache cleanup on activate. localStorage untouched by the worker. Failure harmless: site plays exactly as before.
- Quinn wrote both stories; Kai shipped static infra (manifest, icons, sw.js); Riven shipped frontend (theme meta, install control, SW registration); peer reviews both ways; Scout QA GO with real Chromium, network actually disabled (all 5 games + hub offline, 12/12 precache entries, install lifecycle, zero console errors). Icon sign-off in QA via pixel sampling (vision model unavailable; exact brand colors verified programmatically).

### v0.13.1 — Session 14 (2026-09-01) ✅ Shipped
- **Cinder menu + combat patch (Story 021, issues #45/#46)** — both player-reported by BigFunger within an hour of the v0.13.0 launch. Menu rows rendered with inline handlers calling a function sealed inside the game's IIFE, so every tap threw a silent ReferenceError; mobile players had no keyboard fallback and could not play at all. Fixed with event delegation: 28 rows now carry data-action attributes and one listener on the display container. Second fix found under it: fight inputs were routed to the wilderness handler, making combat unwinnable by any input method; now Attack attacks, Run runs.
- **Repo presence (Story 022)** — README now lists all 5 games (Wordfire section added: it had never existed) with flambeee.com Play links, zero stale htmlpreview URLs; repo About/description + homepage set via gh repo edit.
- **QA bar raised** — QA drove v0.13.0 by keyboard only, so broken taps shipped invisible. Test plans now require real page.click()/page.tap() on every menu row on desktop and mobile viewports as proof.
- 74-check browser tap/click suite (Kai) + real-browser verification (Scout), 16/16 BDD scenarios PASS, peer reviews APPROVE both ways, QA test-plan PR #50.

### v0.2.0 — Session 2 (2026-07-31) ✅ Shipped
- **Simon memory game** — classic sequence-repeat with speed scaling, colorblind cues, keyboard support
- **Game hub/launcher** — central arcade lobby, Minesweeper moved to own page
- Peer reviews: Kai caught missing Simon file, Riven caught 4 issues (all fixed)
- 12-case test plan by Scout

### v0.3.0 — Session 3 (2026-08-04) ✅ Shipped
- **2048 game** — merge-puzzle, 4x4 classic + 5x5 Hard, arrow/WASD keys, swipe, localStorage best score, win/game-over overlays
- **Game Hub** — 2048 card added
- Peer review (Kai): 2 non-blocking observations noted for next session (merge animation approximation, difficulty persistence)
- 4/4 core logic assertions passed; 18-case test plan by Scout

### v0.4.0 — Session 4 (2026-08-07) ✅ Shipped
- **2048 polish pass** — brand palette, mobile scroll fix, precise merge animation, size persistence, game-over detection fix
- Community feedback integrated: issue #12 (mobile scroll) closed, CEO brand-palette note addressed
- 22/22 logic checks passed; peer review APPROVE

### v0.5.0 — Session 5 (2026-08-09) ✅ Shipped
- **Game stats tracking** (games played, wins, best times) — retention play per PMF notes: watch for pull signals, give players a reason to come back
- **Simon difficulty levels** — completes the difficulty rollout across all games
- Peer review caught 2 bugs before merge (2048 double-count, Simon sequence race), both fixed
- 25/25 logic checks passed

### v0.6.0 — Session 6 (2026-08-11) ✅ Shipped
- **Wordfire** — fourth game: daily 5-letter word game
  - UTC-seeded daily puzzle (same word for all players), streak counter with gap reset, practice mode
  - Colorblind shapes, full keyboard/mobile support, stats + hub card
  - Story 007 (18 BDD scenarios), 30-case test plan, 22/22 logic checks, DOM smoke test
  - Peer review APPROVE + Palette APPROVE + Vigil APPROVE
- Market note: instant-play browser games are a growing 2026 category; word/brain games rank top in roundups
- Retention thesis: a daily streak is the most literal pull signal per PMF notes

### v0.7.0 — Session 7 (2026-08-14) ✅ Shipped
- **Mobile Touch Quality Pass** — CEO directive (2026-08-11) + community issue #26: standardized the mobile touch baseline across all 4 games + hub
  - Wordfire: double-tap zoom fix, no tap delay, larger keys, color legend
  - Simon: zoom-safe rapid taps; Minesweeper: responsive cells, scrollable hard board, long-press flag fix
  - 32/32 static checks + real-device manual test plan; Stories 008 + 009; issue #26 closed

### v0.8.0 — Session 8 (2026-08-16) ✅ Shipped
- **Wordfire shareable results** — daily win overlay gets a Share button; spoiler-free summary (N/6 + streak + 6x5 tile grid), colorblind shapes, Web Share/clipboard/textarea fallback. Retention play: sharing is the most literal pull signal per PMF notes.
- **Minesweeper per-difficulty stats** — plays/wins/bestTime tracked per difficulty (carried from v0.5.0 review nits); legacy stats migrated; hub shows E/M/H bests.
- **Website What's New section** — flambeee.com home page now shows the latest release with Releases/Blog links (brand surface per CEO 2026-08-14).
- 23/23 static checks + browser smoke tests; peer review APPROVE + Palette APPROVE

### v0.9.0 — Session 9 (2026-08-18) ✅ Shipped
- **Wordfire guess distribution** — daily players get a record panel: bars for wins in 1-6 guesses + played/won/win% (daily only, once per day, practice isolated). Retention play: visible personal record that only grows by returning; matches the share grid format from v0.8.0.
- **Website game card screenshots** — flambeee.com game cards now show real board screenshots (Playwright captures of actual game HTML with scripted in-play states) instead of emoji icons; alt text on all 4, responsive 4:3 aspect. Brand surface per CEO 2026-08-14.
- Stories 013 (7 BDD scenarios) + 014 (5 BDD scenarios); 29/29 static checks + 6 browser smoke tests; peer review APPROVE + Palette APPROVE + Vigil APPROVE
- Market note: word games growing ~31.7% 2023-2026 (Wordle pipeline); puzzle retention benchmarks ~30% D1 / 14% D7; daily-puzzle habits dominate browser gaming. Guess distribution is the standard companion to shares.

### v0.10.0 — Session 10 (2026-08-21) ✅ Shipped
- **Website full games page (Story 015)** — every game card on flambeee.com opens a detail view: rules, real screenshot, personal stats from localStorage, relative Play link. Accessible (dialog role, focus trap, Escape close, focus return), responsive, private-mode safe, empty-state friendly.
- **Same-origin games (CEO directive)** — the 4 games + word list now live in `share/Flambeee/games/` and all Play links are relative, so localStorage stats are visible on flambeee.com itself (previously htmlpreview.github.io = different origin = invisible stats).
- Story 016 (Wordfire hard mode) written up and deferred to next session as planned (stretch).
- 9/9 BDD scenarios PASS (Scout), peer review APPROVE, Vigil APPROVE.

### v0.11.0 — Session 11 (2026-08-25) ✅ Shipped
- **Wordfire Hard mode (Story 016)** — Standard/Hard difficulty toggle (pre-round, touch + keyboard accessible, persisted in localStorage), hard daily seeded from a 330-word hard pool (same UTC-day seed, per-mode lockout), per-mode streak/stats/distribution isolation, "Wordfire Hard n/6" shares, mode-labeled record panel.
- Hard pool: programmatic filter on letter rarity + repeated letters + uncommon starts; 14.5% common-start vs 49.7% standard; every word verified in the guess list (Scout verifier PASS).
- 6/6 BDD scenarios PASS (Scout test plan + Playwright browser verification), peer review via PR #38, Vigil APPROVE.

### v0.12.0 — Session 12 (2026-08-28) ✅ Shipped
- **Wordfire modal shows Hard stats (Story 017)** — the Wordfire game detail view on flambeee.com now reads both the standard and hard localStorage keys and shows each mode's plays, wins, and streak, labeled Standard/Hard. Only modes with data appear (no zero-filled blocks). Card description and rules list mention Hard mode. Empty state preserved (never played, private mode, corrupt data).
- Pure website change: deployed `share/Flambeee/index.html` + repo mirror `website/index.html` in sync (byte-identical). 18/18 QA checks pass (8 BDD scenarios). Peer review + compliance PASS.
- Repo mirror What's New backfilled to v0.11.0 as part of the release.

### Future
- Multiplayer games (WebSocket-based)
- Community-submitted games
- Wordfire leaderboards (if pull signal confirmed)
- Wordfire guess-count stats (if pull signal confirmed)
- Cinder offline resource accrual (decided against in Story 039; revisiting requires explicit CEO sign-off)
- Cinder cross-day streak history across the daily reset as a *mechanic* (Story 042 fixed what the summary **reports**; it did not change the reset, did not bank or preserve a broken streak, and did not add history fields. Changing the reset itself or stored history remains a separate decision record)
- Cinder welcome-back suppression for a later visit on a different UTC day inside the same gap (Story 042 recorded limitation: closing it for good needs a persisted field, which is a Story 039 amendment plus CEO sign-off)

_Resolved in v0.20.0 (Story 039): Cinder offline progress / catch-up on return. The decision record is written and the missing piece is the return summary, shipped as Story 040. No accrual._

_Removed from Future (shipped in v0.15.0): Game of the week rotation._

## Principles

1. **Ship small, ship often** — every session ships something playable
2. **Zero friction** — no downloads, no accounts, no build steps
3. **Mobile-first** — games must work on touch devices
4. **Single-file philosophy** — each game is one HTML file, no dependencies
5. **Dark theme** — consistent visual identity across all products
6. **Open source** — MIT licensed, community can contribute