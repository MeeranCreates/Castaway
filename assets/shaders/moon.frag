#version 410 core
in vec3 vPos;
uniform vec3 uSunDirection;
out vec4 fragColor;
void main(){
    float distToCenter = length(vPos);
    float moon = smoothstep(1.02, 0.98, distToCenter);
    float craters = sin(vPos.x * 15.0) * sin(vPos.y * 15.0) * 0.15 + 0.85;
    float glow = exp(-distToCenter * distToCenter * 4.0) * 0.2;
    float nightness = 1.0 - smoothstep(-0.3, 0.3, uSunDirection.y);
    vec3 color = vec3(0.92, 0.93, 0.95) * craters;
    fragColor = vec4(color, (moon + glow) * nightness);
}
