---
type: ink-reference
source: WritingWithInk.md
part: 5
section: "Basic Lists"
tags: ["lists"]
---

<!-- search: Developers search for this when: LIST keyword, defining lists, state machines in ink, enums, named states -->

# Basic Lists
*Part 5 of Writing with ink*


The basic unit of state-tracking is a list of states, defined using the `LIST` keyword. Note that a list is really nothing like a C# list (which is an array).

For instance, we might have:

```ink
LIST kettleState = cold, boiling, recently_boiled
```

This line defines two things: firstly three new values - `cold`, `boiling` and `recently_boiled` - and secondly, a variable, called `kettleState`, to hold these states.

We can tell the list what value to take:

```ink
~ kettleState = cold
```

We can change the value:

```ink
*	[Turn on kettle]
	The kettle begins to bubble and boil.
	~ kettleState = boiling
```

We can query the value:

```ink
*	[Touch the kettle]
	{ kettleState == cold:
		The kettle is cool to the touch.
	- else:
	 	The outside of the kettle is very warm!
	}
```

For convenience, we can give a list a value when it's defined using a bracket:

```ink
LIST kettleState = cold, (boiling), recently_boiled
// at the start of the game, this kettle is switched on. Edgy, huh?
```

...and if the notation for that looks a bit redundant, there's a reason for that coming up in a few subsections time.


