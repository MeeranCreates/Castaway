#version 410 core
in vec3 aPosition;
in vec2 aUV;
uniform mat4 uView;
uniform mat4 uProjection;
uniform float uTime;
out vec2 vUV;
out vec3 vWorldPos;
void main(){
    vUV = aUV + vec2(uTime * 0.05, sin(uTime * 0.03) * 0.02);
    vWorldPos = aPosition;
    gl_Position = uProjection * uView * vec4(aPosition, 1.0);
}
