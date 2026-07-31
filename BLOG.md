# Flambeee Blog

Welcome to the Flambeee blog. We build tools people want and solve problems people have. This is where we talk about what we're building, what we're learning, and what's on our mind.

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