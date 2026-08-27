// 05_first_godot_integration.ink
// Reference story for Lesson 05 (First Godot Integration).
// Deterministic (no shuffle / RANDOM) so it earns a golden transcript.
// Small on purpose: one variable that changes, one branching choice, a
// clean END — just enough to drive the inkgd runtime loop in Godot.

VAR torch_lit = false

-> start

=== start ===
You stand at the mouth of a cave. Cold air drifts out of the dark.
A torch bracket juts from the wall beside you.
-> entrance

=== entrance ===
{torch_lit:
    Your torch throws light across the walls.
- else:
    The passage ahead is pitch black.
}
+ [Light the torch] -> light_torch
+ [Step inside anyway] -> step_inside

=== light_torch ===
~ torch_lit = true
You strike a spark. The torch catches and flares to life.
-> entrance

=== step_inside ===
{torch_lit:
    The torchlight reveals a carved stairway leading down.
    You descend with steady footing.
- else:
    You feel your way forward in the dark, one hand on the wall.
    Something crunches underfoot. Best not to look.
}
-> ending

=== ending ===
The passage opens into a wide chamber. Your adventure begins here.
-> END
