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
	// 0.5 becomes the default midpoint — threshold shifts the split intuitively
	float centered = NdotL - light_threshold - diffuse_threshold_offset + 0.5;
	centered = clamp(centered, 0.0, 1.0);

	// Band quantization: floor-divide spans full [0,1] range
	// N bands produce N distinct lit levels (0, 1/(N-1), 2/(N-1), ..., 1.0)
	float banded = floor(centered * light_bands) / max(light_bands - 1.0, 1.0);

	// Smoothness: blend quantized result with continuous value
	// 0.0 = hard cel edges, 1.0 = smooth gradient (no quantization)
	float lit_factor = mix(banded, centered, diffuse_smoothness);

	// Scale: how dramatic the shading appears
	// 0.0 = flat mid-gray, 1.0 = full dark-to-light range
	lit_factor = 0.5 + (lit_factor - 0.5) * light_bands_scale;

	DIFFUSE_LIGHT = max(DIFFUSE_LIGHT, ALBEDO * LIGHT_COLOR * ATTENUATION * lit_factor);
}
