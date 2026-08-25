---
type: ink-reference
source: WritingWithInk.md
part: 1
section: "Varying Choices"
tags: ["choices"]
---

<!-- search: Developers search for this when: once-only choices, sticky choices +, fallback choices, conditional choices, choices that disappear -->

# Varying Choices
*Part 1 of Writing with ink*


### Choices can only be used once

By default, every choice in the game can only be chosen once. If you don't have loops in your story, you'll never notice this behaviour. But if you do use loops, you'll quickly notice your options disappearing...

```ink
=== find_help ===

	You search desperately for a friendly face in the crowd.
	*	The woman in the hat[?] pushes you roughly aside. -> find_help
	*	The man with the briefcase[?] looks disgusted as you stumble past him. -> find_help
```

produces:

```text
You search desperately for a friendly face in the crowd.

1: The woman in the hat?
2: The man with the briefcase?

> 1
The woman in the hat pushes you roughly aside.
You search desperately for a friendly face in the crowd.

1: The man with the briefcase?

>
```

... and on the next loop you'll have no options left.

#### Fallback choices

The above example stops where it does, because the next choice ends up in an "out of content" run-time error.

```ink
> 1
The man with the briefcase looks disgusted as you stumble past him.
You search desperately for a friendly face in the crowd.

Runtime error in tests/test.ink line 6: ran out of content. Do you need a '-> DONE' or '-> END'?
```

We can resolve this with a 'fallback choice'. Fallback choices are never displayed to the player, but are 'chosen' by the game if no other options exist.

A fallback choice is simply a "choice without choice text":

```ink
*	-> out_of_options
```

And, in a slight abuse of syntax, we can make a default choice with content in it, using an "choice then arrow":

```ink
* 	->
	Mulder never could explain how he got out of that burning box car. -> season_2
```

#### Example of a fallback choice

Adding this into the previous example gives us:

```ink
=== find_help ===

	You search desperately for a friendly face in the crowd.
	*	The woman in the hat[?] pushes you roughly aside. -> find_help
	*	The man with the briefcase[?] looks disgusted as you stumble past him. -> find_help
	*	->
		But it is too late: you collapse onto the station platform. This is the end.
		-> END
```

and produces:

```ink
You search desperately for a friendly face in the crowd.

1: The woman in the hat?
2: The man with the briefcase?

> 1
The woman in the hat pushes you roughly aside.
You search desperately for a friendly face in the crowd.

1: The man with the briefcase?

> 1
The man with the briefcase looks disgusted as you stumble past him.
You search desperately for a friendly face in the crowd.
But it is too late: you collapse onto the station platform. This is the end.
```


### Sticky choices

The 'once-only' behaviour is not always what we want, of course, so we have a second kind of choice: the "sticky" choice. A sticky choice is simply one that doesn't get used up, and is marked by a `+` bullet.

```ink
=== homers_couch ===
	+	[Eat another donut]
		You eat another donut. -> homers_couch
	*	[Get off the couch]
		You struggle up off the couch to go and compose epic poetry.
		-> END
```

Fallback choices can be sticky too.

```ink
=== conversation_loop
	*	[Talk about the weather] -> chat_weather
	*	[Talk about the children] -> chat_children
	+	-> sit_in_silence_again
```

### Conditional Choices

You can also turn choices on and off by hand. **ink** has quite a lot of logic available, but the simplest tests is "has the player seen a particular piece of content".

Every knot/stitch in the game has a unique address (so it can be diverted to), and we use the same address to test if that piece of content has been seen.

```ink
*	{ not visit_paris } 	[Go to Paris] -> visit_paris
+ 	{ visit_paris 	 } 		[Return to Paris] -> visit_paris

*	{ visit_paris.met_estelle } [ Telephone Mme Estelle ] -> phone_estelle
```

Note that the test `knot_name` is true if *any* stitch inside that knot has been seen.

Note also that conditionals don't override the once-only behaviour of options, so you'll still need sticky options for repeatable choices.

#### Advanced: multiple conditions

You can use several logical tests on an option; if you do, *all* the tests must all be passed for the option to appear.

```ink
*	{ not visit_paris } 	[Go to Paris] -> visit_paris
+ 	{ visit_paris } { not bored_of_paris }
	[Return to Paris] -> visit_paris
```

#### Logical operators: AND and OR

The above "multiple conditions" are really just conditions with an the usual programming AND operator. Ink supports `and` (also written as `&&`) and `or` (also written as `||`) in the usual way, as well as brackets.

```ink
*	{ not (visit_paris or visit_rome) && (visit_london || visit_new_york) } [ Wait. Go where? I'm confused. ] -> visit_someplace
```

For non-programmers `X and Y` means both X and Y must be true. `X or Y` means either or both. We don't have a `xor`.

You can also use the standard `!` for `not`, though it'll sometimes confuse the compiler which thinks `{!text}` is a once-only list. We recommend using `not` because negated boolean tests are never that exciting.

#### Advanced: knot/stitch labels are actually read counts

The test:

```ink
*	{seen_clue} [Accuse Mr Jefferson]
```

is actually testing an *integer* and not a true/false flag. A knot or stitch used this way is actually an integer variable containing the number of times the content at the address has been seen by the player.

If it's non-zero, it'll return true in a test like the one above, but you can also be more specific as well:

```ink
* {seen_clue > 3} [Flat-out arrest Mr Jefferson]
```


#### Advanced: more logic

**ink** supports a lot more logic and conditionality than covered here - see the section on [variables and logic](#part-3-variables-and-logic).

