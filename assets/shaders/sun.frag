#version 410 core
in vec3 vPos;
uniform vec3 uSunDirection;
out vec4 fragColor;
void main(){
    float distToCenter = length(vPos);
    float sun = smoothstep(1.02, 0.95, distToCenter);
    float glow = exp(-distToCenter * distToCenter * 8.0) * 0.6;
    vec3 color = mix(vec3(1.0, 0.95, 0.7), vec3(1.0, 0.8, 0.4), uSunDirection.y * 0.5 + 0.5);
    fragColor = vec4(color, sun + glow);
}
