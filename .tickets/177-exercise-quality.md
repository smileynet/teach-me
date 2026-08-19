---
id: "177"
title: "Strengthen Check Your Understanding exercises — test core concepts"
status: open
blocked_by: []
priority: high
---

# Strengthen Check Your Understanding exercises — test core concepts

## Context

Current "Check Your Understanding" exercises at the end of lessons are weak:
- They test edge cases or gotchas rather than the core concepts taught in the lesson
- The toon-banding exercise asks about multi-light blowout (`+=` vs `max()`) — a tangential detail, not the central concepts (modulo trick, curve texture, band discretization)
- The spatial-shader-anatomy exercise asks about coordinate space confusion — valid but narrow; doesn't test whether the learner understands the three-function pipeline itself

A reader who can answer the exercise might still not understand the lesson's primary content. The exercise should be the moment where the learner proves they got the main thing.

## What to build

### 1. Exercise design guidelines (add to visual-teaching.md or teach skill)

Exercises MUST:
- Test the **core concept** of the lesson, not a secondary detail or gotcha
- Be answerable by someone who understood the lesson's main arc
- Require **applying** the concept, not just recalling a fact
- Connect to the lesson's "Win" statement — if the win says "you can implement three banding approaches and explain when to use each," the exercise should test that

Exercises SHOULD:
- Ask "given this situation, which approach would you choose and why?" (application)
- Ask "explain to a colleague how X works" (teach-back)
- Ask "predict what happens if you change Y" (mental model)
- Build on the lesson's own code blocks (not introduce new unrelated scenarios)

Exercises SHOULD NOT:
- Test gotchas that weren't the lesson's focus
- Require knowledge from later lessons
- Have answers that are a single line of code without explanation
- Focus on debugging/error scenarios when the lesson taught concepts

### 2. Review and rewrite existing exercises

Audit all current exercises against these criteria. For the toon shader lessons:

**0003 (Spatial Shader Anatomy):**
- Current: "Why does applying MODEL_MATRIX to VERTEX in fragment() produce garbage?" — tests the coordinate space trap (secondary concept)
- Better: "You have a new mesh in your scene. Walk through the steps to get it rendering with your toon shader — what do you create, what do you assign, and what does each of the three functions contribute?" — tests the core pipeline understanding

**0004 (Toon Banding):**
- Current: "Multi-light blowout with +=" — tests a tangential detail from the exercise section
- Better: "You're art-directing a scene and need: narrow bright highlight, wide midtone, sharp shadow edge. Which of the three approaches gives you this control, and why can't the other two?" — tests the central trade-off comparison

### 3. Update generate-topic skill

Add to Phase 2 exercise generation instructions:
- Exercise must test the lesson's Win statement
- Review the exercise against the H2 sections — does it cover the main teaching arc?
- If the exercise only tests a detail, rewrite targeting the core concept

## Acceptance criteria

- [ ] Exercise design guidelines documented (visual-teaching.md or teach skill)
- [ ] Lesson 0003 exercise rewritten to test core pipeline understanding
- [ ] Lesson 0004 exercise rewritten to test banding approach trade-offs
- [ ] generate-topic skill updated with exercise quality criteria
- [ ] Lesson-validation skill's Q7 check updated to verify exercise targets core concept (not just existence)
