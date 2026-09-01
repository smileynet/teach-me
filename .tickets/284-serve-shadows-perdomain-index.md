---
id: "284"
title: "serve.py _root_index shadows per-domain lessons/index.html under multi-domain root"
status: done
blocked_by: []
tags: [platform]
---

# serve.py _root_index shadows per-domain lessons/index.html under multi-domain root

## Context (found during #281)

serve.py's `_root_index` handler (`tools/serve.py`, `@app.get("/{prefix:path}/index.html")`,
active only when `_SERVING_MULTI_DOMAIN`) normalizes EVERY nested `index.html` request to the
aggregate root index. Its purpose: domain-map / lesson pages emit a bare `index.html`
back-link that, under a multi-domain `library/` root serve, would 404 — so it routes them to
the aggregate.

Side effect: the committed per-domain `library/{domain}/lessons/index.html` pages are
**unreachable via `mise run serve`** (the default multi-domain root serve) — every request to
one serves the aggregate instead. Yet on the DEPLOYED static host (GitHub Pages, pages.yml)
the committed per-domain page IS served as-is (pages.yml only synthesizes a redirect where the
page is ABSENT). So per-domain pages are live when deployed but shadowed locally.

Consequences:
- The #281 per-domain style (single-domain IndexView vs sub-map UnifiedView) can't be observed
  or QA'd via the normal local server — only by serving the single workspace
  (`mise run serve -- --workspace library/{domain}`) or by direct deploy.
- serve-vs-deploy behavior diverges for the same URL — a latent surprise.

## What to build / decide

Reconcile the local serve behavior with the deploy behavior for per-domain `lessons/index.html`:
- Option A: `_root_index` serves the per-domain page WHEN it exists (`{prefix}/lessons/index.html`
  on disk), falling back to the aggregate only when absent — mirroring pages.yml exactly.
- Option B: keep the normalizer but document the divergence + provide a serve flag to disable it.
- Option C: accept the divergence (deploy is the source of truth) and document it.

Prefer A — it makes `mise run serve` match the deploy, so per-domain pages become locally
observable and the #281 style is verifiable without single-workspace serving. Confirm the
bare-`index.html` back-link case (the reason the normalizer exists) still resolves.

## Acceptance criteria

- [x] `mise run serve` (multi-domain `library/` root) serves the committed per-domain
      `lessons/index.html` when present (matches pages.yml deploy behavior)
- [x] Bare `index.html` back-links from domain-map / lesson pages still resolve (no 404)
- [x] Decision recorded (ADR 0015 amendment or ticket resolution)
- [x] `mise run verify` EXIT 0

## Resolution

Fixed `_root_index` (`tools/serve.py`): when serving a multi-domain root, a
`/{prefix}/index.html` request now serves the COMMITTED `{prefix}/index.html` when it exists
on disk (path-traversal guarded via resolve()+containment, and excluding the aggregate root
itself), falling back to the aggregate root index only when absent — mirroring the deploy
(pages.yml). Per-domain pages are now reachable via `mise run serve` on `library/`, matching
GitHub Pages, so the #281 content-driven landing is locally observable AND gate-testable.

This unblocked closing the #281 validation gap: added `run_per_domain_checks` to
`verify-interactive.py` (needs this fix to reach the pages) — 4 checks now in the gate:
`perdomain_single_is_indexview` (single domain → IndexView, no toggle), 
`perdomain_submap_is_unifiedview` (sub-map domain → UnifiedView toggle),
`perdomain_live_overlay_override` (crafted overlay drives the count → the behavioral proof
that #281's trimmed bootstrap live-override works on a per-domain page), `perdomain_no_js_errors`.

**Verification:**
- Served `library/` root: `/oidc-rust/lessons/index.html` → IndexView, `/godot-gamedev/...`
  → UnifiedView, `/index.html` → UnifiedView (aggregate), and a bare `index.html` from a
  domain without a per-domain page still falls back to the aggregate (no 404).
- `mise run verify` EXIT 0 — 20 interactive checks (incl. the 4 per-domain), 41 unit, 5/5 ink.

## References
- `tools/serve.py` `_root_index` (`@app.get("/{prefix:path}/index.html")`, gated on `_SERVING_MULTI_DOMAIN`).
- `.github/workflows/pages.yml` (~line 80) — the static analogue that serves committed per-domain pages + synthesizes redirects only when absent.
- ADR 0015 (unifying root / document-relative assets) — the normalizer is part of that scheme.
- #281 (per-domain index style) — surfaced this; its pages are what's shadowed.
