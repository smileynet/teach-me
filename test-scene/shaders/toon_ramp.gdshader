shader_type spatial;

uniform sampler2D albedo_texture : source_color;
uniform sampler2D diffuse_ramp : hint_default_white;

void fragment() {
    ALBEDO = texture(albedo_texture, UV).rgb;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);

    // Remap NdotL from [-1,1] to [0,1] for texture lookup
    float ramp_uv = NdotL * 0.5 + 0.5;

    // Sample the ramp — the texture IS the lighting
    float lit = texture(diffuse_ramp, vec2(ramp_uv, 0.0)).r;

    DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, ALBEDO * LIGHT_COLOR * ATTENUATION * lit);
}
