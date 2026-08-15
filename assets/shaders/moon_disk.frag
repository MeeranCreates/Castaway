#version 410 core
in vec2 vUV;
uniform vec3 uDirection;
out vec4 fragColor;
void main(){
    vec2 moonPos = vec2(0.5 - uDirection.x * 0.52, 0.5 - uDirection.y * 0.42);
    float dist = length(vUV - moonPos);
    float disk = smoothstep(0.065, 0.0, dist);
    float glow = smoothstep(0.18, 0.0, dist) * 0.5;
    float alpha = max(disk, glow * 0.25);
    vec3 color = vec3(0.78, 0.84, 1.0);
    fragColor = vec4(color * (disk + glow), alpha);
}
