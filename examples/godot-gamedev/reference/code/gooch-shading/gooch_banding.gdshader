shader_type spatial;
render_mode specular_disabled;

// === Albedo ===
uniform vec4 albedo_color : source_color = vec4(1.0);
uniform sampler2D albedo_texture : source_color;
uniform bool use_albedo_texture = false;

// === Toon Banding Controls ===
uniform float light_bands : hint_range(1, 9, 1) = 4.0;
uniform float light_bands_scale : hint_range(0, 1) = 0.5;
uniform float light_threshold : hint_range(0, 1) = 0.5;
uniform float diffuse_threshold_offset : hint_range(-1, 1) = 0.0;
uniform float diffuse_smoothness : hint_range(0, 1) = 0.0;

// === Gooch Shading ===
uniform vec4 gooch_bright_color : source_color = vec4(1.0);
uniform vec4 gooch_dark_color : source_color = vec4(0.2, 0.25, 0.35, 1.0);
uniform float gooch_ramp_intensity : hint_range(0, 1) = 0.5;

void fragment() {
	vec3 col = albedo_color.rgb;
	if (use_albedo_texture) {
		col *= texture(albedo_texture, UV).rgb;
	}
	ALBEDO = col;
}

void light() {
	float NdotL = dot(NORMAL, LIGHT);

	// Center around threshold (Half Lambert remap)
	float centered = NdotL - light_threshold - diffuse_threshold_offset + 0.5;
	centered = clamp(centered, 0.0, 1.0);

	// Band quantization
	float banded = floor(centered * light_bands) / max(light_bands - 1.0, 1.0);

	// Smoothness blend
	float lit_factor = mix(banded, centered, diffuse_smoothness);

	// Scale
	lit_factor = 0.5 + (lit_factor - 0.5) * light_bands_scale;

	// Gooch shading: tint shadow and lit endpoints, then interpolate by lit_factor
	vec3 shadow_tint = mix(ALBEDO, ALBEDO * gooch_dark_color.rgb, gooch_ramp_intensity);
	vec3 lit_tint = mix(ALBEDO, ALBEDO * gooch_bright_color.rgb, gooch_ramp_intensity);
	vec3 toon_color = mix(shadow_tint, lit_tint, lit_factor);

	DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, toon_color * LIGHT_COLOR * ATTENUATION);
}
