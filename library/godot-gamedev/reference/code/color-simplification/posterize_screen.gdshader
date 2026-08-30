shader_type canvas_item;

uniform int color_levels : hint_range(2, 32) = 6;
uniform bool enable_dithering = true;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;

// 4×4 Bayer dithering matrix (reduces visible banding)
float bayer4x4(vec2 pos) {
    int x = int(mod(pos.x, 4.0));
    int y = int(mod(pos.y, 4.0));
    float matrix[16] = float[](
        0.0, 8.0, 2.0, 10.0,
        12.0, 4.0, 14.0, 6.0,
        3.0, 11.0, 1.0, 9.0,
        15.0, 7.0, 13.0, 5.0
    );
    return matrix[x + y * 4] / 16.0;
}

void fragment() {
    vec3 color = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    float n = float(color_levels);

    // Optional: ordered dithering smooths the banding transitions
    if (enable_dithering) {
        color += bayer4x4(FRAGCOORD.xy) / n;
    }

    COLOR.rgb = floor(color * n) / n;
    COLOR.a = 1.0;
}
