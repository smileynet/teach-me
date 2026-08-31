---
id: "279"
title: "Rethink progress overlay: read at load time with demo fallback + user-init handoff"
status: open
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
- **Interaction with #276.** #276 unifies index + global-map and regenerates both. Whatever
  load-time model we pick, #276's `build_domain_graph` should emit the demo overlay as data
  the client can fall back to, not just baked counts. Coordinate so #276 doesn't cement the
  build-time-only model right before we replace it.
- **Does this let us stop committing the demo overlay / un-strip pages.yml (#278)?** Possibly
  — if the demo fallback is shipped as page data rather than a committed `.user/` file, the
  #278 gitignore/pages.yml special-casing could be retired. Evaluate.
- **Migration.** #278's committed `library/**/.user/status-overlay.json` is the demo source
  of truth today. Decide whether it stays there or moves to a non-`.user/` committed fixture
  (the Approach B path considered in #278 — mirrors `questions.py:_store_root_for` for SR
  fixtures).

## Acceptance criteria

- [ ] Progress counts resolve at load time (marking a topic reflects without a regen), OR a
      documented decision to keep build-time baking with demo numbers as the no-JS fallback
- [ ] Demo data shows only when the user has no progress of their own (GH Pages / fresh)
- [ ] Once the user records progress (or triggers an explicit init/clear UI action), demo
      data is no longer shown for that user
- [ ] Static-host (GH Pages, no server) behavior defined and working — demo fallback correct
      with no write path available
- [ ] Decision recorded on whether #278's committed-overlay + pages.yml special-casing can be
      retired
- [ ] `mise run verify` EXIT 0

## Notes

Deferred from #278 (commit 455236d). Not blocking #276, but #276 should avoid cementing the
build-time-only model — see the #276 interaction question above. Overlay mechanics documented
in `tools/lib/overlay.py` (ULID-keyed, sparse, whole-doc rewrite; root = maps-dir parent).
