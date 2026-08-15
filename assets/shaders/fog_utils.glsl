#version 410 core
// Fog shader utilities - include this in fragment shaders to apply atmospheric fog
// Usage: fragColor.rgb = applyFog(fragColor.rgb, vWorldPos, uCameraPos, uFogColor, uFogDensity, uFogStart, uFogMax);

// Apply atmospheric fog to a color based on distance
// Uses exponential fog formula for smooth, natural falloff
// fragColor: The color to fog
// worldPos: World position of the fragment
// cameraPos: Camera position
// fogColor: Color to blend with
// fogDensity: Density parameter (higher = thicker fog)
// fogStart: Distance where fog starts (in world units)
// fogMax: Distance where fog is ~99% opaque (in world units)
// Returns: Fogged color
vec3 applyFog(vec3 fragColor, vec3 worldPos, vec3 cameraPos, vec3 fogColor, float fogDensity, float fogStart, float fogMax) {
    // Calculate distance from camera to fragment
    float distance = length(worldPos - cameraPos);
    
    // Apply fog start threshold (no fog before start_distance)
    float effectiveDistance = max(0.0, distance - fogStart);
    
    // Exponential fog formula for smooth, natural appearance
    // exp(-distance * density) creates an exponential falloff
    float fogFactor = exp(-effectiveDistance * fogDensity);
    
    // Clamp fog factor to ensure visible fading at max distance
    // This gives a visual maximum fog opacity while maintaining smoothness
    fogFactor = max(0.0, min(1.0, fogFactor));
    
    // For extreme distances, use linear blend to fog color
    // This prevents distant objects from being overly visible
    if (distance > fogMax) {
        // Beyond max distance, blend completely to fog color
        float extraFar = (distance - fogMax) / (fogMax * 0.5);
        fogFactor = mix(0.01, fogFactor, 1.0 / (1.0 + extraFar * 2.0));
    }
    
    // Blend fragment color with fog color
    return mix(fogColor, fragColor, fogFactor);
}

// Simplified version that doesn't require start distance
// (For post-processing fog, depth-based fog)
float calculateFogOpacity(float distance, float density, float maxDistance) {
    float effectiveDistance = distance;
    float opacity = 1.0 - exp(-effectiveDistance * density);
    
    // Smooth fade to full opacity over max distance
    opacity = mix(opacity, 1.0, smoothstep(0.0, maxDistance, distance));
    
    return clamp(opacity, 0.0, 1.0);
}
