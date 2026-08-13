---
id: "038"
title: "Feature: diagram cards with label masking"
status: done
priority: medium
blocked_by: []
type: feature
---

# Feature: diagram cards with label masking

## What to build

SR cards that present a lesson diagram with specific labels hidden (slate gray masks with "???"). The learner clicks each mask to reveal the answer. In terminal mode, the card degrades to a text prompt + URL.

Proven by spike 040: CSS class toggle, `<g>` groups per mask, per-element click-to-reveal.

## Design (from spike 040 v2)

### Card Schema

Two new optional fields on Card:

```python
# Reference to an SVG in a lesson
svg_ref: dict | None = None
# {"lesson_file": "lessons/0001-iceberg-metadata-tree.html",
#  "svg_index": 1,
#  "description": "Iceberg metadata tree — four layers from catalog to data files"}

# Labels to hide (matched against <text> content in the SVG)
occluded_labels: list[str] | None = None
# ["AWS Glue Data Catalog", "Metadata Files (JSON)", "Manifest Files (Avro)", "Data Files (Parquet)"]
```

### Masking Function

```python
def mask_svg(svg_str: str, labels_to_hide: list[str]) -> str:
    """Replace matching <text> elements with slate mask + ???.
    
    Wraps each match in a <g class="mask-group" onclick="revealOne(this)">
    with the original text (class=label-text, opacity=0) and a mask rect + ??? overlay.
    """
```

- Identify `<text>` elements whose content matches `occluded_labels`
- Get x, y, font-size from attributes to position the mask rect
- Wrap in `<g class="mask-group">` with onclick handler
- Mask color: `#585b70` (slate gray — neutral against all layer colors)

### Rendering

**Browser (quick-check.py):**
- Extract SVG from lesson HTML by index
- Apply masking function
- Embed masked SVG in the card div
- Include click-to-reveal JS + CSS (from spike v2)
- After all masks revealed: show explanation + sources

**Terminal (review.py):**
- Show `svg_ref.description` as context
- Render prompt as normal text
- Append `file://` URL to the lesson for visual reference

### What NOT to build

- No SVG editor or mask drawing tool
- No auto-detection of which labels to hide (teach skill decides at card-generation time)
- No per-mask independent scheduling (all masks = one card)
- No image occlusion regions (just text label replacement)
- No ASCII art conversion

## Acceptance criteria

- [x] `svg_ref` and `occluded_labels` fields added to Card schema
- [x] `mask_svg()` function extracts and masks SVG text elements
- [x] quick-check.py renders diagram cards with click-to-reveal masks
- [x] Mask color is slate gray (#585b70), hover darkens, click reveals with transition
- [x] Terminal review shows description + text prompt (answerable without diagram)
- [x] At least one diagram card exists in the Iceberg question bank
- [x] Card is answerable in both modes (text prompt is sufficient, diagram adds context)
