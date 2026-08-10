# Project Glossary

Domain terms and naming decisions for teach-me.

**teach-me**:
A test bed for learning-oriented agent skills, refined here before deploying globally via crew-research.
_Avoid_: the product, the platform

**Teaching workspace**:
A per-topic directory holding mission, resources, lessons, learning records, and assets — the folder is the continuity, not the conversation.
_Avoid_: course, project

**teach**:
The core skill — multi-session topic learning using a stateful teaching workspace.
_Avoid_: tutor, lesson-plan

**quiz-me**:
Skill that tests the learner's retention by interviewing them on what they've learned. Adapted from grilling, reframed for knowledge verification.
_Avoid_: grill-me (overloaded — grilling is for plan-sharpening, not knowledge-testing)

**wait-what**:
Skill that re-explains when comprehension fails. Fires mid-lesson. Names the listener's state, not the output.
_Avoid_: tldr, simplify

**Mission**:
The concrete real-world reason a user is learning a topic. Grounds every teaching decision.
_Avoid_: goal, objective (too abstract)

**Learning record**:
An ADR-style note capturing demonstrated understanding — not exposure, not coverage. Drives zone of proximal development calculation.
_Avoid_: progress log, activity log

**Zone of proximal development (ZPD)**:
The range where material is challenging enough to require effort but not so far ahead it's unlearnable. Each lesson targets this.
_Avoid_: difficulty level

**Storage strength**:
Long-term retention — the real goal of teaching. Built through retrieval practice, spacing, interleaving.
_Avoid_: fluency (that's in-the-moment recall, feels like mastery but isn't)

**Reference doc**:
A compressed, scannable companion to a lesson — what you pull up at work. Captures the conceptual model and key facts in lookup form. Generated alongside the lesson, not as a separate step.
_Avoid_: summary, cheat sheet (though colloquially acceptable)

**Socratic gate**:
A brief conversation (via quiz-me) where the learner explains concepts in their own words before progressing. Tests understanding through dialog, not recall through quiz. Framed as work conversations from the mission.
_Avoid_: exam, test, quiz (those imply scoring)

**Jargon skill**:
Post-authoring pass that annotates domain-specific terms with glossary tooltips. Three-gate filter: domain-specific, mental model wrong/absent, not explained inline.
_Avoid_: glossary pass (the glossary is the component; jargon is the skill that populates it)

**Scaffold**:
An HTML template in `assets/scaffolds/` that the agent reads before generating a page. Ensures consistent structure, theming, and asset links across all page types.
_Avoid_: template (overloaded with SSG connotations)

**Criteria-based answer**:
The expected answer format for SR cards. States what the learner should mention, not exact wording to reproduce. Format: "Should mention: (1)... (2)... Bonus:..."
_Avoid_: script, exact answer, model answer

**Progressive overload**:
The single mechanism behind all training adaptation — systematically increasing stimulus over time. Used as the workout example's core concept.
_Avoid_: progressive difficulty (different concept in game design)

**Research-first**:
The hard gate requiring domain research before writing any lesson. Established by ADR 0002 after finding 8 factual errors in the Iceberg lesson and having the roguelike premise overturned entirely.
_Avoid_: optional research step
