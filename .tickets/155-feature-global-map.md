---
id: "155"
title: "Feature: global map — unified view of all domain maps with lazy cross-domain connections"
status: open
blocked_by: ["150", "152"]
priority: medium
type: feature
---

# Feature: global map

## Problem

Each domain gets its own MAP.md — but the learner's knowledge spans multiple domains. There's no unified view showing:
- What domains exist and their completion state
- How domains connect (shared concepts, prerequisite chains)
- What's an island (no connections to other domains) vs what's in a cluster

The existing `leads_to` field in MAP.md is hand-authored and rarely populated. Cross-domain connections should emerge from evidence, not be manufactured.

## What to build

A **global map** that aggregates all domain MAPs into a single navigable graph with lazily-detected cross-domain edges.

### Core model

```
global-map.json (generated, cached)
├── domains: [{slug, title, topic_count, completion%, position}]
├── islands: [domain slugs with no cross-domain edges]
└── connections: [{from_domain, to_domain, type, evidence, weight}]
```

### Connection detection (lazy, on-demand)

Connections are NOT pre-computed for all pairs. They're detected when:
1. A new domain is generated → check if its concepts overlap with existing domains
2. A learner completes a domain → "where does this lead?" triggers connection search
3. Explicit `leads_to` fields in MAP.md → always included

**Detection mechanisms:**

| Type | How | Evidence |
|------|-----|----------|
| Shared concepts | YAKE concepts that appear in both domains' chunks | concept term + chunk references |
| Prereq bridge | Topic in domain B uses a term defined in domain A | first-mention edge crossing domains |
| leads_to (explicit) | MAP.md frontmatter | author declaration |
| Topic name overlap | Identical or near-identical topic slugs across maps | slug similarity + content cosine |

### Visualization

Generate an interactive HTML page (Preact + dagre, matching existing map page pattern):
- Each domain is a node (sized by topic count, colored by completion)
- Cross-domain edges shown as thin connectors with hover-to-explain
- Islands float disconnected (not forced into a layout)
- Click a domain → navigates to its domain map page

### "Topic islands" handling

Domains with zero detected connections to others are explicitly surfaced:
- Shown as islands in the visualization (spatially separated)
- Listed in a sidebar: "Standalone domains (no detected connections)"
- NOT treated as a problem — some domains are genuinely independent
- When new connections are detected later, islands naturally join the graph

## CLI

```bash
python tools/generate_global_map.py --scan-dir workspace/maps/ --output workspace/global-map.html
mise run map:global  # shorthand
```

## Architecture

```
workspace/maps/*.MAP.md
    │
    ▼ (map_parser.py — already works)
Per-domain DomainMap objects
    │
    ▼ (extract_concepts.py — per-domain, cached as .concepts.json)
Per-domain concept sets
    │
    ▼ (new: cross_domain_edges.py)
Connection detection: shared concepts + prereq bridges
    │
    ▼ (new: generate_global_map.py)
global-map.html (interactive Preact page)
```

## Acceptance criteria

- [ ] Generates global map HTML from all MAP.md files in a workspace
- [ ] Detects shared-concept connections between domains (when they exist)
- [ ] Surfaces topic islands without treating them as errors
- [ ] Clicking a domain navigates to its map page
- [ ] Lazy detection: only computes connections when triggered (not O(n²) on every serve)
- [ ] Works with 1 domain (just shows a single node), 5 domains, and 20+ domains
- [ ] Handles the `leads_to` frontmatter field as explicit edges
- [ ] Visual matches existing map page style (dagre layout, same color palette)

## Open questions

- Should connections have a confidence threshold (don't show weak ones by default)?
- Should the global map auto-regenerate on domain completion, or only on explicit request?
- How to handle depth-1 child maps (e.g., sub-topics that expand into their own MAP)?
- Does this replace or complement the existing index page (generate_index_page.py)?
