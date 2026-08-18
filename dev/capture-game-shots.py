#!/usr/bin/env python3
"""Palette — v0.9.0 website game card screenshots (Story 014).

Captures a representative in-play state for each of the four games from the
real game HTML (src/*.html) via Playwright, cropping to the game board region
for a card-friendly portrait thumbnail. Output: share/Flambeee/assets/game-*.png

Truthfulness rule: every screenshot is a real render of the real game file,
with a scripted state (the same state a player would see mid-game), not a fake
mockup. No personal data ever appears (boards are seeded with fixed states).
"""
import os
import json
from playwright.sync_api import sync_playwright

REPO = "/home/jake/.openclaw/workspace/flambeee"
OUT = "/home/jake/.openclaw/workspace/share/Flambeee/assets"
os.makedirs(OUT, exist_ok=True)

# (name, html_path, board selector, optional state JS)
GAMES = [
    ("wordfire", "src/wordfire.html", "#board", None),
    ("minesweeper", "src/minesweeper.html", "#board, .board, #minesweeper", None),
    ("simon", "src/simon.html", "#board, .simon-board, .game-board", None),
    ("2048", "src/2048.html", "#grid, .board-wrap, .grid", None),
]

STATE_JS = {
    "wordfire": """
      (() => {
        const rows = [['c','r','a','n','e','green','green','green','green','green'],
                      ['b','l','i','n','d','gray','yellow','yellow','gray','gray']];
        const board = document.getElementById('board');
        if (!board) return;
        for (let r = 0; r < 2; r++) {
          const row = board.children[r];
          for (let c = 0; c < 5; c++) {
            const el = row.children[c];
            el.textContent = rows[r][c];
            el.classList.add('filled', rows[r][5 + c]);
          }
        }
      })();
    """,
    "minesweeper": """
      (() => {
        const cells = document.querySelectorAll('#board .cell');
        if (!cells.length) return;
        const nums = [[5,'1'],[6,'1'],[17,'1'],[18,'1'],[11,'2']];
        nums.forEach(([i,t]) => { const el = cells[i]; if (el) { el.classList.add('revealed'); el.textContent = t; } });
        [0,1,2,3,4,10,16,22,23].forEach(i => { const el = cells[i]; if (el) el.classList.add('revealed'); });
      })();
    """,
    "simon": """
      (() => {
        const pads = document.querySelectorAll('.pad, .simon-pad, [data-pad]');
        pads.forEach((p, i) => { if (i === 0 || i === 2) p.classList.add('lit', 'active'); });
      })();
    """,
    "2048": """
      (() => {
        const cells = document.querySelectorAll('#grid .cell');
        const vals = [2,4,2,8, 4,2,16,2, 2,8,2,4, 4,2,4,8];
        cells.forEach((t, i) => {
          if (vals[i]) { t.textContent = vals[i]; t.dataset.v = String(vals[i]); }
        });
      })();
    """,
}


def find_board(page, selectors):
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                box = el.bounding_box()
                if box and box["width"] > 50:
                    return el, box
        except Exception:
            continue
    return None, None


def capture(name, html_path, selectors):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 460, "height": 700}, device_scale_factor=2)
        page.goto(f"file://{REPO}/{html_path}")
        page.wait_for_timeout(400)
        js = STATE_JS.get(name)
        if js:
            page.evaluate(js)
            page.wait_for_timeout(250)
        el, box = find_board(page, selectors)
        if not el or not box:
            print(f"WARN {name}: board not found, full-page shot")
            png = page.screenshot()
        else:
            pad = 12
            clip = {
                "x": max(0, box["x"] - pad),
                "y": max(0, box["y"] - pad),
                "width": box["width"] + pad * 2,
                "height": box["height"] + pad * 2,
            }
            png = page.screenshot(clip=clip)
        browser.close()
        return png


if __name__ == "__main__":
    for name, html_path, sel, _ in GAMES:
        png = capture(name, html_path, sel.split(", "))
        out = os.path.join(OUT, f"game-{name}.png")
        with open(out, "wb") as f:
            f.write(png)
        print(f"captured {name} -> {out} ({len(png)} bytes)")
    print("done")
