extends CharacterBody3D

func _physics_process(delta: float) -> void:
    var space_state := get_world_3d().direct_space_state
    var from := global_position
    var to := from + Vector3.DOWN * 2.0

    var query := PhysicsRayQueryParameters3D.create(from, to)
    query.exclude = [self]              # don't let our own body block the ray
    query.collide_with_areas = true     # Area3D is off by default

    var result := space_state.intersect_ray(query)
    if result:
        # Dictionary is EMPTY on a miss; on a hit it has these keys.
        print("Standing on: ", result.collider)
        print("Ground normal: ", result.normal)
