#version 410 core
in vec2 vUV;
uniform sampler2D uHdr;
uniform sampler2D uDepth;
uniform float uExposure, uFogDensityPost;
uniform vec3 uFogColor;
out vec4 fragColor;
void main(){
    vec3 hdr = texture(uHdr, vUV).rgb;
    float depth = texture(uDepth, vUV).r;
    float fog = smoothstep(0.82, 0.998, depth) * max(0.08, uFogDensityPost * 0.22);
    hdr = mix(hdr, uFogColor, fog);
    vec3 mapped = vec3(1.0) - exp(-hdr * uExposure);
    mapped = pow(mapped, vec3(1.0 / 2.2));
    fragColor = vec4(mapped, 1.0);
}
