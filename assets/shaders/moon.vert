#version 410 core
in vec3 aPosition;
uniform mat4 uView;
uniform mat4 uProjection;
out vec3 vPos;
void main(){
    vPos = aPosition;
    gl_Position = uProjection * uView * vec4(aPosition, 1.0);
}
