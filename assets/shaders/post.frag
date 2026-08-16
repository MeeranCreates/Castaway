#version 410 core
in vec2 vUV;
uniform sampler2D uHdr;
uniform sampler2D uVolumetric;
uniform sampler2D uDepth;
uniform float uExposure, uFogDensityPost;
uniform vec3 uFogColor;
uniform int uVolumetricEnabled;
out vec4 fragColor;
void main(){
    vec3 hdr = texture(uHdr, vUV).rgb;
    vec3 volumetric = texture(uVolumetric, vUV).rgb;
    float depth = texture(uDepth, vUV).r;
    float fog = smoothstep(0.82, 0.998, depth) * max(0.08, uFogDensityPost * 0.22);
    vec3 fogTint = mix(vec3(0.08, 0.12, 0.18), vec3(0.16, 0.20, 0.24), clamp(depth * 1.15, 0.0, 1.0));
    if (uVolumetricEnabled == 1) {
        hdr += volumetric;
    }
    hdr = mix(hdr, fogTint, fog);
    vec3 mapped = vec3(1.0) - exp(-hdr * uExposure);
    mapped = pow(mapped, vec3(1.0 / 2.2));
    fragColor = vec4(mapped, 1.0);
}
