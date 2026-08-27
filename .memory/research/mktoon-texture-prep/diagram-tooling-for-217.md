# Diagram Tooling for Lesson 0015 (Ticket #217)

## Available Diagram Types

### 1. Stack (`--type stack`)
Vertical layered architecture diagram. Layers stacked top-to-bottom with arrows between.

**Data format:**
```json
{
  "layers": [
    {"label": "Top Layer", "color": "blue", "subtitle": "optional"},
    {"label": "Bottom Layer", "color": "green"}
  ],
  "arrows": ["optional label between layers"]
}
```

**Invocation:**
```bash
python tools/draw-diagram.py --type stack --title "My Stack" --data '{"layers": [...]}'
```

### 2. Flow (`--type flow`)
Left-to-right pipeline. Nodes in a horizontal row with arrows between.

**Data format:**
```json
{
  "nodes": [
    {"label": "Source", "color": "blue"},
    {"label": "Process", "color": "amber"},
    {"label": "Output", "color": "green"}
  ],
  "arrows": ["label1", "label2"]
}
```

**Invocation:**
```bash
python tools/draw-diagram.py --type flow --title "Data Pipeline" --data '{"nodes": [...]}'
```

### 3. Hub (`--type hub`)
Central node with radial spokes. Good for showing one thing connected to many.

**Data format:**
```json
{
  "center": {"label": "Hub", "color": "blue"},
  "spokes": [
    {"label": "Spoke 1", "color": "gray"},
    {"label": "Spoke 2", "color": "gray"}
  ]
}
```

### 4. Graph (`--type graph`)
Free-form DAG with named nodes, edges, and optional groups. Supports fan-out/fan-in, auto-ranks via topological sort.

**Data format:**
```json
{
  "direction": "LR",
  "nodes": [
    {"id": "a", "label": "Node A", "color": "blue"},
    {"id": "b", "label": "Node B", "color": "green"}
  ],
  "edges": [
    {"from": "a", "to": "b", "label": "optional"},
    {"from": ["a", "b"], "to": "c"}
  ],
  "groups": [
    {"label": "Group Name", "nodes": ["a", "b"]}
  ]
}
```

**Fan-out/fan-in:** `"from"` and `"to"` accept arrays for multi-source/multi-target edges.

### 5. Graphviz Backend (`--backend graphviz`)
Same `graph` type but with Graphviz auto-layout. Supports cyclic graphs, state machines, 9+ nodes. Auto-selects engine (dot, neato, fdp, sfdp) based on graph properties, or use `--engine` to override.

**Additional data fields for Graphviz:**
```json
{
  "directed": true,
  "engine": "dot",
  "direction": "TB"
}
```

## CLI Interface

```bash
python tools/draw-diagram.py --type TYPE --data 'JSON' [--title "Accessible Title"] [--backend builtin|graphviz] [--engine dot|neato|fdp|sfdp|circo|twopi]
```

- `--type` (required): stack, flow, hub, graph
- `--data` (required): JSON string
- `--title` (optional): adds accessible `<title>`, `role="img"`, `aria-labelledby`
- `--backend` (optional): builtin (drawsvg, default) or graphviz
- `--engine` (optional): only with `--backend graphviz`
- **Output:** SVG string to stdout — embed directly in HTML

## Color/Preset System

Colors: `blue`, `green`, `amber`, `red`, `gray` — all map to CSS custom properties for theme support.

Presets (semantic aliases):
- `concept` → blue (the thing being taught)
- `example` → green (concrete output)
- `process` → amber (transformation/operational)
- `anti-pattern` → red (problems)
- `infrastructure` → gray (supporting/neutral)

## Hand-Written SVG Patterns (from svg-patterns.md)

For diagrams that need custom layout (annotated detail, side-by-side comparison, non-standard shapes), write inline SVG directly using patterns from `assets/svg-patterns.md`:

- **Layered Stack** — vertical boxes with arrows
- **Flow** — horizontal pipeline
- **Side-by-Side Comparison** — before/after with red/green boxes
- **Annotated Box** — central component with dashed callout lines
- **Hub-and-Spoke** — central + radial connections

All patterns use CSS variables (`var(--svg-primary)`, etc.) and require the accessibility pattern (`role="img"`, `<title>`, `aria-labelledby`).

## Existing Examples in Lessons

All godot-gamedev lessons (0001–0008+) use **hand-written inline SVGs** rather than draw-diagram.py output. Example from 0003-spatial-shader-anatomy.html:
- Pipeline flow (vertex → fragment → light) with annotations
- Uses `var(--svg-primary-fill)`, `var(--svg-warning-fill)`, `var(--svg-neutral-fill)`
- Includes per-box subtitles and scale annotations ("~thousands", "~millions")
- Custom arrow markers defined in `<defs>`

This confirms hand-written SVG is the established pattern for lessons needing annotation detail beyond what draw-diagram.py provides.

## Recommendations for Lesson 0015 Diagrams

### "Channel Triage" Diagram

**What it shows:** How to decide which channel (R, G, B, A) to use for what purpose in a shader.

**Recommended approach: `--type flow` or hand-written SVG**

A flow diagram works if the triage is a linear decision pipeline (signal → classify → assign channel). But if it's a fan-out (one input branching to multiple channels based on criteria), use `--type graph` with fan-out edges:

```json
{
  "direction": "LR",
  "nodes": [
    {"id": "input", "label": "Input Signal", "color": "concept"},
    {"id": "r", "label": "R Channel", "color": "example"},
    {"id": "g", "label": "G Channel", "color": "process"},
    {"id": "b", "label": "B Channel", "color": "infrastructure"},
    {"id": "a", "label": "A Channel", "color": "anti-pattern"}
  ],
  "edges": [
    {"from": "input", "to": ["r", "g", "b", "a"]}
  ]
}
```

If the diagram needs criteria labels on each branch (e.g., "continuous gradient → R", "binary mask → A"), hand-written SVG is better — draw-diagram.py edge labels don't position well for fan-out.

**Best fit: Hand-written inline SVG** using the annotated-box or flow pattern with per-branch criteria labels.

### "Quantization Amplifies Noise" Diagram

**What it shows:** How banding/quantization makes small noise values visible (before: smooth gradient hides noise; after: discrete steps reveal it).

**Recommended approach: Side-by-side comparison (hand-written SVG)**

This is a visual concept — showing smooth vs. stepped gradients with noise. The side-by-side comparison pattern from svg-patterns.md is ideal:

- Left box (red border): "Smooth gradient" with a conceptual ramp + noise
- Right box (green border): "Quantized" with visible steps + amplified noise
- Arrow between showing the quantization operation

This CANNOT be done with draw-diagram.py — it requires custom shapes (gradient ramps, stepped lines) that aren't box-and-arrow. Hand-write using the side-by-side comparison pattern from svg-patterns.md.

**Best fit: Hand-written inline SVG** using the side-by-side comparison pattern with custom gradient/step illustrations.

## Summary

| Diagram | Tool | Reason |
|---------|------|--------|
| Channel triage | Hand-written SVG | Needs branch criteria labels positioned per-edge; fan-out with annotations |
| Quantization amplifies noise | Hand-written SVG | Requires custom shapes (gradient ramps, stepped lines) not supported by box-and-arrow tools |

Both diagrams follow the established lesson pattern (all existing godot-gamedev lessons use hand-written inline SVG). Use `assets/svg-patterns.md` color variables and accessibility patterns.
