shader_type spatial;

uniform sampler2D albedo_texture : source_color;

void fragment() {
    ALBEDO = texture(albedo_texture, UV).rgb;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    float lit = step(0.0, NdotL);
    DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * ATTENUATION * lit;
}
