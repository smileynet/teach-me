---
type: ink-reference
source: WritingWithInk.md
part: 1
section: "Game Queries and Functions"
tags: ["functions", "game-queries"]
---

<!-- search: Developers search for this when: CHOICE_COUNT, TURNS, TURNS_SINCE, SEED_RANDOM, querying game state from ink -->

# Game Queries and Functions
*Part 1 of Writing with ink*


**ink** provides a few useful 'game level' queries about game state, for use in conditional logic. They're not quite parts of the language, but they're always available, and they can't be edited by the author. In a sense, they're the "standard library functions" of the language.

The convention is to name these in capital letters.

### CHOICE_COUNT()

`CHOICE_COUNT` returns the number of options created so far in the current chunk. So for instance.

```ink
*	{false} Option A
* 	{true} Option B
*  {CHOICE_COUNT() == 1} Option C
```

produces two options, B and C. This can be useful for controlling how many options a player gets on a turn.

### TURNS()

This returns the number of game turns since the game began.

### TURNS_SINCE(-> knot)

`TURNS_SINCE` returns the number of moves (formally, player inputs) since a particular knot/stitch was last visited.

A value of 0 means "was seen as part of the current chunk". A value of -1 means "has never been seen". Any other positive value means it has been seen that many turns ago.

```ink
*	{TURNS_SINCE(-> sleeping.intro) > 10} You are feeling tired... -> sleeping
* 	{TURNS_SINCE(-> laugh) == 0}  You try to stop laughing.
```

Note that the parameter passed to `TURNS_SINCE` is a "divert target", not simply the knot address itself (because the knot address is a number - the read count - not a location in the story...)

TODO: (requirement of passing `-c` to the compiler)

#### Sneak preview: using TURNS_SINCE in a function

The `TURNS_SINCE(->x) == 0` test is so useful it's often worth wrapping it up as an ink function.

```ink
=== function came_from(-> x)
	~ return TURNS_SINCE(x) == 0
```

The section on [functions](#5-functions) outlines the syntax here a bit more clearly but the above allows you to say things like:

```ink
* {came_from(->  nice_welcome)} 'I'm happy to be here!'
* {came_from(->  nasty_welcome)} 'Let's keep this quick.'
```

... and have the game react to content the player saw *just now*.

### SEED_RANDOM()

For testing purposes, it's often useful to fix the random number generator so ink will produce the same outcomes every time you play. You can do this by "seeding" the random number system.

```ink
~ SEED_RANDOM(235)
```

The number you pass to the seed function is arbitrary, but providing different seeds will result in different sequences of outcomes.

#### Advanced: more queries

You can make your own external functions, though the syntax is a bit different: see the section on [functions](#5-functions) below.



So far, we've been building branched stories in the simplest way, with "options" that link to "pages".

But this requires us to uniquely name every destination in the story, which can slow down writing and discourage minor branching.

**ink** has a much more powerful syntax available, designed for simplifying story flows which have an always-forwards direction (as most stories do, and most computer programs don't).

This format is called "weave", and its built out of the basic content/option syntax with two new features: the gather mark, `-`, and the nesting of choices and gathers.
