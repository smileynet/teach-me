#!/usr/bin/env python3
"""draw-diagram.py — Generate teaching diagrams as inline SVG.

Usage:
  python tools/draw-diagram.py --type stack --data '{"layers": [...]}'
  python tools/draw-diagram.py --type flow --data '{"nodes": [...]}'
  python tools/draw-diagram.py --type hub --data '{"center": {...}, "spokes": [...]}'

Output: SVG string to stdout (embed directly in HTML lessons).

Requires: pip install drawsvg
"""
import argparse
import json
import re
import sys

import drawsvg as draw

# Color vocabulary (matches .kiro/steering/visual-teaching.md)
COLORS = {
    "blue":  {"fill": "#dbeafe", "stroke": "#2563eb"},
    "green": {"fill": "#dcfce7", "stroke": "#16a34a"},
    "amber": {"fill": "#fef3c7", "stroke": "#d97706"},
    "red":   {"fill": "#fef2f2", "stroke": "#dc2626"},
    "gray":  {"fill": "#f3f4f6", "stroke": "#6b7280"},
}

# Teaching presets (inspired by C4 domain vocabulary pattern from mingrammer/diagrams)
PRESETS = {
    "concept":        "blue",   # the thing being taught
    "example":        "green",  # a concrete instance or output
    "process":        "amber",  # processing, transformation, operational
    "anti-pattern":   "red",    # problems, errors, what not to do
    "infrastructure": "gray",   # supporting context, neutral
}

FONT = "system-ui, sans-serif"
ARROW_COLOR = "#374151"


def _make_arrow(drawing):
    """Create and return a reusable arrowhead marker."""
    arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill=ARROW_COLOR, close=True))
    return arrow


def labeled_box(d, x, y, w, h, label, color="blue", subtitle=None):
    """Draw a rounded labeled box. Color can be a name or a preset."""
    # Resolve preset to color
    if color in PRESETS:
        color = PRESETS[color]
    c = COLORS.get(color, COLORS["blue"])
    d.append(draw.Rectangle(x, y, w, h, rx=6, fill=c["fill"], stroke=c["stroke"], stroke_width=1.5))
    ty = y + h / 2 + (0 if not subtitle else -6)
    d.append(draw.Text(label, 13, x + w / 2, ty, text_anchor='middle',
                       font_family=FONT, font_weight='600', dominant_baseline='central'))
    if subtitle:
        d.append(draw.Text(subtitle, 11, x + w / 2, ty + 16, text_anchor='middle',
                           font_family=FONT, fill='#6b7280', dominant_baseline='central'))


def arrow_down(d, x, y1, y2, arrow_marker, label=None):
    """Draw a vertical arrow with optional label."""
    d.append(draw.Line(x, y1, x, y2, stroke=ARROW_COLOR, stroke_width=1.5, marker_end=arrow_marker))
    if label:
        d.append(draw.Text(label, 10, x + 6, (y1 + y2) / 2, font_family=FONT,
                           fill='#6b7280', dominant_baseline='central'))


def arrow_right(d, x1, x2, y, arrow_marker, label=None):
    """Draw a horizontal arrow with optional label."""
    d.append(draw.Line(x1, y, x2, y, stroke=ARROW_COLOR, stroke_width=1.5, marker_end=arrow_marker))
    if label:
        d.append(draw.Text(label, 10, (x1 + x2) / 2, y - 8, text_anchor='middle',
                           font_family=FONT, fill='#6b7280'))


def diagram_stack(data):
    """Layered stack diagram (vertical).

    data: {"layers": [{"label": "...", "color": "blue", "subtitle": "..."}], "arrows": ["label1", ...]}
    """
    layers = data["layers"]
    arrows = data.get("arrows", [None] * (len(layers) - 1))
    box_w, box_h, gap = 240, 50, 20
    padding = 50
    total_h = len(layers) * box_h + (len(layers) - 1) * gap + 20
    total_w = box_w + padding * 2

    d = draw.Drawing(total_w, total_h)
    marker = _make_arrow(d)

    y = 10
    for i, layer in enumerate(layers):
        labeled_box(d, padding, y, box_w, box_h, layer["label"],
                    layer.get("color", "blue"), layer.get("subtitle"))
        if i < len(layers) - 1:
            arrow_label = arrows[i] if i < len(arrows) else None
            arrow_down(d, padding + box_w / 2, y + box_h, y + box_h + gap, marker, arrow_label)
        y += box_h + gap

    return d


def diagram_flow(data):
    """Left-to-right flow diagram.

    data: {"nodes": [{"label": "...", "color": "blue"}], "arrows": ["label1", ...]}
    """
    nodes = data["nodes"]
    arrows = data.get("arrows", [None] * (len(nodes) - 1))
    box_w, box_h, gap = 120, 50, 40
    total_w = len(nodes) * box_w + (len(nodes) - 1) * gap + 20
    total_h = box_h + 40

    d = draw.Drawing(total_w, total_h)
    marker = _make_arrow(d)

    x = 10
    for i, node in enumerate(nodes):
        labeled_box(d, x, 20, box_w, box_h, node["label"], node.get("color", "blue"))
        if i < len(nodes) - 1:
            arrow_label = arrows[i] if i < len(arrows) else None
            arrow_right(d, x + box_w, x + box_w + gap, 20 + box_h / 2, marker, arrow_label)
        x += box_w + gap

    return d


def diagram_hub(data):
    """Hub-and-spoke diagram (center + radial connections).

    data: {"center": {"label": "...", "color": "blue"}, "spokes": [{"label": "...", "color": "gray"}]}
    """
    center = data["center"]
    spokes = data["spokes"]

    cx, cy = 200, 150
    hub_w, hub_h = 130, 60
    spoke_w, spoke_h = 110, 40
    radius = 120

    import math
    n = len(spokes)
    total_w = cx * 2 + spoke_w
    total_h = cy * 2 + spoke_h

    d = draw.Drawing(total_w, total_h)
    marker = _make_arrow(d)

    # Draw hub
    labeled_box(d, cx - hub_w / 2, cy - hub_h / 2, hub_w, hub_h, center["label"], center.get("color", "blue"))

    # Draw spokes
    for i, spoke in enumerate(spokes):
        angle = (2 * math.pi * i / n) - math.pi / 2
        sx = cx + radius * math.cos(angle) - spoke_w / 2
        sy = cy + radius * math.sin(angle) - spoke_h / 2

        labeled_box(d, sx, sy, spoke_w, spoke_h, spoke["label"], spoke.get("color", "gray"))

        # Arrow from hub edge to spoke
        edge_x = cx + (hub_w / 2 + 5) * math.cos(angle)
        edge_y = cy + (hub_h / 2 + 5) * math.sin(angle)
        spoke_edge_x = sx + spoke_w / 2 - (spoke_w / 2 - 5) * math.cos(angle)
        spoke_edge_y = sy + spoke_h / 2 - (spoke_h / 2 - 5) * math.sin(angle)

        d.append(draw.Line(edge_x, edge_y, spoke_edge_x, spoke_edge_y,
                           stroke=ARROW_COLOR, stroke_width=1.5, marker_end=marker))

    return d


def diagram_graph(data):
    """Free-form graph with named nodes and edges (supports fan-out/fan-in).

    data: {
      "direction": "LR"|"TB" (default "LR"),
      "nodes": [{"id": "x", "label": "...", "color"|"preset": "blue"}],
      "edges": [{"from": "x"|["x","y"], "to": "z"|["z","w"], "label": "..."}],
      "groups": [{"label": "...", "nodes": ["x", "y"]}]  (optional)
    }
    """
    direction = data.get("direction", "LR")
    nodes = {n["id"]: n for n in data["nodes"]}
    edges = data.get("edges", [])
    groups = data.get("groups", [])
    is_lr = direction == "LR"
    box_w, box_h = (120, 50) if is_lr else (140, 50)
    gap_major, gap_minor = 50, 30

    # Assign ranks via topological BFS
    node_ids = list(nodes.keys())
    in_degree = {nid: 0 for nid in node_ids}
    for e in edges:
        targets = e["to"] if isinstance(e["to"], list) else [e["to"]]
        for t in targets:
            if t in in_degree:
                in_degree[t] += 1

    ranks = {}
    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    rank = 0
    while queue:
        for nid in queue:
            ranks[nid] = rank
        next_queue = []
        for e in edges:
            sources = e["from"] if isinstance(e["from"], list) else [e["from"]]
            targets = e["to"] if isinstance(e["to"], list) else [e["to"]]
            for s in sources:
                if s in queue:
                    for t in targets:
                        in_degree[t] -= 1
                        if in_degree[t] == 0 and t not in ranks:
                            next_queue.append(t)
        queue = next_queue
        rank += 1

    for nid in node_ids:
        if nid not in ranks:
            ranks[nid] = rank

    # Group by rank, calculate positions
    rank_groups = {}
    for nid, r in ranks.items():
        rank_groups.setdefault(r, []).append(nid)

    num_ranks = max(ranks.values()) + 1
    max_per_rank = max(len(v) for v in rank_groups.values())

    if is_lr:
        total_w = num_ranks * (box_w + gap_major) + 20
        total_h = max(max_per_rank * (box_h + gap_minor) + 40, 100)
    else:
        total_w = max(max_per_rank * (box_w + gap_minor) + 40, 200)
        total_h = num_ranks * (box_h + gap_major) + 20

    positions = {}
    for r, nids in rank_groups.items():
        for i, nid in enumerate(nids):
            if is_lr:
                x = 10 + r * (box_w + gap_major)
                span = len(nids) * (box_h + gap_minor) - gap_minor
                y = (total_h - span) / 2 + i * (box_h + gap_minor)
            else:
                span = len(nids) * (box_w + gap_minor) - gap_minor
                x = (total_w - span) / 2 + i * (box_w + gap_minor)
                y = 10 + r * (box_h + gap_major)
            positions[nid] = (x, y)

    d = draw.Drawing(total_w, total_h)
    marker = _make_arrow(d)

    # Draw group backgrounds
    for group in groups:
        gnids = [n for n in group.get("nodes", []) if n in positions]
        if not gnids:
            continue
        gxs = [positions[n][0] for n in gnids]
        gys = [positions[n][1] for n in gnids]
        gx, gy = min(gxs) - 10, min(gys) - 25
        gw = max(gxs) - min(gxs) + box_w + 20
        gh = max(gys) - min(gys) + box_h + 35
        d.append(draw.Rectangle(gx, gy, gw, gh, rx=8, fill='#f9fafb',
                                stroke='#d1d5db', stroke_width=1, stroke_dasharray='4'))
        d.append(draw.Text(group.get("label", ""), 10, gx + 8, gy + 12,
                           font_family=FONT, fill='#6b7280'))

    # Draw nodes
    for nid, node in nodes.items():
        if nid in positions:
            x, y = positions[nid]
            color = node.get("color", node.get("preset", "blue"))
            labeled_box(d, x, y, box_w, box_h, node["label"], color, node.get("subtitle"))

    # Draw edges (fan-out/fan-in)
    for e in edges:
        sources = e["from"] if isinstance(e["from"], list) else [e["from"]]
        targets = e["to"] if isinstance(e["to"], list) else [e["to"]]
        label = e.get("label")
        for s in sources:
            for t in targets:
                if s not in positions or t not in positions:
                    continue
                sx, sy = positions[s]
                tx, ty = positions[t]
                if is_lr:
                    x1, y1 = sx + box_w, sy + box_h / 2
                    x2, y2 = tx, ty + box_h / 2
                else:
                    x1, y1 = sx + box_w / 2, sy + box_h
                    x2, y2 = tx + box_w / 2, ty
                d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW_COLOR,
                                   stroke_width=1.5, marker_end=marker))
        # Label on first edge
        if label and sources and targets:
            s, t = sources[0], targets[0]
            if s in positions and t in positions:
                sx, sy = positions[s]
                tx, ty = positions[t]
                if is_lr:
                    lx = (sx + box_w + tx) / 2
                    ly = (sy + ty) / 2 + box_h / 2 - 10
                else:
                    lx = (sx + tx) / 2 + box_w / 2
                    ly = (sy + box_h + ty) / 2 - 4
                d.append(draw.Text(label, 10, lx, ly, text_anchor='middle',
                                   font_family=FONT, fill='#6b7280'))

    return d


DIAGRAM_TYPES = {
    "stack": diagram_stack,
    "flow": diagram_flow,
    "hub": diagram_hub,
    "graph": diagram_graph,
}


# ---------------------------------------------------------------------------
# Graphviz backend
# ---------------------------------------------------------------------------

def _check_graphviz():
    """Verify graphviz Python package and system binary are available.

    Returns (graphviz_module, version_string) or exits with helpful error.
    """
    try:
        import graphviz as gv
    except ImportError:
        print("Error: graphviz Python package not installed.\n"
              "  Install: uv pip install graphviz", file=sys.stderr)
        sys.exit(2)

    try:
        ver = gv.version()
        return gv, ".".join(str(v) for v in ver)
    except gv.ExecutableNotFound:
        print("Error: Graphviz system binary (dot) not found.\n"
              "  Install: sudo apt-get install graphviz  (Linux)\n"
              "           brew install graphviz            (macOS)", file=sys.stderr)
        sys.exit(2)


def _select_engine(data):
    """Auto-select layout engine from graph properties.

    Rules:
    - Directed edges (default) + no groups → dot
    - Directed + groups → dot (only dot/fdp handle clusters)
    - Undirected + groups → fdp
    - Undirected + no groups + ≤100 nodes → neato
    - Undirected + no groups + >100 nodes → sfdp
    - Explicit "engine" in data overrides everything
    """
    if "engine" in data:
        return data["engine"]

    directed = data.get("directed", True)
    has_groups = bool(data.get("groups"))
    node_count = len(data.get("nodes", []))

    if directed:
        return "dot"
    elif has_groups:
        return "fdp"
    elif node_count > 100:
        return "sfdp"
    else:
        return "neato"


def _resolve_color(color_name):
    """Resolve a color/preset name to (fill, stroke) tuple."""
    if color_name in PRESETS:
        color_name = PRESETS[color_name]
    c = COLORS.get(color_name, COLORS["blue"])
    return c["fill"], c["stroke"]


def diagram_graphviz(data, title=None):
    """Render a graph using Graphviz auto-layout.

    data: {
      "directed": true|false (default true),
      "direction": "TB"|"LR"|"BT"|"RL" (default "TB"),
      "engine": "dot"|"neato"|"fdp"|"sfdp"|"circo"|"twopi" (optional, auto-selected),
      "nodes": [{"id": "x", "label": "...", "color"|"preset": "blue"}],
      "edges": [{"from": "x", "to": "y", "label": "...", "color": "gray"}],
      "groups": [{"label": "...", "color": "gray", "nodes": ["x", "y"]}]
    }

    Returns inline SVG string.
    """
    gv, version = _check_graphviz()
    import graphviz

    directed = data.get("directed", True)
    direction = data.get("direction", "TB")
    engine = _select_engine(data)

    # Warn if clusters used with an engine that ignores them
    if data.get("groups") and engine not in ("dot", "fdp"):
        print(f"Warning: engine '{engine}' ignores cluster/group boundaries. "
              f"Use dot or fdp for groups.", file=sys.stderr)

    GraphClass = graphviz.Digraph if directed else graphviz.Graph

    g = GraphClass(
        engine=engine,
        format="svg_inline",
        graph_attr={
            "rankdir": direction,
            "bgcolor": "transparent",
            "fontname": "system-ui, sans-serif",
            "pad": "0.3",
            "nodesep": "0.5",
            "ranksep": "0.6",
        },
        node_attr={
            "shape": "box",
            "style": "filled,rounded",
            "fontname": "system-ui, sans-serif",
            "fontsize": "12",
            "penwidth": "1.5",
        },
        edge_attr={
            "fontname": "system-ui, sans-serif",
            "fontsize": "10",
            "color": ARROW_COLOR,
            "penwidth": "1.5",
        },
    )

    # Determinism for force-directed engines
    if engine in ("neato", "fdp", "sfdp"):
        g.attr(start="42")
    if engine in ("neato", "fdp"):
        g.attr(overlap="false", sep="+5")
    if engine == "sfdp":
        g.attr(overlap="prism")

    # Build node lookup for groups
    grouped_nodes = set()
    for group in data.get("groups", []):
        grouped_nodes.update(group.get("nodes", []))

    # Draw groups as clusters
    for i, group in enumerate(data.get("groups", [])):
        group_color = group.get("color", "gray")
        fill, stroke = _resolve_color(group_color)
        with g.subgraph(name=f"cluster_{i}") as c:
            c.attr(
                style="filled,rounded",
                color=stroke,
                fillcolor=fill,
                label=group.get("label", ""),
                fontsize="11",
                labeljust="l",
            )
            for nid in group.get("nodes", []):
                # Find node data
                node_data = next((n for n in data["nodes"] if n["id"] == nid), None)
                if node_data:
                    nfill, nstroke = _resolve_color(
                        node_data.get("color", node_data.get("preset", "blue"))
                    )
                    c.node(nid, label=node_data["label"],
                           fillcolor=nfill, color=nstroke)

    # Draw ungrouped nodes
    for node in data["nodes"]:
        nid = node["id"]
        if nid not in grouped_nodes:
            fill, stroke = _resolve_color(node.get("color", node.get("preset", "blue")))
            g.node(nid, label=node["label"], fillcolor=fill, color=stroke)

    # Draw edges
    for edge in data.get("edges", []):
        sources = edge["from"] if isinstance(edge["from"], list) else [edge["from"]]
        targets = edge["to"] if isinstance(edge["to"], list) else [edge["to"]]
        label = edge.get("label", "")
        edge_color = ARROW_COLOR
        if "color" in edge:
            _, edge_color = _resolve_color(edge["color"])
        for s in sources:
            for t in targets:
                g.edge(s, t, label=label, color=edge_color, fontcolor="#6b7280")

    # Render to SVG string
    svg_str = g.pipe(encoding="utf-8")

    # Strip comments
    svg_str = re.sub(r'<!--[\s\S]*?-->\s*', '', svg_str)

    return svg_str


DIAGRAM_TYPES = {
    "stack": diagram_stack,
    "flow": diagram_flow,
    "hub": diagram_hub,
    "graph": diagram_graph,
}


def main():
    parser = argparse.ArgumentParser(description="Generate teaching diagrams as inline SVG")
    parser.add_argument("--type", required=True, choices=DIAGRAM_TYPES.keys(),
                        help="Diagram type: stack, flow, hub, graph")
    parser.add_argument("--data", required=True, help="JSON data for the diagram")
    parser.add_argument("--title", default=None,
                        help="Accessible title for the SVG (used in <title> and aria-labelledby)")
    parser.add_argument("--backend", choices=["builtin", "graphviz"], default="builtin",
                        help="Layout backend: builtin (drawsvg) or graphviz (auto-layout)")
    parser.add_argument("--engine", default=None,
                        choices=["dot", "neato", "fdp", "sfdp", "circo", "twopi"],
                        help="Graphviz engine override (only with --backend graphviz)")
    args = parser.parse_args()

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in --data: {e}", file=sys.stderr)
        sys.exit(2)

    if args.engine and args.backend != "graphviz":
        print("Warning: --engine is ignored without --backend graphviz", file=sys.stderr)

    # Inject engine override into data
    if args.engine:
        data["engine"] = args.engine

    if args.backend == "graphviz":
        svg_str = diagram_graphviz(data, title=args.title)
    else:
        diagram_fn = DIAGRAM_TYPES[args.type]
        d = diagram_fn(data)
        svg_str = d.as_svg()

    # Post-process SVG for accessibility + responsive scaling
    # Remove XML declaration if present
    svg_str = re.sub(r'<\?xml[^?]*\?>\s*', '', svg_str)

    # Extract width/height from <svg> tag, convert to viewBox-only
    match = re.search(r'<svg[^>]*>', svg_str)
    if match:
        svg_tag = match.group(0)
        w_match = re.search(r'width="([^"]+)"', svg_tag)
        h_match = re.search(r'height="([^"]+)"', svg_tag)
        w = w_match.group(1) if w_match else '400'
        h = h_match.group(1) if h_match else '300'

        # Graphviz uses pt units — convert to unitless for viewBox
        w_val = w.replace('pt', '').strip()
        h_val = h.replace('pt', '').strip()

        # Remove width, height, and any existing viewBox
        new_tag = re.sub(r'\s*width="[^"]*"', '', svg_tag)
        new_tag = re.sub(r'\s*height="[^"]*"', '', new_tag)
        new_tag = re.sub(r'\s*viewBox="[^"]*"', '', new_tag)

        # Build accessibility and scaling attributes
        attrs = f'viewBox="0 0 {w_val} {h_val}" role="img"'
        if args.title:
            attrs += ' aria-labelledby="diagram-title"'
        attrs += ' style="display:block;margin:1.5rem auto;max-width:100%;height:auto"'

        new_tag = new_tag.replace('<svg', f'<svg {attrs}', 1)
        svg_str = svg_str.replace(svg_tag, new_tag)

    # Insert <title> as first child of <svg>
    if args.title:
        title_el = f'<title id="diagram-title">{args.title}</title>'
        svg_str = re.sub(r'(<svg[^>]*>)', r'\1' + title_el, svg_str, count=1)

    print(svg_str)


if __name__ == "__main__":
    main()
