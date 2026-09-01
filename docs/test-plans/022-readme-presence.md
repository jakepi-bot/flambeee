# Test Plan: 022 - README Presence

## Goal
Verify Cinder is listed in README.md with correct descriptions, and all external links are updated to the same-origin `flambeee.com` domain.

## Verification Checklist

| Scenario | Check | Method | Success Criterion |
| :--- | :--- | :--- | :--- |
| 1 | Cinder is listed | `grep` / Manual | Section exists with title, desc, bullets, Play link |
| 2 | Play links same-origin | `grep` + HTTP check | 5 links point to `https://flambeee.com/games/*.html` |
| 3 | Game Hub link updated | `grep` + HTTP check | Points to `https://flambeee.com` |
| 4 | No stale links | `grep "htmlpreview"` | 0 matches |
| 5 | Format consistency | Visual / Diff | Cinder section matches others (emoji, spacing, style) |
| 6 | Tone compliance | Review | Direct, dry humor, no AI tells (no em dashes, no heavy emoji) |

## Edge Cases
- **Link Accuracy:** Verify `wordfire.html` (or equivalent) matches the actual filename in `share/Flambeee/games/`.
- **Legacy Em Dashes:** Ensure no NEW em dashes are introduced, while ignoring existing ones on lines 5, 7, 13, 31, 37, 128-130.
- **Link Dead-ends:** Perform `curl` on all 5 Play links to ensure 200 OK.
