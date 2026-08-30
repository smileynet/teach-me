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

// === Hatching Overlay (shadow-weighted) ===
uniform bool use_hatching_dark_map = false;
uniform sampler2D hatching_dark_map;
uniform float hatching_strength : hint_range(0, 1) = 0.15;
uniform float hatching_scale : hint_range(0.1, 10.0) = 1.0;

// === Sketch Overlay (uniform) ===
uniform bool use_sketch_map = false;
uniform sampler2D sketch_map;
uniform float sketch_strength : hint_range(0, 1) = 0.08;
uniform float sketch_scale : hint_range(0.1, 10.0) = 1.0;

// === Flat Specular ===
uniform bool specular_enabled = false;
uniform vec4 flat_specular_color : source_color = vec4(1.0);
uniform float flat_specular_size : hint_range(0.0, 1.0) = 0.1;
uniform float flat_specular_edge_smoothness : hint_range(0.0, 1.0) = 0.0;
uniform float specular_intensity : hint_range(0.0, 2.0) = 1.0;

// === Rim Lighting ===
uniform bool rim_enabled = false;
uniform vec4 rim_color : source_color = vec4(1.0);
uniform float rim_size : hint_range(0.5, 8.0) = 2.0;
uniform float rim_smoothness : hint_range(0.0, 1.0) = 0.5;
uniform float rim_intensity : hint_range(0.0, 2.0) = 1.0;

void fragment() {
	vec3 col = albedo_color.rgb;
	if (use_albedo_texture) {
		col *= texture(albedo_texture, UV).rgb;
	}
	ALBEDO = col;
}

void light() {
	float NdotL = clamp(dot(NORMAL, LIGHT), 0.0, 1.0);

	// Wrapped lighting
	float wrap = clamp(wrapped_lighting * wrapped_lighting_scale, 0.0, 1.0);
	float wrapped = NdotL * (1.0 - wrap) + wrap;

	// Noise bias
	float noise_bias = 0.0;
	if (use_noise_map) {
		noise_bias = (texture(noise_map, UV * noise_scale).r - 0.5) * noise_strength;
	}

	// Centering
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

	// === OVERLAYS (multiplicative, BEFORE specular/rim) ===

	// Hatching: shadow-weighted — stronger in dark areas
	if (use_hatching_dark_map) {
		float hatch = texture(hatching_dark_map, UV * hatching_scale).r;
		float shadow_weight = 1.0 - lit_factor;
		toon_color *= mix(1.0, hatch, hatching_strength * shadow_weight);
	}

	// Sketch: uniform overlay — same everywhere regardless of lighting
	if (use_sketch_map) {
		float sketch = texture(sketch_map, UV * sketch_scale).r;
		toon_color *= mix(1.0, sketch, sketch_strength);
	}

	// === HIGHLIGHTS (additive, AFTER overlays) ===

	// Flat specular
	if (specular_enabled) {
		vec3 half_dir = normalize(LIGHT + VIEW);
		float NdotH = clamp(dot(NORMAL, half_dir), 0.0, 1.0);
		float spec_threshold = 1.0 - flat_specular_size;
		float spec_edge = max(flat_specular_edge_smoothness, 0.001);
		float spec_mask = smoothstep(spec_threshold - spec_edge, spec_threshold + spec_edge, NdotH);
		toon_color += flat_specular_color.rgb * spec_mask * specular_intensity;
	}

	// Rim lighting
	if (rim_enabled) {
		float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_size);
		float rim_edge = max(rim_smoothness, 0.001);
		float rim_mask = smoothstep(0.5 - rim_edge, 0.5 + rim_edge, fresnel);
		toon_color += rim_color.rgb * rim_mask * rim_intensity;
	}

	DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, toon_color * LIGHT_COLOR * ATTENUATION);
}
