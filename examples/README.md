# Example Teaching Workspace: Apache Iceberg on AWS

This is a real teaching workspace created during skill development. It serves as a **test fixture** for validating feature improvements to the teach, quiz-me, and visual tooling.

## What's here

| Path | Purpose |
|------|---------|
| `MISSION.md` | Mission: learn Iceberg for customer advisory |
| `RESOURCES.md` | Curated sources (Iceberg spec, AWS docs, communities) |
| `NOTES.md` | Learner profile and preferences |
| `learning-records/0001-*.md` | Prior knowledge baseline |
| `lessons/0001-iceberg-metadata-tree.html` | Lesson 1 with inline SVG diagram |
| `lessons/spike-quiz-test.html` | Quiz component demo (3 questions with source links) |
| `lessons/spike-reveal-test.html` | Progressive reveal demo (step-by-step diagram) |
| `lessons/spike-drawsvg-test.html` | drawsvg output demo (3 diagram types) |

## Use as test fixture

When improving skills or components, test against this workspace:

```bash
# Verify lesson renders
open lessons/0001-iceberg-metadata-tree.html

# Verify quiz component
open lessons/spike-quiz-test.html

# Verify progressive reveal
open lessons/spike-reveal-test.html

# Verify diagram generation
source .venv/bin/activate
python tools/draw-diagram.py --type stack --data "$(python -c "
import json; print(json.dumps({
  'layers': [
    {'label': 'Glue Catalog', 'color': 'blue'},
    {'label': 'Metadata', 'color': 'amber'},
    {'label': 'Data Files', 'color': 'green'}
  ],
  'arrows': ['points to', 'lists']
}))")"
```

## What to test feature changes against

| Feature | Test with |
|---------|-----------|
| Teach skill changes | Does lesson 1 still follow the new guidance? |
| Quiz component changes | Does spike-quiz-test.html still work? (shuffle, feedback, source links) |
| Progressive reveal changes | Does spike-reveal-test.html still advance? (click, keyboard, buttons) |
| draw-diagram.py changes | Do all 3 types in spike-drawsvg-test.html still render? |
| Visual steering changes | Does lesson 1's SVG comply with the updated rules? |
| Glossary component (future) | Add terms from this lesson as test data |
| Accessibility (ticket 013) | Apply ARIA fixes to lesson 1 and verify |
