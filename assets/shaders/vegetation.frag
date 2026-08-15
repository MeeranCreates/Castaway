#version 410 core
in float vLight;
in float vVariation;
in vec3 vWorldPos;
uniform vec3 uCameraPos, uFogColor;
uniform float uFogDensity, uFogStart, uFogMax;
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
    vec3 dry=vec3(.18,.30,.045), fresh=vec3(.035,.32,.055);
    vec3 color = mix(fresh,dry,vVariation)*vLight;
    color = applyFog(color, vWorldPos, uCameraPos, uFogColor, uFogDensity, uFogStart, uFogMax);
    fragColor=vec4(color,1.);
}
