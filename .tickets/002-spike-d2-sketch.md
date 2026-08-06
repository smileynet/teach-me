---
id: "002"
title: "Spike: D2 sketch mode for hand-drawn diagrams"
status: open
priority: high
blocked_by: []
type: spike
---

# Spike: D2 sketch mode for hand-drawn diagrams

## Question to answer

Does D2's sketch mode produce approachable hand-drawn diagrams suitable for teaching? Is the CLI workflow fast enough for agent use (write .d2 → render → embed)?

## Experiment

1. `brew install d2` (if not already installed)
2. Write 2-3 `.d2` files:
   - Architecture layers with containers
   - Data flow with labeled connections
   - Comparison (two side-by-side containers)
3. Render with `d2 --sketch input.d2 output.svg`
4. Also render WITHOUT sketch mode for comparison
5. Try `--no-xml-tag` for inline embedding
6. Measure: render time, file size, visual quality

## Success criteria

- [ ] D2 installs and runs on macOS
- [ ] Sketch mode produces visually distinct hand-drawn output
- [ ] SVG embeds in HTML correctly (with and without `--no-xml-tag`)
- [ ] Render time < 200ms per diagram
- [ ] D2 syntax is simple enough for agent to generate without errors

## Output

- `diagrams/spike/` — the test .d2 files
- `.scratch/spike-results/d2-results.md` — findings, screenshots/comparison, decision
