shader_type spatial;

uniform sampler2D albedo_texture : source_color;
uniform float threshold : hint_range(-1.0, 1.0) = 0.0;
uniform float softness : hint_range(0.0, 1.0) = 0.1;

void fragment() {
    ALBEDO = texture(albedo_texture, UV).rgb;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    // smoothstep(edge0, edge1, x) — 0 below edge0, 1 above edge1, smooth between
    float lit = smoothstep(threshold - softness, threshold + softness, NdotL);
    DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, ALBEDO * LIGHT_COLOR * ATTENUATION * lit);
}
