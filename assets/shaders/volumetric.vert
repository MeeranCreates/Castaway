#version 410 core
in vec3 aPosition;
out vec2 vUV;
void main(){
    vUV = aPosition.xz * 0.5 + 0.5;
    gl_Position = vec4(aPosition.x, aPosition.z, 0.0, 1.0);
}
