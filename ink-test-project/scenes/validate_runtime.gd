# validate_runtime.gd
# Headless inkgd-runtime validation harness (#235).
#
# Run: godot --headless res://scenes/validate_runtime.tscn --path ink-test-project
#
# Instantiates each lesson's SHIPPED story_player scene (running the real script),
# drives it through a fixed choice sequence by pressing the generated choice
# buttons, and asserts on the resulting node state. This is the inkgd-RUNTIME
# gate: it proves the lesson's InkPlayer integration code actually runs in Godot,
# which bink (ink:play / ink:transcripts) cannot test — bink covers story logic.
#
# Exit 0 = all checks pass, 1 = one or more failed.
extends Node

var _failures := 0


func _ready():
	# The players load asynchronously (create_story -> deferred -> loaded).
	# Awaiting process frames lets that settle before we interact.
	await _validate_lesson05()
	await _validate_lesson06()

	if _failures > 0:
		printerr("=== FAIL: %d check(s) failed ===" % _failures)
		get_tree().quit(1)
	else:
		print("=== PASS: all inkgd-runtime checks passed ===")
		get_tree().quit(0)


func _fail(id: String, msg: String):
	printerr("[%s] ERROR: %s" % [id, msg])
	_failures += 1


func _ok(id: String, msg: String):
	print("[%s] Confirmed: %s" % [id, msg])


# Add a player scene, wait for its async load + first advance to settle.
func _spawn(scene_path: String) -> Node:
	var scene = load(scene_path) as PackedScene
	var player = scene.instantiate()
	add_child(player)
	# Two call_deferred hops (player + inkgd) then the loaded handler advances;
	# pump several process frames to be safe.
	for _i in range(5):
		await get_tree().process_frame
	return player


# Press the choice button at `index` in the player's ChoicesContainer,
# then let the resulting advance settle.
func _press_choice(player: Node, index: int) -> void:
	var container = player.get_node("ChoicesContainer")
	var buttons = container.get_children()
	if index >= buttons.size():
		return
	buttons[index].emit_signal("pressed")
	for _i in range(3):
		await get_tree().process_frame


# --- Lesson 05: text accumulates, story reaches END ---
func _validate_lesson05():
	var p = await _spawn("res://scenes/lesson05_player.tscn")
	var text_label = p.get_node("TextLabel")

	if text_label.text.strip_edges() == "":
		_fail("L05", "no text after load — loaded signal / advance did not run")
	else:
		_ok("L05", "text displayed after load")

	# choices 0,1 -> light torch, step inside -> END
	await _press_choice(p, 0)   # Light the torch
	await _press_choice(p, 1)   # Step inside anyway

	if "carved stairway" in text_label.text:
		_ok("L05", "reached torch-lit ending (variable + branch worked)")
	else:
		_fail("L05", "did not reach expected torch-lit ending; got: %s" % text_label.text)

	p.queue_free()


# --- Lesson 06: speaker set, # hidden suppressed, mid-story tag observed ---
func _validate_lesson06():
	var p = await _spawn("res://scenes/lesson06_player.tscn")
	var text_label = p.get_node("TextLabel")
	var speaker_label = p.get_node("SpeakerLabel")

	# The opening lines carry # speaker: tags. If per-line tag dispatch works,
	# the speaker label is set (proves single-step continue preserved per-line tags).
	if speaker_label.text.strip_edges() == "":
		_fail("L06", "speaker label empty — per-line tags not dispatched (maximal-continue bug?)")
	else:
		_ok("L06", "speaker label set from tag: '%s'" % speaker_label.text)

	# choices 0,0 -> Show me -> Buy the compass -> END
	await _press_choice(p, 0)   # Show me
	# The wares knot contains a "# hidden" line: "The needle always points home".
	# Its text must NOT appear (engine suppresses it) though its tag still ran.
	if "points home" in text_label.text:
		_fail("L06", "# hidden line text was shown — suppress contract broken")
	else:
		_ok("L06", "# hidden line text suppressed")

	await _press_choice(p, 0)   # Buy the compass

	if "Safe travels" in text_label.text:
		_ok("L06", "reached ending after tagged dialogue")
	else:
		_fail("L06", "did not reach expected ending; got: %s" % text_label.text)

	p.queue_free()
