// particle_morph.vert — linear morph + turbulence + swirl + explosion
// Custom vertex attribute: targetP (vec3)

uniform float uMorphT;
uniform float uTime;
uniform float uExplodeAmt;
uniform float uSwirlStrength;
uniform float uNoiseAmp;
uniform float uPointSize;

out vec4 vColor;

// ── Simple 3D value noise ────────────────────────────────────────────────────
float hash31(vec3 p) {
    p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float noise3(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    float n000 = hash31(i + vec3(0.0, 0.0, 0.0));
    float n100 = hash31(i + vec3(1.0, 0.0, 0.0));
    float n010 = hash31(i + vec3(0.0, 1.0, 0.0));
    float n110 = hash31(i + vec3(1.0, 1.0, 0.0));
    float n001 = hash31(i + vec3(0.0, 0.0, 1.0));
    float n101 = hash31(i + vec3(1.0, 0.0, 1.0));
    float n011 = hash31(i + vec3(0.0, 1.0, 1.0));
    float n111 = hash31(i + vec3(1.0, 1.0, 1.0));

    float nx00 = mix(n000, n100, f.x);
    float nx10 = mix(n010, n110, f.x);
    float nx01 = mix(n001, n101, f.x);
    float nx11 = mix(n011, n111, f.x);
    float nxy0 = mix(nx00, nx10, f.y);
    float nxy1 = mix(nx01, nx11, f.y);
    return mix(nxy0, nxy1, f.z);
}

vec3 turbulence(vec3 p, float t) {
    vec3 n = vec3(
        noise3(p + vec3(0.0, 0.0, 0.0)),
        noise3(p + vec3(5.2, 1.3, 2.8)),
        noise3(p + vec3(1.7, 4.1, 3.3))
    );
    return (n - 0.5) * 2.0 * t;
}

vec3 swirl(vec3 pos, float strength, float t) {
    float angle = strength * t * 6.28318;
    float c = cos(angle);
    float s = sin(angle);
    return vec3(c * pos.x + s * pos.z, pos.y, -s * pos.x + c * pos.z);
}

void main() {
    vec3 P1 = P;
    vec3 P2 = targetP;
    float t = clamp(uMorphT, 0.0, 1.0);

    // Bell envelope — zero at endpoints, peak at midpoint
    float envelope = 4.0 * t * (1.0 - t);

    vec3 morphed = mix(P1, P2, t);
    vec3 noisy = morphed + turbulence(morphed * 2.0 + uTime * 0.5, uNoiseAmp * envelope);
    vec3 swirled = swirl(noisy - morphed, uSwirlStrength, envelope) + morphed;

    // Radial explosion pulse at morph start
    vec3 center = vec3(0.0);
    vec3 radial = normalize(swirled - center + vec3(0.001));
    vec3 exploded = swirled + radial * uExplodeAmt * 0.35;

    vec4 worldPos = TDWorldMat * vec4(exploded, 1.0);
    gl_Position = TDCameraMat * worldPos;

    vColor = Cd;
    gl_PointSize = uPointSize;
}
