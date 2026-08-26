---
id: "156"
title: "Spike: cycle-breaking + foundational scoring strategies for dependency ordering"
status: done
blocked_by: []
priority: high
type: spike
tags: [source-ingest]
---

# Spike: cycle-breaking + foundational scoring strategy comparison

## Question to answer

For #151's dependency-reordered MAP generation:
1. Does MWFAS (iterative min-weight edge removal) produce better learning orders than Eades-Lin-Smyth for our graph shapes?
2. Do in-degree, PageRank, and frequency×position produce meaningfully different tie-breaking orders?

## Part A: Cycle-breaking

Compare on real (reference fixture) + synthetic (20 nodes, 30 edges, 3-4 cycles) graphs:
- **MWFAS iterative**: find cycle → remove min-weight edge → repeat → try re-adding
- **Eades-Lin-Smyth**: source/sink peeling + max-differential vertex selection

Measure:
- Number of edges removed
- Total weight of removed edges (lower = better — preserves strongest signals)
- Do resulting orderings differ? If so, which preserves more semantically meaningful edges?

## Part B: Foundational scoring

Compare three tie-breaking strategies when topological sort has multiple valid next-nodes:
- **In-degree**: how many nodes depend on this one (normalized)
- **PageRank**: recursive importance (damping=0.85)
- **Frequency×position**: current extract_concepts scoring (frequency × 1/first_appearance)

Measure:
- Agreement rate: how often do all three pick the same next node?
- Disagreement cases: which method picks the "more foundational" topic? (Manual review)

## Decision criteria

- If both cycle-breakers produce same/similar orderings → pick simpler (Eades-Lin-Smyth)
- If MWFAS preserves noticeably better edges → implement iterative approach
- If scoring methods agree 80%+ → use simplest (in-degree or existing frequency×position)
- If one consistently picks "more foundational" → use it; or blend with opinionated weights

## Secondary: SCC module threshold

- Confirm that SCCs of size 2 → soft_prereqs (cut weaker edge)
- Confirm that SCCs of size 3+ → module grouping (no forced internal order)
- Or adjust threshold based on what the synthetic graph shows

## Acceptance criteria

- [x] Comparison harness runs on reference fixture + synthetic graph
- [x] Part A: quantified difference between cycle-breaking strategies
- [x] Part B: quantified agreement between scoring methods
- [x] Decision written (which strategy for each, with rationale)
- [x] SCC module threshold confirmed

## Results

### Part A: Cycle-breaking — MWFAS wins

| Metric | MWFAS iterative | Eades-Lin-Smyth |
|--------|----------------|-----------------|
| Edges removed | 4 | 4 |
| Total weight removed | 0.650 | 0.750 |
| Ordering agreement | — | 35% (with MWFAS) |

**Decision: Use MWFAS iterative.**

MWFAS correctly identifies the weaker direction in bidirectional cycles. In the service-discovery ↔ load-balancing cycle, MWFAS cuts the 0.2-weight edge (SD→LB) while ELS cuts the 0.3-weight edge (LB→SD). This matters pedagogically: "learn load-balancing before service-discovery" is the stronger signal and MWFAS preserves it.

The 35% ordering agreement shows this isn't a cosmetic difference — the algorithms produce meaningfully different final orders.

### Part B: Foundational scoring — Blend freq×position (0.6) + in-degree (0.4)

| Pair | Kendall τ (reference) | Kendall τ (synthetic) |
|------|----------------------|----------------------|
| In-degree vs PageRank | 0.855 | 0.684 |
| In-degree vs Freq×Pos | 0.745 | 0.758 |
| PageRank vs Freq×Pos | 0.818 | 0.526 |

**Decision: Blend frequency×position (0.6) + in-degree (0.4). Drop PageRank.**

Rationale from synthetic ordering review:
- **Freq×position** produces the most intuitive teaching order (ip→tcp→http→dns→...). It captures "the author introduced this early for a reason" — strong pedagogical signal.
- **In-degree** correctly identifies foundational nodes (ip-addressing at top) but over-promotes leaf nodes that are heavily referenced (websockets, reverse-proxy). It's a useful correction signal, not a primary driver.
- **PageRank** pushes terminal nodes high (timeout-config, cdn-caching) which is wrong for teaching. Dropped.

Blend formula: `score = 0.6 * freq_position + 0.4 * normalized_in_degree`

### SCC Module Threshold — Confirmed: 2=soft, 3+=module

| SCC size | Example | Strategy |
|----------|---------|----------|
| 2 | tls ↔ certificates | Soft prereq: cut weaker edge, add forward-reference callout |
| 3 | circuit-breaker / retry / timeout | Module: group as "take in any order" |
| 4 | tcp / http / websockets / socket-api | Module: group as mutually reinforcing |

The size-2 SCCs have a clear weaker edge (0.2 or 0.15) making the cut obvious. Size-3+ have no clear linearization — multiple edges of similar weight, forcing arbitrary order. Module grouping is more honest.

### Edge density fallback threshold

Synthetic graph: 29 edges / (20×19) possible = 0.076 density. This is below the 0.1 threshold I proposed but still produces meaningful ordering. Revising: **fall back when density < 0.05** (fewer than ~5% of possible edges have signal). The synthetic graph validates that 0.07-0.08 density is workable.
