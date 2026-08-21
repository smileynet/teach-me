shader_type spatial;

uniform sampler2D albedo_texture : source_color;
uniform int bands : hint_range(1, 8) = 3;
uniform float wrap : hint_range(-1.0, 1.0) = 0.0;
uniform float steepness : hint_range(0.5, 4.0) = 1.0;

void fragment() {
    ALBEDO = texture(albedo_texture, UV).rgb;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);

    // Combine lighting factors
    float diffuse_amount = NdotL + (ATTENUATION - 1.0) + wrap;
    diffuse_amount *= steepness;

    // THE MODULO TRICK — snaps to nearest band
    float cuts_inv = 1.0 / float(bands);
    float stepped = clamp(
        diffuse_amount + mod(1.0 - diffuse_amount, cuts_inv),
        0.0, 1.0
    );

    DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, ALBEDO * LIGHT_COLOR * stepped);
}
