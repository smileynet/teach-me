shader_type spatial;
render_mode unshaded, cull_front, depth_draw_opaque;

uniform vec4 outline_color : source_color = vec4(0.0078, 0.0549, 0.0863, 1.0);
uniform float outline_width : hint_range(0.0, 3.0) = 0.5;
uniform float outline_scale : hint_range(0.0, 4.0) = 1.0;
uniform float outline_clip_offset : hint_range(0.0, 1.0) = 0.0;
uniform float target_width_scale = 0.006;

void vertex() {
	float outline_amount = max(outline_width * outline_scale * target_width_scale - outline_clip_offset, 0.0);
	VERTEX += NORMAL * outline_amount;
}

void fragment() {
	ALBEDO = outline_color.rgb;
	ALPHA = outline_color.a;
}
