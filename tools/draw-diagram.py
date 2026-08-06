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

FONT = "system-ui, sans-serif"
ARROW_COLOR = "#374151"


def _make_arrow(drawing):
    """Create and return a reusable arrowhead marker."""
    arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill=ARROW_COLOR, close=True))
    return arrow


def labeled_box(d, x, y, w, h, label, color="blue", subtitle=None):
    """Draw a rounded labeled box."""
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


DIAGRAM_TYPES = {
    "stack": diagram_stack,
    "flow": diagram_flow,
    "hub": diagram_hub,
}


def main():
    parser = argparse.ArgumentParser(description="Generate teaching diagrams as inline SVG")
    parser.add_argument("--type", required=True, choices=DIAGRAM_TYPES.keys(),
                        help="Diagram type: stack, flow, hub")
    parser.add_argument("--data", required=True, help="JSON data for the diagram")
    parser.add_argument("--step-attrs", action="store_true",
                        help="Add data-step attributes for progressive reveal (one step per element)")
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
