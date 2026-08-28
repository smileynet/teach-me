# story_player.gd
# Tags-as-commands integration for an ink story using the inkgd runtime.
# Extends Lesson 05: instead of one maximal continue, it steps line-by-line so
# each line's tags are available, then dispatches those tags to game systems.
#
# Tag protocol (a contract between the writer and this parser):
#   # speaker: NAME  -> set the name label
#   # sound: NAME    -> play a sound effect
#   # hidden         -> run side effects but do NOT show this line's text
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

	_ink_player.ink_file = load("res://stories/06_tags_as_commands.ink.json")
	_ink_player.connect("loaded", Callable(self, "_on_story_loaded"))
	call_deferred("_create_story")


func _create_story():
	_ink_player.create_story()


func _on_story_loaded(successfully: bool):
	if not successfully:
		_text_label.text = "[color=red]ERROR: Story failed to load.[/color]"
		return
	_advance_story()


# Step ONE line at a time. continue_story_maximally() would collapse several
# lines into one and leave current_tags reflecting only the last line — we would
# lose the per-line tags. A single-step loop keeps each line's tags intact.
func _advance_story():
	while _ink_player.can_continue:
		var text = _ink_player.continue_story()

		# Read THIS line's tags and dispatch them. The return value decides
		# whether the line's text is shown; side effects run either way.
		var show_line = _process_tags(_ink_player.current_tags)

		if show_line and text.strip_edges() != "":
			_text_label.text += text

	if _ink_player.has_choices:
		_show_choices()


# Parse "key: value" tags and route each to a game system.
# Returns false if a tag says this line's text should be hidden.
func _process_tags(tags: Array) -> bool:
	var show_line := true

	for tag in tags:
		var parts = (tag as String).split(":", false, 1)
		var key = parts[0].strip_edges()
		var value = parts[1].strip_edges() if parts.size() > 1 else ""

		match key:
			"speaker":
				_speaker_label.text = value
			"sound":
				_play_sound(value)      # your audio system
			"hidden":
				show_line = false
			_:
				push_warning("Unhandled tag: %s" % tag)   # no handler — a no-op

	return show_line


func _play_sound(sound_name: String):
	# Stub: a real project would look up and play an AudioStream here.
	print("[sound] %s" % sound_name)


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
