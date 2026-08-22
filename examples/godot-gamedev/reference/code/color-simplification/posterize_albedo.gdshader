shader_type spatial;
render_mode diffuse_toon;

uniform sampler2D albedo_texture : source_color;
uniform int color_levels : hint_range(2, 16) = 4;
uniform int shadow_bands : hint_range(2, 8) = 3;

void fragment() {
    vec3 tex_color = texture(albedo_texture, UV).rgb;

    // Posterize the albedo — reduce to N levels per channel
    float n = float(color_levels);
    ALBEDO = floor(tex_color * n) / n;
}

void light() {
    // Toon banding on the already-posterized color
    float NdotL = dot(NORMAL, LIGHT) * 0.5 + 0.5;
    float bands = floor(NdotL * float(shadow_bands)) / float(shadow_bands);
    DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * ATTENUATION * bands;
}
