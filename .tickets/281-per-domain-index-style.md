---
id: "281"
title: "Decide per-domain lessons/index.html style (old IndexView vs unified two-view)"
status: open
blocked_by: []
tags: [platform]
---

# Decide per-domain lessons/index.html style (old IndexView vs unified two-view)

## Context

#276 rewrote `generate_index_page.py` to produce the unified Tree|Map page (UnifiedView).
But the five per-domain `lessons/index.html` pages were NOT regenerated — they still use
the old `IndexView` (card-grid dashboard, single domain). This creates two conditions:

1. **Inconsistency:** the aggregate is unified, per-domain pages are old-style. Not broken
   (both render, verify passes), but visually different.
2. **Latent behavior change:** anyone who regenerates a per-domain index now gets the
   unified page — which shows a Tree|Map toggle for a single domain (one node, no edges).
   That's functional but odd.

## Options

**A. Detect single-domain in the generator, skip the toggle/map-view.** The generator
checks `len(roots) <= 1 and len(edges) == 0` and emits the old-style IndexView (or a
simplified UnifiedView with the toggle hidden). Per-domain pages get a clean single-domain
dashboard; the aggregate gets the full toggle. Cost: a conditional branch in the generator +
possibly keeping IndexView alive.

**B. Regenerate per-domain pages to unified, accept the toggle.** A single domain with
one root and zero edges renders a tree with one item and a map with one card — harmless if
not visually impressive. Ship it for consistency, revisit if it looks bad. Cost: regenerate
5 pages, accept the diff churn.

**C. Leave as-is (don't regenerate).** Per-domain pages keep the old style. The
inconsistency is cosmetic; lesson breadcrumbs ("All Lessons") land on these pages and they
still work. Cost: none now, but drift accumulates if IndexView and UnifiedView diverge.

## Acceptance criteria

- [ ] A decision is made and documented (ADR or ticket resolution)
- [ ] Per-domain `lessons/index.html` pages are in the chosen style
- [ ] No verify regression
