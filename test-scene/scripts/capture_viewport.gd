@tool
extends EditorScript

func _run() -> void:
	var base_dir := "res://.scratch/screenshots/"
	DirAccess.make_dir_recursive_absolute(base_dir)
	
	# Get the editor's 3D viewport
	var vp := EditorInterface.get_editor_viewport_3d(0)
	if not vp:
		printerr("Could not get 3D viewport")
		return
	
	var img := vp.get_texture().get_image()
	if not img:
		printerr("Could not get viewport image")
		return
	
	# Determine filename from command line or use default
	var fname := "editor_capture.png"
	var args := OS.get_cmdline_args()
	for a in args:
		if a.begins_with("--capture-name="):
			fname = a.trim_prefix("--capture-name=")
	
	var path := base_dir + fname
	var err := img.save_png(path)
	if err == OK:
		print("Screenshot saved: ", ProjectSettings.globalize_path(path))
	else:
		printerr("Failed to save: ", path, " error: ", err)
