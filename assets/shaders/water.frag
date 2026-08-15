#version 410 core
in vec3 vWorldPos;
in vec2 vUV;
uniform vec3 uCameraPos, uSunDirection;
uniform float uTime;
out vec4 fragColor;
void main(){
    vec2 uv = vUV + vec2(uTime * 0.04, uTime * 0.02);
    float ripple = sin(uv.x * 18.0) * sin(uv.y * 15.0) * 0.09;
    vec3 N = normalize(vec3(ripple, 1.0, cos(uv.x * 17.0) * 0.08));
    vec3 V = normalize(uCameraPos - vWorldPos);
    vec3 L = normalize(-uSunDirection);
    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 5.0);
    float shine = pow(max(dot(reflect(-L, N), V), 0.0), 180.0);
    vec3 deep = vec3(0.03, 0.18, 0.25);
    vec3 mid = vec3(0.10, 0.55, 0.70);
    vec3 bright = vec3(0.38, 0.86, 0.96);
    vec3 water = mix(deep, mid, fresnel);
    water = mix(water, bright, 0.35 + 0.65 * shine);
    water += vec3(shine) * 0.55;
    fragColor = vec4(water, 0.72);
}
