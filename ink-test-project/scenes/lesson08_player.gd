# story_player.gd
# Production-patterns player for an ink story using the inkgd runtime.
# This is the SAME single-step drain loop from lessons 05-07 — the capstone adds
# no new engine API. What changes is the STORY's architecture, not the player:
#   * Hub-and-spoke  -- the loop naturally drives a re-enterable hub: drain lines,
#                       render choices, pick one, drain again. One loop, any number
#                       of topics, visited in any order.
#   * State-bus VARs -- the story reads/writes a few flags (asked_name, helped_cook)
#                       to carry cross-topic state. In a real multi-story game you'd
#                       read them out with get_variable and push them into the NEXT
#                       story's fresh InkPlayer with set_variable — that's the
#                       "stateless-per-dialog" pattern: durable state lives HERE, in
#                       the engine, not inside any one ink file.
#
# Node setup (attach this to a Control):
#   Control (this script)
#   +- SpeakerLabel     : Label          -- who is speaking
#   +- TextLabel        : RichTextLabel   -- story text (BBCode enabled)
#   +- ChoicesContainer : VBoxContainer   -- choice buttons appear here
extends Control

var InkPlayerFactory := preload("res://addons/inkgd/ink_player_factory.gd") as GDScript

var _ink_player = null

@onready var _speaker_label: Label = $SpeakerLabel
@onready var _text_label: RichTextLabel = $TextLabel
@onready var _choices_container: VBoxContainer = $ChoicesContainer


func _ready():
	_ink_player = InkPlayerFactory.create()
	_ink_player.loads_in_background = false
	add_child(_ink_player)

	_ink_player.ink_file = load("res://stories/08_production_patterns.ink.json")
	_ink_player.connect("loaded", Callable(self, "_on_story_loaded"))
	call_deferred("_create_story")


func _create_story():
	_ink_player.create_story()


func _on_story_loaded(successfully: bool):
	if not successfully:
		_text_label.text = "[color=red]ERROR: Story failed to load.[/color]"
		return
	_advance_story()


# Phase 1 of the hub loop: drain every available line (single-step, so per-line
# tags survive — the lesson 06 rule). Phase 2 (render choices) happens when the
# drain stops at a choice point.
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


# Read a state-bus flag out of the story — this is how a real game would harvest
# ink's variables to persist them (get_variable) and later push them into the next
# dialog's fresh InkPlayer (set_variable). Shown here for the harness/demo.
func read_flag(name: String):
	return _ink_player.get_variable(name)


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
