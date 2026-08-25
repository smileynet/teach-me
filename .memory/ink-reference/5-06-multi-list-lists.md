---
type: ink-reference
source: WritingWithInk.md
part: 5
section: "Multi-list Lists"
tags: ["lists"]
---

<!-- search: Developers search for this when: tracking objects with lists, multiple state machines, cross-list queries -->

# Multi-list Lists
*Part 5 of Writing with ink*



So far, all of our examples have included one large simplification, again - that the values in a list variable have to all be from the same list family. But they don't.

This allows us to use lists - which have so far played the role of state-machines and flag-trackers - to also act as general properties, which is useful for world modelling.

This is our inception moment. The results are powerful, but also more like "real code" than anything that's come before.

### Lists to track objects

For instance, we might define:

```ink
LIST Characters = Alfred, Batman, Robin
LIST Props = champagne_glass, newspaper

VAR BallroomContents = (Alfred, Batman, newspaper)
VAR HallwayContents = (Robin, champagne_glass)
```

We could then describe the contents of any room by testing its state:

```ink
=== function describe_room(roomState)
	{ roomState ? Alfred: Alfred is here, standing quietly in a corner. } { roomState ? Batman: Batman's presence dominates all. } { roomState ? Robin: Robin is all but forgotten. }
	<> { roomState ? champagne_glass: A champagne glass lies discarded on the floor. } { roomState ? newspaper: On one table, a headline blares out WHO IS THE BATMAN? AND *WHO* IS HIS BARELY-REMEMBERED ASSISTANT? }
```

So then:

```ink
{ describe_room(BallroomContents) }
```

produces:

```text
Alfred is here, standing quietly in a corner. Batman's presence dominates all.

On one table, a headline blares out WHO IS THE BATMAN? AND *WHO* IS HIS BARELY-REMEMBERED ASSISTANT?
```

While:

```ink
{ describe_room(HallwayContents) }
```

gives:

```ink
Robin is all but forgotten.

A champagne glass lies discarded on the floor.
```

And we could have options based on combinations of things:

```ink
*	{ currentRoomState ? (Batman, Alfred) } [Talk to Alfred and Batman]
	'Say, do you two know each other?'
```

### Lists to track multiple states

We can model devices with multiple states. Back to the kettle again...

```ink
LIST OnOff = on, off
LIST HotCold = cold, warm, hot

VAR kettleState = (off, cold) // we need brackets because it's a proper, multi-valued list now

=== function turnOnKettle() ===
{ kettleState ? hot:
	You turn on the kettle, but it immediately flips off again.
- else:
	The water in the kettle begins to heat up.
	~ kettleState -= off
	~ kettleState += on
	// note we avoid "=" as it'll remove all existing states
}

=== function can_make_tea() ===
	~ return kettleState ? (hot, off)
```

These mixed states can make changing state a bit trickier, as the off/on above demonstrates, so the following helper function can be useful.

 	=== function changeStateTo(ref stateVariable, stateToReach)
 		// remove all states of this type
 		~ stateVariable -= LIST_ALL(stateToReach)
 		// put back the state we want
 		~ stateVariable += stateToReach

 which enables code like:

 	~ changeState(kettleState, on)
 	~ changeState(kettleState, warm)


#### How does this affect queries?

The queries given above mostly generalise nicely to multi-valued lists

    LIST Letters = a,b,c
    LIST Numbers = one, two, three

    VAR mixedList = (a, three, c)

```ink
{LIST_ALL(mixedList)}   // a, one, b, two, c, three
```
    {LIST_COUNT(mixedList)} // 3
    {LIST_MIN(mixedList)}   // a
    {LIST_MAX(mixedList)}   // three or c, albeit unpredictably

    {mixedList ? (a,b) }        // false
    {mixedList ^ LIST_ALL(a)}   // a, c

    { mixedList >= (one, a) }   // true
    { mixedList < (three) }     // false

```ink
{ LIST_INVERT(mixedList) }            // one, b, two
```

