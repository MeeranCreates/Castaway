#version 410 core
in vec2 vUV;
in vec3 vWorldPos;
uniform vec3 uSunDirection;
uniform float uTime;
out vec4 fragColor;

void main(){
    vec2 blockUV = floor(vUV * 8.0) / 8.0;
    float cloudNoise = sin(blockUV.x * 12.9898 + blockUV.y * 78.233 + uTime * 0.2) * 
                       cos(blockUV.x * 45.164 + blockUV.y * 94.673 + uTime * 0.15);
    
    float blockDensity = step(0.3, fract(cloudNoise));
    float edgeSmooth = smoothstep(0.28, 0.32, fract(cloudNoise));
    
    vec2 blockCenter = blockUV + vec2(0.0625);
    float distToCenter = length((vUV - blockCenter) * 8.0);
    float blockShape = smoothstep(0.75, 0.5, distToCenter);
    
    float daylight = max(0.0, min(1.0, (uSunDirection.y + 0.2) / 0.9));
    vec3 cloudColor = mix(vec3(0.15, 0.15, 0.2), vec3(0.98, 0.98, 0.95), daylight);
    
    float alpha = blockDensity * blockShape * 0.5 * (0.3 + 0.7 * sin(uTime + vWorldPos.x + vWorldPos.z));
    fragColor = vec4(cloudColor, alpha);
}
