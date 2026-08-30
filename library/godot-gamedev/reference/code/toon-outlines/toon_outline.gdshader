shader_type spatial;
render_mode cull_front, unshaded;

uniform float outline_width : hint_range(0.0, 0.1) = 0.02;
uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);

void vertex() {
    vec4 clip_pos = MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
    vec3 view_normal = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
    clip_pos.xyz += view_normal * outline_width * -clip_pos.z;
    POSITION = PROJECTION_MATRIX * clip_pos;
}

void fragment() {
    ALBEDO = outline_color.rgb;
}
