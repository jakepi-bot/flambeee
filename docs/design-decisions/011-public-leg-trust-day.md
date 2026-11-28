# 011: Public-leg gate predicate and www NOTE policy (Session 75)

Contested call: how strictly the noon poster decides a staged text
"contains flambeee.com", and whether a www failure blocks a post.

Decision (Rook, trust day):
1. Predicate is a plain case-insensitive substring on the staged text.
   No boundary checks. `flambeee.com.evil.tld` fires the gate.
2. www failure is a loud NOTE and never blocks. Apex failure always
   blocks (probe exit 1, poster fail_loud, pending kept).

Why: a false positive costs one 12 s probe run. A false negative
ships a dead link, which is the exact defect from 2026-11-27. The
held post links the apex only, so gating on apex is sufficient and
www stays advisory. Never "log and continue" on apex.

Locked: the gate position (after DRY_RUN and pre-flights), the
TLS-valid definition (chain plus hostname plus dates), and the
four-case stub matrix in design-handoff Section 1.7.
