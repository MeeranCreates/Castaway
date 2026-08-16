#version 410 core

in vec3 vViewDir;

uniform vec3 uSunDirection;
uniform vec3 uSkyBottom;
uniform vec3 uSkyHorizon;
uniform vec3 uSkyZenith;

out vec4 fragColor;

void main()
{
    vec3 dir = normalize(vViewDir);
    float height = clamp(dir.y, -1.0, 1.0);

    // Continuous atmosphere from the bottom haze up to the zenith.
    float lowerAtmosphere = smoothstep(-0.35, 0.15, height);
    float upperAtmosphere = smoothstep(0.15, 0.95, height);
    vec3 color = mix(uSkyBottom, uSkyHorizon, lowerAtmosphere);
    color = mix(color, uSkyZenith, upperAtmosphere);

    // Near the horizon the atmosphere should brighten and haze out into the terrain.
    float horizonBand = smoothstep(0.0, 0.55, 1.0 - abs(height));
    vec3 hazeColor = mix(uSkyBottom, uSkyHorizon, 0.65);
    color = mix(color, hazeColor, horizonBand * 0.38);

    // Atmospheric warm light is a sky effect only. The actual sunlight for surfaces
    // remains world-space and is computed in the lit material shaders using uSunDirection.
    vec3 sunDir = normalize(uSunDirection);
    float sunAlt = clamp(sunDir.y, -1.0, 1.0);
    float daylight = smoothstep(-0.2, 0.25, sunAlt);
    float sunSide = max(dot(dir, sunDir), 0.0);
    float sunGlow = pow(sunSide, 7.0) * daylight;

    vec3 warmAtmosphere = vec3(1.0, 0.67, 0.42);
    color += warmAtmosphere * sunGlow * horizonBand * 0.55;

    // Darken the night sky without a daytime glow.
    color = mix(color, uSkyBottom * 0.45, 1.0 - daylight);

    fragColor = vec4(color, 1.0);
}