#version 410 core
in vec3 aPosition;
in vec2 aUV;
uniform mat4 uModel, uView, uProjection;
uniform float uTime;
out vec3 vWorldPos;
out vec2 vUV;
float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}
void main() {
    vec3 p = aPosition;
    vec2 uv = aUV * 12.0 + vec2(uTime * 0.15, uTime * 0.09);
    float seed = hash21(floor(uv * 2.0) + vec2(8.7, 3.1));
    float waveA = sin((p.x + seed * 2.4) * 1.15 + uTime * 1.8) * 0.68;
    float waveB = sin((p.z - seed * 3.1) * 1.35 - uTime * 1.6) * 0.52;
    float waveC = sin((p.x + p.z) * 2.0 + seed * 9.0 + uTime * 2.6) * 0.22;
    p.y += waveA + waveB + waveC;
    p.xz += vec2(sin(uTime + p.z * 0.8 + seed) * 0.12, cos(uTime * 0.9 + p.x * 0.6 - seed) * 0.12);
    vWorldPos = (uModel * vec4(p, 1.0)).xyz;
    vUV = aUV * 12.0 + vec2(uTime * 0.05, uTime * 0.03);
    gl_Position = uProjection * uView * vec4(vWorldPos, 1.0);
}
