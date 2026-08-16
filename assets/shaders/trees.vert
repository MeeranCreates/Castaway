#version 410 core
in vec3 aPosition;
in vec3 aNormal;
uniform mat4 uModel, uView, uProjection, uLightSpace;
out vec3 vWorldPos;
out vec3 vNormal;
out vec4 vLightPos;
void main(){
    vec4 world = uModel * vec4(aPosition, 1.0);
    vWorldPos = world.xyz;
    vNormal = mat3(uModel) * aNormal;
    vLightPos = uLightSpace * world;
    gl_Position = uProjection * uView * world;
}
