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
5. Post-processes SVG to add accessibility attributes (`role="img"`, `<title>`, `aria-labelledby`)

## When to use

Only for diagrams where our built-in layout fails:
- State machines with cycles
- Dependency graphs with cross-edges
- Network topologies (neato/fdp layout)
- Any diagram with 9+ interconnected nodes

Simple teaching diagrams (stack, flow, hub, small graphs) should still use the built-in layout.

## Research findings (2026-08-09)

### Engine selection decision tree

| Engine | Best for | Node limit | Key constraint |
|--------|----------|------------|----------------|
| **dot** | Hierarchies, DAGs, pipelines, dependency graphs | Thousands | Only engine with reliable `rank=same` alignment |
| **neato** | Small undirected networks, relationship maps | ~100 (O(n²)) | Set `start=N` for reproducible output |
| **fdp** | Clustered undirected graphs | Hundreds | One of only two engines (with dot) that handles clusters |
| **sfdp** | Large undirected graphs (1000+) | Tens of thousands | Ignores edge lengths; use `overlap=prism` |
| **circo** | Ring topologies, protocol state machines | Small-medium | Fixed circular arrangement |
| **twopi** | Radial/hub-spoke from a root node | Medium | Set `root=nodename` for center |

**Recommended default:** `dot` for anything directed or with groups. `fdp` for undirected with clusters. `neato` for small undirected without clusters.

### Key integration patterns

1. **svg_inline format** (Graphviz ≥ 10.0.1) produces `<svg>...</svg>` without XML declaration — ready for HTML embedding. Verify system Graphviz version at runtime.
2. **Cluster naming**: subgraph name MUST start with `cluster_` (lowercase) for engines to render the boundary box.
3. **Color application**: set via `graph_attr`, `node_attr`, `edge_attr` dicts at construction, override per-node with `fillcolor`/`color`.
4. **Determinism**: force-directed engines (neato, fdp, sfdp) are non-deterministic by default. Use `start=42` (or any fixed seed) for reproducible builds.
5. **Edge labels in dot**: use `xlabel` instead of `label` to avoid layout distortion (labels modeled as dummy nodes).

### Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| `svg_inline` requires Graphviz 10.0.1+ | Check version at runtime; fall back to `svg` + strip XML header |
| Non-deterministic output (neato/fdp) | Pin `start=N` attribute; document in skill |
| Node overlaps in force-directed | `overlap=false` + `sep="+5"` for neato/fdp; `overlap=prism` for sfdp |
| Clusters ignored by neato/sfdp | Only offer clusters with dot/fdp backends; error or warn otherwise |
| Large graphs slow with spline routing | Use `splines=polyline` for graphs >50 edges; `splines=ortho` for box diagrams |
| Accessibility not built-in | Post-process SVG to inject `role="img"`, `<title>`, `aria-labelledby` |

### Implementation recommendations

1. **Auto-select engine from JSON input**: if edges are directed → dot; if `groups` present and undirected → fdp; if small undirected → neato. Allow `--engine` override.
2. **Graceful degradation**: try `import graphviz`; if missing, print install instructions and exit 1. Check `graphviz.version()` for svg_inline support.
3. **SVG post-processing**: parse with `xml.etree.ElementTree`, inject accessibility attrs, apply `viewBox`-only sizing (no fixed width/height) per our visual-teaching guidelines.
4. **Testing**: compare output against golden SVG files for a small set of representative graphs (DAG, cyclic, clustered). Accept structural equivalence, not byte-identical.

### Sources

- [Graphviz layout engines](https://graphviz.org/docs/layouts/) — official docs
- [Python graphviz library](https://graphviz.readthedocs.io/en/stable/manual.html) — pipe(), engine selection, subgraphs
- [svg_inline format](https://graphviz.org/docs/outputs/svg/) — requires Graphviz 10.0.1+
- [Graphviz FAQ](https://www.graphviz.org/faq/) — workarounds for common layout issues
- [Graphviz forum: complex layouts](https://forum.graphviz.org/t/i-want-suggestions-on-handling-complex-graph-layouts-in-graphviz/3156)

## Acceptance criteria

- [ ] `pip install graphviz` added as optional dependency
- [ ] `--backend graphviz` produces inline SVG via pipe()
- [ ] Engine auto-selected from graph shape (dot/neato/fdp); `--engine` override available
- [ ] Color vocabulary applied correctly (fills, strokes, edge colors)
- [ ] Groups render as Graphviz clusters (dot/fdp only; warn for other engines)
- [ ] SVG post-processed for accessibility (role, title, aria-labelledby, viewBox-only)
- [ ] Deterministic output via `start=N` for force-directed engines
- [ ] draw-diagram skill documents when to use this backend
- [ ] Graceful error if graphviz system binary not installed or version too old
- [ ] Smoke test: one DAG, one cyclic graph, one clustered graph produce valid SVG
