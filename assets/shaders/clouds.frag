#version 410 core
in vec2 vUV;
in vec3 vWorldPos;
uniform vec3 uSunDirection;
uniform vec3 uCloudTopColor;
uniform vec3 uCloudBottomColor;
uniform vec2 uCloudOffset;
uniform float uCloudDensity;
uniform float uCloudHeight;
uniform float uTime;
out vec4 fragColor;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
               u.y);
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 5; ++i) {
        v += a * noise(p);
        p = p * 2.0 + 1.7;
        a *= 0.5;
    }
    return v;
}

void main(){
    vec2 uv = (vUV - 0.5) * 2.0;
    vec2 p = vWorldPos.xz * 0.08 + uCloudOffset * 3.4;
    float base = fbm(p * (1.3 + uCloudDensity));
    float detail = fbm(p * (2.6 + uCloudDensity * 1.5) + 8.0);
    float cloudMask = smoothstep(0.42, 0.95, base + detail * 0.6 - (1.0 - uCloudDensity) * 0.2);
    float dome = 1.0 - smoothstep(0.8, 1.5, length(uv));
    float alpha = cloudMask * dome;

    float daylight = max(0.0, min(1.0, (uSunDirection.y + 0.2) / 0.9));
    vec3 color = mix(uCloudBottomColor, uCloudTopColor, clamp(vWorldPos.y / (uCloudHeight + 30.0), 0.0, 1.0));
    color *= 0.9 + daylight * 0.35;

    fragColor = vec4(color, alpha * 0.9);
}
