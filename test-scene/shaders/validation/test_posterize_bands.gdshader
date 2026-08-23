shader_type spatial;

// VALIDATION: Does posterizing albedo in fragment() kill toon banding in light()?
//
// If banding survives (expected):
//   → Sphere shows visible light/dark split even with posterized colors
//   → NdotL is geometric, independent of ALBEDO values
//
// If banding disappears:
//   → The exercise answer in 0008 was correct
//
// This validates F9 in ticket #185.
// Apply to a textured mesh (assign albedo_texture in material).

uniform sampler2D albedo_texture : source_color;
uniform float levels : hint_range(2.0, 16.0, 1.0) = 4.0;

void fragment() {
    vec3 col = texture(albedo_texture, UV).rgb;
    // Posterize to N levels per channel
    col = floor(col * levels) / levels;
    ALBEDO = col;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    float band = step(0.0, NdotL);
    DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * ATTENUATION * band;
}
