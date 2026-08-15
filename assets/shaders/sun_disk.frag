#version 410 core
in vec2 vUV;
uniform vec3 uSunDirection;
out vec4 fragColor;
void main(){
    vec2 sunPos = vec2(0.5 + uSunDirection.x * 0.52, 0.5 + uSunDirection.y * 0.42);
    float dist = length(vUV - sunPos);
    float disk = smoothstep(0.065, 0.0, dist);
    float glow = smoothstep(0.18, 0.0, dist) * 0.9;
    float alpha = max(disk, glow * 0.35);
    vec3 color = vec3(1.0, 0.82, 0.45);
    fragColor = vec4(color * (disk + glow), alpha);
}
