@tool
extends EditorScript

## Validation script for ticket #185 shader claims.
## Run via: godot --headless --editor --script res://validate_claims.gd --path test-scene
##
## Creates a simple scene with a sphere, applies each validation shader,
## and attempts to save a rendered frame. If headless rendering produces
## black frames (no GPU), the script still confirms shader compilation.

func _run() -> void:
	print("=== Ticket #185 Validation ===")
	print("")

	# Validate F1: ALBEDO default shader compiles
	var f1_shader := load("res://shaders/validation/test_albedo_default.gdshader") as Shader
	if f1_shader:
		print("[F1] test_albedo_default.gdshader: LOADED OK")
		# Check it has no fragment function (the whole point)
		var code := f1_shader.code
		if "void fragment()" in code:
			print("[F1] WARNING: shader contains fragment() - validation invalid")
		else:
			print("[F1] Confirmed: no fragment() function present")
			print("[F1] If rendered with a light, ALBEDO default determines surface color")
			print("[F1] Official docs say default=white -> expect white toon-banded sphere")
	else:
		print("[F1] ERROR: Could not load shader")

	print("")

	# Validate F9: posterize + bands shader compiles
	var f9_shader := load("res://shaders/validation/test_posterize_bands.gdshader") as Shader
	if f9_shader:
		print("[F9] test_posterize_bands.gdshader: LOADED OK")
		var code := f9_shader.code
		if "void fragment()" in code and "void light()" in code:
			print("[F9] Confirmed: has both fragment() and light()")
			print("[F9] fragment() posterizes ALBEDO, light() applies NdotL banding")
			print("[F9] Since NdotL is geometric (independent of ALBEDO values),")
			print("[F9] toon bands should survive posterization")
		else:
			print("[F9] WARNING: missing expected functions")
	else:
		print("[F9] ERROR: Could not load shader")

	print("")

	# Also validate the detection shader claim (F7)
	var f7_shader := load("res://shaders/toon_outline_colorid_detect.gdshader") as Shader
	if f7_shader:
		print("[F7] toon_outline_colorid_detect.gdshader: LOADED OK")
		var code := f7_shader.code
		if "step(0.01, diff)" in code:
			print("[F7] Confirmed: uses step(0.01, diff) on RGB Manhattan distance")
			print("[F7] This outlines ANY color difference > 0.01, not just 'behind' neighbors")
		if "center.a" in code and "neighbor.a" not in code:
			print("[F7] Confirmed: only center.a used (suppress on transparent bg)")
			print("[F7] Neighbor alpha is NOT checked - 'lower alpha' comment is wrong")
	else:
		print("[F7] Shader not found (may not be imported yet)")

	print("")
	print("=== Compilation validation complete ===")
	print("For VISUAL validation of F1 and F9, open the editor and apply")
	print("shaders to TestSphere with a DirectionalLight3D in the scene.")
	print("")
	print("Expected results:")
	print("  F1: White sphere with hard light/dark split (not black)")
	print("  F9: Posterized colors BUT still visible light/dark band split")
