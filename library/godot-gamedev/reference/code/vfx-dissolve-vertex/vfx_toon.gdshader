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

// === Hatching Overlay ===
uniform bool use_hatching_dark_map = false;
uniform sampler2D hatching_dark_map;
uniform float hatching_strength : hint_range(0, 1) = 0.15;
uniform float hatching_scale : hint_range(0.1, 10.0) = 1.0;

// === Sketch Overlay ===
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

// === Dissolve ===
uniform bool dissolve_enabled = false;
uniform bool use_dissolve_map = false;
uniform sampler2D dissolve_map;
uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve_border_size : hint_range(0.0, 1.0) = 0.25;
uniform vec4 dissolve_border_color : source_color = vec4(1.0);
uniform float dissolve_map_scale : hint_range(0.1, 10.0) = 1.0;

// === Vertex Animation ===
uniform bool vertex_animation_enabled = false;
uniform int vertex_animation_mode : hint_range(0, 3) = 0;
uniform float vertex_animation_intensity : hint_range(0.0, 0.5) = 0.05;
uniform vec4 vertex_animation_frequency = vec4(1.0, 1.0, 1.0, 0.0);
uniform float vertex_animation_stutter : hint_range(0.0, 1.0) = 0.0;

// Hash-based noise for vertex jitter (mode 3)
float vertex_noise(vec3 pos) {
	return fract(sin(dot(pos, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
}

void vertex() {
	if (vertex_animation_enabled && vertex_animation_intensity > 0.0) {
		float t = TIME;
		// Stutter: quantize time for stop-motion feel
		if (vertex_animation_stutter > 0.0) {
			t = floor(t / vertex_animation_stutter) * vertex_animation_stutter;
		}

		float wave = 0.0;
		vec3 freq = vertex_animation_frequency.xyz;

		if (vertex_animation_mode == 1) {
			// Sine: smooth breathing/pulsing
			wave = sin(t * freq.x + VERTEX.x * freq.y + VERTEX.y * freq.z);
		} else if (vertex_animation_mode == 2) {
			// Abs-sine: bouncing (always pushes outward)
			wave = abs(sin(t * freq.x + VERTEX.x * freq.y + VERTEX.y * freq.z));
		} else if (vertex_animation_mode == 3) {
			// Hash noise: chaotic jitter
			wave = vertex_noise(VERTEX + vec3(t * freq.x)) * 2.0 - 1.0;
		}

		VERTEX += NORMAL * wave * vertex_animation_intensity;
	}
}

void fragment() {
	// Albedo
	vec3 col = albedo_color.rgb;
	if (use_albedo_texture) {
		col *= texture(albedo_texture, UV).rgb;
	}

	// Dissolve (discard pixels + border glow)
	if (dissolve_enabled && dissolve_amount > 0.0) {
		if (use_dissolve_map) {
			float dissolve_val = texture(dissolve_map, UV * dissolve_map_scale).r;
			if (dissolve_val < dissolve_amount) {
				discard;
			}
			// Border glow at dissolve edge
			float border = smoothstep(dissolve_amount, dissolve_amount + dissolve_border_size, dissolve_val);
			col = mix(dissolve_border_color.rgb, col, border);
		} else {
			// No map: simple alpha fade (needs alpha blending or alpha_scissor to show)
			ALPHA = 1.0 - dissolve_amount;
		}
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

	// Overlays (multiplicative, before highlights)
	if (use_hatching_dark_map) {
		float hatch = texture(hatching_dark_map, UV * hatching_scale).r;
		float shadow_weight = 1.0 - lit_factor;
		toon_color *= mix(1.0, hatch, hatching_strength * shadow_weight);
	}
	if (use_sketch_map) {
		float sketch = texture(sketch_map, UV * sketch_scale).r;
		toon_color *= mix(1.0, sketch, sketch_strength);
	}

	// Flat specular (additive)
	if (specular_enabled) {
		vec3 half_dir = normalize(LIGHT + VIEW);
		float NdotH = clamp(dot(NORMAL, half_dir), 0.0, 1.0);
		float spec_threshold = 1.0 - flat_specular_size;
		float spec_edge = max(flat_specular_edge_smoothness, 0.001);
		float spec_mask = smoothstep(spec_threshold - spec_edge, spec_threshold + spec_edge, NdotH);
		toon_color += flat_specular_color.rgb * spec_mask * specular_intensity;
	}

	// Rim lighting (additive)
	if (rim_enabled) {
		float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_size);
		float rim_edge = max(rim_smoothness, 0.001);
		float rim_mask = smoothstep(0.5 - rim_edge, 0.5 + rim_edge, fresnel);
		toon_color += rim_color.rgb * rim_mask * rim_intensity;
	}

	DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, toon_color * LIGHT_COLOR * ATTENUATION);
}
