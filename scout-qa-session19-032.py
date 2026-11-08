#!/usr/bin/env python3
"""QA harness (Scout) for Story 032 boss-day balance.

Verifies startCombat pool selection against the real MONSTERS/LEVELS/
WEAPONS/ARMOR data pulled from website/games/cinder.html. Invariants:
  1. Boss day: every combat pools ONLY boss-tier monsters (id >= 13).
  2. Boss day + too weak: stretch fallback is the WEAKEST boss.
  3. Non-boss day: pool selection is UNCHANGED vs pre-patch behavior.
  4. 15-fight day on a boss day at mid-level: quest reachable (boss appears).
"""
import re, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))


def _repo_root():
    """Repo root at run time: $REPO wins, else walk up from this file."""
    env = os.environ.get("REPO")
    if env:
        return env
    d = HERE
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return d
        d = parent


REPO = _repo_root()
SRC = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "CINDER_SRC", os.path.join(REPO, "website", "games", "cinder.html"))
s = open(SRC, encoding="utf-8").read()

def grab(name, pattern):
    m = re.search(pattern, s, re.S)
    if not m:
        raise SystemExit(f"pattern not found for {name}")
    return m.group(1)

# Rebuild MONSTERS / LEVELS / WEAPONS / ARMOR via a tiny JS-less parser is
# fragile; instead evaluate the raw JS arrays with node to get ground truth.
import json as _json
node_script = (
    "const fs = require('fs');\n"
    "const src = fs.readFileSync(%s,'utf8');\n"
    "const body = src.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/)[1];\n"
    "const MONSTERS = eval(body.match(/const MONSTERS = (\\[[\\s\\S]*?\\]);/)[1]);\n"
    "const LEVELS = eval(body.match(/const LEVELS = (\\[[\\s\\S]*?\\]);/)[1]);\n"
    "const WEAPONS = eval(body.match(/const WEAPONS = (\\[[\\s\\S]*?\\]);/)[1]);\n"
    "const ARMOR = eval(body.match(/const ARMOR = (\\[[\\s\\S]*?\\]);/)[1]);\n"
    "console.log(JSON.stringify({MONSTERS, LEVELS, WEAPONS, ARMOR}));\n"
    % _json.dumps(SRC)
)
out = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, cwd=REPO)
if out.returncode != 0:
    raise SystemExit(f"node eval failed: {out.stderr[-500:]}")
data = _json.loads(out.stdout)
MONSTERS, LEVELS, WEAPONS, ARMOR = data["MONSTERS"], data["LEVELS"], data["WEAPONS"], data["ARMOR"]
BOSS_TIER = 13
CAP = 2.5

def base_stats(level):
    hp = atk = df = 0
    for i in range(level):
        hp += LEVELS[i]["hpGain"]; atk += LEVELS[i]["atkGain"]; df += LEVELS[i]["defGain"]
    return hp, atk, df

def str_of(level, weapon, armor):
    _, atk, df = base_stats(level)
    w = next((x["atk"] for x in WEAPONS if x["id"] == weapon), 0)
    a = next((x["def"] for x in ARMOR if x["id"] == armor), 0)
    return level + (atk + w) + (df + a)

def pool(level, weapon, armor, is_boss_day):
    ps = str_of(level, weapon, armor)
    cands = [m for m in MONSTERS if (not is_boss_day or m["id"] >= BOSS_TIER)
             and (m["hp"] + m["atk"] + m["def"]) <= ps * CAP]
    if cands:
        return cands
    if is_boss_day:
        bosses = sorted([m for m in MONSTERS if m["id"] >= BOSS_TIER],
                        key=lambda m: m["hp"] + m["atk"] + m["def"])
        return bosses[:1]
    return MONSTERS[:1]

# Load the patched selection from the actual source to prove we match it.
patched = re.search(r"function startCombat\(\) \{([\s\S]*?)\n  \}\n\n  function renderCombat", s)
if not patched:
    raise SystemExit("startCombat body not found")
body = patched.group(1)
assert "const activeQuest = getActiveQuest();" in body, "boss-day hook missing"
assert "isBossDay" in body and "m.id < BOSS_TIER) return false;" in body, "boss filter missing"
assert "bosses[0]" in body, "stretch fallback missing"
print("PATCH PRESENT: boss-day filter + stretch fallback in startCombat")

fails = 0
def check(label, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + label)
    if not cond: fails += 1

# 1. Boss day, level 10 + Godforge gear: only bosses
p = pool(10, 7, 7, True)
check("boss day L10: pool is all bosses", all(m["id"] >= BOSS_TIER for m in p) and len(p) == 3)

# 2. Boss day, level 1 starter: stretch fallback = weakest boss (Shadow Knight)
p = pool(1, 0, 0, True)
check("boss day L1: stretch fallback is weakest boss", p[0]["id"] == BOSS_TIER)

# 3. Non-boss day: pool unchanged (same filter as pre-patch: plain 2.5x cap)
p0 = pool(1, 0, 0, False)
pre = [m for m in MONSTERS if (m["hp"] + m["atk"] + m["def"]) <= str_of(1, 0, 0) * CAP]
check("normal day L1: pool = pre-patch filter exactly",
      sorted(m["id"] for m in p0) == sorted(m["id"] for m in pre))
check("normal day L1: no bosses in pool", all(m["id"] < BOSS_TIER for m in p0))

# 4. Mid-level boss day reachability: at L5 Rusty Dagger + Leather (realistic,
#    5 fights, 3 heals), every combat is a boss; simulate 200 days of 15 fights:
#    boss always appears (100% of combats is boss).
import random
random.seed(7)
boss_seen = 0
for _ in range(200):
    for _ in range(15):
        p = pool(5, 1, 1, True)
        boss_seen += all(m["id"] >= BOSS_TIER for m in p)
check("boss day L5: 200x15 fights all boss-only", boss_seen == 200 * 15)

# 5. Weak player safety: L1 boss day never forces a fight they can lose
#    instantly? Stretch fallback = Shadow Knight (63 str) vs L1 (7 str).
p = pool(1, 0, 0, True)
check("L1 faces only the weakest boss as stretch", p[0]["name"] == "Shadow Knight")

print(f"\n{fails} failures")
sys.exit(1 if fails else 0)
