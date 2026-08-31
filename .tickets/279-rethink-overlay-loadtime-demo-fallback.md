---
id: "279"
title: "Rethink progress overlay: read at load time with demo fallback + user-init handoff"
status: done
blocked_by: []
tags: [platform]
---

# Rethink progress overlay: read at load time with demo fallback + user-init handoff

## Context (design rethink — deferred from #278)

Today progress counts are **baked at generation time**: the page generators read
`.user/status-overlay.json` and write the resulting complete/in-progress counts into the
page's `#page-data` island. The overlay is server/build-side only — the browser never reads
it. Consequences:

- **Counts are a static snapshot.** They're only correct as of the last regen. A user who
  marks a topic done via `POST /api/map/.../status` updates the overlay JSON, but the
  committed HTML still shows the old count until the page is regenerated.
- **The demo/clean-checkout problem (the #278 footgun).** With no overlay present (fresh
  clone, GH Pages), regen re-bakes counts to 0 — which is why #278 had to commit a demo
  overlay AND stop the deploy from stripping it. That fix works but is indirect: we ship
  frozen demo numbers in the HTML and protect a committed JSON file, rather than deciding
  demo-vs-user at the moment of display.

## Proposed direction (rethink, not yet decided)

Move progress resolution to **load time (client-side)** instead of build time:

1. **Read the overlay in the browser at page load** — the page fetches/inlines the user's
   overlay and computes counts live, so marking a topic done reflects immediately without a
   regen.
2. **Demo fallback when no user data exists.** If there's no user overlay (the GH Pages /
   fresh-clone case), fall back to the committed demo overlay so the showcase still shows
   ink 3/5, godot 2, data-analytics 2. This is the same demo data #278 committed, but now
   it's an explicit *fallback*, not baked numbers.
3. **User-init handoff — stop showing demo once the user owns their progress.** The first
   time a user records real progress (or via an explicit UI action, e.g. "Start my own
   progress" / "Clear demo"), clear the demo view and switch to the user's own (initially
   empty) overlay. From then on, demo data is never shown for that user.

## Open design questions

- **Where does the browser read progress from?** localStorage? A `GET /api/.../status`
  fetch (serve only — no API on static GH Pages)? An inlined `#user-overlay` island the
  serve layer injects but GH Pages omits? The static-host case (no server) constrains this.
- **How is "the user has their own data now" detected?** First `set()` on any topic? A
  localStorage flag set by the init UI action? Needs to be robust across the served
  (serve.py) and static (GH Pages) contexts — GH Pages has no write path at all, so demo
  fallback may be permanent there.
- **Relationship to build-time baking.** Do we drop build-time count baking entirely, or
  keep it as the no-JS fallback (progressive enhancement)? If kept, the baked numbers must
  be the DEMO numbers (so the static page is correct with JS off).
- **Interaction with #276 (NOW SHIPPED).** #276 unified index + global-map and shipped the
  BUILD-TIME count-baking model (`build_domain_graph` in `tools/lib/domain_graph.py` bakes
  counts into `#page-data` at generate time). This ticket REPLACES that model with a load-time
  read. The unified `#page-data` island shape (`{domains, edges, islands, stats, mission}`) is
  already structured so a client-side overlay read can be added WITHOUT reshaping it — see ADR
  0016's #279 note. So the coordination worry is resolved: build against the shipped island.
- **Does this let us stop committing the demo overlay / un-strip pages.yml (#278)?** Possibly
  — if the demo fallback is shipped as page data rather than a committed `.user/` file, the
  #278 gitignore/pages.yml special-casing could be retired. Evaluate.
- **Migration.** #278's committed `library/**/.user/status-overlay.json` is the demo source
  of truth today. Decide whether it stays there or moves to a non-`.user/` committed fixture
  (the Approach B path considered in #278 — mirrors `questions.py:_store_root_for` for SR
  fixtures).

## Acceptance criteria

- [x] Progress counts resolve at load time (marking a topic reflects without a regen), OR a
      documented decision to keep build-time baking with demo numbers as the no-JS fallback
- [x] Demo data shows only when the user has no progress of their own (GH Pages / fresh)
- [x] Once the user records progress (or triggers an explicit init/clear UI action), demo
      data is no longer shown for that user
- [x] Static-host (GH Pages, no server) behavior defined and working — demo fallback correct
      with no write path available
- [x] Decision recorded on whether #278's committed-overlay + pages.yml special-casing can be
      retired
- [x] `mise run verify` EXIT 0

## Resolution

Shipped the **load-time read** model (Option A for the static-host question; Option B for
the migration question). Both design forks were surfaced and decided with the user.

**What shipped:**

1. **Join key + inlined demo seed in `#page-data`.** `build_domain_graph` now carries
   `topic_ids` per record; `build_page_data` emits `domains[*].topicIds`, a flat
   `demoOverlay` map (union of committed demo statuses), and `stats.inProgressCount`. The
   baked `complete`/`inProgress` are the **honest demo/no-JS floor** (never zeroed).
2. **Client reads the real overlay at load.** New `GET /api/overlay` (serve.py) returns the
   whole `{node_id → status}` map — a READ (ADR 0014 §B.6 permits "simple status read"), not
   a browser store. The `_MODULE_SCRIPT` bootstrap (`type=module`, top-level await) fetches
   it and overrides `domains[*].{complete,inProgress}` + recomputes `stats` when the user
   owns their progress OR a non-empty overlay resolves; otherwise the demo floor stands.
   `tabular-nums` on count elements avoids swap-time layout shift.
3. **User-init handoff.** `hasOwnProgress` added to `teach-me-prefs-v1` DEFAULTS (UI state,
   ADR 0016 — NOT learner state). A "Start my own progress" control (`DemoBanner` in
   `UnifiedView`) shows only while the demo floor is displayed; clicking sets the flag and
   reloads → the demo clears to the user's own (empty) overlay, never shown again.

**Static-host decision (Option A):** on GH Pages (no server) the `/api/overlay` fetch 404s
and the page keeps the baked demo counts — display-only demo, no persisted per-user progress.
Real progress tracking stays on served hosts (localhost / serve.py). This keeps ADR 0014
§B.6 intact (no browser STORE of learner state); the research/ADR review flagged that a
localStorage-persisted progress overlay would have violated §B.6, so it was NOT built.

**Migration decision (Option B):** the shipped demo seed moved OFF `.user/` to committed
`library/{domain}/demo-status.json` fixtures, read by a new `demo_status_map_for_map()` in
overlay.py. This **retires the #278 special-casing**: `.gitignore` reverted to plain
`**/.user/*` (`.user/` fully private again — verified via `git check-ignore`), and
`pages.yml` broadened its strip to `find _site -type d -name .user -prune -exec rm -rf`.
Regen is byte-idempotent (two consecutive gens hash-identical); counts unchanged (7c/5ip).

**Verification:** `mise run verify` EXIT 0 — 41 unit tests, 16 interactive checks (3 new:
`index_demo_shows_when_empty` incl. takeover button, `index_user_overlay_overrides`,
`index_init_clears_demo` incl. banner-gone), 5/5 ink transcripts. overlay.py self-test
extended for the demo resolver. Found + fixed a real harness bug in passing: Playwright
`add_init_script("() => {...}")` registers but never CALLS the arrow fn (silent no-op).

Files: `tools/lib/overlay.py`, `tools/lib/domain_graph.py`, `tools/generate_index_page.py`,
`tools/serve.py`, `assets/preferences.js`, `assets/components/UnifiedView.js`,
`tools/verify-interactive.py`, `.gitignore`, `.github/workflows/pages.yml`,
`library/index.html`, `library/{godot-gamedev,iceberg-workspace,ink-godot}/demo-status.json`
(relocated from `.user/status-overlay.json`).

**Follow-up:** #281 (per-domain `lessons/index.html` style) can now decide freely — the
build-time-vs-load-time question #279 raised is settled, so #281 won't re-cement the old model.

## Notes

Deferred from #278 (commit 455236d). #276 shipped (commit 53793b1) with the build-time model
this ticket replaces.

**Key references / files to touch:**
- `tools/lib/overlay.py` — overlay store (ULID-keyed, sparse, whole-doc rewrite; root = maps-dir parent).
- `tools/lib/domain_graph.py` `build_domain_graph` + `tools/generate_index_page.py` `build_page_data` — where counts are baked today.
- `assets/components/UnifiedView.js` / `assets/components/store.js` — client side that would read the overlay at load.
- `assets/preferences.js` — the `teach-me-prefs-v1` signal store (where a user-init flag could live).
- `.github/workflows/pages.yml:~120` — the `_site/.user` strip (may be retireable per the question above).
- ADR 0016 (`.memory/adr/0016-unified-domain-graph-views.md`) — the #279 note + the UI-state-vs-learner-state line (ADR 0014 §B.6 keeps LEARNER state out of the browser; a *view* pref is UI state — do not blur when adding a client overlay read).
- Design context: `.memory/research/unified-graph-views/276-implementation-findings.md` (#279 coordination section).
