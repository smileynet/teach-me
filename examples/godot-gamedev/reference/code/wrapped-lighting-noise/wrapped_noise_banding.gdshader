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

// === Wrapped Lighting ===
uniform float wrapped_lighting : hint_range(0, 1) = 1.0;
uniform float wrapped_lighting_scale : hint_range(0, 1) = 0.35;

// === Noise Map ===
uniform bool use_noise_map = false;
uniform sampler2D noise_map;
uniform float noise_strength : hint_range(0.0, 0.25) = 0.04;
uniform float noise_scale : hint_range(0.1, 10.0) = 1.0;

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
	float NdotL = clamp(dot(NORMAL, LIGHT), 0.0, 1.0);

	// Wrapped lighting: raise the floor of NdotL (Half Lambert variant)
	float wrap = clamp(wrapped_lighting * wrapped_lighting_scale, 0.0, 1.0);
	float wrapped = NdotL * (1.0 - wrap) + wrap;

	// Noise bias: per-pixel threshold perturbation for organic edges
	float noise_bias = 0.0;
	if (use_noise_map) {
		noise_bias = (texture(noise_map, UV * noise_scale).r - 0.5) * noise_strength;
	}

	// Center around threshold (with wrap and noise folded in)
	float centered = clamp(wrapped - light_threshold - diffuse_threshold_offset + 0.5 + noise_bias, 0.0, 1.0);

	// Band quantization
	float banded = floor(centered * light_bands) / max(light_bands - 1.0, 1.0);

	// Smoothness blend
	float lit_factor = mix(banded, centered, diffuse_smoothness);

	// Scale
	lit_factor = 0.5 + (lit_factor - 0.5) * light_bands_scale;

	// Gooch shading
	vec3 shadow_tint = mix(ALBEDO, ALBEDO * gooch_dark_color.rgb, gooch_ramp_intensity);
	vec3 lit_tint = mix(ALBEDO, ALBEDO * gooch_bright_color.rgb, gooch_ramp_intensity);
	vec3 toon_color = mix(shadow_tint, lit_tint, lit_factor);

	DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, toon_color * LIGHT_COLOR * ATTENUATION);
}
