#version 410 core
in vec3 vWorldPos;
in vec3 vNormal;
in vec4 vLightPos;
uniform sampler2D uShadowMap;
uniform vec3 uColor, uCameraPos, uSunDirection, uAmbientSky;
out vec4 fragColor;
float shadow(vec4 lightPos, vec3 n) {
    vec3 p = lightPos.xyz / lightPos.w * 0.5 + 0.5;
    if (p.z > 1.0 || p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 0.0;
    float bias = max(.045 * (1.0 - dot(n, -uSunDirection)), .015);
    float result = 0.0;
    vec2 texel = 1.0 / vec2(textureSize(uShadowMap, 0));
    for (int x = -1; x <= 1; ++x) for (int y = -1; y <= 1; ++y) {
        vec2 sampleUV = clamp(p.xy + vec2(x, y) * texel, vec2(0.0), vec2(1.0));
        float shadowMapDepth = texture(uShadowMap, sampleUV).r;
        result += p.z - bias > shadowMapDepth ? 1.0 : 0.0;
    }
    return result / 9.0;
}
void main(){
    vec3 N = normalize(vNormal), L = normalize(-uSunDirection), V = normalize(uCameraPos - vWorldPos), H = normalize(L + V);
    float diffuse = max(dot(N, L), 0.0), spec = pow(max(dot(N, H), 0.0), 48.0) * 0.17;
    float shadowTerm = shadow(vLightPos, N);
    vec3 lit = uColor * (uAmbientSky * 0.38 + diffuse * (1.0 - shadowTerm));
    vec3 color = mix(lit, lit * 0.12, shadowTerm * 0.95) + spec;
    fragColor = vec4(color, 1.0);
}
