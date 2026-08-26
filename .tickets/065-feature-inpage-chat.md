---
id: "065"
title: "Feature: in-page chat — ask questions about the current lesson"
status: open
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Feature: in-page chat

## Problem

Lesson pages say "ask me anything" but there's no mechanism for it. The learner has to switch to a terminal and invoke kiro-cli manually. An in-page chat widget would let them ask clarifying questions without leaving the lesson.

## What to explore

### Minimal viable chat
- Floating button or collapsible panel at bottom-right
- Text input + send button
- Messages stream via SSE (same pattern as generation)
- Context: kiro-cli receives the current lesson title/content as context
- Responses render as markdown in the chat panel

### Technical questions
1. How to pass lesson context to kiro-cli without exceeding prompt limits?
2. Should chat history persist across page reloads? (localStorage?)
3. Can we reuse the existing `/api/generate` endpoint or need a separate `/api/chat`?
4. How to handle multiple turns? (kiro-cli --no-interactive is single-turn)
5. Would a WebSocket be better than SSE for bidirectional chat?

### UX considerations
- Chat should not obscure lesson content
- Should feel lightweight (not a full chatbot UI)
- Mobile: full-screen overlay when active?
- Clear "new conversation" vs "continue"

## Deliverable

In-page chat widget on lesson pages. Learner types a question → kiro-cli answers with lesson context → response streams into the panel.

## Validation

- **E2E (Playwright):** Open a lesson → click chat button → type a question → verify response streams in → verify response is contextually relevant to the lesson topic
- **Integration:** `/api/chat` endpoint accepts `{message, context_lesson}`, spawns kiro-cli with context, returns SSE stream
