---
id: "145"
title: "Feature: situation index — symptom-first navigation ('I'm stuck on X' → relevant topic)"
status: open
blocked_by: []
priority: low
---

# Feature: situation index

## Context

Research finding (coding-best-practices reference): an inverted lookup that starts from observable symptoms/situations and routes to relevant content. Complements the topic map (which is concept-first) with a problem-first entry point.

## What to build

An alternative navigation surface: "I'm experiencing X" → here's the relevant topic/lesson.

Examples:
- "My baked texture looks washed out" → Lesson 5: Baking (section on Combined vs Emit)
- "Git merge conflicts keep happening" → Topic: branching strategies
- "My API returns 401" → Lesson: OIDC token validation

Implementation: a searchable index generated from lesson content, keyed by symptoms/problems/situations rather than concept names.

## Acceptance criteria

- [ ] Situation entries extracted from lessons (problems described, error states, common issues)
- [ ] Searchable/browsable situation index page
- [ ] Each situation links to the specific lesson section that addresses it
- [ ] Index grows automatically as new lessons are generated
- [ ] Accessible from map page as alternative entry point
