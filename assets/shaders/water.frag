#version 410 core
in vec3 vWorldPos;
in vec2 vUV;
uniform vec3 uCameraPos, uSunDirection;
uniform float uTime;
out vec4 fragColor;
void main(){
    vec2 uv=vUV+vec2(uTime*.025,uTime*.012); float ripple=sin(uv.x*15.)*sin(uv.y*13.)*.08;
    vec3 N=normalize(vec3(ripple,1.,cos(uv.x*17.)*.07)), V=normalize(uCameraPos-vWorldPos), L=normalize(-uSunDirection);
    float fresnel=pow(1.-max(dot(N,V),0.),5.), shine=pow(max(dot(reflect(-L,N),V),0.),180.);
    vec3 water=mix(vec3(.008,.08,.13),vec3(12,.28,.40),fresnel)+vec3(shine);
    fragColor=vec4(water,.58);
}
