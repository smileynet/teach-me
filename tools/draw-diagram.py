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


def main():
    parser = argparse.ArgumentParser(description="Generate teaching diagrams as inline SVG")
    parser.add_argument("--type", required=True, choices=DIAGRAM_TYPES.keys(),
                        help="Diagram type: stack, flow, hub, graph")
    parser.add_argument("--data", required=True, help="JSON data for the diagram")
    args = parser.parse_args()

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in --data: {e}", file=sys.stderr)
        sys.exit(2)

    diagram_fn = DIAGRAM_TYPES[args.type]
    d = diagram_fn(data)
    print(d.as_svg())


if __name__ == "__main__":
    main()
