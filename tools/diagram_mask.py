#!/usr/bin/env python3
"""Diagram label masking for SR cards.

Extracts SVGs from lesson HTML and replaces specified text labels with
clickable mask overlays (slate gray rects with "???").
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MASK_COLOR = "#585b70"
MASK_TEXT_COLOR = "#cdd6f4"

# CSS + JS needed for diagram cards (injected once per page)
DIAGRAM_CARD_STYLES = """
    .mask-group { cursor: pointer; }
    .mask-group:hover .mask-rect { opacity: 0.7; }
    .mask-group .mask-rect,
    .mask-group .mask-text { transition: opacity 0.3s ease; }
    .mask-group .label-text { transition: opacity 0.3s ease; opacity: 0; }
    .mask-group.revealed .mask-rect,
    .mask-group.revealed .mask-text { opacity: 0; pointer-events: none; }
    .mask-group.revealed .label-text { opacity: 1; }
    .mask-group.revealed { cursor: default; }
"""

DIAGRAM_CARD_JS = """
function revealOne(group) {
  if (group.classList.contains('revealed')) return;
  group.classList.add('revealed');
  // Update card status if all masks in this SVG are revealed
  const svg = group.closest('svg');
  const remaining = svg.querySelectorAll('.mask-group:not(.revealed)').length;
  const cardEl = svg.closest('.card');
  const status = cardEl ? cardEl.querySelector('.diagram-status') : null;
  if (status) {
    if (remaining === 0) {
      status.textContent = '✓ All labels revealed';
      // Trigger card feedback if available
      if (cardEl) {
        const feedbackEl = document.getElementById(cardEl.id + '-feedback');
        if (feedbackEl) {
          feedbackEl.classList.add('show', 'correct');
          feedbackEl.textContent = '✓ ' + (explanations[cardEl.id] || 'All labels identified correctly.');
          const cardSources = sources[cardEl.id];
          if (cardSources && cardSources.length) {
            const srcDiv = document.createElement('div');
            srcDiv.className = 'qc-sources';
            srcDiv.innerHTML = '<p class="qc-sources-label">📖 Go deeper:</p>' +
              cardSources.map(s =>
                '<a href="' + s.url + '" target="_blank" rel="noopener">' +
                s.label + (s.section ? ' <span class="source-section">— ' + s.section + '</span>' : '') +
                '</a>'
              ).join('');
            feedbackEl.appendChild(srcDiv);
          }
        }
      }
      answered++;
      correct++;
      if (answered === total) showSummary();
    } else {
      status.textContent = remaining + ' label' + (remaining > 1 ? 's' : '') + ' remaining';
    }
  }
}
"""


def extract_svg(lesson_file: str, svg_index: int = 0) -> str | None:
    """Extract an SVG from a lesson HTML file by index."""
    path = PROJECT_ROOT / lesson_file
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    svgs = re.findall(r'<svg[^>]*>.*?</svg>', content, re.DOTALL)
    if svg_index >= len(svgs):
        return None
    return svgs[svg_index]


def mask_svg(svg_str: str, labels_to_hide: list[str]) -> str:
    """Replace matching <text> elements with clickable mask groups.

    For each <text> whose content matches a label in labels_to_hide:
    - Wraps in a <g class="mask-group" onclick="revealOne(this)">
    - Adds the original text with class="label-text" (hidden by CSS)
    - Adds a mask rect + "???" text overlay (visible by CSS)
    """
    for label in labels_to_hide:
        # Find the text element with this exact content
        pattern = re.compile(
            r'<text([^>]*)>' + re.escape(label) + r'</text>'
        )
        match = pattern.search(svg_str)
        if not match:
            continue

        attrs = match.group(0)
        text_attrs = match.group(1)

        # Extract positioning from attributes
        x = _attr_val(text_attrs, "x", "170")
        y = _attr_val(text_attrs, "y", "100")
        font_size = int(_attr_val(text_attrs, "font-size", "13"))

        # Compute mask rect position (centered on text)
        rect_width = max(len(label) * font_size * 0.55, 100)
        rect_height = font_size + 6
        rect_x = float(x) - rect_width / 2
        rect_y = float(y) - rect_height / 2

        # Check if text-anchor is middle (centered) or not
        if "text-anchor" not in text_attrs:
            # Left-aligned text — rect starts at x
            rect_x = float(x) - 5
            rect_width = max(len(label) * font_size * 0.55, 100)

        # Build the replacement group
        replacement = (
            f'<g class="mask-group" onclick="revealOne(this)">'
            f'<text class="label-text" {text_attrs.strip()}>{label}</text>'
            f'<rect class="mask-rect" x="{rect_x:.0f}" y="{rect_y:.0f}" '
            f'width="{rect_width:.0f}" height="{rect_height:.0f}" rx="3" fill="{MASK_COLOR}"/>'
            f'<text class="mask-text" x="{x}" y="{y}" font-size="{font_size - 1}" '
            f'text-anchor="middle" font-family="system-ui, sans-serif" font-weight="600" '
            f'fill="{MASK_TEXT_COLOR}" dominant-baseline="central">???</text>'
            f'</g>'
        )

        svg_str = svg_str.replace(attrs, replacement, 1)

    return svg_str


def _attr_val(attrs: str, name: str, default: str = "") -> str:
    """Extract an attribute value from an attribute string."""
    match = re.search(rf'{name}="([^"]*)"', attrs)
    return match.group(1) if match else default
