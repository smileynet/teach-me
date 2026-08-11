---
id: "040"
title: "Spike: diagram label masking — can we hide/reveal SVG text for SR?"
status: open
priority: low
blocked_by: []
type: spike
---

# Spike: diagram label masking for SR cards

## Question to answer

Can we take an existing inline SVG from a lesson, mask specific `<text>` labels, and present it as a quiz where revealing the answer shows the hidden labels? Does this work at acceptable visual quality with our existing diagrams?

## What to test

1. Take one SVG from the Iceberg lesson (the metadata tree diagram)
2. Parse it, find `<text>` elements, replace 2-3 with amber mask rectangles + "???"
3. Render in the quick-check page format
4. On reveal, swap masks back to original text (CSS transition or class toggle)
5. Check: does this look good? Is the interaction clear?

## Minimal implementation

```python
# Pseudocode for the spike
svg = extract_svg_from_lesson("lessons/0001-iceberg-metadata-tree.html", index=0)
labels_to_hide = ["Manifest List", "Manifest File"]
masked_svg = mask_labels(svg, labels_to_hide)  # rect overlay + "???"
revealed_svg = svg  # original with all labels
```

## Success criteria

- [ ] SVG renders correctly with masked labels in a browser
- [ ] Reveal transition looks natural (not jarring)
- [ ] Works with our existing draw-diagram.py output (viewBox, no fixed dimensions)
- [ ] Answerable from context (remaining labels + structure give enough clues)
- [ ] Terminal fallback: text description + prompt works without the image

## What this does NOT test

- Full card schema integration
- Automated label selection (which labels to hide)
- SM-2 scheduling of diagram cards
- Production CSS/JS — just a proof-of-concept page

## Expected output

A single HTML file in `.scratch/` demonstrating the masked → revealed flow. If it works, update ticket 038 with implementation plan.
