# Story 147: play-counter-pattern Cinder amendment (Session 66, P1, docs only)

**Status:** Ready for development (Session 66, 2026-11-19).
**Author:** Quinn, Business Analyst.
**Priority:** P1. Docs amendment, included in the Story 145 PR.
**Assigned to:** **Riven**, same owner and same PR as Story 145. Zero website bytes.
**Base commit:** `f26554e` (main, v0.52.0 released).
**Design contract:** `flambeee-team/design-handoff.md`, Story 147 sections 1 through 8. Design-owned observable criteria live in section 6 of that contract; the functional criteria below test the same doc from the requirements side. On any conflict between the doc and the build as reviewed, the build wins and the doc is reconciled to it.
**Pattern source:** `docs/play-counter-pattern.md` as shipped (Story 122, v0.45.0).
**Jakebot ruling (binding):** #215's detail-view clause is re-scoped to a follow-up issue across Cinder, Afterglow, and Typewreck; #215 must not be closed on a false all-criteria-met claim.

## Summary

The shipped pattern doc describes Typewreck-shaped counting only. Add a Cinder section that records the Cinder counting unit (entry into `enterWilderness()` after the daily-fight gate), the re-entry consequence, and the persistent-shell display rule, and record that #215's detail-view clause is re-scoped to a follow-up issue for the three shipped counters. Docs bytes only under `docs/play-counter-pattern.md`, in the same PR as Story 145.

## Requirements

### 1. Cinder section contents

The new section must contain all four items: the counting unit (entry into `enterWilderness()` after the gate at `dayState.fightsUsed < 15`), the re-entry consequence (non-combat treasure entries count again on re-entry), the persistent-shell display rule (beside `#statusLine`, outside `#display`, rendered on boot and after every increment, 0 on a first visit), and the single key plus cap plus helper names (`flambeee-cinder-plays`, 9007199254740991, `playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`).

### 2. Re-scope note

The section must record that #215's detail-view clause is re-scoped to a follow-up issue covering the three shipped counters (Cinder, Afterglow, Typewreck), with the follow-up issue number named, and that #215 stays open until that batch lands. The doc must not claim #215 is fully satisfied by the game-page line.

### 3. Zero website bytes

The amendment touches `docs/play-counter-pattern.md` only. `git diff --stat` on `website/` for this file reads empty. No `CACHE_VERSION` line is touched by it.

## Acceptance criteria (BDD, functional)

1. Given the merged pattern doc, when the Cinder section is read, then it names the counting unit as entry into `enterWilderness()` after the daily-fight gate.
2. Given the Cinder section, when it is read, then it states the re-entry consequence (non-combat treasure entries count again on re-entry).
3. Given the Cinder section, when it is read, then it states the persistent-shell display rule (beside `#statusLine`, outside `#display`, boot plus every increment, 0 on a first visit).
4. Given the Cinder section, when it is read, then it records the single key `flambeee-cinder-plays` with cap 9007199254740991 and the helper names `playsMem`, `sanitizePlays`, `loadPlays`, `renderPlays`, `bumpPlays`.
5. Given the Cinder section, when it is read, then it records that #215's detail-view clause is re-scoped to a follow-up issue across the three shipped counters and that #215 stays open until that batch lands.
6. Given the Story 145 PR diff, when the docs portion is inspected, then zero website bytes come from the pattern amendment and no `CACHE_VERSION` line is touched by it.

## Out of scope

Any website byte, any cache line, any change to the Typewreck or Afterglow sections beyond what the Cinder addition requires, the #215 AC amendment itself and the follow-up issue (release-wave follow-ups, not this story), any new game or mechanic. Do not touch `website/index.html`.

## Definition of done

One Cinder section present with the four required items, one re-scope note naming all three shipped counters and the follow-up issue number, zero website bytes in the amendment diff, and every key, name, number, and hook in the section matching the Story 145 build exactly.
