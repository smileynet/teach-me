shader_type canvas_item;

// Artist-defined palette (set in Inspector — up to 16 colors)
uniform vec4 palette[16] : source_color;
uniform int palette_size : hint_range(2, 16) = 8;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;

// Convert linear RGB to Oklab (perceptually uniform color space)
vec3 rgb_to_oklab(vec3 rgb) {
    float l = 0.4122 * rgb.r + 0.5363 * rgb.g + 0.0514 * rgb.b;
    float m = 0.2119 * rgb.r + 0.6807 * rgb.g + 0.1074 * rgb.b;
    float s = 0.0883 * rgb.r + 0.2817 * rgb.g + 0.6300 * rgb.b;

    l = pow(l, 1.0 / 3.0);
    m = pow(m, 1.0 / 3.0);
    s = pow(s, 1.0 / 3.0);

    return vec3(
        0.2105 * l + 0.7936 * m - 0.0041 * s,
        1.9780 * l - 2.4286 * m + 0.4506 * s,
        0.0259 * l + 0.7828 * m - 0.8087 * s
    );
}

void fragment() {
    vec3 color = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    vec3 lab = rgb_to_oklab(color);

    // Find the perceptually nearest palette color
    float min_dist = 1e10;
    vec3 nearest = palette[0].rgb;

    for (int i = 0; i < palette_size; i++) {
        vec3 palette_lab = rgb_to_oklab(palette[i].rgb);
        float dist = distance(lab, palette_lab);
        if (dist < min_dist) {
            min_dist = dist;
            nearest = palette[i].rgb;
        }
    }

    COLOR.rgb = nearest;
    COLOR.a = 1.0;
}
