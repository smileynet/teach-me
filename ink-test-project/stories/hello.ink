// hello.ink — Minimal story for spike validation
// Tests: basic flow, choices, knots, variables

VAR player_name = "stranger"

=== start ===
Hello, {player_name}. Welcome to the ink test.
This story proves inkgd works in Godot 4.

* [Introduce yourself] -> introduce
* [Stay silent] -> silent

=== introduce ===
~ player_name = "friend"
You offer your name. "A pleasure to meet you, {player_name}."
-> ending

=== silent ===
You say nothing. The silence stretches.
-> ending

=== ending ===
That's the end of the spike test.
The runtime loaded, choices worked, and variables updated.
-> END
