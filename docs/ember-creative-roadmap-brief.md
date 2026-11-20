> **Provenance.** Produced by kanban task `t_dd1da1b1` (2026-11-03) as the
> creative-direction input for IP-3 of `docs/ember-web-search-design.md`
> section 5. The brief below is filed verbatim and unmodified.
>
> Recommended first task: **Seed Cards**, the `?seed=` URL parameter on
> `website/games/2048.html` (direction 1, and step 2 of the brief's
> recommended next steps).

---

# Ember Creative Roadmap Brief, 2026-11-03

Source pool: two live runs of `scripts/ember_hot_ideas.py` (6 hot ideas, zero source reuse between runs), inverted by `scripts/ember_invert.py`. I also swept all six inversion axes across all six ideas to get a real candidate pool: **36 concepts generated, 36 schema-valid, 10 distinct summary shapes.**

That last number is the honest headline. The generator guarantees structure and opposition, not variety. Sweep all six axes on six ideas and you get six "X in Reverse" mechanics, six "The 100-Hour X" seasons, six "Flat-Fee X" models, and six "Rust X" reskins, because each axis planner has one or two branches and the axis choice is a sha256 offset rather than a judgment about the idea. So this brief does the judging: it selects four directions from the pool, refines the ones whose template is right but whose wording is generic, and kills the rest with reasons.

Scoring is 1 to 5 on Novelty, Feasibility (fits a static single-file repo with no accounts and no backend), Fit with the shipped catalog, and Spark (can it seed a new project). Sum out of 20.

| Direction | Origin axis | N | F | Fit | Spark | Total |
|---|---|---|---|---|---|---|
| Seed Cards (same-seed async compare) | social mode, inverted then refined | 4 | 5 | 5 | 4 | **18** |
| Reverse Mode (reverse-loop on a shipped game) | mechanic | 4 | 5 | 5 | 4 | **18** |
| The Long Season (30-day arc on Cinder) | session length | 4 | 3 | 3 | 5 | **15** |
| Build Any Page (hand inversion) | mechanic, off-template | 5 | 2 | 3 | 5 | **15** |
| Rust reskins (theme) | theme | 2 | 5 | 2 | 2 | 11 |
| No-Ghosts / Lonely modes | social mode | 2 | 5 | 2 | 2 | 11 |
| Newcomer rebuilds (audience) | audience | 2 | 4 | 3 | 1 | 10 |
| Flat-fee / pay-once (monetization) | monetization | 1 | 5 | 1 | 1 | 8 |

---

## 1. Seed Cards: same puzzle, your friend's score, no server

**Source trend.** Speed Per Step, named the 2026 exemplar of the single-mechanic viral formula *because of friend comparison*, plus Destroy Any Website, which launched with a built-in race-to-a-kill-target mode. The hot part of both is not the mechanic, it is the comparison.

**The inversion.** Generator output: *Lonely Speed* (axis: social mode): "the world of Speed Per Step with every other human removed: no chat, no leaderboard, no co-op partner, no rival."

Taken literally that is a no-op for us. Grep `website/games/*.html`: zero leaderboard, zero high-score table, zero live multiplayer, no accounts anywhere. Flambeee's catalog is already the lonely version. The useful flip is one axis further out: not *solitary*, but *asynchronous*. Remove the lobby, the matchmaking, the server, and the account, and keep the human. One board, many players, comparison by handing someone a link.

**Why it is interesting.** The half that exists proves the half that does not. Wordfire (`website/games/wordfire.html`, 1,093 lines) already runs a daily word with a per-day key, two streak keys, and a Share button (Story 010: `buildShareText()` emits an emoji grid, sent through `navigator.share` with a clipboard and textarea fallback). So the habit lands: people play the same board and post the result. But the share is strictly outbound. Nothing in the repo can send someone a specific board to play, and nothing accepts one back. That is the defect worth fixing, and it needs no backend, which is exactly why comparison has stayed off the roadmap.

A board is fully determined by a seed plus the player's moves. `website/games/2048.html` (454 lines) has exactly **2** `Math.random()` call sites, both tile spawn (line 235 value, line 244 cell). Swap them for a small seeded PRNG and `?seed=7f3a` fixes the board for everyone. The challenge is one copied URL; the answer is one number. Minesweeper has the same shape: 2 `Math.random()` sites in 786 lines.

**First experiment.** One session: add `?seed=` plus a "Play this board" button that copies `flambeee.com/games/2048.html?seed=…` to the clipboard, on 2048 only. Done means: the same seed produces a byte-identical opening board and the same spawn sequence on desktop 1280x800 and mobile 375x667, proven with a headless run comparing two independent loads; a different seed produces a different board; no-seed play is unchanged. Then hand the link to five people and ask one question: did you compare scores?

**Effort / risk.** Effort: **S**, one session, one file plus a CACHE bump. Risk: low technical, medium product. The falsifier is interest, not correctness: if five people play the same seed and nobody reports a score back, "comparison" is not the hook for this audience and the direction stops at 2048. Second risk: seed links invite cheating by replaying until the board suits you, which is why the first version should show a move counter and nothing else.

---

## 2. Reverse Mode: start solved, win by undoing

**Source trend.** Lagos Run (140,000 players in 7 days on a danfo bus runner) and Danfo Culture Runner (20,000 in days), both built on one legible mechanic reskinned with local culture. Cheap, single-mechanic, screenshot-legible games are what is travelling.

**The inversion.** Generator output: *Lagos in Reverse* (axis: mechanic): "you begin holding everything the source hands out and win by giving it all back. Hoarding triggers the lose state; the end screen celebrates an empty board."

The template's screenshot-legibility is the real asset here, not its Lagos dressing. A game that starts solved and gets worse is the same idea in one frame, and it ports onto code we already own.

**Why it is interesting.** It is a mode, not a new game. `website/games/2048.html` already has merge resolution; "Split" runs the same comparison backwards, where a merge becomes a split and the board starts full. Minesweeper in reverse is the cleaner one: the board starts solved and every flag you place removes information. Either is a small diff against a 454 or 786 line file, and both are visible in a single screenshot, which is exactly the property that made the source trend travel.

**First experiment.** One throwaway single-file prototype in `dev/` (the `dev/fps-probe/` pattern), 2048 Split rules only: 4x4 board starts full, a move splits the largest tile pair instead of merging, board empties toward a win. Done means a playable build with a win and a lose path, proven with real key input at both viewports, plus five people asked one question: did you want a second run?

**Effort / risk.** Effort: **S** to prototype, **M** to ship as a mode on an existing card (mode toggle plus persistence plus CACHE bump). Risk: medium. Reverse loops are a classic novelty that dies after one run, because undoing is not a new decision unless the split rule creates real choice. The falsifier is the second-run question above; if the answer is no from four of five, it ships as a one-off curiosity or not at all, and we do not build the second one.

---

## 3. The Long Season: 30 days, one decision a day, on Cinder

**Source trend.** Movetio Mafia Test (live open test through November 2026 in 5 languages), inverted on session length into *The 100-Hour Movetio*: "one meaningful decision per evening, no grinding, no catching up. Progress compounds across real calendar time and a missed week bends the story instead of ending it. The finale is scheduled, shared, and unrepeatable."

**The inversion.** Inverted again in scope: 100 hours is not the point, *persistence* is. Flambeee ships one-shot snackables. A 30-day arc with a scheduled finale is the one product shape the studio has never made, and Cinder already records the days and counts the streak. What it lacks is an arc with an end.

**Why it is interesting.** Cinder (`website/games/cinder.html`, 1,754 lines) already has a daily quest system with `QUEST_TYPES`, recorded day history, a derived consecutive-day streak, a quest log, and an away-window screen that reports days missed and whether the streak survived. All of it is `localStorage`, no accounts. That machinery is a 30-day season waiting for a spine: 30 quests, one per day, ordered, with an end state. The cheapest new-product-class experiment in the repo.

**First experiment.** No code. Write the 30-day arc on paper against the existing `QUEST_TYPES`: 30 days, one decision each, three branch points where a missed week changes the story instead of ending it, one finale. Done means a table of 30 days that fits the existing quest record shape without a new save field. If it needs a new save field, that is the finding, and the direction costs more than it looked.

**Effort / risk.** Effort: **M** if the arc fits the existing record; **L** if it needs a new persistence layer. Risk: high, and the risk is validation, not code. A day-30 claim cannot be proven in one session, and this repo has the scar: Story 079 closed a 3-day reuse probe as unmeasurable because the profiles were garbage-collected before the crossing. Any long-form direction needs a calendar-based proof plan with a stated day-30 instrument before the first story opens, or it ships unverified.

---

## 4. Build Any Page: the inverse of Destroy Any Website (spike only)

**Source trend.** Destroy Any Website, September 2026 launch: paste any URL, spawn a stickman, blast the page to 100 percent destruction, with a Flash-era nostalgia hook and a race mode. Note the noise around it: "paste any URL" is the hook, and the destruction is the wrapper.

**The inversion.** The generator took the monetization axis on this idea (*Flat-Fee Destroy*), which is the weakest of its six possible flips. The interesting one is off-template and hand-written: paste a URL and *rebuild* it. Same input, opposite verb. The page arrives in fragments and the play is to reassemble it.

**Why it is interesting.** Highest novelty in the pool and the only concept here that could become its own product rather than a feature. It also inverts the trend's mean streak, which is a brand position Flambeee could own: we build things, we do not vandalise them.

**First experiment.** A spike, not a story. One `dev/` page that takes **five fixed local pages**, shreds one into draggable fragments, and measures whether reassembly is fun before any URL handling exists. Done means a playable shred-and-rebuild loop on a fixed page plus five playtesters, and a written answer on whether arbitrary URLs are needed at all.

**Effort / risk.** Effort: **S** for the spike, **L** or dead for the real thing. Risk: high and mostly structural. Fetching an arbitrary page from a static site is blocked by CORS; there is no app server in this stack and adding a fetch proxy means new infrastructure and a Caddy change, which is Jake's call, not a roadmap line item. Second risk: rebuild-my-page is a toy with a one-minute lifespan unless the fragment set is authored. Ship the spike, then decide whether to spend the server.

---

## Killed, with reasons

- **All six monetization inversions** (Flat-Fee Culture/Daily/Lagos/Movetio/Speed/Destroy). The site promises "no sign-up, no download, no paywall" and the repo is open source; a pay-once model is a business decision for Jake, not a creative direction, and the generator produced it for every idea because `_plan_monetization` has exactly two branches.
- **All six Rust reskins** (theme). Template artifact, and the mechanism is visibly broken: **6 of 6** theme flips produced "Rust X", including Destroy Any Website, whose source is already grim. The body text is written for cozy sources and still says "every cozy promise curdles, the harbor silts up" when applied to a path-drawing puzzle. Also a brand conflict: Flambeee's surface is playful, and a permanent grim reskin is not.
- **Newcomer rebuilds** (audience). Flambeee games are already one-idea, no-tutorial, one-click. "Rebuilt for total beginners" is the status quo with more words.
- **No-Ghosts / Lonely modes.** Folded into direction 1. As a standalone build it removes a feature that does not exist.

---

## Pipeline findings worth fixing before the next run

1. **Axis choice is hashed, not judged.** `default_axes()` picks three axes from a sha256 offset. That put the monetization axis on 2 of the 6 ideas from the live runs, and monetization is the axis with the least creative value for us. Fix: generate all six axes and rank by the scoring table above, keeping the top axis per idea. Cost: one selection function, no new schemas.
2. **Theme planner has no neutral branch.** It flips grim to cozy and everything else to Rust. A source that is neither should skip the theme axis rather than get a canned grim reskin. Fix: add a `skip` outcome and let ranking drop it.
3. **The mechanic planner has one generic default.** Four of six ideas fell through to "undoes the loop step by step", so the mechanic axis produced one shape across a pool of unrelated genres. Fix: add per-genre planners or at minimum vary the default by loop verb.
4. **All 36 pass validation.** The schema and anti-rewording checks work; they just do not measure novelty. Nothing to change there, but do not read "0 invalid" as "36 good ideas".

---

## Recommended next steps, in order

1. **Approve or kill the four directions.** Two are one-session ships (Seed Cards on 2048, Reverse Mode prototype), one is a paper exercise (Long Season), one is a gated spike (Build Any Page). Total cost to the first decision point: three or four sessions.
2. **Open the Seed Cards story on 2048 first.** It is the cheapest direction that tests the biggest open question, it touches one 454-line file, and its proof is mechanical rather than taste-based.
3. **Fix axis selection before the next Ember run.** Otherwise the next six ideas will again yield what this run's hash picks yielded: 2 usable flips, 2 monetization flips we kill, 1 theme flip we kill, and 1 social flip that is a no-op. The brief would do this filtering again.
4. **Fold the surviving directions into `docs/roadmap.md`** as a "Creative directions" section under Now, not as v-numbers. The roadmap owner carries that edit; this brief is the input.
5. **Give the Long Season a day-30 instrument before any code.** If that instrument cannot be named, the direction is unverifiable and should stay on paper.

Evidence files in this workspace: `run1-ideas.json`, `run2-ideas.json` (real search output), `run1-inverted.json`, `run2-inverted.json` (hash-assigned concepts), `sweep.json` (all 36 candidates, all validated), `sweep.py`.
