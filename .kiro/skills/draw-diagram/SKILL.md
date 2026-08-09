---
name: draw-diagram
description: "Generate inline SVG teaching diagrams using tools/draw-diagram.py. Use when creating architecture stacks, data flows, or hub-and-spoke diagrams for lessons. Trigger: draw diagram, generate SVG, architecture diagram, flow diagram, visual for lesson."
metadata:
  type: reference
  invocation: both
  practice: null
---

# Draw Diagram

Generate teaching diagrams as inline SVG via `tools/draw-diagram.py`. Output goes to stdout — paste directly into lesson HTML.

## Prerequisites

```bash
mise run setup  # installs drawsvg via uv
```

## Commands

### Layered Stack (architecture layers, top-to-bottom)

```bash
python tools/draw-diagram.py --type stack --data '{
  "layers": [
    {"label": "AWS Glue Catalog", "color": "blue"},
    {"label": "Metadata (JSON)", "color": "amber", "subtitle": "schema + snapshots"},
    {"label": "Data Files (Parquet)", "color": "green"}
  ],
  "arrows": ["points to", "lists files"]
}'
```

### Left-to-Right Flow (pipelines, sequences)

```bash
python tools/draw-diagram.py --type flow --data '{
  "nodes": [
    {"label": "Producers", "color": "blue"},
    {"label": "Glue ETL", "color": "amber"},
    {"label": "Iceberg Table", "color": "green"},
    {"label": "Athena", "color": "blue"}
  ],
  "arrows": ["raw events", "write Parquet", "query"]
}'
```

### Hub-and-Spoke (central service + connections)

```bash
python tools/draw-diagram.py --type hub --data '{
  "center": {"label": "Glue Catalog", "color": "blue"},
  "spokes": [
    {"label": "Athena", "color": "gray"},
    {"label": "EMR Spark", "color": "gray"},
    {"label": "Redshift", "color": "gray"},
    {"label": "Glue ETL", "color": "gray"}
  ]
}'
```

### Graph (fan-out/fan-in, groups, auto-layout)

The most flexible type. Nodes are named by ID, edges can connect one-to-many or many-to-one. Layout is computed automatically via topological ranking.

```bash
python tools/draw-diagram.py --type graph --data '{
  "direction": "LR",
  "nodes": [
    {"id": "lb", "label": "Load Balancer", "preset": "infrastructure"},
    {"id": "w1", "label": "Worker 1", "preset": "concept"},
    {"id": "w2", "label": "Worker 2", "preset": "concept"},
    {"id": "db", "label": "Database", "preset": "example"}
  ],
  "edges": [
    {"from": "lb", "to": ["w1", "w2"], "label": "distribute"},
    {"from": ["w1", "w2"], "to": "db", "label": "write"}
  ],
  "groups": [
    {"label": "Compute", "nodes": ["w1", "w2"]}
  ]
}'
```

**Features:**
- `"from"` and `"to"` accept single ID or array (fan-out/fan-in)
- `"groups"` draw a dashed background rectangle around named nodes
- `"direction"`: `"LR"` (left-to-right) or `"TB"` (top-to-bottom)
- Auto-ranks nodes by dependency depth (sources left/top, sinks right/bottom)

## Color Vocabulary & Presets

Colors can be specified by name or preset. Presets map teaching intent to color:

| Preset | Color | Use for |
|--------|-------|---------|
| `concept` | blue | The thing being taught, primary components |
| `example` | green | Concrete instances, outputs, results |
| `process` | amber | Processing, transformation, operational steps |
| `anti-pattern` | red | Problems, errors, what not to do |
| `infrastructure` | gray | Supporting services, neutral context |

Use `"preset": "concept"` or `"color": "blue"` — both work.

## Output

Prints SVG XML to stdout. Embed in lessons:

```html
<p>The Iceberg metadata tree has three layers:</p>
<!-- paste SVG output here -->
```

Always add a one-line verbal summary above the diagram (dual coding principle).

## When to use this vs raw SVG vs D2

| Situation | Use |
|-----------|-----|
| Standard teaching diagram (stack/flow/hub/small graph) | `draw-diagram.py` (builtin) |
| Complex graphs: cycles, cross-edges, 9+ nodes | `draw-diagram.py --backend graphviz` |
| Custom layout or annotated component | Raw inline SVG from `assets/svg-patterns.md` |
| Complex auto-layout (sequence diagrams) | D2 (`d2 input.d2 output.svg`) |

## Graphviz Backend (auto-layout)

For diagrams too complex for the built-in rank-based layout — state machines with cycles, dependency graphs with cross-edges, network topologies.

### Prerequisites

```bash
mise run setup       # installs drawsvg + graphviz Python package
sudo apt install graphviz  # system binary (Linux)
# or: brew install graphviz (macOS)
```

### Usage

```bash
python tools/draw-diagram.py --type graph --backend graphviz --data '{
  "directed": true,
  "nodes": [
    {"id": "plan", "label": "Planning", "color": "blue"},
    {"id": "scan", "label": "Scanning", "color": "amber"},
    {"id": "done", "label": "Complete", "color": "green"},
    {"id": "fail", "label": "Failed", "color": "red"},
    {"id": "retry", "label": "Retry", "color": "gray"}
  ],
  "edges": [
    {"from": "plan", "to": "scan"},
    {"from": "scan", "to": "done"},
    {"from": "scan", "to": "fail", "label": "timeout"},
    {"from": "fail", "to": "retry"},
    {"from": "retry", "to": "plan", "label": "backoff"}
  ]
}' --title "Query Lifecycle"
```

### Engine selection

Auto-selected from graph properties, or override with `--engine`:

| Engine | Auto-selected when | Best for |
|--------|-------------------|----------|
| `dot` | Directed edges (default) | Hierarchies, DAGs, pipelines |
| `fdp` | Undirected + groups | Clustered networks |
| `neato` | Undirected, ≤100 nodes, no groups | Small relationship maps |
| `sfdp` | Undirected, >100 nodes | Large graphs |
| `circo` | Manual only (`--engine circo`) | Ring topologies |
| `twopi` | Manual only (`--engine twopi`) | Radial from center |

### Clustered graphs (groups)

Groups render as Graphviz cluster subgraphs. Only `dot` and `fdp` engines honor cluster boundaries — other engines will render the graph but ignore group boxes (a warning is printed).

```bash
python tools/draw-diagram.py --type graph --backend graphviz --data '{
  "nodes": [
    {"id": "api", "label": "API", "color": "blue"},
    {"id": "auth", "label": "Auth", "color": "blue"},
    {"id": "db", "label": "Database", "color": "green"},
    {"id": "cache", "label": "Cache", "color": "green"}
  ],
  "edges": [
    {"from": "api", "to": "auth"},
    {"from": "api", "to": "db"},
    {"from": "api", "to": "cache"}
  ],
  "groups": [
    {"label": "Services", "color": "blue", "nodes": ["api", "auth"]},
    {"label": "Storage", "color": "green", "nodes": ["db", "cache"]}
  ]
}' --title "Service Groups"
```

### Data format (graphviz backend)

```json
{
  "directed": true,             // true (default) = Digraph, false = Graph
  "direction": "TB",            // "TB"|"LR"|"BT"|"RL" (rankdir)
  "engine": "dot",              // optional override (auto-selected if omitted)
  "nodes": [{"id": "x", "label": "...", "color": "blue"}],
  "edges": [{"from": "x", "to": "y", "label": "...", "color": "gray"}],
  "groups": [{"label": "...", "color": "gray", "nodes": ["x", "y"]}]
}
```

Fan-out/fan-in edges work the same as the builtin backend: `"from": ["a", "b"]` or `"to": ["c", "d"]`.

## Limitations

- **Builtin backend:** No auto-layout for cycles/cross-edges — grid-based positioning works for 3-7 elements
- **Graphviz backend:** Non-deterministic force-directed layouts (mitigated with `start=42`); requires system `graphviz` binary
- Hub diagram with >6 spokes gets crowded — split into multiple diagrams
- No interactive elements (use progressive-reveal.js `data-step` attrs for that)
