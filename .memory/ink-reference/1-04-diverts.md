---
type: ink-reference
source: WritingWithInk.md
part: 1
section: "Diverts"
tags: ["diverts"]
---

<!-- search: Developers search for this when: connecting knots, jumping between sections, -> arrow syntax, invisible flow, glue -->

# Diverts
*Part 1 of Writing with ink*


### Knots divert to knots

You can tell the story to move from one knot to another using `->`, a "divert arrow". Diverts happen immediately without any user input.

```ink
=== back_in_london ===

We arrived into London at 9.45pm exactly.
-> hurry_home

=== hurry_home ===
We hurried home to Savile Row as fast as we could.
```

#### Diverts are invisible

Diverts are intended to be seamless and can even happen mid-sentence:

```ink
=== hurry_home ===
We hurried home to Savile Row -> as_fast_as_we_could

=== as_fast_as_we_could ===
as fast as we could.
```

produces the same line as above:

```text
We hurried home to Savile Row as fast as we could.
```

#### Glue

The default behaviour inserts line-breaks before every new line of content. In some cases, however, content must insist on not having a line-break, and it can do so using `<>`, or "glue".

```ink
=== hurry_home ===
We hurried home <>
-> to_savile_row

=== to_savile_row ===
to Savile Row
-> as_fast_as_we_could

=== as_fast_as_we_could ===
<> as fast as we could.
```

also produces:

```ink
We hurried home to Savile Row as fast as we could.
```

You can't use too much glue: multiple glues next to each other have no additional effect. (And there's no way to "negate" a glue; once a line is sticky, it'll stick.)

