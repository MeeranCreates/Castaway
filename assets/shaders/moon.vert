#version 410 core
in vec3 aPosition;
uniform mat4 uView;
uniform mat4 uProjection;
uniform mat4 uModel;
out vec3 vPos;
void main(){
    vPos = vec3(uModel * vec4(aPosition, 1.0));
    gl_Position = uProjection * uView * uModel * vec4(aPosition, 1.0);
}
