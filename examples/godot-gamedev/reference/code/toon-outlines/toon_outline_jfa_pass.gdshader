shader_type canvas_item;
render_mode blend_mix;

// This shader runs multiple times with decreasing offset values
uniform sampler2D in_texture : hint_screen_texture, filter_nearest;
uniform float offset; // Halves each pass: 128, 64, 32, 16, 8, 4, 2, 1
uniform float distance_denominator;
uniform bool last_pass;

const vec2 NEIGHBOR_OFFSETS[8] = {
    vec2(-1.0,-1.0), vec2(0.0,-1.0), vec2(1.0,-1.0),
    vec2(-1.0,0.0),                   vec2(1.0,0.0),
    vec2(-1.0,1.0),  vec2(0.0,1.0),  vec2(1.0,1.0) };

void fragment() {
    vec2 texture_size = vec2(textureSize(in_texture, 0));
    vec2 pixel_size = 1.0 / texture_size;
    vec2 tex_coord = UV / pixel_size; // Current pixel coordinate

    // Read current best seed (packed as UV coordinates in RG channels)
    vec4 seed_color = texelFetch(in_texture, ivec2(tex_coord), 0);
    vec2 seed_coord = seed_color.rg * texture_size;
    bool valid_seed = seed_color.a > 0.5;
    float min_dist_sq = valid_seed ? distance(tex_coord, seed_coord) : 1000000.0;
    min_dist_sq = min_dist_sq * min_dist_sq;

    // Check 8 neighbors at current offset distance
    for (int i = 0; i < 8; i++) {
        vec2 neighbor_coord = tex_coord + NEIGHBOR_OFFSETS[i] * offset;
        neighbor_coord = clamp(neighbor_coord, vec2(0.0), texture_size - vec2(1.0));

        vec4 neighbor_color = texelFetch(in_texture, ivec2(neighbor_coord), 0);
        if (neighbor_color.a < 0.5) continue; // No seed here

        vec2 neighbor_seed = neighbor_color.rg * texture_size;
        float dist_sq = distance(tex_coord, neighbor_seed);
        dist_sq = dist_sq * dist_sq;

        if (dist_sq < min_dist_sq) {
            min_dist_sq = dist_sq;
            seed_coord = neighbor_seed;
            seed_color = neighbor_color;
            valid_seed = true;
        }
    }

    if (last_pass) {
        // Output normalized distance (0 = on edge, 1 = far from edge)
        float dist = valid_seed ? sqrt(min_dist_sq) / distance_denominator : 1.0;
        COLOR = vec4(dist, 0.0, 0.0, 1.0);
    } else {
        // Pass seed coordinates to next iteration
        COLOR = valid_seed ? vec4(seed_coord / texture_size, 0.0, 1.0) : vec4(0.0);
    }
}
