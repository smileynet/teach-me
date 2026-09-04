---
id: "291"
title: "Doc/asset mismatch: lesson 0018 says 256x256 threshold map, wired mask is 1024x1024"
status: open
blocked_by: []
priority: low
tags: [mktoon, content-quality]
---

# Doc/asset mismatch: lesson 0018 says 256x256 threshold map, wired mask is 1024x1024

## Problem

Surfaced during #253. Lesson 0018 (`04-toon-control-maps.html`) prose describes baking the
threshold map at 256×256, but the wired asset `test-scene/assets/masks/toon_threshold.png` is
**1024×1024** (the noise map `toon_noise.png` is 256×256 as described). So the lesson text and
the shipped asset disagree on the threshold map's resolution.

Neither is wrong per se (threshold is low-frequency, so 1024 works fine), but the lesson should
match the asset — either update the prose to 1024, or re-bake/downscale the mask to 256 and
confirm it still reads. Low priority, cosmetic-doc.

## Acceptance criteria

- [ ] Lesson 0018 prose and the wired `toon_threshold.png` agree on resolution
- [ ] If the mask is changed, `mise run verify` still EXIT 0 and the #253 figure still reads
      (re-capture if the mask resolution materially changes the threshold panel)
