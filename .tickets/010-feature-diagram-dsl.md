---
id: "010"
title: "Feature: graphviz auto-layout backend for complex diagrams (stretch)"
status: open
priority: low
blocked_by: []
type: feature
---

# Feature: graphviz auto-layout backend for complex diagrams

## Updated scope (based on deep dive 2026-08-07)

The original "declarative DSL with operator overloading" is unnecessary — our JSON input format works well for agent generation. The real gap is **auto-layout for complex diagrams** (9+ nodes, cycles, cross-edges) where our rank-based positioning breaks down.

The `graphviz` Python library (xflr6/graphviz) can fill this gap:
- `.pipe(format='svg_inline', encoding='utf-8')` returns inline SVG strings directly
- 8 layout engines (dot=hierarchical, neato=spring, circo=circular, etc.)
- Subgraph/cluster support via context managers
- Requires `brew install graphviz` (system dependency)

## What to build

Add a `--backend graphviz` option to `tools/draw-diagram.py` that:
1. Maps our node/edge/group JSON to Graphviz DOT attributes
2. Applies our color vocabulary to node fills/strokes
3. Selects layout engine based on diagram shape (dot for DAGs, neato for networks)
4. Returns inline SVG via `.pipe(format='svg_inline')`

## When to use

Only for diagrams where our built-in layout fails:
- State machines with cycles
- Dependency graphs with cross-edges
- Network topologies (neato/fdp layout)
- Any diagram with 9+ interconnected nodes

Simple teaching diagrams (stack, flow, hub, small graphs) should still use the built-in layout.

## Acceptance criteria

- [ ] `pip install graphviz` added as optional dependency
- [ ] `--backend graphviz` produces inline SVG via pipe()
- [ ] Color vocabulary applied correctly
- [ ] Groups render as Graphviz clusters
- [ ] draw-diagram skill documents when to use this backend
- [ ] Graceful error if graphviz system binary not installed
