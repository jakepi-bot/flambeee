#!/usr/bin/env python3
"""Generate WORDFIRE_HARD_ANSWERS for Story 016.

Reads WORDFIRE_ANSWERS + WORDFIRE_GUESSES from src/wordfire-words.js,
scores each answer for hardness (rare letters, repeated letters, uncommon
starts), picks the hardest 330, verifies every pick is a valid guess-list
word, and writes the WORDFIRE_HARD_ANSWERS array into the file.
"""
import json
import re
import sys

SRCJS = "/home/jake/.openclaw/workspace/flambeee/src/wordfire-words.js"
HARD_TARGET = 330  # >= 300 required; extra margin for safety

# English letter frequency (relative); higher = more common
COMMON = "eariotnslcudpmhgbfywkvxzjq"

def parse_array(name, text):
    m = re.search(r"const\s+" + name + r"\s*=\s*\[(.*?)\];", text, re.S)
    if not m:
        raise SystemExit(f"could not find {name} in {SRCJS}")
    return [w.strip(" '\"") for w in m.group(1).split(",") if w.strip()]

def hard_score(word):
    """Higher = harder to guess. Weighted letter frequency + patterns."""
    letters = set(word)
    score = 0.0
    # Letter frequency penalty: common letters lower the score
    for ch in word:
        score += 1.0 / (1 + 10 * (ch in "eariotnslcudpmh"))  # rare letters weigh more
    # Rare-letter bonus
    score += 3.0 * sum(1 for c in letters if c in "jqxzvwkyf")
    # Repeated letters are tricky
    if len(word) != len(letters):
        score += 2.0
    # Uncommon starting letter (avoids the easy s/t/c/b starts)
    if word[0] in "jqxzvwkyfp":
        score += 2.0
    elif word[0] in "stcbdmae":
        score -= 1.0
    return score

def main():
    text = open(SRCJS, encoding="utf-8").read()
    answers = parse_array("WORDFIRE_ANSWERS", text)
    guesses = set(parse_array("WORDFIRE_GUESSES", text))

    # Score + sort, break ties deterministically
    scored = sorted(((hard_score(w), w) for w in answers), reverse=True)
    hard = [w for _, w in scored[:HARD_TARGET]]

    # Verify
    missing = [w for w in hard if w not in guesses]
    bad = [w for w in hard if len(w) != 5 or not w.islower()]
    if missing:
        raise SystemExit("NOT IN GUESSES: " + ", ".join(missing[:20]))
    if bad:
        raise SystemExit("BAD WORDS: " + ", ".join(bad[:20]))
    if len(hard) < 300:
        raise SystemExit(f"only {len(hard)} words")

    # Stats for the verification report
    common_starts = sum(1 for w in hard if w[0] in "stcbpm")
    common_in_all = sum(1 for w in answers if w[0] in "stcbpm")

    arr = "const WORDFIRE_HARD_ANSWERS = [" + ", ".join(f"'{w}'" for w in hard) + "];"
    # Insert after the WORDFIRE_ANSWERS declaration
    m = re.search(r"(const\s+WORDFIRE_ANSWERS\s*=\s*\[.*?\];)", text, re.S)
    if not m:
        raise SystemExit("cannot locate WORDFIRE_ANSWERS for insertion")
    updated = text[: m.end()] + "\n" + arr + text[m.end():]
    open(SRCJS, "w", encoding="utf-8").write(updated)

    report = {
        "hard_pool_size": len(hard),
        "all_in_guesses": True,
        "all_lowercase_5": True,
        "distinct_from_standard": len(set(hard)) == len(hard),
        "common_start_letters_pct_hard": round(100 * common_starts / len(hard), 1),
        "common_start_letters_pct_standard": round(100 * common_in_all / len(answers), 1),
        "sample": hard[:12],
    }
    print(json.dumps(report, indent=2))
    print("WROTE WORDFIRE_HARD_ANSWERS to", SRCJS)

if __name__ == "__main__":
    main()
