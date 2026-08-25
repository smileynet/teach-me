// 01_flow_and_knots.ink
// Reference story for Lesson 01: Flow & Knots
// Demonstrates: knots, diverts, loose-end-free endings, basic choices, comments, -> END

// The story starts here — flow begins at the top
-> opening

=== opening ===
The morning sun filters through dusty blinds. Your desk is cluttered
with half-finished maps and cold coffee.

A note on the door reads: "Meeting in the archive. Come when ready."

* [Head to the archive] -> archive_entrance
* [Finish your coffee first] -> coffee_first
- -> archive_entrance

=== coffee_first ===
You take a long sip. The coffee is terrible — but it's yours.

Feeling slightly more awake, you grab your coat and head out.
-> archive_entrance

=== archive_entrance ===
The archive is three floors down, past rows of shelves that smell
like old paper and forgotten intentions.

A librarian nods as you pass. The meeting room door is ajar.

// Both paths converge here — this is what makes knots powerful.
// No matter which choice the reader made, they arrive at the same place.

-> meeting

=== meeting ===
Inside, two colleagues are already arguing over a map spread
across the table.

"Ah, you're here," says Maren, not looking up. "We found something."

She taps a point on the map where three rivers converge.
"This doesn't match any survey on record."

The meeting has begun. Whatever comes next will require
leaving the building — and your comfortable routine — behind.

-> END
