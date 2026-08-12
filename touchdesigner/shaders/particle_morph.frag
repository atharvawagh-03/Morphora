// particle_morph.frag — soft glowing point sprites

in vec4 vColor;
out vec4 fragColor;

void main() {
    vec2 uv = gl_PointCoord - vec2(0.5);
    float d = length(uv);
    if (d > 0.5) discard;

    // Soft falloff for bloom-friendly highlights
    float alpha = smoothstep(0.5, 0.05, d);
    vec3 col = vColor.rgb * (1.0 + (1.0 - d) * 0.6);
    fragColor = vec4(col, alpha * vColor.a);
}
