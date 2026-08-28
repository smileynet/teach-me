# story_player.gd
# First Godot integration for an ink story using the inkgd GDScript runtime.
# Loads a compiled .ink.json, displays text, renders choices as buttons, and
# reads a story variable when the story ends.
#
# Node setup (attach this to a Control):
#   Control (this script)
#   +- TextLabel        : RichTextLabel   -- story text (BBCode enabled)
#   +- ChoicesContainer : VBoxContainer   -- choice buttons appear here
extends Control

var InkPlayerFactory := preload("res://addons/inkgd/ink_player_factory.gd") as GDScript

var _ink_player = null

@onready var _text_label: RichTextLabel = $TextLabel
@onready var _choices_container: VBoxContainer = $ChoicesContainer


func _ready():
	# 1. Create the player and put it in the tree (InkPlayer is a Node).
	_ink_player = InkPlayerFactory.create()
	_ink_player.loads_in_background = false
	add_child(_ink_player)

	# 2. Assign the COMPILED story (.ink.json, not the raw .ink source).
	_ink_player.ink_file = load("res://stories/05_first_godot_integration.ink.json")

	# 3. Wait for the story to finish building before touching it.
	_ink_player.connect("loaded", Callable(self, "_on_story_loaded"))

	# 4. Defer create_story() so the __InkRuntime autoload is ready this frame.
	call_deferred("_create_story")


func _create_story():
	_ink_player.create_story()


# Only interact with the story once it has loaded successfully.
func _on_story_loaded(successfully: bool):
	if not successfully:
		_text_label.text = "[color=red]ERROR: Story failed to load.[/color]"
		return
	_advance_story()


# Step ONE line at a time, accumulating each line's text. Through inkgd's
# InkPlayer, continue_story_maximally() returns only the LAST line (it discards
# the story's concatenated text), so a single-step loop is how you show a whole
# passage — read each line's return value and append it.
func _advance_story():
	while _ink_player.can_continue:
		var text = _ink_player.continue_story()
		if text != "":
			_text_label.text += text + "\n"

	if _ink_player.has_choices:
		_show_choices()
	elif not _ink_player.can_continue:
		_on_ended()


# Render one button per available choice.
func _show_choices():
	for child in _choices_container.get_children():
		child.queue_free()

	var choices = _ink_player.current_choices
	for i in range(choices.size()):
		var btn = Button.new()
		btn.text = choices[i].text          # each choice is an object; use .text
		btn.connect("pressed", Callable(self, "_on_choice_selected").bind(i))
		_choices_container.add_child(btn)


func _on_choice_selected(index: int):
	for child in _choices_container.get_children():
		child.queue_free()

	_ink_player.choose_choice_index(index)  # tell the runtime which choice
	_advance_story()                         # then continue


# The story ended -- read a variable to prove GDScript shares ink's state.
func _on_ended():
	var torch_lit = _ink_player.get_variable("torch_lit")
	_text_label.text += "\n[color=gray]torch_lit = %s[/color]" % str(torch_lit)
