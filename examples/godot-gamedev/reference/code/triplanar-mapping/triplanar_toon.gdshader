shader_type spatial;
render_mode cull_disabled;

uniform sampler2D albedo_texture : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform float tex_scale : hint_range(0.01, 10.0) = 1.0;
uniform float blend_sharpness : hint_range(1.0, 20.0) = 5.0;
uniform int bands : hint_range(1, 8) = 3;
uniform float wrap : hint_range(-1.0, 1.0) = 0.0;
uniform float steepness : hint_range(0.5, 4.0) = 1.0;

varying vec3 world_pos;
varying vec3 world_normal;

void vertex() {
    world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}

void fragment() {
    // Compute blending weights from surface normal
    vec3 blend = pow(abs(world_normal), vec3(blend_sharpness));
    blend /= (blend.x + blend.y + blend.z); // normalize to sum = 1.0

    // Sample texture from each axis (X flipped to prevent mirroring)
    vec3 x_proj = texture(albedo_texture, world_pos.zy * vec2(-1.0, 1.0) * tex_scale).rgb;
    vec3 y_proj = texture(albedo_texture, world_pos.xz * tex_scale).rgb;
    vec3 z_proj = texture(albedo_texture, world_pos.xy * tex_scale).rgb;

    // Blend the three projections
    ALBEDO = x_proj * blend.x + y_proj * blend.y + z_proj * blend.z;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    float diffuse_amount = NdotL + (ATTENUATION - 1.0) + wrap;
    diffuse_amount *= steepness;
    float cuts_inv = 1.0 / float(bands);
    float stepped = clamp(diffuse_amount + mod(1.0 - diffuse_amount, cuts_inv), 0.0, 1.0);
    DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, ALBEDO * LIGHT_COLOR * stepped);
}
