#version 410 core
layout(location = 0) in vec3 aPosition;

uniform mat4 uProjection;
uniform mat4 uView;

out vec3 vViewDir;

void main()
{
    vec2 ndc = vec2(aPosition.x, aPosition.z);
    vec4 clip = vec4(ndc, -1.0, 1.0);
    vec4 viewRay = inverse(uProjection) * clip;
    vec3 cameraDir = normalize(vec3(viewRay.xy / viewRay.w, -1.0));
    vViewDir = normalize(mat3(uView) * cameraDir);

    gl_Position = vec4(ndc, 1.0, 1.0);
}
