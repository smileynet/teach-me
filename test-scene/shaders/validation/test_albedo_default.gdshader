shader_type spatial;

// VALIDATION: What does ALBEDO default to when fragment() is absent?
//
// If ALBEDO defaults to white (vec3(1,1,1)):
//   → Sphere renders white with visible toon bands (lit/shadow split)
//
// If ALBEDO defaults to black (vec3(0,0,0)):
//   → Sphere renders solid black (anything * black = black)
//
// This validates F1 in ticket #185.
// Official docs claim: "ALBEDO ... Albedo (default white). Base color."

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    float lit = step(0.0, NdotL);
    DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * ATTENUATION * lit;
}
