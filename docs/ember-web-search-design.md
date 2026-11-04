# Ember Web Search: Audit and Extension Interfaces

Date: 2026-11-03. Status: design note, no code changed.

## 1. What exists today

Ember web search is prompt-defined, not code. There is no search module,
no query template, no parser, no store. Four call sites say the same thing:

| # | File | Line / anchor |
|---|---|---|
| 1 | `team/personas.md` (Ember responsibilities) | "Gathers product direction from three sources: GitHub enhancement requests, industry/market trends (web search), and community feedback on Bluesky" |
| 2 | `work-session-prompt.md` | Phase 1 step 4: "Use web_search to analyze current market trends relevant to the product" |
| 3 | `flambeee-team/parent-launcher-prompt.md` (ops tree, not in repo) | Wave 1 step 4: same wording as #2 |
| 4 | `flambeee-team/briefs/EMBER-brief.md` (ops tree, not in repo) | "If market research is needed, use web_search to analyze current trends relevant to Flambeee's products" |

`ARCHITECTURE.md` (ops tree) Wave 1 repeats the same one-liner.

### Query construction

Ad hoc. Whoever runs Ember / Wave 1 invents queries each session. No seed
list, no required operators, no record of what was asked. Grep over session
notes, SESSION-LOG, and plans shows zero logged queries.

### Parsing and ranking

Agent prose judgment. Results feed `docs/roadmap.md` priorities directly.
No scoring rubric, no threshold, no structured intermediate output.

### Source persistence

None. Verified by grep: no file in the repo stores result URLs or domains.
`docs/roadmap.md` records decisions, not sources. The community log records
GitHub/Bluesky interactions, not web sources. Consequence: the "do not reuse
a previous source" requirement (parent task t_b953d417, item 2) cannot be
enforced today. That gap is what the store below closes.

## 2. Persistent seen-sources store

Path: `docs/ember-seen-sources.json` (in repo, versioned, reviewable in PRs,
updated through the normal branch/commit/PR flow each session that runs a
search).

Shape: one JSON object keyed by canonical URL. Canonical form: lowercase
scheme+host, strip trailing slash, drop tracking params (`utm_*`, `fbclid`,
`gclid`), drop fragment.

```json
{
  "https://example.com/some-game-trend": {
    "domain": "example.com",
    "first_seen": "2026-11-04",
    "session": "session-51",
    "title_used": "rising cozy fishing sims",
    "sourced_idea": "harbor idle",
    "reuse_cooldown_sessions": 4
  }
}
```

Field rules:

- `domain`: registrable host, lowercase, no port. Stored per record so
  domain-level exclusion needs no second index.
- `first_seen`: ISO date the source was first used.
- `session`: work-session id that introduced it. Traceability.
- `title_used`, `sourced_idea`: what the source backed, for audit.
- `reuse_cooldown_sessions`: integer, default 4. How many later sessions
  must pass before the domain may appear again.

Exclusion rule (two tiers, so one good domain is not burned forever):

1. URL tier: an exact canonical URL in the store is never reused. Permanent.
2. Domain tier: a domain is excluded while
   `current_session_number - first_seen_session_number <= reuse_cooldown_sessions`
   for ANY record carrying that domain. After the cooldown lapses the domain
   is eligible again, but only with a URL not already in the store.

Session numbering: sessions are already numbered (`docs/stories/NNN-*`,
release versions). The search step resolves the current session number from
the session plan and applies the arithmetic above. Empty or missing store
means no exclusions (first-run behavior).

## 3. Hot game idea record (JSON Schema, draft 2020-12)

Exactly three of these are produced per search run, ranked hottest first.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://flambeee.com/schemas/hot-game-idea.json",
  "title": "HotGameIdea",
  "type": "object",
  "required": ["title", "source_url", "source_domain", "why_hot",
               "core_mechanic", "audience", "monetization", "retrieved_at"],
  "additionalProperties": false,
  "properties": {
    "title":          { "type": "string", "minLength": 1 },
    "source_url":     { "type": "string", "format": "uri" },
    "source_domain":  { "type": "string", "minLength": 1 },
    "why_hot":        { "type": "string", "minLength": 1 },
    "core_mechanic":  { "type": "string", "minLength": 1 },
    "audience":       { "type": "string", "minLength": 1 },
    "monetization":   { "type": "string", "minLength": 1 },
    "retrieved_at":   { "type": "string", "format": "date-time" }
  }
}
```

Field semantics: `title` is the idea in under 8 words. `source_url` is the
canonical URL (same canonicalization as section 2) and MUST NOT match any
exclusion in the store. `source_domain` is the registrable domain of that
URL. `why_hot` cites the evidence seen (1 to 2 sentences, numbers where the
source gives them). `core_mechanic` is the playable verb loop, not a genre
label. `audience` names who plays it. `monetization` names how it earns
(free, ads, cosmetic shop, pay-what-you-want, etc.). `retrieved_at` is
RFC 3339 UTC.

## 4. Inverted creative concept (JSON Schema, draft 2020-12)

One per hot idea, so three per run. Inversion flips a meaningful axis
(mechanic, audience, session length, social mode, monetization, theme),
never just wording.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://flambeee.com/schemas/inverted-concept.json",
  "title": "InvertedConcept",
  "type": "object",
  "required": ["source_idea_title", "inverted_title", "inversion_axis",
               "concept_summary", "why_it_is_opposite", "first_experiment"],
  "additionalProperties": false,
  "properties": {
    "source_idea_title": { "type": "string", "minLength": 1 },
    "inverted_title":    { "type": "string", "minLength": 1 },
    "inversion_axis":    { "type": "string", "minLength": 1,
                           "description": "The single axis flipped: mechanic, audience, session length, social mode, monetization, or theme." },
    "concept_summary":   { "type": "string", "minLength": 1 },
    "why_it_is_opposite":{ "type": "string", "minLength": 1 },
    "first_experiment":  { "type": "string", "minLength": 1 }
  }
}
```

Field semantics: `source_idea_title` MUST equal the `title` of one of the
three hot-idea records from the same run. `inverted_title` is the opposite
concept in under 8 words. `inversion_axis` names exactly one axis from the
list above. `concept_summary` is the playable sketch (2 to 4 sentences).
`why_it_is_opposite` states the flip explicitly ("source does X, this does
not-X") so sameness-by-synonym fails review. `first_experiment` is the
cheapest playable test that would falsify the concept.

## 5. Insertion points

All anchors are in Phase 1 / Wave 1 planning. No Wave 3 or release code is
touched.

- IP-1 source exclusion: `work-session-prompt.md` Phase 1 step 4, and the
  mirror steps in `parent-launcher-prompt.md` Wave 1 step 4 and
  `briefs/EMBER-brief.md` item 1. New behavior: load
  `docs/ember-seen-sources.json`, build exclusions (`-site:` operators or
  post-filter on canonical URL/domain), run queries, append new records.
- IP-2 top-3 hot ideas: new sub-step between Phase 1 step 4 (search) and
  step 8 (roadmap update). Rank to exactly three, emit section-3 records.
- IP-3 inversion: new stage after IP-2 output is fixed, before the roadmap
  update. Takes the three hot-idea records, emits three section-4 records.
  Output feeds roadmap priorities and the creative roadmap brief (task
  t_dd1da1b1), which keeps the existing-products focus while opening new
  directions.

## 6. Non-goals (explicitly not this task)

No query templates, no crawler code, no prompt edits, no store writes. Those
belong to t_e2e2cd14 (search + exclusion), t_891d96ce (inversion), and
t_dd1da1b1 (roadmap brief). This note is the interface they build against.
