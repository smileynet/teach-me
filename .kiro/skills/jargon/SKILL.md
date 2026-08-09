---
name: jargon
description: "Review a lesson and annotate domain-specific jargon with tooltip definitions. Runs after content is written. Trigger: jargon, annotate terms, define jargon, mark up terms, glossary pass, annotate jargon."
metadata:
  type: process
  invocation: both
  practice: null
---

# Jargon

Review a written lesson and annotate domain-specific terms with glossary tooltips so newcomers can look up jargon without leaving the page.

## When to run

After a lesson is written and content is finalized. This is a post-processing pass — don't annotate while writing (it interrupts flow).

## Input

A lesson HTML file. If no path is given, operate on the most recent lesson in `lessons/`.

## Process

### 1. Read the lesson

Read the full HTML content. Identify the domain being taught (from the lesson title, content, and MISSION.md if available).

### 2. Extract candidate terms

Find words and phrases that are domain-specific jargon. Look for:
- Terms with a specific meaning in this domain
- Acronyms used without expansion
- Familiar words used with an unfamiliar domain-specific meaning
- Compound terms unique to this domain (e.g., "manifest list", "partition spec")

### 3. Filter ruthlessly

Apply these three gates. ALL must pass for a term to be annotated:

**Gate 1: Is this term specific to the domain being taught?**
Skip general computing terms (API, JSON, server, database), general cloud terms (S3, region), product names (Athena, Spark), and basic vocabulary the audience already has.

**Gate 2: Could the learner's mental model be wrong or absent?**
Define terms where:
- The word sounds familiar but means something specific here ("snapshot", "catalog", "partition")
- The concept has no everyday equivalent ("manifest list", "MVCC")
- Getting it wrong would cause confusion later

Skip terms that are genuinely self-explanatory in context.

**Gate 3: Is the term used WITHOUT inline explanation?**
If the surrounding sentence already defines the term (e.g., "compaction (merging small files into larger ones)"), skip it — a tooltip would be redundant. Only annotate terms the reader must look up themselves.

### 4. Write definitions

For each term that passes all three gates:
- One sentence, max two
- Plain language — no jargon in the definition
- Grounded in THIS domain's meaning, not a dictionary entry
- If the term has a misleading common meaning, address it: "In Iceberg, X means Y — not Z"

### 5. Annotate the lesson

- Wrap each term on **first use only** with `<span class="term" data-term="key">term</span>`
- Add a `<script type="application/json" id="glossary-data">` block before `</body>` with all definitions
- Add `<link rel="stylesheet" href="../assets/glossary.css">` to `<head>` if not present
- Add `<script src="../assets/glossary.js"></script>` before `</body>` if not present
- If you're annotating more than ~12 terms, the lesson is probably covering too much ground — but let the gates decide, not a hard count.

### 6. Check prior lessons (optional)

If other lessons exist in `lessons/`, scan their glossary JSON blocks. Terms already defined in earlier lessons can still be annotated (the learner may have forgotten), but prefer slightly shorter definitions for repeated terms.

## What NOT to define

| Category | Examples | Why skip |
|----------|----------|----------|
| General computing | API, JSON, server, query, schema | Audience already knows these |
| Cloud/infra basics | S3, region, bucket, endpoint | Not domain-specific |
| Product names | Athena, Spark, Trino, Glue | Names, not concepts |
| Terms explained inline | "...atomic commit (the pointer updates, or it doesn't)" | Already defined in text |
| Meta-terms about learning | lesson, concept, example | Not domain jargon |

## Definition style

Good:
> **snapshot** — A frozen view of which files belong to the table at one point in time. Every write creates a new one; readers always see a consistent set of files.

Bad:
> **snapshot** — In computer science, a snapshot refers to the state of a system at a particular point in time. In the context of Apache Iceberg...

Keep it conversational and short. The tooltip is small — the learner wants to unblock themselves, not read an essay.

## After annotating

Report what was annotated:
```
Annotated N terms: term1, term2, term3...
Skipped (inline explanation): term4, term5
Skipped (too general): term6, term7
```
