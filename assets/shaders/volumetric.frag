#version 410 core

in vec2 vUV;

uniform sampler2D uSceneColor;
uniform sampler2D uSceneDepth;
uniform sampler2D uShadowMap;
uniform mat4 uInvViewProjection;
uniform mat4 uLightSpace;
uniform vec3 uCameraPos;
uniform vec3 uSunDirection;
uniform vec3 uSunColor;
uniform vec3 uMoonDirection;
uniform vec3 uMoonColor;
uniform vec2 uResolution;
uniform float uFogDensity;
uniform float uSunIntensity;
uniform float uMoonIntensity;
uniform float uVolumetricIntensity;
uniform float uShadowBias;
uniform int uQualitySteps;

out vec4 fragColor;

const float MAX_DIST = 120.0;
const int MAX_STEPS = 64;

vec3 worldFromScreen(vec2 uv, float depth) {
    vec4 clip = vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    vec4 world = uInvViewProjection * clip;
    return world.xyz / world.w;
}

float sampleShadow(vec3 worldPos) {
    vec4 lightClip = uLightSpace * vec4(worldPos, 1.0);
    vec3 lightNdc = lightClip.xyz / lightClip.w;
    vec2 shadowUV = lightNdc.xy * 0.5 + 0.5;
    if (shadowUV.x < 0.0 || shadowUV.x > 1.0 || shadowUV.y < 0.0 || shadowUV.y > 1.0) return 1.0;
    if (lightNdc.z < -1.0 || lightNdc.z > 1.0) return 1.0;

    float currentDepth = lightNdc.z - uShadowBias;
    float shadowMapDepth = texture(uShadowMap, shadowUV).r;
    float shadow = currentDepth > shadowMapDepth ? 0.0 : 1.0;
    return shadow;
}

void main() {
    vec2 uv = vUV;
    float sceneDepth = texture(uSceneDepth, uv).r;
    vec3 sceneColor = texture(uSceneColor, uv).rgb;

    vec3 viewPos = worldFromScreen(uv, sceneDepth);
    vec3 rayOrigin = uCameraPos;
    vec3 rayDir = normalize(viewPos - rayOrigin);
    float maxDist = min(length(viewPos - rayOrigin), MAX_DIST);

    vec3 sunDir = normalize(uSunDirection);
    vec3 moonDir = normalize(uMoonDirection);
    float daylight = clamp((sunDir.y + 0.25) * 0.9, 0.0, 1.0);
    float hg = pow(max(0.0, dot(rayDir, -sunDir)), 2.0);
    float moonHg = pow(max(0.0, dot(rayDir, -moonDir)), 2.0) * clamp(1.0 - daylight, 0.0, 1.0);

    vec3 accumulated = vec3(0.0);
    float transmittance = 1.0;
    float stepLen = maxDist / max(float(uQualitySteps), 1.0);

    for (int i = 0; i < MAX_STEPS; i++) {
        if (i >= uQualitySteps) break;
        float t = (float(i) + 0.5) * stepLen;
        if (t >= maxDist) break;

        vec3 p = rayOrigin + rayDir * t;
        float density = uFogDensity * (0.5 + 0.5 * clamp((p.y + 4.0) / 16.0, 0.0, 1.0));
        density *= mix(0.15, 1.2, daylight);

        float shadow = sampleShadow(p);
        float beam = max(0.0, dot(normalize(p - rayOrigin), -sunDir));
        float moonBeam = max(0.0, dot(normalize(p - rayOrigin), -moonDir));
        float scatter = density * shadow * max(0.0, dot(rayDir, -sunDir)) * (0.6 + hg) * (0.4 + beam);
        float moonScatter = density * shadow * max(0.0, dot(rayDir, -moonDir)) * moonHg * (0.25 + moonBeam);

        vec3 localLight = uSunColor * (uSunIntensity * 0.5 + 0.5) * scatter * uVolumetricIntensity;
        localLight += uMoonColor * (uMoonIntensity * 0.8) * moonScatter * uVolumetricIntensity * 0.18;
        accumulated += vec3(localLight) * transmittance * (1.0 / max(float(uQualitySteps), 1.0));

        transmittance *= exp(-density * stepLen * 0.9);
        if (transmittance < 0.02) break;
    }

    vec3 tint = mix(vec3(0.08, 0.12, 0.18), vec3(1.0, 0.66, 0.42), daylight);
    vec3 finalColor = sceneColor + accumulated * tint;
    fragColor = vec4(finalColor, 1.0);
}
