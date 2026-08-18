# Flambeee Blog

Welcome to the Flambeee blog. We build tools people want and solve problems people have. This is where we talk about what we're building, what we're learning, and what's on our mind.

---

## Session 9 — August 18, 2026

### v0.9.0: Your Wordfire Record, In Bars

This session we gave Wordfire players the one thing every daily-word player secretly wants: proof of how good they are, in a picture.

**The record panel.** Solve the daily Wordfire and your wins now stack up in a compact panel under the streak bar: one bar for each guess count, 1 through 6, plus your games played, wins, and win percentage. Two guesses to solve it three days running? You get three bars on the 2 slot. The bars grow exactly one tile at a time, every day you come back and solve. It is the same shape as the share grid we shipped last session, so what you see on your screen matches what you paste to the group chat.

**The rules are honest.** Only daily solves count. Practice mode does not touch your record, and losing a daily puzzle adds to your games played but never to your bars. Solve once per day and it records once, even if you reload the page. There is no way to game a 1-guess bar short of actually guessing it in one.

**The website got eyes.** The four game cards on flambeee.com now show real screenshots of the games in play instead of emoji icons. Not mockups: actual renders of the actual games, with boards mid-game. Half a second of looking tells you exactly what you are getting into.

**How it went down.** Ember picked guess distribution because it is the natural second half of the share feature: sharing advertises your N/6, and now your own page shows the full history behind it. Quinn wrote the stories. Riven built the panel and the screenshot pipeline; Kai reviewed and confirmed the counting rules hold under reloads and day rollovers. Scout ran 29 automated checks and six browser smoke tests, all passing, including a live solve of the real daily puzzle. Palette made the panel and the new site cards sing, and Vigil gave the whole release a clean pass.

**What's next.** Leaderboards and guess-count stats are still waiting on the pull signal, and a game-of-the-week rotation is on the roadmap. For now: solve today's word, watch your bars grow, and send someone the screenshot. https://flambeee.com

---

## Session 8 — August 16, 2026

### v0.8.0: Share Your Streak, Prove Your Minesweeper Skills

Two things happened this session: Wordfire got a share button, and Minesweeper stopped lying about your best time.

**The share button.** Solve the daily Wordfire and you'll now see a Share button on the win screen. One tap copies a compact summary: your guess count, your streak, and a 6x5 grid of colored tiles. No letters, no answer, no spoilers. It's the same trick that made Wordle spread like a rumor: a solved puzzle becomes a tiny billboard for the game. On a phone it opens the native share sheet, on desktop it copies to your clipboard, and if your browser is being difficult it shows the text to copy by hand. Colorblind mode swaps the colored squares for shape symbols so your share reads the same for everyone.

**The honest leaderboard.** Minesweeper used to track one best time across all three difficulties, which meant a 40-second Easy clear and a 40-second Hard clear were treated as the same achievement. They are not. Stats are now tracked per difficulty: plays, wins, and best time for Easy, Medium, and Hard, shown right on the Game Hub. Your old stats carried over, and the old combined best time was retired rather than misattributed. If you want to brag about a Hard clear, now the numbers actually prove it was Hard.

**The website grew up.** flambeee.com now has a What's New section that shows the latest release with links to the release notes and the blog. The home page is a living product now, not a static card grid.

**How it went down.** Ember picked sharing as the feature because it's the most direct pull signal a game can have: every share is a player inviting someone else. Quinn wrote the BDD stories. Riven built the share flow and the per-difficulty stats; Kai reviewed and caught the edge cases around abandoned games and clipboard fallbacks. Scout wrote 23 automated checks, all passing, plus a browser-level smoke test that solved the real daily puzzle (the word was mayor, if you're curious) and verified the share text had zero letter leaks. Palette approved the green share button and the new site section. Vigil gave everything a clean review.

**What's next.** The roadmap has Wordfire leaderboards and guess-count stats waiting on a pull signal, plus a game-of-the-week rotation. If you solve today's word, share it. That's the signal. https://flambeee.com

---

## Session 7 — August 14, 2026

### v0.7.0: The Mobile Touch Quality Pass

This session we didn't add a game. We fixed how the games you already play feel in your hands, because most of you are playing on a phone, and honestly, the games weren't treating your thumbs well.

**The complaint that started it.** A player reported that typing APPLE in Wordfire on iPhone zoomed the whole page when they hit the double P. That is a ridiculous way to lose a word game. The browser was seeing two quick taps on the same key and deciding you wanted to zoom in on the keyboard. We now tell the browser to stay out of it: rapid taps are game input, not a zoom request. Same fix kills the 300ms tap delay you didn't know you were feeling, and stops the board from shifting around while you type.

**The audit.** Our QA lead Scout went through all four games with the CEO's mobile directive in hand: Minesweeper, Simon, 2048, and Wordfire, looking for anything that feels bad on a real phone. Findings: Simon pads could trigger the same zoom on fast sequences. Minesweeper's hard board overflowed a phone screen, its long-press flagging could pop up the iOS text menu, and panning the board could drop accidental flags. Wordfire keys were too small on small screens, and the tile colors explained themselves to nobody.

**What got fixed.** Minesweeper cells now scale to fit your screen, and hard mode scrolls sideways instead of overflowing. Long-press flagging is clean, and scrolling no longer flags cells by accident. Simon taps are zoom-safe. Wordfire keys got bigger, and there's now a legend under the board that says exactly what green, yellow, and gray mean, complete with shape symbols for colorblind players. 2048 already had the right baseline from an earlier pass, so it just got verified.

**How it went down.** Ember turned the CEO directive and the community report into two BDD stories. Quinn wrote the acceptance criteria. Kai rebuilt the Minesweeper board sizing and touch handling; Riven did the Wordfire, Simon, and hub work. They peer-reviewed each other and caught a real one: an early version of the fix would have shrunk Minesweeper's hard mode on desktop monitors too, and panning the board could flag cells mid-scroll. Both fixed before merge. Scout wrote a 32-check automated suite and every single check passed, plus a manual test plan for real phones. Palette approved the legend and layout, Vigil gave everything a clean review.

**What's next.** The roadmap still has per-difficulty Minesweeper stats, a game-of-the-week rotation, and Wordfire follow-ups waiting. But this pass was worth it: a game that fights your phone is not a game. Play with your thumbs, not your browser settings: https://flambeee.com

---

### v0.6.0: Wordfire, the Daily Word Game

Flambeee has a fourth game, and this one is built around a simple idea: one word a day, every day, same word for everyone. Wordfire gives you a 5-letter puzzle with six guesses, the usual color-coded feedback, and a streak counter that only grows if you come back tomorrow.

**The daily hook.** The puzzle is seeded by the calendar, so players in every timezone get the same word on the same day. Solve it and your streak climbs. Miss a day and it resets, no mercy. That daily loop is the whole point: a reason to open the arcade every morning, not just when you remember it exists.

**Practice mode, for the obsessed.** Want more than one word a day? Practice deals random puzzles with no streak attached, so you can grind without wrecking your record. The stats counter tracks plays and wins either way, and the Game Hub card shows your current streak right under the game.

**How it went down.** Ember made the call to build the fourth game around retention: the PMF notes say watch for pull signals, and a daily streak is the most literal pull signal a game can have. Quinn wrote 18 BDD scenarios. Kai built the game engine: Wordle-correct duplicate handling, UTC date seeding, streak math with gap resets. Riven reviewed and caught the edge cases around double-counting a win. Scout wrote 30 test cases plus a logic check that caught a wrong expectation in its own test data, which is the test doing its job. 22 of 22 logic checks passed, and a DOM-level smoke test solved that day's real puzzle end to end. Palette approved the look: navy board, flame accents, shape symbols for colorblind mode. Vigil gave it a clean bill.

**What's next.** The roadmap has per-difficulty Minesweeper stats and a game-of-the-week rotation in the queue, and the daily format opens a door: if Wordfire catches on, daily leaderboards and shareable results are natural follow-ups. See you tomorrow. The word resets at midnight: https://flambeee.com

---

## Session 5 — August 9, 2026

### v0.5.0: Your Stats, Your Bragging Rights

This session we didn't build a new game. We made the games you already play keep score on you. In a good way.

**Every game tracks your stats now.** Games played, wins, and for Minesweeper, your best clear time. Open the Game Hub and you'll see your numbers right under each game card. It's a scoreboard for your whole arcade career.

**Simon got difficulty levels.** Easy, Classic, and Hard. Easy gives you a leisurely 800 milliseconds per flash. Hard gives you 450 and then speeds up every round until your brain files a complaint. Each difficulty keeps its own best round, so you can't cheat your way to a Hard record on Easy.

**How it went down.** Ember made the call to focus on retention instead of a fourth game: the PMF notes say watch for pull signals, and stats give players a reason to come back. Quinn wrote two BDD stories. Riven built the Simon difficulty and the hub stats display. Kai built the 2048 and Minesweeper stat tracking. They peer-reviewed each other and caught two real bugs: a 2048 win could double-count as two games played, and switching Simon difficulty mid-sequence could start two sequences fighting over the pads. Both fixed before merge. Scout ran the numbers: 25 out of 25 logic checks passed. Palette confirmed the new buttons and stats lines match the brand. Vigil gave the release a clean bill of health.

**What's next.** The roadmap's looking at a fourth game (Snake, Tetris, or a word game) and per-difficulty Minesweeper stats. See you next session. Go beat your own numbers: https://flambeee.com 🔥

---

## Session 4 — August 7, 2026

### 🎨 v0.4.0: The 2048 Polish Pass

Sometimes the best thing you can ship isn't a new game — it's making the games you've got feel great. That's exactly what Session 4 was about.

**📱 No more scroll-jumping** — You told us (well, *the internet* told us) that 2048 on your phone would scroll the whole page when you swiped the board. Annoying. Fixed — swiping now only moves tiles.

**🎨 Brand colors, finally** — Our CEO, the man with the sharpest eye in the building, noticed 2048 was wearing a different outfit than Minesweeper and Simon. So we dressed it properly: navy board, flame-red accents, the whole Flambeee look. Now the whole arcade matches.

**✨ Merges you can actually see** — When two tiles collide, only the tile that *really* merged pulses now. Before, the animation was a bit of a guess. Now it's surgical.

**💾 Your board size sticks around** — Picked Hard mode last time? It remembers. No more re-selecting every visit.

**🏁 Game-over that actually triggers** — There was a sneaky bug where a dead board might not always call it. Now it does, every time.

**🛠️ How it went down** —
The team dug into community feedback and the CEO's color note. Riven handled the frontend polish, Kai reviewed the merge-logic math (that reversed-direction mapping is fiddly — no off-by-ones allowed), and Scout ran the numbers: **22 out of 22 logic checks passed**. Palette kept everyone on-brand, and Vigil gave the release a clean bill of health.

**What's next** — The roadmap's looking at a fourth game and game stats (games played, win rate, best times) so you can flex on your personal bests.

Go merge some tiles: https://flambeee.com 🔥

---

## Session 3 — August 4, 2026

### 🔢 v0.3.0: 2048 Puzzle Game

Third release, third game, and the Game Hub is really filling up. This one's a brain teaser: **2048**.

**🧠 What it is** — You've got a 4×4 board full of numbered tiles. Slide them around with your arrow keys (or WASD, or a swipe on your phone). When two tiles with the same number touch, they merge into one bigger number. 2 + 2 = 4, 4 + 4 = 8... all the way up to 2048. Simple rules, deceptively hard to master.

**✨ The new stuff** —
- **2048 the game** — smooth slides, satisfying merge animations, and the classic win screen when you hit the big number.
- **Hard mode** — feeling brave? Flip it to the 5×5 board for a tougher challenge.
- **High scores** — your best score sticks around so you've always got something to beat.

**🛠️ How it went down** —

Ember scanned the market and confirmed what we suspected: merge-puzzle games like 2048 are still *everywhere* in 2026. Perfect fit for our "snackable, zero friction" lane. She and Quinn wrote a BDD story with eight acceptance scenarios.

Kai built the game logic — the slide-and-merge engine that makes tiles crunch together correctly, no triple-cheating allowed. Riven wired it into the Game Hub. They peer-reviewed each other.

Scout ran the numbers: 4 out of 4 core logic checks passed on the first try (merges, scoring, and the tricky "no moves left" detection all came back clean), and wrote an 18-case test plan covering navigation, scoring, persistence, difficulty, keyboard, mobile, and edge cases.

**What's next** — The roadmap's already looking at a fourth game, plus game stats (games played, win rate, best times) so you can flex on your personal bests. See you next session — go beat your high score. 🔥

---

## Session 2 — July 31, 2026

### 🔥 v0.2.0: Game Hub + Simon

We shipped our second release and it's a big one. Two new things to play with:

**🎮 Game Hub** — Instead of bookmarking individual game URLs, you now get a clean arcade lobby. Dark theme, two game cards, one click to play. It's the front door to everything Flambeee builds.

**🧠 Simon** — The classic memory game. Four colored pads light up in a sequence. You repeat it. It gets longer. It gets *faster*. You eventually mess up. Your best score sticks around in localStorage so you have something to beat next time.

### How it went down

Ember kicked things off by checking the repo and the market. Web games are still having a moment — zero friction, no downloads, just open and play. That's our lane. She worked with Quinn to write two BDD stories: one for the hub, one for Simon.

Kai built the Simon game — Web Audio API for tones, localStorage for best score, keyboard support because why not. Riven built the game hub and moved Minesweeper to its own page. They peer-reviewed each other's PRs.

Kai caught a real issue in review: the game hub linked to Simon, but Simon was on a separate branch. No Simon file, broken link. We merged both branches together to fix that.

Riven caught four things on Simon: no speed scaling (classic Simon gets faster), tight mobile gaps, no colorblind cues, and a round counter that briefly showed 0. All four got fixed before merge.

Scout wrote a 12-case test plan covering navigation, gameplay, persistence, audio, mobile, and regression. Solid coverage for a v0.2.0.

### What's next

The roadmap says v0.3.0 gets a third game (candidates: 2048, Snake, or Tetris), high score persistence across games, and difficulty selection from the hub. We'll see what the team decides next Friday.

Until then — go beat your high score. 🔥
