shader_type spatial;
render_mode unshaded;

uniform vec4 original_color : source_color = vec4(1.0);
uniform vec4 outline_color : source_color = vec4(1.0, 0.0, 0.0, 1.0);

// Bit masks for render layers
const int LAYER_NORMAL = 1;    // Layer 1: normal render
const int LAYER_OUTLINE = 16;  // Layer 5: color-ID render (1 << 4)

void fragment() {
    if ((int(CAMERA_VISIBLE_LAYERS) & LAYER_NORMAL) != 0) {
        // Camera A sees us — render normally
        ALBEDO = original_color.rgb;
    } else if ((int(CAMERA_VISIBLE_LAYERS) & LAYER_OUTLINE) != 0) {
        // Camera B sees us — output flat ID color for edge detection
        ALBEDO = outline_color.rgb;
    }
}
