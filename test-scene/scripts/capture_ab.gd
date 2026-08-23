@tool
extends EditorScript

func _run() -> void:
	var viewport := EditorInterface.get_editor_viewport_3d(0)
	var img := viewport.get_texture().get_image()
	var dir := "res://.scratch/screenshots/"
	DirAccess.make_dir_recursive_absolute(dir)
	img.save_png(dir + "current_view.png")
	print("Saved screenshot to ", dir + "current_view.png")
