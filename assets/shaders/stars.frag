#version 410 core
in vec3 vPos;
uniform vec3 uSunDirection;
uniform float uTime;
out vec4 fragColor;

float hash(vec3 p) {
    p = fract(p * vec3(443.897, 441.423, 340.122));
    p += dot(p, p.yzx + 19.19);
    return fract((p.x + p.y) * p.z);
}

void main(){
    float nightness = 1.0 - smoothstep(-0.4, 0.2, uSunDirection.y);
    vec3 normalized = normalize(vPos);
    vec3 starSeed = floor(normalized * 12.0);
    float star = hash(starSeed);
    float brightness = smoothstep(0.5, 0.95, star) * (0.4 + 0.6 * sin(uTime * 2.0 + star * 6.28));
    brightness *= nightness;
    fragColor = vec4(vec3(0.95, 0.96, 1.0), brightness * 0.8);
}
