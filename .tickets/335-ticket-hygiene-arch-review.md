---
id: "335"
title: "Reconcile ticket records flagged by the architecture review"
status: open
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

- [ ] Each listed done ticket annotated honestly (amended AC text or an as-built note; no fabricated evidence)
- [ ] Each listed open ticket closed or re-scoped with an explicit remaining-work list
- [ ] `tkt validate` finding count does not increase
- [ ] #199's surviving scope is accurate (spot-verified against source, not copied from this ticket blindly)

## Resolution

TBD
