#version 410 core

in float vHeight;

uniform vec3 uSunDirection;
uniform vec3 uSkyBottom;
uniform vec3 uSkyHorizon;
uniform vec3 uSkyZenith;

out vec4 fragColor;

void main()
{
    float h = clamp(vHeight, 0.0, 1.0);

    // Smooth atmospheric height.
    // Keeps the horizon transition continuous instead of creating
    // two obvious gradient sections.
    float atmosphere = smoothstep(0.0, 1.0, h);

    // Start with the horizon and smoothly transition toward the zenith.
    vec3 color = mix(
        uSkyHorizon,
        uSkyZenith,
        atmosphere
    );

    // Very subtle lower-atmosphere influence.
    float horizonFactor = 1.0 - smoothstep(0.0, 0.35, h);

    color = mix(
        color,
        uSkyBottom,
        horizonFactor * 0.35
    );

    // Sun elevation.
    float sunHeight = clamp(uSunDirection.y, -1.0, 1.0);

    // Sun becomes more important near the horizon.
    float sunsetFactor =
        1.0 - smoothstep(0.0, 0.5, abs(sunHeight));

    // Warm atmospheric glow.
    vec3 warmAtmosphere = vec3(1.0, 0.55, 0.25);

    color += warmAtmosphere
        * sunsetFactor
        * horizonFactor
        * 0.18;

    fragColor = vec4(color, 1.0);
}