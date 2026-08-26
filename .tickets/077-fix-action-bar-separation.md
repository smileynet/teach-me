---
id: "077"
title: "Fix: lesson action bar needs stronger visual separation from content"
status: done
priority: high
blocked_by: []
type: feature
tags: [platform]
---

# Fix: action bar visual separation

## Problem

At the bottom of long lessons, the "What's next" action bar blends into the lesson content. There's no clear visual break indicating "the lesson ends here, actions start here."

## What to build

Add visual separation between lesson content and the action bar:
- Horizontal rule or increased top margin
- Slightly different background shade or border treatment
- Consider a "—" divider or "End of lesson" subtle marker

## Acceptance criteria

- [x] Clear visual break between lesson content and action bar
- [x] Action bar is immediately recognizable as a navigation element (not content)
- [x] Consistent across all lesson pages (via lesson-actions.js CSS)

## Validation

- **E2E (Playwright):** Screenshot lesson bottom → verify visible separation between last content block and action bar
