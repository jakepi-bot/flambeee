# Flambeee session cadence policy

Status: proposed (PR `feat/cadence-policy`, reverses on team objection).
Decided by: jakebot advisory 2026-11-05 (Option B), adopting the CEO's
2026-11-05 direction to stop shipping a new game every day.
Inputs: `docs/legacy-games-apps-audit.md` (t_60577470),
`docs/new-game-cadence-audit-2026-11-05.md` (t_7e655cf6),
recommendation task t_39a7024b (in flight, no objection recorded).
jakebot rule consult: hermes session `local-63d0e943a8b917182dd08bf7054de3bdd33a70a5f6fd80802a0856f50799e9a8.

## What the audits show

1. Legacy cost is near zero: 14 shipped items, all static single files with
   zero dependencies, zero open issues, ~0 hr/month steady state. Cinder is
   the only historically expensive file (23 commits) and has been quiet
   since 2026-10-15.
2. New-game output is 27% of sessions and ~10% of insertions over the last
   60 days, but value is unmeasured: no play telemetry exists anywhere, four
   of nine recent launches were never announced, and one full build
   (Snapline, 755 lines) was discarded pre-merge.
3. The binding constraint is not legacy maintenance but per-release shared
   tax (CACHE bump, What's New, release cut, noon post) plus QA capacity per
   new file. Slowing new games does not cut legacy cost; it redirects session
   capacity toward instrumentation, rotation gaps, and dead-weight cleanup.

## Options considered

| Option | Rule | Cost | Risk | Upside |
|---|---|---|---|---|
| A. Daily new game (status quo) | Every session may ship new | Highest QA + release-tax load; maintenance surface grows unbounded | Burnout of the release chain; more unannounced launches; value still unmeasured | Maximum shots on goal |
| B. Fixed weekly split (RECOMMENDED) | Mon/Wed/Fri new-game, Tue/Thu/Sat/Sun legacy maintenance | 3 new builds/week max; 4 sessions/week for backlog + instrumentation | Needs the enforcement below or it drifts back to A | Sustainable; backlog visibly shrinks; outcome data gets built |
| C. Maintenance sprint month | One week/month all maintenance | Whole-week context switch; 3 weeks of debt pile up first | Debt goes stale before the sprint; sprint week ships nothing | Simple calendar |

Recommendation: **Option B**. It spreads maintenance instead of batching it,
is enforceable by date (no judgement calls), and matches the CEO's "not
every day" without swinging to "never".

## The operational rule

- **Mon / Wed / Fri: NEW-GAME days.** New builds allowed; backlog work still allowed.
- **Tue / Thu / Sat / Sun: LEGACY days.** Work `docs/legacy-maintenance-backlog.md`
  only. New-game builds are out of scope.
- **Anything broken jumps the queue on any day** (game unplayable, site down,
  compliance block). Repairs are never cadence violations.
- **Enforcement, not memory:** Wave 1 planning runs
  `python3 scripts/cadence_mode.py [--date YYYY-MM-DD]` (defaults to today)
  and scopes the session to the printed mode. The mode line is recorded in
  `flambeee-team/session-plan.md`. If the script is not run, the session plan
  is incomplete.

## Revisit tripwires (any one fires a policy rewrite)

1. Legacy backlog above 40 open tracked items for two straight weeks:
   convert one new-game day to legacy.
2. Fewer than 2 shippable increments per 14 days for three weeks running:
   drop to 2 new-game days.
3. Legacy incidents eat more than 25% of new-game sessions in any month:
   swap the worst-hit day.

If none fire in a quarter, the split is holding.

## Backlog and audits

- Backlog: `docs/legacy-maintenance-backlog.md` (M-1 through M-4, tracked as
  GitHub issues with the `maintenance` label).
- Legacy audit: `docs/legacy-games-apps-audit.md` (branches
  `origin/docs/legacy-audit-t60577470`).
- Cadence audit: `docs/new-game-cadence-audit-2026-11-05.md` (branch
  `origin/docs/cadence-audit-t7e655cf6`).

## Reversal

This policy reverses by team review of its PR. A single team-member objection
with evidence (tripwire math or audit correction) reopens the option table;
two sessions of silent non-compliance (mode line missing or wrong-scoped
sessions) escalate to the CEO per the existing DM rules.
