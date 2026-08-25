---
type: ink-reference
source: WritingWithInk.md
part: 1
section: "Knots"
tags: ["knots"]
---

<!-- search: Developers search for this when: structuring ink stories, creating named sections, dividing content into pieces, === syntax -->

# Knots
*Part 1 of Writing with ink*


### Pieces of content are called knots

To allow the game to branch we need to mark up sections of content with names (as an old-fashioned gamebook does with its 'Paragraph 18', and the like.)

These sections are called "knots" and they're the fundamental structural unit of ink content.

### Writing a knot

The start of a knot is indicated by two or more equals signs, as follows.

```ink
=== top_knot ===
```

(The equals signs on the end are optional; and the name needs to be a single word with no spaces.)

The start of a knot is a header; the content that follows will be inside that knot.

```ink
=== back_in_london ===

We arrived into London at 9.45pm exactly.
```

#### Advanced: a knottier "hello world"

When you start an ink file, content outside of knots will be run automatically. But knots won't. So if you start using knots to hold your content, you'll need to tell the game where to go. We do this with a divert arrow `->`, which is covered properly in the next section.

The simplest knotty script is:

```ink
-> top_knot

=== top_knot ===
Hello world!
```

However, **ink** doesn't like loose ends, and produces a warning on compilation and/or run-time when it thinks this has happened. The script above produces this on compilation:

```ink
WARNING: Apparent loose end exists where the flow runs out. Do you need a '-> END' statement, choice or divert? on line 3 of tests/test.ink
```

and this on running:

```ink
Runtime error in tests/test.ink line 3: ran out of content. Do you need a '-> DONE' or '-> END'?
```

The following plays and compiles without error:

```ink
=== top_knot ===
Hello world!
-> END
```

`-> END` is a marker for both the writer and the compiler; it means "the story flow should now stop".
