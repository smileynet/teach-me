---
id: "329"
title: "godot-asset-pipeline topic 6: reimport-and-round-trip-hygiene"
status: open
blocked_by: ["305", "325"]
validation_criteria:
  - "Lesson 06: from 'can get assets in' → 'source keeps changing / need it back out' → iterate loop, reimport-multiple, changing importer, reverse GLTFDocument export (runtime API), UID stability, .blend-vs-committed-glTF team tradeoff. Decision callout at that fork. Soft-prereq topic 5. References gltf-format round-trip fidelity. Lands at a mature round-trip"
  - "Runnable artifact (import → export-back → reimport) + asset:validate-gd L6 assertion (surface/vertex count preserved within tolerance)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 6: reimport-and-round-trip-hygiene

## What to build

TBD

## Acceptance criteria

- [ ] TBD
