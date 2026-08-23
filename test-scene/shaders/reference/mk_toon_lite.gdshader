shader_type spatial;
render_mode specular_disabled;

uniform vec4 albedo_color : source_color = vec4(1.0);
uniform sampler2D albedo_texture : source_color;
uniform bool use_albedo_texture = false;
uniform float albedo_texture_intensity : hint_range(0.0, 1.0) = 1.0;

uniform float light_bands : hint_range(1.0, 9.0, 1.0) = 4.0;
uniform float light_bands_scale : hint_range(0.0, 1.0) = 0.5;
uniform float light_threshold : hint_range(0.0, 1.0) = 0.5;
uniform float diffuse_threshold_offset : hint_range(-1.0, 1.0) = 0.0;
uniform float diffuse_smoothness : hint_range(0.0, 1.0) = 0.0;
uniform bool use_threshold_map = false;
uniform sampler2D threshold_map;
uniform float threshold_map_scale = 1.0;
uniform bool use_normal_map = false;
uniform sampler2D normal_map;
uniform float normal_map_intensity : hint_range(0.0, 2.0) = 1.0;
uniform float normal_map_scale = 1.0;
uniform float wrapped_lighting : hint_range(0.0, 1.0) = 1.0;
uniform float wrapped_lighting_scale : hint_range(0.0, 1.0) = 0.35;

uniform vec4 gooch_bright_color : source_color = vec4(1.0);
uniform vec4 gooch_dark_color : source_color = vec4(0.2, 0.25, 0.35, 1.0);
uniform float gooch_ramp_intensity : hint_range(0.0, 1.0) = 0.5;

uniform bool use_noise_map = false;
uniform sampler2D noise_map;
uniform float noise_strength : hint_range(0.0, 0.25) = 0.04;
uniform float noise_scale = 1.0;

uniform bool use_hatching_dark_map = false;
uniform sampler2D hatching_dark_map;
uniform float hatching_strength : hint_range(0.0, 1.0) = 0.15;
uniform float hatching_scale = 1.0;

uniform bool use_sketch_map = false;
uniform sampler2D sketch_map;
uniform float sketch_strength : hint_range(0.0, 1.0) = 0.08;
uniform float sketch_scale = 1.0;

uniform bool use_drawn_map = false;
uniform sampler2D drawn_map;
uniform float drawn_strength : hint_range(0.0, 1.0) = 0.08;
uniform float drawn_scale = 1.0;
uniform float drawn_clamp_min : hint_range(0.0, 1.0) = 0.0;
uniform float drawn_clamp_max : hint_range(0.0, 1.0) = 1.0;

uniform bool dissolve_enabled = false;
uniform bool use_dissolve_map = false;
uniform sampler2D dissolve_map;
uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve_border_size : hint_range(0.0, 1.0) = 0.25;
uniform vec4 dissolve_border_color : source_color = vec4(1.0);
uniform float dissolve_map_scale = 1.0;

uniform bool specular_enabled = false;
uniform vec4 flat_specular_color : source_color = vec4(1.0);
uniform float flat_specular_size : hint_range(0.0, 1.0) = 0.1;
uniform float flat_specular_edge_smoothness : hint_range(0.0, 1.0) = 0.0;
uniform float specular_threshold_offset : hint_range(0.0, 1.0) = 0.25;
uniform float specular_intensity = 1.0;

uniform bool rim_enabled = false;
uniform vec4 rim_color : source_color = vec4(1.0);
uniform vec4 rim_bright_color : source_color = vec4(1.0);
uniform vec4 rim_dark_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float rim_size : hint_range(0.0, 8.0) = 2.0;
uniform float rim_smoothness : hint_range(0.0, 1.0) = 0.5;
uniform float rim_threshold_offset : hint_range(0.0, 1.0) = 0.25;

uniform bool iridescence_enabled = false;
uniform vec4 iridescence_color : source_color = vec4(1.0);
uniform float iridescence_size : hint_range(0.0, 8.0) = 1.0;
uniform float iridescence_smoothness : hint_range(0.0, 1.0) = 0.5;
uniform float iridescence_threshold_offset : hint_range(0.0, 1.0) = 0.0;

uniform bool vertex_animation_enabled = false;
uniform int vertex_animation_mode : hint_range(0, 3, 1) = 0;
uniform float vertex_animation_intensity = 0.05;
uniform vec4 vertex_animation_frequency = vec4(1.0, 1.0, 1.0, 0.0);
uniform float vertex_animation_stutter = 0.0;
uniform bool use_vertex_animation_map = false;
uniform sampler2D vertex_animation_map;
uniform float vertex_animation_map_scale = 1.0;

uniform bool alpha_clip_enabled = false;
uniform float alpha_cutoff : hint_range(0.0, 1.0) = 0.5;

uniform float brightness = 1.0;
uniform float saturation = 1.0;
uniform float contrast = 1.0;
uniform float hue = 0.0;

vec3 rgb_to_hsv(vec3 color) {
	vec4 k = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(color.bg, k.wz), vec4(color.gb, k.xy), step(color.b, color.g));
	vec4 q = mix(vec4(p.xyw, color.r), vec4(color.r, p.yzx), step(p.x, color.r));
	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv_to_rgb(vec3 color) {
	vec3 p = abs(fract(color.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return color.z * mix(vec3(1.0), clamp(p - 1.0, vec3(0.0), vec3(1.0)), color.y);
}

float vertex_noise(vec3 position) {
	return fract(sin(dot(position, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
}

void vertex() {
	if (vertex_animation_enabled && vertex_animation_mode > 0 && vertex_animation_intensity != 0.0) {
		float t = TIME;
		if (vertex_animation_stutter > 0.0) {
			t = floor(t / vertex_animation_stutter) * vertex_animation_stutter;
		}
		float phase = dot(VERTEX, vertex_animation_frequency.xyz) + t;
		float wave = 0.0;
		if (vertex_animation_mode == 1) {
			wave = sin(phase);
		} else if (vertex_animation_mode == 2) {
			wave = abs(sin(phase));
		} else {
			wave = vertex_noise(VERTEX + vec3(t));
		}
		float mask = 1.0;
		if (use_vertex_animation_map) {
			mask = texture(vertex_animation_map, UV * vertex_animation_map_scale).r;
		}
		VERTEX += NORMAL * wave * mask * vertex_animation_intensity;
	}
}

void fragment() {
	vec4 base = albedo_color;

	if (use_albedo_texture) {
		vec4 tex = texture(albedo_texture, UV);
		base.rgb = mix(albedo_color.rgb, albedo_color.rgb * tex.rgb, albedo_texture_intensity);
		base.a *= tex.a;
	}

	if (dissolve_enabled) {
		if (use_dissolve_map) {
			float dissolve_mask = texture(dissolve_map, UV * dissolve_map_scale).r;
			if (dissolve_mask < dissolve_amount) {
				discard;
			}
			if (dissolve_amount > 0.0 && dissolve_border_size > 0.0) {
				float border = 1.0 - smoothstep(dissolve_amount, dissolve_amount + dissolve_border_size, dissolve_mask);
				base.rgb = mix(base.rgb, dissolve_border_color.rgb, border * dissolve_border_color.a);
			}
		} else {
			base.a *= 1.0 - dissolve_amount;
		}
	}

	if (alpha_clip_enabled && base.a < alpha_cutoff) {
		discard;
	}

	vec3 gray = vec3(dot(base.rgb, vec3(0.299, 0.587, 0.114)));
	base.rgb = mix(gray, base.rgb, saturation) * brightness;
	if (hue != 0.0) {
		vec3 hsv = rgb_to_hsv(base.rgb);
		hsv.x = fract(hsv.x + hue);
		base.rgb = hsv_to_rgb(hsv);
	}
	base.rgb = clamp((base.rgb - vec3(0.5)) * contrast + vec3(0.5), vec3(0.0), vec3(1.0));

	if (use_normal_map) {
		NORMAL_MAP = texture(normal_map, UV * normal_map_scale).rgb;
		NORMAL_MAP_DEPTH = normal_map_intensity;
	}

	ALBEDO = base.rgb;
	ALPHA = base.a;
}

void light() {
	float ndotl = clamp(dot(NORMAL, LIGHT), 0.0, 1.0);
	float wrap = clamp(wrapped_lighting * wrapped_lighting_scale, 0.0, 1.0);
	float wrapped = clamp(ndotl * (1.0 - wrap) + wrap, 0.0, 1.0);
	float noise_bias = 0.0;
	if (use_noise_map) {
		noise_bias = (texture(noise_map, UV * noise_scale).r - 0.5) * noise_strength;
	}
	float threshold_bias = 0.0;
	if (use_threshold_map) {
		threshold_bias = texture(threshold_map, UV * threshold_map_scale).r - 0.5;
	}
	float centered = clamp(wrapped - light_threshold - diffuse_threshold_offset + 0.5 + noise_bias + threshold_bias, 0.0, 1.0);
	float bands = max(light_bands, 1.0);
	float hard_band = floor(centered * bands) / max(bands - 1.0, 1.0);
	float band = mix(hard_band, centered, clamp(diffuse_smoothness, 0.0, 1.0));
	float lit_factor = band * light_bands_scale + (1.0 - light_bands_scale) * 0.5;

	float gooch_strength = clamp(gooch_ramp_intensity * 2.0, 0.0, 1.0);
	vec3 shadow_color = mix(ALBEDO, ALBEDO * gooch_dark_color.rgb, gooch_strength);
	vec3 lit_color = mix(ALBEDO, ALBEDO * gooch_bright_color.rgb, gooch_strength);
	vec3 toon_color = mix(shadow_color, lit_color, lit_factor);
	if (use_hatching_dark_map) {
		float hatch = texture(hatching_dark_map, UV * hatching_scale).r;
		float shadow_weight = 1.0 - lit_factor;
		toon_color *= mix(1.0, hatch, shadow_weight * hatching_strength);
	}
	if (use_sketch_map) {
		float sketch = texture(sketch_map, UV * sketch_scale).r;
		toon_color *= mix(1.0, sketch, sketch_strength);
	}
	if (use_drawn_map) {
		float drawn_range = max(drawn_clamp_max - drawn_clamp_min, 0.001);
		float drawn = clamp((texture(drawn_map, UV * drawn_scale).r - drawn_clamp_min) / drawn_range, 0.0, 1.0);
		toon_color *= mix(1.0, drawn, drawn_strength);
	}
	if (rim_enabled) {
		float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
		float rim = pow(1.0 - facing, max(rim_size, 0.001));
		float edge = max(rim_smoothness, 0.001);
		float rim_mask = smoothstep(0.5 + rim_threshold_offset - edge, 0.5 + rim_threshold_offset + edge, rim);
		vec3 rim_tint = rim_color.rgb * mix(rim_dark_color.rgb, rim_bright_color.rgb, rim_mask);
		toon_color += rim_tint * rim_color.a;
	}
	if (iridescence_enabled) {
		float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
		float iri = pow(1.0 - facing, max(iridescence_size, 0.001));
		float edge = max(iridescence_smoothness, 0.001);
		float iri_mask = smoothstep(0.5 + iridescence_threshold_offset - edge, 0.5 + iridescence_threshold_offset + edge, iri);
		toon_color += iridescence_color.rgb * iri_mask * iridescence_color.a;
	}
	if (specular_enabled && flat_specular_size > 0.0) {
		vec3 half_dir = normalize(LIGHT + VIEW);
		float ndoth = clamp(dot(NORMAL, half_dir), 0.0, 1.0);
		float threshold = clamp(1.0 - flat_specular_size + (specular_threshold_offset - 0.25), 0.0, 1.0);
		float edge = max(flat_specular_edge_smoothness, 0.001);
		float spec_mask = smoothstep(threshold - edge, threshold + edge, ndoth);
		toon_color += flat_specular_color.rgb * spec_mask * specular_intensity;
	}

	DIFFUSE_LIGHT += toon_color * LIGHT_COLOR * ATTENUATION;
}
