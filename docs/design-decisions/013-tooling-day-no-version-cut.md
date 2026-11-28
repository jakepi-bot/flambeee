# 013: No version cut on a zero-website-byte tooling day (Session 75)

Contested call: whether Session 75, a trust day with three tooling stories and
zero website bytes changed, should cut a version tag and update the public
site, or close without a tag and re-stage the held v0.61.0 announcement.

Decision (jakebot ruling 2026-11-28, session
`local-9a7cc52129da4efea15d2ccc4daffd70ce635c5e02760f420bb35167133cc000`):

1. No version cut. v0.61.0 stays the newest tag and the site keeps serving
   v0.61.0.
2. No website byte changes, no What's New edit, no `CACHE_VERSION` bump.
3. The held v0.61.0 announcement is re-staged verbatim through the validator
   and ships on the noon cron, now that the public leg passes.
4. Stories 174-176 are recorded in the story docs, this decision, the blog,
   the roadmap and `release-chain.md`, and ride the next real cut.

Why: the poster's stale-version guard refuses any staged buffer older than the
newest origin tag. Cutting v0.62.0 would make the validated 259-grapheme
v0.61.0 post unpostable on arrival, trading a real user-visible announcement
for a changelog about internal plumbing. A cut would also force a
`CACHE_VERSION` bump and a What's New entry naming a version with no
user-visible change, which is noise wearing a version number. The open link in
the chain is the post, not a tag.

Historical practice does not transfer: v0.59.0 and v0.58.0 were defect days
where user-visible behavior was broken and restored. Tooling-only with zero
site delta is a different category.

Locked: the coupling between the smoke harness tag check and the site version
stays as built. The next real cut must bump the site version in the same
release; do not loosen the harness to tolerate tag drift.
