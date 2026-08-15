#version 410 core
in vec3 aPosition;
in vec3 aNormal;
in vec3 aTangent;
in vec2 aUV;
uniform mat4 uModel, uView, uProjection, uLightSpace;
out VS_OUT { vec3 worldPos; vec3 normal; vec3 tangent; vec2 uv; vec4 lightPos; } v;
void main() {
    vec4 world = uModel * vec4(aPosition, 1.0);
    v.worldPos = world.xyz; v.normal = mat3(uModel) * aNormal; v.tangent = mat3(uModel) * aTangent;
    v.uv = aUV * 20.0; v.lightPos = uLightSpace * world;
    gl_Position = uProjection * uView * world;
}
