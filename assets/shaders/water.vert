#version 410 core
in vec3 aPosition;
in vec2 aUV;
uniform mat4 uModel, uView, uProjection;
uniform float uTime;
out vec3 vWorldPos;
out vec2 vUV;
vec3 gerstner(vec2 d, float amp, float length, float speed, vec3 p) {
    float k=6.283185/length, phase=k*dot(d,p.xz)-speed*uTime, qa=.65*amp;
    return vec3(d.x*qa*cos(phase), amp*sin(phase), d.y*qa*cos(phase));
}
void main(){ vec3 p=aPosition; p+=gerstner(normalize(vec2(1,.3)),.55,14.,1.5,p); p+=gerstner(normalize(vec2(-.4,1)),.28,7.,2.3,p); p+=gerstner(normalize(vec2(.7,-.8)),.12,3.,3.1,p); vWorldPos=(uModel*vec4(p,1)).xyz;vUV=aUV*8.;gl_Position=uProjection*uView*vec4(vWorldPos,1); }
