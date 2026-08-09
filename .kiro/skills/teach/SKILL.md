---
name: teach
description: "Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace. Trigger: teach, teach me, learn, I want to learn, help me understand, next lesson."
metadata:
  type: process
  invocation: user-only
  practice: null
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## Teaching Workspace

Treat the current directory as a teaching workspace. The state of their learning is captured in this directory in several files:

- `MISSION.md`: A document capturing the _reason_ the user is interested in the topic. This should be used to ground all teaching. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: A directory of reference documents. Compressed, scannable companions to lessons — the conceptual model plus facts in lookup form. What the learner pulls up at work. Generated alongside each lesson.
- `RESOURCES.md`: A list of resources which can be explored to ground your teaching in contextual knowledge, or to acquire knowledge and wisdom. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./learning-records/*.md`: A directory of learning records, which capture what the user has learned. These are loosely equivalent to architectural decision records in software development - they capture non-obvious lessons and key insights that may need to be revised later, or drive future sessions. These should be used to calculate the zone of proximal development. They are titled `0001-<dash-case-name>.md`, where the number increments each time. Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.html`: A directory of lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching in this workspace.
- `./assets/*`: Reusable **components** shared across lessons. See [Assets](#assets).
- `NOTES.md`: A scratchpad for you to jot down user preferences, or working notes.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before the `RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Try to design lessons which build long-term retention by desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice - for skills practice only)

## Lessons

A lesson is the main thing you produce — the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file, saved to `./lessons/` and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful** — clean, readable typography and layout — since the user will return to these later to review. Think Tufte.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

### Lesson Opening Structure

Every lesson starts with brief orientation, then gets to the content:

1. **End-state preview** (one sentence after lesson-meta): What the learner will be able to explain or do after this lesson. Keep it concrete and testable.

2. **Context** (1-3 sentences): Why this matters for their mission. State the problem this concept solves — not as a narrative, but as a direct "here's what breaks without this" framing. The learner already has motivation (their mission); they just need to know why THIS piece matters.

3. **Then teach.** Get to the mechanics quickly. The learner wants to understand and move on.

The tone is a knowledgeable colleague at a whiteboard — direct, assumes intelligence, doesn't over-explain motivation.

### Referencing Prior Concepts

When a concept from a prior lesson reappears, briefly restate it in a clause. Don't assume the learner remembers.

- Good: "The manifest list (which tracks which data files belong to a snapshot) also stores..."
- Bad: "The manifest list also stores..." (assumes they remember what it does)
- Bad: "As we discussed in Lesson 1, the manifest list is a file that..." (too formal, too long)

One clause is enough. If the concept needs more than a sentence to refresh, use a `<details>` reminder instead.

### Writing Style

- **Grade 8-10 reading level.** Sentences average 15-20 words. Cap at 25 words.
- **No subordinate clause stacking.** One conditional or relative clause per sentence max.
- **No idioms or cultural references.** Non-native speakers are part of the audience.
- **Short paragraphs.** 1-4 sentences. Single-sentence paragraphs are fine for emphasis.
- **Plain words.** "Use" not "utilize", "find" not "ascertain", "show" not "demonstrate".

### Grounding Claims

When stating facts (latency, scale, failure modes): cite a source or frame as general ("at scale, listing becomes the bottleneck"). Don't invent specific numbers. End-state preview should be testable against the lesson's quiz or challenge.

If possible, open the lesson file for the user by running a CLI command.

Each lesson should link via HTML anchors to other lessons and reference documents.

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

Each lesson with an architectural or conceptual explanation **must include at least one inline SVG diagram**. Place a one-line verbal summary above the diagram. For complex architectures with 3+ layers, use the progressive-reveal component (`data-step` attributes + `assets/progressive-reveal.js`).

## Assets

Lessons are built from reusable **components**, stored in `./assets/`: stylesheets, quiz widgets, simulators, diagram helpers — anything a second lesson could reuse.

Reuse is the default, not the exception. Before authoring a lesson, read `./assets/` and build from the components already there. When a lesson needs something new and reusable, write it as a component in `./assets/` and link to it — never inline code a future lesson would duplicate.

A shared stylesheet is the first component every workspace earns: every lesson links it, so the lessons look like one consistent course rather than a pile of one-offs. As the workspace grows, so should the component library.

### Diagrams

Every architectural or conceptual explanation needs a visual. Before creating one:

1. Read `./assets/svg-patterns.md` for reusable snippet patterns
2. Follow `.kiro/steering/visual-teaching.md` for color vocabulary and anti-patterns
3. Choose the right tool:

| Diagram type | Method |
|-------------|--------|
| Standard teaching diagram (stack, flow, hub) | `python tools/draw-diagram.py --type X --data '{...}'` |
| Custom layout or annotated detail | Raw inline SVG from patterns |
| Complex auto-layout (sequence, state machine) | D2 (`d2 input.d2 output.svg`) |

**Rules:**
- One-line verbal summary ABOVE every diagram (dual coding principle)
- Max 5-9 elements per diagram — break complex systems into multiple
- Use progressive reveal (`data-step` attrs + `assets/progressive-reveal.js`) for 3+ layers
- Colors: blue=primary, green=output, amber=processing/warning, red=error, gray=infrastructure
- Labels go ON the diagram, never separate

### Glossary Terms

On first use of a domain term the learner may not know, wrap it in a glossary tooltip:

```html
<!-- Inline definition (one-off terms specific to this lesson) -->
<span class="term" data-def="A complete set of data files visible at a point in time.">snapshot</span>

<!-- Glossary lookup (term defined in the JSON block below) -->
<span class="term" data-term="snapshot">snapshot</span>

<!-- With link to reference doc -->
<span class="term" data-term="snapshot" data-ref="glossary.html#snapshot">snapshot</span>
```

At the bottom of the lesson (before `</body>`), include a glossary JSON block and the script:

```html
<script type="application/json" id="glossary-data">
{ "snapshot": "A complete set of data files visible at a point in time." }
</script>
<script src="../assets/glossary.js"></script>
```

Also link `assets/glossary.css` in the `<head>`. After the lesson, add any new terms to `.memory/CONTEXT.md`.

### Collapsible Details

Use `<details>` for content that's useful but not required to follow the lesson. Three use cases:

```html
<!-- Deep dive: optional "why" or "how" beyond the core explanation -->
<details>
<summary>How does pruning actually work?</summary>
<p>Each manifest file records min/max values per column...</p>
</details>

<!-- Practical note: operational detail for later reference -->
<details>
<summary>What does compaction look like in practice?</summary>
<p>You run a periodic job that merges small manifest files...</p>
</details>

<!-- Reminder (for multi-lesson workspaces): restate a prior concept -->
<details>
<summary>Reminder: how snapshots work</summary>
<p>Each snapshot is a frozen view of which files belong to the table...</p>
</details>
```

**When to use:** The core lesson path should be understandable without opening any `<details>`. Use them for:
- Deeper "why" that would interrupt flow
- Operational/practical notes the learner may want later
- Prior-concept reminders in later lessons

**When NOT to use:** Don't hide core content. If the learner needs it to understand the lesson's point, it belongs in the main flow.

### Exercises (optional)

When the learner's mission involves *applying* knowledge (not just understanding it), add a brief exercise near the end of the lesson. Use `<details>` for progressive hints:

```html
<div class="next-steps">
  <h3>Check Your Understanding</h3>
  <p><strong>Exercise:</strong> [A question that tests WHY, not WHAT]</p>
  <details><summary>Hint</summary><p>...</p></details>
  <details><summary>Key points to hit</summary><p>...</p></details>
</div>
```

**Test understanding, not recall.** Good exercises ask the learner to explain, compare, or defend — not to recite steps or trace a diagram mechanically.

- Good: "Your customer asks X. Explain why the naive approach breaks and what this design does differently."
- Bad: "List the five layers in order." (that's recall, not understanding)
- Bad: "Trace the query path from A to B." (mechanical, doesn't require insight)

The exercise should be answerable by someone who *understands* the lesson's core insight, even if they can't remember every detail.

## The Mission

Every lesson should be tied into the mission - the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or the `MISSION.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal - make sure to update the `MISSION.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

## Zone Of Proximal Development

Each lesson, the user should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading their `learning-records`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `RESOURCES.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically.

For quizzes, each answer should be exactly the same number of words (and characters, if possible). Don't give the user any clues about the answer through formatting.

When embedding a quiz, include a noscript fallback so the lesson degrades gracefully without JavaScript:

```html
<noscript>
  <p><em>This quiz requires JavaScript to run. The questions and answers are visible below — try answering mentally, then check the source for the correct answer marked with <code>data-correct</code>.</em></p>
</noscript>
```

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it.

## Reference Documents

When writing a lesson, simultaneously produce a companion reference doc in `reference/`. The lesson teaches; the reference doc is what the learner pulls up at work.

**Lessons are rarely revisited. Reference docs are.** They should capture the conceptual model and key facts — designed for a quick lookup during a meeting, architecture review, or decision-making.

### What a reference doc captures

1. **The core concept** — the mental model in one sentence ("Iceberg is a metadata tree that replaces file listing")
2. **The key visual** — the diagram that makes the concept stick
3. **Facts in lookup form** — tables, not paragraphs
4. **Decision aids** — "when X, do Y" (if applicable to the topic)
5. **Terms introduced** — short definitions for the vocabulary this lesson added

The reference doc is NOT a summary of the lesson. It's the *conceptual model plus the facts you'd look up*. If the lesson explains why something works, the reference shows what it is and how to use it.

### Generating references

Produce `reference/NNNN-slug.html` alongside each lesson in the same authoring pass. Same stylesheet, different structure. Cross-link both directions.

### The test

A colleague who never read the lesson should be able to:
- Understand the core concept from the reference alone
- Look up a specific fact (what layer stores what, where it lives)
- Make a decision using the reference as support

If they can't, the reference is missing the conceptual model or the facts aren't scannable enough.

## Socratic Gate

After delivering a lesson, have a conversation with the learner to help them think through what they've learned. The goal isn't evaluation — it's helping them build confidence that they can explain and apply the concepts.

This is what `quiz-me` does. When the learner returns for the next session, the agent should start with a brief conversation about the previous lesson before producing new material. The `quiz-me` skill can also be invoked explicitly by the learner at any time.

### How it works

Ask the learner to explain a core concept in their own words. Then help them think through it — ask follow-ups, offer worked examples, probe gently. Continue until they feel confident in their understanding.

The conversation should feel like talking through an idea with a colleague, not like an oral exam.

### What to ask

Frame questions around the learner's actual mission — the conversations they'll have at work:

- "How would you explain [concept] to [person from their context]?"
- "If someone asked you [realistic question], what would you say?"
- "Walk me through what happens when [scenario relevant to their work]"

### What NOT to do

- Don't ask recall questions ("name the five layers")
- Don't grade or score
- Don't block progression — if the learner wants to move on, let them
- Don't re-teach the lesson — ask questions that help *them* articulate it

### After the conversation

Write a learning record capturing what the learner demonstrated understanding of, and any concepts they're still working through. This drives what gets taught next.

## `NOTES.md`

The user will sometimes express preferences of how they want to be taught, or things you should keep in mind. This is the place to record those preferences, so you can refer back to them when designing lessons or working with the user.

## Before Publishing a Lesson

Quick sanity check after writing:

- [ ] Brief context at top — why this matters for the mission
- [ ] At least one diagram for architectural/conceptual content
- [ ] Factual claims cited or framed as general
- [ ] Jargon annotated (run the jargon skill)
- [ ] Reference doc generated alongside
- [ ] "What's Next" section present

## It's Working If

- The first thing it does in an empty workspace is ask why the learner wants this — not produce a lesson
- RESOURCES.md fills before lessons do, and each lesson names a primary source worth reading yourself
- Claims in lessons carry links out. A lesson with no citations is teaching from memory.
- A lesson takes one sitting and leaves the learner able to explain one thing they couldn't before
- After the lesson, the learner can talk through the concepts in their own words — and feels ready to
- Reference docs are useful at work — the learner pulls one up in a meeting and it helps
- Opening a fresh session in the workspace continues the course, not restarts it
- Learning records grow, and lessons stop re-teaching what's already been demonstrated
- Lessons look like one course — they share a stylesheet and visual language
- A question that needs real-world judgment gets a resource pointer, not just an answer

## It's NOT Working If

- It produces a lesson before understanding why the learner cares
- Lessons cite no sources — the agent is teaching from memory
- The learner reads lessons but never explains anything back
- Reference docs read like shorter lessons instead of scannable lookup artifacts
- Every lesson re-explains concepts from lesson 1 regardless of what's been demonstrated
- The workspace accumulates files but the learner can't have better conversations at work
