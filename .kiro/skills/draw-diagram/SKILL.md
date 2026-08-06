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
mise run install-deps  # installs drawsvg
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

## Color Vocabulary

| Name | Meaning | Use for |
|------|---------|---------|
| `blue` | Primary, input, the thing being discussed | Main components, sources |
| `green` | Success, output, healthy state | Results, data at rest |
| `amber` | Warning, caution, operational | Processing, metadata |
| `red` | Error, anti-pattern | Problems, wrong approaches |
| `gray` | Infrastructure, neutral | Supporting services |

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
| Standard teaching diagram (stack/flow/hub) | `draw-diagram.py` |
| Custom layout or annotated component | Raw inline SVG from `assets/svg-patterns.md` |
| Complex auto-layout (sequence, state machine) | D2 (`d2 input.d2 output.svg`) |

## Limitations

- No auto-layout — positions are grid-based (good enough for 3-7 elements)
- No interactive elements (use progressive-reveal.js `data-step` attrs for that)
- Hub diagram with >6 spokes gets crowded — split into multiple diagrams
