---
id: "010"
title: "Feature: declarative diagram DSL (stretch)"
status: open
priority: low
blocked_by: ["001", "006"]
type: feature
---

# Feature: declarative diagram DSL (stretch)

## What to build

A thin Python DSL layer (inspired by mingrammer/diagrams) on top of the chosen SVG library that makes diagram authoring more declarative. Operator overloading for connections, context managers for grouping.

**Stretch goal.** Only build if the simpler helper (ticket 006) proves insufficient.

## Design sketch

```python
with Diagram("Architecture", direction="down") as d:
    with Cluster("AWS", fill="blue"):
        catalog = Node("Glue Catalog")
    metadata = Node("Metadata")
    catalog >> Edge("points to") >> metadata

print(d.render())  # → SVG string
```

## Acceptance criteria

- [ ] Context manager grouping works
- [ ] `>>` operator creates directed connections
- [ ] Auto-positions nodes (simple grid, no Graphviz)
- [ ] Produces valid inline SVG
