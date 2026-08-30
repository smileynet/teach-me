# story_player.gd
# State-bridge integration for an ink story using the inkgd runtime.
# Extends Lesson 06's single-step loop with the three ink<->engine bridges:
#   1. External function  — ink calls OUT to game logic (discount_for)
#   2. Variable observer  — the game reacts TO an ink VAR change (gold -> HUD)
#   3. Save / load         — persist and restore the whole story state
#
# Node setup (attach this to a Control):
#   Control (this script)
#   +- SpeakerLabel     : Label          -- who is speaking
#   +- TextLabel        : RichTextLabel   -- story text (BBCode enabled)
#   +- GoldLabel        : Label           -- HUD mirror of the ink `gold` VAR
#   +- ChoicesContainer : VBoxContainer   -- choice buttons appear here
extends Control

var InkPlayerFactory := preload("res://addons/inkgd/ink_player_factory.gd") as GDScript

var _ink_player = null
var _saved_state := ""   # a snapshot for the save/load demo

@onready var _speaker_label: Label = $SpeakerLabel
@onready var _text_label: RichTextLabel = $TextLabel
@onready var _gold_label: Label = $GoldLabel
@onready var _choices_container: VBoxContainer = $ChoicesContainer


func _ready():
	_ink_player = InkPlayerFactory.create()
	_ink_player.loads_in_background = false
	add_child(_ink_player)

	_ink_player.ink_file = load("res://stories/07_state_bridge.ink.json")
	_ink_player.connect("loaded", Callable(self, "_on_story_loaded"))
	call_deferred("_create_story")


func _create_story():
	_ink_player.create_story()


func _on_story_loaded(successfully: bool):
	if not successfully:
		_text_label.text = "[color=red]ERROR: Story failed to load.[/color]"
		return

	# BRIDGE 1 — External function. The story declared `EXTERNAL discount_for(rep)`;
	# we bind it AFTER create_story() and BEFORE the first continue. It's pure (no
	# side effects), so lookahead_safe = true: ink may call it while previewing
	# choices, and that's harmless here. A function that PLAYED A SOUND or SPENT
	# GOLD would need lookahead_safe = false, or it would fire during preview.
	_ink_player.bind_external_function("discount_for", self, "_discount_for", true)

	# BRIDGE 2 — Variable observer. The engine reacts to `gold` changing inside
	# ink (push, not poll) — but the observer only fires on a CHANGE, not on
	# registration. So seed the HUD once from the current value, then let the
	# observer keep it in sync from here on.
	_ink_player.observe_variable("gold", self, "_on_gold_changed")
	_on_gold_changed("gold", _ink_player.get_variable("gold"))

	_advance_story()


# BRIDGE 1 target: given the player's reputation, return a coin discount.
# This is GAME logic the writer doesn't have to hardcode in ink.
func _discount_for(rep: int) -> int:
	return 3 if rep >= 2 else 0


# BRIDGE 2 target: (variable_name, new_value). Mirror gold onto the HUD.
func _on_gold_changed(_variable_name: String, new_value) -> void:
	_gold_label.text = "Gold: %d" % int(new_value)


# Step ONE line at a time (Lesson 05/06 loop). Ink's line text already ends in a
# newline, so append it as-is (adding "\n" here double-spaces output).
func _advance_story():
	while _ink_player.can_continue:
		var text = _ink_player.continue_story()
		var show_line = _process_tags(_ink_player.current_tags)
		if show_line and text.strip_edges() != "":
			_text_label.text += text

	if _ink_player.has_choices:
		_show_choices()


func _process_tags(tags: Array) -> bool:
	var show_line := true
	for tag in tags:
		var parts = (tag as String).split(":", false, 1)
		var key = parts[0].strip_edges()
		var value = parts[1].strip_edges() if parts.size() > 1 else ""
		match key:
			"speaker":
				_speaker_label.text = value
			"hidden":
				show_line = false
			_:
				pass
	return show_line


# BRIDGE 3 — Save / load. get_state() returns the WHOLE story state as one JSON
# string (variables, visit counts, callstack, RNG seed). Never hand-save vars one
# by one — you'd drop the current knot and read counts. set_state() restores it.
func save_game() -> void:
	_saved_state = _ink_player.get_state()


func load_game() -> void:
	if _saved_state != "":
		_ink_player.set_state(_saved_state)


func _show_choices():
	for child in _choices_container.get_children():
		child.queue_free()

	var choices = _ink_player.current_choices
	for i in range(choices.size()):
		var btn = Button.new()
		btn.text = choices[i].text
		btn.connect("pressed", Callable(self, "_on_choice_selected").bind(i))
		_choices_container.add_child(btn)


func _on_choice_selected(index: int):
	for child in _choices_container.get_children():
		child.queue_free()
	_ink_player.choose_choice_index(index)
	_advance_story()
