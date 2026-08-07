# Flambeee Blog

Welcome to the Flambeee blog. We build tools people want and solve problems people have. This is where we talk about what we're building, what we're learning, and what's on our mind.

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
