shader_type spatial;
render_mode unshaded, depth_test_disabled;

uniform sampler2D DEPTH_TEXTURE : hint_depth_texture, filter_linear;
uniform sampler2D NORMAL_TEXTURE : hint_normal_roughness_texture, filter_nearest;
uniform float depth_threshold : hint_range(0.0, 2.0) = 0.4;
uniform float normal_threshold : hint_range(0.0, 2.0) = 0.6;
uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_thickness : hint_range(0.5, 5.0) = 1.0;

float getLinearDepth(vec2 uv, mat4 inv_proj) {
    float raw = texture(DEPTH_TEXTURE, uv).r;
    vec3 ndc = vec3(uv * 2.0 - 1.0, raw);
    vec4 view = inv_proj * vec4(ndc, 1.0);
    view.xyz /= view.w;
    return -view.z;
}

void vertex() {
    // Fullscreen quad — bypass model transform
    POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

void fragment() {
    vec2 pixel = outline_thickness / VIEWPORT_SIZE;

    // Sample depth at 4 neighbors
    float depth_center = getLinearDepth(SCREEN_UV, INV_PROJECTION_MATRIX);
    float depth_left   = getLinearDepth(SCREEN_UV + vec2(-pixel.x, 0.0), INV_PROJECTION_MATRIX);
    float depth_right  = getLinearDepth(SCREEN_UV + vec2( pixel.x, 0.0), INV_PROJECTION_MATRIX);
    float depth_up     = getLinearDepth(SCREEN_UV + vec2(0.0,  pixel.y), INV_PROJECTION_MATRIX);
    float depth_down   = getLinearDepth(SCREEN_UV + vec2(0.0, -pixel.y), INV_PROJECTION_MATRIX);

    // Depth edge: difference between opposing neighbors
    float depth_diff = abs(depth_left - depth_right) + abs(depth_up - depth_down);
    float depth_edge = smoothstep(depth_threshold * 0.1, depth_threshold, depth_diff);

    // Sample normals at 4 neighbors
    vec3 normal_center = texture(NORMAL_TEXTURE, SCREEN_UV).rgb * 2.0 - 1.0;
    vec3 normal_left   = texture(NORMAL_TEXTURE, SCREEN_UV + vec2(-pixel.x, 0.0)).rgb * 2.0 - 1.0;
    vec3 normal_right  = texture(NORMAL_TEXTURE, SCREEN_UV + vec2( pixel.x, 0.0)).rgb * 2.0 - 1.0;
    vec3 normal_up     = texture(NORMAL_TEXTURE, SCREEN_UV + vec2(0.0,  pixel.y)).rgb * 2.0 - 1.0;
    vec3 normal_down   = texture(NORMAL_TEXTURE, SCREEN_UV + vec2(0.0, -pixel.y)).rgb * 2.0 - 1.0;

    // Normal edge: how much normals diverge from center
    float normal_diff = 0.0;
    normal_diff += 1.0 - dot(normal_center, normal_left);
    normal_diff += 1.0 - dot(normal_center, normal_right);
    normal_diff += 1.0 - dot(normal_center, normal_up);
    normal_diff += 1.0 - dot(normal_center, normal_down);
    float normal_edge = smoothstep(normal_threshold, normal_threshold * 2.0, normal_diff);

    // Combine: either signal triggers the outline
    float edge = max(depth_edge, normal_edge);

    ALBEDO = outline_color.rgb;
    ALPHA = edge * outline_color.a;
}
