---
id: "335"
title: "Reconcile ticket records flagged by the architecture review"
status: done
priority: medium
blocked_by: []
type: fix
tags: ["arch-review"]
---

# Reconcile ticket records flagged by the 2026-09-16 architecture review

## Why

The repo's honest-records convention (AGENTS.md: verified claims, no faked boxes). The review found done tickets whose checked ACs or body claims are false in source, and open tickets that are stale or already satisfied. Amend honestly — annotate what actually shipped, never fake a box. Per #285 baseline rules these are targeted forward amendments, not bulk backfill.

## Done tickets with false/overstated records (each verified 2026-09-16)

- **#258** — checked AC "client seeds status from the overlay-joined `/api/map` payload; island no longer the status source of truth". As-built: topic map pages seed from the generate-time baked island (`tools/generate_map_page.py:250-265` → `assets/components/MapView.js:21` → `store.js`); only the aggregate index reads the live overlay (#279). Values are overlay-derived, but the described mechanism doesn't exist.
- **#257** — consumers plan "serve.py GET /api/map emits `id` + typed edges": not implemented (`tools/serve.py:195-199` — no `id`, no edges array). Was a blast-radius item, not a final AC checkbox.
- **#141** — "Modified files: `map_parser.py` — add `sources` field to Topic dataclass": field was never added (`map_parser.py:23-33`).
- **#112** — checked AC "README links to the live demo" (no live-demo link in README.md) and "deploys automatically on push to main" (`.github/workflows/pages.yml` gates the build on a `v*` tag or manual dispatch).
- **#090** — closed `done` with 0 checked ACs and no Resolution section; functionality is real (`tools/check-update.py` + mise `update:check`). Add an honest Resolution.

## Open tickets to triage (close or re-scope)

- **#162** (copy code blocks) — already shipped via #173/CodeBlockToolbar. Close.
- **#199** — several findings already fixed: XSS claim invalid (`GraphView.js:43` measures via escaped Preact render), GenButton interval gone, LessonActions error handling shipped. Remaining valid: quick-check FOUC (`tools/lib/preact_page.py:79-89` emits no blocking `typography-prefs.js`, confirmed in `library/iceberg-workspace/lessons/review/quick-check.html`), dead "Explore subtopics" button (`TopicCard.js:53`), unstyled `.rating-*`/`.assess-buttons`/`.gen-progress`/`.leads-to-btn` classes, scaffold import-map strip, port quick-check to page_template and delete preact_page.py. Re-scope to the remaining list.
- **#066** (generation error/retry UX) — largely mooted by the honest-prompt model (#319 removed server-driven generation). Re-scope or close with rationale.
- **#046** — all ACs already checked but status still open. Close.
- **#047** — leads_to data model exists (`map_parser.py` EDGE_TYPES, #320); the discovery UX half is unstarted. Re-scope to the UX or close.

## Acceptance criteria

- [x] Each listed done ticket annotated honestly (amended AC text or an as-built note; no fabricated evidence)
- [x] Each listed open ticket closed or re-scoped with an explicit remaining-work list
- [x] `tkt validate` finding count does not increase
- [x] #199's surviving scope is accurate (spot-verified against source, not copied from this ticket blindly)

## Verification outcome (2026-09-17 — deltas from this ticket's own claims)

Every claim above was re-verified against source before acting (per the convention this
ticket enforces). Deltas found:

- **#258 claim is now STALE, not false**: commit `40aedb9` (#338, 2026-09-17) shipped the
  live `/api/map/{domain}` fetch at page load (`generate_map_page.py:212-224`), so the
  mechanism the AC described now exists in a different form. The #258 annotation records
  both the at-close truth and the #338 correction.
- **#046 close-claim is REFUTED**: #046 has TWO unchecked ACs ("all done" leads_to
  presentation, "everything available" choice). Closing it as "all ACs checked" would
  have faked a record. Re-scoped open instead.
- **#047 "no discovery UX" overstated**: domain-level leads_to discovery renders today
  (`IndentedTreeView.js:92-97`); only the completion-triggered/start-domain UX is
  unstarted. Re-scope reflects that.
- **#199 item precision**: only `.assess-buttons` + rating rules are genuinely unstyled;
  `.gen-progress` is dead, `.leads-to-btn` styled on map pages. XSS/GenButton/
  LessonActions/Generate-quiz items already fixed. Full re-scope section added to #199.

## Resolution (2026-09-17)

Reconciled all ten ticket records flagged by the 2026-09-16 architecture review, with
every claim re-verified against source first (two claims from this ticket itself were
refuted in the process — the #046 close and the #047 flat claim — and the #258 claim
was overtaken by #338's same-day live-refresh fix). Five done tickets now carry honest
as-built annotations (#258, #257, #141, #112, #090); two open tickets were closed with
verified-evidence resolutions (#162 duplicate-of-#173, #066 mooted-by-#319); three were
re-scoped to explicit verified remaining-work lists (#199, #046, #047). `tkt validate`
findings went 127 → 124 (no increase). Verified via: source greps quoted in each
ticket, CodeBlockToolbar/style.css/page-shell.js inspection for #162, serve.py route
inventory for #066, and preact_page.py/TopicCard.js/scaffolds for #199.
