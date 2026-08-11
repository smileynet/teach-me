---
id: "040"
title: "Spike: diagram label masking — can we hide/reveal SVG text for SR?"
status: done
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

## Findings (2026-08-10)

**Result: Works.** The approach is visually clean and the interaction is intuitive.

### What worked

1. **CSS class toggle** (`masked`/`revealed`) with opacity transitions is the simplest possible implementation — no JS DOM manipulation of SVG elements needed at render time
2. **Sub-labels as clues** make the quiz answerable without external context. "pointer to current metadata" → catalog, "file list + column stats" → manifests
3. **Amber mask rects** are visually distinct from diagram content (no confusion about what's hidden vs what's a real element)
4. **viewBox SVG scales correctly** at any container width — responsive by default

### Implementation approach for production

- At card-generation time: identify bold `<text>` elements (font-weight=600) as maskable labels
- Add `.label-original` class to those elements
- Insert a sibling `<rect>` + `<text>???</text>` pair with `.label-mask` class at the same coordinates
- CSS handles the rest — no runtime SVG parsing needed in the browser

### Limitations discovered

- Mask rect positioning is manual (needs x/y/width matching the text bounds). Could auto-compute from font-size × character count, but imprecise
- Only works with `<text>` elements at known coordinates — won't work with path-based text or transformed groups
- Our draw-diagram.py output uses simple `<text x= y=>` positioning, so this works for all our diagrams

### Next step

Update ticket 038 with the proven approach: add `svg_ref` and `occluded_labels` fields to Card, write a masking function that takes an SVG + label list → masked SVG, integrate into quick-check.py rendering.
