## Spike: proves inkgd works in Godot 4.7.1 with standard (non-.NET) build.
## Loads hello.ink.json, continues text, handles choices, reads variables.
extends Control

var InkPlayerFactory := preload("res://addons/inkgd/ink_player_factory.gd") as GDScript

var _ink_player = null

@onready var _text_label: RichTextLabel = $MarginContainer/VBoxContainer/TextLabel
@onready var _choices_container: VBoxContainer = $MarginContainer/VBoxContainer/ChoicesContainer
@onready var _continue_button: Button = $MarginContainer/VBoxContainer/ContinueButton

func _ready():
	_ink_player = InkPlayerFactory.create()
	_ink_player.loads_in_background = false
	add_child(_ink_player)

	_ink_player.ink_file = load("res://stories/hello.ink.json")

	_ink_player.connect("loaded", Callable(self, "_on_story_loaded"))

	_continue_button.connect("pressed", Callable(self, "_on_continue_pressed"))
	_continue_button.hide()

	# Defer to next frame so the autoload __InkRuntime is fully ready
	call_deferred("_create_story")

func _create_story():
	_ink_player.create_story()

func _on_story_loaded(successfully: bool):
	if not successfully:
		_text_label.text = "[color=red]ERROR: Story failed to load.[/color]"
		return
	print("[SPIKE] Story loaded successfully!")
	_advance_story()

func _advance_story():
	# Step one line at a time, accumulating text. InkPlayer.continue_story_maximally()
	# returns only the LAST line, so loop with continue_story() to show a whole passage.
	while _ink_player.can_continue:
		var text = _ink_player.continue_story()
		if text != "":
			_text_label.text += text

	# Check for choices
	if _ink_player.has_choices:
		_show_choices()
	elif not _ink_player.can_continue:
		_on_ended()

func _show_choices():
	# Clear any existing choice buttons
	for child in _choices_container.get_children():
		child.queue_free()

	var choices = _ink_player.current_choices
	print("[SPIKE] Showing %d choices" % choices.size())
	for i in range(choices.size()):
		var btn = Button.new()
		btn.text = choices[i].text
		btn.connect("pressed", Callable(self, "_on_choice_selected").bind(i))
		_choices_container.add_child(btn)

func _on_choice_selected(index: int):
	print("[SPIKE] Choice selected: %d" % index)
	# Clear choice buttons
	for child in _choices_container.get_children():
		child.queue_free()

	_ink_player.choose_choice_index(index)
	_advance_story()

func _on_ended():
	var player_name = _ink_player.get_variable("player_name")
	_text_label.text += "\n[color=green]--- STORY ENDED ---[/color]"
	_text_label.text += "\n[color=gray]Variable 'player_name' = %s[/color]" % str(player_name)
	print("[SPIKE] Story ended. player_name = %s" % str(player_name))
	print("[SPIKE] SUCCESS: inkgd works in Godot 4.7.1!")

func _on_continue_pressed():
	_advance_story()
