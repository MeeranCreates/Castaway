#version 410 core
in VS_OUT { vec3 worldPos; vec3 normal; vec3 tangent; vec2 uv; vec4 lightPos; } v;
uniform sampler2D uAlbedo0, uAlbedo1, uAlbedo2, uNormal0, uNormal1, uNormal2, uShadowMap;
uniform vec3 uCameraPos, uSunDirection, uAmbientSky;
uniform float uRoughness;
out vec4 fragColor;
float shadowPCF(vec4 lightPos, vec3 n) {
    vec3 p = lightPos.xyz / lightPos.w * .5 + .5;
    if (p.z > 1.0 || p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 0.0;
    float bias = max(.0045 * (1.0 - dot(n, -uSunDirection)), .0015);
    float sum = 0.0;
    vec2 texel = 1.0 / vec2(textureSize(uShadowMap, 0));
    for (int x = -1; x <= 1; ++x) for (int y = -1; y <= 1; ++y) {
        vec2 sampleUV = clamp(p.xy + vec2(x, y) * texel, vec2(0.0), vec2(1.0));
        float shadowMap = texture(uShadowMap, sampleUV).r;
        sum += p.z - bias > shadowMap ? 1.0 : 0.0;
    }
    return sum / 9.0;
}
void main() {
    vec3 baseN = normalize(v.normal), t = normalize(v.tangent), b = normalize(cross(baseN, t));
    float slope = 1.0 - max(baseN.y, 0.0), rock = smoothstep(.24, .62, slope);
    float beach = smoothstep(-1.0, 2.8, v.worldPos.y) * (1.0 - rock);
    float valley = smoothstep(2.0, 11.0, v.worldPos.y) * (1.0 - rock);

    vec3 sand = texture(uAlbedo2, v.uv).rgb;
    vec3 grass = texture(uAlbedo0, v.uv).rgb;
    vec3 stone = texture(uAlbedo1, v.uv).rgb;

    vec3 albedo = mix(sand, grass, clamp((v.worldPos.y + 1.0) / 6.5, 0.0, 1.0));
    albedo = mix(albedo, stone, clamp((v.worldPos.y - 6.0) / 12.0, 0.0, 1.0) * rock * 1.25);
    albedo = mix(albedo, sand, beach * 0.75);

    float groundVariation = fract(sin(dot(floor(v.worldPos.xz * 1.7), vec2(127.1, 311.7))) * 43758.5453);
    albedo *= mix(.84, 1.12, groundVariation);

    vec3 mapN = mix(mix(texture(uNormal2,v.uv).xyz, texture(uNormal0,v.uv).xyz, valley), texture(uNormal1,v.uv).xyz, rock) * 2.0 - 1.0;
    vec3 N = normalize(mat3(t,b,baseN) * mapN), L = normalize(-uSunDirection), V = normalize(uCameraPos-v.worldPos), H = normalize(L+V);
    float ndl = max(dot(N,L),0.0), spec = pow(max(dot(N,H),0.0), mix(128.0, 8.0, uRoughness));
    vec3 direct = (albedo * ndl + vec3(spec * .38)) * (1.0 - shadowPCF(v.lightPos, N));
    fragColor = vec4(uAmbientSky * albedo * .55 + direct, 1.0);
}
