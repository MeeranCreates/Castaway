#version 410 core
in vec3 vWorldPos;
in vec2 vUV;
uniform vec3 uCameraPos, uSunDirection, uFogColor;
uniform float uTime, uFogDensity, uFogStart, uFogMax;
out vec4 fragColor;
vec3 applyFog(vec3 fragColor, vec3 worldPos, vec3 cameraPos, vec3 fogColor, float fogDensity, float fogStart, float fogMax) {
    float distance = length(worldPos - cameraPos);
    float effectiveDistance = max(0.0, distance - fogStart);
    float fogFactor = exp(-effectiveDistance * fogDensity);
    fogFactor = max(0.0, min(1.0, fogFactor));
    if (distance > fogMax) { float extraFar = (distance - fogMax) / (fogMax * 0.5); fogFactor = mix(0.01, fogFactor, 1.0 / (1.0 + extraFar * 2.0)); }
    return mix(fogColor, fragColor, fogFactor);
}
void main(){
    vec2 uv = vUV + vec2(uTime * 0.04, uTime * 0.02);
    float ripple = sin(uv.x * 18.0) * sin(uv.y * 15.0) * 0.09;
    vec3 N = normalize(vec3(ripple, 1.0, cos(uv.x * 17.0) * 0.08));
    vec3 V = normalize(uCameraPos - vWorldPos);
    vec3 L = normalize(-uSunDirection);
    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 5.0);
    float shine = pow(max(dot(reflect(-L, N), V), 0.0), 180.0);
    vec3 deep = vec3(0.03, 0.18, 0.25);
    vec3 mid = vec3(0.10, 0.55, 0.70);
    vec3 bright = vec3(0.38, 0.86, 0.96);
    vec3 water = mix(deep, mid, fresnel);
    water = mix(water, bright, 0.35 + 0.65 * shine);
    water += vec3(shine) * 0.55;
    water = applyFog(water, vWorldPos, uCameraPos, uFogColor, uFogDensity, uFogStart, uFogMax);
    fragColor = vec4(water, 0.72);
}
