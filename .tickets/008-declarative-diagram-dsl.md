---
id: "008"
title: "Create DSL helper for declarative diagram authoring"
status: open
priority: low
blocked_by: ["001"]
---

# Create DSL helper for declarative diagram authoring

## What to build

Inspired by mingrammer/diagrams' operator-overloading pattern, create a thin Python DSL layer on top of drawsvg that makes diagram authoring more declarative and readable in generated code.

## Design (from mingrammer/diagrams exploration)

```python
from tools.diagram_dsl import Diagram, Node, Cluster, Edge

with Diagram("Iceberg Architecture", direction="down") as d:
    with Cluster("AWS Glue", fill="blue"):
        catalog = Node("Data Catalog")
    
    with Cluster("S3", fill="gray"):
        metadata = Node("Metadata Files")
        data = Node("Data Files (Parquet)")
    
    catalog >> Edge("points to") >> metadata
    metadata >> Edge("lists") >> data

print(d.render())  # → SVG string
```

## Key patterns from prior art

- **Context managers** for auto-registration (mingrammer/diagrams)
- **Operator overloading** (`>>`) for connections (Python `__rshift__`)
- **Edge as first-class** with labels (mingrammer pattern)
- **Auto-layout** using simple grid positioning (no Graphviz dep)
- Color vocabulary from visual teaching steering

## Scope

This is a stretch goal. Only build if the simpler `draw-diagram.py` (ticket 001) proves insufficient for lesson authoring.

## Acceptance criteria

- [ ] DSL produces valid SVG via drawsvg
- [ ] Context manager pattern works for grouping
- [ ] `>>` operator creates directed connections
- [ ] Auto-positions nodes in a grid (no manual x,y needed)
- [ ] Colors follow visual teaching steering
