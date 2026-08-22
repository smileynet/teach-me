shader_type canvas_item;

uniform int kernel_size : hint_range(1, 10) = 3;
uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;

void fragment() {
    vec2 pixel = 1.0 / vec2(textureSize(SCREEN_TEXTURE, 0));
    int radius = kernel_size;

    // Sample four quadrants around the pixel
    // For each: compute mean color and variance
    vec3 means[4];
    float variances[4];

    // Quadrant offsets: top-left, top-right, bottom-left, bottom-right
    ivec2 offsets[4] = ivec2[](
        ivec2(-1, -1), ivec2(1, -1),
        ivec2(-1, 1), ivec2(1, 1)
    );

    for (int q = 0; q < 4; q++) {
        vec3 sum = vec3(0.0);
        vec3 sum_sq = vec3(0.0);
        float count = 0.0;

        for (int x = 0; x <= radius; x++) {
            for (int y = 0; y <= radius; y++) {
                vec2 offset = vec2(
                    float(x * offsets[q].x),
                    float(y * offsets[q].y)
                ) * pixel;

                vec3 sample_color = texture(SCREEN_TEXTURE, SCREEN_UV + offset).rgb;
                sum += sample_color;
                sum_sq += sample_color * sample_color;
                count += 1.0;
            }
        }

        means[q] = sum / count;
        vec3 variance = (sum_sq / count) - (means[q] * means[q]);
        variances[q] = variance.r + variance.g + variance.b;
    }

    // Output the mean of the quadrant with lowest variance
    // (flattest region = most paint-like)
    int min_idx = 0;
    float min_var = variances[0];
    for (int q = 1; q < 4; q++) {
        if (variances[q] < min_var) {
            min_var = variances[q];
            min_idx = q;
        }
    }

    COLOR.rgb = means[min_idx];
    COLOR.a = 1.0;
}
