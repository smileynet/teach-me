extends Node3D

func _ready() -> void:
	# Wait a frame for everything to render
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	
	var dir_path := "user://screenshots/"
	DirAccess.make_dir_recursive_absolute(dir_path)
	
	# Capture WITH shader (PostProcess is visible by default)
	await get_tree().process_frame
	_capture("with_shader")
	
	# Toggle shader OFF
	var post_rect := get_node("PostProcess/PostProcessRect")
	post_rect.visible = false
	await get_tree().process_frame
	await get_tree().process_frame
	
	# Capture WITHOUT shader
	_capture("without_shader")
	
	print("Screenshots saved to: ", ProjectSettings.globalize_path(dir_path))
	# Don't quit - let user review


func _capture(suffix: String) -> void:
	var img := get_viewport().get_texture().get_image()
	var path := "user://screenshots/color_test_%s.png" % suffix
	img.save_png(path)
	print("Saved: ", ProjectSettings.globalize_path(path))
