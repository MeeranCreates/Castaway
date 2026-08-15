#version 410 core
in vec3 aPosition;
in vec2 aUV;
out vec2 vUV;
out vec3 vWorldPos;
uniform mat4 uView;
uniform mat4 uProjection;
uniform vec2 uCloudOffset;
uniform float uCloudHeight;
void main(){
    vec3 pos = aPosition;
    pos.xz += uCloudOffset * 12.0;
    pos.y += uCloudHeight;
    vUV = aUV;
    vWorldPos = pos;
    gl_Position = uProjection * uView * vec4(pos, 1.0);
}
