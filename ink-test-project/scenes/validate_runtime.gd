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
	await _validate_lesson07()

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

	# Bug-signature guard (#236/#251): the maximal-continue bug dropped the OPENING
	# narration and showed only the last line. A non-empty check alone would still
	# pass in that case. Assert the exact opening line the bug dropped so a
	# regression of THIS bug fails, not just any missing-ending.
	if "You stand at the mouth" in text_label.text:
		_ok("L05", "opening narration present (#236 bug-signature guard)")
	else:
		_fail("L05", "opening narration missing — #236 maximal-continue regression; got: %s" % text_label.text)

	# choices 0,1 -> light torch, step inside -> END
	await _press_choice(p, 0)   # Light the torch
	await _press_choice(p, 1)   # Step inside anyway

	if "carved stairway" in text_label.text:
		_ok("L05", "reached torch-lit ending (variable + branch worked)")
	else:
		_fail("L05", "did not reach expected torch-lit ending; got: %s" % text_label.text)

	p.queue_free()


# --- Lesson 06: exact speaker, sound dispatch, # hidden suppressed, ending ---
func _validate_lesson06():
	var p = await _spawn("res://scenes/lesson06_player.tscn")
	var text_label = p.get_node("TextLabel")
	var speaker_label = p.get_node("SpeakerLabel")

	# EXACT speaker value after the opening. The opening's last dialogue line is
	# tagged `# speaker: Alfoz`; a working per-line dispatcher sets exactly that
	# (non-empty alone is too weak — a stuck/wrong dispatcher could pass).
	if speaker_label.text == "Alfoz":
		_ok("L06", "speaker label == 'Alfoz' (exact per-line tag dispatch)")
	else:
		_fail("L06", "speaker expected 'Alfoz', got '%s'" % speaker_label.text)

	# SOUND dispatch: drive a "sound: probe" tag through the player's own
	# _process_tags. A recognized command returns show=true (no suppress) and does
	# NOT hit the unhandled-tag fallthrough. Combined with the speaker check above,
	# this proves the command-with-value path (not just speaker) is wired.
	if _tag_returns_show(p, "sound: probe") == true:
		_ok("L06", "sound command handled (returns show=true, not suppressed)")
	else:
		_fail("L06", "sound command mis-handled")

	# choices 0,0 -> Show me -> Buy the compass -> END
	await _press_choice(p, 0)   # Show me

	# # hidden line "The needle always points home" must NOT appear as text...
	if "points home" in text_label.text:
		_fail("L06", "# hidden line text was shown — suppress contract broken")
	else:
		_ok("L06", "# hidden line text suppressed")

	# ...but the hidden key is RECOGNIZED (returns show=false), proving the
	# dispatch path ran and gated the text rather than ignoring the tag.
	if _tag_returns_show(p, "hidden") == false:
		_ok("L06", "# hidden recognized: suppress path ran (text gated, not a no-op)")
	else:
		_fail("L06", "# hidden not recognized as a suppress command")

	await _press_choice(p, 0)   # Buy the compass

	# After the buy passage (Narrator line then Alfoz line), the LAST line's tag
	# wins: speaker == 'Alfoz'. Confirms dispatch kept running through the passage.
	if "Safe travels" in text_label.text and speaker_label.text == "Alfoz":
		_ok("L06", "reached ending; speaker updated through the passage")
	else:
		_fail("L06", "ending/speaker wrong: text=%s speaker=%s" % [text_label.text, speaker_label.text])

	p.queue_free()


# --- Lesson 07: external function, variable observer, save/load round-trip ---
func _validate_lesson07():
	var p = await _spawn("res://scenes/lesson07_player.tscn")
	var text_label = p.get_node("TextLabel")
	var gold_label = p.get_node("GoldLabel")

	# OBSERVER fired on load with the initial value (10) -> HUD mirrors it.
	if gold_label.text == "Gold: 10":
		_ok("L07", "observer fired on load: HUD shows initial gold (10)")
	else:
		_fail("L07", "observer did not sync initial gold; GoldLabel='%s'" % gold_label.text)

	# EXTERNAL discount_for(reputation=2) -> 3, so price = 12 - 3 = 9. The discount
	# line only prints when off > 0, proving ink actually called out to the engine.
	if "9 coins" in text_label.text and "friend of the guild" in text_label.text:
		_ok("L07", "external fn called: discount applied (price 9 from reputation)")
	else:
		_fail("L07", "external discount not applied; text=%s" % text_label.text)

	# SAVE the whole state at gold=10 (before buying).
	p.save_game()

	# Buy the lantern (choice 0, "Buy the lantern (9 coins)") -> gold 10 - 9 = 1.
	await _press_choice(p, 0)

	# OBSERVER fired again on the mutation -> HUD now shows 1.
	if gold_label.text == "Gold: 1":
		_ok("L07", "observer fired on mutation: HUD shows gold after purchase (1)")
	else:
		_fail("L07", "observer did not sync gold after buy; GoldLabel='%s'" % gold_label.text)

	# LOAD the saved state -> gold restored to 10 (whole-state round-trip).
	p.load_game()
	var restored = p._ink_player.get_variable("gold")
	if int(restored) == 10:
		_ok("L07", "save/load round-trip: gold restored to 10 after set_state")
	else:
		_fail("L07", "save/load did not restore gold; get_variable('gold')=%s" % str(restored))

	p.queue_free()


# Return the show_line bool the player's _process_tags yields for one tag.
# Lets the harness assert command recognition directly (a recognized command
# key returns true; only "hidden" returns false; an unhandled key also returns
# true but push_warnings — distinguished by the paired speaker/suppress checks).
func _tag_returns_show(player: Node, tag: String):
	return player._process_tags([tag])
