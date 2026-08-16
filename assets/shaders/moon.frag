#version 410 core
in vec3 vPos;
uniform vec3 uSunDirection;
uniform vec3 uMoonColor;
uniform float uMoonIntensity;
uniform float uPhase;
out vec4 fragColor;
void main(){
    vec2 uv = vPos.xy;
    float distToCenter = length(uv);
    float moon = smoothstep(1.12, 0.74, distToCenter);
    float phaseOffset = (uPhase - 0.5) * 2.0;
    float litMask = clamp(1.0 - abs((uv.x * 1.2) + phaseOffset), 0.0, 1.0);
    float crater = sin(uv.x * 18.0) * sin(uv.y * 18.0) * 0.12 + 0.9;
    float glow = exp(-distToCenter * distToCenter * 8.0) * 0.35;
    float nightness = 1.0 - smoothstep(-0.35, 0.25, uSunDirection.y);
    float alpha = (moon + glow) * nightness * max(0.05, litMask);
    vec3 color = uMoonColor * crater * (0.75 + uMoonIntensity * 1.3);
    fragColor = vec4(color, alpha);
}
