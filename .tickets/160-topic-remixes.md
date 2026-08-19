---
id: "160"
title: "Feature: topic remixes — re-teach a concept in a different language/framework, preserving both as complementary alternatives"
status: backlog
blocked_by: []
priority: low
---

# Feature: topic remixes — re-teach a concept in a different language/framework, preserving both as complementary alternatives

## What to build

Allow a user to "remix" an existing topic into a different language, framework, or context. For example: "I learned this in Rust — now teach it in Python." The remix generates a new lesson that covers the same conceptual ground but in the target ecosystem, and both versions are preserved side-by-side as complementary alternatives.

Key behaviors:
- User names a source topic + target language/framework
- Agent generates a remix lesson that maps concepts 1:1 where possible, noting where idioms diverge
- Both original and remix live in the same topic area, linked to each other
- MAP.md (or equivalent) shows both variants with a "remix" relationship
- Reference docs, SR cards, and quizzes are generated for the remix independently
- Differences and trade-offs between approaches are highlighted (not just transliterated)

## Acceptance criteria

- [ ] User can request a remix of an existing topic into a different language/framework
- [ ] Remix lesson maps concepts to the target ecosystem, noting idiom differences
- [ ] Original and remix are linked bidirectionally (each references the other)
- [ ] MAP.md represents the remix relationship (variant/alternative, not prerequisite)
- [ ] Remix gets its own reference doc, SR cards, and quiz
- [ ] Key differences between approaches are surfaced explicitly in the lesson
- [ ] Both versions remain independently navigable (no forced comparison view)
