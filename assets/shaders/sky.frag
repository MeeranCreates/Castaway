#version 410 core
in float vHeight;
uniform vec3 uSunDirection;
uniform vec3 uSkyBottom;
uniform vec3 uSkyHorizon;
uniform vec3 uSkyZenith;
out vec4 fragColor;
void main(){
    float h = clamp(vHeight, 0.0, 1.0);
    float sunGlow = clamp((uSunDirection.y + 0.15) * 0.8, 0.0, 1.0);
    vec3 color = mix(uSkyBottom, uSkyHorizon, smoothstep(0.0, 0.45, h));
    color = mix(color, uSkyZenith, smoothstep(0.45, 1.0, h));
    color += vec3(1.0, 0.75, 0.45) * sunGlow * (1.0 - h) * 0.22;
    fragColor = vec4(color, 1.0);
}
