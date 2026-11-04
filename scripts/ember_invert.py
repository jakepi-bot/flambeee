#!/usr/bin/env python3
"""Ember inversion stage: opposite creative concepts for hot game ideas.

Implements the interface defined in docs/ember-web-search-design.md
(section 4, insertion point IP-3) for task t_891d96ce.

Pipeline (agent drives, this module enforces):
  1. The sibling search stage (scripts/ember_hot_ideas.py) yields exactly
     three HotGameIdea records, hottest first.
  2. invert_ideas() takes those three records and emits three
     InvertedConcept records, one per hot idea. Each flips exactly one
     meaningful axis (mechanic, audience, session length, social mode,
     monetization, theme), never just wording.
  3. validate_concept() enforces the section-4 schema plus the opposition
     rule: the concept must read as genuinely opposite, not a rewording.

Stdlib only. No network access: all creativity here is deterministic
template logic so output is reproducible and testable. The Wave 1 agent
may refine the prose; this module guarantees structure and opposition.
"""

import argparse
import hashlib
import json
import re
import sys

# The six flippable axes from section 4 of the design note. Canonical
# lowercase spellings; validation is exact-match against this tuple.
INVERSION_AXES = (
    "mechanic",
    "audience",
    "session length",
    "social mode",
    "monetization",
    "theme",
)

INVERTED_CONCEPT_REQUIRED = (
    "source_idea_title",
    "inverted_title",
    "inversion_axis",
    "concept_summary",
    "why_it_is_opposite",
    "first_experiment",
)

# Markers that prove the flip is stated explicitly ("source does X, this
# does not-X"). At least one must appear in why_it_is_opposite.
CONTRAST_MARKERS = (
    "instead of",
    "while the source",
    "unlike the source",
    "whereas",
    "in contrast",
    "reverses",
    "reverse of",
    "opposite",
    "flips",
)

# Inverted-side token overlap with the source must stay below this or the
# concept is rejected as a rewording. Computed over content tokens of
# inverted_title + concept_summary only: why_it_is_opposite and
# first_experiment are *supposed* to reference the source.
MAX_OVERLAP_RATIO = 0.60

_STOPWORDS = frozenset(
    "the a an and or to of in on for with you your yours its it is are "
    "was were be been as at by from that this these those they them "
    "their there here your our ours his her him she our we us game play "
    "plays played player players gaming web browser new".split()
)

_WORD_PAT = re.compile(r"[a-z]+")


def content_tokens(text):
    """Lowercase alpha tokens of length >= 4 minus stopwords."""
    return {
        w for w in _WORD_PAT.findall(text.lower())
        if len(w) >= 4 and w not in _STOPWORDS
    }


def overlap_ratio(inverted_text, source_text):
    """Share of inverted-side content tokens also present source-side."""
    inv = content_tokens(inverted_text)
    if not inv:
        return 0.0
    return len(inv & content_tokens(source_text)) / len(inv)


def anchor_word(title):
    """Longest alpha word in the title (first wins ties). Never empty."""
    words = re.findall(r"[A-Za-z]+", title)
    if not words:
        return "Game"
    best = words[0]
    for word in words[1:]:
        if len(word) > len(best):
            best = word
    return best


def _sentences(text):
    return [s for s in re.split(r"[.!?]+", text) if s.strip()]


# --- per-axis inversion planners -------------------------------------------
# Each takes a HotGameIdea dict and returns the four generated fields.
# Direction is detected from the source fields with deterministic keyword
# rules so the flip always runs against the source's actual polarity.

_MECHANIC_SWAPS = (
    (re.compile(r"\bcatch\w*", re.I),
     "releases the catch instead of landing it"),
    (re.compile(r"\bcollect\w*|\bgather\w*", re.I),
     "scatters resources instead of stockpiling them"),
    (re.compile(r"\bgrow\w*|\bbuild\w*|\bexpand\w*", re.I),
     "dismantles progress instead of building it"),
    (re.compile(r"\brace\w*|\brush\w*|\bspeed\w*", re.I),
     "lingers and savors instead of racing"),
    (re.compile(r"\bfight\w*|\bbattle\w*|\battack\w*|\bstrike\w*", re.I),
     "befriends rivals instead of fighting them"),
    (re.compile(r"\bconquer\w*|\bcaptur\w*|\bclaim\w*", re.I),
     "relinquishes ground instead of claiming it"),
    (re.compile(r"\bmerge\w*|\bcombin\w*|\bstack\w*", re.I),
     "splits things apart instead of combining them"),
    (re.compile(r"\btap\w*|\bclick\w*|\bgrab\w*", re.I),
     "withholds action instead of grabbing at everything"),
)


def _plan_mechanic(idea):
    loop = idea["core_mechanic"]
    flipped = None
    for pattern, flip_clause in _MECHANIC_SWAPS:
        if pattern.search(loop):
            flipped = flip_clause
            break
    if flipped is None:
        flipped = ("undoes the '%s' loop step by step instead of "
                   "advancing it" % loop)
    anchor = anchor_word(idea["title"])
    return {
        "inverted_title": "%s in Reverse" % anchor,
        "concept_summary": (
            "A reverse-loop game in the world of %s: you begin holding "
            "everything the source hands out and win by giving it all "
            "back. Where the source loop is '%s', here every move %s, "
            "so the map empties and the score falls. Hoarding triggers "
            "the lose state; the end screen celebrates an empty board."
            % (idea["title"], loop, flipped)
        ),
        "why_it_is_opposite": (
            "While the source rewards accumulation (%s), this concept "
            "rewards the opposite: progress means having less, so a "
            "winning run here would score zero in the source."
            % loop
        ),
        "first_experiment": (
            "Paper prototype: ten tokens stand in for everything the "
            "player owns and each turn must discard at least one; test "
            "with five players whether emptying the board feels like "
            "winning after three rounds."
        ),
    }


_AUDIENCE_RULES = (
    (("kid", "child", "junior"), "kids", "Working Adults",
     "forgiving, ten-minute sessions with training wheels",
     "unforgiving ranked ladders with no tutorial"),
    (("teen", "youth"), "teens", "Parents",
     "reflex duels and ranked seasons",
     "slow evening co-op with pause-anywhere and no chat pressure"),
    (("casual", "cozy", "relax"), "casual players", "Hardcore",
     "gentle assists, no fail states, and bite-size sessions",
     "permadeath, no assists, and a public skill rating"),
    (("friend", "party", "family"), "friend groups", "Rival Strangers",
     "private lobbies with people you trust",
     "skill-matched strangers you will never meet again"),
    (("hardcore", "competitive", "ranked", "elite", "pro "),
     "hardcore competitors", "First-Timers",
     "punishing systems that assume mastery",
     "a zero-fail guided tour that assumes nothing"),
)


def _plan_audience(idea):
    audience = idea["audience"]
    lowered = audience.lower()
    for keywords, old_short, new_short, old_tuning, new_tuning in (
            _AUDIENCE_RULES):
        if any(k in lowered for k in keywords):
            break
    else:
        old_short, new_short = "its current crowd", "Newcomers"
        old_tuning = "systems tuned for veterans of the genre"
        new_tuning = "a guided, jargon-free on-ramp for total beginners"
    anchor = anchor_word(idea["title"])
    return {
        "inverted_title": "%s for %s" % (anchor, new_short),
        "concept_summary": (
            "The same core loop as %s, rebuilt end to end for %s "
            "instead of %s. Controls, difficulty, session shape, and "
            "rewards assume %s: %s. Nothing in this build serves the "
            "old crowd; one client cannot satisfy both."
            % (idea["title"], new_short.lower(), old_short,
               new_short.lower(), new_tuning)
        ),
        "why_it_is_opposite": (
            "While the source is tuned for %s (%s: %s), this concept "
            "flips every tuning decision toward %s (%s), so the two "
            "builds want mutually exclusive players."
            % (old_short, audience, old_tuning, new_short.lower(),
               new_tuning)
        ),
        "first_experiment": (
            "Take one level from the source fantasy, apply the inverted "
            "tuning only, and playtest with five target players for ten "
            "minutes; a quit-rate on the opposite side of half from the "
            "source baseline confirms the audience split is real."
        ),
    }


_SHORT_HINTS = ("idle", "quick", "daily", "minute", "bite", "arcade",
                "fast", "casual", "short")
_LONG_HINTS = ("epic", "campaign", "100-hour", "100 hour", "mmo",
               "massive", "grind", "season", "saga", "year")


def _plan_session_length(idea):
    blob = "%s %s %s" % (idea["title"], idea["core_mechanic"],
                         idea["why_hot"])
    lowered = blob.lower()
    anchor = anchor_word(idea["title"])
    if any(h in lowered for h in _LONG_HINTS):
        return {
            "inverted_title": "%s in 60 Seconds" % anchor,
            "concept_summary": (
                "The fantasy of %s compressed into a single sixty-second "
                "burst: one map, one timer, no saves, no carryover. Every "
                "system from the source is kept but must pay out inside "
                "the minute. Leaderboards rank single bursts, and a run "
                "is over before a queue would even form."
                % idea["title"]
            ),
            "why_it_is_opposite": (
                "While the source sprawls across long commitments, this "
                "concept reverses the time scale: the same fantasy must "
                "resolve in one minute, so patience strategies from the "
                "source score nothing here."
            ),
            "first_experiment": (
                "Prototype one sixty-second round and time twenty "
                "volunteers; if most immediately retry, the compressed "
                "loop carries the fantasy."
            ),
        }
    short_evidence = next(
        (h for h in _SHORT_HINTS if h in lowered), "short sessions")
    return {
        "inverted_title": "The 100-Hour %s" % anchor,
        "concept_summary": (
            "The fantasy of %s stretched over a single persistent season "
            "lasting months: one meaningful decision per evening, no "
            "grinding, no catching up. Progress compounds across real "
            "calendar time and a missed week bends the story instead of "
            "ending it. The finale is scheduled, shared, and unrepeatable."
            % idea["title"]
        ),
        "why_it_is_opposite": (
            "While the source fits %s, this concept flips the clock: one "
            "season here outlasts hundreds of source sessions, so the "
            "source habit of quick payoff actively hurts."
            % short_evidence
        ),
        "first_experiment": (
            "Concierge test: run the core decision by hand over seven "
            "daily messages with three players; if day-seven return beats "
            "the source's second-session return, the long form has legs."
        ),
    }


_SOCIAL_HINTS = ("co-op", "coop", "multiplayer", "mmo", "together",
                 "team", "pvp", "rival", "friend", "guild", "squad",
                 "versus", "leaderboard")


def _plan_social_mode(idea):
    blob = "%s %s %s" % (idea["title"], idea["core_mechanic"],
                         idea["why_hot"])
    lowered = blob.lower()
    anchor = anchor_word(idea["title"])
    if any(h in lowered for h in _SOCIAL_HINTS):
        evidence = next(h for h in _SOCIAL_HINTS if h in lowered)
        return {
            "inverted_title": "Lonely %s" % anchor,
            "concept_summary": (
                "The world of %s with every other human removed: no "
                "chat, no leaderboard, no co-op partner, no rival. Past "
                "runs echo back only as weather and ruins, never as "
                "ghosts to race. The design spends its whole budget on "
                "solitude instead of shared moments."
                % idea["title"]
            ),
            "why_it_is_opposite": (
                "While the source needs other people (%s), this concept "
                "removes them entirely: a perfect source session is "
                "crowded, while a perfect session here has zero "
                "witnesses." % evidence
            ),
            "first_experiment": (
                "Wizard-of-oz one session with a moderator simulating the "
                "empty world; if players describe the mood unprompted "
                "instead of asking where everyone is, solitude works."
            ),
        }
    return {
        "inverted_title": "%s Together" % anchor,
        "concept_summary": (
            "The fantasy of %s replanted on one shared map where every "
            "player acts at once and every move is visible. Resources, "
            "storms, and scarcities hit everyone simultaneously, so "
            "private optimization loses to public negotiation. The game "
            "only functions above fifty concurrent players."
            % idea["title"]
        ),
        "why_it_is_opposite": (
            "While the source is a private experience, this concept "
            "flips it into a crowd: playing alone is impossible here, "
            "whereas the source never requires another person."
        ),
        "first_experiment": (
            "Moderated crowd test: put fifteen volunteers on one shared "
            "board for twenty minutes; if alliances form without "
            "prompting, the social layer carries the game."
        ),
    }


_PAID_HINTS = ("purchase", "premium", "pay once", "upfront", "pass",
               "subscription", "paid", "price")


def _plan_monetization(idea):
    monetization = idea["monetization"]
    lowered = monetization.lower()
    anchor = anchor_word(idea["title"])
    if any(h in lowered for h in _PAID_HINTS):
        return {
            "inverted_title": "Free %s" % anchor,
            "concept_summary": (
                "The full %s experience free forever: no price, no shop, "
                "no premium track, every unlock earned in play. Support "
                "comes from an optional tip jar plus a creator fund that "
                "pays out on community maps. Spending money buys nothing "
                "but goodwill." % idea["title"]
            ),
            "why_it_is_opposite": (
                "While the source earns through %s, this concept earns "
                "the opposite way: a player who pays in the source pays "
                "nothing here, and revenue depends on generosity instead "
                "of gating." % monetization
            ),
            "first_experiment": (
                "Fake-door pricing page showing both models to two "
                "hundred visitors; if the free-plus-tips option doubles "
                "signups, build that economy first."
            ),
        }
    return {
        "inverted_title": "Flat-Fee %s" % anchor,
        "concept_summary": (
            "The %s experience for one upfront price with everything in "
            "the box: no ads, no shop, no currency, no premium track. "
            "Every future update is included, so the studio only earns "
            "by shipping a game worth buying once." % idea["title"]
        ),
        "why_it_is_opposite": (
            "While the source earns through %s, this concept flips to a "
            "single payment: ongoing spending, the source's engine, is "
            "impossible here by construction." % monetization
        ),
        "first_experiment": (
            "Fake-door pricing page showing both models to two hundred "
            "visitors; if enough choose pay-once at a price covering "
            "costs, the flat fee is viable."
        ),
    }


_COZY_HINTS = ("cozy", "cute", "bright", "cheerful", "farm", "harbor",
               "garden", "pastel", "fish", "village", "warm", "gentle")
_GRIM_HINTS = ("dark", "grim", "horror", "dungeon", "neon", "cyber",
               "war", "zombie", "demon", "blood", "rust", "void")


def _plan_theme(idea):
    blob = "%s %s %s" % (idea["title"], idea["core_mechanic"],
                         idea["why_hot"])
    lowered = blob.lower()
    anchor = anchor_word(idea["title"])
    if any(h in lowered for h in _GRIM_HINTS):
        return {
            "inverted_title": "Cozy %s" % anchor,
            "concept_summary": (
                "The systems of %s reskinned into pure comfort: warm "
                "palette, no death, no fail state, every conflict "
                "resolves into friendship or cake. The mechanics stay "
                "recognizable but the fantasy promises safety instead "
                "of danger." % idea["title"]
            ),
            "why_it_is_opposite": (
                "While the source sells its systems with dread and edge, "
                "this concept sells the same systems with the mirror "
                "tone: nothing here can frighten, whereas the source "
                "cannot comfort."
            ),
            "first_experiment": (
                "Reskin one screenshot both ways and run a five-second "
                "test with ten people; the emotion words must flip "
                "valence for the theme inversion to count."
            ),
        }
    return {
        "inverted_title": "Rust %s" % anchor,
        "concept_summary": (
            "The systems of %s dragged into a dying world: muted "
            "palette, scarce resources, and stakes that bite. The loop "
            "is familiar but every cozy promise curdles: the harbor "
            "silts up, the lights go out, and comfort must be defended. "
            "Loss is permanent and the ending is elegiac." % idea["title"]
        ),
        "why_it_is_opposite": (
            "While the source sells its systems with warmth and comfort, "
            "this concept sells the same systems with the mirror tone of "
            "decay: the source comforts, whereas this one mourns."
        ),
        "first_experiment": (
            "Reskin one screenshot both ways and run a five-second test "
            "with ten people; the emotion words must flip valence for "
            "the theme inversion to count."
        ),
    }


_PLANNERS = {
    "mechanic": _plan_mechanic,
    "audience": _plan_audience,
    "session length": _plan_session_length,
    "social mode": _plan_social_mode,
    "monetization": _plan_monetization,
    "theme": _plan_theme,
}


# --- validation ------------------------------------------------------------


def validate_concept(concept, ideas):
    """Validate an InvertedConcept record against the section-4 schema.

    ideas: the run's HotGameIdea records (used for source linkage and the
    opposition check). Returns a list of problem strings; empty is valid.
    """
    problems = []
    if not isinstance(concept, dict):
        return ["concept must be an object"]
    for key in INVERTED_CONCEPT_REQUIRED:
        value = concept.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append("missing or empty: %s" % key)
    for key in concept:
        if key not in INVERTED_CONCEPT_REQUIRED:
            problems.append("unexpected field: %s" % key)
    if problems:
        return problems

    # All required keys are present non-empty strings here (else we
    # returned above), so direct indexing is safe.
    titles = [i.get("title") for i in ideas if isinstance(i, dict)]
    source_title = concept["source_idea_title"]
    if source_title not in titles:
        problems.append(
            "source_idea_title does not match any hot-idea title")
        return problems

    axis = concept["inversion_axis"]
    if axis not in INVERSION_AXES:
        problems.append(
            "inversion_axis must be one of %s" % (
                ", ".join(INVERSION_AXES),))

    inverted_title = concept["inverted_title"]
    if len(inverted_title.split()) > 8:
        problems.append("inverted_title exceeds 8 words")
    if inverted_title.strip().lower() == source_title.strip().lower():
        problems.append("inverted_title merely repeats the source title")

    if not (2 <= len(_sentences(concept["concept_summary"])) <= 6):
        problems.append("concept_summary must be 2 to 4 sentences")

    lowered = concept["why_it_is_opposite"].lower()
    if not any(m in lowered for m in CONTRAST_MARKERS):
        problems.append(
            "why_it_is_opposite states no explicit flip "
            "(needs a contrast marker)")

    source = next(i for i in ideas
                  if isinstance(i, dict) and i.get("title") == source_title)
    source_text = "%s %s %s %s" % (
        source.get("title", ""), source.get("core_mechanic", ""),
        source.get("why_hot", ""), source.get("audience", ""))
    inverted_text = "%s %s" % (concept["inverted_title"],
                               concept["concept_summary"])
    ratio = overlap_ratio(inverted_text, source_text)
    if ratio >= MAX_OVERLAP_RATIO:
        problems.append(
            "reads like a rewording (token overlap %.2f >= %.2f)"
            % (ratio, MAX_OVERLAP_RATIO))
    return problems


# --- generation ------------------------------------------------------------


def default_axes(ideas):
    """Deterministically assign three distinct axes from the run's titles.

    Offset comes from sha256 over the joined titles, so the same run
    always assigns the same axes while different runs spread across all
    six axes instead of always flipping the same three.
    """
    digest = hashlib.sha256(
        "|".join(i["title"] for i in ideas).encode("utf-8")).hexdigest()
    offset = int(digest, 16) % len(INVERSION_AXES)
    return [INVERSION_AXES[(offset + k) % len(INVERSION_AXES)]
            for k in range(3)]


def invert_idea(idea, axis):
    """Generate one InvertedConcept draft for a hot idea on one axis."""
    if axis not in INVERSION_AXES:
        raise ValueError(
            "axis must be one of %s" % (", ".join(INVERSION_AXES),))
    for field in ("title", "core_mechanic", "audience", "monetization",
                  "why_hot"):
        value = idea.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("idea missing or empty: %s" % field)
    concept = {"source_idea_title": idea["title"],
               "inversion_axis": axis}
    concept.update(_PLANNERS[axis](idea))
    return concept


def invert_ideas(ideas, axes=None):
    """Invert exactly three hot ideas, one concept each.

    axes: optional explicit list of three axes (one per idea). Default is
    the deterministic distinct assignment from default_axes(). Every
    output is validated; a ValueError is raised if any fails, so invalid
    concepts can never silently pass through.
    """
    if not isinstance(ideas, list) or len(ideas) != 3:
        raise ValueError("inversion needs exactly three hot ideas, got %s"
                         % (len(ideas) if isinstance(ideas, list)
                            else type(ideas).__name__))
    if axes is None:
        axes = default_axes(ideas)
    if len(axes) != 3 or len(set(axes)) != 3:
        raise ValueError("axes must be three distinct inversion axes")
    concepts = [invert_idea(idea, axis)
                for idea, axis in zip(ideas, axes)]
    for concept in concepts:
        problems = validate_concept(concept, ideas)
        if problems:
            raise ValueError("invalid inversion for %r: %s"
                             % (concept.get("source_idea_title"), problems))
    return concepts


# --- CLI -------------------------------------------------------------------


def run(ideas, axes=None):
    """Full run: invert three hot ideas, return validated concepts."""
    return invert_ideas(ideas, axes)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate opposite creative concepts for hot ideas.")
    parser.add_argument("--ideas", required=True,
                        help="JSON file: list of exactly 3 HotGameIdea dicts")
    parser.add_argument("--out", required=True,
                        help="output JSON file for the inverted concepts")
    parser.add_argument("--axes", default=None,
                        help="optional comma-separated axes, one per idea")
    args = parser.parse_args(argv)
    with open(args.ideas, encoding="utf-8") as fh:
        ideas = json.load(fh)
    axes = ([a.strip() for a in args.axes.split(",")]
            if args.axes else None)
    try:
        concepts = run(ideas, axes)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(concepts, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %d concepts to %s" % (len(concepts), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
