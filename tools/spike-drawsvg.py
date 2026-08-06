#!/usr/bin/env python3
"""Spike 001: Test drawsvg for teaching diagrams.

Generates 3 diagram types and outputs them as inline SVG in an HTML file.
"""
import drawsvg as draw


def make_arrow_marker():
    """Reusable arrowhead marker."""
    arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='#374151', close=True))
    return arrow


def layered_stack():
    """Diagram 1: Layered architecture (Iceberg metadata tree)."""
    d = draw.Drawing(340, 280)
    arrow = make_arrow_marker()

    layers = [
        ("AWS Glue Data Catalog", "#dbeafe", "#2563eb"),
        ("Metadata Files (JSON)", "#fef3c7", "#d97706"),
        ("Manifest Files (Avro)", "#fef3c7", "#d97706"),
        ("Data Files (Parquet)", "#dcfce7", "#16a34a"),
    ]

    y = 10
    for i, (label, fill, stroke) in enumerate(layers):
        d.append(draw.Rectangle(60, y, 220, 50, rx=6, fill=fill, stroke=stroke, stroke_width=1.5))
        d.append(draw.Text(label, 13, 170, y + 28, text_anchor='middle',
                           font_family='system-ui, sans-serif', font_weight='600'))
        if i < len(layers) - 1:
            d.append(draw.Line(170, y + 50, 170, y + 65,
                               stroke='#374151', stroke_width=1.5, marker_end=arrow))
        y += 65

    return d


def left_to_right_flow():
    """Diagram 2: Data pipeline flow."""
    d = draw.Drawing(560, 90)
    arrow = make_arrow_marker()

    nodes = [
        ("Producers", "#dbeafe", "#2563eb"),
        ("Glue ETL", "#fef3c7", "#d97706"),
        ("Iceberg Table", "#dcfce7", "#16a34a"),
        ("Athena Query", "#dbeafe", "#2563eb"),
    ]

    x = 10
    for i, (label, fill, stroke) in enumerate(nodes):
        d.append(draw.Rectangle(x, 20, 110, 50, rx=6, fill=fill, stroke=stroke, stroke_width=1.5))
        d.append(draw.Text(label, 12, x + 55, 48, text_anchor='middle',
                           font_family='system-ui, sans-serif'))
        if i < len(nodes) - 1:
            d.append(draw.Line(x + 110, 45, x + 140, 45,
                               stroke='#374151', stroke_width=1.5, marker_end=arrow))
        x += 140

    return d


def hub_and_spoke():
    """Diagram 3: Central service with connections."""
    d = draw.Drawing(400, 300)
    arrow = make_arrow_marker()

    # Center hub
    d.append(draw.Rectangle(140, 120, 120, 60, rx=6, fill='#dbeafe', stroke='#2563eb', stroke_width=2))
    d.append(draw.Text('Glue Catalog', 13, 200, 153, text_anchor='middle',
                       font_family='system-ui, sans-serif', font_weight='600'))

    # Spokes
    spokes = [
        (150, 30, 100, 40, "Athena"),
        (290, 130, 100, 40, "EMR Spark"),
        (150, 230, 100, 40, "Redshift"),
        (10, 130, 100, 40, "Glue ETL"),
    ]

    connections = [
        (200, 120, 200, 70),   # top
        (260, 150, 290, 150),  # right
        (200, 180, 200, 230),  # bottom
        (140, 150, 110, 150),  # left
    ]

    for (sx, sy, sw, sh, label), (x1, y1, x2, y2) in zip(spokes, connections):
        d.append(draw.Rectangle(sx, sy, sw, sh, rx=6, fill='#f3f4f6', stroke='#6b7280', stroke_width=1.5))
        d.append(draw.Text(label, 12, sx + sw/2, sy + sh/2 + 4, text_anchor='middle',
                           font_family='system-ui, sans-serif'))
        d.append(draw.Line(x1, y1, x2, y2, stroke='#374151', stroke_width=1.5, marker_end=arrow))

    return d


# Generate all three and wrap in HTML
diagrams = [
    ("Layered Stack (Architecture)", layered_stack()),
    ("Left-to-Right Flow (Pipeline)", left_to_right_flow()),
    ("Hub and Spoke (Service Map)", hub_and_spoke()),
]

html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Spike 001: drawsvg</title>
<style>body{font-family:system-ui;max-width:800px;margin:2rem auto;padding:0 1rem}
h2{margin-top:2rem;color:#1a1a1a}svg{border:1px solid #eee;border-radius:4px;margin:1rem 0}</style>
</head><body><h1>Spike 001: drawsvg Teaching Diagrams</h1>
"""

for title, diagram in diagrams:
    html += f"<h2>{title}</h2>\n{diagram.as_svg()}\n"

html += "</body></html>"

with open("lessons/spike-drawsvg-test.html", "w") as f:
    f.write(html)

print(f"✓ Generated {len(diagrams)} diagrams")
print(f"✓ Output: lessons/spike-drawsvg-test.html")
print(f"✓ Lines of code per diagram: ~25-30")
for title, diagram in diagrams:
    svg_str = diagram.as_svg()
    print(f"  {title}: {len(svg_str)} bytes SVG")
