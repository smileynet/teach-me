extends CharacterBody3D

@export var speed: float = 5.0
@export var gravity: float = 9.8

func _physics_process(delta: float) -> void:
    # Gravity is an acceleration, so it IS multiplied by delta.
    if not is_on_floor():
        velocity.y -= gravity * delta

    var input := Input.get_vector("left", "right", "forward", "back")
    velocity.x = input.x * speed
    velocity.z = input.y * speed

    # move_and_slide() already accounts for the timestep —
    # do NOT multiply velocity by delta here.
    move_and_slide()
