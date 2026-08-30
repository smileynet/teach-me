shader_type spatial;
render_mode unshaded, cull_front, depth_draw_opaque;

// === Outline Controls ===
uniform vec4 outline_color : source_color = vec4(0.008, 0.055, 0.086, 1.0);
uniform float outline_width : hint_range(0.0, 3.0) = 0.5;
uniform float outline_scale : hint_range(0.0, 4.0) = 1.0;
uniform float outline_clip_offset : hint_range(0.0, 1.0) = 0.0;

// Normalizing constant: converts artist-friendly width values to vertex offsets
const float TARGET_WIDTH_SCALE = 0.006;

void vertex() {
	// Compute effective width (scale multiplies, clip_offset removes thin outlines)
	float width = max(outline_width * outline_scale * TARGET_WIDTH_SCALE - outline_clip_offset * TARGET_WIDTH_SCALE, 0.0);
	VERTEX += NORMAL * width;
}

void fragment() {
	ALBEDO = outline_color.rgb;
	ALPHA = outline_color.a;
}
