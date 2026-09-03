# Physics & Collision Systems — Code Files

Final-state files from lesson 0015.

- `player.gd` — a `CharacterBody3D` movement controller driven with `move_and_slide()`.
  Demonstrates the correct delta handling: gravity is scaled by `delta` (it's an
  acceleration) while `velocity` is NOT (`move_and_slide()` already includes the timestep).
- `ground_probe.gd` — a physics-space raycast (`intersect_ray`) that detects the ground
  beneath the body. Shows `exclude = [self]`, `collide_with_areas`, and reading the result
  dictionary's `collider`/`normal`.

Both belong in `_physics_process()`. Attach to a `CharacterBody3D` with a `CollisionShape3D`.
