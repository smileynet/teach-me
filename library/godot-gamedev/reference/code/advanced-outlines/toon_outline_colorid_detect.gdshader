shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width : hint_range(0.5, 8.0) = 1.0;

const vec2 DIRECTIONS[8] = {
    vec2(1.0, 0.0), vec2(0.0, 1.0), vec2(-1.0, 0.0), vec2(0.0, -1.0),
    vec2(1.0, 1.0), vec2(-1.0, 1.0), vec2(-1.0, -1.0), vec2(1.0, -1.0)
};

void fragment() {
    vec4 center = texture(TEXTURE, UV);
    float edge = 0.0;

    // Compare center pixel to 8 neighbors
    for (int i = 0; i < 8; i++) {
        vec2 offset = DIRECTIONS[i] * TEXTURE_PIXEL_SIZE * outline_width;
        vec4 neighbor = texture(TEXTURE, UV + offset);

        // Color difference = different objects = edge
        float diff = abs(neighbor.r - center.r)
                   + abs(neighbor.g - center.g)
                   + abs(neighbor.b - center.b);

        // Any color difference means boundary
        float is_boundary = step(0.01, diff);
        edge = max(edge, is_boundary);
    }

    COLOR.rgb = outline_color.rgb;
    COLOR.a = edge * center.a; // No outline on transparent background
}
